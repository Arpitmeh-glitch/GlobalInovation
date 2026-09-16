"""Integration coverage for CareerPilot profile and recommendation endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def client() -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


PROFILE = {
    "target_role": "Security Analyst",
    "skills": ["Python", "Linux"],
    "experience_level": "entry",
    "years_experience": 1,
    "education": "B.Tech Computer Science",
    "preferred_locations": ["Remote"],
    "work_preference": "remote",
    "industries": ["Cybersecurity"],
    "salary_expectation": 500000,
}


@pytest.mark.integration
async def test_profile_create_and_read(client: AsyncClient) -> None:
    saved = {"profile_id": "default", **PROFILE, "created_at": "now", "updated_at": "now"}
    with patch("app.routers.careerpilot.db", new_callable=AsyncMock) as mock_db:
        mock_db.upsert_careerpilot_profile.return_value = saved
        mock_db.get_careerpilot_profile.return_value = saved
        async with client:
            create_response = await client.put("/api/v1/careerpilot/profile", json=PROFILE)
            read_response = await client.get("/api/v1/careerpilot/profile")

    assert create_response.status_code == 200
    assert create_response.json()["target_role"] == "Security Analyst"
    assert read_response.status_code == 200
    assert read_response.json()["skills"] == ["Python", "Linux"]


@pytest.mark.integration
async def test_profile_validation_rejects_missing_role(client: AsyncClient) -> None:
    async with client:
        response = await client.put(
            "/api/v1/careerpilot/profile",
            json={**PROFILE, "target_role": ""},
        )
    assert response.status_code == 422


@pytest.mark.integration
async def test_discovery_returns_ranked_match_data(client: AsyncClient) -> None:
    with patch("app.routers.careerpilot.db", new_callable=AsyncMock) as mock_db:
        mock_db.get_careerpilot_profile.return_value = {
            "skills": ["Python", "Linux"],
            "target_role": "Security Analyst",
            "years_experience": 1,
            "education": "B.Tech",
        }
        mock_db.upsert_careerpilot_job.return_value = {}
        async with client:
            response = await client.post("/api/v1/careerpilot/jobs/discover", json={"persist": False})

    assert response.status_code == 200
    jobs = response.json()["jobs"]
    assert jobs
    assert jobs[0]["match"]["overall_score"] >= jobs[-1]["match"]["overall_score"]

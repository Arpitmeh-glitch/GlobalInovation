import pytest

from app.career_intelligence.career_gap_service import CareerGapService


class FakeDiscovery:
    async def discover_jobs_async(self, criteria=None, persist=False):
        assert persist is False
        return [
            {"id": "one", "title": "Backend Engineer", "skills_required": ["AWS", "Docker"], "skills_preferred": []},
            {"id": "two", "title": "Cloud Engineer", "skills_required": ["AWS"], "skills_preferred": ["Docker"]},
        ]


@pytest.mark.asyncio
async def test_gap_frequency_order_and_classification() -> None:
    result = await CareerGapService(discovery=FakeDiscovery()).analyze(
        {"skills": ["Python"], "summary": "Built AWS deployment automation"},
        target_role="Backend Engineer",
    )

    assert result.total_jobs_analyzed == 2
    assert [gap.name for gap in result.gaps] == ["AWS", "Docker"]
    assert [gap.frequency for gap in result.gaps] == [2, 2]
    assert result.gaps[0].gap_type == "evidence_gap"
    assert result.gaps[1].gap_type == "skill_gap"
    assert "AWS" in result.gaps[0].recommendation
    assert "Docker" in result.gaps[1].recommendation


@pytest.mark.asyncio
async def test_career_gap_dao_scopes_and_replaces_generated_gaps(isolated_backend_state) -> None:
    created = await isolated_backend_state.create_career_gap(
        profile_id="profile-1",
        gap_type="skill_gap",
        name="Docker",
        explanation="Docker appears in analyzed requirements.",
        recommendation="Build a Docker project.",
        frequency=2,
    )
    await isolated_backend_state.create_career_gap(
        profile_id="profile-2",
        gap_type="evidence_gap",
        name="AWS",
        explanation="AWS appears in the resume but lacks a declared skill entry.",
        recommendation="Add verified AWS evidence.",
    )

    assert (await isolated_backend_state.get_career_gap(created["gap_id"]))["name"] == "Docker"
    profile_one = await isolated_backend_state.list_career_gaps(profile_id="profile-1")
    assert [gap["name"] for gap in profile_one] == ["Docker"]

    replaced = await isolated_backend_state.replace_career_gaps(
        [
            {
                "gap_type": "skill_gap",
                "name": "Terraform",
                "explanation": "Terraform appears in analyzed requirements.",
                "recommendation": "Complete a Terraform project.",
                "frequency": 3,
            }
        ],
        profile_id="profile-1",
    )
    assert [gap["name"] for gap in replaced] == ["Terraform"]
    assert [gap["name"] for gap in await isolated_backend_state.list_career_gaps(profile_id="profile-1")] == ["Terraform"]
    assert [gap["name"] for gap in await isolated_backend_state.list_career_gaps(profile_id="profile-2")] == ["AWS"]

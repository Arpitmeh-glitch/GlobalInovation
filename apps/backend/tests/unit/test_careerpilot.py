import pytest

from app.job_providers.base import JobProvider
from app.job_providers.demo import DemoProvider
from app.job_discovery.service import JobDiscoveryService
from app.matching.engine import JobMatchingEngine
from app.matching.resume_context import (
    MULTIPLE_RESUMES_MESSAGE,
    NO_RESUME_MESSAGE,
    get_matching_resume,
)
from app.schemas.careerpilot import CareerPilotDiscoveryRequest
import app.database as database_module
import app.job_discovery.service as discovery_service


def test_job_provider_contract_is_abstract() -> None:
    assert issubclass(JobProvider, object)
    assert hasattr(JobProvider, "search_jobs")
    assert hasattr(JobProvider, "get_job_details")


def test_demo_provider_is_deterministic() -> None:
    provider = DemoProvider()
    jobs_a = provider.search_jobs({})
    jobs_b = provider.search_jobs({})
    assert jobs_a == jobs_b
    assert len(jobs_a) >= 10
    assert all(job["provider"] == "demo" for job in jobs_a)


def test_job_discovery_service_deduplicates_jobs() -> None:
    provider = DemoProvider()
    service = JobDiscoveryService(providers=[provider])
    jobs = service.discover_jobs({})
    assert jobs
    assert len({job["id"] for job in jobs}) == len(jobs)


def test_job_discovery_filters_sorts_and_paginates() -> None:
    service = JobDiscoveryService(providers=[DemoProvider()])
    jobs = service.discover_jobs({"min_salary": 800000, "work_mode": "remote"})
    page, total, offset, limit, has_more = service.paginate_jobs(
        jobs, {"sort_by": "salary", "sort_order": "desc", "offset": 1, "limit": 2}
    )
    assert total == len(jobs)
    assert offset == 1
    assert limit == 2
    assert len(page) == 2
    assert page[0]["salary_max"] >= page[1]["salary_max"]
    assert has_more is (total > 3)


def test_discovery_request_rejects_invalid_pagination_and_salary() -> None:
    with pytest.raises(ValueError):
        CareerPilotDiscoveryRequest(criteria={"limit": 0})
    with pytest.raises(ValueError):
        CareerPilotDiscoveryRequest(criteria={"min_salary": -1})


@pytest.mark.asyncio
async def test_sync_discovery_persist_true_writes_jobs() -> None:
    service = JobDiscoveryService(providers=[DemoProvider()])
    jobs = service.discover_jobs({}, persist=True)
    persisted = await discovery_service.db.list_careerpilot_jobs()
    assert len(jobs) == len(persisted)


def test_matching_engine_flags_hard_requirements() -> None:
    jobs = DemoProvider().search_jobs({})
    resume = {
        "skills": ["Python", "Linux", "Networking", "Wireshark"],
        "experience": [{"title": "IT Support", "years": "2 years"}],
        "education": [],
        "projects": [{"name": "Packet Analysis Lab", "description": ["Used Wireshark to inspect traffic"]}],
    }
    result = JobMatchingEngine().match_resume_to_job(resume, jobs[0])
    assert result["overall_score"] >= 0
    assert "hard_requirement_failures" in result


def test_matching_engine_supports_evidence() -> None:
    job = DemoProvider().search_jobs({})[0]
    resume = {
        "skills": ["Python", "Linux", "Networking", "Wireshark"],
        "experience": [{"title": "IT Support", "years": "2 years"}],
        "projects": [{"name": "CyberReconX", "description": ["Built a Python tool for traffic analysis using Wireshark"]}],
    }
    result = JobMatchingEngine().match_resume_to_job(resume, job)
    assert any(item["status"] == "supported" for item in result["evidence"])


def test_demo_provider_uses_fixed_canonical_timestamp() -> None:
    jobs = DemoProvider().search_jobs({})
    assert {job["discovered_at"] for job in jobs} == {"2026-09-16T00:00:00+00:00"}


def test_required_skill_is_a_hard_failure() -> None:
    result = JobMatchingEngine().match_resume_to_job(
        {"skills": ["Python"]},
        {"skills_required": ["Linux"], "skills_preferred": []},
    )
    assert "Required skill: Linux" in result["hard_requirement_failures"]


def test_preferred_skill_missing_is_not_a_hard_failure() -> None:
    result = JobMatchingEngine().match_resume_to_job(
        {"skills": ["Python"]},
        {"skills_required": ["Python"], "skills_preferred": ["Terraform"]},
    )
    assert result["hard_requirement_failures"] == []


def test_explicit_years_requirement_fails_without_years_evidence() -> None:
    result = JobMatchingEngine().match_resume_to_job(
        {"skills": ["Python", "Linux"]},
        {
            "skills_required": ["Python", "Linux"],
            "hard_requirements": ["At least 5 years of experience"],
        },
    )
    assert "At least 5 years of experience" in result["hard_requirement_failures"]


def test_high_skill_overlap_does_not_override_failed_hard_requirement() -> None:
    result = JobMatchingEngine().match_resume_to_job(
        {
            "skills": ["Python", "Linux"],
            "workExperience": [{"years": "2 years", "title": "Engineer"}],
        },
        {
            "skills_required": ["Python", "Linux"],
            "hard_requirements": ["At least 5 years of experience"],
        },
    )
    assert result["overall_score"] >= 60
    assert result["hard_requirement_failures"]
    assert result["recommendation"].startswith("Not recommended")


def test_missing_required_certification_is_detected() -> None:
    result = JobMatchingEngine().match_resume_to_job(
        {"skills": ["Python"], "additional": {"certificationsTraining": []}},
        {"skills_required": ["Python"], "hard_requirements": ["Required certification: Security+"]},
    )
    assert result["hard_requirement_failures"] == ["Required certification: Security+"]


def test_structured_resume_fields_and_case_insensitive_skills_are_supported() -> None:
    result = JobMatchingEngine().match_resume_to_job(
        {
            "summary": "Two years building APIs",
            "workExperience": [{"title": "Engineer", "years": "2 years", "description": []}],
            "additional": {"technicalSkills": ["python"]},
            "personalProjects": [],
        },
        {"skills_required": ["Python"], "skills_preferred": []},
    )
    assert "Python" in result["matched_requirements"]
    assert result["hard_requirement_failures"] == []


def test_matching_returns_explicit_skill_experience_and_education_results() -> None:
    result = JobMatchingEngine().match_resume_to_job(
        {
            "skills": ["Python"],
            "experience": [{"years": "2 years"}],
            "education": [{"degree": "Bachelor of Computer Science"}],
        },
        {
            "skills_required": ["Python", "AWS"],
            "qualifications": ["Bachelor degree"],
            "experience_required": "1-3 years",
        },
    )
    assert result["matched_skills"] == ["Python"]
    assert result["missing_skills"] == ["AWS"]
    assert result["experience_match"] is True
    assert result["education_match"] is True


@pytest.mark.asyncio
async def test_resume_selection_prefers_master(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeDatabase:
        async def get_master_resume(self) -> dict:
            return {"resume_id": "master", "is_master": True, "processing_status": "ready", "processed_data": {"skills": ["Python"]}}

        async def list_resumes(self) -> list[dict]:
            return []

    monkeypatch.setattr(database_module, "db", FakeDatabase())
    selected = await get_matching_resume()
    assert selected["resume_id"] == "master"


@pytest.mark.asyncio
async def test_resume_selection_reports_missing_or_ambiguous_profiles(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeDatabase:
        async def get_master_resume(self) -> None:
            return None

        async def list_resumes(self) -> list[dict]:
            return [
                {"resume_id": "one", "processing_status": "ready", "processed_data": {"skills": ["Python"]}},
                {"resume_id": "two", "processing_status": "ready", "processed_data": {"skills": ["Linux"]}},
            ]

    monkeypatch.setattr(database_module, "db", FakeDatabase())
    with pytest.raises(ValueError, match=MULTIPLE_RESUMES_MESSAGE):
        await get_matching_resume()

    monkeypatch.setattr(database_module, "db", type("EmptyDatabase", (), {"get_master_resume": lambda self: _none(), "list_resumes": lambda self: _empty()})())
    with pytest.raises(ValueError, match=NO_RESUME_MESSAGE):
        await get_matching_resume()


async def _none() -> None:
    return None


async def _empty() -> list[dict]:
    return []

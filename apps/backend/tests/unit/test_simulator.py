from copy import deepcopy

import pytest

from app.career_intelligence.simulator import SkillSimulator
from app.schemas.career_intelligence import SimulationRequest


class FakeDiscovery:
    async def get_job(self, job_id):
        return {
            "id": job_id,
            "title": "Cloud Engineer",
            "skills_required": ["Python", "AWS"],
            "skills_preferred": [],
            "qualifications": [],
            "hard_requirements": [],
        }


@pytest.mark.asyncio
async def test_simulator_reports_score_delta_and_preserves_inputs() -> None:
    resume = {
        "skills": ["Python"],
        "experience": [{"title": "Developer", "years": "2 years"}],
        "education": [],
        "additional": {"technicalSkills": []},
    }
    job = await FakeDiscovery().get_job("cloud-1")
    original_resume = deepcopy(resume)
    original_job = deepcopy(job)

    result = await SkillSimulator(discovery=FakeDiscovery()).simulate(
        SimulationRequest(
            resume=resume,
            job_ids=["cloud-1"],
            hypothetical_skills=["AWS"],
        )
    )

    comparison = result.comparisons[0]
    assert comparison.is_hypothetical is True
    assert comparison.baseline_score < comparison.simulated_score
    assert comparison.score_delta == comparison.simulated_score - comparison.baseline_score
    assert "AWS" not in comparison.baseline_matched_skills
    assert "AWS" in comparison.simulated_matched_skills
    assert resume == original_resume
    assert job == original_job
    assert result.hypothetical_additions["is_hypothetical"] is True

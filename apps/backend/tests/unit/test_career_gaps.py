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

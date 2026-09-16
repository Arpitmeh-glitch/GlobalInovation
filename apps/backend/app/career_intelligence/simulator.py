"""Immutable, in-memory what-if skill simulation."""

from __future__ import annotations

from copy import deepcopy
from statistics import mean
from typing import Any

from app.database import db
from app.job_discovery.service import JobDiscoveryService
from app.job_providers.registry import get_default_providers
from app.matching.engine import JobMatchingEngine
from app.schemas.career_intelligence import (
    SimulationComparisonItem,
    SimulationRequest,
    SimulationResponse,
    SimulationSummary,
)


class SkillSimulator:
    """Compare baseline and hypothetical matches without persistence."""

    def __init__(self, discovery: JobDiscoveryService | None = None) -> None:
        self.discovery = discovery or JobDiscoveryService(providers=get_default_providers())
        self.matcher = JobMatchingEngine()

    async def _load_resume(self, request: SimulationRequest) -> dict[str, Any]:
        if request.resume is not None:
            return deepcopy(request.resume)
        resume = await db.get_resume(request.resume_id or "")
        if resume is None:
            raise LookupError("Resume not found")
        processed = resume.get("processed_data")
        if not isinstance(processed, dict):
            raise ValueError("Resume has no structured data available for simulation")
        return deepcopy(processed)

    async def _load_jobs(self, request: SimulationRequest) -> list[dict[str, Any]]:
        if request.job_ids:
            jobs: list[dict[str, Any]] = []
            for job_id in request.job_ids:
                job = await self.discovery.get_job(job_id)
                if job is None:
                    raise LookupError(f"Job not found: {job_id}")
                jobs.append(deepcopy(job))
            return jobs
        return [deepcopy(job) for job in await self.discovery.discover_jobs_async(request.criteria, persist=False)]

    @staticmethod
    def _skills(result: dict[str, Any], key: str, fallback: str) -> list[str]:
        values = result.get(key)
        if isinstance(values, list):
            return [str(value) for value in values]
        fallback_values = result.get(fallback, [])
        return [str(value) for value in fallback_values] if isinstance(fallback_values, list) else []

    @staticmethod
    def _summary(scores: list[int]) -> SimulationSummary:
        return SimulationSummary(
            jobs_analyzed=len(scores),
            average_score=round(mean(scores), 2) if scores else 0,
            average_score_delta=0,
        )

    async def simulate(self, request: SimulationRequest) -> SimulationResponse:
        original_resume = await self._load_resume(request)
        jobs = await self._load_jobs(request)
        simulated_resume = deepcopy(original_resume)
        additions = [skill.strip() for skill in request.hypothetical_skills if skill.strip()]
        additional = simulated_resume.setdefault("additional", {})
        existing_skills = list(simulated_resume.get("skills", []) or [])
        technical_skills = list(additional.get("technicalSkills", []) or [])
        for skill in additions:
            if skill.casefold() not in {str(item).casefold() for item in existing_skills + technical_skills}:
                technical_skills.append(skill)
        additional["technicalSkills"] = technical_skills
        if request.hypothetical_experience:
            experience_key = "experience" if "experience" in simulated_resume else "workExperience"
            simulated_resume.setdefault(experience_key, []).append(
                {"description": request.hypothetical_experience}
            )
        if request.hypothetical_education:
            simulated_resume.setdefault("education", []).append({"degree": request.hypothetical_education})

        comparisons: list[SimulationComparisonItem] = []
        baseline_scores: list[int] = []
        simulated_scores: list[int] = []
        for job in jobs:
            baseline = self.matcher.match_resume_to_job(deepcopy(original_resume), deepcopy(job))
            simulated = self.matcher.match_resume_to_job(deepcopy(simulated_resume), deepcopy(job))
            baseline_score = int(baseline.get("overall_score", 0))
            simulated_score = int(simulated.get("overall_score", 0))
            baseline_scores.append(baseline_score)
            simulated_scores.append(simulated_score)
            comparisons.append(
                SimulationComparisonItem(
                    job_id=str(job.get("id") or job.get("job_id")),
                    job_title=str(job.get("title") or "Untitled Role"),
                    baseline_score=baseline_score,
                    baseline_matched_skills=self._skills(baseline, "matched_skills", "matched_requirements"),
                    baseline_missing_skills=self._skills(baseline, "missing_skills", "missing_requirements"),
                    simulated_score=simulated_score,
                    simulated_matched_skills=self._skills(simulated, "matched_skills", "matched_requirements"),
                    simulated_missing_skills=self._skills(simulated, "missing_skills", "missing_requirements"),
                    score_delta=simulated_score - baseline_score,
                )
            )

        original_summary = self._summary(baseline_scores)
        simulated_summary = self._summary(simulated_scores)
        simulated_summary.average_score_delta = round(
            simulated_summary.average_score - original_summary.average_score, 2
        )
        return SimulationResponse(
            original_summary=original_summary,
            simulated_summary=simulated_summary,
            comparisons=comparisons,
            hypothetical_additions={
                "skills": additions,
                "experience": request.hypothetical_experience,
                "education": request.hypothetical_education,
                "is_hypothetical": True,
            },
        )

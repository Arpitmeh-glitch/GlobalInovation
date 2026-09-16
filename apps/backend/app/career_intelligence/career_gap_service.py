"""Deterministic gap analysis grounded in candidate and provider data."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.job_discovery.service import JobDiscoveryService
from app.job_providers.registry import get_default_providers
from app.schemas.career_intelligence import CareerGapItem, CareerGapsResponse


class CareerGapService:
    """Analyze recurring job requirements without changing stored records."""

    def __init__(self, discovery: JobDiscoveryService | None = None) -> None:
        self.discovery = discovery or JobDiscoveryService(providers=get_default_providers())

    @staticmethod
    def _normalize(value: Any) -> str:
        return " ".join(str(value or "").lower().split())

    @classmethod
    def _resume_text(cls, resume: dict[str, Any]) -> str:
        values: list[str] = []

        def collect(value: Any) -> None:
            if isinstance(value, dict):
                for nested in value.values():
                    collect(nested)
            elif isinstance(value, list):
                for nested in value:
                    collect(nested)
            elif value is not None:
                values.append(str(value))

        collect(resume)
        return cls._normalize(" ".join(values))

    @classmethod
    def _declared_resume_values(cls, resume: dict[str, Any]) -> set[str]:
        additional = resume.get("additional", {}) or {}
        values = list(resume.get("skills", []) or [])
        values.extend(additional.get("technicalSkills", []) or [])
        values.extend(resume.get("certifications", []) or [])
        values.extend(additional.get("certificationsTraining", []) or [])
        return {cls._normalize(value) for value in values if cls._normalize(value)}

    @staticmethod
    def _recommendation(name: str, gap_type: str) -> str:
        if gap_type == "evidence_gap":
            return f"Add verified resume evidence for {name}, such as a concrete project, work example, or credential you genuinely completed."
        return f"Build a small project or complete a relevant course or certification for {name} before claiming it as a skill."

    async def analyze(
        self,
        resume: dict[str, Any],
        *,
        criteria: dict[str, Any] | None = None,
        target_role: str | None = None,
    ) -> CareerGapsResponse:
        filters = dict(criteria or {})
        if target_role and "role" not in filters:
            filters["role"] = target_role
        jobs = await self.discovery.discover_jobs_async(criteria=filters, persist=False)
        resume_text = self._resume_text(resume)
        declared = self._declared_resume_values(resume)
        frequencies: Counter[str] = Counter()
        display_names: dict[str, str] = {}

        for job in jobs:
            for requirement in [*(job.get("skills_required", []) or []), *(job.get("skills_preferred", []) or [])]:
                normalized = self._normalize(requirement)
                if not normalized or normalized in declared:
                    continue
                frequencies[normalized] += 1
                display_names.setdefault(normalized, str(requirement))

        gaps: list[CareerGapItem] = []
        for normalized, frequency in frequencies.most_common():
            name = display_names[normalized]
            gap_type = "evidence_gap" if normalized in resume_text else "skill_gap"
            gaps.append(
                CareerGapItem(
                    name=name,
                    frequency=frequency,
                    gap_type=gap_type,
                    recommendation=self._recommendation(name, gap_type),
                )
            )

        return CareerGapsResponse(
            gaps=gaps,
            target_role=target_role or filters.get("role"),
            filters=filters,
            total_jobs_analyzed=len(jobs),
        )

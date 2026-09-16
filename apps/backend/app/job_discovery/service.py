"""Discovery service that aggregates provider results into one job feed."""

from __future__ import annotations

from typing import Any

from app.database import db
from app.job_providers.base import JobProvider
from app.job_providers.registry import get_default_providers


class JobDiscoveryService:
    """Provider-independent discovery orchestration for CareerPilot."""

    def __init__(self, providers: list[JobProvider] | None = None) -> None:
        self.providers = providers or get_default_providers()

    @staticmethod
    def _dedupe_key(job: dict[str, Any]) -> str:
        provider = str(job.get("provider") or "unknown")
        external_id = str(job.get("external_id") or job.get("id") or "")
        return f"{provider}:{external_id}"

    @staticmethod
    def _normalize_job(job: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(job)
        normalized.setdefault("provider", "demo")
        normalized.setdefault("external_id", normalized.get("id"))
        normalized.setdefault("id", normalized.get("external_id") or normalized.get("company") or "job")
        normalized.setdefault("company", "Unknown Company")
        normalized.setdefault("title", "Untitled Role")
        normalized.setdefault("description", "")
        normalized.setdefault("location", "Unknown")
        normalized.setdefault("work_mode", "remote")
        normalized.setdefault("employment_type", "full_time")
        normalized.setdefault("currency", "USD")
        normalized.setdefault("salary_min", None)
        normalized.setdefault("salary_max", None)
        normalized.setdefault("experience_required", None)
        normalized.setdefault("skills_required", [])
        normalized.setdefault("skills_preferred", [])
        normalized.setdefault("qualifications", [])
        normalized.setdefault("hard_requirements", [])
        normalized.setdefault("application_url", None)
        normalized.setdefault("posted_at", None)
        normalized.setdefault("discovered_at", None)
        normalized.setdefault("provider_metadata", {})
        normalized.setdefault("screening_questions", [])
        return normalized

    def discover_jobs(self, criteria: dict[str, Any] | None = None, *, persist: bool = True) -> list[dict[str, Any]]:
        criteria = criteria or {}
        seen: set[str] = set()
        jobs: list[dict[str, Any]] = []

        for provider in self.providers:
            for raw_job in provider.search_jobs(criteria=criteria):
                normalized = self._normalize_job(raw_job)
                dedupe_key = self._dedupe_key(normalized)
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                jobs.append(normalized)

        if persist:
            for job in jobs:
                db.upsert_careerpilot_job_sync(job)

        return jobs

    async def discover_jobs_async(
        self, criteria: dict[str, Any] | None = None, *, persist: bool = True
    ) -> list[dict[str, Any]]:
        jobs = self.discover_jobs(criteria=criteria, persist=False)
        if persist:
            for job in jobs:
                await db.upsert_careerpilot_job(job)
        return jobs

    async def get_job(self, job_id: str) -> dict[str, Any] | None:
        for provider in self.providers:
            job = provider.get_job_details(job_id)
            if job is not None:
                return self._normalize_job(job)
        return await db.get_job(job_id)

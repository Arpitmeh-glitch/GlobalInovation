"""Discovery service that aggregates provider results into one job feed."""

from __future__ import annotations

import re
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

    @staticmethod
    def _experience_bounds(value: Any) -> tuple[int | None, int | None]:
        numbers = [int(item) for item in re.findall(r"\d+", str(value or ""))]
        if not numbers:
            return None, None
        return numbers[0], numbers[1] if len(numbers) > 1 else numbers[0]

    @classmethod
    def _matches_generic_criteria(cls, job: dict[str, Any], criteria: dict[str, Any]) -> bool:
        minimum_salary = criteria.get("min_salary")
        maximum_salary = criteria.get("max_salary")
        salary_min = job.get("salary_min")
        salary_max = job.get("salary_max")
        if minimum_salary is not None and (salary_max is None or salary_max < int(minimum_salary)):
            return False
        if maximum_salary is not None and (salary_min is None or salary_min > int(maximum_salary)):
            return False

        minimum_experience = criteria.get("min_experience")
        maximum_experience = criteria.get("max_experience")
        experience_min, experience_max = cls._experience_bounds(job.get("experience_required"))
        if minimum_experience is not None and (experience_max is None or experience_max < int(minimum_experience)):
            return False
        if maximum_experience is not None and (experience_min is None or experience_min > int(maximum_experience)):
            return False
        return True

    @classmethod
    def _sort_jobs(cls, jobs: list[dict[str, Any]], criteria: dict[str, Any]) -> list[dict[str, Any]]:
        sort_by = str(criteria.get("sort_by") or "discovered_at")
        reverse = str(criteria.get("sort_order") or "desc").lower() != "asc"

        def sort_value(job: dict[str, Any]) -> Any:
            if sort_by == "salary":
                return job.get("salary_max") if reverse else job.get("salary_min")
            if sort_by == "title":
                return str(job.get("title") or "").lower()
            if sort_by == "company":
                return str(job.get("company") or "").lower()
            return str(job.get(sort_by) or "")

        present = [job for job in jobs if sort_value(job) is not None and sort_value(job) != ""]
        missing = [job for job in jobs if job not in present]
        present.sort(key=sort_value, reverse=reverse)
        return present + missing

    def discover_jobs(self, criteria: dict[str, Any] | None = None, *, persist: bool = True) -> list[dict[str, Any]]:
        criteria = criteria or {}
        seen: set[str] = set()
        jobs: list[dict[str, Any]] = []

        for provider in self.providers:
            for raw_job in provider.search_jobs(criteria=criteria):
                normalized = self._normalize_job(raw_job)
                if not self._matches_generic_criteria(normalized, criteria):
                    continue
                dedupe_key = self._dedupe_key(normalized)
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                jobs.append(normalized)

        if persist:
            for job in jobs:
                db.upsert_careerpilot_job_sync(job)

        return jobs

    @classmethod
    def paginate_jobs(
        cls, jobs: list[dict[str, Any]], criteria: dict[str, Any] | None = None
    ) -> tuple[list[dict[str, Any]], int, int, int, bool]:
        criteria = criteria or {}
        ordered = cls._sort_jobs(jobs, criteria)
        total = len(ordered)
        offset = max(0, int(criteria.get("offset") or 0))
        raw_limit = criteria.get("limit")
        limit = max(1, min(100, int(raw_limit))) if raw_limit is not None else total
        page = ordered[offset : offset + limit]
        return page, total, offset, limit, offset + len(page) < total

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

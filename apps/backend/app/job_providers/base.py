"""Provider abstraction for normalized job discovery."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class JobProvider(ABC):
    """Base interface for job-source integrations.

    Provider implementations must return normalized CareerPilot jobs, never
    provider-specific payloads. This keeps the rest of the application isolated
    from provider quirks and lets the dashboard show a single job model.
    """

    provider_name: str = "base"

    @abstractmethod
    def search_jobs(self, criteria: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Return a list of normalized jobs for the supplied search criteria."""

    @abstractmethod
    def get_job_details(self, job_id: str) -> dict[str, Any] | None:
        """Return a single normalized job by provider-specific id."""

    def supports_application(self) -> bool:
        return False

    def prepare_application(self, *, job: dict[str, Any], resume: dict[str, Any]) -> dict[str, Any]:
        return {
            "provider": self.provider_name,
            "job_id": job.get("id"),
            "resume_id": resume.get("resume_id"),
            "application_url": job.get("application_url"),
            "status": "draft",
        }

    def submit_application(self, *, application: dict[str, Any]) -> dict[str, Any]:
        return {
            "provider": application.get("provider"),
            "job_id": application.get("job_id"),
            "status": "demo-only",
            "message": "Demo mode only: no real employer submission is being performed.",
        }

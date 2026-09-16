"""Deterministic and isolated CareerPilot demo workspace."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from sqlalchemy import delete

from app.audit.event_store import log_activity
from app.database import db
from app.job_providers.demo import DemoProvider
from app.models import AgentActivity
from app.schemas.demo_mode import DemoResetResponse, DemoStatusResponse


class DemoModeManager:
    """Own demo fixtures without persisting or mutating real CareerPilot data."""

    DEMO_USER_ID = "demo-user-careerpilot"
    SEEDED_AT = "2026-01-01T00:00:00+00:00"
    SCENARIOS = ("default", "cloud_security", "software_engineering")

    _profiles: dict[str, dict[str, Any]] = {
        "default": {
            "profile_id": "demo-profile-default",
            "user_id": DEMO_USER_ID,
            "target_role": "Backend Engineer",
            "skills": ["Python", "SQL", "Cloud fundamentals"],
            "experience_level": "entry",
            "years_experience": 1,
            "education": "Bachelor of Computer Science",
            "preferred_locations": ["Remote", "Bengaluru"],
            "work_preference": "remote",
            "industries": ["Software", "Cloud"],
            "salary_expectation": 600000,
        },
        "cloud_security": {
            "profile_id": "demo-profile-cloud-security",
            "user_id": DEMO_USER_ID,
            "target_role": "Cloud Security Engineer",
            "skills": ["Python", "AWS", "Linux", "Cloud Security"],
            "experience_level": "entry",
            "years_experience": 1,
            "education": "Bachelor of Computer Science",
            "preferred_locations": ["Remote", "Bengaluru"],
            "work_preference": "remote",
            "industries": ["Cybersecurity", "Cloud"],
            "salary_expectation": 800000,
        },
        "software_engineering": {
            "profile_id": "demo-profile-software-engineering",
            "user_id": DEMO_USER_ID,
            "target_role": "Software Engineer",
            "skills": ["Python", "SQL", "Git", "REST APIs"],
            "experience_level": "entry",
            "years_experience": 1,
            "education": "Bachelor of Computer Science",
            "preferred_locations": ["Remote"],
            "work_preference": "remote",
            "industries": ["Software"],
            "salary_expectation": 600000,
        },
    }
    _activity_fixtures = (
        ("demo_event", "demo_workspace_initialized", "success", {"source": "demo", "sequence": 1}),
        ("demo_event", "demo_jobs_loaded", "success", {"provider": "demo", "sequence": 2}),
        ("demo_event", "demo_match_ready", "success", {"hypothetical": False, "sequence": 3}),
    )

    def __init__(self) -> None:
        self._scenario = "default"
        self._seeded_at: str | None = None
        self._activities: list[dict[str, Any]] = []

    async def _clear_demo_activities(self) -> None:
        async with db._write_session() as session:
            await session.execute(
                delete(AgentActivity).where(AgentActivity.user_id == self.DEMO_USER_ID)
            )
            await session.commit()

    async def reset_demo_state(self, scenario: str = "default") -> DemoResetResponse:
        """Reset only demo-scoped state to fixed fixtures; real records are untouched."""
        if scenario not in self.SCENARIOS:
            raise ValueError(f"Unknown demo scenario: {scenario}")

        await self._clear_demo_activities()
        seeded: list[dict[str, Any]] = []
        for sequence, (activity_type, action, status, details) in enumerate(self._activity_fixtures, 1):
            await log_activity(
                activity_type,
                action,
                details,
                user_id=self.DEMO_USER_ID,
                status=status,
                created_at=f"2026-01-01T00:00:0{sequence}+00:00",
            )
            seeded.append(
                {
                    "id": sequence,
                    "user_id": self.DEMO_USER_ID,
                    "activity_type": activity_type,
                    "action": action,
                    "details": deepcopy(details),
                    "status": status,
                    "created_at": f"2026-01-01T00:00:0{sequence}+00:00",
                }
            )
        self._scenario = scenario
        self._seeded_at = self.SEEDED_AT
        self._activities = seeded
        return DemoResetResponse(
            status="reset",
            message="Demo mode reset completed. Real user data was not modified.",
            demo_profile_id=self._profiles[scenario]["profile_id"],
            seeded_jobs_count=len(DemoProvider().search_jobs({})),
            seeded_activities_count=len(seeded),
        )

    async def get_demo_status(self) -> DemoStatusResponse:
        return DemoStatusResponse(
            is_demo_mode=True,
            demo_user_id=self.DEMO_USER_ID,
            seeded_at=self._seeded_at,
            demo_scenario=self._scenario,
            metadata={
                "isolated": True,
                "persistence": "demo_activity_events_only",
                "real_data_mutated": False,
                "available_scenarios": list(self.SCENARIOS),
            },
        )

    async def get_demo_profile(self) -> dict[str, Any]:
        return deepcopy(self._profiles[self._scenario])

    async def get_demo_jobs(self) -> list[dict[str, Any]]:
        return deepcopy(DemoProvider().search_jobs({}))

    async def get_demo_activities(self) -> list[dict[str, Any]]:
        return deepcopy(self._activities) if self._seeded_at is not None else []
"""API schemas for deterministic CareerPilot demo mode."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DemoStatusResponse(BaseModel):
    is_demo_mode: bool
    demo_user_id: str
    seeded_at: str | None = None
    demo_scenario: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class DemoResetRequest(BaseModel):
    scenario: str = Field(default="default", min_length=1, max_length=60)
    force_clean: bool = True


class DemoResetResponse(BaseModel):
    status: str
    message: str
    demo_profile_id: str
    seeded_jobs_count: int = Field(ge=0)
    seeded_activities_count: int = Field(ge=0)


class DemoHealthResponse(BaseModel):
    status: DemoStatusResponse
    available_scenarios: list[str]
    profile_preview: dict[str, Any]
    activity_count: int
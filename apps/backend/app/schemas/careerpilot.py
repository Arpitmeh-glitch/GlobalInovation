"""Pydantic models for the CareerPilot vertical slice."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CareerPilotJob(BaseModel):
    id: str
    external_id: str | None = None
    provider: str = "demo"
    company: str
    title: str
    description: str
    location: str | None = None
    work_mode: str | None = None
    employment_type: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    currency: str | None = None
    experience_required: str | None = None
    skills_required: list[str] = Field(default_factory=list)
    skills_preferred: list[str] = Field(default_factory=list)
    qualifications: list[str] = Field(default_factory=list)
    hard_requirements: list[str] = Field(default_factory=list)
    application_url: str | None = None
    posted_at: str | None = None
    discovered_at: str | None = None
    provider_metadata: dict[str, Any] = Field(default_factory=dict)
    screening_questions: list[dict[str, Any]] = Field(default_factory=list)
    match: "CareerPilotMatchResult | None" = None


class CareerPilotDiscoveryRequest(BaseModel):
    criteria: dict[str, Any] = Field(default_factory=dict)
    persist: bool = True


class CareerPilotProfileInput(BaseModel):
    target_role: str = Field(min_length=2, max_length=120)
    skills: list[str] = Field(default_factory=list, max_length=40)
    experience_level: str = Field(min_length=1, max_length=40)
    years_experience: int | None = Field(default=None, ge=0, le=70)
    education: str | None = Field(default=None, max_length=200)
    preferred_locations: list[str] = Field(default_factory=list, max_length=20)
    work_preference: str = Field(default="remote", pattern="^(remote|hybrid|onsite)$")
    industries: list[str] = Field(default_factory=list, max_length=20)
    salary_expectation: int | None = Field(default=None, ge=0, le=100_000_000)


class CareerPilotProfileResponse(CareerPilotProfileInput):
    profile_id: str
    created_at: str
    updated_at: str


class CareerPilotDiscoveryResponse(BaseModel):
    jobs: list[CareerPilotJob]
    total: int
    demo_mode: bool = True


class CareerPilotMatchResult(BaseModel):
    overall_score: int
    recommendation: str
    matched_requirements: list[str] = Field(default_factory=list)
    partially_matched_requirements: list[str] = Field(default_factory=list)
    missing_requirements: list[str] = Field(default_factory=list)
    hard_requirement_failures: list[str] = Field(default_factory=list)
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    score_breakdown: dict[str, int] = Field(default_factory=dict)


class CareerPilotJobMatchResponse(BaseModel):
    job: CareerPilotJob
    match: CareerPilotMatchResult


class CareerPilotJobDetailResponse(BaseModel):
    job: CareerPilotJob

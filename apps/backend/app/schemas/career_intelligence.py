"""Schemas for CareerPilot career-gap analysis and hypothetical simulations."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class CareerGapItem(BaseModel):
    name: str
    frequency: int = Field(ge=1)
    gap_type: Literal["skill_gap", "evidence_gap"]
    recommendation: str


class CareerGapsResponse(BaseModel):
    gaps: list[CareerGapItem]
    target_role: str | None = None
    filters: dict[str, Any] = Field(default_factory=dict)
    total_jobs_analyzed: int = Field(ge=0)


class SimulationRequest(BaseModel):
    resume_id: str | None = None
    resume: dict[str, Any] | None = None
    job_ids: list[str] = Field(default_factory=list, max_length=100)
    criteria: dict[str, Any] | None = None
    hypothetical_skills: list[str] = Field(default_factory=list, max_length=40)
    hypothetical_experience: str | None = Field(default=None, max_length=500)
    hypothetical_education: str | None = Field(default=None, max_length=300)

    @model_validator(mode="after")
    def require_resume_and_jobs(self) -> "SimulationRequest":
        if self.resume_id is None and self.resume is None:
            raise ValueError("Provide resume_id or resume")
        if not self.job_ids and not self.criteria:
            raise ValueError("Provide job_ids or criteria")
        return self


class SimulationComparisonItem(BaseModel):
    job_id: str
    job_title: str
    baseline_score: int
    baseline_matched_skills: list[str] = Field(default_factory=list)
    baseline_missing_skills: list[str] = Field(default_factory=list)
    simulated_score: int
    simulated_matched_skills: list[str] = Field(default_factory=list)
    simulated_missing_skills: list[str] = Field(default_factory=list)
    score_delta: int
    is_hypothetical: Literal[True] = True


class SimulationSummary(BaseModel):
    jobs_analyzed: int = Field(ge=0)
    average_score: float = Field(ge=0, le=100)
    average_score_delta: float


class SimulationResponse(BaseModel):
    original_summary: SimulationSummary
    simulated_summary: SimulationSummary
    comparisons: list[SimulationComparisonItem]
    hypothetical_additions: dict[str, Any] = Field(default_factory=dict)

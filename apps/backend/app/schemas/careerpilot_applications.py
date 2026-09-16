"""Schemas for CareerPilot preparation and approval."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PrepareApplicationRequest(BaseModel):
    resume_id: str | None = None
    prompt_id: str | None = None


class ScreeningAnswerUpdate(BaseModel):
    answers: dict[str, str | int | bool] = Field(default_factory=dict)


class CoverLetterUpdate(BaseModel):
    content: str = ""


class CareerPilotApplicationResponse(BaseModel):
    application_id: str
    job_id: str
    source_resume_id: str
    original_resume_id: str
    tailored_resume_id: str
    status: str
    tracker_status: str
    company: str | None = None
    role: str | None = None
    application_url: str | None = None
    provider: str | None = None
    match: dict[str, Any] = Field(default_factory=dict)
    changes: list[dict[str, Any]] = Field(default_factory=list)
    claim_validation: dict[str, Any] = Field(default_factory=dict)
    screening_questions: list[dict[str, Any]] = Field(default_factory=list)
    cover_letter: str | None = None
    needs_review: bool = False
    demo_mode: bool = True
    events: list[dict[str, Any]] = Field(default_factory=list)


class CareerPilotApplicationEventResponse(BaseModel):
    events: list[dict[str, Any]]


class ApprovalResponse(BaseModel):
    application_id: str
    status: str
    tracker_status: str
    message: str

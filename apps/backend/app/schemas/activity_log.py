"""API schemas for CareerPilot activity logs."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ActivityLogCreate(BaseModel):
    user_id: str | None = Field(default=None, max_length=120)
    activity_type: str = Field(min_length=1, max_length=80)
    action: str = Field(min_length=1, max_length=200)
    details: dict[str, Any] = Field(default_factory=dict)
    status: Literal["success", "failure"] = "success"


class ActivityLogResponse(ActivityLogCreate):
    id: int
    created_at: str


class ActivityLogQueryParams(BaseModel):
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    activity_type: str | None = Field(default=None, max_length=80)
    user_id: str | None = Field(default=None, max_length=120)


class ActivityLogListResponse(BaseModel):
    activities: list[ActivityLogResponse]
    limit: int
    offset: int
    count: int
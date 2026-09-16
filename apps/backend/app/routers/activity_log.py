"""CareerPilot audit activity endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.audit.event_store import get_activities
from app.schemas.activity_log import ActivityLogListResponse, ActivityLogQueryParams

router = APIRouter(prefix="/careerpilot", tags=["CareerPilot Activity Log"])


@router.get("/activity-log", response_model=ActivityLogListResponse)
async def list_activity_log(
    query: ActivityLogQueryParams = Depends(),
) -> ActivityLogListResponse:
    activities = await get_activities(
        activity_type=query.activity_type,
        user_id=query.user_id,
        limit=query.limit,
        offset=query.offset,
    )
    return ActivityLogListResponse(
        activities=activities,
        limit=query.limit,
        offset=query.offset,
        count=len(activities),
    )
"""CareerPilot deterministic demo-mode endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.agent.demo_mode import DemoModeManager
from app.schemas.demo_mode import DemoHealthResponse, DemoResetRequest, DemoResetResponse

router = APIRouter(prefix="/careerpilot", tags=["CareerPilot Demo Mode"])
manager = DemoModeManager()


@router.get("/demo", response_model=DemoHealthResponse)
async def demo_status() -> DemoHealthResponse:
    status = await manager.get_demo_status()
    activities = await manager.get_demo_activities()
    return DemoHealthResponse(
        status=status,
        available_scenarios=list(manager.SCENARIOS),
        profile_preview=await manager.get_demo_profile(),
        activity_count=len(activities),
    )


@router.post("/demo/reset", response_model=DemoResetResponse)
async def reset_demo(request: DemoResetRequest) -> DemoResetResponse:
    if not request.force_clean:
        raise HTTPException(status_code=400, detail="Demo reset requires force_clean=true.")
    try:
        return await manager.reset_demo_state(request.scenario)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
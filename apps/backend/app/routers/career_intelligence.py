"""CareerPilot gap analysis and what-if simulation routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.career_intelligence.career_gap_service import CareerGapService
from app.career_intelligence.simulator import SkillSimulator
from app.database import db
from app.matching.resume_context import get_matching_resume
from app.schemas.career_intelligence import CareerGapsResponse, SimulationRequest, SimulationResponse

router = APIRouter(prefix="/careerpilot", tags=["CareerPilot Intelligence"])


async def _resume_for_request(resume_id: str | None) -> dict[str, Any]:
    try:
        resume = await get_matching_resume(resume_id)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    processed = resume.get("processed_data")
    if not isinstance(processed, dict):
        raise HTTPException(status_code=409, detail="Resume has no structured data available.")
    return processed


@router.get("/gaps", response_model=CareerGapsResponse)
async def career_gaps(
    resume_id: str | None = Query(default=None),
    role: str | None = Query(default=None, max_length=120),
    location: str | None = Query(default=None, max_length=120),
    work_mode: str | None = Query(default=None, pattern="^(remote|hybrid|onsite)$"),
    employment_type: str | None = Query(default=None, max_length=40),
) -> CareerGapsResponse:
    resume = await _resume_for_request(resume_id)
    criteria = {
        key: value
        for key, value in {
            "location": location,
            "work_mode": work_mode,
            "employment_type": employment_type,
        }.items()
        if value is not None
    }
    try:
        return await CareerGapService().analyze(resume, criteria=criteria, target_role=role)
    except Exception as error:
        raise HTTPException(status_code=503, detail="Career gap analysis is currently unavailable.") from error


@router.post("/simulate", response_model=SimulationResponse)
async def simulate_career_change(request: SimulationRequest) -> SimulationResponse:
    try:
        return await SkillSimulator().simulate(request)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail="Career simulation is currently unavailable.") from error

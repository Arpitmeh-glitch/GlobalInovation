"""CareerPilot routes for discovery, ranking, and job analysis."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.database import DatabaseBusyError, db
from app.applications.service import (
    get_application_review,
    prepare_application,
    regenerate_cover_letter,
    update_cover_letter,
    update_screening_answers,
)
from app.job_discovery.service import JobDiscoveryService
from app.job_providers.registry import get_default_providers
from app.matching.engine import JobMatchingEngine
from app.matching.resume_context import get_matching_resume
from app.schemas.careerpilot import (
    CareerPilotDiscoveryRequest,
    CareerPilotDiscoveryResponse,
    CareerPilotJob,
    CareerPilotJobDetailResponse,
    CareerPilotJobMatchResponse,
    CareerPilotProfileInput,
    CareerPilotProfileResponse,
)
from app.schemas.careerpilot_applications import (
    ApprovalResponse,
    CareerPilotApplicationEventResponse,
    CareerPilotApplicationResponse,
    CoverLetterUpdate,
    PrepareApplicationRequest,
    ScreeningAnswerUpdate,
)

router = APIRouter(prefix="/careerpilot", tags=["CareerPilot"])
logger = logging.getLogger(__name__)


def _discovery_response(
    jobs: list[dict[str, Any]], criteria: dict[str, Any]
) -> CareerPilotDiscoveryResponse:
    page, total, offset, limit, has_more = JobDiscoveryService.paginate_jobs(jobs, criteria)
    return CareerPilotDiscoveryResponse(
        jobs=[CareerPilotJob.model_validate(job) for job in page],
        total=total,
        offset=offset,
        limit=limit,
        has_more=has_more,
        demo_mode=True,
    )


def _query_criteria(
    role: str | None,
    location: str | None,
    work_mode: str | None,
    employment_type: str | None,
    min_salary: int | None,
    max_salary: int | None,
    min_experience: int | None,
    max_experience: int | None,
    sort_by: str,
    sort_order: str,
    offset: int,
    limit: int,
) -> dict[str, Any]:
    return {
        key: value
        for key, value in {
            "role": role,
            "location": location,
            "work_mode": work_mode,
            "employment_type": employment_type,
            "min_salary": min_salary,
            "max_salary": max_salary,
            "min_experience": min_experience,
            "max_experience": max_experience,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "offset": offset,
            "limit": limit,
        }.items()
        if value is not None
    }


def _careerpilot_job_payload(job: dict[str, Any]) -> dict[str, Any]:
    payload = dict(job)
    payload["id"] = payload.get("id") or payload.get("job_id")
    return payload


def _profile_resume_data(profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "skills": profile.get("skills", []),
        "summary": profile.get("target_role", ""),
        "experience": [
            {"title": profile.get("target_role", ""), "years": profile.get("years_experience")}
        ],
        "education": [{"degree": profile.get("education", "")}],
    }


async def _matching_resume(resume_id: str | None = None) -> dict[str, Any]:
    try:
        return await get_matching_resume(resume_id)
    except ValueError:
        profile = await db.get_careerpilot_profile()
        if profile is None:
            raise
        return {"resume_id": "careerpilot-profile", "processed_data": _profile_resume_data(profile)}


async def _job_with_match(job: dict[str, Any]) -> dict[str, Any]:
    try:
        resume = await _matching_resume()
    except ValueError:
        return _careerpilot_job_payload(job)
    payload = _careerpilot_job_payload(job)
    payload["match"] = JobMatchingEngine().match_resume_to_job(resume.get("processed_data"), job)
    return payload


@router.get("/profile", response_model=CareerPilotProfileResponse | None)
async def get_profile() -> CareerPilotProfileResponse | None:
    profile = await db.get_careerpilot_profile()
    return CareerPilotProfileResponse.model_validate(profile) if profile else None


@router.put("/profile", response_model=CareerPilotProfileResponse)
async def save_profile(request: CareerPilotProfileInput) -> CareerPilotProfileResponse:
    values = request.model_dump()
    for field in ("skills", "preferred_locations", "industries"):
        values[field] = [item.strip() for item in values[field] if item.strip()]
    saved = await db.upsert_careerpilot_profile(values)
    return CareerPilotProfileResponse.model_validate(saved)


@router.get("/jobs", response_model=CareerPilotDiscoveryResponse)
async def list_jobs(
    role: str | None = Query(default=None),
    location: str | None = Query(default=None),
    work_mode: str | None = Query(default=None),
    employment_type: str | None = Query(default=None),
    min_salary: int | None = Query(default=None, ge=0),
    max_salary: int | None = Query(default=None, ge=0),
    min_experience: int | None = Query(default=None, ge=0),
    max_experience: int | None = Query(default=None, ge=0),
    sort_by: str = Query(default="discovered_at"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> CareerPilotDiscoveryResponse:
    criteria = _query_criteria(
        role, location, work_mode, employment_type, min_salary, max_salary,
        min_experience, max_experience, sort_by, sort_order, offset, limit,
    )
    service = JobDiscoveryService(providers=get_default_providers())
    try:
        jobs = await service.discover_jobs_async(criteria=criteria, persist=True)
    except DatabaseBusyError:
        raise
    except Exception as error:
        logger.exception("CareerPilot provider discovery failed")
        raise HTTPException(status_code=503, detail="Job providers are currently unavailable.") from error
    jobs = [await _job_with_match(job) for job in jobs]
    if sort_by == "match_score":
        jobs.sort(key=lambda job: (job.get("match") or {}).get("overall_score", -1), reverse=sort_order == "desc")
    return _discovery_response(jobs, criteria)


@router.post("/jobs/discover", response_model=CareerPilotDiscoveryResponse)
async def discover_jobs(request: CareerPilotDiscoveryRequest) -> CareerPilotDiscoveryResponse:
    service = JobDiscoveryService(providers=get_default_providers())
    criteria = request.criteria.model_dump(exclude_none=True)
    try:
        jobs = await service.discover_jobs_async(criteria=criteria, persist=request.persist)
    except DatabaseBusyError:
        raise
    except Exception as error:
        logger.exception("CareerPilot provider discovery failed")
        raise HTTPException(status_code=503, detail="Job providers are currently unavailable.") from error
    jobs = [await _job_with_match(job) for job in jobs]
    if criteria.get("sort_by") == "discovered_at":
        criteria["sort_by"] = "match_score"
        jobs.sort(key=lambda job: (job.get("match") or {}).get("overall_score", -1), reverse=True)
    return _discovery_response(jobs, criteria)


@router.get("/jobs/{job_id}", response_model=CareerPilotJobDetailResponse)
async def get_job(job_id: str) -> CareerPilotJobDetailResponse:
    job = await db.get_job(job_id)
    if job is None:
        service = JobDiscoveryService(providers=get_default_providers())
        job = await service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="CareerPilot job not found")
    return CareerPilotJobDetailResponse(job=CareerPilotJob.model_validate(_careerpilot_job_payload(job)))


@router.get("/jobs/{job_id}/match", response_model=CareerPilotJobMatchResponse)
async def match_job(
    job_id: str,
    resume_id: str | None = Query(default=None),
) -> CareerPilotJobMatchResponse:
    job = await db.get_job(job_id)
    if job is None:
        service = JobDiscoveryService(providers=get_default_providers())
        job = await service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="CareerPilot job not found")
    try:
        resume = await _matching_resume(resume_id)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    match_result = JobMatchingEngine().match_resume_to_job(
        resume.get("processed_data"), job
    )
    return CareerPilotJobMatchResponse(
        job=CareerPilotJob.model_validate(_careerpilot_job_payload(job)),
        match=match_result,
    )


@router.post("/jobs/{job_id}/prepare", response_model=CareerPilotApplicationResponse)
async def prepare_job_application(
    job_id: str, request: PrepareApplicationRequest
) -> CareerPilotApplicationResponse:
    """Prepare a reviewable application using Resume Matcher tailoring."""
    try:
        result = await prepare_application(job_id, request)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return CareerPilotApplicationResponse.model_validate(result)


@router.get("/applications/{application_id}/review", response_model=CareerPilotApplicationResponse)
async def application_review(application_id: str) -> CareerPilotApplicationResponse:
    try:
        result = await get_application_review(application_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return CareerPilotApplicationResponse.model_validate(result)


@router.patch("/applications/{application_id}/screening", response_model=CareerPilotApplicationResponse)
async def answer_screening_questions(
    application_id: str, request: ScreeningAnswerUpdate
) -> CareerPilotApplicationResponse:
    try:
        result = await update_screening_answers(application_id, request.answers)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return CareerPilotApplicationResponse.model_validate(result)


@router.patch("/applications/{application_id}/cover-letter", response_model=CareerPilotApplicationResponse)
async def save_cover_letter(
    application_id: str, request: CoverLetterUpdate
) -> CareerPilotApplicationResponse:
    try:
        result = await update_cover_letter(application_id, request.content)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return CareerPilotApplicationResponse.model_validate(result)


@router.post(
    "/applications/{application_id}/cover-letter/regenerate",
    response_model=CareerPilotApplicationResponse,
)
async def regenerate_application_cover_letter(
    application_id: str,
) -> CareerPilotApplicationResponse:
    try:
        result = await regenerate_cover_letter(application_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="Cover letter generation is currently unavailable.",
        ) from error
    return CareerPilotApplicationResponse.model_validate(result)


@router.post("/applications/{application_id}/approve", response_model=ApprovalResponse)
async def approve_application(application_id: str) -> ApprovalResponse:
    try:
        review = await get_application_review(application_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    if review["needs_review"]:
        raise HTTPException(status_code=409, detail="Unsupported claims require review before approval.")
    missing = [
        question["question_id"]
        for question in review["screening_questions"]
        if question.get("status") == "USER_INPUT_REQUIRED" and not str(question.get("answer") or "").strip()
    ]
    if missing:
        raise HTTPException(status_code=409, detail="Answer all required screening questions before approval.")
    updated = await db.update_application_metadata(
        application_id,
        {"draft_status": "APPROVED", "tracker_status": "applied"},
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Application not found")
    await db.update_application(application_id, {"status": "applied"})
    await db.create_application_event(application_id, "USER_APPROVED", {})
    return ApprovalResponse(
        application_id=application_id,
        status="APPROVED",
        tracker_status="applied",
        message="Application approved and ready for submission.",
    )


@router.post("/applications/{application_id}/reject", response_model=ApprovalResponse)
async def reject_application(application_id: str) -> ApprovalResponse:
    updated = await db.update_application_metadata(
        application_id,
        {"draft_status": "REJECTED", "tracker_status": "rejected"},
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Application not found")
    await db.update_application(application_id, {"status": "rejected"})
    await db.create_application_event(application_id, "DRAFT_REJECTED", {})
    return ApprovalResponse(
        application_id=application_id,
        status="REJECTED",
        tracker_status="rejected",
        message="Application draft rejected.",
    )


@router.get("/applications/{application_id}/events", response_model=CareerPilotApplicationEventResponse)
async def application_events(application_id: str) -> CareerPilotApplicationEventResponse:
    if await db.get_application(application_id) is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return CareerPilotApplicationEventResponse(
        events=await db.list_application_events(application_id)
    )

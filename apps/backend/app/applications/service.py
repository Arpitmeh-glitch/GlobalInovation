"""Phase 2 application preparation orchestration."""

from __future__ import annotations

from typing import Any

from app.applications.claim_validator import validate_tailored_claims
from app.applications.screening import prepare_screening_questions, validate_screening_answers
from app.config_cache import get_content_language
from app.database import db
from app.job_discovery.service import JobDiscoveryService
from app.job_providers.registry import get_default_providers
from app.matching.engine import JobMatchingEngine
from app.matching.resume_context import get_matching_resume
from app.services.cover_letter import generate_cover_letter
from app.schemas.careerpilot_applications import PrepareApplicationRequest
from app.schemas.models import ImproveResumeConfirmRequest, ImproveResumeRequest


async def _find_or_create_tracker_application(
    job: dict[str, Any], source_resume: dict[str, Any], request: PrepareApplicationRequest
) -> dict[str, Any]:
    """Tailor through Resume Matcher and reuse its tracker card."""
    from app.routers.resumes import (
        improve_resume_confirm_endpoint,
        improve_resume_preview_endpoint,
    )

    existing = await db.find_careerpilot_application(job["id"], source_resume["resume_id"])
    if existing is not None:
        return existing

    preview = await improve_resume_preview_endpoint(
        ImproveResumeRequest(
            resume_id=source_resume["resume_id"],
            job_id=job["id"],
            prompt_id=request.prompt_id,
        )
    )
    preview_data = preview.data
    confirmed = await improve_resume_confirm_endpoint(
        ImproveResumeConfirmRequest(
            resume_id=source_resume["resume_id"],
            job_id=job["id"],
            preview_id=preview_data.preview_id,
            improved_data=preview_data.resume_preview,
            improvements=preview_data.improvements,
        )
    )
    tailored_resume_id = confirmed.data.resume_id
    if not tailored_resume_id:
        raise ValueError("Tailoring completed without a saved resume")

    applications = await db.list_applications()
    for application in applications:
        if application["job_id"] == job["id"] and application["resume_id"] == tailored_resume_id:
            return application
    return await db.create_application(
        job_id=job["id"],
        resume_id=tailored_resume_id,
        master_resume_id=source_resume["resume_id"],
        status="saved",
        company=job.get("company"),
        role=job.get("title"),
    )


async def prepare_application(
    job_id: str, request: PrepareApplicationRequest
) -> dict[str, Any]:
    """Create an evidence-checked draft using the existing tailoring pipeline."""
    job = await db.get_job(job_id)
    if job is None:
        service = JobDiscoveryService(providers=get_default_providers())
        job = await service.get_job(job_id)
    if job is None:
        raise LookupError("CareerPilot job not found")
    job = dict(job)
    job["id"] = job.get("id") or job.get("job_id")

    source_resume = await get_matching_resume(request.resume_id)
    application = await _find_or_create_tracker_application(job, source_resume, request)
    tailored_resume = await db.get_resume(application["resume_id"])
    if tailored_resume is None:
        raise LookupError("Tailored resume is no longer available")

    original_data = source_resume.get("processed_data") or {}
    tailored_data = tailored_resume.get("processed_data") or {}
    claim_validation = validate_tailored_claims(original_data, tailored_data, job)
    match = JobMatchingEngine().match_resume_to_job(original_data, job)
    changes = _changes_from_resume_diff(application, source_resume, tailored_resume)
    questions = prepare_screening_questions(
        job.get("screening_questions", []), original_data
    )
    missing_questions = validate_screening_answers(questions)
    needs_review = bool(claim_validation["needs_review"])
    metadata = {
        "source_resume_id": source_resume["resume_id"],
        "original_resume_id": source_resume["resume_id"],
        "tailored_resume_id": tailored_resume["resume_id"],
        "draft_status": "AWAITING_APPROVAL" if not needs_review else "DRAFT_READY",
        "tracker_status": "saved",
        "match": match,
        "match_score": match["overall_score"],
        "source": "DemoProvider" if job.get("provider") == "demo" else job.get("provider"),
        "review_url": f"/applications/{application['application_id']}/review",
        "changes": changes,
        "claim_validation": claim_validation,
        "screening_questions": questions,
        "missing_screening_answers": missing_questions,
        "cover_letter": tailored_resume.get("cover_letter"),
        "needs_review": needs_review,
        "demo_mode": job.get("provider") == "demo",
    }
    application = await db.update_application_metadata(application["application_id"], metadata)
    assert application is not None
    await db.update_application(application["application_id"], {"status": "saved"})
    await db.create_application_event(application["application_id"], "JOB_DISCOVERED", {"provider": job.get("provider")})
    await db.create_application_event(application["application_id"], "MATCH_ANALYZED", {"score": match["overall_score"]})
    await db.create_application_event(application["application_id"], "APPLICATION_PREPARED", {"job_id": job_id})
    await db.create_application_event(application["application_id"], "RESUME_TAILORED", {"resume_id": tailored_resume["resume_id"]})
    await db.create_application_event(application["application_id"], "CLAIMS_VALIDATED", {"needs_review": needs_review})
    return await get_application_review(application["application_id"])


def _changes_from_resume_diff(
    application: dict[str, Any], original: dict[str, Any], tailored: dict[str, Any]
) -> list[dict[str, Any]]:
    """Create review-friendly change records from the saved structured resumes."""
    changes: list[dict[str, Any]] = []
    if original.get("processed_data") != tailored.get("processed_data"):
        changes.append(
            {
                "section": "RESUME",
                "type": "modified",
                "before": "Original resume content",
                "after": "Evidence-grounded tailored resume",
                "reason": "Aligned existing evidence to the job description",
                "evidence_source": original.get("resume_id"),
            }
        )
    return changes


async def get_application_review(application_id: str) -> dict[str, Any]:
    """Build the review payload from the tracker row and its saved metadata."""
    application = await db.get_application(application_id)
    if application is None:
        raise LookupError("Application not found")
    events = await db.list_application_events(application_id)
    return {
        "application_id": application_id,
        "job_id": application["job_id"],
        "source_resume_id": application.get("source_resume_id") or application["master_resume_id"] or application["resume_id"],
        "original_resume_id": application.get("original_resume_id") or application.get("source_resume_id") or application["resume_id"],
        "tailored_resume_id": application.get("tailored_resume_id") or application["resume_id"],
        "status": application.get("draft_status") or application["status"],
        "tracker_status": application.get("tracker_status") or application["status"],
        "company": application.get("company"),
        "role": application.get("role"),
        "match": application.get("match") or {},
        "changes": application.get("changes") or [],
        "claim_validation": application.get("claim_validation") or {},
        "screening_questions": application.get("screening_questions") or [],
        "cover_letter": application.get("cover_letter"),
        "needs_review": bool(application.get("needs_review", False)),
        "demo_mode": bool(application.get("demo_mode", False)),
        "events": events,
    }


async def update_screening_answers(application_id: str, answers: dict[str, Any]) -> dict[str, Any]:
    """Store user answers and recalculate missing required questions."""
    application = await db.get_application(application_id)
    if application is None:
        raise LookupError("Application not found")
    questions = list(application.get("screening_questions") or [])
    for question in questions:
        question_id = question.get("question_id")
        if question_id in answers:
            question["answer"] = answers[question_id]
            question["status"] = "USER_CONFIRMED"
    await db.update_application_metadata(
        application_id,
        {
            "screening_questions": questions,
            "missing_screening_answers": validate_screening_answers(questions),
        },
    )
    return await get_application_review(application_id)


async def update_cover_letter(application_id: str, content: str) -> dict[str, Any]:
    """Save a user-edited cover letter on the draft metadata."""
    if await db.get_application(application_id) is None:
        raise LookupError("Application not found")
    await db.update_application_metadata(application_id, {"cover_letter": content})
    return await get_application_review(application_id)


async def regenerate_cover_letter(application_id: str) -> dict[str, Any]:
    """Regenerate through Resume Matcher using the saved tailored evidence."""
    application = await db.get_application(application_id)
    if application is None:
        raise LookupError("Application not found")
    job = await db.get_job(application["job_id"])
    tailored = await db.get_resume(
        application.get("tailored_resume_id") or application["resume_id"]
    )
    if job is None or tailored is None:
        raise LookupError("Application context is no longer available")
    generated = await generate_cover_letter(
        tailored.get("processed_data") or {},
        job.get("content", ""),
        get_content_language(),
    )
    return await update_cover_letter(application_id, generated)

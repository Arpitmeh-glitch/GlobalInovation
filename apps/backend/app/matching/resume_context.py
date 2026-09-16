"""Resolve the stored resume used for CareerPilot matching."""

from __future__ import annotations

from typing import Any

import app.database as database_module


NO_RESUME_MESSAGE = "No resume available for job matching. Upload or select a resume first."
MULTIPLE_RESUMES_MESSAGE = "Multiple resumes are available. Select a resume before matching this job."


def _has_meaningful_value(value: Any) -> bool:
    if isinstance(value, dict):
        return any(_has_meaningful_value(item) for item in value.values())
    if isinstance(value, list):
        return any(_has_meaningful_value(item) for item in value)
    if isinstance(value, str):
        return bool(value.strip())
    return value is not None


def is_usable_resume(resume: dict[str, Any]) -> bool:
    """Return whether a stored resume has parsed data usable for matching."""
    return (
        resume.get("processing_status") == "ready"
        and isinstance(resume.get("processed_data"), dict)
        and _has_meaningful_value(resume["processed_data"])
    )


async def get_matching_resume(resume_id: str | None = None) -> dict[str, Any]:
    """Resolve an explicit resume, the master resume, or one usable resume.

    The existing master-resume flag is preferred. When no master exists, a
    single usable resume is selected; multiple usable resumes require an
    explicit identifier so matching never silently chooses the wrong profile.
    """
    if resume_id is not None:
        resume = await database_module.db.get_resume(resume_id)
        if resume is None or not is_usable_resume(resume):
            raise ValueError(NO_RESUME_MESSAGE)
        return resume

    master = await database_module.db.get_master_resume()
    if master is not None and is_usable_resume(master):
        return master

    usable_resumes = [
        resume
        for resume in await database_module.db.list_resumes()
        if is_usable_resume(resume)
    ]
    if not usable_resumes:
        raise ValueError(NO_RESUME_MESSAGE)
    if len(usable_resumes) > 1:
        raise ValueError(MULTIPLE_RESUMES_MESSAGE)
    return usable_resumes[0]

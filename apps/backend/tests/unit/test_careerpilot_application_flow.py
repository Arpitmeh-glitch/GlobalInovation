from types import SimpleNamespace

import pytest

from app.applications.service import prepare_application, regenerate_cover_letter
from app.routers.careerpilot import approve_application
from app.schemas.careerpilot_applications import PrepareApplicationRequest


@pytest.mark.asyncio
async def test_prepare_and_approve_application_reuses_tracker(
    isolated_backend_state, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = await isolated_backend_state.create_resume(
        content="resume",
        is_master=True,
        processing_status="ready",
        processed_data={"additional": {"technicalSkills": ["Python"]}, "workExperience": []},
    )
    job = await isolated_backend_state.upsert_careerpilot_job(
        {
            "id": "phase2-job",
            "provider": "demo",
            "company": "Demo Co",
            "title": "Python Intern",
            "description": "Build Python tools",
            "skills_required": ["Python"],
            "screening_questions": [],
        }
    )

    async def fake_preview(request):
        return SimpleNamespace(
            data=SimpleNamespace(
                preview_id="preview-1",
                resume_preview={"additional": {"technicalSkills": ["Python"]}, "workExperience": []},
                improvements=[],
            )
        )

    async def fake_confirm(request):
        tailored = await isolated_backend_state.create_resume(
            content="tailored",
            parent_id=source["resume_id"],
            processing_status="ready",
            processed_data={"additional": {"technicalSkills": ["Python"]}, "workExperience": []},
        )
        return SimpleNamespace(data=SimpleNamespace(resume_id=tailored["resume_id"]))

    monkeypatch.setattr("app.routers.resumes.improve_resume_preview_endpoint", fake_preview)
    monkeypatch.setattr("app.routers.resumes.improve_resume_confirm_endpoint", fake_confirm)

    result = await prepare_application(
        job["job_id"], PrepareApplicationRequest(resume_id=source["resume_id"])
    )
    assert result["status"] == "AWAITING_APPROVAL"
    assert result["tracker_status"] == "saved"
    assert result["needs_review"] is False
    assert result["events"]

    approval = await approve_application(result["application_id"])
    assert approval.status == "APPROVED"
    assert approval.tracker_status == "applied"
    assert "ready for submission" in approval.message


@pytest.mark.asyncio
async def test_cover_letter_regeneration_uses_saved_tailored_context(
    isolated_backend_state, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = await isolated_backend_state.create_resume(
        content="original",
        processing_status="ready",
        processed_data={"additional": {"technicalSkills": ["Python"]}},
    )
    tailored = await isolated_backend_state.create_resume(
        content="tailored",
        parent_id=source["resume_id"],
        processing_status="ready",
        processed_data={"additional": {"technicalSkills": ["Python"]}},
        cover_letter="old edited letter",
    )
    job = await isolated_backend_state.create_job("Python job")
    application = await isolated_backend_state.create_application(
        job["job_id"], tailored["resume_id"], master_resume_id=source["resume_id"], status="saved"
    )
    await isolated_backend_state.update_application_metadata(
        application["application_id"],
        {"tailored_resume_id": tailored["resume_id"], "cover_letter": "old edited letter"},
    )

    async def fake_generate(resume_data, job_description, language):
        assert resume_data["additional"]["technicalSkills"] == ["Python"]
        assert job_description == "Python job"
        assert language
        return "new verified letter"

    monkeypatch.setattr("app.applications.service.generate_cover_letter", fake_generate)
    result = await regenerate_cover_letter(application["application_id"])
    assert result["cover_letter"] == "new verified letter"

import pytest

from app.applications.claim_validator import validate_tailored_claims
from app.applications.screening import prepare_screening_questions, validate_screening_answers


def test_unsupported_skill_is_flagged() -> None:
    original = {"additional": {"technicalSkills": ["Python", "Linux"]}}
    tailored = {"additional": {"technicalSkills": ["Python", "Linux", "Splunk"]}}
    result = validate_tailored_claims(original, tailored)
    assert result["needs_review"] is True
    assert any(claim["claim"] == "splunk" for claim in result["unsupported_claims"])


def test_reworded_existing_project_is_allowed() -> None:
    original = {
        "additional": {"technicalSkills": ["Python", "Wireshark"]},
        "personalProjects": [{"name": "Packet Lab", "years": "2025", "description": ["Built packet analysis tool using Wireshark"]}],
    }
    tailored = {
        "additional": {"technicalSkills": ["Python", "Wireshark"]},
        "personalProjects": [{"name": "Packet Lab", "years": "2025", "description": ["Developed a network packet analysis tool with Wireshark"]}],
    }
    assert validate_tailored_claims(original, tailored)["needs_review"] is False


def test_new_certification_is_flagged() -> None:
    result = validate_tailored_claims(
        {"additional": {"certificationsTraining": []}},
        {"additional": {"certificationsTraining": ["Security+"]}},
    )
    assert result["needs_review"] is True
    assert result["unsupported_claims"][0]["claim_type"] == "certification"


def test_screening_protects_sensitive_questions_and_autofills_supported_skill() -> None:
    questions = [
        {"question_id": "splunk", "type": "YES_NO", "question": "Do you have Splunk experience?"},
        {"question_id": "auth", "type": "YES_NO", "question": "Are you legally authorized to work?"},
    ]
    result = prepare_screening_questions(
        questions,
        {"additional": {"technicalSkills": ["Python"]}},
    )
    assert result[0]["status"] == "USER_INPUT_REQUIRED"
    assert result[0]["suggested_answer"] is None
    assert result[1]["requires_confirmation"] is True
    assert validate_screening_answers(result) == ["splunk", "auth"]


def test_screening_answers_clear_required_questions() -> None:
    questions = prepare_screening_questions(
        [{"question_id": "q1", "type": "TEXT", "question": "What is your earliest joining date?"}],
        {},
    )
    questions[0]["answer"] = "2026-10-01"
    assert validate_screening_answers(questions) == []


@pytest.mark.asyncio
async def test_application_event_creation_and_duplicate_tracker_card(isolated_backend_state) -> None:
    resume = await isolated_backend_state.create_resume(content="resume", processing_status="ready", processed_data={"summary": "Python"})
    job = await isolated_backend_state.create_job("Python job")
    first = await isolated_backend_state.create_application(job["job_id"], resume["resume_id"], status="saved")
    second = await isolated_backend_state.create_application(job["job_id"], resume["resume_id"], status="saved")
    assert first["application_id"] == second["application_id"]
    event = await isolated_backend_state.create_application_event(first["application_id"], "APPLICATION_PREPARED", {"source": "test"})
    events = await isolated_backend_state.list_application_events(first["application_id"])
    assert event["event"] == "APPLICATION_PREPARED"
    assert events[0]["metadata"]["source"] == "test"

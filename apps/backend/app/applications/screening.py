"""Screening-question normalization and evidence-aware suggestions."""

from __future__ import annotations

from typing import Any


PROTECTED_QUESTION_TERMS = (
    "authorized",
    "work authorization",
    "salary",
    "notice period",
    "relocat",
    "demographic",
    "legal",
)


def _normal(value: Any) -> str:
    return str(value or "").strip().casefold()


def prepare_screening_questions(
    questions: list[dict[str, Any]], resume: dict[str, Any]
) -> list[dict[str, Any]]:
    """Return questions with safe suggestions and explicit user-input states."""
    skills = set()
    additional = resume.get("additional", {}) if isinstance(resume.get("additional"), dict) else {}
    for value in [*(resume.get("skills", []) or []), *(additional.get("technicalSkills", []) or [])]:
        skills.add(_normal(value))
    experience_text = " ".join(str(item) for item in resume.get("experience", []) or resume.get("workExperience", []) or []).casefold()
    result: list[dict[str, Any]] = []
    for index, raw in enumerate(questions):
        question = dict(raw)
        text = _normal(question.get("question"))
        protected = any(term in text for term in PROTECTED_QUESTION_TERMS)
        suggestion: str | int | None = None
        status = "USER_INPUT_REQUIRED"
        evidence: str | None = None
        if not protected:
            for skill in skills:
                if skill and skill in text:
                    suggestion = "Yes"
                    status = "AUTO_FILLED_FROM_VERIFIED_DATA"
                    evidence = f"Resume skill: {skill}"
                    break
            if suggestion is None and "how many years" in text:
                import re

                match = re.search(r"(\d+)\s*(?:years?|yrs?)", experience_text)
                if match:
                    suggestion = int(match.group(1))
                    status = "AUTO_FILLED_FROM_VERIFIED_DATA"
                    evidence = "Explicit years in resume experience"
        question.update(
            {
                "question_id": str(question.get("question_id") or f"question-{index + 1}"),
                "type": question.get("type") or "TEXT",
                "suggested_answer": suggestion,
                "answer": None,
                "status": status,
                "evidence": evidence,
                "requires_confirmation": True if protected else status == "USER_INPUT_REQUIRED",
            }
        )
        result.append(question)
    return result


def validate_screening_answers(questions: list[dict[str, Any]]) -> list[str]:
    """Return required question IDs that still need explicit answers."""
    return [
        str(question.get("question_id"))
        for question in questions
        if question.get("status") == "USER_INPUT_REQUIRED" and not str(question.get("answer") or "").strip()
    ]

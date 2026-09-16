"""Deterministic validation for claims introduced during resume tailoring."""

from __future__ import annotations

import re
from typing import Any


_FIELDS = (
    "skills",
    "technicalSkills",
    "certifications",
    "certificationsTraining",
)


def _normal(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().casefold()


def _list_values(data: dict[str, Any], key: str) -> set[str]:
    value = data.get(key, [])
    if isinstance(value, dict):
        value = value.values()
    if not isinstance(value, list):
        return set()
    return {_normal(item) for item in value if str(item).strip()}


def _section_entries(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = data.get(key, [])
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _source_context(source: dict[str, Any]) -> dict[str, set[str]]:
    additional = source.get("additional", {}) if isinstance(source.get("additional"), dict) else {}
    skills = _list_values(source, "skills") | _list_values(additional, "technicalSkills")
    certifications = _list_values(source, "certifications") | _list_values(additional, "certificationsTraining")
    employers = {_normal(item.get("company")) for item in _section_entries(source, "workExperience")}
    titles = {_normal(item.get("title")) for item in _section_entries(source, "workExperience")}
    education = {_normal(item.get("degree")) for item in _section_entries(source, "education")}
    projects = {_normal(item.get("name")) for item in _section_entries(source, "personalProjects")}
    dates: set[str] = set()
    for section in ("workExperience", "education", "personalProjects"):
        dates.update(_normal(item.get("years")) for item in _section_entries(source, section))
    return {
        "skills": skills,
        "certifications": certifications,
        "employers": employers,
        "titles": titles,
        "education": education,
        "projects": projects,
        "dates": dates,
    }


def validate_tailored_claims(
    original: dict[str, Any], tailored: dict[str, Any], job: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Find new structured factual claims; wording changes remain allowed.

    This intentionally validates structured facts rather than every prose token.
    It catches unsupported tools/certifications/employers/titles/projects/dates,
    while allowing semantically equivalent bullet rewrites.
    """
    source = _source_context(original)
    unsupported: list[dict[str, str]] = []
    additional = tailored.get("additional", {}) if isinstance(tailored.get("additional"), dict) else {}
    tailored_skills = _list_values(tailored, "skills") | _list_values(additional, "technicalSkills")
    for skill in sorted(tailored_skills - source["skills"]):
        unsupported.append({"claim_type": "skill", "claim": skill, "reason": "Not present in the original resume"})

    tailored_certs = _list_values(tailored, "certifications") | _list_values(additional, "certificationsTraining")
    for certification in sorted(tailored_certs - source["certifications"]):
        unsupported.append({"claim_type": "certification", "claim": certification, "reason": "Not present in the original resume"})

    for section, claim_type in (("workExperience", "employment"), ("education", "education"), ("personalProjects", "project")):
        allowed = source["employers" if section == "workExperience" else "education" if section == "education" else "projects"]
        for item in _section_entries(tailored, section):
            name_key = "company" if section == "workExperience" else "degree" if section == "education" else "name"
            value = _normal(item.get(name_key))
            if value and value not in allowed:
                unsupported.append({"claim_type": claim_type, "claim": value, "reason": "Not present in the original resume"})
            if section == "workExperience":
                title = _normal(item.get("title"))
                if title and title not in source["titles"]:
                    unsupported.append({"claim_type": "job_title", "claim": title, "reason": "Not present in the original resume"})
            years = _normal(item.get("years"))
            if years and years not in source["dates"]:
                unsupported.append({"claim_type": "date", "claim": years, "reason": "Not present in the original resume"})

    return {
        "needs_review": bool(unsupported),
        "unsupported_claims": unsupported,
        "verified_claim_count": max(0, len(source["skills"] | source["certifications"] | source["projects"])),
    }

"""Deterministic matching engine for CareerPilot."""

from __future__ import annotations

import re
from typing import Any


class JobMatchingEngine:
    """Explainable score engine grounded in resume evidence and job requirements."""

    def _normalize(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return re.sub(r"\s+", " ", value).strip().lower()
        return self._normalize(str(value))

    def _resume_tokens(self, resume: dict[str, Any] | None) -> dict[str, list[str]]:
        if not resume:
            return {"skills": [], "experience": [], "projects": [], "education": [], "certifications": []}

        additional = resume.get("additional", {}) or {}
        skills = [str(item) for item in resume.get("skills", []) or []]
        skills.extend(str(item) for item in additional.get("technicalSkills", []) or [])
        experience_items = resume.get("experience", []) or resume.get("workExperience", []) or []
        experience = [str(item.get("title", "")) for item in experience_items]
        experience.extend(str(item.get("years", "")) for item in experience_items)
        experience.extend(str(item.get("description", "")) for item in experience_items)
        experience.extend([str(item) for item in resume.get("experience_text", []) or []])
        projects_items = resume.get("projects", []) or resume.get("personalProjects", []) or []
        projects = [str(item.get("name", "")) for item in projects_items]
        for project in projects_items:
            projects.extend([str(entry) for entry in project.get("description", []) or []])
        education = [str(item.get("degree", "")) for item in resume.get("education", []) or []]
        certifications = [str(item) for item in resume.get("certifications", []) or []]
        certifications.extend(str(item) for item in additional.get("certificationsTraining", []) or [])
        summary = resume.get("summary", "")
        if summary:
            experience.append(str(summary))
        return {
            "skills": skills,
            "experience": experience,
            "projects": projects,
            "education": education,
            "certifications": certifications,
        }

    def _experience_years(self, resume_tokens: dict[str, list[str]]) -> int | None:
        """Extract explicit years from resume text without guessing from titles."""
        years: list[int] = []
        for value in resume_tokens["experience"]:
            for match in re.finditer(r"(\d+)\s*\+?\s*(?:years?|yrs?)", value.lower()):
                years.append(int(match.group(1)))
            for start, end in re.findall(r"\b(19\d{2}|20\d{2})\s*[-–]\s*(19\d{2}|20\d{2})\b", value):
                years.append(max(0, int(end) - int(start)))
        return max(years) if years else None

    def _required_years(self, value: str) -> int | None:
        match = re.search(r"(\d+)\s*\+?\s*(?:years?|yrs?)", value.lower())
        return int(match.group(1)) if match else None

    def _experience_bounds(self, value: Any) -> tuple[int | None, int | None]:
        numbers = [int(item) for item in re.findall(r"\d+", str(value or ""))]
        if not numbers:
            return None, None
        return numbers[0], numbers[1] if len(numbers) > 1 else numbers[0]

    def _is_education_requirement(self, value: str) -> bool:
        return bool(re.search(r"degree|bachelor|master|ph\.d|education|diploma", value.lower()))

    def _education_value_matches(self, education: str, requirement: str) -> bool:
        education_norm = self._normalize(education)
        requirement_norm = self._normalize(requirement)
        if self._text_matches(education_norm, requirement_norm) or self._text_matches(requirement_norm, education_norm):
            return True
        education_levels = {
            "bachelor": ("bachelor", "b.s", "bs", "bsc"),
            "master": ("master", "m.s", "ms", "msc"),
            "doctorate": ("doctor", "ph.d", "phd"),
        }
        return any(
            level in requirement_norm and any(alias in education_norm for alias in aliases)
            for level, aliases in education_levels.items()
        )

    def _is_certification_requirement(self, value: str) -> bool:
        return bool(re.search(r"certif(?:icate|ication|ied)", value.lower()))

    def _text_matches(self, text: str, keyword: str) -> bool:
        return self._normalize(keyword) in self._normalize(text)

    def _match_skill(self, skill: str, resume_tokens: dict[str, list[str]]) -> tuple[bool, str | None, str]:
        skill_norm = self._normalize(skill)
        for bucket_name in ("skills", "experience", "projects", "education", "certifications"):
            for value in resume_tokens.get(bucket_name, []):
                if self._normalize(value) and skill_norm in self._normalize(value):
                    return True, value, bucket_name
        return False, None, "missing"

    def _build_evidence(self, requirement: str, resume_tokens: dict[str, list[str]], is_hard: bool = False) -> dict[str, Any]:
        supported, evidence_text, source = self._match_skill(requirement, resume_tokens)
        status = "supported" if supported else "missing"
        if not supported and not is_hard:
            status = "missing"
        return {
            "requirement": requirement,
            "status": status,
            "evidence": evidence_text if supported else None,
            "source": source if supported else "resume",
        }

    def match_resume_to_job(self, resume: dict[str, Any] | None, job: dict[str, Any]) -> dict[str, Any]:
        resume_tokens = self._resume_tokens(resume)
        required_skills = [str(item) for item in job.get("skills_required", []) or []]
        preferred_skills = [str(item) for item in job.get("skills_preferred", []) or []]
        qualifications = [str(item) for item in job.get("qualifications", []) or []]
        hard_requirements = [str(item) for item in job.get("hard_requirements", []) or []]

        matched_requirements: list[str] = []
        partially_matched_requirements: list[str] = []
        missing_requirements: list[str] = []
        evidence: list[dict[str, Any]] = []
        hard_requirement_failures: list[str] = []

        for skill in required_skills:
            supported, evidence_text, source = self._match_skill(skill, resume_tokens)
            if supported:
                matched_requirements.append(skill)
                evidence.append({"requirement": skill, "status": "supported", "evidence": evidence_text, "source": source})
            else:
                missing_requirements.append(skill)
                evidence.append({"requirement": skill, "status": "missing", "evidence": None, "source": "resume"})

        for skill in preferred_skills:
            supported, evidence_text, source = self._match_skill(skill, resume_tokens)
            if supported:
                partially_matched_requirements.append(skill)
                evidence.append({"requirement": skill, "status": "supported", "evidence": evidence_text, "source": source})
            else:
                missing_requirements.append(skill)
                evidence.append({"requirement": skill, "status": "missing", "evidence": None, "source": "resume"})

        for qualification in qualifications:
            if any(self._text_matches(value, qualification) for value in resume_tokens["education"] + resume_tokens["experience"] + resume_tokens["projects"] + resume_tokens["certifications"]):
                matched_requirements.append(qualification)
            else:
                missing_requirements.append(qualification)

        experience_years = self._experience_years(resume_tokens)
        required_experience = job.get("experience_required")
        required_experience_min, _ = self._experience_bounds(required_experience)
        experience_match: bool | None = None
        if required_experience_min is not None:
            experience_match = experience_years is not None and experience_years >= required_experience_min
        elif experience_years is not None:
            experience_match = True

        education_match: bool | None = None
        education_requirements = [
            qualification for qualification in qualifications
            if self._is_education_requirement(qualification)
        ]
        if education_requirements:
            education_match = any(
                self._education_value_matches(value, qualification)
                for qualification in education_requirements
                for value in resume_tokens["education"]
            )
        for requirement in hard_requirements:
            required_years = self._required_years(requirement)
            if required_years is not None:
                if experience_years is None or experience_years < required_years:
                    hard_requirement_failures.append(requirement)
                continue

            if self._is_certification_requirement(requirement):
                if not resume_tokens["certifications"]:
                    hard_requirement_failures.append(requirement)
                continue

            mentioned_required_skills = [
                skill for skill in required_skills if self._normalize(skill) in self._normalize(requirement)
            ]
            if mentioned_required_skills and any(
                not self._match_skill(skill, resume_tokens)[0]
                for skill in mentioned_required_skills
            ):
                hard_requirement_failures.append(requirement)

        for skill in required_skills:
            if not self._match_skill(skill, resume_tokens)[0]:
                hard_requirement_failures.append(f"Required skill: {skill}")

        skill_points = 0
        if required_skills:
            skill_points = min(100, round((len(matched_requirements) / max(len(required_skills), 1)) * 100))
        experience_score = 60 if experience_years is not None else 25
        if experience_match is False:
            experience_score = 20
        qualification_score = 70 if qualifications and not missing_requirements else 60
        role_score = 80 if resume_tokens["skills"] else 50
        location_score = 100
        work_mode_score = 100

        score_breakdown = {
            "skill_match": skill_points,
            "experience_match": experience_score,
            "qualification_match": qualification_score,
            "role_preference_match": role_score,
            "location_preference_match": location_score,
            "work_mode_match": work_mode_score,
        }
        weighted = (
            score_breakdown["skill_match"] * 0.45
            + score_breakdown["experience_match"] * 0.2
            + score_breakdown["qualification_match"] * 0.15
            + score_breakdown["role_preference_match"] * 0.12
            + score_breakdown["location_preference_match"] * 0.05
            + score_breakdown["work_mode_match"] * 0.03
        )
        overall_score = int(round(weighted))

        hard_failed = bool(hard_requirement_failures)
        if hard_failed:
            recommendation = "Not recommended until the hard requirement gap is addressed"
        elif overall_score >= 80:
            recommendation = "Strong candidate for review"
        elif overall_score >= 60:
            recommendation = "Good fit with targeted follow-up"
        else:
            recommendation = "Lower confidence match"

        return {
            "overall_score": max(0, min(100, overall_score)),
            "recommendation": recommendation,
            "matched_skills": sorted(set(
                skill for skill in required_skills + preferred_skills
                if self._match_skill(skill, resume_tokens)[0]
            )),
            "missing_skills": sorted(set(
                skill for skill in required_skills + preferred_skills
                if not self._match_skill(skill, resume_tokens)[0]
            )),
            "experience_match": experience_match,
            "education_match": education_match,
            "matched_requirements": sorted(set(matched_requirements)),
            "partially_matched_requirements": sorted(set(partially_matched_requirements)),
            "missing_requirements": sorted(set(missing_requirements)),
            "hard_requirement_failures": hard_requirement_failures,
            "evidence": evidence,
            "score_breakdown": score_breakdown,
        }

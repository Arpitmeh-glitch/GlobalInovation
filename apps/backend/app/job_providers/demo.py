"""Deterministic demo job provider for CareerPilot."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.job_providers.base import JobProvider


DEMO_DISCOVERED_AT = "2026-09-16T00:00:00+00:00"
DEMO_SCREENING_QUESTIONS = [
    {
        "question_id": "work-authorization",
        "type": "YES_NO",
        "question": "Are you legally authorized to work in this location?",
    },
    {
        "question_id": "python-years",
        "type": "NUMBER",
        "question": "How many years of Python experience do you have?",
    },
    {
        "question_id": "splunk-experience",
        "type": "YES_NO",
        "question": "Do you have Splunk experience?",
    },
    {
        "question_id": "earliest-start",
        "type": "TEXT",
        "question": "What is your earliest joining date?",
    },
]


def _iso_now() -> str:
    """Return the fixed timestamp used by the canonical demo dataset."""
    return DEMO_DISCOVERED_AT


class DemoProvider(JobProvider):
    """Seeded provider for the hackathon demo.

    The route intentionally never creates random jobs; the dataset is fixed and
    deterministic so the UI and tests can trust rank order and explanation output.
    """

    provider_name = "demo"

    _jobs: list[dict[str, Any]] = [
        {
            "id": "demo-soc-analyst-intern-01",
            "external_id": "SOC-001",
            "provider": "demo",
            "company": "Northstar Security Labs",
            "title": "SOC Analyst Intern",
            "description": (
                "Join a security operations team supporting monitoring, triage, and incident response. "
                "Must be comfortable with Linux, Python, and network telemetry. Preferred familiarity with Wireshark, SIEM tools, and Splunk."
            ),
            "location": "Dehradun / Hybrid",
            "work_mode": "hybrid",
            "employment_type": "internship",
            "salary_min": 30000,
            "salary_max": 45000,
            "currency": "INR",
            "experience_required": "0-1 years",
            "skills_required": ["Python", "Linux", "Networking", "Wireshark"],
            "skills_preferred": ["SIEM", "Splunk", "Incident Response"],
            "qualifications": ["Basic security fundamentals", "Ability to analyze logs and network traffic"],
            "hard_requirements": ["Must have hands-on Linux and Python experience"],
            "application_url": "https://example.com/demo/jobs/soc-analyst-intern",
            "posted_at": "2026-09-14T00:00:00Z",
            "discovered_at": _iso_now(),
            "provider_metadata": {"demo_mode": True, "source": "sample-job-feed"},
        },
        {
            "id": "demo-junior-soc-analyst-02",
            "external_id": "SOC-002",
            "provider": "demo",
            "company": "Signal Forge",
            "title": "Junior SOC Analyst",
            "description": (
                "Monitor alerts, investigate suspicious activity, and document findings. Need excellent understanding of Linux, incident response workflows, and security tooling."
            ),
            "location": "Remote",
            "work_mode": "remote",
            "employment_type": "full_time",
            "salary_min": 450000,
            "salary_max": 700000,
            "currency": "INR",
            "experience_required": "1-2 years",
            "skills_required": ["Linux", "Incident Response", "SIEM", "Python"],
            "skills_preferred": ["Splunk", "AWS", "Wireshark"],
            "qualifications": ["Bachelor's degree in CS or related field"],
            "hard_requirements": ["Must have professional or project-based incident response experience"],
            "application_url": "https://example.com/demo/jobs/junior-soc-analyst",
            "posted_at": "2026-09-12T00:00:00Z",
            "discovered_at": _iso_now(),
            "provider_metadata": {"demo_mode": True, "source": "sample-job-feed"},
        },
        {
            "id": "demo-security-analyst-03",
            "external_id": "SEC-003",
            "provider": "demo",
            "company": "Guardian Cloud",
            "title": "Security Analyst",
            "description": (
                "Work on cloud and application security monitoring for an enterprise environment. Candidates should have experience with AWS, Python, and log analysis."
            ),
            "location": "Bengaluru",
            "work_mode": "onsite",
            "employment_type": "full_time",
            "salary_min": 900000,
            "salary_max": 1500000,
            "currency": "INR",
            "experience_required": "2-4 years",
            "skills_required": ["AWS", "Python", "Cloud Security", "Security Monitoring"],
            "skills_preferred": ["Docker", "Terraform", "Linux"],
            "qualifications": ["Security engineering fundamentals", "Cloud experience preferred"],
            "hard_requirements": ["Professional or strong project experience with AWS security"],
            "application_url": "https://example.com/demo/jobs/security-analyst",
            "posted_at": "2026-09-08T00:00:00Z",
            "discovered_at": _iso_now(),
            "provider_metadata": {"demo_mode": True, "source": "sample-job-feed"},
        },
        {
            "id": "demo-cloud-security-intern-04",
            "external_id": "CLOUD-004",
            "provider": "demo",
            "company": "Nimbus Defense",
            "title": "Cloud Security Intern",
            "description": (
                "Assist with IAM reviews, threat modeling, cloud logging, and simple automation. Strong Python and AWS basics are required."
            ),
            "location": "Remote",
            "work_mode": "remote",
            "employment_type": "internship",
            "salary_min": 25000,
            "salary_max": 40000,
            "currency": "INR",
            "experience_required": "0-1 years",
            "skills_required": ["AWS", "Python", "Docker", "Cloud Security"],
            "skills_preferred": ["Terraform", "IAM", "Linux"],
            "qualifications": ["Cloud fundamentals"],
            "hard_requirements": ["Must be able to discuss AWS services and automation basics"],
            "application_url": "https://example.com/demo/jobs/cloud-security-intern",
            "posted_at": "2026-09-07T00:00:00Z",
            "discovered_at": _iso_now(),
            "provider_metadata": {"demo_mode": True, "source": "sample-job-feed"},
        },
        {
            "id": "demo-network-security-intern-05",
            "external_id": "NET-005",
            "provider": "demo",
            "company": "CyberReconX",
            "title": "Network Security Intern",
            "description": (
                "Explore network reconnaissance, packet capture, and service discovery. Must be comfortable with Linux, Wireshark, and network analysis tools."
            ),
            "location": "Pune",
            "work_mode": "hybrid",
            "employment_type": "internship",
            "salary_min": 28000,
            "salary_max": 42000,
            "currency": "INR",
            "experience_required": "0-2 years",
            "skills_required": ["Linux", "Networking", "Wireshark", "Python"],
            "skills_preferred": ["Nmap", "TCP/IP", "IDS"],
            "qualifications": ["Networking fundamentals", "Basic scripting"],
            "hard_requirements": ["Must demonstrate network analysis capability"],
            "application_url": "https://example.com/demo/jobs/network-security-intern",
            "posted_at": "2026-09-05T00:00:00Z",
            "discovered_at": _iso_now(),
            "provider_metadata": {"demo_mode": True, "source": "sample-job-feed"},
        },
        {
            "id": "demo-software-engineer-intern-06",
            "external_id": "SW-006",
            "provider": "demo",
            "company": "Code Harbor",
            "title": "Software Engineer Intern",
            "description": (
                "Build backend services and internal tooling in a modern engineering team. Experience with JavaScript, React, Node.js, and Git is important."
            ),
            "location": "Remote",
            "work_mode": "remote",
            "employment_type": "internship",
            "salary_min": 32000,
            "salary_max": 50000,
            "currency": "INR",
            "experience_required": "0-1 years",
            "skills_required": ["JavaScript", "React", "Node.js", "Git"],
            "skills_preferred": ["TypeScript", "REST APIs", "SQL"],
            "qualifications": ["Computer Science fundamentals"],
            "hard_requirements": ["Must be comfortable with full-stack or backend development workflows"],
            "application_url": "https://example.com/demo/jobs/software-engineer-intern",
            "posted_at": "2026-09-04T00:00:00Z",
            "discovered_at": _iso_now(),
            "provider_metadata": {"demo_mode": True, "source": "sample-job-feed"},
        },
        {
            "id": "demo-backend-developer-intern-07",
            "external_id": "BE-007",
            "provider": "demo",
            "company": "Stack Harbor",
            "title": "Backend Developer Intern",
            "description": (
                "Develop APIs and services with Python or JavaScript. Strong problem-solving, REST APIs, and deployment experience are valuable."
            ),
            "location": "Bengaluru / Hybrid",
            "work_mode": "hybrid",
            "employment_type": "internship",
            "salary_min": 35000,
            "salary_max": 55000,
            "currency": "INR",
            "experience_required": "0-2 years",
            "skills_required": ["Python", "REST APIs", "SQL", "Git"],
            "skills_preferred": ["FastAPI", "Docker", "AWS"],
            "qualifications": ["Backend fundamentals", "Data structures"],
            "hard_requirements": ["Must be able to explain API design and data modeling"],
            "application_url": "https://example.com/demo/jobs/backend-developer-intern",
            "posted_at": "2026-09-03T00:00:00Z",
            "discovered_at": _iso_now(),
            "provider_metadata": {"demo_mode": True, "source": "sample-job-feed"},
        },
        {
            "id": "demo-dfir-intern-08",
            "external_id": "DFIR-008",
            "provider": "demo",
            "company": "Blue Lantern",
            "title": "DFIR Intern",
            "description": (
                "Support digital forensics and incident response work. Need comfort with Linux, log analysis, memory forensics and security investigations."
            ),
            "location": "Remote",
            "work_mode": "remote",
            "employment_type": "internship",
            "salary_min": 30000,
            "salary_max": 48000,
            "currency": "INR",
            "experience_required": "0-1 years",
            "skills_required": ["Linux", "Forensics", "Incident Response", "Python"],
            "skills_preferred": ["Volatility", "Autopsy", "Wireshark"],
            "qualifications": ["Digital evidence handling basics"],
            "hard_requirements": ["Must have at least one forensic or investigation project"],
            "application_url": "https://example.com/demo/jobs/dfir-intern",
            "posted_at": "2026-09-02T00:00:00Z",
            "discovered_at": _iso_now(),
            "provider_metadata": {"demo_mode": True, "source": "sample-job-feed"},
        },
        {
            "id": "demo-security-engineer-09",
            "external_id": "ENG-009",
            "provider": "demo",
            "company": "SysGuard Technologies",
            "title": "Junior Security Engineer",
            "description": (
                "Help implement security tooling, ensure secure deployments, and review system logs. Familiarity with IAM, cloud, and automation is valuable."
            ),
            "location": "Remote",
            "work_mode": "remote",
            "employment_type": "full_time",
            "salary_min": 800000,
            "salary_max": 1200000,
            "currency": "INR",
            "experience_required": "1-3 years",
            "skills_required": ["Python", "AWS", "Security Engineering", "Linux"],
            "skills_preferred": ["Terraform", "Docker", "IAM"],
            "qualifications": ["System administration basics"],
            "hard_requirements": ["Must have secure cloud or system engineering proof"],
            "application_url": "https://example.com/demo/jobs/junior-security-engineer",
            "posted_at": "2026-09-01T00:00:00Z",
            "discovered_at": _iso_now(),
            "provider_metadata": {"demo_mode": True, "source": "sample-job-feed"},
        },
        {
            "id": "demo-security-operations-10",
            "external_id": "OPS-010",
            "provider": "demo",
            "company": "Cobalt Response",
            "title": "Security Operations Engineer",
            "description": (
                "Manage security monitoring pipelines, review alerts, and help with response workflows. Splunk, SIEM, and Linux experience are key."
            ),
            "location": "Delhi",
            "work_mode": "onsite",
            "employment_type": "full_time",
            "salary_min": 1000000,
            "salary_max": 1700000,
            "currency": "INR",
            "experience_required": "2-5 years",
            "skills_required": ["Splunk", "SIEM", "Linux", "Incident Response"],
            "skills_preferred": ["Python", "AWS", "Wireshark"],
            "qualifications": ["Security operations experience"],
            "hard_requirements": ["Must have direct SOC or security operations experience"],
            "application_url": "https://example.com/demo/jobs/security-operations-engineer",
            "posted_at": "2026-08-30T00:00:00Z",
            "discovered_at": _iso_now(),
            "provider_metadata": {"demo_mode": True, "source": "sample-job-feed"},
        },
        {
            "id": "demo-web-security-11",
            "external_id": "WEB-011",
            "provider": "demo",
            "company": "AppShield",
            "title": "Web Security Analyst",
            "description": (
                "Investigate application and API security issues, support assessments, and assist with secure development practices."
            ),
            "location": "Remote",
            "work_mode": "remote",
            "employment_type": "contract",
            "salary_min": 700000,
            "salary_max": 1100000,
            "currency": "INR",
            "experience_required": "1-3 years",
            "skills_required": ["Security Testing", "Python", "APIs", "Web Security"],
            "skills_preferred": ["OWASP", "JavaScript", "Linux"],
            "qualifications": ["Application security understanding"],
            "hard_requirements": ["Must have security review or testing experience"],
            "application_url": "https://example.com/demo/jobs/web-security-analyst",
            "posted_at": "2026-08-28T00:00:00Z",
            "discovered_at": _iso_now(),
            "provider_metadata": {"demo_mode": True, "source": "sample-job-feed"},
        },
        {
            "id": "demo-azure-security-12",
            "external_id": "AZ-012",
            "provider": "demo",
            "company": "Azure Heights",
            "title": "Cloud Security Engineer",
            "description": (
                "Optimize Azure-based security controls, support incident response, and improve automation for cloud workloads."
            ),
            "location": "Mumbai",
            "work_mode": "hybrid",
            "employment_type": "full_time",
            "salary_min": 1000000,
            "salary_max": 1600000,
            "currency": "INR",
            "experience_required": "2-4 years",
            "skills_required": ["Azure", "Python", "Cloud Security", "IAM"],
            "skills_preferred": ["Terraform", "Linux", "Security Monitoring"],
            "qualifications": ["Cloud security operations"],
            "hard_requirements": ["Must understand identity, cloud policy and secure automation"],
            "application_url": "https://example.com/demo/jobs/cloud-security-engineer",
            "posted_at": "2026-08-26T00:00:00Z",
            "discovered_at": _iso_now(),
            "provider_metadata": {"demo_mode": True, "source": "sample-job-feed"},
        },
        {
            "id": "demo-incident-response-13",
            "external_id": "IR-013",
            "provider": "demo",
            "company": "Redline Defense",
            "title": "Incident Response Analyst",
            "description": (
                "Investigate alerts and coordinate containment workflows. Deep experience with logs, response and forensics is expected."
            ),
            "location": "Remote",
            "work_mode": "remote",
            "employment_type": "full_time",
            "salary_min": 850000,
            "salary_max": 1300000,
            "currency": "INR",
            "experience_required": "1-3 years",
            "skills_required": ["Incident Response", "Linux", "Security Monitoring", "Python"],
            "skills_preferred": ["Forensics", "SIEM", "Wireshark"],
            "qualifications": ["Security response workflow knowledge"],
            "hard_requirements": ["Must show investigation workflow and incident handling experience"],
            "application_url": "https://example.com/demo/jobs/incident-response-analyst",
            "posted_at": "2026-08-21T00:00:00Z",
            "discovered_at": _iso_now(),
            "provider_metadata": {"demo_mode": True, "source": "sample-job-feed"},
        },
        {
            "id": "demo-mis-14",
            "external_id": "MIS-014",
            "provider": "demo",
            "company": "SecureOps India",
            "title": "Managed Security Intern",
            "description": (
                "Support monitoring operations, triage, and dashboard coverage across customer environments. Good Linux and Python basics are important."
            ),
            "location": "Noida",
            "work_mode": "onsite",
            "employment_type": "internship",
            "salary_min": 26000,
            "salary_max": 42000,
            "currency": "INR",
            "experience_required": "0-1 years",
            "skills_required": ["Python", "Linux", "Security Monitoring"],
            "skills_preferred": ["SIEM", "Networking", "AWS"],
            "qualifications": ["Security fundamentals"],
            "hard_requirements": ["Must be able to explain alert triage basics"],
            "application_url": "https://example.com/demo/jobs/managed-security-intern",
            "posted_at": "2026-08-20T00:00:00Z",
            "discovered_at": _iso_now(),
            "provider_metadata": {"demo_mode": True, "source": "sample-job-feed"},
        },
    ]

    def search_jobs(self, criteria: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        criteria = criteria or {}
        filtered = deepcopy(self._jobs)
        role_word = (criteria.get("role") or "").strip().lower()
        location = (criteria.get("location") or "").strip().lower()
        work_mode = (criteria.get("work_mode") or "").strip().lower()
        employment_type = (criteria.get("employment_type") or "").strip().lower()
        keywords = [str(item).lower() for item in criteria.get("keywords", [])]

        if role_word:
            filtered = [job for job in filtered if role_word in job["title"].lower() or role_word in job["description"].lower()]
        if location:
            filtered = [job for job in filtered if location in job["location"].lower()]
        if work_mode:
            filtered = [job for job in filtered if job["work_mode"].lower() == work_mode]
        if employment_type:
            filtered = [job for job in filtered if job["employment_type"].lower() == employment_type]
        if keywords:
            filtered = [
                job for job in filtered
                if any(keyword in " ".join([
                    job["title"],
                    job["description"],
                    *job.get("skills_required", []),
                    *job.get("skills_preferred", []),
                ]).lower() for keyword in keywords)
            ]

        result = []
        for job in filtered:
            copy_job = deepcopy(job)
            copy_job["screening_questions"] = deepcopy(DEMO_SCREENING_QUESTIONS)
            result.append(copy_job)
        return result

    def get_job_details(self, job_id: str) -> dict[str, Any] | None:
        for job in self._jobs:
            if job["id"] == job_id:
                result = deepcopy(job)
                result["screening_questions"] = deepcopy(DEMO_SCREENING_QUESTIONS)
                return result
        return None

    def supports_application(self) -> bool:
        return True

    def prepare_application(self, *, job: dict[str, Any], resume: dict[str, Any]) -> dict[str, Any]:
        return {
            "provider": self.provider_name,
            "job_id": job.get("id"),
            "resume_id": resume.get("resume_id"),
            "company": job.get("company"),
            "title": job.get("title"),
            "status": "draft",
            "application_url": job.get("application_url"),
            "notes": "Demo mode: application prepared for review without submitting to a real employer.",
        }

    def submit_application(self, *, application: dict[str, Any]) -> dict[str, Any]:
        return {
            "provider": self.provider_name,
            "job_id": application.get("job_id"),
            "status": "submitted-demo",
            "message": "Demo Mode — sample job data only. No real application was submitted.",
        }

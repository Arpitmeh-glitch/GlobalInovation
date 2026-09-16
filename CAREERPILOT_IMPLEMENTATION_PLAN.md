# CareerPilot Implementation Plan

## 1. Current architecture

### Backend

The current backend is a FastAPI service anchored in `apps/backend/app/main.py` and organized around a small set of routers:

- `app/routers/health.py` — health/status endpoints
- `app/routers/config.py` — LLM provider configuration and encrypted API keys
- `app/routers/resumes.py` — upload, parse, improve, preview, confirm, PDF export
- `app/routers/jobs.py` — job description upload and retrieval
- `app/routers/applications.py` — tracker CRUD and Kanban status transitions
- `app/routers/enrichment.py` — extra AI enrichment flows
- `app/routers/resume_wizard.py` — guided resume-building workflow

The persistence layer is a SQLite + SQLAlchemy 2.0 design with a `Database` facade returning plain dicts rather than ORM objects. The schema currently supports:

- `Resume`
- `Job`
- `Improvement`
- `Application`
- `TailoringPreview`
- `ApiKey`

See:

- `apps/backend/app/database.py`
- `apps/backend/app/models.py`
- `apps/backend/app/db_engine.py`

The backend already has reusable AI components:

- `app/services/parser.py` — PDF/DOCX/DOC → Markdown, then resume extraction
- `app/services/improver.py` — keyword extraction, skill targeting, resume diff generation
- `app/services/cover_letter.py` — cover letters and outreach copy
- `app/services/interview_prep.py` — interview prep outputs
- `app/services/ats.py` — ATS-style scoring heuristics
- `app/llm.py` — multi-provider LiteLLM wrapper

Important constraints from the current design:

- A single master resume is enforced via a partial unique index.
- Jobs and resumes are stored with dynamic metadata in JSON fields.
- LLM API keys are encrypted at rest via Fernet and stored in SQLite.
- Tracker cards are modeled as a Kanban board with statuses such as saved/applied/no_response/response/interview/accepted/rejected.
- Resume tailoring is already built around job-content + resume-content + AI improvement flow.

### Frontend

The frontend is a Next.js App Router app in `apps/frontend/app` with distinct sections:

- `/dashboard` — resume state and master selection
- `/builder` — master resume authoring and preview
- `/tailor` — job description analysis + tailored resume workflow
- `/tracker` — Kanban application tracker
- `/settings` — configuration for model/provider keys
- `/resumes/[id]` — resume viewer/edit flow
- `/print/...` — PDF generation routes

Reusable UI and logic are already split into:

- `components/ui` for primitives
- `components/dashboard` for resume management
- `components/tracker` for tracker board
- `components/tailor` for JD + improve + diff previews
- `components/resume` and `components/builder` for resume rendering and editing
- `lib/api/*` for backend interaction

### Existing capabilities that should be preserved

The following are valuable foundations for CareerPilot and should be adapted rather than replaced:

- Resume upload and document parsing
- Resume extraction into structured data (`ResumeData`)
- Job description upload and storage
- AI-driven resume improvement and diff preview
- Cover letter / outreach generation
- Interview preparation output
- Kanban-style application tracking
- LLM provider configuration and encrypted secret handling
- PDF rendering pipeline for print/export

### Technical debt / constraints to respect

- No broad rewriting of working functionality is acceptable.
- Current API patterns and DB conventions are already stable and should be preserved for existing resume flows.
- The project is not yet organized around a provider abstraction for job search.
- There is no evidence graph or claim-validation layer yet.
- Matching is currently close to resume-improvement and ATS-style heuristics, not an explainable eligibility engine.
- The frontend is designed around Swiss-style layout; new pages should follow the same visual language.

---

## 2. Existing features we will preserve

### Resume Matcher features to keep

1. Master resume management and resume processing pipeline
2. Structured resume parsing and editing
3. Job description upload and tailoring workflow
4. Cover letter / outreach generation
5. Interview preparation generation
6. Application tracker Kanban board
7. API-key encryption and settings management
8. PDF/print flows for resume and cover-letter outputs
9. Swiss-style front-end design system

### Features to adapt into CareerPilot

- Resume tailoring becomes the “Application Draft” generation step.
- Job upload becomes a job discovery + normalized job model step.
- Application tracker becomes the CRM flow for discovered / recommended / approved / submitted jobs.
- Cover letter and interview prep remain as downstream artifacts for the application agent.
- The existing LLM abstraction remains the execution engine for matching, tailoring, and screening analysis.

---

## 3. Proposed architecture

CareerPilot should be introduced as a new capability layer on top of the current app, not as a full rewrite.

### Recommended architecture shape

Backend modules:

```text
apps/backend/app/
├── agent/
│   ├── __init__.py
│   ├── activity_log.py
│   ├── application_agent.py
│   └── demo_mode.py
├── career_intelligence/
│   ├── __init__.py
│   ├── career_gap_service.py
│   └── simulator.py
├── evidence/
│   ├── __init__.py
│   ├── evidence_graph.py
│   ├── validators.py
│   └── vault.py
├── job_providers/
│   ├── __init__.py
│   ├── base.py
│   ├── demo_provider.py
│   └── registry.py
├── job_discovery/
│   ├── __init__.py
│   ├── discovery_service.py
│   └── normalization.py
├── matching/
│   ├── __init__.py
│   ├── scorer.py
│   ├── requirements_matcher.py
│   └── explainability.py
├── applications/
│   ├── __init__.py
│   ├── draft_service.py
│   ├── screening_service.py
│   └── submission_service.py
├── audit/
│   ├── __init__.py
│   └── event_store.py
└── routers/
    ├── careerpilot.py
    ├── jobs.py (extended)
    ├── applications.py (extended)
    └── resumes.py (extended)
```

The most important design rule is: keep the current resume/job/tracker flows stable, then add CareerPilot-specific services and routers around them. This minimizes breakage and aligns with the current project architecture.

### Core data model strategy

The current `Database` design uses a dict-based facade and SQLAlchemy models. CareerPilot should follow the same pattern:

- add new ORM tables in `models.py`
- expose new dict-returning methods in `database.py`
- keep the rest of the app consuming dicts, not ORM objects
- add transaction-aware writes where cross-model state changes must be consistent

This is compatible with the existing architecture and prevents a heavy refactor.

---

## 4. Directory and file changes

### Backend additions

Relevant files to add or extend:

- `apps/backend/app/models.py` — add CareerPilot models
- `apps/backend/app/database.py` — add DAO methods for profiles, jobs, matches, evidence, applications, gaps, agent events
- `apps/backend/app/routers/careerpilot.py` — new onboarding, discovery, recommendation, evidence, and simulator endpoints
- `apps/backend/app/job_providers/base.py` — provider interface + normalization contract
- `apps/backend/app/job_providers/demo_provider.py` — deterministic demo provider for hackathon flow
- `apps/backend/app/job_providers/registry.py` — provider registry and factory
- `apps/backend/app/job_discovery/discovery_service.py` — aggregate provider search and filtering
- `apps/backend/app/job_discovery/normalization.py` — common `Job` model normalization
- `apps/backend/app/matching/scorer.py` — explainable scoring engine
- `apps/backend/app/matching/requirements_matcher.py` — requirements analysis
- `apps/backend/app/evidence/evidence_graph.py` — evidence linking and verification
- `apps/backend/app/evidence/vault.py` — evidence source management
- `apps/backend/app/applications/draft_service.py` — application drafting logic
- `apps/backend/app/applications/screening_service.py` — screening question validation
- `apps/backend/app/career_intelligence/career_gap_service.py` — missing-skill trend analysis
- `apps/backend/app/career_intelligence/simulator.py` — what-if skill/project simulation
- `apps/backend/app/agent/application_agent.py` — orchestrator for discovery → analysis → recommendation → draft → approval trail
- `apps/backend/app/audit/event_store.py` — structured agent log activity

### Frontend additions

- `apps/frontend/app/(default)/onboarding/page.tsx` — profile and preferences onboarding
- `apps/frontend/app/(default)/discover/page.tsx` — job discovery and filtering results
- `apps/frontend/app/(default)/recommended/page.tsx` — recommended jobs and match cards
- `apps/frontend/app/(default)/applications/page.tsx` — tracker / CRM dashboard
- `apps/frontend/app/(default)/resumes/page.tsx` or existing resume list enhanced
- `apps/frontend/app/(default)/evidence/page.tsx` — evidence vault UI
- `apps/frontend/app/(default)/gaps/page.tsx` — gap analysis and recommendations
- `apps/frontend/app/(default)/jobs/[job_id]/page.tsx` — job analysis page
- `apps/frontend/app/(default)/demo/page.tsx` — explicit demo mode flow

### Shared client code

- `apps/frontend/lib/api/careerpilot.ts` — onboarding, discovery, match, evidence, simulator APIs
- `apps/frontend/components/careerpilot/` — reusable dashboard cards, match panels, evidence tables, application review panels

---

## 5. Data models

### Core user and preference state

```python
class UserProfile(Base):
    user_id: str
    name: str
    email: str
    location: str | None
    work_authorization: str | None
    created_at: str
    updated_at: str
```

```python
class JobPreference(Base):
    preference_id: str
    user_id: str
    desired_titles: list[str]
    desired_industries: list[str]
    preferred_locations: list[str]
    remote_hybrid_onsite: str
    minimum_salary: int | None
    experience_level: str
    employment_types: list[str]
    companies_to_exclude: list[str]
    industries_to_exclude: list[str]
    min_match_threshold: float
    max_applications_per_day: int
    requires_approval: bool
    notification_preferences: dict[str, Any]
```

### Resume and evidence

```python
class Resume(Base):
    # existing resume model remains; add a user_id and resume_profile_name if needed
    resume_id: str
    user_id: str
    profile_name: str | None  # "Cybersecurity Resume"
    is_master: bool
    parent_id: str | None
```

```python
class Evidence(Base):
    evidence_id: str
    user_id: str
    source_type: str  # resume, project, github, certificate, employment, portfolio, manual
    source_id: str | None
    skill_name: str
    evidence_text: str
    confidence: float
    metadata_json: dict[str, Any]
    created_at: str
```

### Job and matching

```python
class Job(Base):
    job_id: str
    external_id: str
    provider: str
    company: str
    title: str
    description: str
    location: str | None
    work_mode: str | None
    employment_type: str | None
    salary_min: int | None
    salary_max: int | None
    currency: str | None
    experience_required: str | None
    skills_required: list[str]
    skills_preferred: list[str]
    qualifications: list[str]
    application_url: str | None
    posted_at: str | None
    discovered_at: str
    raw_metadata_json: dict[str, Any]
```

```python
class JobMatch(Base):
    match_id: str
    job_id: str
    resume_id: str
    overall_match: float
    eligibility: bool
    confidence: float
    matched_requirements: list[str]
    partially_matched_requirements: list[str]
    missing_requirements: list[str]
    hard_requirement_failures: list[str]
    evidence_refs: list[str]
    explanation: str
    created_at: str
```

### Application workflow

```python
class Application(Base):
    application_id: str
    user_id: str
    job_id: str
    resume_id: str
    status: str  # DISCOVERED, ANALYZED, RECOMMENDED, DRAFT_READY, AWAITING_APPROVAL, APPROVED, SUBMITTED, INTERVIEW, OFFER, REJECTED, WITHDRAWN
    match_score: float | None
    approval_required: bool
    source: str
    application_url: str | None
    created_at: str
    updated_at: str
```

```python
class ApplicationEvent(Base):
    event_id: str
    application_id: str
    event_type: str
    event_detail: str
    created_at: str
```

```python
class ProviderConnection(Base):
    provider_id: str
    user_id: str
    provider_name: str
    auth_method: str
    token_encrypted: str | None
    status: str
    metadata_json: dict[str, Any]
```

### Career intelligence and audit

```python
class CareerGap(Base):
    gap_id: str
    user_id: str
    target_role: str
    missing_skill: str
    frequency: float
    evidence_gap: str
    recommendation: str
    created_at: str
```

```python
class AgentActivity(Base):
    activity_id: str
    user_id: str
    message: str
    category: str
    created_at: str
```

---

## 6. API design

Add a dedicated `CareerPilot` router under `/api/v1` with these endpoints.

### Onboarding and profile

- `POST /api/v1/careerpilot/profile` — create/update user profile and preferences
- `GET /api/v1/careerpilot/profile` — fetch profile
- `POST /api/v1/careerpilot/resumes` — attach a master resume profile
- `GET /api/v1/careerpilot/resumes` — list all profile resumes

### Job discovery

- `POST /api/v1/careerpilot/discover` — run enabled providers and return discovered jobs
- `GET /api/v1/careerpilot/jobs` — list normalized jobs
- `GET /api/v1/careerpilot/jobs/{job_id}` — fetch full job + supporting metadata

### Matching and evidence

- `POST /api/v1/careerpilot/jobs/{job_id}/match` — score a job against selected resume(s)
- `GET /api/v1/careerpilot/evidence` — fetch evidence vault entries
- `POST /api/v1/careerpilot/evidence/link` — manually connect a skill or project to a requirement

### Application preparation

- `POST /api/v1/careerpilot/jobs/{job_id}/draft` — prepare application draft
- `POST /api/v1/careerpilot/applications/{application_id}/approve` — approve without submitting
- `POST /api/v1/careerpilot/applications/{application_id}/submit` — demo or controlled submit
- `GET /api/v1/careerpilot/applications` — list application pipeline

### Career intelligence

- `GET /api/v1/careerpilot/gaps` — missing-skill analysis
- `POST /api/v1/careerpilot/simulate` — what-if simulation without mutating evidence
- `GET /api/v1/careerpilot/activity-log` — structured agent activity feed

### Demo mode

- `GET /api/v1/careerpilot/demo` — deterministic demo snapshot
- `POST /api/v1/careerpilot/demo/reset` — restore a seeded demo dataset

---

## 7. JobProvider interface

This should be isolated behind a provider abstraction and not embedded in the app logic.

```python
class JobProvider(ABC):
    name: str

    @abstractmethod
    async def search_jobs(self, *, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def get_job_details(self, *, job_id: str) -> dict[str, Any] | None:
        ...

    @abstractmethod
    async def supports_application(self) -> bool:
        ...

    @abstractmethod
    async def prepare_application(self, *, job: dict[str, Any], resume: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    async def submit_application(self, *, application: dict[str, Any]) -> dict[str, Any]:
        ...
```

### Provider implementations

Recommended MVP set:

1. `DemoProvider` — deterministic sample jobs for hackathon demo and testing
2. `PermittedSourceProvider` — real provider integration when allowed (for example a public RSS/feed or authorized API if available)

### Provider rules

- No scraping that violates ToS or anti-bot controls
- No LinkedIn/Indeed automation assumptions in the MVP
- Keep provider logic isolated, with common normalization to a standard `Job` model
- All providers are behind the registry/factory to keep the app modular

### Normalized job model

```python
Job = {
    "id": "...",
    "externalId": "...",
    "provider": "demo|official_api|...",
    "company": "Example Corp",
    "title": "SOC Analyst Intern",
    "description": "...",
    "location": "Remote",
    "workMode": "remote",
    "employmentType": "internship",
    "salaryMin": 60000,
    "salaryMax": 80000,
    "currency": "USD",
    "experienceRequired": "0-2 years",
    "skillsRequired": ["Python", "Linux"],
    "skillsPreferred": ["Splunk", "Wireshark"],
    "qualifications": ["Bachelor's degree"],
    "applicationUrl": "https://...",
    "postedAt": "2026-09-01T00:00:00Z",
    "discoveredAt": "2026-09-16T00:00:00Z",
}
```

---

## 8. Matching-engine design

The key innovation is explainability and evidence grounding, not raw keyword overlap.

### Matching categories

- Skill match
- Experience match
- Education match
- Project evidence match
- Location match
- Work mode match
- Salary match
- Role preference match

### Explainable output contract

```python
{
  "overallMatch": 87,
  "eligibility": True,
  "confidence": "medium",
  "matchedRequirements": ["Python", "Linux", "Wireshark"],
  "partiallyMatchedRequirements": ["SIEM"],
  "missingRequirements": ["Splunk"],
  "hardRequirementFailures": [],
  "evidence": [
    {
      "requirement": "Network traffic analysis",
      "status": "supported",
      "source": "Project: CyberReconX",
      "evidenceText": "Built packet-analysis project using Wireshark."
    }
  ],
  "explanation": "Candidate demonstrates evidence for 6/7 core requirements. Splunk is listed as preferred rather than mandatory."
}
```

### Design rules

- Every match result must be tied to evidence or explicitly marked unsupported.
- Hard requirements are not guessed; they are only checked against verified evidence.
- The score is never presented as an objective probability; it is an explainable recommendation.
- The matching engine should operate after job normalization and resume evidence extraction.

---

## 9. Evidence-grounding design

This is the most critical investment for CareerPilot.

### Evidence Vault / Candidate Evidence Graph

The app should maintain a normalized evidence model with explicit provenance.

Example graph:

```text
Candidate
├── Python
│   └── Project A
├── Linux
│   └── Project B
├── Wireshark
    └── Network Analysis Project
```

### Evidence verification policy

Every requirement is treated as either:

- supported
- partial
- missing
- unsupported

### Hard policy

- Never invent qualifications
- Never fabricate employers, durations, education, certifications, or achievements
- Tailoring must only use supported evidence
- The app must explicitly flag unsupported claims instead of silently generating them

### Implementation approach

- Parse resume structured data into evidence nodes
- Attach project and certificate details to skill nodes
- Create an explicit `Evidence` table plus `requirements -> evidence` mapping for each match result
- Add a validation layer that rejects unsupported tailoring claims before save

---

## 10. Application-agent design

### Workflow

1. Discover jobs
2. Filter by user preferences and eligibility heuristics
3. Match jobs to resumes using explainable scoring
4. Verify evidence support for each requirement
5. Recommend only jobs that pass eligibility criteria
6. Build an application draft for the selected resume
7. Generate screening questions and identify required user input
8. Require human approval before automated or manual submission
9. Record all actions in the audit log

### Application draft output

`ApplicationDraft` should contain:

- best resume choice
- tailored wording with only supported evidence
- cover letter when appropriate
- screening questions
- answers with evidence-backed status
- unknown questions requiring explicit user confirmation
- application preview and metadata

### Default submission policy

- Human approval before submission
- Auto-apply only when enabled explicitly
- Auto-apply rules must include:
  - minimum match threshold met
  - no hard requirement failure
  - all required screening questions have verified answers
  - provider supports legal/allowed automation
  - daily limit not reached

### Status ladder

```text
DISCOVERED
ANALYZED
RECOMMENDED
DRAFT_READY
AWAITING_APPROVAL
APPROVED
SUBMITTED
INTERVIEW
OFFER
REJECTED
WITHDRAWN
```

---

## 11. Security considerations

- Never store plaintext passwords or tokens in config files.
- Keep provider credentials in environment variables or encrypted store.
- Continue using encrypted API keys where practical.
- Never expose API keys client-side.
- Validate uploads and sanitize all user-controlled content.
- Protect endpoints with appropriate request validation and rate limiting.
- Do not log authentication credentials or raw secret values.
- Keep demo mode clearly labelled and never present simulated applications as real submissions.

---

## 12. UI and pages

The frontend should evolve from the existing Resume Matcher flow into a CareerPilot dashboard while keeping the current pages intact.

### Main navigation

- Dashboard
- Discover Jobs
- Recommended
- Applications
- Resumes
- Evidence Vault
- Career Gaps
- Settings

### Dashboard experience

Display: 

- “Welcome back”
- 142 Jobs Discovered
- 31 Strong Matches
- 12 Ready for Review
- 18 Applications
- 3 Interviews

Then show:

- Top matches with “View Analysis” CTA buttons
- Career insights: most valuable missing skill, most successful target role, application progression

### Job analysis page

A richer, highly visual job analysis screen should include:

- Company, role, location, salary, work mode
- Match overview: overall, skills, experience, education, preference
- Requirement analysis with supported/partial/missing states
- Evidence sources and explanation
- CTA: “Prepare Application”

### Onboarding UI

Use a multi-step wizard:

- Personal profile
- Job preferences
- Search behavior
- Resume profile upload
- Review/submit

### Demo mode UI

Must have obvious labeling such as “Demo Mode — Sample Data Only”.

---

## 13. Demo strategy

The demo mode should be deterministic and should not claim a real employer submission happened.

### Demo sequence

1. User already onboarded into a demo profile
2. Demo jobs are discovered from a seeded provider
3. Jobs are analyzed and scored
4. Strong matches are surfaced with evidence-backed explanation
5. Application draft is generated for a target role
6. User approves the draft
7. A simulated, controlled submission succeeds
8. The application is visible in the tracker with a clearly labeled demo status

### Demo requirements

- Seed a few realistic jobs with clear match results
- Include one strong match and one partial match
- Show evidence for supported requirements and missing items
- Provide “Approved & Submitted (Demo)” language, not “Applied at Real Employer”

---

## 14. Implementation phases

### Phase 0 — Stabilize and map the current app

- Review and confirm working flow for resume upload, parsing, and tracker
- Document current conventions and data contracts
- Add the new CareerPilot plan without altering active behavior
- Identify exact modules for extension

### Phase 1 — Core onboarding + job model

- Add `UserProfile`, `JobPreference`, and provider-normalized `Job` schema
- Add onboarding API + UI
- Add seed/demo provider
- Persist discovered jobs in SQLite

### Phase 2 — Evidence vault + matching

- Add `Evidence` table and linking logic
- Implement explainable requirement matcher
- Add job matching endpoints and recommended jobs page
- Add a score + evidence explanation response shape

### Phase 3 — Application preparation + tracker flow

- Add draft generation logic
- Add screening question evaluation and user approval flow
- Extend tracker statuses for recommended / draft ready / approval states
- Add application review modal and approval actions

### Phase 4 — Career gaps + what-if simulator

- Add frequency-based missing skill analysis
- Add simulation mode without mutating real evidence
- Add gap dashboard UI

### Phase 5 — Demo polish and hardening

- Make demo mode deterministic and visible
- Add activity log and audit details
- Validate route UX and security behavior
- Perform targeted backend and frontend tests

---

## 15. Testing strategy

### Backend tests

Add deterministic tests for:

- provider normalization
- job discovery output contract
- requirement scoring with supported/partial/missing evidence
- evidence-grounding validation fails on unsupported claims
- application draft generation given verified evidence only
- demo mode flow

Target test directories:

- `apps/backend/tests/unit/`
- `apps/backend/tests/service/`
- `apps/backend/tests/integration/`

### Frontend tests

Add UI tests for:

- onboarding flow
- recommended jobs cards and match labels
- job analysis page render
- tracker status transitions
- demo mode banner and clear labeling

### Critical principle

Tests should validate behavior and evidence, not mock-only happy paths. The demo mode should be deterministic and easy to verify.

---

## 16. Risks and mitigations

### Risk: over-scoring based on keyword overlap

Mitigation: require evidence linking and explainability; never produce a numeric match without evidence.

### Risk: a provider abstraction gets too broad too early

Mitigation: keep MVP to `DemoProvider` + 1 permitted provider, with registry-first design.

### Risk: false claims in tailored resume text

Mitigation: add evidence-validation gate before writing any application draft or tailored resume.

### Risk: UI becomes too complex before backend is stable

Mitigation: build the backend contract first, then the pages around it; keep the demo flow simple and deterministic.

### Risk: security issues around provider credentials and user data

Mitigation: keep all secrets in env vars or encrypted store and keep provider-specific tokens isolated.

---

## 17. MVP completion checklist

### Required for MVP

- [ ] User onboarding with profile + preferences
- [ ] Multiple resume profiles supported
- [ ] Job discovery abstraction with at least one real or demo provider
- [ ] Normalized job model
- [ ] Explainable match score with evidence links
- [ ] Evidence vault and unsupported-claim guarding
- [ ] Application draft generation with human approval default
- [ ] Application tracker / Kanban flow
- [ ] Demo mode with explicit labeling
- [ ] Activity log / agent audit trail
- [ ] Job analysis page with match and evidence breakdown
- [ ] Backend endpoints and frontend pages connected
- [ ] Tests covering the key CareerPilot logic

### Deferred to later phases

- [ ] Advanced auto-apply rules
- [ ] Advanced analytics dashboards
- [ ] Extra providers and feeds
- [ ] Notifications and integrations
- [ ] Full production-grade provider automation

---

## 18. Recommended first implementation sequence

1. Create the data model additions and migration-safe storage methods
2. Add the `JobProvider` interface and `DemoProvider`
3. Implement a minimal `DiscoveryService` that normalizes jobs
4. Add the matching engine with evidence-backed output
5. Add the first job analysis API and UI page
6. Add the application draft and approval workflow
7. Add tracker integration and audit log
8. Add demo mode and deterministic seed data
9. Add tests around score/evidence and demo workflow

This sequence keeps the project runnable while introducing CareerPilot in a controlled, testable way.

---

## 19. Summary recommendation

The fastest path to a credible hackathon CareerPilot MVP is not to replace Resume Matcher, but to extend it deliberately:

- keep the current resume, tailoring, and tracker backend flows
- add a job discovery abstraction and normalized job model
- add an evidence vault and explainable matching engine
- add a deterministic demo path
- keep human approval as the default safety model

This approach gives a real product story, preserves working functionality, and keeps implementation complexity manageable for a hackathon sprint.

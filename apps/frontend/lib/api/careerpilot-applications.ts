import { apiFetch, apiPatch, apiPost } from '@/lib/api/client';

export interface ScreeningQuestion {
  question_id: string;
  type: 'YES_NO' | 'TEXT' | 'NUMBER' | 'SELECT' | string;
  question: string;
  suggested_answer?: string | number | null;
  answer?: string | number | boolean | null;
  status: string;
  evidence?: string | null;
  requires_confirmation?: boolean;
}

export interface CareerPilotApplication {
  application_id: string;
  job_id: string;
  source_resume_id: string;
  original_resume_id: string;
  tailored_resume_id: string;
  status: string;
  tracker_status: string;
  company?: string | null;
  role?: string | null;
  match: {
    overall_score?: number;
    recommendation?: string;
    evidence?: Array<{ requirement: string; status: string; evidence?: string | null }>;
  };
  changes: Array<{
    section: string;
    type: string;
    before: string;
    after: string;
    reason: string;
    evidence_source?: string | null;
  }>;
  claim_validation: {
    needs_review?: boolean;
    verified_claim_count?: number;
    unsupported_claims?: Array<{ claim_type: string; claim: string; reason: string }>;
  };
  screening_questions: ScreeningQuestion[];
  cover_letter?: string | null;
  needs_review: boolean;
  demo_mode: boolean;
  events: Array<{ event: string; timestamp: string; metadata: Record<string, unknown> }>;
}

async function readJson<T>(response: Response, fallback: string): Promise<T> {
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    const detail = typeof payload?.detail === 'string' ? payload.detail : fallback;
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export async function prepareCareerPilotApplication(
  jobId: string,
  resumeId?: string
): Promise<CareerPilotApplication> {
  const response = await apiPost(`/careerpilot/jobs/${encodeURIComponent(jobId)}/prepare`, {
    resume_id: resumeId ?? null,
  });
  return readJson<CareerPilotApplication>(response, 'Unable to prepare application.');
}

export async function fetchCareerPilotApplicationReview(
  applicationId: string
): Promise<CareerPilotApplication> {
  const response = await apiFetch(
    `/careerpilot/applications/${encodeURIComponent(applicationId)}/review`,
    { credentials: 'include' }
  );
  return readJson<CareerPilotApplication>(response, 'Unable to load application review.');
}

export async function updateCareerPilotScreening(
  applicationId: string,
  answers: Record<string, string | number | boolean>
): Promise<CareerPilotApplication> {
  const response = await apiPatch(
    `/careerpilot/applications/${encodeURIComponent(applicationId)}/screening`,
    { answers }
  );
  return readJson<CareerPilotApplication>(response, 'Unable to save screening answers.');
}

export async function updateCareerPilotCoverLetter(
  applicationId: string,
  content: string
): Promise<CareerPilotApplication> {
  const response = await apiPatch(
    `/careerpilot/applications/${encodeURIComponent(applicationId)}/cover-letter`,
    { content }
  );
  return readJson<CareerPilotApplication>(response, 'Unable to save cover letter.');
}

export async function regenerateCareerPilotCoverLetter(
  applicationId: string
): Promise<CareerPilotApplication> {
  const response = await apiPost(
    `/careerpilot/applications/${encodeURIComponent(applicationId)}/cover-letter/regenerate`,
    {}
  );
  return readJson<CareerPilotApplication>(response, 'Unable to regenerate cover letter.');
}

export async function approveCareerPilotApplication(
  applicationId: string
): Promise<{ application_id: string; status: string; tracker_status: string; message: string }> {
  const response = await apiPost(
    `/careerpilot/applications/${encodeURIComponent(applicationId)}/approve`,
    {}
  );
  return readJson(response, 'Unable to approve application.');
}

export async function rejectCareerPilotApplication(applicationId: string): Promise<void> {
  const response = await apiPost(
    `/careerpilot/applications/${encodeURIComponent(applicationId)}/reject`,
    {}
  );
  await readJson(response, 'Unable to reject application.');
}

import { apiFetch, apiPost } from '@/lib/api/client';

export interface CareerPilotJob {
  id: string;
  external_id?: string | null;
  provider?: string;
  company: string;
  title: string;
  description: string;
  location?: string | null;
  work_mode?: string | null;
  employment_type?: string | null;
  salary_min?: number | null;
  salary_max?: number | null;
  currency?: string | null;
  experience_required?: string | null;
  skills_required?: string[];
  skills_preferred?: string[];
  qualifications?: string[];
  hard_requirements?: string[];
  application_url?: string | null;
  posted_at?: string | null;
  discovered_at?: string | null;
}

export interface CareerPilotMatchResult {
  overall_score: number;
  recommendation: string;
  matched_requirements: string[];
  partially_matched_requirements: string[];
  missing_requirements: string[];
  hard_requirement_failures: string[];
  evidence: Array<{
    requirement: string;
    status: string;
    evidence?: string | null;
    source?: string;
  }>;
  score_breakdown: Record<string, number>;
}

export async function fetchCareerPilotJobs(): Promise<CareerPilotJob[]> {
  const response = await apiFetch('/careerpilot/jobs', { credentials: 'include' });
  if (!response.ok) {
    throw new Error('Unable to load recommended jobs.');
  }
  const payload = await response.json();
  return payload.jobs ?? [];
}

export async function discoverCareerPilotJobs(): Promise<CareerPilotJob[]> {
  const response = await apiPost('/careerpilot/jobs/discover', {
    criteria: {},
    persist: true,
  });
  if (!response.ok) {
    throw new Error('Error discovering jobs');
  }
  const payload = await response.json();
  return payload.jobs ?? [];
}

export async function fetchCareerPilotJob(jobId: string): Promise<CareerPilotJob> {
  const response = await apiFetch(`/careerpilot/jobs/${encodeURIComponent(jobId)}`, {
    credentials: 'include',
  });
  if (!response.ok) {
    throw new Error('Unable to load job details.');
  }
  const payload = await response.json();
  return payload.job;
}

export async function fetchCareerPilotMatch(jobId: string): Promise<CareerPilotMatchResult> {
  const response = await apiFetch(`/careerpilot/jobs/${encodeURIComponent(jobId)}/match`, {
    credentials: 'include',
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    const detail = typeof payload?.detail === 'string' ? payload.detail : null;
    throw new Error(detail ?? 'Unable to load job match.');
  }
  const payload = await response.json();
  return payload.match;
}

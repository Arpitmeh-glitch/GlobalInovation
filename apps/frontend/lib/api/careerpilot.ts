import { apiFetch, apiPost, apiPut } from '@/lib/api/client';

export interface CareerPilotProfile {
  profile_id?: string;
  target_role: string;
  skills: string[];
  experience_level: string;
  years_experience?: number | null;
  education?: string | null;
  preferred_locations: string[];
  work_preference: 'remote' | 'hybrid' | 'onsite';
  industries: string[];
  salary_expectation?: number | null;
  created_at?: string;
  updated_at?: string;
}

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
  match?: CareerPilotMatchResult | null;
}

export interface CareerPilotMatchResult {
  overall_score: number;
  recommendation: string;
  matched_skills: string[];
  missing_skills: string[];
  experience_match: boolean | null;
  education_match: boolean | null;
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

export interface CareerPilotDiscoveryResponse {
  jobs: CareerPilotJob[];
  total: number;
  offset: number;
  limit: number | null;
  has_more: boolean;
  demo_mode: boolean;
}

function discoveryQuery(criteria: CareerPilotDiscoveryCriteria): string {
  const params = new URLSearchParams();
  Object.entries(criteria).forEach(([key, value]) => {
    if (value === undefined || value === '') return;
    params.set(key, Array.isArray(value) ? value.join(',') : String(value));
  });
  const query = params.toString();
  return query ? `?${query}` : '';
}

export async function fetchCareerPilotJobs(): Promise<CareerPilotJob[]> {
  const response = await apiFetch('/careerpilot/jobs', { credentials: 'include' });
  if (!response.ok) {
    throw new Error('Unable to load recommended jobs.');
  }
  const payload = await response.json();
  if (!payload || !Array.isArray(payload.jobs)) throw new Error('Malformed jobs response.');
  return payload.jobs;
}

export async function fetchCareerPilotJobsPage(
  criteria: CareerPilotDiscoveryCriteria = {}
): Promise<CareerPilotDiscoveryResponse> {
  const response = await apiFetch(`/careerpilot/jobs${discoveryQuery(criteria)}`, {
    credentials: 'include',
  });
  if (!response.ok) throw new Error('Unable to load recommended jobs.');
  const payload = await response.json();
  if (!payload || !Array.isArray(payload.jobs) || typeof payload.total !== 'number') {
    throw new Error('Malformed jobs response.');
  }
  return payload;
}

export async function fetchCareerPilotProfile(): Promise<CareerPilotProfile | null> {
  const response = await apiFetch('/careerpilot/profile', { credentials: 'include' });
  if (!response.ok) throw new Error('Unable to load your CareerPilot profile.');
  return response.json();
}

export async function saveCareerPilotProfile(
  profile: CareerPilotProfile
): Promise<CareerPilotProfile> {
  const response = await apiPut('/careerpilot/profile', profile);
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(typeof payload?.detail === 'string' ? payload.detail : 'Unable to save profile.');
  }
  return response.json();
}

export interface CareerPilotDiscoveryCriteria {
  role?: string;
  location?: string;
  work_mode?: string;
  employment_type?: string;
  keywords?: string[];
  min_salary?: number;
  max_salary?: number;
  min_experience?: number;
  max_experience?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc' | string;
  offset?: number;
  limit?: number;
}

export async function discoverCareerPilotJobs(
  criteria: CareerPilotDiscoveryCriteria = {}
): Promise<CareerPilotJob[]> {
  const response = await apiPost('/careerpilot/jobs/discover', {
    criteria,
    persist: true,
  });
  if (!response.ok) {
    throw new Error('Error discovering jobs');
  }
  const payload = await response.json();
  if (!payload || !Array.isArray(payload.jobs)) throw new Error('Malformed jobs response.');
  return payload.jobs;
}

export async function discoverCareerPilotJobsPage(
  criteria: CareerPilotDiscoveryCriteria = {}
): Promise<CareerPilotDiscoveryResponse> {
  const response = await apiPost('/careerpilot/jobs/discover', {
    criteria,
    persist: true,
  });
  if (!response.ok) throw new Error('Error discovering jobs');
  const payload = await response.json();
  if (!payload || !Array.isArray(payload.jobs) || typeof payload.total !== 'number') {
    throw new Error('Malformed jobs response.');
  }
  return payload;
}

export async function fetchCareerPilotJob(jobId: string): Promise<CareerPilotJob> {
  const response = await apiFetch(`/careerpilot/jobs/${encodeURIComponent(jobId)}`, {
    credentials: 'include',
  });
  if (!response.ok) {
    throw new Error('Unable to load job details.');
  }
  const payload = await response.json();
  if (!payload || !payload.job || typeof payload.job.id !== 'string') {
    throw new Error('Malformed job response.');
  }
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
  if (!payload || !payload.match || typeof payload.match.overall_score !== 'number') {
    throw new Error('Malformed match response.');
  }
  return payload.match;
}

import { apiFetch, apiPost } from '@/lib/api/client';

export interface CareerGapItem {
  name: string;
  frequency: number;
  gap_type: 'skill_gap' | 'evidence_gap';
  recommendation: string;
}

export interface CareerGapsResponse {
  gaps: CareerGapItem[];
  target_role: string | null;
  filters: Record<string, unknown>;
  total_jobs_analyzed: number;
}

export interface SimulationRequest {
  resume_id?: string | null;
  resume?: Record<string, unknown> | null;
  job_ids?: string[];
  criteria?: Record<string, unknown> | null;
  hypothetical_skills: string[];
  hypothetical_experience?: string | null;
  hypothetical_education?: string | null;
}

export interface SimulationSummary {
  jobs_analyzed: number;
  average_score: number;
  average_score_delta: number;
}

export interface SimulationComparisonItem {
  job_id: string;
  job_title: string;
  baseline_score: number;
  baseline_matched_skills: string[];
  baseline_missing_skills: string[];
  simulated_score: number;
  simulated_matched_skills: string[];
  simulated_missing_skills: string[];
  score_delta: number;
  is_hypothetical: true;
}

export interface SimulationResponse {
  original_summary: SimulationSummary;
  simulated_summary: SimulationSummary;
  comparisons: SimulationComparisonItem[];
  hypothetical_additions: Record<string, unknown>;
}

async function readJson<T>(response: Response, fallback: string): Promise<T> {
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(typeof payload?.detail === 'string' ? payload.detail : fallback);
  }
  return response.json() as Promise<T>;
}

export async function fetchCareerGaps(params: { target_role?: string; limit?: number } = {}): Promise<CareerGapsResponse> {
  const query = new URLSearchParams();
  if (params.target_role?.trim()) query.set('role', params.target_role.trim());
  if (params.limit !== undefined) query.set('limit', String(Math.max(1, Math.min(params.limit, 100))));
  const suffix = query.toString() ? `?${query.toString()}` : '';
  const response = await apiFetch(`/careerpilot/gaps${suffix}`, { credentials: 'include' });
  const payload = await readJson<CareerGapsResponse>(response, 'Unable to load career gaps.');
  if (!payload || !Array.isArray(payload.gaps) || typeof payload.total_jobs_analyzed !== 'number') {
    throw new Error('Malformed career gaps response.');
  }
  return params.limit === undefined ? payload : { ...payload, gaps: payload.gaps.slice(0, params.limit) };
}

export async function simulateSkillImpact(payload: SimulationRequest): Promise<SimulationResponse> {
  const response = await apiPost('/careerpilot/simulate', payload);
  const result = await readJson<SimulationResponse>(response, 'Unable to run skill simulation.');
  if (!result || !Array.isArray(result.comparisons) || !result.original_summary || !result.simulated_summary) {
    throw new Error('Malformed simulation response.');
  }
  return result;
}

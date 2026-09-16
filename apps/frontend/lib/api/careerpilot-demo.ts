import { apiFetch, apiPost } from '@/lib/api/client';

export interface DemoStatus {
  is_demo_mode: boolean;
  demo_user_id: string;
  seeded_at: string | null;
  demo_scenario: string;
  metadata: Record<string, unknown>;
}

export interface DemoHealthResponse {
  status: DemoStatus;
  available_scenarios: string[];
  profile_preview: Record<string, unknown>;
  activity_count: number;
}

export interface DemoResetResponse {
  status: string;
  message: string;
  demo_profile_id: string;
  seeded_jobs_count: number;
  seeded_activities_count: number;
}

export async function fetchDemoStatus(): Promise<DemoHealthResponse> {
  const response = await apiFetch('/careerpilot/demo', { credentials: 'include' });
  if (!response.ok) throw new Error('Unable to load demo status.');
  const payload = (await response.json()) as DemoHealthResponse;
  if (!payload?.status || !Array.isArray(payload.available_scenarios)) {
    throw new Error('Malformed demo status response.');
  }
  return payload;
}

export async function resetDemoState(scenario = 'default'): Promise<DemoResetResponse> {
  const response = await apiPost('/careerpilot/demo/reset', { scenario, force_clean: true });
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(typeof payload?.detail === 'string' ? payload.detail : 'Unable to reset demo state.');
  }
  const payload = (await response.json()) as DemoResetResponse;
  if (!payload || typeof payload.seeded_jobs_count !== 'number') {
    throw new Error('Malformed demo reset response.');
  }
  return payload;
}

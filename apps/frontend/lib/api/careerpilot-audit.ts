import { apiFetch } from '@/lib/api/client';

export interface ActivityLog {
  id: number;
  user_id: string | null;
  activity_type: string;
  action: string;
  details: Record<string, unknown>;
  status: 'success' | 'failure' | string;
  created_at: string;
}

export interface ActivityLogResponse {
  activities: ActivityLog[];
  limit: number;
  offset: number;
  count: number;
}

export async function fetchActivityLogs(
  params: { activity_type?: string; limit?: number; offset?: number } = {}
): Promise<ActivityLogResponse> {
  const query = new URLSearchParams();
  if (params.activity_type) query.set('activity_type', params.activity_type);
  if (params.limit !== undefined) query.set('limit', String(Math.max(1, Math.min(params.limit, 100))));
  if (params.offset !== undefined) query.set('offset', String(Math.max(0, params.offset)));
  const suffix = query.toString() ? `?${query.toString()}` : '';
  const response = await apiFetch(`/careerpilot/activity-log${suffix}`, { credentials: 'include' });
  if (!response.ok) throw new Error('Unable to load activity logs.');
  const payload = (await response.json()) as ActivityLogResponse;
  if (!payload || !Array.isArray(payload.activities) || typeof payload.count !== 'number') {
    throw new Error('Malformed activity log response.');
  }
  return payload;
}

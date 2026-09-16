import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { discoverCareerPilotJobsPage, fetchCareerPilotJobsPage } from '@/lib/api/careerpilot';

const response = {
  jobs: [],
  total: 12,
  offset: 6,
  limit: 6,
  has_more: false,
  demo_mode: true,
};

describe('CareerPilot discovery API', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify(response), { status: 200 })));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('loads a filtered page with backend pagination parameters', async () => {
    await expect(fetchCareerPilotJobsPage({ work_mode: 'remote', sort_by: 'salary', offset: 6, limit: 6 })).resolves.toMatchObject(response);
    const [url] = vi.mocked(fetch).mock.calls[0];
    expect(String(url)).toContain('/careerpilot/jobs?');
    expect(String(url)).toContain('work_mode=remote');
    expect(String(url)).toContain('offset=6');
  });

  it('posts discovery criteria without fabricating job data', async () => {
    await expect(discoverCareerPilotJobsPage({ min_salary: 800000, min_experience: 2 })).resolves.toMatchObject(response);
    const [, options] = vi.mocked(fetch).mock.calls[0];
    expect(options?.method).toBe('POST');
    expect(JSON.parse(String(options?.body))).toMatchObject({
      criteria: { min_salary: 800000, min_experience: 2 },
      persist: true,
    });
  });

  it('rejects malformed discovery payloads', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ jobs: null }), { status: 200 })));
    await expect(fetchCareerPilotJobsPage()).rejects.toThrow('Malformed jobs response.');
  });
});

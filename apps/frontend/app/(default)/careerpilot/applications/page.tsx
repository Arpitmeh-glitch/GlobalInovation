'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { apiFetch, apiPatch } from '@/lib/api/client';

const statuses = ['saved', 'applied', 'response', 'interview', 'accepted', 'rejected', 'no_response'] as const;
type Status = (typeof statuses)[number];
type Application = { application_id: string; job_id: string; status: Status; company?: string | null; role?: string | null; applied_at?: string | null; notes?: string | null; match_score?: number | null };
type Columns = Record<Status, Application[]>;

const emptyColumns = (): Columns => ({
  saved: [],
  applied: [],
  response: [],
  interview: [],
  accepted: [],
  rejected: [],
  no_response: [],
});

export default function CareerPilotApplicationsPage() {
  const [columns, setColumns] = useState<Columns>(emptyColumns);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const response = await apiFetch('/applications', { credentials: 'include' });
      if (!response.ok) throw new Error('Unable to load applications.');
      const payload = await response.json();
      setColumns({ ...emptyColumns(), ...(payload.columns ?? {}) });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load applications.');
    } finally {
      setLoading(false);
    }
  }

  async function updateStatus(applicationId: string, status: Status) {
    try {
      const response = await apiPatch(`/applications/${encodeURIComponent(applicationId)}`, { status });
      if (!response.ok) throw new Error('Unable to update application status.');
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to update application status.');
    }
  }

  useEffect(() => { void load(); }, []);

  return <main className="min-h-screen bg-background p-4 md:p-8"><div className="mx-auto max-w-7xl">
    <div className="flex flex-col gap-4 border border-black bg-white p-6 shadow-sw-md md:flex-row md:items-end md:justify-between"><div><Link href="/careerpilot" className="font-mono text-xs uppercase text-blue-700">Back to CareerPilot</Link><h1 className="mt-2 font-serif text-4xl font-semibold">Application tracking</h1><p className="mt-2 text-sm text-ink-soft">Review and update your applications. CareerPilot never submits to external sites automatically.</p></div><Link href="/careerpilot/jobs" className="border border-black bg-blue-700 px-3 py-2 font-mono text-[10px] font-bold uppercase text-white">Discover jobs</Link></div>
    {loading ? <p className="mt-8 font-mono text-xs uppercase">Loading applications...</p> : error ? <div role="alert" className="mt-6 border border-red-700 bg-red-50 p-4 text-sm text-red-700">{error}<button type="button" onClick={() => void load()} className="ml-3 underline">Retry</button></div> : <div className="mt-6 grid gap-4 lg:grid-cols-3 xl:grid-cols-7">{statuses.map((status) => <section key={status} className="min-h-48 border border-black bg-white p-3"><div className="flex items-center justify-between border-b border-black pb-2"><h2 className="font-mono text-[10px] font-bold uppercase">{status.replace('_', ' ')}</h2><span className="font-mono text-xs">{columns[status].length}</span></div><div className="mt-3 space-y-3">{columns[status].map((application) => <article key={application.application_id} className="border border-black bg-background p-3"><Link href={`/careerpilot/jobs/${encodeURIComponent(application.job_id)}`} className="font-serif text-lg font-semibold hover:text-blue-700">{application.role || 'Untitled role'}</Link><p className="mt-1 text-xs text-ink-soft">{application.company || 'Company not listed'}</p>{application.match_score != null && <p className="mt-2 font-mono text-[10px] uppercase">Match {application.match_score}%</p>}<Link href={`/careerpilot/applications/${encodeURIComponent(application.application_id)}/review`} className="mt-2 inline-block font-mono text-[10px] uppercase text-blue-700 underline">View application</Link><select aria-label={`Update status for ${application.role || 'application'}`} value={application.status} onChange={(event) => void updateStatus(application.application_id, event.target.value as Status)} className="mt-3 w-full border border-black bg-white px-2 py-1 font-mono text-[10px] uppercase"><option value="saved">Prepared</option><option value="applied">Applied</option><option value="response">Response</option><option value="interview">Interview</option><option value="accepted">Offer</option><option value="rejected">Rejected</option><option value="no_response">No response</option></select>{application.notes && <p className="mt-2 text-xs text-ink-soft">{application.notes}</p>}</article>)}{columns[status].length === 0 && <p className="text-xs text-ink-soft">Nothing here yet.</p>}</div></section>)}</div>}
  </div></main>;
}

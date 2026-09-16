'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import RefreshCw from 'lucide-react/dist/esm/icons/refresh-cw';
import Loader2 from 'lucide-react/dist/esm/icons/loader-2';
import { Button } from '@/components/ui/button';
import { DemoBanner } from '@/components/careerpilot/DemoBanner';
import { fetchActivityLogs, type ActivityLog } from '@/lib/api/careerpilot-audit';

const PAGE_SIZE = 10;

export default function ActivityPage() {
  const [activities, setActivities] = useState<ActivityLog[]>([]);
  const [activityType, setActivityType] = useState('');
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (nextOffset = 0) => {
    setLoading(true);
    setError(null);
    try {
      const payload = await fetchActivityLogs({ activity_type: activityType || undefined, limit: PAGE_SIZE, offset: nextOffset });
      setActivities(payload.activities);
      setOffset(nextOffset);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to load activity logs.');
    } finally {
      setLoading(false);
    }
  }, [activityType]);

  useEffect(() => { void load(0); }, [load]);

  return <main className="min-h-screen bg-background"><DemoBanner /><div className="mx-auto max-w-6xl p-4 md:p-8"><Link href="/careerpilot" className="font-mono text-xs uppercase text-blue-700">Back to CareerPilot</Link><header className="mt-4 flex flex-col gap-4 border border-black bg-white p-6 shadow-sw-md md:flex-row md:items-end md:justify-between"><div><p className="font-mono text-xs font-bold uppercase tracking-wider text-blue-700">Audit trail</p><h1 className="mt-2 font-serif text-4xl font-semibold">Activity log</h1><p className="mt-2 text-sm text-ink-soft">Sanitized activity events from CareerPilot operations.</p></div><Button variant="outline" onClick={() => void load(offset)} disabled={loading}><RefreshCw className={loading ? 'animate-spin' : ''} />Refresh</Button></header><div className="mt-6 flex flex-col gap-3 border border-black bg-white p-4 md:flex-row md:items-end"><label className="font-mono text-xs font-bold uppercase">Activity type<select value={activityType} onChange={(event) => setActivityType(event.target.value)} className="mt-2 h-10 w-full border border-black bg-background px-3 font-sans text-sm md:w-64"><option value="">All activity types</option><option value="demo_event">Demo events</option><option value="job_discovery">Job discovery</option><option value="match">Match analysis</option></select></label></div>{error && <div role="alert" className="mt-6 border border-red-700 bg-red-50 p-4 text-sm text-red-700">{error}<button type="button" onClick={() => void load(offset)} className="ml-3 underline">Retry</button></div>}{loading ? <div className="mt-8 flex items-center gap-2 font-mono text-xs uppercase"><Loader2 className="animate-spin" />Loading activity...</div> : activities.length === 0 ? <div className="mt-8 border border-black bg-white p-8 text-sm text-ink-soft">No activity events found.</div> : <div className="mt-8 space-y-3">{activities.map((activity) => <details key={activity.id} className="border border-black bg-white shadow-sw-sm"><summary className="flex cursor-pointer list-none flex-wrap items-center gap-3 p-4"><time className="font-mono text-xs text-ink-soft" dateTime={activity.created_at}>{new Date(activity.created_at).toLocaleString()}</time><span className="border border-black bg-background px-2 py-1 font-mono text-[10px] uppercase">{activity.activity_type}</span><span className="flex-1 font-semibold">{activity.action}</span><span className={`border border-black px-2 py-1 font-mono text-[10px] font-bold uppercase ${activity.status === 'success' ? 'bg-green-100 text-green-900' : 'bg-red-100 text-red-900'}`}>{activity.status}</span></summary><pre className="overflow-x-auto border-t border-black bg-background p-4 font-mono text-xs whitespace-pre-wrap">{JSON.stringify(activity.details, null, 2)}</pre></details>)}</div>}{!loading && (offset > 0 || activities.length === PAGE_SIZE) && <div className="mt-6 flex items-center justify-between border-t border-black pt-4"><Button variant="outline" disabled={offset === 0} onClick={() => void load(Math.max(0, offset - PAGE_SIZE))}>Previous</Button><span className="font-mono text-xs uppercase">Events {offset + 1}-{offset + activities.length}</span><Button variant="outline" disabled={activities.length < PAGE_SIZE} onClick={() => void load(offset + PAGE_SIZE)}>Next</Button></div>}</div></main>;
}

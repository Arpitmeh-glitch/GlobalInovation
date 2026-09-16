'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import Loader2 from 'lucide-react/dist/esm/icons/loader-2';
import { Button } from '@/components/ui/button';
import { DemoBanner } from '@/components/careerpilot/DemoBanner';
import { fetchDemoStatus, resetDemoState, type DemoHealthResponse } from '@/lib/api/careerpilot-demo';
import { fetchCareerPilotJobsPage } from '@/lib/api/careerpilot';

export default function DemoPage() {
  const [data, setData] = useState<DemoHealthResponse | null>(null);
  const [scenario, setScenario] = useState('default');
  const [loading, setLoading] = useState(true);
  const [resetting, setResetting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [jobCount, setJobCount] = useState(0);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [next, jobs] = await Promise.all([
        fetchDemoStatus(),
        fetchCareerPilotJobsPage({ limit: 100 }),
      ]);
      setData(next);
      setScenario(next.status.demo_scenario);
      setJobCount(jobs.total);
    } catch (caught) {
      setMessage(caught instanceof Error ? caught.message : 'Unable to load demo status.');
    } finally {
      setLoading(false);
    }
  }, []);

  async function reset() {
    setResetting(true);
    setMessage(null);
    try {
      const result = await resetDemoState(scenario);
      setMessage(`${result.message} ${result.seeded_jobs_count} jobs and ${result.seeded_activities_count} activities restored.`);
      await load();
    } catch (caught) {
      setMessage(caught instanceof Error ? caught.message : 'Unable to reset demo state.');
    } finally {
      setResetting(false);
    }
  }

  useEffect(() => { void load(); }, [load]);

  return <main className="min-h-screen bg-background"><DemoBanner /><div className="mx-auto max-w-6xl p-4 md:p-8"><Link href="/careerpilot" className="font-mono text-xs uppercase text-blue-700">Back to CareerPilot</Link><header className="mt-4 border border-black bg-white p-6 shadow-sw-md"><p className="font-mono text-xs font-bold uppercase tracking-wider text-blue-700">Demo operations</p><h1 className="mt-2 font-serif text-4xl font-semibold">Demo workspace</h1><p className="mt-2 text-sm text-ink-soft">Inspect and reset the deterministic CareerPilot demo fixtures. Real user records are isolated.</p></header>{loading ? <div className="mt-8 flex items-center gap-2 font-mono text-xs uppercase"><Loader2 className="animate-spin" />Loading demo status...</div> : data ? <><div className="mt-6 grid gap-4 md:grid-cols-4"><div className="border border-black bg-white p-5"><p className="font-mono text-xs uppercase text-ink-soft">Scenario</p><p className="mt-2 font-serif text-2xl font-semibold">{data.status.demo_scenario}</p></div><div className="border border-black bg-white p-5"><p className="font-mono text-xs uppercase text-ink-soft">Seeded jobs</p><p className="mt-2 font-serif text-2xl font-semibold">{jobCount}</p></div><div className="border border-black bg-white p-5"><p className="font-mono text-xs uppercase text-ink-soft">Demo activities</p><p className="mt-2 font-serif text-2xl font-semibold">{data.activity_count}</p></div><div className="border border-black bg-white p-5"><p className="font-mono text-xs uppercase text-ink-soft">Demo user</p><p className="mt-2 break-all font-mono text-sm">{data.status.demo_user_id}</p></div></div><section className="mt-6 grid gap-6 lg:grid-cols-[1fr_20rem]"><div className="border border-black bg-white p-6"><h2 className="font-serif text-2xl font-semibold">Mock candidate overview</h2><dl className="mt-5 grid gap-3 text-sm sm:grid-cols-2">{Object.entries(data.profile_preview).filter(([key]) => key !== 'skills').map(([key, value]) => <div key={key} className="border-b border-black pb-2"><dt className="font-mono text-[10px] uppercase text-ink-soft">{key.replaceAll('_', ' ')}</dt><dd className="mt-1">{Array.isArray(value) ? value.join(', ') : String(value ?? 'Not specified')}</dd></div>)}</dl><div className="mt-5"><p className="font-mono text-[10px] uppercase text-ink-soft">Skills</p><p className="mt-2 text-sm">{String((data.profile_preview.skills as string[] | undefined)?.join(', ') ?? 'None')}</p></div></div><div className="border border-black bg-white p-6"><h2 className="font-serif text-2xl font-semibold">Reset fixtures</h2><label className="mt-5 block font-mono text-xs font-bold uppercase">Scenario<select value={scenario} onChange={(event) => setScenario(event.target.value)} className="mt-2 h-10 w-full border border-black bg-background px-2 font-sans text-sm">{data.available_scenarios.map((option) => <option key={option} value={option}>{option}</option>)}</select></label><Button onClick={() => void reset()} disabled={resetting} className="mt-5 w-full">{resetting && <Loader2 className="animate-spin" />}{resetting ? 'Resetting...' : 'Reset demo state'}</Button>{message && <p role="status" className="mt-4 border border-black bg-[#FFF9DB] p-3 text-sm">{message}</p>}</div></section></> : <div role="alert" className="mt-8 border border-red-700 bg-red-50 p-4 text-sm text-red-700">{message ?? 'Demo status unavailable.'}<button type="button" onClick={() => void load()} className="ml-3 underline">Retry</button></div>}</div></main>;
}

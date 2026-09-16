'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import RefreshCw from 'lucide-react/dist/esm/icons/refresh-cw';
import Loader2 from 'lucide-react/dist/esm/icons/loader-2';
import { Button } from '@/components/ui/button';
import { DemoBanner } from '@/components/careerpilot/DemoBanner';
import { fetchCareerGaps, type CareerGapItem } from '@/lib/api/careerpilot-intelligence';
import { fetchCareerPilotProfile } from '@/lib/api/careerpilot';

export default function CareerGapsPage() {
  const [role, setRole] = useState('');
  const [gaps, setGaps] = useState<CareerGapItem[]>([]);
  const [jobsAnalyzed, setJobsAnalyzed] = useState(0);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadGaps = useCallback(async (selectedRole = role) => {
    setRefreshing(true);
    setError(null);
    try {
      const result = await fetchCareerGaps({ target_role: selectedRole || undefined, limit: 50 });
      setGaps(result.gaps);
      setJobsAnalyzed(result.total_jobs_analyzed);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to load career gaps.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [role]);

  useEffect(() => {
    void fetchCareerPilotProfile()
      .then((profile) => {
        const savedRole = profile?.target_role ?? '';
        setRole(savedRole);
        void loadGaps(savedRole);
      })
      .catch(() => void loadGaps(''));
  }, [loadGaps]);

  return (
    <main className="min-h-screen bg-background">
      <DemoBanner />
      <div className="mx-auto max-w-6xl p-4 md:p-8">
        <Link href="/careerpilot" className="font-mono text-xs uppercase text-blue-700">Back to CareerPilot</Link>
        <header className="mt-4 flex flex-col gap-4 border border-black bg-white p-6 shadow-sw-md md:flex-row md:items-end md:justify-between">
          <div><p className="font-mono text-xs font-bold uppercase tracking-wider text-blue-700">Career intelligence</p><h1 className="mt-2 font-serif text-4xl font-semibold">Career gaps</h1><p className="mt-2 text-sm text-ink-soft">Recurring requirements across the jobs in your selected feed.</p></div>
          <Button variant="outline" onClick={() => void loadGaps()} disabled={refreshing}><RefreshCw className={refreshing ? 'animate-spin' : ''} />Refresh analysis</Button>
        </header>
        <form onSubmit={(event) => { event.preventDefault(); void loadGaps(); }} className="mt-6 flex flex-col gap-3 border border-black bg-white p-4 md:flex-row md:items-end">
          <label className="flex-1 font-mono text-xs font-bold uppercase tracking-wider">Target role<input value={role} onChange={(event) => setRole(event.target.value)} placeholder="e.g. Backend Engineer" className="mt-2 h-10 w-full border border-black bg-background px-3 font-sans text-sm" /></label>
          <Button type="submit" disabled={refreshing}>Apply role filter</Button>
        </form>
        {error && <div role="alert" className="mt-6 border border-red-700 bg-red-50 p-4 text-sm text-red-700">{error}<button type="button" className="ml-3 underline" onClick={() => void loadGaps()}>Retry</button></div>}
        {loading ? <div className="mt-8 flex items-center gap-2 font-mono text-xs uppercase"><Loader2 className="animate-spin" />Loading gaps...</div> : gaps.length === 0 ? <div className="mt-8 border border-black bg-white p-8 text-sm text-ink-soft">No gaps were found across {jobsAnalyzed} analyzed jobs.</div> : <><p className="mt-8 font-mono text-xs uppercase text-ink-soft">{jobsAnalyzed} jobs analyzed · {gaps.length} recurring gaps</p><div className="mt-3 grid gap-4 md:grid-cols-2">{gaps.map((gap) => <article key={`${gap.name}-${gap.gap_type}`} className="border border-black bg-white p-5 shadow-sw-sm"><div className="flex items-start justify-between gap-3"><h2 className="font-serif text-2xl font-semibold">{gap.name}</h2><span className={`shrink-0 border border-black px-2 py-1 font-mono text-[10px] font-bold uppercase ${gap.gap_type === 'evidence_gap' ? 'bg-[#FFF9DB]' : 'bg-blue-700 text-white'}`}>{gap.gap_type.replace('_', ' ')}</span></div><p className="mt-4 font-mono text-sm">Appears in {gap.frequency} job{gap.frequency === 1 ? '' : 's'}</p><div className="mt-4 border-t border-black pt-4"><p className="font-mono text-[10px] font-bold uppercase tracking-wider text-blue-700">Recommended next step</p><p className="mt-2 text-sm leading-relaxed text-ink-soft">{gap.recommendation}</p></div></article>)}</div></>}
      </div>
    </main>
  );
}

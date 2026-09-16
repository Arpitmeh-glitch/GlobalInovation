'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import RefreshCw from 'lucide-react/dist/esm/icons/refresh-cw';
import Search from 'lucide-react/dist/esm/icons/search';
import Loader2 from 'lucide-react/dist/esm/icons/loader-2';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  discoverCareerPilotJobsPage,
  fetchCareerPilotJobsPage,
  type CareerPilotJob,
} from '@/lib/api/careerpilot';

export default function RecommendedJobsPage() {
  const [jobs, setJobs] = useState<CareerPilotJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [discovering, setDiscovering] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [role, setRole] = useState('');
  const [location, setLocation] = useState('');
  const [workMode, setWorkMode] = useState('');
  const [employmentType, setEmploymentType] = useState('');
  const [sortBy, setSortBy] = useState('match_score');
  const [sortOrder, setSortOrder] = useState('desc');
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);
  const [minSalary, setMinSalary] = useState('');
  const [maxSalary, setMaxSalary] = useState('');
  const [minExperience, setMinExperience] = useState('');
  const [maxExperience, setMaxExperience] = useState('');
  const pageSize = 6;

  async function loadJobs() {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchCareerPilotJobsPage({
        role: role.trim() || undefined,
        location: location.trim() || undefined,
        work_mode: workMode || undefined,
        employment_type: employmentType || undefined,
        min_salary: minSalary ? Number(minSalary) : undefined,
        max_salary: maxSalary ? Number(maxSalary) : undefined,
        min_experience: minExperience ? Number(minExperience) : undefined,
        max_experience: maxExperience ? Number(maxExperience) : undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
        offset,
        limit: pageSize,
      });
      setJobs(result.jobs);
      setTotal(result.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load recommended jobs.');
    } finally {
      setLoading(false);
    }
  }

  async function discoverJobs() {
    setDiscovering(true);
    setError(null);
    try {
      const result = await discoverCareerPilotJobsPage({
        role: role.trim() || undefined,
        location: location.trim() || undefined,
        work_mode: workMode || undefined,
        employment_type: employmentType || undefined,
        min_salary: minSalary ? Number(minSalary) : undefined,
        max_salary: maxSalary ? Number(maxSalary) : undefined,
        min_experience: minExperience ? Number(minExperience) : undefined,
        max_experience: maxExperience ? Number(maxExperience) : undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
        offset: 0,
        limit: pageSize,
      });
      setJobs(result.jobs);
      setTotal(result.total);
      setOffset(0);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error discovering jobs');
    } finally {
      setDiscovering(false);
    }
  }

  useEffect(() => {
    void loadJobs();
  }, [offset, sortBy, sortOrder]);

  return (
    <main className="min-h-screen bg-background p-4 md:p-8">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6 flex flex-col gap-4 border border-black bg-white p-4 shadow-sw-md md:flex-row md:items-end md:justify-between">
          <div>
            <p className="font-mono text-xs font-bold uppercase tracking-wider text-blue-700">
              Demo Mode — Sample Job Data
            </p>
            <h1 className="mt-2 font-serif text-4xl font-semibold text-ink">Recommended Jobs</h1>
          </div>
          <Link
            href="/careerpilot"
            className="inline-flex items-center border border-black bg-background px-4 py-2 font-mono text-xs font-bold uppercase tracking-wider text-black transition hover:translate-y-[1px] hover:translate-x-[1px] hover:shadow-sw-sm"
          >
            Back to dashboard
          </Link>
        </div>

        <div className="mb-6 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={() => void discoverJobs()}
            disabled={discovering}
            className="inline-flex items-center gap-2 border border-black bg-blue-700 px-4 py-2 font-mono text-xs font-bold uppercase tracking-wider text-white shadow-sw-sm transition hover:translate-y-[1px] hover:translate-x-[1px] hover:shadow-none disabled:cursor-wait disabled:opacity-60"
          >
            {discovering ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Search className="h-4 w-4" />
            )}
            {discovering ? 'Discovering jobs...' : 'Discover Jobs'}
          </button>
          <button
            type="button"
            onClick={() => void loadJobs()}
            disabled={loading || discovering}
            className="inline-flex items-center gap-2 border border-black bg-background px-4 py-2 font-mono text-xs font-bold uppercase tracking-wider text-black shadow-sw-sm transition hover:translate-y-[1px] hover:translate-x-[1px] hover:shadow-none disabled:cursor-wait disabled:opacity-60"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
          {discovering && (
            <span className="font-mono text-xs uppercase tracking-wider text-ink-soft">
              Analyzing opportunities...
            </span>
          )}
        </div>

        <form
          onSubmit={(event) => {
            event.preventDefault();
            void discoverJobs();
          }}
          className="mb-6 grid gap-3 border border-black bg-white p-4 shadow-sw-sm md:grid-cols-4"
        >
          <input value={role} onChange={(event) => setRole(event.target.value)} placeholder="Role or keyword" aria-label="Role or keyword" className="border border-black bg-background px-3 py-2 text-sm" />
          <input value={location} onChange={(event) => setLocation(event.target.value)} placeholder="Location" aria-label="Location" className="border border-black bg-background px-3 py-2 text-sm" />
          <select value={workMode} onChange={(event) => setWorkMode(event.target.value)} aria-label="Work mode" className="border border-black bg-background px-3 py-2 text-sm">
            <option value="">Any work mode</option><option value="remote">Remote</option><option value="hybrid">Hybrid</option><option value="onsite">On-site</option>
          </select>
          <select value={employmentType} onChange={(event) => setEmploymentType(event.target.value)} aria-label="Employment type" className="border border-black bg-background px-3 py-2 text-sm">
            <option value="">Any employment type</option><option value="full_time">Full-time</option><option value="internship">Internship</option><option value="contract">Contract</option>
          </select>
          <input type="number" min="0" value={minSalary} onChange={(event) => setMinSalary(event.target.value)} placeholder="Minimum salary" aria-label="Minimum salary" className="border border-black bg-background px-3 py-2 text-sm" />
          <input type="number" min="0" value={maxSalary} onChange={(event) => setMaxSalary(event.target.value)} placeholder="Maximum salary" aria-label="Maximum salary" className="border border-black bg-background px-3 py-2 text-sm" />
          <input type="number" min="0" value={minExperience} onChange={(event) => setMinExperience(event.target.value)} placeholder="Minimum years" aria-label="Minimum experience" className="border border-black bg-background px-3 py-2 text-sm" />
          <input type="number" min="0" value={maxExperience} onChange={(event) => setMaxExperience(event.target.value)} placeholder="Maximum years" aria-label="Maximum experience" className="border border-black bg-background px-3 py-2 text-sm" />
          <select value={sortBy} onChange={(event) => { setSortBy(event.target.value); setOffset(0); }} aria-label="Sort jobs" className="border border-black bg-background px-3 py-2 text-sm">
            <option value="match_score">Best match</option><option value="salary">Salary</option><option value="posted_at">Newest</option><option value="title">Title</option>
          </select>
          <select value={sortOrder} onChange={(event) => { setSortOrder(event.target.value); setOffset(0); }} aria-label="Sort order" className="border border-black bg-background px-3 py-2 text-sm">
            <option value="desc">Descending</option><option value="asc">Ascending</option>
          </select>
          <button type="submit" className="border border-black bg-blue-700 px-3 py-2 font-mono text-xs font-bold uppercase text-white">Apply filters</button>
        </form>

        {loading ? (
          <Card>
            <CardContent className="min-h-48 p-8 text-sm font-mono uppercase tracking-wider text-ink-soft">
              Loading recommendations…
            </CardContent>
          </Card>
        ) : error ? (
          <Card>
            <CardContent className="min-h-48 p-8 text-sm text-red-700">{error}</CardContent>
          </Card>
        ) : jobs.length === 0 ? (
          <Card>
            <CardContent className="min-h-48 p-8">
              <p className="font-mono text-sm uppercase tracking-wider text-ink-soft">
                No jobs found
              </p>
              <p className="mt-2 text-sm text-black">
                Discover sample jobs to populate your CareerPilot feed.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {jobs.map((job) => (
              <Card
                key={job.id}
                variant="interactive"
                className="h-full border border-black bg-white shadow-sw-md"
              >
                <CardHeader>
                  <p className="font-mono text-[10px] font-bold uppercase tracking-wider text-blue-700">
                    {job.provider ?? 'demo'} · {job.employment_type ?? 'full-time'}
                  </p>
                  <CardTitle className="text-2xl">{job.title}</CardTitle>
                  <CardDescription>{job.company}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2 text-sm text-ink-soft">
                    <p>
                      <span className="font-mono text-[10px] uppercase tracking-wider text-ink-soft">
                        Location:
                      </span>{' '}
                      {job.location ?? 'Remote'}
                    </p>
                    <p>
                      <span className="font-mono text-[10px] uppercase tracking-wider text-ink-soft">
                        Mode:
                      </span>{' '}
                      {job.work_mode ?? 'remote'}
                    </p>
                  </div>
                  <p className="line-clamp-4 text-sm text-black">{job.description}</p>
                  <div className="flex flex-wrap gap-2">
                    {(job.skills_required ?? []).slice(0, 4).map((skill) => (
                      <span
                        key={`${job.id}-${skill}`}
                        className="border border-black bg-background px-2 py-1 font-mono text-[10px] uppercase tracking-wider text-ink"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                  <div className="flex items-center justify-between pt-2">
                    <span className="font-mono text-[10px] uppercase tracking-wider text-ink-soft">
                      {job.location ?? 'Remote'}
                    </span>
                    <Link
                      href={`/careerpilot/jobs/${encodeURIComponent(job.id)}`}
                      className="inline-flex items-center border border-black bg-blue-700 px-3 py-2 font-mono text-[10px] font-bold uppercase tracking-wider text-white shadow-sw-sm transition hover:translate-y-[1px] hover:translate-x-[1px] hover:shadow-none"
                    >
                      Analyze
                    </Link>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
        {!loading && !error && total > pageSize ? (
          <div className="mt-6 flex items-center justify-between border-t border-black pt-4">
            <button type="button" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - pageSize))} className="border border-black bg-background px-3 py-2 font-mono text-xs uppercase disabled:opacity-40">Previous</button>
            <span className="font-mono text-xs uppercase">Showing {offset + 1}-{Math.min(offset + pageSize, total)} of {total}</span>
            <button type="button" disabled={offset + pageSize >= total} onClick={() => setOffset(offset + pageSize)} className="border border-black bg-background px-3 py-2 font-mono text-xs uppercase disabled:opacity-40">Next</button>
          </div>
        ) : null}
      </div>
    </main>
  );
}

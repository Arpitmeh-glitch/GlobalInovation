'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import Loader2 from 'lucide-react/dist/esm/icons/loader-2';
import {
  fetchCareerPilotJob,
  fetchCareerPilotMatch,
  type CareerPilotJob,
  type CareerPilotMatchResult,
} from '@/lib/api/careerpilot';

export default function JobAnalysisPage() {
  const params = useParams<{ id: string }>();
  const [job, setJob] = useState<CareerPilotJob | null>(null);
  const [match, setMatch] = useState<CareerPilotMatchResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [preparing, setPreparing] = useState(false);

  useEffect(() => {
    const jobId = params?.id;
    if (!jobId) return;
    let active = true;

    async function load() {
      try {
        const [jobData, matchData] = await Promise.all([
          fetchCareerPilotJob(jobId),
          fetchCareerPilotMatch(jobId),
        ]);
        if (!active) return;
        setJob(jobData);
        setMatch(matchData);
      } catch (err) {
        if (!active) return;
        setError(err instanceof Error ? err.message : 'Unable to load job analysis.');
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();
    return () => {
      active = false;
    };
  }, [params?.id]);

  async function handlePrepare() {
    if (!params?.id) return;
    setPreparing(true);
    setError(null);
    try {
      window.location.assign(`/careerpilot/applications/${encodeURIComponent(params.id)}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to prepare application.');
      setPreparing(false);
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-background p-4 md:p-8">
        <div className="mx-auto max-w-5xl rounded-none border border-black bg-white p-6 shadow-sw-md">
          <p className="font-mono text-xs uppercase tracking-wider text-blue-700">
            Loading analysis…
          </p>
        </div>
      </main>
    );
  }

  if (error || !job) {
    return (
      <main className="min-h-screen bg-background p-4 md:p-8">
        <div className="mx-auto max-w-5xl border border-black bg-white p-6 shadow-sw-md">
          <p className="font-mono text-xs uppercase tracking-wider text-red-700">
            Job analysis unavailable
          </p>
          <p className="mt-2 text-sm text-black">
            {error ?? 'This role is unavailable in demo mode.'}
          </p>
          {error?.includes('No resume available') || error?.includes('Multiple resumes') ? (
            <Link
              href="/dashboard"
              className="mt-4 inline-flex border border-black bg-blue-700 px-3 py-2 font-mono text-[10px] uppercase tracking-wider text-white hover:translate-y-[1px] hover:translate-x-[1px] hover:shadow-sw-sm"
            >
              Upload or select a resume
            </Link>
          ) : null}
          <Link
            href="/careerpilot/jobs"
            className="ml-3 mt-4 inline-flex border border-black bg-background px-3 py-2 font-mono text-[10px] uppercase tracking-wider text-black hover:translate-y-[1px] hover:translate-x-[1px] hover:shadow-sw-sm"
          >
            Back to jobs
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background p-4 md:p-8">
      <div className="mx-auto max-w-5xl space-y-6">
        <div className="flex flex-col gap-4 border border-black bg-white p-4 shadow-sw-md md:flex-row md:items-center md:justify-between">
          <div>
            <p className="font-mono text-xs font-bold uppercase tracking-wider text-blue-700">
              Demo Mode — Sample Job Data
            </p>
            <h1 className="mt-2 font-serif text-4xl font-semibold text-ink">{job.title}</h1>
            <p className="mt-1 font-mono text-xs uppercase tracking-wider text-ink-soft">
              {job.company}
            </p>
          </div>
          <div className="flex gap-3">
            <Link
              href="/careerpilot/jobs"
              className="inline-flex border border-black bg-background px-3 py-2 font-mono text-[10px] uppercase tracking-wider text-black hover:translate-y-[1px] hover:translate-x-[1px] hover:shadow-sw-sm"
            >
              Back to jobs
            </Link>
            <Button
              variant="default"
              size="sm"
              onClick={() => void handlePrepare()}
              disabled={preparing}
            >
              {preparing ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              {preparing ? 'Preparing...' : 'Prepare Application'}
            </Button>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1.5fr_1fr]">
          <Card className="border border-black bg-white shadow-sw-md">
            <CardHeader>
              <CardTitle>Job overview</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-black">
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="border border-black bg-background p-3">
                  <p className="font-mono uppercase tracking-wider text-ink-soft">Location</p>
                  <p className="mt-2 text-sm font-medium">{job.location ?? 'Remote'}</p>
                </div>
                <div className="border border-black bg-background p-3">
                  <p className="font-mono uppercase tracking-wider text-ink-soft">Work mode</p>
                  <p className="mt-2 text-sm font-medium">{job.work_mode ?? 'remote'}</p>
                </div>
                <div className="border border-black bg-background p-3">
                  <p className="font-mono uppercase tracking-wider text-ink-soft">Type</p>
                  <p className="mt-2 text-sm font-medium">{job.employment_type ?? 'full-time'}</p>
                </div>
                <div className="border border-black bg-background p-3">
                  <p className="font-mono uppercase tracking-wider text-ink-soft">Experience</p>
                  <p className="mt-2 text-sm font-medium">{job.experience_required ?? 'Not specified'}</p>
                </div>
                <div className="border border-black bg-background p-3">
                  <p className="font-mono uppercase tracking-wider text-ink-soft">Salary</p>
                  <p className="mt-2 text-sm font-medium">
                    {job.salary_min
                      ? `₹${job.salary_min.toLocaleString()} - ₹${job.salary_max?.toLocaleString() ?? job.salary_min.toLocaleString()}`
                      : 'Not listed'}
                  </p>
                </div>
              </div>
              <div>
                <p className="font-mono text-[10px] uppercase tracking-wider text-ink-soft">
                  Description
                </p>
                <p className="mt-2 leading-relaxed">{job.description}</p>
              </div>
              <div>
                <p className="font-mono text-[10px] uppercase tracking-wider text-ink-soft">
                  Required skills
                </p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {(job.skills_required ?? []).map((skill) => (
                    <span
                      key={skill}
                      className="border border-black bg-background px-2 py-1 font-mono text-[10px] uppercase tracking-wider text-black"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
              {job.skills_preferred?.length ? (
                <div>
                  <p className="font-mono text-[10px] uppercase tracking-wider text-ink-soft">Preferred skills</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {job.skills_preferred.map((skill) => (
                      <span key={skill} className="border border-black bg-background px-2 py-1 font-mono text-[10px] uppercase tracking-wider text-black">{skill}</span>
                    ))}
                  </div>
                </div>
              ) : null}
              {job.application_url ? <a href={job.application_url} target="_blank" rel="noreferrer" className="inline-flex border border-black bg-background px-3 py-2 font-mono text-[10px] font-bold uppercase tracking-wider shadow-sw-sm">Open provider listing</a> : null}
              <p className="font-mono text-[10px] uppercase tracking-wider text-ink-soft">Source: {job.provider ?? 'Unavailable'}</p>
              {job.qualifications?.length ? <div><p className="font-mono text-[10px] uppercase tracking-wider text-ink-soft">Qualifications</p><ul className="mt-2 list-disc space-y-1 pl-5 text-sm">{job.qualifications.map((qualification) => <li key={qualification}>{qualification}</li>)}</ul></div> : null}
              {job.hard_requirements?.length ? <div><p className="font-mono text-[10px] uppercase tracking-wider text-ink-soft">Required conditions</p><ul className="mt-2 list-disc space-y-1 pl-5 text-sm">{job.hard_requirements.map((requirement) => <li key={requirement}>{requirement}</li>)}</ul></div> : null}
            </CardContent>
          </Card>

          <Card className="border border-black bg-white shadow-sw-md">
            <CardHeader>
              <CardTitle>Compatibility</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border border-black bg-blue-700 p-4 text-white">
                <p className="font-mono text-[10px] uppercase tracking-wider text-blue-100">
                  Overall score
                </p>
                <p className="mt-2 text-4xl font-serif font-semibold">
                  {match?.overall_score ?? 0}%
                </p>
                <p className="mt-3 font-mono text-[10px] uppercase tracking-wider">
                  {match?.recommendation ?? 'Review pending'}
                </p>
              </div>
              <div className="space-y-2">
                <div className="border border-black bg-background p-3">
                  <p className="font-mono text-[10px] uppercase tracking-wider text-ink-soft">Experience match</p>
                  <p className="mt-1 text-sm">{match?.experience_match == null ? 'Not specified' : match.experience_match ? 'Meets available experience evidence' : 'Does not meet available experience evidence'}</p>
                </div>
                <div className="border border-black bg-background p-3">
                  <p className="font-mono text-[10px] uppercase tracking-wider text-ink-soft">Education match</p>
                  <p className="mt-1 text-sm">{match?.education_match == null ? 'No education requirement detected' : match.education_match ? 'Supported by education evidence' : 'Education evidence is missing'}</p>
                </div>
                <div className="border border-black bg-background p-3">
                  <p className="font-mono text-[10px] uppercase tracking-wider text-ink-soft">Matching skills</p>
                  <p className="mt-1 text-sm">{match?.matched_requirements?.join(', ') || 'No direct matches recorded'}</p>
                </div>
                <div className="border border-black bg-background p-3">
                  <p className="font-mono text-[10px] uppercase tracking-wider text-ink-soft">Missing skills</p>
                  <p className="mt-1 text-sm">{match?.missing_requirements?.join(', ') || 'No missing requirements recorded'}</p>
                </div>
                {match?.evidence?.slice(0, 8).map((item) => (
                  <div
                    key={`${item.requirement}-${item.source}`}
                    className="border border-black bg-background p-3"
                  >
                    <p className="font-mono text-[10px] uppercase tracking-wider text-ink-soft">
                      {item.requirement}
                    </p>
                    <p className="mt-1 text-sm text-black">
                      {item.status === 'supported'
                        ? 'Supported by resume evidence'
                        : 'No clear evidence in the current profile'}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}

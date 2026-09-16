'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import Loader2 from 'lucide-react/dist/esm/icons/loader-2';
import { discoverCareerPilotJobs, fetchCareerPilotJobs, fetchCareerPilotProfile, type CareerPilotJob, type CareerPilotProfile } from '@/lib/api/careerpilot';

function JobCard({ job }: { job: CareerPilotJob }) {
  return <article className="border border-black bg-white p-5 shadow-sw-sm">
    <div className="flex items-start justify-between gap-3"><div><p className="font-mono text-[10px] uppercase text-blue-700">{job.company}</p><h3 className="mt-1 font-serif text-2xl font-semibold">{job.title}</h3></div>{job.match && <strong className="border border-black bg-blue-700 px-2 py-1 font-mono text-xs text-white">{job.match.overall_score}%</strong>}</div>
    <p className="mt-3 text-sm text-ink-soft">{job.location ?? 'Location not listed'} · {job.work_mode ?? 'Flexible'}</p>
    <div className="mt-4 flex flex-wrap gap-2">{(job.match?.matched_requirements ?? job.skills_required ?? []).slice(0, 3).map((skill) => <span key={skill} className="border border-black bg-background px-2 py-1 font-mono text-[10px] uppercase">{skill}</span>)}</div>
    {job.match?.missing_requirements?.length ? <p className="mt-3 text-xs text-ink-soft">Missing: {job.match.missing_requirements.slice(0, 2).join(', ')}</p> : null}
    <Link href={`/careerpilot/jobs/${encodeURIComponent(job.id)}`} className="mt-5 inline-flex border border-black bg-background px-3 py-2 font-mono text-[10px] font-bold uppercase shadow-sw-sm">View match analysis</Link>
  </article>;
}

export default function CareerPilotDashboardPage() {
  const [profile, setProfile] = useState<CareerPilotProfile | null>(null);
  const [jobs, setJobs] = useState<CareerPilotJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void Promise.all([fetchCareerPilotProfile(), fetchCareerPilotJobs()]).then(async ([savedProfile, savedJobs]) => {
      const recommendations = savedJobs.length ? savedJobs : await discoverCareerPilotJobs();
      setProfile(savedProfile);
      setJobs(recommendations.slice(0, 6));
    }).catch((err) => setError(err instanceof Error ? err.message : 'Unable to load CareerPilot.')).finally(() => setLoading(false));
  }, []);

  if (loading) return <main className="min-h-screen bg-background p-8"><Loader2 className="h-5 w-5 animate-spin" /></main>;

  return <main className="min-h-screen bg-background p-4 md:p-8"><div className="mx-auto max-w-6xl">
    <header className="flex flex-col gap-5 border border-black bg-white p-6 shadow-sw-md md:flex-row md:items-end md:justify-between"><div><p className="font-mono text-xs font-bold uppercase tracking-wider text-blue-700">CareerPilot</p><h1 className="mt-2 font-serif text-5xl font-semibold">Your next move, organized.</h1><p className="mt-3 max-w-xl text-sm text-ink-soft">Profile-aware recommendations, evidence-backed matching, and user-controlled applications.</p></div><div className="flex flex-wrap gap-2"><Link href="/careerpilot/onboarding" className="border border-black bg-background px-3 py-2 font-mono text-[10px] font-bold uppercase">{profile ? 'Edit profile' : 'Complete profile'}</Link><Link href="/careerpilot/applications" className="border border-black bg-blue-700 px-3 py-2 font-mono text-[10px] font-bold uppercase text-white">Applications</Link></div></header>
    {error ? <div role="alert" className="mt-6 border border-red-700 bg-red-50 p-4 text-sm text-red-700">{error}</div> : null}
    {!profile ? <section className="mt-6 border border-black bg-white p-6"><h2 className="font-serif text-2xl font-semibold">Start with your career profile</h2><p className="mt-2 text-sm text-ink-soft">Add your target role and skills to make the demo job feed personal.</p><Link href="/careerpilot/onboarding" className="mt-4 inline-flex border border-black bg-blue-700 px-4 py-2 font-mono text-xs font-bold uppercase text-white">Set up profile</Link></section> : <section className="mt-6 border border-black bg-white p-6"><div className="flex flex-wrap items-start justify-between gap-4"><div><p className="font-mono text-[10px] uppercase text-blue-700">Profile summary</p><h2 className="mt-1 font-serif text-3xl font-semibold">{profile.target_role}</h2><p className="mt-2 text-sm text-ink-soft">{profile.experience_level} · {profile.work_preference} · {profile.preferred_locations.join(', ') || 'Any location'}</p></div><Link href="/careerpilot/onboarding" className="font-mono text-xs uppercase text-blue-700">Edit profile</Link></div><div className="mt-4 flex flex-wrap gap-2">{profile.skills.slice(0, 8).map((skill) => <span key={skill} className="border border-black bg-background px-2 py-1 font-mono text-[10px] uppercase">{skill}</span>)}</div></section>}
    <div className="mt-8 flex items-end justify-between"><div><p className="font-mono text-xs uppercase text-blue-700">Recommended for you</p><h2 className="mt-1 font-serif text-3xl font-semibold">Strongest openings</h2></div><Link href="/careerpilot/jobs" className="font-mono text-xs uppercase text-blue-700">View all jobs</Link></div>
    {jobs.length ? <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">{jobs.map((job) => <JobCard key={job.id} job={job} />)}</div> : <div className="mt-4 border border-black bg-white p-6 text-sm text-ink-soft">No recommendations yet. <Link href="/careerpilot/jobs" className="text-blue-700 underline">Discover jobs</Link>.</div>}
    <div className="mt-8 grid gap-4 md:grid-cols-3"><Link href="/careerpilot/jobs" className="border border-black bg-white p-5 shadow-sw-sm"><p className="font-mono text-xs uppercase text-blue-700">01</p><h3 className="mt-2 font-serif text-xl font-semibold">Discover jobs</h3></Link><Link href="/careerpilot/onboarding" className="border border-black bg-white p-5 shadow-sw-sm"><p className="font-mono text-xs uppercase text-blue-700">02</p><h3 className="mt-2 font-serif text-xl font-semibold">Tune your profile</h3></Link><Link href="/careerpilot/applications" className="border border-black bg-white p-5 shadow-sw-sm"><p className="font-mono text-xs uppercase text-blue-700">03</p><h3 className="mt-2 font-serif text-xl font-semibold">Track applications</h3></Link></div>
  </div></main>;
}

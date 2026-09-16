'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import Loader2 from 'lucide-react/dist/esm/icons/loader-2';
import { Button } from '@/components/ui/button';
import { DemoBanner } from '@/components/careerpilot/DemoBanner';
import { fetchResumeList, type ResumeListItem } from '@/lib/api/resume';
import { fetchCareerPilotJobsPage, type CareerPilotJob } from '@/lib/api/careerpilot';
import { simulateSkillImpact, type SimulationResponse } from '@/lib/api/careerpilot-intelligence';

export default function SimulatorPage() {
  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [jobs, setJobs] = useState<CareerPilotJob[]>([]);
  const [resumeId, setResumeId] = useState('');
  const [selectedJobs, setSelectedJobs] = useState<string[]>([]);
  const [skills, setSkills] = useState('');
  const [experience, setExperience] = useState('');
  const [education, setEducation] = useState('');
  const [result, setResult] = useState<SimulationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void Promise.all([fetchResumeList(true), fetchCareerPilotJobsPage({ limit: 50, sort_by: 'match_score' })])
      .then(([resumeData, jobData]) => {
        const readyResumes = resumeData.filter((resume) => resume.processing_status === 'ready');
        setResumes(readyResumes);
        setResumeId(readyResumes.find((resume) => resume.is_master)?.resume_id ?? readyResumes[0]?.resume_id ?? '');
        setJobs(jobData.jobs);
        setSelectedJobs(jobData.jobs.slice(0, 3).map((job) => job.id));
      })
      .catch((caught) => setError(caught instanceof Error ? caught.message : 'Unable to load simulator data.'))
      .finally(() => setLoading(false));
  }, []);

  function toggleJob(jobId: string) {
    setSelectedJobs((current) => current.includes(jobId) ? current.filter((id) => id !== jobId) : [...current, jobId]);
  }

  async function runSimulation(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const hypotheticalSkills = skills.split(',').map((skill) => skill.trim()).filter(Boolean);
    if (!resumeId || selectedJobs.length === 0 || (hypotheticalSkills.length === 0 && !experience.trim() && !education.trim())) {
      setError('Choose a resume, at least one job, and one hypothetical addition.');
      return;
    }
    setSimulating(true);
    setError(null);
    try {
      setResult(await simulateSkillImpact({
        resume_id: resumeId,
        job_ids: selectedJobs,
        hypothetical_skills: hypotheticalSkills,
        hypothetical_experience: experience.trim() || null,
        hypothetical_education: education.trim() || null,
      }));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to run simulation.');
    } finally {
      setSimulating(false);
    }
  }

  return (
    <main className="min-h-screen bg-background">
      <DemoBanner />
      <div className="mx-auto max-w-7xl p-4 md:p-8">
        <Link href="/careerpilot" className="font-mono text-xs uppercase text-blue-700">Back to CareerPilot</Link>
        <header className="mt-4 border border-black bg-white p-6 shadow-sw-md"><p className="font-mono text-xs font-bold uppercase tracking-wider text-blue-700">Career intelligence</p><h1 className="mt-2 font-serif text-4xl font-semibold">What-if simulator</h1><p className="mt-2 text-sm text-ink-soft">Explore possible improvements without saving anything to your profile or applications.</p></header>
        <div className="mt-6 border-2 border-red-700 bg-red-50 p-4 font-mono text-xs font-bold uppercase tracking-wider text-red-900">HYPOTHETICAL SIMULATION - Does not alter candidate profile or application records</div>
        {error && <div role="alert" className="mt-6 border border-red-700 bg-red-50 p-4 text-sm text-red-700">{error}</div>}
        {loading ? <div className="mt-8 flex items-center gap-2 font-mono text-xs uppercase"><Loader2 className="animate-spin" />Loading simulator...</div> : <form onSubmit={runSimulation} className="mt-6 grid gap-6 lg:grid-cols-[20rem_1fr]">
          <section className="border border-black bg-white p-5"><h2 className="font-serif text-2xl font-semibold">Hypothetical additions</h2><label className="mt-5 block font-mono text-xs font-bold uppercase">Source resume<select value={resumeId} onChange={(event) => setResumeId(event.target.value)} className="mt-2 h-10 w-full border border-black bg-background px-2 font-sans text-sm"><option value="">Select a ready resume</option>{resumes.map((resume) => <option key={resume.resume_id} value={resume.resume_id}>{resume.title || resume.filename || resume.resume_id}</option>)}</select></label><label className="mt-4 block font-mono text-xs font-bold uppercase">Skills<input value={skills} onChange={(event) => setSkills(event.target.value)} placeholder="AWS, Terraform" className="mt-2 h-10 w-full border border-black bg-background px-3 font-sans text-sm" /></label><label className="mt-4 block font-mono text-xs font-bold uppercase">Experience<input value={experience} onChange={(event) => setExperience(event.target.value)} placeholder="2 years cloud security" className="mt-2 h-10 w-full border border-black bg-background px-3 font-sans text-sm" /></label><label className="mt-4 block font-mono text-xs font-bold uppercase">Education or certification<input value={education} onChange={(event) => setEducation(event.target.value)} placeholder="AWS certification" className="mt-2 h-10 w-full border border-black bg-background px-3 font-sans text-sm" /></label><Button type="submit" className="mt-6 w-full" disabled={simulating || !resumes.length}>{simulating && <Loader2 className="animate-spin" />}{simulating ? 'Running simulation...' : 'Run hypothetical simulation'}</Button></section>
          <section className="border border-black bg-white p-5"><div className="flex items-end justify-between gap-3"><div><h2 className="font-serif text-2xl font-semibold">Jobs to compare</h2><p className="mt-1 text-sm text-ink-soft">Select one or more provider jobs.</p></div><span className="font-mono text-xs uppercase">{selectedJobs.length} selected</span></div><div className="mt-4 grid gap-2 md:grid-cols-2">{jobs.map((job) => <label key={job.id} className="flex cursor-pointer items-start gap-3 border border-black bg-background p-3"><input type="checkbox" checked={selectedJobs.includes(job.id)} onChange={() => toggleJob(job.id)} className="mt-1" /><span><span className="block font-serif text-lg font-semibold">{job.title}</span><span className="block text-xs text-ink-soft">{job.company} · {job.location ?? 'Location not listed'}</span></span></label>)}</div></section>
        </form>}
        {result && <section className="mt-8 border border-black bg-white p-5 shadow-sw-md"><div className="grid gap-3 md:grid-cols-2"><div className="border border-black bg-background p-4"><p className="font-mono text-xs uppercase text-ink-soft">Baseline average</p><p className="mt-2 font-serif text-3xl font-semibold">{result.original_summary.average_score}%</p></div><div className="border border-black bg-blue-700 p-4 text-white"><p className="font-mono text-xs uppercase text-blue-100">Simulated average</p><p className="mt-2 font-serif text-3xl font-semibold">{result.simulated_summary.average_score}% <span className="font-mono text-sm">({result.simulated_summary.average_score_delta >= 0 ? '+' : ''}{result.simulated_summary.average_score_delta})</span></p></div></div><div className="mt-6 overflow-x-auto"><table className="w-full min-w-[760px] border-collapse text-left text-sm"><thead><tr className="border-b-2 border-black font-mono text-xs uppercase"><th className="p-3">Job</th><th className="p-3">Baseline</th><th className="p-3">Simulated</th><th className="p-3">Delta</th><th className="p-3">New matches</th></tr></thead><tbody>{result.comparisons.map((comparison) => <tr key={comparison.job_id} className="border-b border-black"><td className="p-3 font-semibold">{comparison.job_title}</td><td className="p-3">{comparison.baseline_score}%<span className="block text-xs text-ink-soft">Missing: {comparison.baseline_missing_skills.join(', ') || 'None'}</span></td><td className="p-3">{comparison.simulated_score}%<span className="block text-xs text-ink-soft">Missing: {comparison.simulated_missing_skills.join(', ') || 'None'}</span></td><td className="p-3 font-mono font-bold text-green-800">{comparison.score_delta >= 0 ? '+' : ''}{comparison.score_delta}</td><td className="p-3">{comparison.simulated_matched_skills.filter((skill) => !comparison.baseline_matched_skills.includes(skill)).join(', ') || 'None'}</td></tr>)}</tbody></table></div></section>}
      </div>
    </main>
  );
}

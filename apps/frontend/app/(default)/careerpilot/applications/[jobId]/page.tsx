'use client';

import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import Loader2 from 'lucide-react/dist/esm/icons/loader-2';
import { fetchResumeList, type ResumeListItem } from '@/lib/api/resume';
import { fetchCareerPilotJob, type CareerPilotJob } from '@/lib/api/careerpilot';
import { prepareCareerPilotApplication } from '@/lib/api/careerpilot-applications';

function resumeLabel(resume: ResumeListItem): string {
  return resume.title || resume.filename || resume.resume_id;
}

export default function CareerPilotApplicationPreparationPage() {
  const params = useParams<{ jobId: string }>();
  const router = useRouter();
  const [job, setJob] = useState<CareerPilotJob | null>(null);
  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [resumeId, setResumeId] = useState('');
  const [loading, setLoading] = useState(true);
  const [preparing, setPreparing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const jobId = params?.jobId;
    if (!jobId) return;
    void Promise.all([fetchCareerPilotJob(jobId), fetchResumeList(true)])
      .then(([jobData, resumeData]) => {
        setJob(jobData);
        setResumes(resumeData);
        setResumeId(resumeData.find((resume) => resume.is_master)?.resume_id || resumeData[0]?.resume_id || '');
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Unable to load preparation details.'))
      .finally(() => setLoading(false));
  }, [params?.jobId]);

  async function prepare() {
    if (!params?.jobId || !resumeId) {
      setError('Select a ready resume before preparing this application.');
      return;
    }
    setPreparing(true);
    setError(null);
    try {
      const application = await prepareCareerPilotApplication(params.jobId, resumeId);
      router.push(`/careerpilot/applications/${application.application_id}/review`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to prepare application.');
      setPreparing(false);
    }
  }

  if (loading) return <main className="min-h-screen bg-background p-8"><Loader2 className="h-5 w-5 animate-spin" /></main>;

  return (
    <main className="min-h-screen bg-background p-4 md:p-8">
      <div className="mx-auto max-w-3xl">
        <Link href={`/careerpilot/jobs/${encodeURIComponent(params?.jobId ?? '')}`} className="font-mono text-xs uppercase text-blue-700">Back to job</Link>
        <section className="mt-4 border border-black bg-white p-6 shadow-sw-md md:p-10">
          <p className="font-mono text-xs font-bold uppercase tracking-wider text-blue-700">Application preparation</p>
          <h1 className="mt-2 font-serif text-4xl font-semibold">Prepare your materials</h1>
          {job && <p className="mt-3 text-sm text-ink-soft">{job.title} at {job.company}</p>}
          <p className="mt-6 text-sm text-ink-soft">Choose the source resume. CareerPilot will create a reviewable tailored draft and will never submit it automatically.</p>
          <label className="mt-6 block font-mono text-xs font-bold uppercase tracking-wider">
            Resume
            <select value={resumeId} onChange={(event) => setResumeId(event.target.value)} className="mt-2 block w-full border border-black bg-white px-3 py-3 text-sm" disabled={!resumes.length}>
              {!resumes.length && <option value="">No resumes available</option>}
              {resumes.map((resume) => <option key={resume.resume_id} value={resume.resume_id}>{resumeLabel(resume)}{resume.is_master ? ' (master)' : ''}</option>)}
            </select>
          </label>
          {error && <p role="alert" className="mt-5 border border-red-700 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
          <button type="button" onClick={() => void prepare()} disabled={preparing || !resumeId} className="mt-6 inline-flex items-center gap-2 border border-black bg-blue-700 px-5 py-3 font-mono text-xs font-bold uppercase tracking-wider text-white shadow-sw-sm disabled:opacity-60">
            {preparing && <Loader2 className="h-4 w-4 animate-spin" />}
            {preparing ? 'Preparing application...' : 'Create reviewable draft'}
          </button>
        </section>
      </div>
    </main>
  );
}

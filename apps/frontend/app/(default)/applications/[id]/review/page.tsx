'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import AlertTriangle from 'lucide-react/dist/esm/icons/alert-triangle';
import CheckCircle2 from 'lucide-react/dist/esm/icons/check-circle-2';
import Loader2 from 'lucide-react/dist/esm/icons/loader-2';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  approveCareerPilotApplication,
  fetchCareerPilotApplicationReview,
  regenerateCareerPilotCoverLetter,
  rejectCareerPilotApplication,
  updateCareerPilotCoverLetter,
  updateCareerPilotScreening,
  type CareerPilotApplication,
} from '@/lib/api/careerpilot-applications';

export default function CareerPilotApplicationReviewPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [application, setApplication] = useState<CareerPilotApplication | null>(null);
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [coverLetter, setCoverLetter] = useState('');
  const [answers, setAnswers] = useState<Record<string, string | number | boolean>>({});
  const [savingCoverLetter, setSavingCoverLetter] = useState(false);

  useEffect(() => {
    const applicationId = params?.id;
    if (!applicationId) return;
    let active = true;
    void fetchCareerPilotApplicationReview(applicationId)
      .then((data) => {
        if (!active) return;
        setApplication(data);
        setCoverLetter(data.cover_letter ?? '');
        setAnswers(
          Object.fromEntries(
            data.screening_questions
              .filter((question) => question.answer !== null && question.answer !== undefined)
              .map((question) => [
                question.question_id,
                question.answer as string | number | boolean,
              ])
          )
        );
      })
      .catch((err) => {
        if (active)
          setError(err instanceof Error ? err.message : 'Unable to load application review.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [params?.id]);

  async function saveAnswer(questionId: string, value: string) {
    if (!application) return;
    const nextAnswers = { ...answers, [questionId]: value };
    setAnswers(nextAnswers);
    try {
      setApplication(await updateCareerPilotScreening(application.application_id, nextAnswers));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to save screening answer.');
    }
  }

  async function approve() {
    if (!application) return;
    setWorking(true);
    setError(null);
    try {
      await approveCareerPilotApplication(application.application_id);
      router.push('/careerpilot/applications');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to approve application.');
      setWorking(false);
    }
  }

  async function reject() {
    if (!application) return;
    setWorking(true);
    try {
      await rejectCareerPilotApplication(application.application_id);
      router.push('/careerpilot/applications');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to reject application.');
      setWorking(false);
    }
  }

  async function saveCoverLetter() {
    if (!application) return;
    setSavingCoverLetter(true);
    try {
      setApplication(await updateCareerPilotCoverLetter(application.application_id, coverLetter));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to save cover letter.');
    } finally {
      setSavingCoverLetter(false);
    }
  }

  async function regenerateCoverLetter() {
    if (!application) return;
    setSavingCoverLetter(true);
    setError(null);
    try {
      const updated = await regenerateCareerPilotCoverLetter(application.application_id);
      setApplication(updated);
      setCoverLetter(updated.cover_letter ?? '');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to regenerate cover letter.');
    } finally {
      setSavingCoverLetter(false);
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-background p-4 md:p-8">
        <div className="mx-auto flex max-w-5xl items-center gap-2 border border-black bg-white p-8 shadow-sw-md">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span className="font-mono text-xs uppercase tracking-wider">
            Loading application review...
          </span>
        </div>
      </main>
    );
  }

  if (!application) {
    return (
      <main className="min-h-screen bg-background p-4 md:p-8">
        <div className="mx-auto max-w-5xl border border-black bg-white p-8 shadow-sw-md">
          <p className="font-mono text-xs uppercase tracking-wider text-red-700">
            Application unavailable
          </p>
          <p className="mt-2 text-sm">{error ?? 'This application draft may have been deleted.'}</p>
          <Link
            href="/careerpilot/jobs"
            className="mt-4 inline-flex border border-black bg-background px-3 py-2 font-mono text-xs uppercase tracking-wider shadow-sw-sm"
          >
            Back to jobs
          </Link>
        </div>
      </main>
    );
  }

  const unsupported = application.claim_validation.unsupported_claims ?? [];
  const missingAnswers = application.screening_questions.filter(
    (question) =>
      question.status === 'USER_INPUT_REQUIRED' &&
      !String(question.answer ?? answers[question.question_id] ?? '').trim()
  );
  const approvalBlocked = application.needs_review || missingAnswers.length > 0;

  return (
    <main className="min-h-screen bg-background p-4 md:p-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="border border-black bg-white p-5 shadow-sw-md">
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="font-mono text-xs font-bold uppercase tracking-wider text-blue-700">
                {application.demo_mode ? 'DEMO MODE — SAMPLE JOB DATA' : 'APPLICATION REVIEW'}
              </p>
              <h1 className="mt-2 font-serif text-4xl font-semibold">Application Review</h1>
              <p className="mt-2 font-mono text-xs uppercase tracking-wider text-ink-soft">
                {application.role ?? 'Role'} · {application.company ?? 'Company'} · Match{' '}
                {application.match.overall_score ?? 0}%
              </p>
            </div>
            <Link
              href="/careerpilot/applications"
              className="border border-black bg-background px-3 py-2 font-mono text-xs uppercase tracking-wider shadow-sw-sm"
            >
              Open tracker
            </Link>
          </div>
        </header>

        {error ? (
          <div className="border border-red-700 bg-red-50 p-3 text-sm text-red-700">{error}</div>
        ) : null}

        <Card className="border border-black bg-white shadow-sw-md">
          <CardHeader>
            <CardTitle>Submission control</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p>CareerPilot prepares materials only. Final submission happens on the external job site.</p>
            <p className="font-mono text-xs uppercase text-ink-soft">Source resume: {application.original_resume_id} · Provider: {application.provider ?? 'Unavailable'}</p>
            {application.application_url ? <a href={application.application_url} target="_blank" rel="noreferrer" className="inline-flex border border-black bg-blue-700 px-3 py-2 font-mono text-xs font-bold uppercase text-white shadow-sw-sm">Open external application</a> : <p className="text-ink-soft">No external application URL was supplied by this provider.</p>}
          </CardContent>
        </Card>

        <Card className="border border-black bg-white shadow-sw-md">
          <CardHeader>
            <CardTitle>Tailored Resume</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-3">
              <Link
                href={`/builder?id=${application.original_resume_id}`}
                className="border border-black bg-background px-3 py-2 font-mono text-xs uppercase tracking-wider shadow-sw-sm"
              >
                View Original
              </Link>
              <Link
                href={`/builder?id=${application.tailored_resume_id}`}
                className="border border-black bg-blue-700 px-3 py-2 font-mono text-xs uppercase tracking-wider text-white shadow-sw-sm"
              >
                View Tailored
              </Link>
            </div>
            <div className="border border-black bg-background p-4">
              <p className="font-mono text-xs font-bold uppercase tracking-wider">Changes Made</p>
              {application.changes.length ? (
                application.changes.map((change) => (
                  <div
                    key={`${change.section}-${change.type}-${change.reason}`}
                    className="mt-3 grid gap-1 text-sm md:grid-cols-[1fr_2fr]"
                  >
                    <span className="font-mono text-xs uppercase text-blue-700">
                      {change.section}
                    </span>
                    <span>
                      {change.after}
                      <span className="block text-xs text-ink-soft">{change.reason}</span>
                    </span>
                  </div>
                ))
              ) : (
                <p className="mt-3 text-sm text-ink-soft">No structural changes were recorded.</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="border border-black bg-white shadow-sw-md">
          <CardHeader>
            <CardTitle>Evidence Check</CardTitle>
          </CardHeader>
          <CardContent>
            {application.needs_review ? (
              <div className="border border-orange-700 bg-orange-50 p-4 text-sm text-orange-900">
                <div className="flex items-center gap-2 font-mono text-xs font-bold uppercase">
                  <AlertTriangle className="h-4 w-4" /> Claims require review
                </div>
                <ul className="mt-3 list-disc pl-5">
                  {unsupported.map((claim) => (
                    <li key={`${claim.claim_type}-${claim.claim}`}>
                      {claim.claim} ({claim.claim_type})
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-sm text-green-800">
                <CheckCircle2 className="h-4 w-4" />{' '}
                {application.claim_validation.verified_claim_count ?? 0} claims verified, 0
                unsupported claims
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="border border-black bg-white shadow-sw-md">
          <CardHeader>
            <CardTitle>Cover Letter</CardTitle>
          </CardHeader>
          <CardContent>
            <textarea
              value={coverLetter}
              onChange={(event) => setCoverLetter(event.target.value)}
              className="min-h-40 w-full border border-black bg-background p-3 text-sm"
              placeholder="No cover letter generated."
            />
            <div className="mt-3 flex items-center justify-between gap-3">
              <p className="font-mono text-[10px] uppercase tracking-wider text-ink-soft">
                Generated from verified resume evidence.
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => void saveCoverLetter()}
                disabled={savingCoverLetter}
              >
                {savingCoverLetter ? 'Saving...' : 'Save'}
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => void regenerateCoverLetter()}
                disabled={savingCoverLetter}
              >
                {savingCoverLetter ? 'Regenerating...' : 'Regenerate'}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-black bg-white shadow-sw-md">
          <CardHeader>
            <CardTitle>Application Timeline</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {application.events.map((event) => (
              <div
                key={`${event.event}-${event.timestamp}`}
                className="border-l-2 border-blue-700 pl-3"
              >
                <p className="font-mono text-xs font-bold uppercase tracking-wider">
                  {event.event.replaceAll('_', ' ')}
                </p>
                <p className="text-xs text-ink-soft">
                  {new Date(event.timestamp).toLocaleString()}
                </p>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="border border-black bg-white shadow-sw-md">
          <CardHeader>
            <CardTitle>Screening Questions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {application.screening_questions.length ? (
              application.screening_questions.map((question) => (
                <div key={question.question_id} className="border border-black bg-background p-4">
                  <p className="text-sm font-medium">{question.question}</p>
                  <p className="mt-2 font-mono text-[10px] uppercase tracking-wider text-ink-soft">
                    {question.status === 'AUTO_FILLED_FROM_VERIFIED_DATA'
                      ? `AUTO-FILLED FROM VERIFIED DATA${question.evidence ? ` · ${question.evidence}` : ''}`
                      : 'USER INPUT REQUIRED'}
                  </p>
                  <input
                    value={String(
                      answers[question.question_id] ??
                        question.answer ??
                        question.suggested_answer ??
                        ''
                    )}
                    onChange={(event) => void saveAnswer(question.question_id, event.target.value)}
                    className="mt-3 w-full border border-black bg-white px-3 py-2 text-sm"
                    placeholder="Enter an answer"
                  />
                </div>
              ))
            ) : (
              <p className="text-sm text-ink-soft">
                No screening questions were supplied by this provider.
              </p>
            )}
          </CardContent>
        </Card>

        <div className="flex flex-wrap justify-between gap-3 border-t border-black pt-5">
          <Button variant="destructive" onClick={() => void reject()} disabled={working}>
            Reject Draft
          </Button>
          <div className="flex gap-3">
            <Link
              href={`/builder?id=${application.tailored_resume_id}`}
              className="inline-flex items-center border border-black bg-background px-4 py-2 font-mono text-xs uppercase tracking-wider shadow-sw-sm"
            >
              Edit
            </Link>
            <Button
              variant="success"
              onClick={() => void approve()}
              disabled={working || approvalBlocked}
            >
              {working ? 'Working...' : 'Approve Application'}
            </Button>
          </div>
        </div>
        {approvalBlocked ? (
          <p className="text-right font-mono text-xs uppercase tracking-wider text-orange-800">
            Resolve evidence review and required screening answers before approval.
          </p>
        ) : null}
      </div>
    </main>
  );
}

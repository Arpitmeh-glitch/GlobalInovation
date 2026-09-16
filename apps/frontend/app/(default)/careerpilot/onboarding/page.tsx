'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Loader2 from 'lucide-react/dist/esm/icons/loader-2';
import { fetchCareerPilotProfile, saveCareerPilotProfile, type CareerPilotProfile } from '@/lib/api/careerpilot';

const initialProfile: CareerPilotProfile = {
  target_role: '',
  skills: [],
  experience_level: 'entry',
  years_experience: null,
  education: '',
  preferred_locations: [],
  work_preference: 'remote',
  industries: [],
  salary_expectation: null,
};

const inputClass = 'w-full border border-black bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-700';

export default function CareerPilotOnboardingPage() {
  const router = useRouter();
  const [profile, setProfile] = useState<CareerPilotProfile>(initialProfile);
  const [skills, setSkills] = useState('');
  const [locations, setLocations] = useState('');
  const [industries, setIndustries] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void fetchCareerPilotProfile()
      .then((saved) => {
        if (!saved) return;
        setProfile(saved);
        setSkills(saved.skills.join(', '));
        setLocations(saved.preferred_locations.join(', '));
        setIndustries(saved.industries.join(', '));
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Unable to load profile.'))
      .finally(() => setLoading(false));
  }, []);

  function update(field: keyof CareerPilotProfile, value: string | number | null) {
    setProfile((current) => ({ ...current, [field]: value }));
  }

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!profile.target_role.trim()) {
      setError('Target role is required.');
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await saveCareerPilotProfile({
        ...profile,
        target_role: profile.target_role.trim(),
        skills: skills.split(',').map((item) => item.trim()).filter(Boolean),
        preferred_locations: locations.split(',').map((item) => item.trim()).filter(Boolean),
        industries: industries.split(',').map((item) => item.trim()).filter(Boolean),
      });
      router.push('/careerpilot');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to save profile.');
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <main className="min-h-screen bg-background p-8"><p className="font-mono text-xs uppercase">Loading CareerPilot profile...</p></main>;
  }

  return (
    <main className="min-h-screen bg-background p-4 md:p-8">
      <div className="mx-auto max-w-3xl">
        <Link href="/careerpilot" className="font-mono text-xs uppercase text-blue-700">Back to CareerPilot</Link>
        <div className="mt-4 border border-black bg-white p-6 shadow-sw-md md:p-10">
          <p className="font-mono text-xs font-bold uppercase tracking-wider text-blue-700">Career profile</p>
          <h1 className="mt-2 font-serif text-4xl font-semibold text-ink">Tell CareerPilot where you want to go.</h1>
          <p className="mt-3 text-sm text-ink-soft">This profile powers the recommendation scores. You can update it any time.</p>
          <form onSubmit={submit} className="mt-8 space-y-6">
            <label className="block text-sm font-medium">Target role<input required className={`${inputClass} mt-2`} value={profile.target_role} onChange={(event) => update('target_role', event.target.value)} placeholder="e.g. Security Analyst" /></label>
            <label className="block text-sm font-medium">Skills<span className="mt-1 block text-xs text-ink-soft">Comma-separated</span><input className={`${inputClass} mt-2`} value={skills} onChange={(event) => setSkills(event.target.value)} placeholder="Python, Linux, AWS" /></label>
            <div className="grid gap-4 md:grid-cols-2">
              <label className="block text-sm font-medium">Experience level<select className={`${inputClass} mt-2`} value={profile.experience_level} onChange={(event) => update('experience_level', event.target.value)}><option value="entry">Entry level</option><option value="mid">Mid level</option><option value="senior">Senior</option><option value="student">Student</option></select></label>
              <label className="block text-sm font-medium">Years of experience<input type="number" min="0" max="70" className={`${inputClass} mt-2`} value={profile.years_experience ?? ''} onChange={(event) => update('years_experience', event.target.value ? Number(event.target.value) : null)} /></label>
            </div>
            <label className="block text-sm font-medium">Education<input className={`${inputClass} mt-2`} value={profile.education ?? ''} onChange={(event) => update('education', event.target.value)} placeholder="e.g. B.Tech Computer Science" /></label>
            <label className="block text-sm font-medium">Preferred locations<input className={`${inputClass} mt-2`} value={locations} onChange={(event) => setLocations(event.target.value)} placeholder="Remote, Bengaluru" /></label>
            <div className="grid gap-4 md:grid-cols-2">
              <label className="block text-sm font-medium">Work preference<select className={`${inputClass} mt-2`} value={profile.work_preference} onChange={(event) => update('work_preference', event.target.value)}><option value="remote">Remote</option><option value="hybrid">Hybrid</option><option value="onsite">On-site</option></select></label>
              <label className="block text-sm font-medium">Salary expectation<input type="number" min="0" className={`${inputClass} mt-2`} value={profile.salary_expectation ?? ''} onChange={(event) => update('salary_expectation', event.target.value ? Number(event.target.value) : null)} /></label>
            </div>
            <label className="block text-sm font-medium">Industries<input className={`${inputClass} mt-2`} value={industries} onChange={(event) => setIndustries(event.target.value)} placeholder="Cybersecurity, SaaS" /></label>
            {error && <p role="alert" className="border border-red-700 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
            <button type="submit" disabled={saving} className="inline-flex items-center gap-2 border border-black bg-blue-700 px-5 py-3 font-mono text-xs font-bold uppercase tracking-wider text-white shadow-sw-sm disabled:opacity-60">{saving && <Loader2 className="h-4 w-4 animate-spin" />}{saving ? 'Saving profile...' : 'Save and continue'}</button>
          </form>
        </div>
      </div>
    </main>
  );
}

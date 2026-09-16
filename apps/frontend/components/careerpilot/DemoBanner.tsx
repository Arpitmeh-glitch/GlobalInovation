'use client';

import { useEffect, useState } from 'react';
import RotateCcw from 'lucide-react/dist/esm/icons/rotate-ccw';
import Loader2 from 'lucide-react/dist/esm/icons/loader-2';
import { Button } from '@/components/ui/button';
import { fetchDemoStatus, resetDemoState } from '@/lib/api/careerpilot-demo';

export function DemoBanner() {
  const [scenario, setScenario] = useState('default');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    void fetchDemoStatus()
      .then((payload) => setScenario(payload.status.demo_scenario))
      .catch(() => setMessage('Demo status is unavailable.'));
  }, []);

  async function reset() {
    setBusy(true);
    setMessage(null);
    try {
      await resetDemoState(scenario);
      setMessage('Demo state reset.');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Unable to reset demo state.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="border-b border-black bg-[#FFF9DB] px-4 py-3">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3">
        <p className="font-mono text-xs font-bold uppercase tracking-wider text-ink">
          Demo mode · scenario: {scenario}
        </p>
        <div className="flex items-center gap-3">
          {message && <span className="text-xs text-ink-soft" role="status">{message}</span>}
          <Button variant="outline" size="sm" onClick={() => void reset()} disabled={busy}>
            {busy ? <Loader2 className="animate-spin" /> : <RotateCcw />}
            Reset Demo State
          </Button>
        </div>
      </div>
    </div>
  );
}

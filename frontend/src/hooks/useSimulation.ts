/* useSimulation - AEGISFLOW frontend useSimulation for dashboard data management. */

import { useState, useCallback } from 'react';

type Action = 'kill' | 'restore' | 'deploy' | 'scale';

export function useSimulation() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  const execute = useCallback(async (action: Action, target: string, severity?: string) => {
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch('http://localhost:8000/api/v1/simulate/failure', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, target, severity, delay: 0 }),
      });
      const data = await res.json();
      setResult(data.success ? `Done: ${target}` : `Error: ${data.error}`);
    } catch {
      setResult('Network error');
    } finally {
      setLoading(false);
    }
  }, []);

  return { execute, loading, result };
}

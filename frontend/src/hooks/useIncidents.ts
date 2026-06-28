/* useIncidents - AEGISFLOW frontend useIncidents for dashboard data management. */

import { useState, useEffect, useCallback } from 'react';
import type { Incident } from '@/types';

export function useIncidents() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchIncidents = useCallback(async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/incidents');
      if (res.ok) {
        setIncidents(await res.json());
      }
    } catch {
      // silent fail
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchIncidents(); }, [fetchIncidents]);

  return { incidents, loading, refetch: fetchIncidents };
}

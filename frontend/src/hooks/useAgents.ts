/* useAgents - AEGISFLOW frontend useAgents for dashboard data management. */

import { useState, useEffect, useCallback } from 'react';
import type { AgentInfo } from '@/types';

export function useAgents() {
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAgents = useCallback(async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/agents');
      if (res.ok) {
        setAgents(await res.json());
      }
    } catch {
      // silent fail
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAgents(); }, [fetchAgents]);

  return { agents, loading, refetch: fetchAgents };
}

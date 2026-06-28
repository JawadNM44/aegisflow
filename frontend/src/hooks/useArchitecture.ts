/* useArchitecture - AEGISFLOW frontend useArchitecture for dashboard data management. */

import { useState, useEffect } from 'react';
import type { C4Architecture } from '@/types';

export function useArchitecture() {
  const [arch, setArch] = useState<C4Architecture | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/architecture')
      .then(r => r.json())
      .then(setArch)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return { architecture: arch, loading };
}

/** Application constants for the AEGISFLOW dashboard. */

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

export const NODE_COLORS: Record<string, string> = {
  database: '#6366f1',
  service: '#22c55e',
  api: '#f59e0b',
  load_balancer: '#3b82f6',
  queue: '#a855f7',
  storage: '#06b6d4',
  ci_cd: '#ec4899',
  component: '#64748b',
  container_group: '#14b8a6',
};

export const SEVERITY_LABELS: Record<string, string> = {
  sev1: 'CRITICAL',
  sev2: 'HIGH',
  sev3: 'MEDIUM',
  sev4: 'LOW',
};

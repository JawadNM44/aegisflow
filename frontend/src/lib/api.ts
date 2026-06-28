const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function fetchAPI(path: string, options?: RequestInit) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  get: (path: string) => fetchAPI(path),
  getArchitecture: () => fetchAPI('/architecture'),
  getIncidents: (limit = 20) => fetchAPI(`/incidents?limit=${limit}`),
  getIncident: (id: string) => fetchAPI(`/incidents/${id}`),
  getEvents: (limit = 50) => fetchAPI(`/events?limit=${limit}`),
  getAgents: () => fetchAPI('/agents'),
  getAgent: (name: string) => fetchAPI(`/agents/${name}`),

  simulateFailure: (target: string, severity = 'critical') =>
    fetchAPI('/simulate/failure', {
      method: 'POST',
      body: JSON.stringify({ action: 'kill', target, severity, delay: 0 }),
    }),

  simulateRestore: (target: string) =>
    fetchAPI(`/simulate/restore?target=${encodeURIComponent(target)}`, { method: 'POST' }),

  simulateDeployment: (target: string) =>
    fetchAPI(`/simulate/deployment?target=${encodeURIComponent(target)}`, { method: 'POST' }),

  simulateScaling: (target: string, replicas = 3) =>
    fetchAPI(`/simulate/scaling?target=${encodeURIComponent(target)}&replicas=${replicas}`, { method: 'POST' }),

  getHealth: () => fetchAPI('/health'),

  analyzeDiagram: (image: string, prompt?: string) =>
    fetchAPI('/analyze/diagram', {
      method: 'POST',
      body: JSON.stringify({ image, prompt: prompt || 'Analyze this infrastructure architecture diagram. Identify potential issues, single points of failure, bottlenecks, and optimization opportunities.' }),
    }),
};

/* SimulationControls component - AEGISFLOW dashboard UI for infrastructure observability. */

import React, { useState, useCallback } from 'react';
import { Zap, Skull, RefreshCw, Rocket, Gauge, Loader } from 'lucide-react';
import { api } from '@/lib/api';

const targets = [
  { id: 'db-1', name: 'PostgreSQL' },
  { id: 'cache-1', name: 'Redis Cache' },
  { id: 'api-1', name: 'API Server' },
  { id: 'queue-1', name: 'Message Queue' },
  { id: 'auth-1', name: 'Auth Service' },
];

export default function SimulationControls() {
  const [loading, setLoading] = useState<string | null>(null);
  const [log, setLog] = useState<string[]>([]);

  const addLog = (msg: string) => setLog(prev => [msg, ...prev].slice(0, 20));

  const runAction = useCallback(async (action: string, target: string, name: string) => {
    const key = `${action}-${target}`;
    setLoading(key);
    addLog(`Running ${action} on ${name}...`);
    try {
      if (action === 'kill') {
        const res = await api.simulateFailure(target);
        addLog(res.success ? `Injected ${name} failure — cascading impact detected` : `Failed: ${res.error}`);
      } else if (action === 'restore') {
        const res = await api.simulateRestore(target);
        addLog(res.success ? `${name} restored to healthy` : `Failed: ${res.error}`);
      } else if (action === 'deploy') {
        const res = await api.simulateDeployment(target);
        addLog(res.success ? `${name} deployment triggered` : `Failed: ${res.error}`);
      } else if (action === 'scale') {
        const res = await api.simulateScaling(target, 5);
        addLog(res.success ? `${name} scaled to 5 replicas` : `Failed: ${res.error}`);
      }
    } catch (e: any) {
      addLog(`Error: ${e.message}`);
    }
    setLoading(null);
  }, []);

  const isBusy = (target: string) => loading?.endsWith(target) || false;

  return (
    <div className="flex flex-col h-full">
      <div className="text-xs text-gray-500 mb-2 font-medium">Infrastructure Controls</div>
      <div className="flex-1 space-y-1.5 overflow-y-auto">
        {targets.map((t) => (
          <div key={t.id} className="bg-gray-800/30 rounded-lg p-2 border border-gray-800">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-sm font-medium text-white">{t.name}</span>
              {isBusy(t.id) && <Loader className="w-3 h-3 text-cyan-400 animate-spin" />}
            </div>
            <div className="flex gap-1">
              <button
                onClick={() => runAction('kill', t.id, t.name)}
                disabled={loading !== null}
                className="flex-1 flex items-center justify-center gap-1 px-2 py-1.5 text-xs rounded bg-red-500/20 text-red-400 hover:bg-red-500/30 border border-red-500/30 disabled:opacity-50 transition-colors"
              >
                <Skull className="w-3 h-3" /> Kill
              </button>
              <button
                onClick={() => runAction('restore', t.id, t.name)}
                disabled={loading !== null}
                className="flex-1 flex items-center justify-center gap-1 px-2 py-1.5 text-xs rounded bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 border border-emerald-500/30 disabled:opacity-50 transition-colors"
              >
                <RefreshCw className="w-3 h-3" /> Restore
              </button>
              <button
                onClick={() => runAction('deploy', t.id, t.name)}
                disabled={loading !== null}
                className="flex items-center justify-center px-2 py-1.5 text-xs rounded bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 border border-blue-500/30 disabled:opacity-50 transition-colors"
                title="Trigger deployment"
              >
                <Rocket className="w-3 h-3" />
              </button>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-2 bg-gray-900/50 rounded-lg border border-gray-800 p-2 max-h-[140px] overflow-y-auto">
        {log.length === 0 && (
          <div className="text-xs text-gray-500 text-center py-3">
            Click Kill to inject infrastructure failures
          </div>
        )}
        {log.map((msg, i) => (
          <div key={i} className="text-[11px] text-gray-400 font-mono leading-5">{msg}</div>
        ))}
      </div>
    </div>
  );
}

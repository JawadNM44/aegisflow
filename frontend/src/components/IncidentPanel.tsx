/* IncidentPanel component - AEGISFLOW dashboard UI for infrastructure observability. */

import React from 'react';
import { AlertTriangle, CheckCircle, Clock, UserCheck, Activity, Zap } from 'lucide-react';
import type { Incident } from '@/types';

const severityColors: Record<string, string> = {
  sev1: 'bg-red-500/20 text-red-400 border-red-500/30',
  sev2: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  sev3: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  sev4: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
};

const statusIcons: Record<string, React.ReactNode> = {
  open: <AlertTriangle className="w-4 h-4" />,
  investigating: <Activity className="w-4 h-4" />,
  mitigating: <UserCheck className="w-4 h-4" />,
  resolved: <CheckCircle className="w-4 h-4" />,
  closed: <Clock className="w-4 h-4" />,
};

interface Props {
  incidents: Incident[];
}

export default function IncidentPanel({ incidents }: Props) {
  if (incidents.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500 text-sm">
        <CheckCircle className="w-5 h-5 mr-2 text-emerald-400" />
        No incidents
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto space-y-2 pr-1">
      {incidents.map((inc) => (
        <div
          key={inc.id}
          className={`rounded-lg border p-3 ${
            inc.severity === 'sev1'
              ? 'border-red-500/30 bg-red-500/5'
              : inc.severity === 'sev2'
              ? 'border-orange-500/30 bg-orange-500/5'
              : 'border-gray-700 bg-gray-800/50'
          }`}
        >
          <div className="flex items-start gap-2">
            <div className={`shrink-0 px-2 py-0.5 rounded text-xs font-bold border ${severityColors[inc.severity] || ''}`}>
              {inc.severity?.toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-white truncate">{inc.title}</div>
              {inc.root_cause && (
                <div className="text-xs text-gray-400 mt-1 line-clamp-2">{inc.root_cause}</div>
              )}
              {inc.ai_analysis && (
                <div className="mt-2 space-y-1">
                  <div className="flex items-center gap-1.5 text-xs text-cyan-400">
                    <Zap className="w-3 h-3" />
                    <span>{(inc.ai_analysis.confidence * 100).toFixed(0)}% confidence</span>
                    {inc.ai_analysis.inference_time_ms && (
                      <span className="ml-1 px-1.5 py-0.5 rounded bg-indigo-900/40 text-indigo-300 text-[10px] font-semibold">
                        {inc.ai_analysis.inference_time_ms.toFixed(0)}ms
                      </span>
                    )}
                  </div>
                  {inc.ai_analysis.reasoning_trace && inc.ai_analysis.reasoning_trace.length > 0 && (
                    <div className="text-[10px] text-gray-500 leading-relaxed border-l border-gray-700 pl-2 mt-1 space-y-0.5">
                      {inc.ai_analysis.reasoning_trace.map((step, i) => (
                        <div key={i} className="hover:text-gray-300 transition-colors">{step}</div>
                      ))}
                    </div>
                  )}
                </div>
              )}
              {inc.remediation.length > 0 && (
                <div className="mt-2 space-y-1">
                  {inc.remediation.slice(0, 2).map((step) => (
                    <div key={step.order} className="flex items-center gap-1.5 text-xs text-gray-400">
                      <span className={`w-1.5 h-1.5 rounded-full ${step.automated ? 'bg-emerald-400' : 'bg-yellow-400'}`} />
                      {step.action}
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="shrink-0 text-gray-400">
              {statusIcons[inc.status] || null}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

/* AgentConsole component - AEGISFLOW dashboard UI for infrastructure observability. */

import React from 'react';
import { Bot, Activity, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import type { AgentInfo } from '@/types';

const statusConfig: Record<string, { icon: React.ReactNode; color: string }> = {
  idle: { icon: <CheckCircle className="w-3 h-3" />, color: 'text-gray-400' },
  working: { icon: <Loader className="w-3 h-3 animate-spin" />, color: 'text-blue-400' },
  error: { icon: <AlertCircle className="w-3 h-3" />, color: 'text-red-400' },
  disabled: { icon: <Activity className="w-3 h-3" />, color: 'text-gray-600' },
};

interface Props {
  agents: AgentInfo[];
}

export default function AgentConsole({ agents }: Props) {
  return (
    <div className="h-full overflow-y-auto space-y-2 pr-1">
      {agents.length === 0 && (
        <div className="text-center text-gray-500 text-sm py-8">No agents running</div>
      )}
      {agents.map((agent) => {
        const cfg = statusConfig[agent.status] || statusConfig.idle;
        return (
          <div key={agent.name} className="flex items-start gap-2 bg-gray-800/30 rounded-lg p-2 border border-gray-800">
            <Bot className="w-4 h-4 mt-0.5 text-gray-400 shrink-0" />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-white">{agent.name}</span>
                <span className={`flex items-center gap-1 text-xs ${cfg.color}`}>
                  {cfg.icon}
                  {agent.status}
                </span>
              </div>
              {agent.current_task && (
                <div className="text-xs text-gray-400 mt-0.5 truncate">{agent.current_task}</div>
              )}
              {agent.logs.length > 0 && (
                <div className="text-xs text-gray-500 mt-1 line-clamp-2">
                  {agent.logs[agent.logs.length - 1]?.message}
                </div>
              )}
            </div>
            {agent.error_count > 0 && (
              <span className="text-xs text-red-400">{agent.error_count} err</span>
            )}
          </div>
        );
      })}
    </div>
  );
}

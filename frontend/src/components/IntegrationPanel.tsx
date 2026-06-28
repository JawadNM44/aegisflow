import React from 'react';
import { Slack, Github, BookOpen } from 'lucide-react';

interface Integration {
  name: string;
  status: 'connected' | 'disconnected' | 'error' | 'simulated';
  icon: React.ReactNode;
}

interface Props {
  statuses?: Record<string, string>;
}

export default function IntegrationPanel({ statuses = {} }: Props) {
  const integrations: Integration[] = [
    { name: 'Slack', status: (statuses.slack as any) || 'simulated', icon: <Slack className="w-4 h-4" /> },
    { name: 'Jira', status: (statuses.jira as any) || 'simulated', icon: <BookOpen className="w-4 h-4" /> },
    { name: 'Notion', status: (statuses.notion as any) || 'simulated', icon: <BookOpen className="w-4 h-4" /> },
    { name: 'GitHub', status: 'simulated', icon: <Github className="w-4 h-4" /> },
  ];

  const statusColor = (s: string) => {
    switch (s) {
      case 'connected': return 'text-emerald-400 bg-emerald-500/10';
      case 'simulated': return 'text-yellow-400 bg-yellow-500/10';
      case 'error': return 'text-red-400 bg-red-500/10';
      default: return 'text-gray-500 bg-gray-800';
    }
  };

  return (
    <div className="space-y-2">
      {integrations.map((int) => (
        <div key={int.name} className="flex items-center gap-2 bg-gray-800/30 rounded-lg p-2 border border-gray-800">
          <div className="text-gray-400">{int.icon}</div>
          <span className="text-sm text-white flex-1">{int.name}</span>
          <span className={`text-xs px-2 py-0.5 rounded-full ${statusColor(int.status)}`}>
            {int.status}
          </span>
        </div>
      ))}
    </div>
  );
}

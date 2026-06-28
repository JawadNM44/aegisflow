/* StatusBadge component - AEGISFLOW dashboard UI for infrastructure observability. */

import React from 'react';

interface Props {
  status: string;
  size?: 'sm' | 'md' | 'lg';
}

const colors: Record<string, string> = {
  healthy: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  warning: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  critical: 'bg-red-500/20 text-red-400 border-red-500/30',
  healthy: 'bg-green-500/20 text-green-400 border-green-500/30',
  investigating: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  mitigating: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  resolved: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  closed: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
};

const sizeClasses = { sm: 'text-[10px] px-1.5 py-0.5', md: 'text-xs px-2 py-0.5', lg: 'text-sm px-3 py-1' };

export default function StatusBadge({ status, size = 'md' }: Props) {
  return (
    <span className={`inline-block rounded border font-medium ${colors[status] || 'bg-gray-500/20 text-gray-400 border-gray-500/30'} ${sizeClasses[size]}`}>
      {status.toUpperCase()}
    </span>
  );
}

/* LoadingSpinner component - AEGISFLOW dashboard UI for infrastructure observability. */

import React from 'react';

interface Props {
  size?: number;
  label?: string;
}

export default function LoadingSpinner({ size = 24, label = 'Loading...' }: Props) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-8">
      <svg className="animate-spin text-cyan-400" width={size} height={size} viewBox="0 0 24 24" fill="none">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      {label && <span className="text-xs text-gray-500">{label}</span>}
    </div>
  );
}

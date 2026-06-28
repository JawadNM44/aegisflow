/* EmptyState component - AEGISFLOW dashboard UI for infrastructure observability. */

import React from 'react';

interface Props {
  icon?: React.ReactNode;
  title: string;
  description?: string;
}

export default function EmptyState({ icon, title, description }: Props) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      {icon && <div className="mb-3 text-gray-600">{icon}</div>}
      <h3 className="text-sm font-medium text-gray-400">{title}</h3>
      {description && <p className="text-xs text-gray-600 mt-1 max-w-xs">{description}</p>}
    </div>
  );
}

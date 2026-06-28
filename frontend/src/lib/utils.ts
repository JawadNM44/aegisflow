/** Utility functions for the frontend dashboard. */

export function classNames(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ');
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

export function truncate(str: string, max: number): string {
  return str.length > max ? str.slice(0, max) + '...' : str;
}

export function severityColor(sev: string): string {
  const map: Record<string, string> = { sev1: 'red', sev2: 'orange', sev3: 'yellow', sev4: 'blue' };
  return map[sev] || 'gray';
}

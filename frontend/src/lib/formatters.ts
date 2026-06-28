/** Data formatting utilities for the dashboard UI. */
import type { GemmaAnalysis } from '@/types';

export function formatConfidence(analysis: GemmaAnalysis | null | undefined): string {
  if (!analysis || analysis.confidence == null) return 'N/A';
  return `${(analysis.confidence * 100).toFixed(0)}%`;
}

export function formatInferenceTime(analysis: GemmaAnalysis | null | undefined): string {
  if (!analysis || analysis.inference_time_ms == null) return 'N/A';
  if (analysis.inference_time_ms === 0) return 'simulated';
  return `${analysis.inference_time_ms.toFixed(0)}ms`;
}

export function formatHealthCount(healthy: number, total: number): string {
  return `${healthy}/${total} healthy`;
}

import { formatConfidence, formatInferenceTime } from '@/lib/formatters';

describe('formatConfidence', () => {
  it('returns formatted percentage', () => {
    expect(formatConfidence({ confidence: 0.85 } as any)).toBe('85%');
  });
  it('returns N/A for null', () => {
    expect(formatConfidence(null)).toBe('N/A');
  });
});

describe('formatInferenceTime', () => {
  it('returns ms for valid time', () => {
    expect(formatInferenceTime({ inference_time_ms: 743.3 } as any)).toBe('743ms');
  });
  it('returns simulated for 0', () => {
    expect(formatInferenceTime({ inference_time_ms: 0 } as any)).toBe('simulated');
  });
});

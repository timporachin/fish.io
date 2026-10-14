import { describe, expect, it } from 'vitest';
import { SWIM_DURATION, SWIM_FRAMES, swimOffset, swimPhase } from '../src/animation/swim';

describe('C2 swim loop', () => {
  it('wraps phase exactly over one loop', () => {
    expect(swimPhase(0)).toBeCloseTo(0, 12);
    expect(swimPhase(SWIM_FRAMES)).toBeCloseTo(0, 12);
    expect(swimPhase(SWIM_FRAMES * 3 + 7)).toBeCloseTo(swimPhase(7), 12);
  });

  it('grows amplitude toward the tail and matches first/last loop pose', () => {
    const head = Math.abs(swimOffset(1.1, 1));
    const tail = Math.abs(swimOffset(1.1, 0));
    expect(tail).toBeGreaterThan(head);
    for (const s of [0, 0.25, 0.5, 0.75, 1]) {
      expect(swimOffset(0, s)).toBeCloseTo(swimOffset(2 * Math.PI, s), 12);
    }
  });

  it('uses a 1 s 30-frame loop', () => {
    expect(SWIM_FRAMES).toBe(30);
    expect(SWIM_DURATION).toBeCloseTo(1, 12);
  });
});

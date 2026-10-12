import { describe, expect, it } from 'vitest';
import { createState, deserializeState, serializeState, stepState } from '../src/simulation';
import { FixedClock } from '../src/simulation/fixed-clock';

describe('deterministic aquarium simulation', () => {
  it('replays from a seed and resumes identically from a save', () => {
    let a = stepState(createState(9876), {type: 'buy-fish', species: 'clownfish'});
    let b = stepState(createState(9876), {type: 'buy-fish', species: 'clownfish'});
    for (let i = 0; i < 240; i++) { a = stepState(a); b = stepState(b); }
    expect(a).toEqual(b);
    let restored = deserializeState(serializeState(a));
    for (let i = 0; i < 120; i++) { a = stepState(a); restored = stepState(restored); }
    expect(restored).toEqual(a);
  });

  it('rejects unsupported versions, unknown fields, and broken fish references', () => {
    const valid = createState();
    expect(() => deserializeState(JSON.stringify({ ...valid, version: 99 }))).toThrow();
    expect(() => deserializeState(JSON.stringify({ ...valid, surprise: true }))).toThrow();
    const broken = structuredClone(valid);
    broken.habitats[0].fishIds[0] = 'missing-fish';
    expect(() => deserializeState(JSON.stringify(broken))).toThrow();
    const duplicateHabitats = structuredClone(valid);
    duplicateHabitats.habitats[1].id = duplicateHabitats.habitats[0].id;
    expect(() => deserializeState(JSON.stringify(duplicateHabitats))).toThrow();
  });

  it('rejects inherited species names without corrupting saves', () => {
    for (const species of ['constructor', '__proto__', 'toString']) {
      const result = stepState(createState(), {type: 'buy-fish', species});
      expect(result.fish).toHaveLength(0);
      expect(() => serializeState(result)).not.toThrow();
    }
  });

  it('keeps fish purchase and feeding within coin and habitat rules', () => {
    const starting = createState(4);
    expect(starting.fish).toHaveLength(0);
    expect(starting.progression.discoveries).toEqual([]);
    const bought = stepState(starting, { type: 'buy-fish', species: 'seahorse' });
    expect(bought.coins).toBe(15);
    expect(bought.fish).toHaveLength(1);
    const hungry = { ...bought, fish: bought.fish.map((f, i) => i === 0 ? { ...f, energy: 0.5 } : f) };
    const fed = stepState(hungry, { type: 'feed', fishId: bought.fish[0].id });
    expect(fed.coins).toBe(13);
    expect(fed.fish[0].energy).toBeGreaterThan(hungry.fish[0].energy);
  });
});

describe('FixedClock', () => {
  it('uses fixed ticks, caps catch-up and stops while paused', () => {
    const clock = new FixedClock({ tickSeconds: 0.1, maxCatchUpSteps: 3 });
    let count = 0;
    expect(clock.advance(0.25, () => count++)).toBe(2);
    expect(clock.advance(2, () => count++)).toBe(3);
    expect(count).toBe(5);
    clock.pause();
    expect(clock.advance(1, () => count++)).toBe(0);
    clock.resume();
    expect(clock.advance(0.1, () => count++)).toBe(1);
    expect(count).toBe(6);
    clock.reset();
    expect(clock.advance(0.05, () => count++)).toBe(0);
  });

  it('produces the same ticks for equivalent frame partitions', () => {
    const fine = new FixedClock();
    const coarse = new FixedClock();
    let fineState = createState(73);
    let coarseState = createState(73);
    for (let i = 0; i < 60; i++) fine.advance(1 / 60, () => { fineState = stepState(fineState); });
    for (let i = 0; i < 20; i++) coarse.advance(1 / 20, () => { coarseState = stepState(coarseState); });
    expect(fineState.tick).toBe(30);
    expect(coarseState.tick).toBe(30);
    expect(fineState).toEqual(coarseState);
  });
});

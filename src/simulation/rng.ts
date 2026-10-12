/** Mulberry32 step. State is stored explicitly so save/load resumes exactly. */
export function nextRandom(state: number): { value: number; state: number } {
  let t = (state + 0x6d2b79f5) >>> 0;
  let x = t;
  x = Math.imul(x ^ (x >>> 15), x | 1);
  x ^= x + Math.imul(x ^ (x >>> 7), x | 61);
  return { value: ((x ^ (x >>> 14)) >>> 0) / 4294967296, state: t >>> 0 };
}

export function randomInt(state: number, min: number, max: number): { value: number; state: number } {
  const result = nextRandom(state);
  return { value: min + Math.floor(result.value * (max - min + 1)), state: result.state };
}

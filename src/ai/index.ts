import { nextRandom } from '../simulation/rng';
import type { Fish, SimulationState } from '../simulation/types';

/** Tiny deterministic schooling policy: fish wander slowly and seek nearby food. */
export function updateFish(state: SimulationState): { fish: Fish[]; rngState: number } {
  let rngState = state.rngState;
  const fish = state.fish.map(f => {
    const r1 = nextRandom(rngState); rngState = r1.state;
    const r2 = nextRandom(rngState); rngState = r2.state;
    const angle = (r1.value - 0.5) * 0.24;
    const speed = 0.0008 + r2.value * 0.0008;
    return {
      ...f,
      x: Math.min(0.98, Math.max(0.02, f.x + Math.cos(angle) * speed)),
      y: Math.min(0.98, Math.max(0.02, f.y + Math.sin(angle) * speed)),
      age: f.age + 1 / 30,
      energy: Math.max(0, f.energy - 0.0006),
    };
  });
  return { fish, rngState };
}

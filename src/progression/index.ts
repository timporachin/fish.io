import { HABITAT_DEFINITIONS } from '../habitats';
import type { SimulationState } from '../simulation/types';

export function xpForNextLevel(level: number): number { return 20 + level * 15; }

/** Award XP and unlock milestones in a deterministic, idempotent pass. */
export function awardXp(state: SimulationState, amount: number): SimulationState {
  let level = state.progression.level;
  let xp = state.progression.xp + amount;
  while (xp >= xpForNextLevel(level)) { xp -= xpForNextLevel(level); level++; }
  const habitats = state.habitats.map(h => {
    const definition = HABITAT_DEFINITIONS.find(d => d.id === h.id)!;
    return { ...h, unlocked: h.unlocked || level >= definition.unlockLevel };
  });
  return {
    ...state,
    habitats,
    progression: { ...state.progression, level, xp },
    showroom: { ...state.showroom, unlocked: state.showroom.unlocked || level >= 2 },
  };
}

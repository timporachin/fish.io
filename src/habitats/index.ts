import type { Habitat, HabitatId, SimulationState } from '../simulation/types';

export const HABITAT_DEFINITIONS: ReadonlyArray<{ id: HabitatId; capacity: number; unlockLevel: number }> = [
  { id: 'coral-bay', capacity: 8, unlockLevel: 1 },
  { id: 'kelp-forest', capacity: 12, unlockLevel: 3 },
  { id: 'moonlit-reef', capacity: 16, unlockLevel: 6 },
];

export function makeHabitats(): Habitat[] {
  return HABITAT_DEFINITIONS.map((h, i) => ({ id: h.id, capacity: h.capacity, unlocked: i === 0, fishIds: [] }));
}

export function habitatForFish(state: SimulationState, fishId: string): Habitat | undefined {
  return state.habitats.find(h => h.fishIds.includes(fishId));
}

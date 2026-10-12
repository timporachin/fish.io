import type { SimulationState } from '../simulation/types';

export function showroomSummary(state: SimulationState) {
  return {
    unlocked: state.showroom.unlocked,
    visits: state.showroom.visits,
    featuredFish: state.fish.find(f => f.id === state.showroom.featuredFishId) ?? null,
    exhibitCount: state.progression.discoveries.length,
  };
}

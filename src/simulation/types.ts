export const STATE_VERSION = 1 as const;
export const TICK_RATE = 30;
export const TICK_SECONDS = 1 / TICK_RATE;

export type Fish = {
  id: string;
  species: string;
  x: number;
  y: number;
  age: number;
  energy: number;
};

export type HabitatId = 'coral-bay' | 'kelp-forest' | 'moonlit-reef';
export type Habitat = { id: HabitatId; unlocked: boolean; capacity: number; fishIds: string[] };

export type SimulationState = {
  version: typeof STATE_VERSION;
  seed: number;
  rngState: number;
  tick: number;
  coins: number;
  activeHabitat: HabitatId;
  fish: Fish[];
  habitats: Habitat[];
  progression: { level: number; xp: number; totalTicks: number; discoveries: string[] };
  showroom: { unlocked: boolean; featuredFishId: string | null; visits: number };
};

export type SimulationAction =
  | { type: 'feed'; fishId: string }
  | { type: 'buy-fish'; species: string }
  | { type: 'move-fish'; fishId: string; habitatId: HabitatId }
  | { type: 'select-habitat'; habitatId: HabitatId }
  | { type: 'feature-fish'; fishId: string | null }
  | { type: 'visit-showroom' };

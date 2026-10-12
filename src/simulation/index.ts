import { makeHabitats, habitatForFish } from '../habitats';
import { updateFish } from '../ai';
import { awardXp } from '../progression';
import { nextRandom } from './rng';
import { STATE_VERSION, TICK_SECONDS, type SimulationAction, type SimulationState } from './types';

export * from './types';
export { FixedClock } from './fixed-clock';

function makeFish(id: string, species: string, x: number, y: number) {
  return { id, species, x, y, age: 0, energy: 1 };
}

export function createState(seed = 1): SimulationState {
  if (!Number.isSafeInteger(seed)) throw new TypeError('seed must be a safe integer');
  const normalizedSeed = seed >>> 0;
  const habitats = makeHabitats();
  return {
    version: STATE_VERSION, seed: normalizedSeed, rngState: normalizedSeed || 0x6d2b79f5,
    tick: 0, coins: 60, activeHabitat: 'coral-bay', fish: [], habitats,
    progression: { level: 1, xp: 0, totalTicks: 0, discoveries: [] },
    showroom: { unlocked: false, featuredFishId: null, visits: 0 },
  };
}

const COSTS: Record<string, number> = { clownfish: 20, blue_tang: 30, seahorse: 45, jellyfish: 60 };
const clamp01 = (n: number) => Math.min(1, Math.max(0, n));

function applyAction(state: SimulationState, action: SimulationAction): SimulationState {
  switch (action.type) {
    case 'feed': {
      const fish = state.fish.find(f => f.id === action.fishId);
      if (!fish || state.coins < 2 || fish.energy >= 0.98) return state;
      return { ...state, coins: state.coins - 2, fish: state.fish.map(f => f.id === fish.id ? { ...f, energy: clamp01(f.energy + 0.3) } : f) };
    }
    case 'buy-fish': {
      const species = action.species.toLowerCase().replaceAll('-', '_');
      const cost = Object.hasOwn(COSTS, species) ? COSTS[species] : undefined;
      const habitat = state.habitats.find(h => h.id === state.activeHabitat);
      if (!cost || !habitat?.unlocked || state.coins < cost || habitat.fishIds.length >= habitat.capacity) return state;
      const id = `fish-${state.tick}-${state.fish.length + 1}`;
      const r1 = nextRandom(state.rngState), r2 = nextRandom(r1.state);
      const fish = makeFish(id, species.replaceAll('_', '-'), 0.15 + r1.value * 0.7, 0.15 + r2.value * 0.7);
      return { ...state, coins: state.coins - cost, rngState: r2.state,
        fish: [...state.fish, fish], habitats: state.habitats.map(h => h.id === habitat.id ? { ...h, fishIds: [...h.fishIds, id] } : h),
        progression: { ...state.progression, discoveries: state.progression.discoveries.includes(fish.species) ? state.progression.discoveries : [...state.progression.discoveries, fish.species] } };
    }
    case 'move-fish': {
      const from = habitatForFish(state, action.fishId), to = state.habitats.find(h => h.id === action.habitatId);
      if (!from || !to?.unlocked || from.id === to.id || to.fishIds.length >= to.capacity) return state;
      return { ...state, habitats: state.habitats.map(h => h.id === from.id ? { ...h, fishIds: h.fishIds.filter(id => id !== action.fishId) } : h.id === to.id ? { ...h, fishIds: [...h.fishIds, action.fishId] } : h) };
    }
    case 'select-habitat':
      return state.habitats.some(h => h.id === action.habitatId && h.unlocked) ? { ...state, activeHabitat: action.habitatId } : state;
    case 'feature-fish':
      if (!state.showroom.unlocked || (action.fishId !== null && !state.fish.some(f => f.id === action.fishId))) return state;
      return { ...state, showroom: { ...state.showroom, featuredFishId: action.fishId } };
    case 'visit-showroom':
      return state.showroom.unlocked ? { ...state, showroom: { ...state.showroom, visits: state.showroom.visits + 1 } } : state;
  }
}

/** Advance exactly one fixed simulation tick. Invalid game actions are ignored. */
export function stepState(previous: SimulationState, action?: SimulationAction): SimulationState {
  let state = action ? applyAction(previous, action) : previous;
  const updated = updateFish(state);
  state = { ...state, fish: updated.fish, rngState: updated.rngState, tick: state.tick + 1,
    coins: state.coins + (state.tick % 30 === 29 ? 1 : 0),
    progression: { ...state.progression, totalTicks: state.progression.totalTicks + 1 } };
  if (state.tick % 300 === 0) state = awardXp(state, 1);
  return state;
}

export function serializeState(state: SimulationState): string {
  assertState(state);
  return JSON.stringify(state);
}

/** Strict versioned save validation; rejects unknown fields and inconsistent references. */
export function deserializeState(serialized: string): SimulationState {
  let parsed: unknown;
  try { parsed = JSON.parse(serialized); } catch { throw new TypeError('save is not valid JSON'); }
  assertState(parsed);
  return parsed;
}

function record(value: unknown, keys: string[], name: string): asserts value is Record<string, any> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new TypeError(`${name} must be an object`);
  const actual = Object.keys(value);
  if (actual.length !== keys.length || keys.some(k => !actual.includes(k))) throw new TypeError(`${name} has invalid fields`);
}
function integer(n: unknown, min = 0): n is number { return Number.isSafeInteger(n) && (n as number) >= min; }
function assertState(value: unknown): asserts value is SimulationState {
  record(value, ['version','seed','rngState','tick','coins','activeHabitat','fish','habitats','progression','showroom'], 'state');
  const s = value as SimulationState;
  if (s.version !== STATE_VERSION || !integer(s.seed) || s.seed > 0xffffffff || !integer(s.rngState) || s.rngState > 0xffffffff || !integer(s.tick) || !integer(s.coins)) throw new TypeError('invalid state header');
  const ids = new Set<string>();
  if (!Array.isArray(s.fish)) throw new TypeError('fish must be an array');
  for (const f of s.fish) {
    record(f, ['id','species','x','y','age','energy'], 'fish');
    if (typeof f.id !== 'string' || !f.id || ids.has(f.id) || typeof f.species !== 'string' || !f.species || ![f.x,f.y,f.age,f.energy].every(Number.isFinite) || f.x < 0 || f.x > 1 || f.y < 0 || f.y > 1 || f.age < 0 || f.energy < 0 || f.energy > 1) throw new TypeError('invalid fish');
    ids.add(f.id);
  }
  if (!Array.isArray(s.habitats) || s.habitats.length !== 3) throw new TypeError('invalid habitats');
  const assigned = new Set<string>();
  const habitatIds = new Set<string>();
  for (const h of s.habitats) {
    record(h, ['id','unlocked','capacity','fishIds'], 'habitat');
    if (!['coral-bay','kelp-forest','moonlit-reef'].includes(h.id) || habitatIds.has(h.id) || typeof h.unlocked !== 'boolean' || !integer(h.capacity, 1) || !Array.isArray(h.fishIds) || h.fishIds.length > h.capacity) throw new TypeError('invalid habitat');
    habitatIds.add(h.id);
    for (const id of h.fishIds) { if (!ids.has(id) || assigned.has(id)) throw new TypeError('invalid habitat fish reference'); assigned.add(id); }
  }
  if (assigned.size !== ids.size || !s.habitats.some(h => h.id === s.activeHabitat && h.unlocked)) throw new TypeError('inconsistent habitat assignment');
  record(s.progression, ['level','xp','totalTicks','discoveries'], 'progression');
  if (!integer(s.progression.level, 1) || !integer(s.progression.xp) || !integer(s.progression.totalTicks) || s.progression.totalTicks !== s.tick || !Array.isArray(s.progression.discoveries) || s.progression.discoveries.some(x => typeof x !== 'string')) throw new TypeError('invalid progression');
  record(s.showroom, ['unlocked','featuredFishId','visits'], 'showroom');
  if (typeof s.showroom.unlocked !== 'boolean' || (s.showroom.featuredFishId !== null && !ids.has(s.showroom.featuredFishId)) || !integer(s.showroom.visits)) throw new TypeError('invalid showroom');
}

export const SIMULATION_TICK_SECONDS = TICK_SECONDS;

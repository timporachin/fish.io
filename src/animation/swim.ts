import * as THREE from 'three';

// Isolated C2 swim helpers. No gameplay scene changes; the C0 renderer is untouched.
// Pure functions are deterministic and unit-tested. The mixer wrapper only runs
// when a caller supplies a skinned GLB with a looping action (C2 review asset).

export const SWIM_FPS = 30;
export const SWIM_FRAMES = 30;
export const SWIM_DURATION = SWIM_FRAMES / SWIM_FPS; // 1.0 s loop

/** Traveling-wave lateral offset in metres for station s (0 tail .. 1 head). */
export function swimOffset(phase: number, station: number): number {
  const s = Math.min(1, Math.max(0, station));
  const smooth = s * s * (3 - 2 * s);
  const amp = 0.004 + 0.028 * (1 - smooth);
  return amp * Math.sin(phase - (1 - s) * 2.2);
}

/** Loop phase in radians for a tick at 30 Hz simulation. Wraps exactly. */
export function swimPhase(tick: number): number {
  const t = ((tick % SWIM_FRAMES) + SWIM_FRAMES) % SWIM_FRAMES;
  return (2 * Math.PI * t) / SWIM_FRAMES;
}

export function createSwimMixer(object: THREE.Object3D, clip: THREE.AnimationClip) {
  const mixer = new THREE.AnimationMixer(object);
  const action = mixer.clipAction(clip);
  action.setLoop(THREE.LoopRepeat, Infinity);
  action.play();
  return {
    mixer,
    action,
    update(dt: number) {
      mixer.update(dt);
    },
    dispose() {
      action.stop();
      mixer.stopAllAction();
      mixer.uncacheClip(clip);
    },
  };
}

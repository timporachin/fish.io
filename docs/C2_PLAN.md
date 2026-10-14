# C2 — animation development plan (started)

**Branch:** `dev/c2-animation` from `main@140c39e` (PR #2 merged; C0 + C1-approved supplied bass in history).
**Gate:** C1 visual approval granted 2026-10-12 for DigitalLife3D Model 67A static adaptation (personal, noncommercial CC BY-NC 4.0). C2 authorized by owner message `merge result + start C2`.

## Scope (from ROADMAP + BLENDER_PIPELINE)

1. Deform rig + weighting on the approved topology (nose +X, dorsal +Z, 0.45 m).
2. Baked swimming clip(s), loop-checked, exported as GLB with skin + active action.
3. Loop/deformation review (six-view + three-quarter, rest vs mid-stroke vs loop-end).
4. Only then: steering/feeding/progression refinement, interaction + save migrations.

Out of scope for this starter: gameplay control mapping, showroom changes, LODs/compression (C3), device matrix (C4).

## Rig spec (starter, within ARCHITECTURE budget <=24 deform bones)

- Armature `BassRig`: `root` + spine chain `spine.00..spine.07` (8) + `head` + `caudal.00..caudal.02` (3) = 13 deform bones. Fin chains deferred.
- Stable names, rest pose = C1 bind pose, origin at body center, meters.
- Weights: smooth by X station (`smooth01` falloff across neighboring spine bones), head rigid past hinge X, eyes excluded (no deform).
- Eyes/fin-ray combined meshes parented, not skinned, in this starter.

## Clip spec (starter)

- Action `SwimCruise`: 30 frames @30fps, 1.0 s loop, lateral Y sine traveling head→tail, amplitude growing to peduncle (e.g. `A(x)=0.004+0.028*smooth01((0.10-x)/0.30)`), yaw phase per bone.
- Bake: sampled keyframes on pose bones, linear→bezier, first frame duplicated at frame 31 for continuity check, then 30-frame export (first==last within 1e-5).
- Export: selected meshes + armature, `export_animations=True`, `export_force_sampling=True`, single active action, Khronos validator zero errors/warnings.

## This workspace limits

- `artifacts/c1/...` supplied source absent (ignored, not committed) and `blender` binary absent, so the headless bake cannot run here. `tools/blender/rig_swim.py` fails with a clear message when `--input` is missing and documents the exact command for a Blender 4.3.2 host.
- `src/animation/swim.ts` is isolated pure logic + an `AnimationMixer` wrapper; gameplay scene (`src/main.ts`, `src/rendering/underwater.ts`) unchanged. No production GLB committed.

## Run (Blender host)

```sh
blender --background --python-exit-code 1 --python tools/blender/rig_swim.py -- --input artifacts/c1/supplied-candidate/candidate-static.blend --output-dir artifacts/c2
npm ci --prefix tools/blender
npm run validate --prefix tools/blender -- ../../artifacts/c2/bass-swim.glb
```

## Verify (this workspace)

```sh
npm ci
npm run build
npm test
```

## Review gate

Rest + mid-stroke + loop-end renders, bone/weight table, validator report, Three.js `AnimationMixer` loop screenshot, owner visual approval before gameplay integration.

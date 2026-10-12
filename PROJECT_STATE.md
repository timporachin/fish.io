# FISH.IO project state

**C0 complete. Further C1 refinement in progress from saved work; visual acceptance pending. C2 not started.**

## Current C1 work

**C1 NOT ACCEPTED. Targeted anatomical reconstruction is in progress on `dev/c1-largemouth-bass`; draft [PR #2](https://github.com/timporachin/fish.io/pull/2) remains open and unmerged.** Main remains at `95f63b07575cece839f21c6d4dfd6fa9056ebf86` as checked against the remote. C0 application code is unchanged. C2 and Fish Factory are not authorized.

The owner’s completed feedback requires a fuller forebody tapering toward the tail and fins that blend into substantial roots. Those saved corrections are preserved. The current task reconstructs the upper/lower jaw, rounded lips, mouth corners, maxillary region and adjacent head only, using actual photographed largemouth bass. See [jaw references](docs/C1_JAW_REFERENCES.md) and [owner feedback](docs/C1_OWNER_FEEDBACK.md).

The immediately preceding asset is frozen under `artifacts/c1/anatomy-before/`. A first jaw reconstruction is preserved under `artifacts/c1/anatomical-revision/`, including seven 1600 × 1000 neutral views, matching baseline views and an additional matched three-quarter opening view. It passes the current export and limited articulation checks, but Astra identifies angular lip edges, a pointed posterior corner and a shelf-like mandibular rim. Another geometry correction is underway; these technical passes do not establish biological or visual acceptance. Source checkpoints and generated-asset hashes are retained in [the checkpoint manifest](docs/evidence/c1/jaw/checkpoints/manifest.json).

The original performance reference remains **10,976 triangles, 11 draw calls and five textures**. The saved later body/fin asset has 21,762 triangles; the first jaw pass retains that count, uses nine runtime draw calls and packs five embedded textures. **The higher triangle count is an unapproved proposal, not an adopted production budget.** Device profiling, LODs, compression and population performance remain unverified. The next revision’s measurements and visual review must be recorded after its assets are frozen.

Generated `.blend`, `.glb` and licensed reference photographs remain ignored local artifacts; selected review PNGs, reports, procedural scripts and documentation are committed. Earlier rejected evidence remains under `docs/evidence/c1/before/`, matching-light baseline under `before-matched-lighting/`, and first rework under `rework-1/`.

**Stop at the C1 visual gate.** Deliver the final revised asset, seven matching comparison views, photograph-based reference gallery, controlled jaw-opening evidence, geometry/runtime report and independent Astra review. C1 remains unaccepted until the user explicitly approves visual quality; any increased budget also requires explicit approval. No merge or next milestone is authorized.

## C0 delivery history (retained)


Fresh cloud project at `/workspace/fish.io`, based only on the initial repository README. Development branch: `dev/c0-cloud-foundation`; target: `main`.

## Delivered

Production-oriented Three.js/TypeScript/Vite bootstrap with exact direct pins, committed lockfiles, strict types, ignored generated outputs, and GitHub CI checks. Working underwater 3D scene with landscape-first layout, safe-area spacing, touch-size controls, pause/resume, empty species showroom, portrait guidance, reduced motion and WebGL recovery. Modular simulation, AI, progression, habitats, showroom and rendering boundaries. Seeded 30 Hz deterministic state, bounded timing and validated versioned JSON save APIs. No fish proxy geometry appears in the app.

Blender 4.3.2 was already installed; installation was unnecessary. Verified headless animated non-fish GLB export, structural inspection, pinned Khronos validation and corrupt-output rejection. Procedural/rigging/animation tooling evaluated; built-in Python/armatures/Geometry Nodes plus bundled glTF exporter are the chosen baseline. No GUI extensions installed. Realistic fish modeling and swimming-rig pipeline are documented, not executed.

## Exact versions

Node 24.19.0; npm 11.9.0; Three.js 0.180.0; TypeScript 5.9.3; Vite 7.3.7; Vitest 5.0.3; Playwright 1.56.1; @types/three 0.180.0; @types/node 24.7.2; gltf-validator 2.0.0-dev.3.10. Blender 4.3.2, Debian package 4.3.2+dfsg-2. Cloud browser Chromium 154.0.8037.57; CI uses Playwright's versioned Chromium instead.

## Verification and limitations

Build, six unit tests, two browser tests and GLB smoke validation pass. npm audit reports zero vulnerabilities. See [test evidence](docs/TEST_EVIDENCE.md) for actual commands, screenshot path and qualification. Lower-cost agents implemented bounded simulation/Blender tasks; Astra performed final review.

No iPhone hardware or Safari device testing occurred. Scene is a rendering foundation, not final photorealistic habitat art. No production fish assets, skinning proof, texture pipeline, persistent save UI, GLB browser import or release deployment. Mobile performance budgets are proposed, not achieved. Optional Blender Draco library is unavailable; uncompressed GLB works. CI is configured but not executed remotely. See [architecture](docs/ARCHITECTURE.md), [Blender plan](docs/BLENDER_PIPELINE.md) and [roadmap](docs/ROADMAP.md).

## Delivery

Implementation committed as `dfbdf44` and pushed to `dev/c0-cloud-foundation`. Draft [PR #1](https://github.com/timporachin/fish.io/pull/1) targets `main`. Working tree clean after delivery documentation commit. Stop after C0.

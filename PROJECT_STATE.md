# FISH.IO project state

**Milestone: C0 complete. C1 not started; explicit approval required.**

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

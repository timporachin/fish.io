# FISH.IO project state

**C0 complete. C1 modeling candidate delivered for review; visual acceptance pending. C2 not started.**

## Current C1 work

Authorized on 2026-10-12, based on `main` at `0ce0fc6143ea0b4827acd3d341f862a4c2e5090b`. Development branch: `dev/c1-largemouth-bass`. No changes to C0 gameplay, simulation, rendering or application tests. No merge is authorized.

Blender 4.3.2 Python generator authors a 0.455 m largemouth bass candidate, curved quad body with recessed mouth, a separate volumetric mandible and gill covers, embedded eye layers, separate spinous/soft dorsal, paired pectoral/pelvic, anal and caudal fins, and closed modeled rays. Seeded olive/broken-stripe scale textures, normal/roughness maps and olive/amber fin textures are generated and packed. The source has 24 anatomical mesh objects; a temporary joined export produces one GLB mesh with 11 material primitives. No rig, skin or clips are included.

Six 1200 × 800, 64-sample Cycles reference views and the actual Three.js browser screenshot are committed under `docs/evidence/c1/`. Generated Blender/GLB/texture artifacts remain in ignored `artifacts/c1/`, reproducible from the committed generator. See [modeling and render gallery](docs/C1_MODELING.md), [references](docs/C1_REFERENCES.md), [test evidence](docs/C1_TEST_EVIDENCE.md), and [Astra review](docs/C1_REVIEW.md).

Final checks pass: independent Blender geometry validation, pinned Khronos GLB validator (0 errors, 0 warnings), actual Three.js texture decoding/rendering, and corrupt/empty/animation/skin/geometry negative cases. Exported cost: 8,488 vertices, 10,976 triangles, 11 draw calls per fish, 2,585,016-byte GLB. Five embedded images: three 1024² and two 512². These checks establish technical validity; they do not establish production visual realism or user acceptance. The near-LOD 8k triangle proposal is exceeded; physical iPhone performance, LODs and deformation remain untested.

**Stop at the C1 visual gate.** The model must not be labeled visually accepted because automated checks pass. Consult the independent review for remaining artistic/anatomical issues; C2 animation work requires the user's approval and further instruction.

Draft [PR #2](https://github.com/timporachin/fish.io/pull/2) targets `main`; it remains a draft and is not merged. Main advanced during C1 to `95f63b0`, adding `docs/GAME_DESIGN.md`; that document is incorporated into this development branch and reconciled with the owner’s modeling-only C1 scope. No gameplay proposals were implemented.

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

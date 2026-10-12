# FISH.IO project state

**C0 complete. C1 NOT ACCEPTED. Final touchup candidate delivered for owner inspection; C2 and Fish Factory not started.**

## Current C1 checkpoint

Existing branch `dev/c1-largemouth-bass`, draft [PR #2](https://github.com/timporachin/fish.io/pull/2), unmerged. Main remains at `95f63b07575cece839f21c6d4dfd6fa9056ebf86`. Application/simulation code and existing test assertions are unchanged.

The final attempt modifies the jaw mesh: curved snout-to-lip and oral tissue transitions, local posterior maxillary support, deeper oral floor and a recessed convex chin. The overcompressed diagnostic was withdrawn following owner feedback that the face was becoming shorter/flatter. The final approximately 0.4524 m asset retains the fuller head and anterior projection. Fin and rear-body indexed position fingerprints exactly match the saved v2 source. Material source, primary cameras, neutral lighting and exposure remain unchanged; additional uniform-material pictures expose surface geometry.

**Visual acceptance is withheld.** The owner's standard is CAD-grade accuracy and photogrammetry scan quality. Four uncalibrated photographs of different fish and an original procedural mesh cannot certify those standards. The independent [final Astra review](docs/C1_JAW_FINAL_REVIEW.md) records the actual final-image findings and remaining defects. Technical PASS is separate from biological/visual acceptance. This was the last authorized touchup attempt; stop for owner inspection and explicit approval.

The final asset is **22,238 triangles / nine runtime draw calls / five embedded maps**. The owner's **10,976 / 11 / five** remains the reference, and the entire increase is unapproved. Cap simplification removes 676 triangles; local cheek support adds 660, for only 16 fewer than the previous 22,254 proposal. This is not meaningful overall budget optimization. No LOD, population, iPhone/Safari or thermal result is established.

Khronos validation: zero errors/warnings. Three.js loads five images; zero skins/clips. Closed/outward/finite body checks and expanded strict upper/lower/cross-jaw checks pass at rest and in the 25° fixture. The application build, six unit tests and two browser tests pass. Contact/coplanar and enclosed-volume limitations remain; the deformation fixture is not a rig or a natural feeding sequence.

Review [matched final comparisons](docs/C1_JAW_COMPARISONS.md), [latest review](docs/C1_JAW_REVIEW.md), [validation](docs/C1_JAW_VALIDATION.md), [modeling/reproduction](docs/C1_JAW_MODELING.md), [reference limits](docs/C1_JAW_REFERENCES.md) and [final manifest](docs/evidence/c1/jaw/final-touchup/manifest.json). Permitted renders/reports and exact v2 baseline sources are committed under `docs/evidence/c1/jaw/final-touchup/`. Historical v2 baseline images retain their original source identity; geometry validation uses an explicitly regenerated baseline with a distinct `.blend` hash.

The final local Blender/GLB and private photographic gallery are under ignored `artifacts/c1/jaw-final/`; licensed stock photos stay in ignored `artifacts/c1/references/`. Previous evidence remains preserved. No C1 completion, merge, release, C2 or Fish Factory is authorized.

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

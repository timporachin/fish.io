# FISH.IO project state

**C0 complete. C1 supplied-model review checkpoint delivered; C1 NOT ACCEPTED. C2 not started.**

## Current C1 supplied-model adaptation

The owner supplied DigitalLife3D **Model 67A – Largemouth Bass** and confirmed personal, noncommercial use under CC BY-NC 4.0. The original Blender project and textures are preserved unchanged. This adaptation continues on `dev/c1-largemouth-bass` and draft PR #2; it does not replace the saved procedural checkpoint or modify C0/main. See [source, attribution and adaptation](docs/C1_SUPPLIED_ASSET.md) and [asset notice](docs/third-party/DigitalLife3D-Model67A-NOTICE.md).

The static candidate retains the supplied head, volumetric jaws, oral pocket, body silhouette and fin anatomy, repairs PBR connections/color spaces, reduces geometry and textures, and removes source rig/actions from the runtime export. It contains **10,724 triangles**, four embedded images (three 1024² and one 512²), and a 2,097,516-byte GLB. Estimated RGBA8 texture footprint is 13 MiB base / 17.33 MiB with mips, within the previous texture reference. Physical iPhone/Safari profiling remains unverified. The original performance reference remains **10,976 triangles / 11 calls / five textures**.

[Seven matched views and historical comparisons](docs/C1_SUPPLIED_COMPARISONS.md), [mesh/export/jaw validation](docs/C1_SUPPLIED_VALIDATION.md) and [Astra’s independent review](docs/C1_SUPPLIED_REVIEW.md) are delivered. Three.js measures three draw calls; all four images decode, and the truncated negative fixture is rejected. The exact reduced QA mesh supports the temporary jaw-opening test; the runtime remains static. The portable Blender copy packs its four used images. [Evidence identities](docs/evidence/c1/supplied/manifest.json) bind the checkpoint to the rendered files and ignored generated assets.

Astra recommends presenting this anatomically stronger candidate for owner review while identifying a subtle upper-snout centerline seam, reduced close-up skin detail, broad/opaque-looking fin ribs and source-derived fin-root/dorsal-boundary limitations. **C1 remains NOT ACCEPTED.** Technical checks do not establish full photographic realism or deformation readiness. The owner’s visual approval remains pending; no merge, C2 or Fish Factory work is authorized by this checkpoint.

## Preserved procedural C1 checkpoint

**C1 NOT ACCEPTED.** A targeted jaw reconstruction checkpoint is delivered on `dev/c1-largemouth-bass`; draft [PR #2](https://github.com/timporachin/fish.io/pull/2) remains unmerged. C0 application, simulation and tests are unchanged. Main remains at `95f63b07575cece839f21c6d4dfd6fa9056ebf86`. C2 and Fish Factory have not started.

The saved fuller forebody, tapered rear and substantial fin-root geometry are preserved. The revision changes the mouth/head only: curved bite, raised anterior arch, denser lip/interior loops, recessed oral roof/floor, coherent cap sections, maxillary relief aligned with the bite and a wider lower-jaw deformation transition. Actual licensed largemouth photographs guide the reconstruction; they are reference material, not copied texture pixels. Source checkpoint `cecdc94` contains the exact frozen generator/material code. [Archived checkpoints](docs/evidence/c1/jaw/checkpoints/manifest.json) preserve the pre-jaw source and first rejected jaw pass for rollback.

All seven matched neutral anatomical views and an additional open three-quarter comparison are delivered at 1600 × 1000 and 128 Cycles samples. See [comparison gallery](docs/C1_JAW_COMPARISONS.md), [modeling and reproduction](docs/C1_JAW_MODELING.md), [reference documentation](docs/C1_JAW_REFERENCES.md), [validation](docs/C1_JAW_VALIDATION.md) and [independent Astra review](docs/C1_JAW_REVIEW.md). A private portable HTML gallery with the real photographs is under ignored `artifacts/c1/anatomical-revision-v2/jaw-qa/jaw-comparison.html`. Generated `.blend`/GLB/texture files and raw licensed photos remain local ignored artifacts.

The frozen asset has 11,395 source vertices, 22,254 triangles, 16 authored mesh objects, nine runtime draw calls and five embedded images. GLB size is 3,906,132 bytes. The original reference remains **10,976 triangles / 11 calls / five textures**. The full 22,254-triangle cost is an **unapproved budget proposal**, not an adopted production budget. The final mouth loops account for 492 additional triangles over the saved 21,762 checkpoint. Physical iPhone/Safari profiling, LODs, compression and population performance remain unverified.

The GLB validator reports zero errors and warnings; Three.js loads all five images with no rig, skin or clips. Strengthened geometry tests find zero strict intra-upper, intra-lower or cross-jaw crossings at rest and in a temporary 25° lower-jaw opening. The body is closed/outward/finite, and fin/rear-body position hashes exactly match the baseline. Those checks exclude coplanar/shared-vertex contacts and enclosed volumes and do not prove natural feeding biomechanics or every self-intersection. The new checks also expose self-folds in the older checkpoints, documented without changing their preserved evidence.

**Astra recommends HOLD.** The final views still show an overprojected/blunt upper rim, an insufficiently distinct posterior maxillary terminal and mouth-corner return, and a broad cap/shelf-like lower oral tip. This is a structurally repaired checkpoint, not a completed biologically accurate reconstruction. Technical PASS does not grant visual acceptance.

**Stop at the C1 review gate.** The user’s visual approval and explicit approval of any increased budget remain pending. No merge, release, C2 or unrelated development is authorized. Earlier rejected evidence remains archived under `docs/evidence/c1/before/`, `before-matched-lighting/`, `rework-1/` and `jaw/pass-1/`.

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

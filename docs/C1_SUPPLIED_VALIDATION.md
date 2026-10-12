# C1 supplied bass validation

**Technical checks do not grant visual acceptance. C1 remains NOT ACCEPTED.** The source, permitted personal/noncommercial use, adaptation steps and attribution are documented in [C1 supplied asset](C1_SUPPLIED_ASSET.md). The previous procedural checkpoint remains preserved.

## Frozen runtime candidate

| Measure | Result | Original reference |
| --- | ---: | ---: |
| Geometric and rendered triangles | 10,724 | 10,976 |
| Measured Three.js draw calls, one fish | 3 | 11 |
| Embedded, successfully decoded images | 4 | 5 |
| Texture dimensions | Three 1024²; one 512² | — |
| Estimated RGBA8 base / mip footprint | 13 / 17.33 MiB | 14 / 18.67 MiB |
| GLB bytes | 2,097,516 | — |
| Skins / animation clips | 0 / 0 | Static C1 |
| Model length | 0.45 m | — |

The footprint is a dimension-based estimate, not measured GPU memory. Renderer metrics come from the actual GLB loaded through Three.js GLTFLoader in Chromium/SwiftShader. They establish compatibility and asset cost, not physical iPhone/Safari frame rate or population performance. Single-sided fin surfaces avoid the transparent double-sided extra draw; both source fin sides remain modeled.

Frozen GLB SHA-256: `b2476193bb8b79431e3ab15596b660ed0297e5bf7f3f0e5394d85e04bb44a7eb`.

Frozen static Blender SHA-256: `0be1f4cdea04ef070bec30c926b4fe86c9368d62938716de8a01962f34c215e6`.

A separate portable Blender copy packs exactly the four used images and opens without the workspace texture paths. It leaves the frozen static input and GLB unchanged. Portable `.blend`: 4,186,800 bytes, SHA-256 `e1b5ae2b6f593a98d2752f2ce9aa55afdba15cb6c57ba2076358b9ccd62b7d64`. `pack_supplied_candidate.py` reproduces this delivery copy and its report. The private review ZIP includes that Blender copy, the GLB and the attribution notice.

The pinned Khronos validator reports **zero errors and warnings**. A deliberately truncated copy is rejected by the real browser loader. Existing procedural C1 test assertions are unchanged; the supplied asset has its own meaningful checks instead of pretending to have the procedural model's named parts or UV atlas.

## Geometry and temporary articulation

The reduced body/fin mesh contains 10,500 triangles; the eyes add 224. Cleanup removes the source's two unused vertices and four wire edges without changing the surface triangle count. Geometry inspection checks finite positions, zero-area faces, connectivity, winding and edges with more than two incident faces.

The assembly retains **64 body boundary edges**: two 26-edge eye-socket loops covered by separate eye cups, and a 12-edge near-sagittal dorsal fin rim at the spiny/soft dorsal transition. The eye cups also have attachment boundaries. This is not a watertight single solid; the dorsal rim remains a documented source-derived limitation requiring visual inspection. No boundary count is relabeled as proof of a closed manifold.

A private weighted QA snapshot preserves the exact reduced body surface and original jaw weights before the runtime rig is stripped. In memory only, the existing jaw bone rotates −25° around its local X axis. This exposes a genuine invaginated oral pocket; it does not add gameplay animation or adopt the source swim actions. At a source-coordinate section 2 mm off the sagittal plane and 105 mm toward the snout, the inner gap changes **5.770 → 24.971 mm**, versus **5.767 → 25.059 mm** in the unreduced source.

Combined head-region BVH checks include jaw-transition faces and find **zero strict nonadjacent triangle crossings** at rest and in that QA opening (2,274 / 2,272 tested triangles). The tests exclude shared-vertex adjacency and coplanar contact and cover only the defined anterior head region. They do not prove every model surface is intersection-free or establish natural feeding biomechanics. Body and eye polygon indices in the QA snapshot match the final static surface; the documented orientation/scale/translation fits every position within 2.02 × 10⁻⁸ m, binding the fixture to the candidate rather than relying on source-only deformation.

## Reproduction and evidence

Run from the repository root with Blender 4.3.2, keeping the original source and textures under ignored `artifacts/c1/user-supplied/original/`:

```sh
blender --background --disable-autoexec artifacts/c1/user-supplied/original/largemouthBass_065_johnson_sketchfab.blend --python-exit-code 1 --python tools/blender/prepare_supplied_bass.py
node tools/blender/validate_glb.mjs artifacts/c1/supplied-candidate/candidate-static.glb
node tools/blender/qa_supplied_browser.mjs artifacts/c1/supplied-candidate/candidate-static.glb artifacts/c1/supplied-candidate/browser-qa.json
python tools/blender/validate_supplied_candidate.py --qa-dir artifacts/c1/supplied-candidate
```

Geometry, mouth-section and rendering tools are `qa_supplied_bass.py`, `qa_supplied_mouth.py`, `qa_supplied_sections.py` and `render_supplied_bass_qa.py` under `tools/blender/`; their command-line help specifies fixture and output arguments. Selected immutable reports and rendered evidence are retained under [supplied evidence](evidence/c1/supplied/). Original source bytes and generated Blender/GLB files remain ignored local artifacts. See [comparisons](C1_SUPPLIED_COMPARISONS.md) and [Astra review](C1_SUPPLIED_REVIEW.md) for visual findings.

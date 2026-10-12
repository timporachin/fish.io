# C1 jaw final-touchup modeling handoff

**C1 NOT ACCEPTED; the final attempt fails the requested anatomical/visual standard.** This is the owner's final touchup attempt on `dev/c1-largemouth-bass` and draft PR #2. Owner visual approval and geometry-budget approval remain outstanding. No merge, C2 or Fish Factory is authorized. The final candidate is a procedural mesh referenced to photographs; it is not a photogrammetry scan or a dimensionally certified CAD reconstruction.

## Final mesh changes

The final source keeps the fuller head and anterior projection after withdrawing an overcompressed diagnostic. It changes the anterior exterior-to-oral correspondence, snout contour, curved bite, oral-floor depth and convex mandibular contour. Concave oral sections close with a horseshoe-shaped tissue strip and projected contour tessellation instead of contracting to a single cap center. The posterior maxillary relief is supported by local exterior cheek subdivision and an oval contour placed above the mouth seam. The final-image review still finds this contour too sharply bounded and the terminal seam unresolved. Original cheek vertices are preserved during subdivision; new points carry the local relief. Fin and rear-body indexed position fingerprints match the regenerated v2 baseline exactly.

These are actual mesh changes. `bass_materials.py` is byte-for-byte unchanged. Primary cameras, neutral white lighting, exposure and render settings match the preceding evidence. Supplemental uniform-material views show the same geometry without texture detail. Source/asset identities and the independent anatomical verdict belong to the final evidence manifest and review, not to these implementation descriptions.

The final asset has **22,238 triangles / nine runtime draw calls / five embedded images**, versus the owner's **10,976 / 11 / five** reference. Removing four cap sections and both center vertices removes 676 triangles; local maxillary support adds 660. Net reduction from v2 is only 16 triangles (0.0719%), not meaningful overall budget optimization. The entire higher budget remains unapproved. Existing fin/rear geometry is retained rather than silently decimated. No LOD, population or physical-device performance qualification is claimed.

## Reproduce the final candidate

From the repository root with Blender 4.3.2 and installed pinned npm dependencies:

```sh
blender --background --python-exit-code 1 --python tools/blender/generate_bass.py -- --seed 1947 --output artifacts/c1/jaw-final --skip-renders
npm run test:bass --prefix tools/blender -- ../../artifacts/c1/jaw-final/largemouth-bass.glb
```

For the exact v2 source used to rebuild the geometry baseline, see `docs/evidence/c1/jaw/final-touchup/checkpoints/v2/`. The generator hash must match the historical v2 source recorded in the preceding review. Regenerating a `.blend` changes its file identity, even if the deterministic geometry matches.

```sh
blender --background --python-exit-code 1 --python docs/evidence/c1/jaw/final-touchup/checkpoints/v2/generate_bass.py -- --seed 1947 --output artifacts/c1/checkpoint-v2 --skip-renders
blender --background --python-exit-code 1 --python tools/blender/render_jaw_revision.py -- --before artifacts/c1/checkpoint-v2/largemouth-bass.blend --after artifacts/c1/jaw-final/largemouth-bass.blend --output-dir artifacts/c1/jaw-final/jaw-qa --require-geometry-pass
```

This last command freshly renders both sides. The delivered primary set instead uses `--skip-before-renders`: geometry checks load the regenerated baseline, while the before pictures are the verbatim, previously rendered v2 images, with their original asset/image lineage preserved separately in the manifest. Do not attribute those historical pixels to the regenerated baseline's new `.blend` hash. The candidate's new images are bound to the exact frozen final `.blend` by the new QA report.

The seven primary after views are 1600 × 1000, 128 Cycles samples, fixed orthographic cameras and neutral white lighting, without denoising. Supplemental open three-quarter rendering uses `--views jaw_open_25deg --open-three-quarter`. Additional three-view uniform-material comparisons use `--clay --views close_right_mouth,front_three_quarter_head,jaw_open_25deg --open-three-quarter --samples 32 --width 1200 --height 750`; their baseline pictures are freshly rendered from the regenerated v2 source.

The QA opening is a weighted 25° lower-jaw deformation fixture. It is not a rig, feeding-motion validation, maxillary articulation, skin or animation clip. C2 remains outside scope. Strict triangle-crossing checks exclude shared-vertex pairs and do not classify coplanar contacts or enclosed volumes.

A private photographic gallery can be rebuilt with:

```sh
python tools/blender/build_jaw_gallery.py --qa-dir artifacts/c1/jaw-final/jaw-qa --baseline-metrics docs/evidence/c1/jaw/browser-validation.json --candidate-metrics artifacts/c1/jaw-final/browser-validation.json --reference-dir artifacts/c1/references --baseline-label 'Previous v2 (NOT ACCEPTED)' --baseline-cost-label 'Previous v2 (unapproved)' --embed-images --output artifacts/c1/jaw-final/jaw-qa/jaw-comparison.html
```

Keep the licensed reference photographs, the embedded gallery, GLB and Blender asset under ignored `artifacts/`. Permitted renders, reports and reproducible sources are committed under `docs/evidence/c1/jaw/final-touchup/`. Inspect the latest [comparisons](C1_JAW_COMPARISONS.md), [validation](C1_JAW_VALIDATION.md), [independent final review](C1_JAW_FINAL_REVIEW.md) and [photographic reference limits](C1_JAW_REFERENCES.md).

## Superseded v2 handoff (historical)

The following retained record describes the previous v2 candidate, not the final touchup.

# C1 jaw reconstruction — modeling handoff

**Status: C1 NOT ACCEPTED.** The second jaw revision is frozen as an unaccepted review candidate. Seven matched 1600 × 1000 views, a supplemental open three-quarter comparison and the independent Astra review are delivered; owner visual and budget approval remain pending. The first jaw pass under `docs/evidence/c1/jaw/pass-1/` is a diagnostic checkpoint, not the final candidate.

## Reconstruction changes

The saved body and fin geometry is preserved. The head has a curved bite, a common raised anterior arch, denser lip-to-interior loops, recessed roof/floor depth, and forward cap sections that advance as coherent planes. This replaces the irregular cap contraction that produced local folds. The maxillary relief follows the bite direction; lower-jaw weights transition over 30 mm for the temporary opening test. No complete jaw animation system is implemented.

The candidate adds 246 source vertices and 492 triangles over the saved 21,762-triangle jaw pass, all in local mouth/cap topology. It has 11,395 source vertices, 11,525 authored polygon faces, 22,254 triangles, 16 authored mesh objects, nine materials and five packed images. Five maps comprise three 1024² body maps and two 512² fin maps; the latter include an opaque iris tile shared with the pectoral map. The material is original procedural PBR calibrated against inspected photos, not photographic texture pixels.

The final [independent Astra review](C1_JAW_REVIEW.md) remains HOLD: the upper rim is too tube-like, the posterior maxillary termination is insufficiently distinct, and the open lower tip remains cap-like. The high-resolution evidence confirms these defects remain; this is a structurally repaired checkpoint, not a completed anatomical reconstruction.

## Anatomical target

Model an adult largemouth bass head with a short blunt snout, a rounded upper lip, a long curved lateral mouth seam, and a substantial lower mandible and chin. The side plate below the eye should carry the mouth corner back into the cheek. The front and three-quarter views must retain jaw width and a recessed cavity. Use the actual local photographs and their pose limits in [C1 jaw references](C1_JAW_REFERENCES.md). Stock 482505893 shows a hand pulling/supporting the lower lip; its extreme gape documents cavity and jaw volume, not a relaxed jaw angle.

Keep the jaw as a connected, closed, outward-facing body surface with meaningful upper/lower regions for later animation. The temporary 25° QA opening rotates weighted lower-jaw vertices around a posterior hinge. It tests opening clearance and visible depth only; it does not establish a C2 rig, skin weights, an animation clip, or a biological maximum gape. C2 remains outside this modeling pass.

## Reproduce the v2 working asset

Run from the repository root with Blender 4.3.2 and the repository's Node dependencies installed. The generator's default seed is `1947`. Its `--output` and `--output-dir` flags are aliases. The direct Blender command is explicit about the v2 output path:

```sh
npm ci
npm ci --prefix tools/blender
blender --background --python-exit-code 1 --python tools/blender/generate_bass.py -- --seed 1947 --output artifacts/c1/anatomical-revision-v2 --skip-renders
npm run test:bass --prefix tools/blender -- ../../artifacts/c1/anatomical-revision-v2/largemouth-bass.glb
```

The generator writes the `.blend`, GLB, procedural maps and stats to the ignored v2 directory. npm runs the script from `tools/blender`, so the GLB argument uses `../../artifacts/`. `test:bass` accepts that path as its positional argument, finds the adjacent `.blend`, runs GLB, browser and Blender geometry checks, and writes `browser-validation.json` and `blender-geometry-validation.json` beside the asset. Preserve the reviewed asset and reports together; do not infer final v2 metrics from the earlier pass. The tests require an environment with Blender and the browser dependencies used by the project.

## Matched jaw render and local gallery

If the ignored baseline Blender file is missing, regenerate it from the archived pre-jaw sources (the sibling archived material module is imported automatically):

```sh
blender --background --python-exit-code 1 --python docs/evidence/c1/jaw/checkpoints/anatomy-before/generate_bass.py -- --seed 1947 --output artifacts/c1/anatomy-before --skip-renders
```

A regenerated `.blend` may have different metadata/hash; rerender both sides rather than attempting hash-verified baseline reuse.

The seven-view renderer takes a preserved before `.blend`, a candidate after `.blend`, and an output directory. The `--after-only` mode verifies the baseline Blender hash and the seven baseline image hashes recorded in the supplied report, then renders only the v2 candidate. The baseline report shown below is the complete first-pass seven-view report, not the separate supplemental report. If the prior baseline is unavailable or its hashes fail, rerender both sides by omitting `--after-only` and `--baseline-report`.

```sh
blender --background --python-exit-code 1 --python tools/blender/render_jaw_revision.py -- \
  --before artifacts/c1/anatomy-before/largemouth-bass.blend \
  --after artifacts/c1/anatomical-revision-v2/largemouth-bass.blend \
  --output-dir artifacts/c1/anatomical-revision-v2/jaw-qa \
  --after-only \
  --baseline-report artifacts/c1/anatomical-revision/jaw-qa/jaw-qa-report.json
```

The supplemental open-mouth view needs its own camera-matched baseline report and `--open-three-quarter` flag. It uses only the `jaw_open_25deg` view:

```sh
blender --background --python-exit-code 1 --python tools/blender/render_jaw_revision.py -- \
  --before artifacts/c1/anatomy-before/largemouth-bass.blend \
  --after artifacts/c1/anatomical-revision-v2/largemouth-bass.blend \
  --output-dir artifacts/c1/anatomical-revision-v2/jaw-qa/supplemental-open \
  --views jaw_open_25deg --open-three-quarter --after-only \
  --baseline-report artifacts/c1/anatomical-revision/jaw-qa/supplemental-open/jaw-qa-report.json
```

Both reports are named `jaw-qa-report.json` in their respective output directories. Default render settings are 1600 × 1000, 128 Cycles samples, and fixed neutral lighting. Keep the camera and sample settings matched when reusing a baseline report.

The gallery script embeds the unaltered existing images for a portable private HTML page when `--embed-images` is set; otherwise it links them locally. It does not render or edit pixels. It reads original and candidate browser metrics at generation time. Its default QA path is the v2 path above:

```sh
python tools/blender/build_jaw_gallery.py \
  --qa-dir artifacts/c1/anatomical-revision-v2/jaw-qa \
  --reference-dir artifacts/c1/references \
  --embed-images --output artifacts/c1/anatomical-revision-v2/jaw-qa/jaw-comparison.html
```

Open the resulting HTML locally. The three raw licensed stock photographs and this gallery must stay in ignored `artifacts/` for private review; do not commit or publish them. The gallery includes the seven matched views, the supplemental three-quarter open pair, and source captions with the hand-forced gape caveat.

## Delivered review package

The permitted rendered/model evidence is archived in `docs/evidence/c1/jaw/`: seven images each in `before/` and `after/`, the supplemental pair in `supplemental-open/before/` and `supplemental-open/after/`, both `jaw-qa-report.json` files, `browser-validation.json`, `blender-geometry-validation.json`, model stats, and an asset manifest with hashes. These are the actual review-evidence paths. See [comparison gallery](C1_JAW_COMPARISONS.md) and [manifest](evidence/c1/jaw/manifest.json). Keep the stock photos in ignored `artifacts/c1/references/`.

The independent decision belongs in [C1_JAW_REVIEW.md](C1_JAW_REVIEW.md), with visual evidence across left, right, front, top, three-quarter and open views. A machine pass or a better first-pass comparison alone does not accept C1.

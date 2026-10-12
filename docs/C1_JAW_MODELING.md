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

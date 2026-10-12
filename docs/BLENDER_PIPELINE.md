# Blender to GLB pipeline

## Toolchain evidence

The headless executable available in this workspace reports `Blender 4.3.2` (`blender --version`). The smoke fixture exports using Blender's bundled `bpy.ops.export_scene.gltf` operator and produced a valid animated binary glTF (GLB). This verifies the installed exporter path end to end. The exporter logged that its optional Draco library is unavailable; compression is not enabled, and the file exported and validated without Draco.

GLB validation is pinned to npm package `gltf-validator@2.0.0-dev.3.10` in this directory's package manifest and lockfile. Install deterministically with `npm ci`; run `npm run smoke` to export, inspect, and validate the fixture. The generated GLBs are written under root `artifacts/`, which is ignored by Git. To validate a model directly, run `npm run validate -- ../../artifacts/model.glb` from `tools/blender`.

The smoke fixture is intentionally a blue cube and a moving amber sphere (`Validation_Cube`, `Validation_Animated_Beacon`), with translation and rotation keyframes. It is not fish geometry. The smoke check verifies the GLB header, both node names, at least one animation channel, and zero glTF validation errors. Its negative check corrupts the GLB magic and confirms the validator exits unsuccessfully.

## Production fish asset pipeline

Keep generation deterministic and reviewable: accept a seed and explicit species/size parameters, create geometry and a rig in Blender Python, bake the intended animation into a named Action, export selected asset objects and the active action as GLB, then run the pinned validator. Avoid hand-authored GUI state as an input to generation. Store reusable generator scripts and compact parameter data in source control; put generated `.blend` previews and `.glb` outputs in ignored `artifacts/`.

A practical first rig can use a small deforming armature with a root, several spine joints, head, and tail chain, plus separate fin chains for dorsal, pectoral, pelvic, and caudal motion where useful. Weight the body smoothly across the spine and tail. Keep bone names stable and use a deliberate rest pose. Bake procedural oscillation to sampled keyframes in a named looping action before export; include a short period with matching first and last pose. glTF animation carries node/bone transforms and morph weights, but does not carry Blender constraints, drivers, Geometry Nodes logic, or arbitrary simulation state. Baking makes playback portable in ordinary glTF runtimes.

Use Blender authoring coordinates consistently: define the fish's nose along local +X, dorsal direction +Z, and keep the origin near the body center. Apply object transforms before skinning/export, use meters, and let Blender's glTF exporter perform the glTF coordinate conversion. Use one material per visual region where possible, UVs for detailed markings, and keep names stable. Prefer a single skinned mesh and armature per fish asset unless separate materials/parts provide a clear benefit. Export a separate GLB for each reusable fish asset, rather than scene lighting/cameras or aquarium environment content.

For varied populations, derive meshes and markings from a stable seed plus explicit parameters (body length/depth, head profile, fin proportions, palette, markings). Start with a compact parameterized mesh generator and shared armature topology; add mesh variants only when parameters cannot express a meaningful species difference. Validate representative output for each topology/material/animation path, and re-import a release candidate in Blender or the target runtime to check pose, scale, orientation, material appearance, and loop continuity.

## Extension assessment

The direct Blender Python API and official glTF exporter are the production baseline: they are already present in Blender 4.3.2 and the headless GLB smoke export works. The exporter is the required boundary because it writes portable glTF data.

Rigify is an official Blender add-on for generating control rigs from building-block components. Its source metadata at `blender/blender-addons/rigify/__init__.py` describes automatic rigging and declares Blender 4.0 compatibility in the fetched upstream source. It may help an artist create a complex animator-facing control rig, but its generated controls and constraints still need a simpler deform skeleton and baked animation for GLB. A fish's continuous body bend is also a specialized rig; for this pipeline a small custom deform armature is easier to keep deterministic and export-ready. No Rigify dependency is needed for headless generation.

Animation Nodes describes itself upstream as a node-based visual scripting system aimed at motion graphics. It adds an external add-on dependency and does not remove the need to bake its output to standard glTF animation channels. It is not a good runtime interchange dependency for this fish asset workflow. Blender's built-in Python and armature tools cover deterministic procedural geometry and animation without requiring extra GUI or add-on installation.

Sources checked from upstream repositories on 2026-10-12:

- Blender add-on source: `https://raw.githubusercontent.com/blender/blender-addons/main/rigify/__init__.py`
- Animation Nodes project README: `https://raw.githubusercontent.com/JacquesLucke/animation_nodes/master/README.md`
- Blender glTF exporter source: `https://raw.githubusercontent.com/blender/blender/main/scripts/addons_core/io_scene_gltf2/__init__.py`


## C1 modeling workflow

The C1 entry point is `tools/blender/generate_bass.py`, with original photo-referenced PBR maps authored by `bass_materials.py`. It authors an unrigged largemouth bass in meters with nose +X and dorsal +Z. Generated textures, `.blend`, GLB, six reference images and reports are written to `artifacts/c1/`; those generated asset files remain ignored. Selected reference PNGs are retained in `docs/evidence/c1/` for visual PR review. The owner rejected the first C1 candidate; the rework preserves its evidence and compares all six views under matching inspection lighting. See [photographic references](C1_PHOTO_REFERENCES.md) and [comparisons](C1_COMPARISONS.md).

Run from the repository root using Blender 4.3.2:

```sh
blender --background --python-exit-code 1 --python tools/blender/generate_bass.py -- --output-dir artifacts/c1 --seed 1947
npm ci
npm ci --prefix tools/blender
npm run test:bass --prefix tools/blender
```

`--skip-renders` regenerates authoring/export artifacts without reference rendering; `--render-view left` limits a diagnostic run to one view. A release review must use the complete six-view run. `--python-exit-code 1` is required because Blender otherwise can exit successfully after a Python exception. Denoising is disabled on this Debian build because its OpenImageDenoise backend is unavailable.

`test:bass` validates with the pinned Khronos validator, loads the actual embedded GLB textures in Three.js/Chromium, captures a rendered screenshot and runtime metrics, rejects a corrupt model, and independently inspects the authored Blender mesh. The asset viewer is isolated tooling; it adds no fish geometry or asset loading to the C0 gameplay scene. See [C1 modeling](C1_MODELING.md), [references](C1_REFERENCES.md), and [independent review](C1_REVIEW.md).

The C1 request takes priority over the general rig-and-animation proposal above: no armature, skinning or swimming clips are included in C1. Human visual approval is required before C2 animation development. Source topology checks cannot establish deformation readiness or automatically accept visual quality.


## Targeted C1 jaw reconstruction (pending acceptance)

The latest revision uses the saved body/fin model as its baseline; it does not restart C1. Archived generator/material sources and asset hashes are under `docs/evidence/c1/jaw/checkpoints/`. The original 10,976-triangle/11-call/five-texture reference is unchanged; higher geometry budgets are proposals pending explicit owner approval. Generated candidates use separate ignored output directories rather than replacing the preserved assets.

`render_jaw_revision.py` compares frozen Blender inputs with fixed neutral cameras and lighting. Its seven anatomical views include a temporary weighted 25° lower-jaw opening, with an optional supplemental three-quarter opening. This loaded-scene deformation is validation only: production exports contain no rig, skin or animation clips. The report checks closed/outward geometry, limited upper/lower triangle crossings, and fin/rear-body position fingerprints; it cannot prove natural feeding biomechanics or every local self-intersection. Hash-verified `--after-only` reuse avoids rerendering an unchanged baseline.

`build_jaw_gallery.py` makes a private local comparison page with the seven pairs, supplemental opening pair and licensed real photographic references. Those raw photos remain local ignored review material. See [jaw modeling](C1_JAW_MODELING.md), [validation](C1_JAW_VALIDATION.md), [references](C1_JAW_REFERENCES.md) and [Astra review](C1_JAW_REVIEW.md). A technical pass is separate from the user's visual acceptance; C2 and merge remain gated.

## Supplied-model C1 adaptation (personal, noncommercial)

The owner subsequently supplied DigitalLife3D Model 67A and confirmed personal, noncommercial use. Its original Blender source, textures, rig and saved actions remain unchanged in ignored artifacts. `prepare_supplied_bass.py` creates a separate static reduced candidate, repairs PBR connections/color spaces and bakes portable fin opacity; it exports no rig or clips. The previous procedural checkpoint remains available for comparison and rollback. Attribution and exact changes are recorded in [supplied asset documentation](C1_SUPPLIED_ASSET.md).

Source-specific geometry, oral-section, controlled jaw-opening and browser checks are separate from the procedural atlas/part-name assertions. A private weighted snapshot retains the exact reduced surface for the temporary jaw test; transform equivalence establishes its correspondence to the final static asset. `render_supplied_bass_qa.py` uses length-scaled cameras and area lights with squared-length energy normalization. Seven matched anatomical views and the historical comparison are for review, not automatic acceptance. See [validation](C1_SUPPLIED_VALIDATION.md), [comparisons](C1_SUPPLIED_COMPARISONS.md) and [independent review](C1_SUPPLIED_REVIEW.md). C1 remains unaccepted and C2 is untouched.

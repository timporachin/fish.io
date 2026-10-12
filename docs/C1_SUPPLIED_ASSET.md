# C1 user-supplied largemouth bass: intake and adaptation checkpoint

**Status: personal, noncommercial adaptation prototype authorized; C1 visual acceptance pending.** The supplied model is a candidate anatomical starting point for C1. The existing procedural C1 checkpoint at `cc12202` and its frozen source at `cecdc94` remain preserved. Draft PR #2 remains unmerged; C0, `main`, and C2 are outside this adaptation.

## Source and permitted use

The user supplied `largemouthBass_065_johnson_sketchfab.zip` and confirmed the intended use is personal and noncommercial. The source is [Model 67A - Largemouth Bass](https://sketchfab.com/3d-models/model-67a-largemouth-bass-e60c457636b640629747c19feac4906c), published by DigitalLife3D on 2020-06-13. The source identifies the CG artists as Jer Bot, Johnson Martin, and Robert Gutierrez. It describes an animated adult *Micropterus salmoides* based on adult images from Maymont Nature Center and a preserved specimen scan at the Natural History Collection, University of Massachusetts Amherst. The page credits Maymont Nature Center, Richard Lewis Media Group, and the Natural History Collection. It offers downloads for creative and nonprofit use and directs licensing inquiries to [DigitalLife3D](https://www.digitallife3d.org/).

The user provided the [Creative Commons Attribution-NonCommercial 4.0 International](https://creativecommons.org/licenses/by-nc/4.0/) license link and confirmed personal, noncommercial use. For this prototype and any adapted model or renders shared under that license, retain creator/source attribution, the license link, a description of changes, and the no-endorsement condition. Commercial use requires separate rights-holder permission. The [asset notice](third-party/DigitalLife3D-Model67A-NOTICE.md) supplies copy-ready attribution. Project-authored scripts and other independent work do not acquire the model's license merely by being stored nearby.

## Intake and baseline

Original extracted files remain unchanged and ignored under `artifacts/c1/user-supplied/original/`; the archive and private inspection files are also ignored. [`intake-manifest.json`](../artifacts/c1/user-supplied/intake-manifest.json) records file byte counts, SHA-256 hashes, provenance and inspection settings. That local file is an inspection artifact, not a public distribution of the supplied model. The source `.blend` saved in Blender 2.82 opens in Blender 4.3.2.

| Source characteristic | Inspected value |
| --- | ---: |
| Base body mesh | 1,075 vertices, 1,988 triangles |
| Base eye mesh | 130 vertices, 224 triangles |
| Total base triangles | 2,212 |
| Evaluated source with Mirror and subdivision | 16,128 triangles |
| Color, normal, roughness maps | Three 4,096 × 4,096 images |
| Alpha map | One 2,048 × 2,048 image |
| Armature / saved swim actions | Present / five |

The base and evaluated counts are distinct; runtime export cost must be measured from the candidate GLB. The four source maps represent an estimated 208 MiB if decoded as RGBA8 at their original resolutions, or about 277 MiB with a full mip chain. This is a format-and-dimension estimate, **not measured GPU memory**, and it excludes other runtime copies or compression. The five saved actions were inventoried only; no action was adopted, modified or exported for C2.

## Inspection and adaptation gate

The initial inspection repaired external texture paths in memory, reconnected the existing Principled BSDF to the material output in place of a saved Emission Viewer, used the armature rest pose, and rendered two neutral-lit views. It did not change the original extracted files. An independent review found materially better anatomical potential than the procedural starting point, while flagging washed-out coloration, pale or opaque fins, and unverified mouth width, depth, articulation, and front views. Subsequent source geometry inspection found an invaginated oral pocket: upper and lower inner surfaces converge approximately 30–35 mm behind the lip tips, and a temporary −25° pose of the *existing* jaw bone exposes that interior. This establishes a source feature, not candidate mouth validation or C2 rig adoption. The inspection is **not** visual acceptance.

The frozen static candidate, renders and `preparation-report.json` are under ignored `artifacts/c1/supplied-candidate/`. Reproduce it from the repository root with `blender --background --disable-autoexec artifacts/c1/user-supplied/original/largemouthBass_065_johnson_sketchfab.blend --python-exit-code 1 --python tools/blender/prepare_supplied_bass.py`. The script saves `authoring-baseline.blend`, `candidate-weighted-qa.blend`, `candidate-static.blend`, `candidate-static.glb`, derived textures, four candidate renders and a report containing source/derivative SHA-256 hashes. The original supplied files remain byte-identical.

The candidate reconnects the source PBR material in place of the saved Emission Viewer and marks roughness/normal maps as non-color data. It reduces the source's 4K color, normal and roughness maps to 1K and the 2K alpha map to 512 px. It bakes fin opacity into a derived 512 px RGBA color map (`opacity = 1 − 0.6 × source alpha grayscale`) and applies a translucent material only to polygons classified by named fin groups. Both materials are single-sided. Symmetry-preserving mesh reduction takes the evaluated body from 15,904 to 10,500 triangles; the eye remains 224 triangles. Cleanup removes four source-inherited wire edges and two loose vertices. The static export has no armature, skin or actions, with nose +X, dorsal +Z and 0.45 m length. No global recoloring or tint was applied; neutral render light was adjusted to show the supplied olive coloration.

| Candidate export measure | Result | Original target |
| --- | ---: | ---: |
| Triangles | 10,724 | 10,976 |
| Measured Three.js draw calls, one fish | 3 | 11 |
| Embedded GLB images | 4 | 5 textures |
| Materials | 2 | — |
| GLB bytes | 2,097,516 | — |
| Skin / animation clips | 0 / 0 | C2 not started |

The GLB SHA-256 is `b2476193bb8b79431e3ab15596b660ed0297e5bf7f3f0e5394d85e04bb44a7eb`. Its three 1K maps and one 512 px fin RGBA map have an estimated 13 MiB RGBA8 decoded base-level footprint, or 17.33 MiB with full mip chains. That is below the previous 18.67 MiB texture estimate, but remains an estimate, **not measured GPU memory**. The separate 512 px alpha intermediate is not embedded in the GLB. The Khronos glTF validator reports zero errors and warnings. Three draw calls were measured with the actual GLB in Three.js/Chromium using SwiftShader; physical iPhone/Safari and population performance remain unverified. The original 10,976-triangle / 11-call / five-texture target remains unchanged.

Geometry QA records 64 body boundary edges: two 26-edge eye-socket loops beneath separate eye cups and a 12-edge dorsal midline rim at the spiny/soft dorsal transition. The rim remains a source-derived limitation for visual review; this assembly is not a watertight single solid. The private weighted QA snapshot preserves the reduced surface and source jaw weights for a temporary −25° jaw opening. It exposes an oral pocket; a defined anterior-head check found zero strict nonadjacent triangle crossings at rest and in that opening, within the check's stated scope. The static export itself has no rig or open-mouth state. See [technical validation](C1_SUPPLIED_VALIDATION.md), the pending [supplied-asset review](C1_SUPPLIED_REVIEW.md) and [evidence gallery](evidence/c1/supplied/) for the full evidence and limitations. Neither the export nor validator grants visual acceptance; **C1 remains not accepted**.

Before any C1 adoption, inspect matched anatomical views including the front and document the source open-mouth pose separately from the static candidate, complete geometry and browser GLB loading checks, and assess the candidate's texture appearance and silhouette with the user. A static export cannot itself demonstrate an open-mouth pose. No C2 work or merge follows from the private prototype alone.

The remote final procedural touchup at `9d4dcb2` was integrated without replacing either history; its [independent final review](C1_JAW_FINAL_REVIEW.md) and archived evidence remain intact. The owner’s [CAD-grade / photogrammetry-quality acceptance requirements](C1_OWNER_FEEDBACK.md) remain in force. The supplied model is a live-photo/preserved-specimen composite; this adaptation does not certify calibrated morphometric or CAD accuracy.

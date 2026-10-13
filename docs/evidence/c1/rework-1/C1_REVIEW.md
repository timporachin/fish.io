# C1 photographic rework — independent final review

**Production recommendation: HOLD / further visual refinement required.** The rework is substantially closer to the photographed largemouth bass, and the identified construction defects were corrected. It still does not support an unqualified production-realism or photorealism claim at close inspection. Owner visual approval is pending. C1 remains open; this review does not authorize C2, merging, or release.

This review supersedes the earlier review of the rejected candidate. It covers the complete 128-sample render set generated on 2026-10-12 at approximately 12:39–12:40 UTC and the matching final Three.js validation. Intermediate renders and tests are not the reviewed deliverable.

## Evidence and artifact identity

The reviewer directly inspected the pixels of all three actual photographs in [C1_PHOTO_REFERENCES.md](C1_PHOTO_REFERENCES.md), all six final views individually—[left](evidence/c1/left.png), [right](evidence/c1/right.png), [front](evidence/c1/front.png), [rear](evidence/c1/rear.png), [top](evidence/c1/top.png), and [front three-quarter](evidence/c1/front_three_quarter.png)—and the final [Three.js screenshot](evidence/c1/largemouth-bass-browser.png). The original rejected views and the [same-lighting baseline profile](evidence/c1/before-matched-lighting/left.png), [front](evidence/c1/before-matched-lighting/front.png), and [three-quarter](evidence/c1/before-matched-lighting/front_three_quarter.png) were compared directly.

All final Blender images are 1200 × 800 at 128 Cycles samples. Five views are orthographic; front three-quarter is perspective with a 60 mm lens. The complete fish is framed in each image. Smaller studio lights were introduced to reduce broad grazing reflections; the rejected model was rerendered with that same lighting for the matched comparison. The original evidence is retained under `evidence/c1/before/`.

These SHA-256 hashes were computed from the actual files and independently matched against `artifacts/c1/browser-validation.json`:

| Artifact | SHA-256 |
| --- | --- |
| `artifacts/c1/largemouth-bass.glb` | `ed28f05b0114ebcb7f92079d698f4edcdee7cd47f3e656158ac88d9d19cc9371` |
| `artifacts/c1/largemouth-bass.blend` | `54f7f280127d3571509a624c02d364d92e1e7772c173945be998f39b9a1c942c` |
| `tools/blender/generate_bass.py` | `a0239183ea81be3c71844831fffdc6d20becb6d7ae09f2a85fb72ffba50f1036` |
| `tools/blender/bass_materials.py` | `cfdd172f4de0b7632bf3e6a6b3a8eed8935ef8124de1e2c76dae274f1522ba6f` |

The reviewed browser report hashes to `b37b40ec41cae2587db6bf14b73a3aeddf774d279076477fab2ae9cdbb9c6546`; its screenshot hashes to `03537e905c5d998384e265ee3d724dd66557f7f2c431eb458c5d1dc6b87b0bea`. The [evidence manifest](evidence/c1/manifest.json) records individual render hashes. Independent verification confirmed that all six committed-gallery render hashes, the runtime screenshot, both source files, the GLB and Blender source match the reviewed files and the final report. All ten copied render/report/statistics files are byte-identical to their working artifacts.

## Confirmed improvements

- **Photographic proportions:** Head length, forward eye position, mouth-corner location and forward shoulder depth are substantially closer to the full-profile photograph. These are approximate image-derived proportions, not exact biological measurements.
- **Continuous head construction:** A single connected body branches into upper and lower jaws. The former separate straight jaw strip and large elliptical gill badge are gone. The mouth has a broad raised-center seam, a projecting rounded lower lip and an integrated opercular groove.
- **Corrected artifacts:** The forehead UV stripe, over-pinched muzzle, thick eye washer, excessively deep caudal notch, folded pelvic surfaces and pale angular lip panel were corrected. The lip fold was verified in clay, fixed geometrically with convex cap rings, then checked again without textures. A separate terminal-U wrapping error was corrected to remove the cap's radial shader bands.
- **Skin and fins:** Dark olive dorsum, pale ventrum, irregular lateral blotches, individual gold/olive scale variation and regionally varied roughness replace the earlier cloudy surface. Fin membranes have actual exported alpha, curved fans and less conspicuous ray highlights. The caudal outline is shallower and more coherent.

## Remaining realism findings

| Priority | Final visual evidence | Refinement needed for the requested standard |
| --- | --- | --- |
| High | **Head planes remain simplified.** The side and three-quarter head reads as a broad smooth rounded surface. The cheek/maxilla and operculum have relief, but their distinct anatomical planes remain weak compared with the actual close head photograph. The rounded lip and uniform iris also retain a constructed appearance in the frontal close-up. | Resolve the oblique maxillary plate below and behind the eye, its transition into the cheek, and the opercular volume/rim against the photographed head. Use those specific landmarks to shape the surface; adding general noise or larger bumps will not establish the missing anatomy. Refine iris and surrounding tissue variation at the same inspection scale. |
| Medium | **The scale field remains visibly procedural at close range.** Randomized pigment and gold centers improve the result, but repeated scalloped cells and regular rows remain conspicuous across the flank and belly. The head has less convincing regional surface detail than the photographed fish. | Refine regional scale size, overlap and directional flow, reduce the repeated scallop appearance, and introduce finer irregular head-plate texture while preserving the lateral marking and restrained wet response. |
| Medium | **Fin surfaces remain regular.** Transparency, curvature and ray shading are improved, but the soft dorsal, anal and paired fins still read as comparatively uniform membrane sheets with orderly radiating ribs. | Refine local membrane variation, finer branching striations and subtle curvature around rays. The full-profile reference folds its anterior dorsal and clips the tail edge, so it cannot by itself establish exact standing-dorsal or caudal-edge shape. |

No remaining forehead stripe, central lip fold or floating jaw rail is being reported. The outstanding findings concern the requested visual standard, not a repetition of corrected defects. The runtime screenshot shows the same underlying appearance; its smaller on-screen fish does not establish close-up realism.

## Technical result and limits

| Property | Final measured result |
| --- | --- |
| Blender | 4.3.2 |
| GLB size | 3,513,480 bytes |
| Khronos validator | 0 errors, 0 warnings, 16 informational messages |
| Export geometry | 14,326 triangles; 11,028 vertices |
| Source geometry | 7,435 vertices; 18 anatomical mesh objects |
| Export structure / runtime calls | 1 GLB mesh, 10 material primitives; 10 Three.js draw calls |
| Embedded textures | Five decoded successfully: three 1024² skin maps and two 512² fin maps |
| Fin transparency | Two transparent materials; observed alpha ranges approximately 0.48–0.70 and 0.45–0.67 |
| Authored length | Approximately 0.452 m |
| Skinning / animation | 0 skinned meshes; 0 clips |

The independent Blender report has no failures for its finite geometry/UV, loose geometry, zero-area face, winding, closed-volume and anatomical-part checks. The body is one closed connected component, with distinct upper/lower jaw face regions. Negative cases reject corrupt GLB, unexpected skin/animation, empty mesh, loose vertices, inconsistent winding, missing fin and missing jaw regions. The actual GLB loads, decodes its images and renders in Three.js. Closed fin membranes use outward-facing surfaces with backface culling, avoiding the earlier redundant transparent rendering passes; their surfaces remain visible in the final screenshot.

These checks do not detect every self-intersection, establish anatomy or prove deformation. Longitudinal topology and semantic jaw regions provide a starting point for rig development; no weights, jaw motion, fin deformation or swimming loop were tested. The approximately 8k near-LOD proposal is exceeded. Ten calls per fish, population cost, LODs, compression, memory, thermal behavior and physical iPhone/Safari performance remain unqualified.

## Approval gate

This is a substantial photographic rework and a technically valid candidate. **The independent review still withholds a production-realism recommendation for the reasons above.** Owner inspection and explicit visual approval remain necessary; automated passes and improvement over a rejected baseline do not satisfy that gate. Do not mark C1 complete, call the model visually accepted or production-ready, merge the draft PR, or begin C2 on the basis of this review.

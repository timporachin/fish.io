# C1 final independent review

**Recommendation: REQUEST CHANGES against the requested production-quality realism standard.** This is a technically valid, reviewable modeling candidate, not a visually accepted production asset. User approval is pending. C1 remains open; C2, merging, and release are not authorized by this review.

This review supersedes the preliminary 04:49 review. It covers the final coherent six-view set generated on 2026-10-12 around 05:07 UTC and the refreshed Three.js validation evidence. Previously reported floating mouth rails, stacked protruding eye layers, and the multi-lobed angular tail were corrected and are not current findings.

## Reviewed artifacts

All six 1200 × 800, 64-sample Blender renders were inspected individually: [left](evidence/c1/left.png), [right](evidence/c1/right.png), [front](evidence/c1/front.png), [rear](evidence/c1/rear.png), [top](evidence/c1/top.png), and [front three-quarter](evidence/c1/front_three_quarter.png). The current [Three.js screenshot](evidence/c1/largemouth-bass-browser.png), generator, geometry report, and browser validation report were also inspected.

The five principal cameras are orthographic and aligned to their named axes; the sixth is an elevated front three-quarter perspective view using a 60 mm lens, satisfying the mixed orthographic/perspective evidence requirement in [GAME_DESIGN.md](GAME_DESIGN.md). Anatomical left is viewed from +Y and right from -Y, with the nose +X and dorsal direction +Z in Blender. All views frame the complete fish.

The reviewed GLB is `artifacts/c1/largemouth-bass.glb`, SHA-256:

`851052321895192dad228db459a43a3787f4a9538d59b835e2b30654b46b0865`

The reviewed Blender source is `artifacts/c1/largemouth-bass.blend`, SHA-256:

`384f0c75fd6367fdfb45f6370d6c8ed96426ed38fa8cc31913dfd4d7542537f2`

Hashes were checked against the actual files and agree with `artifacts/c1/browser-validation.json`. The final source contains 24 anatomical mesh objects. Export joins a temporary copy into one mesh with material primitives, preserving the separate authoring parts.

## Remaining visual findings

| Priority | Current evidence | Required refinement |
| --- | --- | --- |
| High | **Jaw and cheek transitions remain visibly constructed from overlapping surfaces.** Left, right, and three-quarter views show an abrupt light lower-jaw border, stepped rear edge, and discontinuous dark mouth seam. The frontal mouth is cleaner, but the cheek/maxilla transitions do not yet read as continuous anatomical tissue. | Fit the lower jaw and upper maxilla to a shared anatomical mouth boundary, blend the rear mandibular transition into the cheek, and remove visible step/intersection edges. Verify in the side and three-quarter views as well as front. |
| High | **Fin shape and material still read as stylized rigid sheets.** The dorsal spine membrane has a regular sawtooth outline and prominent straight ray relief; the soft dorsal and anal fins are uniformly rounded sheets. Pelvic fins retain angular folds visible from front, rear, and side. Pectorals are now coherent radial fans, but remain opaque and leaf-like. | Refine species-specific outlines, soften membrane curvature and ray relief, and rebuild the pelvic fan surfaces to remove sharp folds. Use more convincing regional membrane shading and, where appropriate for the runtime budget, controlled translucency. |
| Medium | **Skin and head realism remain below the requested photographic standard.** Olive coloration, pale belly, and the broken lateral band are present. However, broad cloudy mottling dominates the scale pattern; the cheek/gill cover reads as a separate plate, and the smooth tapered head lacks convincing bony and fleshy transitions around the maxilla and operculum. | Refine head planes against matched photographs and improve regional scale definition, color variation, and wet-skin roughness. Judge the exported material in runtime lighting as well as the studio setup. |

The top view confirms that floating side rails are gone and the terminal outline is rounded. Front/rear views confirm improved eye integration and coherent pectoral fans. The caudal outline is substantially improved. These corrections remove earlier defects, but the remaining findings above prevent a production-realism recommendation.

## Technical results

| Property | Final measured result |
| --- | --- |
| Blender version | 4.3.2 |
| GLB size | 2,585,016 bytes |
| Khronos validator | 0 errors, 0 warnings, 18 informational messages |
| Exported geometry | 10,976 triangles; 8,488 vertices |
| Exported structure | 1 mesh; 11 material primitives |
| Three.js draw calls | 11 for the fish alone |
| Embedded images | 5, all decoded successfully |
| Texture sizes | Three 1024 × 1024 skin maps; two 512 × 512 fin maps |
| Runtime skinning/animation | 0 skinned meshes; 0 animation clips |
| Authored fish length | Approximately 0.455 m |

The body material exports base color, tangent-space normal, and packed roughness/metalness maps. Independent Blender validation reports no failures for the checked finite geometry/UVs, loose or zero-area geometry, unexpected boundaries, and winding/manifold properties. The body is a closed volume. Selected facial plates and lip surfaces have explicitly allowed open boundaries. Negative cases cover corrupt GLB, unexpected animation/skin, empty mesh, missing fin, loose vertex, and inconsistent winding.

Structural passes do **not** establish anatomical accuracy, detect all self-intersections or poorly fitted surfaces, or prove realistic shading. The isolated Three.js screenshot confirms successful loading and visible rendering, with the same stylized appearance seen in the studio references.

## Animation and mobile limits

Longitudinal body loops and separate authoring parts provide a basis for later rig development. No skinning, weights, jaw/fin deformation, or swimming loop has been tested. “Prepared for rig development” is supportable; proven animation readiness is not.

The asset exceeds the provisional approximately 8k near-LOD triangle target. Eleven draw calls per fish use eleven percent of the provisional 100-call whole-scene budget before other scene content. LODs, compression, population rendering, GPU timing, memory, and thermal behavior are unqualified. No physical iPhone or Safari testing occurred; cloud Chromium/SwiftShader evidence is not a device-performance result.

## Approval gate

The final candidate is ready for the user's inspection, but this review recommends further C1 visual refinement before acceptance as a production-quality realistic largemouth bass. User approval remains pending and is separate from the technical export pass. Do not describe the asset as approved, photorealistic, production-ready, or proven optimized for iPhone. Do not begin C2 from automated tests or this review.

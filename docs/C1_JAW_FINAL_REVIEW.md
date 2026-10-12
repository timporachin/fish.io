# C1 final jaw touchup — independent review

**Final verdict: FAIL / HOLD. C1 remains NOT ACCEPTED.** The frozen final asset does not meet the requested anatomical appearance, CAD-grade accuracy, or photogrammetry-scan quality. The smaller upper roll and newly visible oval cheek relief are real mesh changes, but the final lip/chin silhouette has pronounced angular defects. Passing geometry checks does not resolve these visual failures. This review does not authorize owner acceptance, the increased triangle budget, merge, C2, FishFactory, or release.

## Evidence inspected

On 2026-10-12 the independent reviewer inspected the actual pixels of all **11 final candidate renders and 11 matched baseline renders**: seven primary color views, one supplemental open three-quarter view, and three uniform-matte views per candidate. The seven primary views are full-body lateral, left mouth, right mouth, frontal mouth, top snout, front three-quarter, and a temporary 25° lower-jaw opening. Primary and supplemental color images are 1600 × 1000 at 128 Cycles samples; the matte images are 1200 × 750 at 32 samples. Cameras and neutral lighting are fixed within each comparison; denoising is disabled. The [final browser screenshot](evidence/c1/jaw/final-touchup/largemouth-bass-browser.png) and all four private photographic references were also inspected directly.

The side/three-quarter adult photograph, Stock 306335267, supports the smooth blunt snout, rounded maxillary overlap and continuous lower jaw. The frontal Stock 512226129 supports a broad arched lip and deep convex chin. Stock 482505893 supports fleshy oral rims and cavity walls, while its hand-forced extreme opening is not a resting-pose or angle target. Stock 381475146 corroborates black-bass form but does not independently establish largemouth identity. See [reference provenance and limits](C1_JAW_REFERENCES.md). No stock pixels were copied into this review or the product.

Earlier diagnostics and the withdrawn compressed candidate are not the basis of this final verdict. The findings below concern the frozen identity in the table at the end of this review.

## Final anatomy findings

| Requirement | Finding in the frozen final images | Assessment |
| --- | --- | --- |
| Rounded, integrated upper snout and lip; remove the oversized tube | The broad v2 roll is smaller, and the top/front contour has more curvature. However, both [left](evidence/c1/jaw/final-touchup/after/close_left_mouth.png) and [right](evidence/c1/jaw/final-touchup/after/close_right_mouth.png) profiles show a steep forehead dropping into a concave saddle, then stacked pointed edges at the muzzle. The [front](evidence/c1/jaw/final-touchup/after/front_mouth.png) and [three-quarter](evidence/c1/jaw/final-touchup/after/front_three_quarter_head.png) views show two ridges separated by a recessed band. These do not form the continuous fleshy transition seen in the photographs. | **Fails.** Reducing the tube introduced or exposed other conspicuous contour defects. |
| Rounded rear maxillary plate below and behind the eye, with a natural mouth corner | An oval relief is now clearly visible below/behind the eye, an improvement over the indistinct v2 wedge. Its raised, sharply bounded pad-like form is still weakly integrated with the lip/cheek. The left dark mouth slot retains an abrupt squared posterior ending; the right ending remains a fine taper. The opening still terminates in a sharp triangular rear junction. | **Partly improved; requirement still fails.** The visible oval is not sufficient while its relationship to the mouth corner remains constructed. |
| Rounded lower lip and chin with a continuous oral cavity; no cap, shelf or flat inner panel | The lower jaw has substantial volume, and the [open three-quarter](evidence/c1/jaw/final-touchup/supplemental-open/after/jaw_open_25deg.png) shows an actual recessed cavity. Nevertheless, the front jaw remains a separately readable cap with a horizontal groove below the lip. Both resting side views expose a deep notch and angular ventral return beneath the projecting lip. The [open side](evidence/c1/jaw/final-touchup/after/jaw_open_25deg.png) makes the stepped anterior profile particularly clear. The front oral floor is broad and shallow, with a sharp edge into the exterior instead of a continuous rounded tissue turn. | **Fails.** Cavity depth and chin mass are present, but their integration is not anatomically convincing. |

The [matte side](evidence/c1/jaw/final-touchup/clay/after/close_right_mouth.png), [matte three-quarter](evidence/c1/jaw/final-touchup/clay/after/front_three_quarter_head.png), and [matte opening](evidence/c1/jaw/final-touchup/clay/after/jaw_open_25deg.png) retain these defects without the skin material. They are therefore geometry/silhouette findings, not merely an impression caused by the texture. The pointed tip and lower notch are visible even in the [full-body render](evidence/c1/jaw/final-touchup/after/full_body_lateral.png).

The actual v2 baseline has an oversized upper cap, but its anterior side outline is smoother than this final candidate. A blanket claim that the final touchup improves the face would be inaccurate. The owner's concern about the face becoming shorter/flatter is not answered simply by retaining its maximum forward coordinate: the measured hinge-to-front proxy is nearly unchanged, about 59.7 mm before and 59.6 mm after, while the distribution of snout volume and its silhouette have changed substantially. This proxy is not an anatomical measurement.

Procedural scale repetition, block-like head texture patches and constructed eye rims also remain visible. They reinforce the absence of scan-like surface fidelity, although the jaw defects alone are sufficient for this HOLD.

## Technical validity and budget

The completed [primary QA report](evidence/c1/jaw/final-touchup/jaw-qa-report.json), [supplemental report](evidence/c1/jaw/final-touchup/supplemental-open/jaw-qa-report.json), [matte report](evidence/c1/jaw/final-touchup/clay/jaw-qa-report.json), and [Blender geometry report](evidence/c1/jaw/final-touchup/blender-geometry-validation.json) pass their stated gates. They record closed, outward, finite body geometry; no loose vertices, invalid UVs, zero-area faces or inconsistent winding; and zero detected strict upper/lower or intra-jaw crossings at rest and at 25°. Fin geometry and 3,024 indexed noncranial body positions through authoring X ≤ 0.13 match the regenerated baseline. The reviewer additionally compared final fin fingerprints with the historical v2 report; they match.

These intersection checks exclude shared-vertex pairs and do not classify coplanar contact or enclosed volumes. They are not exhaustive intersection proof or an anatomical test. The weighted lower-jaw rotation is a temporary fixture with a fixed upper head; it does not establish natural maxillary rotation, premaxillary protrusion, hyoid movement, a production rig or animation. The selected vertex-band aperture estimates are 3.06 mm at rest and 26.41 mm in the fixture, not calibrated biological landmarks.

| Property | Final value |
| --- | --- |
| Triangles | **22,238 — unapproved** |
| Exported / source vertices | 15,212 / 11,387 |
| Draw calls / embedded maps | Nine / five |
| Khronos validation | Zero errors, zero warnings |
| Skinned meshes / animation clips | Zero / zero |
| Authored total length | Approximately 0.4524 m |

Cap simplification removes 676 triangles while cheek support adds 660: the net saving is **16 triangles, or 0.072%**, versus the preceding unapproved 22,254. This is local topology reallocation with negligible overall reduction. It remains **11,262 triangles above the owner's 10,976 reference**. Neither this review nor nine draw calls/five maps approves that increase or establishes population, iPhone/Safari, memory or thermal performance.

## CAD and scan-quality standard

**The requested standards are not met.** Visually, the final anatomical and surface defects prevent a photogrammetry-scan-quality recommendation. Quantitatively, the evidence cannot establish CAD-grade accuracy: these are four uncalibrated photographs of different fish, with varying perspective, pose and lighting, no common scale or metric ground truth, no measured landmark tolerances and no registered reference surface. A procedural mesh and an authored length do not supply those missing measurements. There is no photogrammetric reconstruction or validated scan against which to report surface error or detail fidelity. The reviewer can assess photographed form cues and technical validity; this evidence does not support a metric accuracy or scan-equivalence claim.

## Identity and baseline provenance

The reviewer independently verified the hashes and byte counts of 44 manifest entries covering available assets/sources, reports, preserved images, exact archived baseline sources and private references. All 14 newly generated render hashes match their completed QA reports: seven final primary, one final supplemental, and six matte comparisons. The eight historical baseline color images match their preserved identities and original report hashes. No mismatch was found. The [manifest](evidence/c1/jaw/final-touchup/manifest.json) contains the complete image-level ledger.

| Frozen final artifact | SHA-256 |
| --- | --- |
| GLB | `3704933e5084246765a78b28f5c0e6aa4a903f88b54d668717ceea88574c9260` |
| Blender source | `fb99d5471c7324f2d016fa913253b6eba4b77dc0695c08760a5953fcd71272ea` |
| Generator | `76ebbf0c419afc50313c1308beeec5608a01c5123ec32670b85ecc3ec832c367` |
| Material source | `bc2cd6b1ab8248b09154cf6003c16bf41ece93aade4755cc5352c69b72568a7f` |
| Primary QA report | `27894b5d3191b9be30331f2cff02f9714dcb6b71447b9691f237a104340775b3` |
| Supplemental QA report | `582f12d8e6482dda5d87628d03e5ee1df0293721a1fc9e114ac567a6790e47c4` |
| Matte QA report | `ea9779674fa8489b6845c8a95395d4f9fa997f640d5b689144d6dbae4e492d3c` |
| Browser report | `c08b5175417a5ef32a45a6cc9cdd8b6064197098cba2aca76d9c0b4c5cd26481` |

The eight baseline **color** images are verbatim historical v2 pixels, originally bound to Blender hash `ab420964c487658ebb7223a0cbf068844f74f6f9dc3b457908891e70fe511fa2`. They were not rerendered from the rebuilt file. Exact archived v2 generator/material hashes match the historical record; the regenerated baseline Blender hash is `c35fc9ac979074f6400918c9d18c54c5296936c667da90b064281de081658ac3`. That rebuilt file is the geometry-check baseline and the source of the three new baseline matte renders. Primary/supplemental QA deliberately have empty baseline render lists under `--skip-before-renders`; their rebuilt input identity does not rebind the historical color pixels. The historical GLB/Blend identities are preserved provenance, not a claim that their original binaries were available for a new direct hash check.

**Disposition: preserve this as the failed final touchup candidate and its reviewable evidence. C1 stays NOT ACCEPTED pending explicit owner approval; no further remodeling, merge, C2 or FishFactory is authorized by this review.**

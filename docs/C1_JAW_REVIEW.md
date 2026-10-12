# C1 jaw reconstruction — independent review

**Final independent recommendation: HOLD — the requested anatomical reconstruction remains incomplete.** The frozen second-pass candidate fixes the detected jaw self-crossings, replaces the folded anterior edge with a continuous rounded rim and retains a substantial lower jaw with a recessed oral cavity. Its muzzle, maxillary termination and lower oral tip still look constructed in the final close-ups. Technical validity and improvement do not establish photographic realism or owner acceptance. C1 remains open; C2, FishFactory, merge and release are outside this review.

## Final evidence and identity

This review covers the frozen iteration-9 candidate generated on 2026-10-12, not the earlier diagnostics. The reviewer directly inspected all seven final 1600 × 1000, 128-sample Cycles images and their matched baseline counterparts: [full-body lateral](evidence/c1/jaw/after/full_body_lateral.png), [left mouth](evidence/c1/jaw/after/close_left_mouth.png), [right mouth](evidence/c1/jaw/after/close_right_mouth.png), [front mouth](evidence/c1/jaw/after/front_mouth.png), [top snout/jaw](evidence/c1/jaw/after/top_snout_jaw.png), [front three-quarter](evidence/c1/jaw/after/front_three_quarter_head.png) and [25° opening](evidence/c1/jaw/after/jaw_open_25deg.png). The [supplemental open three-quarter](evidence/c1/jaw/supplemental-open/after/jaw_open_25deg.png), its [matched baseline](evidence/c1/jaw/supplemental-open/before/jaw_open_25deg.png), and the actual [Three.js screenshot](evidence/c1/jaw/largemouth-bass-browser.png) were also inspected. The paired Blender views use fixed orthographic cameras and neutral white lighting, without denoising.

All four local reference photographs were inspected as actual pixels. Stock 306335267 supplies the nearly closed adult side/three-quarter head; Stock 512226129 supplies the frontal mandible; Stock 482505893 exposes the open lip/cavity structure but has a hand-forced gape. Stock 381475146 corroborates black-bass form but does not independently establish largemouth identity. Their provenance and limitations are in [C1_JAW_REFERENCES.md](C1_JAW_REFERENCES.md). No unviewed external figure is being treated as pixel-inspected evidence.

The reviewer independently checked all 14 primary image hashes, both supplemental image hashes and both Blender input hashes against the completed QA reports. The final GLB, Blender source, generator and material source independently match the [browser report](evidence/c1/jaw/browser-validation.json). These identities bind the findings to the exported candidate:

| Final artifact | SHA-256 |
| --- | --- |
| `anatomical-revision-v2/largemouth-bass.glb` | `a4a2dfe6c1b7d0210ca4a7ac1b293f8e28a9f51f1a003c65380eeed3d9170ea0` |
| `anatomical-revision-v2/largemouth-bass.blend` | `ab420964c487658ebb7223a0cbf068844f74f6f9dc3b457908891e70fe511fa2` |
| `generate_bass.py` | `c239936c2a37fac66e7413354c3579971948c88899ae7a93840ffeff0072986e` |
| `bass_materials.py` | `bc2cd6b1ab8248b09154cf6003c16bf41ece93aade4755cc5352c69b72568a7f` |
| Primary QA report | `4074884aa1e59c10ea0cd82bff66f61cbc6df34443c1563eaa6fd20494fdca29` |
| Supplemental QA report | `a62e1867ebec30f6853317c51b56f3962fc786c13ffee8c0988d57ef6721ca06` |
| Head self-crossing regression report | `abea5703ff267a44171d014386c4f80c94db78a7d99f9817b747d8fa1a9f21fd` |
| Browser report | `b62d96af1afc68dbfe29c2acb5d5738926c14f83aa1fa5c74af1506ed66340b6` |
| Browser screenshot | `4dc0ae1048686cfb8097220539d423faf14f7fa6d45c9c025cd2f9cc7adf69d4` |

## Final anatomical assessment

The final candidate makes genuine mesh changes. The upper anterior rim is now rounded and continuous; the former thin folded tip is gone. The side opening follows a curved, varying line and reaches behind the eye. The lower jaw has substantial chin volume and moves as a whole in the temporary opening fixture. The supplemental open view shows recessed roof/floor surfaces and a bowl-like interior. These are meaningful corrections, rather than a painted mouth or a detached flat flap.

The following requirements remain unresolved in the frozen final images:

| Priority | Final evidence | Remaining correction |
| --- | --- | --- |
| High | **Muzzle and upper lip remain mechanically shaped.** Front and three-quarter views show an oversized, tube-like projecting roll across the muzzle. Side views expose a blunt planar anterior face, and the top view shows an almost straight front edge with squared turns. | Integrate the premaxillary roll into the photographed rounded snout, with a continuous curved plan silhouette and less uniform projection. The new volume fixes the fold but does not yet match the natural lip proportions in Stock 306335267/512226129. |
| High | **The terminal maxilla and mouth corner remain weak.** The side/three-quarter cheek is still dominated by a smooth wedge. A rounded oblong maxillary termination is not clearly readable below and behind the eye. The left view shows an abruptly squared-off posterior dark slot; the opposite view tapers to a fine point. The three-quarter seam also has an angular kink. | Resolve the softly overlapping maxillary plate and its rounded posterior return into the cheek, as visible in Stock 306335267. Reaching behind the eye is necessary but does not by itself establish that form. |
| High | **The lower lip/chin transition and open tip remain cap-like.** The front view has a broad shelf above a dark concavity. The side silhouette steps angularly beneath the front lip. In the supplemental opening, the lower jaw ends in a broad pale, flat-looking inner panel, while the posterior opening pinches into a sharp triangular junction. | Preserve the substantial jaw mass while making its lip, chin and lateral return one rounded anatomical form. Stock 512226129 supplies the convex frontal mandible; Stock 482505893 supplies rim thickness and oral-wall transitions, not the required resting angle. |

The frontal resting aperture still reads as a nearly horizontal dark band, despite the better side curvature. The small browser fish demonstrates successful export and consistent appearance; it cannot overturn these close-up findings. Procedural scale repetition, block-like head texture patches and constructed eye rims remain visible, but they are not the basis of this jaw HOLD and cannot be solved by changing the jaw's texture alone.

## Final technical result and budget

The [primary QA report](evidence/c1/jaw/jaw-qa-report.json) and [expanded self-crossing regression](evidence/c1/jaw/head-self-regression.json) report zero detected strict upper-versus-lower, intra-upper and intra-lower triangle crossings in both the neutral pose and the temporary 25° opening. The reviewer checked the final Blender hash against both reports. Closed/outward body geometry, finite coordinates/normals/UVs and zero reported loose vertices, zero-area faces or winding defects pass. Fin-position hashes match the preceding checkpoint.

| Property | Final measured value |
| --- | --- |
| Export geometry | 22,254 triangles; 15,203 exported vertices |
| Source geometry | 11,395 vertices; 16 mesh objects |
| Runtime materials/calls | Nine primitives; nine Three.js draw calls |
| Embedded maps | Five decoded: three 1024² skin maps and two 512² maps, including the shared pectoral/iris atlas |
| Khronos validation | Zero errors; zero warnings |
| Skinning/animation | Zero skinned meshes; zero clips |
| Authored length | Approximately 0.4525 m |
| Central-band aperture estimate | 1.85 mm at rest; 24.68 mm at the tested 25° opening |

The crossing method excludes shared-vertex pairs and does not classify coplanar contacts or enclosed volumes; zero detected strict crossings is not exhaustive intersection proof. The aperture is a selected vertex-band measurement, not an anatomical landmark annotation. The fixture tests a weighted lower-jaw rotation with a fixed upper head. It does not validate natural maxillary rotation, premaxillary protrusion, hyoid motion, a feeding sequence, a production rig or swimming animation.

The owner's **10,976 triangles / 11 draw calls / five maps** remains the reference budget. The final **22,254-triangle asset is an explicit, unapproved proposal**, 492 triangles above the immediate 21,762-triangle pre-jaw/first-pass checkpoint and 11,278 above the owner's reference. Added lip/cap topology therefore supersedes the first pass's no-triangle-increase statement. Nine calls and five maps do not approve the triangle increase or establish population, iPhone/Safari, memory or thermal performance.

## Decision

The final candidate is a technically repaired, reviewable C1 asset. **The independent reviewer withholds an anatomical-realism recommendation for the specific remaining forms above.** The owner has not accepted its appearance or increased budget. Do not mark C1 complete, describe the jaw correction as fully achieved, start C2/FishFactory, merge or release on this review.

## Preserved first-pass review history

The following record concerns the earlier, superseded first jaw revision. Its identities and findings are retained so its narrower technical checks are not confused with the expanded final result above.

## First jaw revision: inspected evidence

On 2026-10-12 the independent reviewer inspected the actual pixels of all four local photographs identified in [C1_JAW_REFERENCES.md](C1_JAW_REFERENCES.md), both versions of the seven-view primary comparison under `artifacts/c1/anatomical-revision/jaw-qa/`, and the candidate Three.js screenshot. Each primary image is 1600 × 1000 at 128 Cycles samples, with fixed cameras and neutral lighting. The seven views are full-body lateral, close left mouth, close right mouth, front mouth, top snout/jaw, front three-quarter head and a temporary 25° lower-jaw opening. Left/right filenames were corrected to authoring +Y-left before the final report hashes were checked; no image pixels were changed by that correction.

All 14 primary render hashes and both input Blender hashes independently matched the completed `jaw-qa-report.json`. The GLB, Blender file, generator and material-source hashes independently matched the candidate browser report. The first-pass identity is recorded below so these findings cannot be silently attributed to a later model.

| First-pass artifact | SHA-256 |
| --- | --- |
| Candidate GLB | `850617dca1cdd5c5a036299299f5607acb2030b04d46981a601111b269175b05` |
| Candidate Blender file | `52a9149f1fbde497e037c30402fab4f5cc9afa7ebac8d07dbe2f19e2bd065db7` |
| `generate_bass.py` | `00a7e5b8c8b84423de1ef45be87e6b2388a85754ac370446cbc45212f8851b0e` |
| `bass_materials.py` | `bc2cd6b1ab8248b09154cf6003c16bf41ece93aade4755cc5352c69b72568a7f` |
| Completed primary QA report | `1525f45a764dd2a61d736c356c62b5850a8afd9196665d9253f66c4ef2e8f80f` |

## First-pass anatomy findings

| Priority | Direct visual finding | Photograph-based correction |
| --- | --- | --- |
| High | Both side crops retain a long, almost straight diagonal mouth seam that tapers to a needle-like posterior point. The upper surface reads as a smooth wedge; its rounded maxillary termination remains indistinct. The seam does extend behind the eye, but that endpoint alone does not establish the missing anatomical form. | Stock 306335267 shows a softly rounded oblong maxillary plate below and aft of the eye, with a discernible overlap and return into the cheek. Resolve that volume and its lower/posterior boundary in the mesh. |
| High | The final front-three-quarter crop shows a pinched, angular anterior upper lip with a thin, fold-like edge across the muzzle. The frontal view shows greater projection, but the fleshy roll does not remain continuous around the front. | Stock 482505893 shows a thick, rounded upper rim turning continuously into the maxillary side wall. Preserve an ordered, rounded transition from exterior skin over the lip into the oral roof. Its hand-forced gape is not a resting-pose target. |
| High | The lower jaw has real depth and a substantial chin, but its frontal lip still reads as a broad shelf over a dark concavity, with sharply tucked lateral corners. In the opening fixture, the oral rim remains long and slab-like, ending in a sharply triangular rear opening. | Stock 512226129 shows a continuously convex lower front/chin mass; Stock 306335267 shows its rounded side return into the head. Shape the lip, chin and cheek junction together rather than simply increasing bulk. |

The revised top view confirms a broader projecting snout, and the matched views confirm actual geometric changes. The open fixture confirms that a substantial lower-jaw mass moves, rather than a detached thin flap. These are improvements, but the neutral close-ups still fail the specific continuous-lip and maxillary-form requirements. A second geometry pass was requested on that evidence. Repeated scales, rectangular head texture patches and constructed eye rims are also visible; they are not substitutes for fixing the jaw and are not the basis of the jaw HOLD.

The reviewer also inspected both supplemental 1600 × 1000, 128-sample open three-quarter images in `jaw-qa/supplemental-open/`. These show actual roof/floor separation and a bowl-like lower interior, so the mouth is not just a painted dark line. They also reveal the unresolved thin angular upper oral edge, a sharp floor-to-exterior edge on the lower jaw and a needle-like posterior closure. Compared with the open-mouth photograph, the missing form is the fleshy rim and rounded tissue transition around that cavity. The hand-held reference does not establish the required opening angle.

## First-pass technical result and limits

The candidate browser report records 21,762 triangles, 14,951 exported vertices, nine material primitives/nine draw calls, five successfully decoded embedded maps, zero skinned meshes and zero animation clips. Khronos validation records zero errors and zero warnings. The independent jaw checks find closed, outward, finite body geometry and zero strict upper/lower triangle crossings in both the resting pose and the temporary 25° fixture. Fin-position hashes match the preceding checkpoint.

The crossing check excludes shared-vertex pairs and does not classify coplanar contacts, enclosed volumes or every same-region surface fold. It therefore cannot rule out the angular upper-lip appearance seen in the images. The central-band aperture estimate changes from −1.63 mm to +21.25 mm in the fixture; the negative resting value is a projected overlap of separately selected vertex bands, not proof of penetration. The fixture rotates weighted lower-jaw vertices; it does not establish natural maxillary rotation, premaxillary protrusion, hyoid motion or a production rig.

**Subsequent expanded testing found a real technical defect in the first pass.** `artifacts/c1/anatomical-revision-v2/head-self-regression.json` adds separate upper- and lower-jaw self-overlap checks. For the first-pass Blender identity above, it records 63 strict upper-jaw self-crossings at rest and at 25°, plus 16 lower-jaw self-crossings at 25°. The preserved pre-jaw baseline already has 54 upper-jaw self-crossings. These are distinct from the earlier zero *upper-versus-lower* crossings, and show why that earlier result was insufficient. The revised final candidate must be checked with the expanded method as well as visually. Shared-vertex exclusions, coplanar contacts and enclosed volumes remain limitations of the expanded method.

The owner's **10,976 triangles / 11 draw calls / five maps** remains the budget reference. **21,762 triangles is an explicit, unapproved budget proposal.** Its equality to the immediate pre-jaw checkpoint does not approve the earlier increase. Nine calls and five maps do not establish iPhone/Safari or population performance.

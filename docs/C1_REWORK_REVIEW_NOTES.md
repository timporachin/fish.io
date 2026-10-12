# C1 photographic rework — independent review notes

This is a working review checklist, not an acceptance record. The previous candidate was rejected by the owner. C1 remains open; no merge, C2 work, or visual acceptance follows from technical validation.

## Evidence inspected before rework

The reviewer directly viewed all three local photographic references listed in [C1_PHOTO_REFERENCES.md](C1_PHOTO_REFERENCES.md), along with the rejected candidate's left and front three-quarter views in `evidence/c1/before/`. These observations therefore come from image pixels rather than source descriptions alone.

| Region | Photographic observation and review criterion |
| --- | --- |
| Proportions | In the nearly complete profile, the head ends approximately 26% of visible total length behind the snout and the eye is approximately 8% behind it. Maximum trunk depth is approximately 25% of that visible length; peduncle depth is approximately 11%. Perspective and the slightly clipped tail prevent treating these as exact species measurements. |
| Snout and jaw | Blunt rounded snout, projecting fleshy lower lip, mouth corner behind and below the eye, and curved transitions into cheek and operculum. The rejected candidate's long wedge head and separate straight jaw strip must be absent. |
| Front cross-section | Broad arched forehead, slightly projecting high lateral eyes, raised-center upper lip arch, and substantial rounded lower jaw/chin. Avoid a circular pipe mouth or tiny slit attached to an otherwise undifferentiated tube. |
| Gill region | Several curved anatomical planes with a restrained rear rim, terminating just ahead of the pectoral attachment. Avoid a large flat elliptical badge or floating plate edges. |
| Body skin | Individually legible overlapping scales with small gold/olive centers and darker crescent boundaries. Approximately 55–70 visible columns between gill and peduncle in the profile provide a rough texture-frequency target. Broad cloudy noise must remain secondary. Head plate detail should be regionally distinct from trunk scales. |
| Lateral marking | Connected and separated dark blotches with irregular short downward extensions, softened edges, and stronger contrast on the middle/rear flank. Avoid evenly spaced rectangular stamps or a clean painted stripe. |
| Fins | Thin radial fans with narrow attachments, gently curved membranes, restrained ray relief and variable edge silhouettes. Pectoral opacity and leaf-like rigidity, pelvic folds, and an excessively regular spinous dorsal were major rejected-candidate defects. |
| Lighting | The full-profile photograph's cyan cast is underwater illumination, not the desired literal albedo. Compare material response in both studio renders and the actual Three.js GLB screenshot. |

## Final review requirements

- Inspect all six final Blender images individually, including the perspective view; inspect the before/after comparison and final Three.js screenshot.
- Check the generated `.blend` and `.glb` hashes against their validation evidence and record the exact reviewed artifacts.
- Assess anatomy and surface continuity independently of mesh/export validity. Structural validation cannot establish realistic silhouette, skin, or fin appearance.
- Correct clear remaining blockers before handing the candidate back for owner inspection. Record unresolved limits candidly without treating a technical pass as visual acceptance.
- Preserve the distinction between preparation for later rig development and demonstrated deformation; no rig, animation, or physical iPhone performance is authorized or proved by this review.

## Corrective review during rework

The reviewer inspected intermediate side, front and three-quarter renders and returned specific changes to the anatomy author. Confirmed corrections include a shorter photographic head proportion, forward eye placement, a continuous branched jaw instead of overlay strips, a shallower caudal notch, an integrated gill rim, broader muzzle and a shared upward bow in the closed mouth seam. A bright forehead stripe was traced by the author to discontinuous upper-jaw UVs and removed; the reviewer's initial cap-material hypothesis was superseded by that verified cause. Pectoral outer-margin curvature was also requested and must be checked in the final set.

The refreshed front diagnostic clears the identified UV stripe, excessive muzzle pinching and horizontal mouth-seam defects. This is a narrow finding about those defects, not approval of overall realism. The final material, all six views, runtime GLB and frozen artifact hashes remain the basis for the final independent review.

Further photographic corrections moved the shoulder's fullness forward, lowered and resized the eye, shortened the mouth to the measured photographic corner landmark, and thinned the eye rim. The large dorsal white band was isolated with a no-specular diagnostic and addressed through material calibration and smaller studio lights. The rejected baseline was rerendered under those same lights for a fair comparison.

The first complete rework set exposed a lower-lip diamond/fold in the front view. A clay render confirmed geometry, rather than pigment alone, caused the defect. Independent source inspection identified that the cap's intermediate rings could overshoot the terminal center, creating a central recess. The anatomy author replaced the cumulative rings with convex elliptical interpolation from the original boundary. A fresh clay front was inspected and confirmed that the central fold was removed; terminal pigment cleanup then followed separately. This is why final review hashes must come from the corrected complete generation, not the earlier six-view set or intermediate test run.

## Owner-requested second refinement

The owner requested another refinement after the first rework's production HOLD. That candidate and its review are archived under `evidence/c1/rework-1/`; its approval status is unchanged.

The reviewer reopened the actual photographic pixels, including enlarged analysis crops, and identified three concrete next corrections:

1. The outer opercular margin in the full-profile photograph bends forward under the cheek. The existing near-straight crease instead moves backward at its lower end. A shield-shaped curved rim in the continuous skin should replace that path.
2. A separate preopercular J-shaped border encloses a broad flatter cheek plane ahead of the outer gill rim. The existing summed smooth bulges do not resolve this plane break. The maxillary strip below the eye must transition into a rounded posterior mass near the mouth corner, then into that cheek plane.
3. Fin rays and intervening membrane need differential curvature and slight slack, with finer distal branching. The current mostly ruled strips remain too uniform even after transparency and material improvement.

The close-head photograph also shows a dark bronze/olive iris with a thin gold ring immediately around the black pupil, rather than a uniformly pale iris. Head and fin refinements should be assessed in clay and in the final PBR material; preserve the validated connected jaw, rounded cap and terminal UV fixes while improving anatomy.

### Second-refinement geometry handoff

The reviewer inspected all six 32-sample diagnostic views after the cheek-plane and fin-camber changes, and compared the side and three-quarter views with the archived 128-sample first rework and the actual close-head photograph. The continuous opercular sheet and single maxillary contour are a modest visible improvement. The front cap remains convex without radial pigment bands; the top muzzle remains rounded. No new visible fin folds or cheek corrugations were found in this set. Earlier experiments with additive cheek ridges were rejected and replaced by a lateral plane anchored to the unmodified surface widths at the two photographic curves.

Geometry may be held stable for the combined material pass. This does **not** clear photographic realism or constitute a final review: the unchanged material still draws a near-vertical gill marking across the new curved shield, leaves the cheek insufficiently differentiated, and retains regular scalloped trunk scales and a pale iris. The next useful comparison is this geometry with aligned cranial pigment, broken regional sheen, irregular scale rows and finer fin treatment. Additional plate inflation, ridges or subdivision are not justified before that comparison.

The geometry author reports 17,938 triangles with NR56, 18 mesh objects and 10 materials. That is approximately 25% more triangles than the archived 14,326-triangle first rework; the smaller 19% increase discussed during iteration used an intermediate 15,126-triangle denominator. The proposed 8k near-LOD target remains unmet. These diagnostic views are not frozen final export/runtime validation evidence.

Reviewed diagnostic state (SHA-256):

| File | SHA-256 |
| --- | --- |
| `tools/blender/generate_bass.py` | `6258eed8e7b6d7703c6a4ada47c2baf160dbdf07707b68d8d4b9a5e5bab04c9f` |
| `tools/blender/bass_materials.py` (unchanged first-rework material) | `cfdd172f4de0b7632bf3e6a6b3a8eed8935ef8124de1e2c76dae274f1522ba6f` |
| `artifacts/c1/diagnostic/left.png` | `1679835f8cf63b60d9378b50e9fb682af52c83492ecd737eaf0de1aac505099e` |
| `artifacts/c1/diagnostic/right.png` | `d06123a4447813971dfc26710186fc5ece47d36ff3d3cb8fe38f0e889af11dd7` |
| `artifacts/c1/diagnostic/front.png` | `d64b9fbe2d660c2202217cbd7a8690e74e0078c479b396fbc9f159a71bc47d67` |
| `artifacts/c1/diagnostic/rear.png` | `8c813902e40329e03574c50f84db5639617f16db4f9bf44aab3e0db243254df9` |
| `artifacts/c1/diagnostic/top.png` | `2f97bad1315be5a6b34b8491f948fdc8b27738f59b00effc907b6187c55780dc` |
| `artifacts/c1/diagnostic/front_three_quarter.png` | `90b34ed7bd734a46781f5ee8151c6e0fd56c30befec5119dc6b72f691e11e90c` |

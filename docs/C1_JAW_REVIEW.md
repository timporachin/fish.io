# C1 jaw reconstruction — independent review

**Interim result: HOLD. A second targeted geometry pass is in progress; no final v2 recommendation has been issued.** The first jaw revision improves lip projection and opens as a substantial lower-jaw volume, but it does not yet resolve the owner's anatomical concerns. Its technical passes do not establish visual acceptance. C1 remains open; C2, FishFactory, merge and release are outside this review.

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

## Pending final review

Review the second pass first in early neutral or clay close-ups, then against a frozen matched render set, exported-model screenshot and matching reports. The final decision must address the photographed anatomical forms directly. Technical validity, a larger mesh or improvement over a rejected model must not be presented as owner acceptance.

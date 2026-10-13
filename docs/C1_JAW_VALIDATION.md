# C1 final-touchup validation

**C1 NOT ACCEPTED.** These are technical results for the frozen final touchup. They do not establish anatomical acceptance, CAD dimensional accuracy or photogrammetry scan quality. See the [independent final review](C1_JAW_FINAL_REVIEW.md) and [comparison evidence](C1_JAW_COMPARISONS.md). Draft PR #2 stays unmerged.

| Check | Final result |
| --- | --- |
| GLB / Khronos | Zero errors, zero warnings; 13 informational messages |
| Runtime geometry | 22,238 triangles; 15,212 exported vertices; one mesh, nine primitives and nine Three.js draw calls |
| Maps | Five decoded embedded images: three 1024² body maps, two 512² maps, shared pectoral/iris atlas |
| Source | 11,387 vertices; 16 authored mesh objects; connected body has 5,355 vertices and 10,706 triangles |
| Authored length | Approximately 0.452403 m |
| Source geometry | Closed, outward-facing and finite; no reported loose vertices, zero-area faces or winding failures |
| Head crossings | Zero detected strict intra-upper, intra-lower and cross-jaw crossings, both at rest and at 25° |
| Preservation | Every fin geometry fingerprint and the indexed rear-body positions at X ≤ 0.13 m match the rebuilt v2 source |
| Aperture proxy | 3.06 mm at rest; 26.41 mm in the 25° temporary deformation |
| Rig / animation | Zero skins, zero skinned meshes and zero clips |
| Asset bytes | GLB 3,906,464; Blender 5,023,436 |
| Application checks | Production build, six unit tests and two browser tests pass |

The unchanged existing suites exercise corrupt GLB, unexpected skin/animation, empty mesh, split atlas, missing parts and invalid geometry cases within their implemented scope. Neither source nor runtime assertions have been relaxed. Final source, asset and image hashes are recorded in the [manifest](evidence/c1/jaw/final-touchup/manifest.json) and the linked raw reports.

## Geometry cost assessment

The owner's reference remains **10,976 triangles / 11 draw calls / five maps**. The final **22,238 / nine / five** is an unapproved proposal, 11,262 triangles (+102.61%) above that reference. It is only 16 triangles (0.0719%) below the previous unapproved 22,254 candidate. Four cap sections and both fan centers are removed (676 triangles), while local cheek support adds 660 triangles. This is a different allocation of almost the same overall cost, not a meaningful population-performance optimization. Cheek support addresses sparse sampling of the anatomical return; added density does not by itself establish that the resulting form is correct. No altered fin or rear-body topology is passed off as unchanged.

No LOD, compression, thermal test, iPhone/Safari measurement, scan-to-mesh deviation report or calibrated dimensional tolerance exists for this candidate. The five-map full-mip RGBA8 arithmetic remains approximately 18.67 MiB, not measured GPU residency. Six final fish would contribute 133,428 triangles and 54 calls; eight would contribute 177,904 triangles and 72 calls before habitat rendering. These are arithmetic costs, not measured performance.

## Evidence identities and limits

The seven new primary candidate images and supplemental open three-quarter are 1600 × 1000 at 128 Cycles samples, fixed orthographic cameras and unchanged neutral lighting, without denoising. The additional uniform-material set is three matched views at 1200 × 750 and 32 samples; its baseline is freshly rendered from regenerated v2 geometry.

Primary before pictures are the verbatim previous v2 after pictures, retaining their original Blender/image identities. The v2 geometry baseline was regenerated from the exact archived generator and material-source hashes for the preservation/crossing checks. Its new `.blend` metadata/file hash is distinct. `--skip-before-renders` leaves `before.renderFiles` empty in the new report; historical baseline-image provenance is separately recorded in the manifest. Do not bind historical pixels to the regenerated file hash.

The strict crossing method excludes shared-vertex pairs and does not classify coplanar contacts or enclosed volumes. The fixture rotates weighted lower-jaw vertices and tests geometry at one angle; it does not validate natural maxillary rotation, premaxillary protrusion, hyoid motion, a production rig or a feeding sequence. Aperture is a selected vertex-band proxy, not a measured landmark. Four uncalibrated photographs of different fish provide form references; they cannot certify CAD accuracy or scan fidelity.

Reproduce asset, runtime checks and render fixtures using [C1 modeling handoff](C1_JAW_MODELING.md). Keep C1 open for owner inspection and explicit approval; no merge, C2 or Fish Factory.

## Superseded v2 validation (historical)

The following retained record belongs to the preceding v2 candidate.

# C1 jaw reconstruction — validation scaffold

**Status: C1 NOT ACCEPTED.** The frozen v2 asset has passed the executed format, runtime and strengthened geometry checks below. Astra’s final visual recommendation is HOLD; owner visual and budget approval are pending.

## Comparison points and budget status

| Checkpoint | Triangles | Draw calls / material groups | Maps | Evidence meaning |
| --- | ---: | ---: | ---: | --- |
| Original owner's C1 reference | 10,976 | 11 runtime draw calls | 5 embedded images | Browser/GLB report in `docs/evidence/c1/before/browser-validation.json` |
| Immediate pre-jaw saved source | 21,762 | 9 Blender materials; runtime calls not separately measured in this snapshot | 6 source textures | `artifacts/c1/anatomy-before/largemouth-bass-stats.json`; source inventory, not browser texture cost |
| First jaw pass | 21,762 | 9 runtime draw calls | 5 embedded images | `docs/evidence/c1/jaw/pass-1/browser-validation.json`; diagnostic pass only |
| Frozen v2 proposal | 22,254 | 9 runtime draw calls | 5 embedded images | Frozen browser/GLB reports; visual acceptance and budget approval pending |

The 22,254-triangle v2 count is an **unapproved production budget increase** over the original 10,976-triangle reference. Nine first-pass draw calls and five embedded maps do not approve that increase. The pre-jaw count of six describes Blender source textures; it is not an exported embedded-image count. LODs, compression, multi-fish scenes, device GPU time, memory residency, thermal behavior and physical iPhone/Safari performance remain unqualified.

## Executed frozen-candidate results

Executed in the existing cloud environment on 2026-10-12 with Blender 4.3.2 and Three.js 0.180.0. The authored asset has 11,525 polygon faces (5,377 in the connected body/head), 11,395 vertices and 22,254 triangulated faces. The exported GLB has one mesh, nine material primitives, 15,203 exported vertices and 22,254 triangles. The pinned Khronos validator records zero errors, zero warnings and 13 informational messages. Three.js/Chromium renders nine draw calls and decodes all five images; it finds zero skinned meshes and zero animation clips. Independent Blender validation has zero failures. Corrupt/empty/animated/skinned/missing-part and split-atlas negative cases pass within the implemented suites.

The strengthened head check finds zero strict upper, lower and cross-jaw crossings in the rest pose and temporary 25° fixture. Both are closed, outward-facing and finite. The central-band aperture proxy increases from 1.85 mm at rest to 24.68 mm in the 25° fixture; the 59.7 mm hinge-to-front span is a depth proxy, not a measured anatomical cavity landmark. Every fin-position fingerprint and the rear-body vertex-position fingerprint (authoring X ≤ 0.13 m) match the saved baseline. This is a narrower claim than whole-mesh collision freedom. The added self-crossing check exposed defects missed by the old cross-jaw-only gate; its regression report retains those historical findings rather than retroactively claiming the old assets passed it.

The model is 0.45251 m long. Five images are three 1024² body maps and two 512² fin/iris maps. Estimated full-mip RGBA8 residency is 18.67 MiB, not measured GPU residency. GLB size is 3,906,132 bytes; Blender file is 5,026,060 bytes. The generator SHA is `c239936c2a37fac66e7413354c3579971948c88899ae7a93840ffeff0072986e`; the material-source SHA is `bc2cd6b1ab8248b09154cf6003c16bf41ece93aade4755cc5352c69b72568a7f`. Final evidence manifests identify the exact asset/image bytes.

The additional 492 triangles over the saved 21,762-triangle model are allocated to local lip/interior/cap loops. Overall, 22,254 is 11,278 triangles above the original 10,976 reference (+102.75%). This is a proposal for review, not an adopted production budget. Six full-detail fish would contribute 133,524 triangles and 54 calls; eight would contribute 178,032 triangles and 72 calls before habitat rendering. Those are arithmetic costs, not population benchmarks. LODs and physical iPhone/Safari profiling remain open; no device frame rate is claimed.

## Reproduce the machine checks

Generate and test the v2 candidate from the repository root. npm runs the test script from `tools/blender`; the `../../artifacts/` path after `--` is passed to `test_bass.mjs` as its positional GLB input:

```sh
blender --background --python-exit-code 1 --python tools/blender/generate_bass.py -- --seed 1947 --output artifacts/c1/anatomical-revision-v2 --skip-renders
npm run test:bass --prefix tools/blender -- ../../artifacts/c1/anatomical-revision-v2/largemouth-bass.glb
```

The test writes `artifacts/c1/anatomical-revision-v2/browser-validation.json` and `blender-geometry-validation.json`. Record from them the Khronos error/warning counts, GLB primitives and embedded images, browser decoded images, browser triangles and draw calls, and geometry failures. Keep source/asset hashes with the final evidence manifest. These checks establish format, connectivity, winding, finite geometry, decoded textures and runtime loading within their implemented scope. They do not prove anatomical resemblance, attractive shading, a usable C2 jaw rig, or device performance.

Run the seven matched camera views with the baseline report and the separate supplemental camera using the exact commands in [C1 jaw modeling](C1_JAW_MODELING.md). The seven image names are `full_body_lateral`, `close_left_mouth`, `close_right_mouth`, `front_mouth`, `top_snout_jaw`, `front_three_quarter_head`, and `jaw_open_25deg`. The supplemental pair uses `jaw_open_25deg.png` under `supplemental-open/before/` and `supplemental-open/after/`. Each render report records input hashes, image hashes, geometry measurements and limitations. After-only mode checks the preserved before asset and images against the prior report before producing candidate renders.

The jaw fixture tests a **weighted 25° lower-jaw rotation** around a posterior hinge. Its estimated central-lip aperture and hinge-to-front span are QA proxies. Strict intra-upper, intra-lower and upper/lower triangle-crossing checks exclude triangles sharing vertices and do not classify coplanar contacts or enclosed volumes. A zero-crossing result therefore is narrower than full collision freedom. The temporary rotation is not an animation clip, skin or C2 rig; maximum biological gape is not established by it.

## Final review and evidence

Inspect the private local HTML from `python tools/blender/build_jaw_gallery.py --qa-dir artifacts/c1/anatomical-revision-v2/jaw-qa` against the three photographs in `artifacts/c1/references/`. The side photo guides the closed mouth seam and maxillary endpoint; the frontal photo guides lip width and chin depth. The open photo shows cavity and mandible volume but its lower lip is pulled by a hand, so its extreme angle must not become the resting pose. See [C1 jaw references](C1_JAW_REFERENCES.md) for source and rights details.

The committed evidence package is `docs/evidence/c1/jaw/{before,after,supplemental-open/}` with reports and hashes beside the permitted renders. Keep the raw stock photos and gallery in ignored artifacts. The independent [C1 jaw review](C1_JAW_REVIEW.md) assesses the final v2 silhouette, both mouth corners, frontal thickness, three-quarter depth, the 25° test pose, and the mouth cavity. It records unresolved visual defects and a HOLD decision separate from machine checks. Owner approval of the visual result and the higher geometry budget remains pending.

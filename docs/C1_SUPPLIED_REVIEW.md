# C1 supplied largemouth bass — independent review

**Recommendation: present this frozen candidate for owner review as the stronger anatomical starting point. C1 remains NOT ACCEPTED.** The supplied model resolves much of the conspicuously constructed jaw appearance documented in the [procedural review](C1_JAW_REVIEW.md), and the reduction preserves its adult largemouth silhouette within the original asset budget. Full photographic realism, deformation readiness and owner acceptance are not established by the technical checks.

## Inspected evidence and identity

On 2026-10-12 the reviewer directly inspected all nine final source images, all seven final static candidate images, and the weighted candidate's two opening images plus its dorsal-root image. The final normalized comparison renders are 1600 × 1000, 32-sample Cycles images without denoising. Camera/light distances and light sizes scale with fish length; lamp wattage scales with the square of length to keep approximate irradiance comparable. The source uses its original high-resolution maps, while the candidate uses the final reduced maps. These are strong white inspection lights, so the lower-light [profile](evidence/c1/supplied/candidate-profile.png), [head close-up](evidence/c1/supplied/candidate-head-close.png), three-quarter/front previews and actual browser image were also directly inspected. Earlier mismatched-illumination diagnostic images are not the basis of this final comparison.

The reviewer viewed the actual local pixels of Stock 306335267 (adult side/three-quarter), Stock 512226129 (front) and Stock 482505893 (hand-forced opening), with the provenance and limitations recorded in [C1_JAW_REFERENCES.md](C1_JAW_REFERENCES.md). The prior procedural front and three-quarter close-ups were also inspected. The same-camera 2048² profile and head previews were compared with the frozen 1024²/512² version to bound texture loss.

All 25 image hashes in the source/static/weighted render reports were independently recomputed and matched; this hash check includes weighted rest views beyond the 19 final views visually inspected above. The three render-input hashes matched the actual source, static and weighted Blender files. The runtime GLB hash matched the preparation report. The following independently computed identities bind this review to the frozen artifacts:

| Artifact | SHA-256 |
| --- | --- |
| Static GLB | `b2476193bb8b79431e3ab15596b660ed0297e5bf7f3f0e5394d85e04bb44a7eb` |
| Static Blender | `0be1f4cdea04ef070bec30c926b4fe86c9368d62938716de8a01962f34c215e6` |
| Weighted QA Blender | `7d4fb93ab4851bb5a632d32c51c3d5d20754c6442115c77322924c6a1089eec4` |
| Source render report | `c366dfacb0a0545ebf15134c14777415a8a9d97ac7319075abf6bf5381c06b75` |
| Static candidate render report | `4f563f8dc5209930c7ba65c5a0e9ef25abf625ba93c04e894e20d1320549f746` |
| Weighted candidate render report | `620ff5ecc9f665a7bc6d88b6d3ca79b33e64c416635796bf4cce80fc62fcece2` |
| Browser QA report | `da9610c305b3b92a0ffcb5606f0e21f13deaefeae06b267855119dc994dc1bad` |
| Geometry QA report | `ceba32e29a4b63983de806d3364c80c7931ea708b7602b7bf313e18fd42d9c49` |
| Mouth QA report | `db360ed40b7418d6b6dec6b2136610693e1496d48d2dcdc400eae0b7a0b77d2f` |
| Weighted/static equivalence | `e310f8fadfe3487e8eb2375fa30f6bff38dbdd1a49c8ff44fcfd81d29058d1ce` |

## Direct visual findings

The adult head reads substantially better: the upper lip turns around a rounded snout, the lower lip belongs to a substantial projecting chin, and the oblong maxillary termination is readable below and behind the eye. The side opening has depth and a curved anatomical return. The front view shows an arched aperture and convex lower jaw, and the top view has a rounded plan silhouette. These are meaningful improvements over the previous tube-like upper muzzle, weak maxillary termination and shelf-like lower front.

The full-body lateral view has a deep, substantial forebody and a progressively narrower rear body ending at the caudal peduncle. The dorsal outline, gill cover, pectoral position and lower-jaw projection support adult largemouth identification. Forebody and rear are visibly different in mass and taper. This is a visual assessment, not a morphometric species determination or evidence of natural left/right asymmetry; the source uses mirrored construction.

The [left](evidence/c1/supplied/qa-candidate/close_left_mouth.png), [right](evidence/c1/supplied/qa-candidate/close_right_mouth.png), [front](evidence/c1/supplied/qa-candidate/front_mouth.png), [top](evidence/c1/supplied/qa-candidate/top_snout_jaw.png) and [three-quarter](evidence/c1/supplied/qa-candidate/front_three_quarter_head.png) views retain the source's principal forms after reduction. The following limitations remain visible:

| Finding | Evidence and practical significance |
| --- | --- |
| Short centerline mark on the upper snout/lip | A dark vertical seam is visible in the reduced candidate's front/top close-ups and is less evident in the matched source. Its precise material/normal/geometry cause is unproven. It is much less conspicuous at full-body and browser scale, but should not be described as a seamless close-up finish. |
| Softened fine detail | The 1024² maps preserve the mottling, lateral marking, gill cover and principal head landmarks, while reducing scale and skin detail at inspection distance. Same-camera 2048² previews retain more fine detail. The 512² fin color/opacity image is a deliberate budget tradeoff; these images do not establish unlimited close-up fidelity. |
| Fin material remains model-like | The dorsal, anal and tail fins retain broad, opaque-looking ribs in the lower-light previews and browser view. This appearance also exists in the 2048² comparison, so it cannot all be attributed to the final texture reduction. The photographs show finer rays and more translucent membranes. Exported alpha support alone does not prove a convincing living-fin appearance. |
| Fin-root finish is uneven | Dorsal and anal roots blend into the body at full-body scale, and the pectoral emerges from a plausible attachment behind the gill cover. A rough, dark/light patch remains at the pectoral attachment. The dorsal transition has a very thin, pinched web/rim in close inspection; its open boundary is confirmed by topology QA. This does not establish that every fin root is naturally finished or deformation-safe. |

The lower-light candidate previews show subdued olive/grey coloration and irregular mottling. The bright white QA rig makes both the source and candidate pale. That matched appearance is not sufficient evidence of a defective color texture, and underwater reference photographs cannot supply an exact neutral color target. The overall surface still reads more matte and specimen-like than the living reference fish; wet surface response and membrane appearance remain matters for owner review under the intended presentation lighting. The [actual browser screenshot](evidence/c1/supplied/browser-qa.png) confirms that the silhouette and major markings survive GLB export at its displayed size.

## Mouth depth and temporary opening

The [temporary opening](evidence/c1/supplied/qa-weighted/jaw_open_25deg.png) exposes an actual recessed oral pocket with a continuous lip and lower interior surface. The substantial lower jaw moves together. This is materially stronger evidence than a painted dark mouth line or a detached flat flap. The section plots show the inner surfaces returning into a rounded rear pocket; they do not establish a complete pharynx or feeding anatomy.

The opening belongs to a separate QA-only weighted checkpoint. The runtime GLB is static and contains no skin or animation clip. The [mesh-equivalence report](evidence/c1/supplied/qa/weighted-static-equivalence.json) records identical polygon index order and a maximum body-coordinate residual of approximately 2.02 × 10⁻⁸ m after the known rotation, uniform scale and translation. This connects the tested reduced surface to the static candidate, rather than relying on equal triangle counts alone.

At the recorded source-coordinate section, the reduced mesh's inner gap changes from 5.770 to 24.971 mm when the existing jaw bone rotates −25°; the unreduced source changes from 5.767 to 25.059 mm. These are section measurements in the QA checkpoint's source scale, not direct landmark measurements of the rescaled 0.45 m runtime fish. The test does not validate maxillary rotation, premaxillary protrusion, hyoid motion, swimming deformation or a production rig. The hand-forced open-mouth reference establishes visible rim/interior structure, not the required resting pose or opening angle.

## Technical result and limits

The reviewer inspected the [geometry report](evidence/c1/supplied/qa/candidate-geometry-qa.json), [mouth report](evidence/c1/supplied/qa/candidate-mouth-qa.json), [browser report](evidence/c1/supplied/qa/browser-qa.json), [Khronos result](evidence/c1/supplied/qa/glb-validator-qa.json) and the equivalence report. The frozen candidate has 10,724 triangles, three measured draw calls, two materials and four decoded images: three 1024² maps and one 512² map. This fits the original 10,976-triangle / 11-call / five-image reference. The estimated RGBA8 footprint with mipmaps is 17.33 MiB; it is not measured GPU memory. The GLB is 2,097,516 bytes and approximately 0.45 m long. Browser loading succeeds, a deliberately truncated GLB is rejected, and Khronos validation reports zero errors and warnings.

Finite positions, zero-area faces, loose geometry and winding checks pass in the reports. The body nevertheless retains 64 boundary edges: two 26-edge eye-socket loops covered by separate eye cups and a 12-edge dorsal web/rim. Each eye cup also has a 16-edge attachment boundary. **The assembly is not a watertight single solid.** The dorsal boundary and the decimated triangle layout remain limitations for future deformation work.

The combined anterior head checks include jaw-transition faces and report zero strict nonadjacent triangle crossings at rest and at the temporary opening. They cover 2,274 and 2,272 triangles respectively. Shared-vertex pairs and coplanar contact are excluded; the defined head region does not cover the complete fish. This is bounded evidence against detected head crossings, not an exhaustive intersection or deformation guarantee. Desktop Chromium/SwiftShader loading does not establish physical iPhone/Safari performance, population frame rate, thermal behavior or transparent-fin sorting during motion.

## Decision

The evidence supports using this supplied asset as the preferred candidate for the owner's C1 decision. It preserves a more convincing adult largemouth head, mouth and body than the procedural checkpoint while meeting the original measured asset-cost limits. The remaining centerline seam, close-up texture loss, fin membrane/root finish and topology limitations are disclosed above. **Keep C1 open until the owner accepts the appearance. Do not infer C2 authorization, merge approval or release approval from this review.** Source attribution and the authorized personal/noncommercial scope remain documented in [C1_SUPPLIED_ASSET.md](C1_SUPPLIED_ASSET.md).

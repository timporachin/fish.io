# C1 supplied bass: visual review evidence

**C1 NOT ACCEPTED.** This is an attributed personal, noncommercial adaptation of DigitalLife3D Model 67A, not an original model authored from scratch. The compared procedural checkpoint at `cc12202` remains preserved, along with the separately archived final touchup at `9d4dcb2`. See [source and changes](C1_SUPPLIED_ASSET.md), [validation](C1_SUPPLIED_VALIDATION.md), [Astra review](C1_SUPPLIED_REVIEW.md) and [creator/license notice](third-party/DigitalLife3D-Model67A-NOTICE.md).

## Seven matched anatomical views

| View | Full-resolution supplied baseline | Reduced candidate |
| --- | --- | --- |
| Full-body lateral | [Before](evidence/c1/supplied/qa-source/full_body_lateral.png) | [Candidate](evidence/c1/supplied/qa-candidate/full_body_lateral.png) |
| Left mouth profile | [Before](evidence/c1/supplied/qa-source/close_left_mouth.png) | [Candidate](evidence/c1/supplied/qa-candidate/close_left_mouth.png) |
| Right mouth profile | [Before](evidence/c1/supplied/qa-source/close_right_mouth.png) | [Candidate](evidence/c1/supplied/qa-candidate/close_right_mouth.png) |
| Front mouth | [Before](evidence/c1/supplied/qa-source/front_mouth.png) | [Candidate](evidence/c1/supplied/qa-candidate/front_mouth.png) |
| Top snout/jaw | [Before](evidence/c1/supplied/qa-source/top_snout_jaw.png) | [Candidate](evidence/c1/supplied/qa-candidate/top_snout_jaw.png) |
| Front three-quarter head | [Before](evidence/c1/supplied/qa-source/front_three_quarter_head.png) | [Candidate](evidence/c1/supplied/qa-candidate/front_three_quarter_head.png) |
| Temporary jaw opening | [Before](evidence/c1/supplied/qa-source/jaw_open_25deg.png) | [Exact reduced QA mesh](evidence/c1/supplied/qa-weighted/jaw_open_25deg.png) |

The supplied-source baseline is rendered with repaired texture paths, the existing Principled material reconnected and appropriate image color spaces; the original file remains unchanged. The candidate additionally uses reduced geometry/textures and baked fin opacity. The opening uses the existing source jaw bone in a private weighted QA snapshot, whose surface correspondence to the static candidate is verified. It is not a runtime animation or C2 asset.

The 1600 × 1000, 32-sample Cycles images use identical relative cameras, area-light directions/sizes and neutral color management. Lights and cameras scale with fish length; light power scales by squared length to match irradiance. Both models therefore appear at matching relative scale despite different authoring units. Bright inspection lighting makes small geometry changes visible but washes out skin color; it is not the sole material-quality evidence.

## Material and fin evidence

The [lower-light neutral three-quarter](evidence/c1/supplied/candidate-three-quarter.png), [head close-up](evidence/c1/supplied/candidate-head-close.png) and [actual Three.js loading screenshot](evidence/c1/supplied/browser-qa.png) show the candidate's olive/grey mottling under other documented neutral lighting. These are supplemental views, not substitutes for the matched camera comparisons. The [dorsal-root inspection](evidence/c1/supplied/qa-candidate/dorsal_root.png) and [open three-quarter test](evidence/c1/supplied/qa-weighted/jaw_open_three_quarter.png) expose the fin transition and mouth interior.

The private portable HTML gallery under `artifacts/c1/supplied-candidate/qa-gallery/jaw-comparison.html` places real adult largemouth photographs beside each relevant before/after pair. Original photographic sources and perspective/forced-gape limitations remain documented in [jaw references](C1_JAW_REFERENCES.md). Raw licensed photographs and the embedded private gallery are ignored and are not published in the repository.

## Previous rejected C1 versus supplied candidate

The saved rejected procedural `.blend` is also rendered through the same camera/light normalization for six direct neutral comparisons. These show the change in anatomical starting point, not changes made to the supplied source alone:

| View | Rejected procedural checkpoint | Supplied candidate |
| --- | --- | --- |
| Full body | [Previous](evidence/c1/supplied/qa-historical/full_body_lateral.png) | [Candidate](evidence/c1/supplied/qa-candidate/full_body_lateral.png) |
| Left mouth | [Previous](evidence/c1/supplied/qa-historical/close_left_mouth.png) | [Candidate](evidence/c1/supplied/qa-candidate/close_left_mouth.png) |
| Right mouth | [Previous](evidence/c1/supplied/qa-historical/close_right_mouth.png) | [Candidate](evidence/c1/supplied/qa-candidate/close_right_mouth.png) |
| Front | [Previous](evidence/c1/supplied/qa-historical/front_mouth.png) | [Candidate](evidence/c1/supplied/qa-candidate/front_mouth.png) |
| Top | [Previous](evidence/c1/supplied/qa-historical/top_snout_jaw.png) | [Candidate](evidence/c1/supplied/qa-candidate/top_snout_jaw.png) |
| Three-quarter | [Previous](evidence/c1/supplied/qa-historical/front_three_quarter_head.png) | [Candidate](evidence/c1/supplied/qa-candidate/front_three_quarter_head.png) |

Different meshes and UVs are intentional. The old and new camera positions share fish-relative framing; this is not an exact world-space overlay or a claim of tissue-landmark correspondence. The owner's visual approval remains required. No merge, C2 or Fish Factory development follows from technical validation.

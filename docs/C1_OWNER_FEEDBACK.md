# C1 owner visual feedback

Feedback intake is **complete**. The owner explicitly said “Feedback finish continue remodel.” Remodeling is authorized against the requirements below; visual acceptance remains pending.

Owner observations are additional acceptance requirements alongside the independent Astra review. They do not replace the C1 visual approval gate.

## Recorded observations

- The fins do not transition smoothly from the body.
- The fins are very thin and look like stick figures.
- The body looks too symmetrical from front to rear: its front has the same shape and angle as its rear. The next pass must distinguish the head/forward shoulder from the rear taper and caudal peduncle, using the owner's feedback alongside photographic references.

## Saved refinement state

The existing C1 development branch and draft PR #2 remain in place. Current source edits are saved in `tools/blender/generate_bass.py` and `tools/blender/bass_materials.py`. The latest head-refinement three-quarter inspection render is under `artifacts/c1/head-finish/`; it is a diagnostic, not a final six-view approval set. The first validated rework remains preserved under `artifacts/c1/rework-1/` and `docs/evidence/c1/rework-1/`.

No visual acceptance, merge, C1 completion or C2 development is authorized by this feedback intake.

## Final-touchup requirements (2026-10-12)

The owner requires removal of the projecting tubular/squared upper lip, reconstruction of the rounded posterior maxillary plate and mouth-corner return, and a rounded lower lip/chin with a continuous oral cavity. Corrections must change the mesh; textures, lighting and camera placement cannot conceal defects. Preserve passing geometry, articulation fixtures, GLB and Three.js checks. The 22,254-triangle proposal is not approved; remove redundant topology where practical.

The owner states: “This will be the last touchup. attempt, the outcome needs to be CAD-grade accuracy and Photogrammetry scan quality.” No calibrated photo set, measured anatomical landmarks, scan or dimensional ground truth is supplied. Passing the existing technical gates cannot certify those accuracy/scan standards.

Further steering: “The renders are getting worst, the face is getting shorter and flatter.” The overcompressed diagnostic candidate is withdrawn and remains only in ignored `artifacts/c1/withdrawn-flat/`. The deliverable must retain the full head length and rounded snout volume while correcting the lips and mouth corner.

The owner requests an independent Astra inspection of the actual final renders and updated full-body/close-up comparisons. Keep C1 open and PR #2 draft and unmerged; stop for owner visual inspection and explicit approval. C2 and Fish Factory remain prohibited.

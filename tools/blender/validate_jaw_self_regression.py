"""Compare strict within-jaw triangle crossings across preserved C1 checkpoints.

Run with Blender 4.3.2. This inspection does not save or export any model.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_jaw_revision as qa


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--first-pass", required=True, type=Path)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = parser.parse_args(argv)
    for path in (args.baseline, args.first_pass, args.candidate):
        if path is not None and not path.is_file():
            parser.error(f"Missing input {path}")
    return args


def inspect(label, path):
    bpy.ops.wm.open_mainfile(filepath=str(path.resolve()))
    body = bpy.data.objects[qa.BODY_NAME]
    neutral = qa.meaningful_head_self_intersections(body)
    neutral_body = qa.source_geometry(body)
    _, pose = qa.open_jaw(body, "before" if label == "baseline" else "after")
    posed = qa.meaningful_head_self_intersections(body)
    posed_body = qa.source_geometry(body)
    return {
        "source": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "jawWeightSource": pose["weightSource"], "poseAngleDegrees": qa.ANGLE_DEG,
        "neutral": {"signedVolumeM3": neutral_body["signedVolumeM3"],
                    "upper": neutral["upper"], "lower": neutral["lower"]},
        "posed": {"signedVolumeM3": posed_body["signedVolumeM3"],
                  "upper": posed["upper"], "lower": posed["lower"]},
    }


def main():
    args = arguments()
    report = {
        "check": "strict-intra-jaw-self-intersection-regression",
        "blenderVersion": bpy.app.version_string,
        "method": "Head FACE anatomical_region 1/2 triangle BVH self-overlap; shared-vertex pairs excluded; strict segment/triangle crossings at 0.01 mm contact tolerance",
        "limitations": ["Coplanar contacts and enclosed volumes are inconclusive; this is not exhaustive self-intersection proof.",
                        "Baseline opening weights are derived from face-region incidence, not an authored articulation."],
    }
    for label, path in (("baseline", args.baseline), ("firstPass", args.first_pass),
                        ("candidate", args.candidate)):
        if path is not None:
            report[label] = inspect(label, path)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("JAW_SELF_REGRESSION " + str(args.output.resolve()))
    for label in ("baseline", "firstPass", "candidate"):
        if label in report:
            print(label, {state: {part: report[label][state][part]["properCrossings"]
                                  for part in ("upper", "lower")} for state in ("neutral", "posed")})


if __name__ == "__main__":
    main()

"""Compare weighted QA checkpoint with the exact static derivative geometry."""

import argparse
import json
from pathlib import Path
import sys

import bpy
import numpy as np


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--candidate", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    weighted_path = bpy.data.filepath
    before = {}
    for name in ("body_mesh", "eye_mesh"):
        obj = bpy.data.objects[name]
        before[name] = {
            "coords": np.array([list(obj.matrix_world @ v.co) for v in obj.data.vertices], dtype=np.float64),
            "faces": [tuple(p.vertices) for p in obj.data.polygons],
        }
    bpy.ops.wm.open_mainfile(filepath=str(a.candidate.resolve()))
    result = {"weighted": weighted_path, "candidate": bpy.data.filepath, "objects": {}}
    for name, old in before.items():
        obj = bpy.data.objects[name]
        new = np.array([list(obj.matrix_world @ v.co) for v in obj.data.vertices], dtype=np.float64)
        faces = [tuple(p.vertices) for p in obj.data.polygons]
        source = old["coords"]
        if source.shape != new.shape:
            raise ValueError(f"{name}: vertex counts differ")
        # Known +90° Z rotation followed by common scale and X recenter.
        rotated = np.column_stack((-source[:, 1], source[:, 0], source[:, 2]))
        design = np.column_stack((rotated, np.ones(len(rotated))))
        coefficients, *_ = np.linalg.lstsq(design, new, rcond=None)
        fitted = design @ coefficients
        errors = np.linalg.norm(new - fitted, axis=1)
        result["objects"][name] = {
            "vertices": len(new), "faces": len(faces),
            "identicalFaceIndexOrder": old["faces"] == faces,
            "affineCoefficients": coefficients.tolist(),
            "maxAffineResidualM": float(max(errors)),
            "meanAffineResidualM": float(np.mean(errors)),
        }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2))
    print("QA_SUPPLIED_EQUIVALENCE", a.output)


if __name__ == "__main__":
    main()

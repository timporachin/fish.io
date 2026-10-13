"""Read-only midline mouth cross sections for both source and static derivative."""

import argparse
import json
from pathlib import Path
import sys

import bpy


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--orientation", choices=("source", "candidate"), required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    obj = bpy.data.objects["body_mesh"]
    for armature in (o for o in bpy.data.objects if o.type == "ARMATURE"):
        armature.data.pose_position = "REST"
        if armature.animation_data:
            armature.animation_data_clear()
    ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = ev.to_mesh()
    mesh.calc_loop_triangles()
    coords = [obj.matrix_world @ v.co for v in mesh.vertices]
    if a.orientation == "source":
        axis, cut, nose_axis = 0, .002, 1
    else:
        axis, cut, nose_axis = 1, .0025, 0
    segments = []
    for tri in mesh.loop_triangles:
        pts = [coords[i] for i in tri.vertices]
        hits = []
        for u, v in ((pts[0], pts[1]), (pts[1], pts[2]), (pts[2], pts[0])):
            d = v[axis] - u[axis]
            if abs(d) < 1e-12:
                continue
            t = (cut - u[axis]) / d
            if 0 <= t <= 1:
                h = u.lerp(v, t)
                hits.append([round(h[nose_axis], 7), round(h.z, 7)])
        if len(hits) == 2 and hits[0] != hits[1]:
            segments.append(hits)
    report = {"source": bpy.data.filepath, "orientation": a.orientation,
              "sectionPlane": {"axis": "X" if axis == 0 else "Y", "valueM": cut},
              "headAxis": "Y (-nose)" if a.orientation == "source" else "X (+nose)",
              "segments": segments}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2))
    ev.to_mesh_clear()
    print("QA_SUPPLIED_SECTION", a.output)


if __name__ == "__main__":
    main()

"""Source-only mouth sections and strict head triangle-crossing QA.

Uses actual evaluated `jaw` vertex-group weights, not the authored C1 region
attribute. The 25-degree pose is temporary in memory and is never saved.
"""

import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


TOL = 1e-5


def options():
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--attach-armature", action="store_true",
                   help="Bind retained armature to weighted decimated checkpoint in memory")
    return p.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])


def strict_crossing(a, b, p, q, r):
    direction = b - a
    normal = (q - p).cross(r - p)
    if normal.length < 1e-12:
        return False
    denominator = normal.dot(direction)
    if abs(denominator) < 1e-12:
        return False
    t = normal.dot(p - a) / denominator
    if direction.length < 2 * TOL or t <= TOL / direction.length or t >= 1 - TOL / direction.length:
        return False
    point = a + t * direction
    v0, v1, v2 = q - p, r - p, point - p
    d00, d01, d11 = v0.dot(v0), v0.dot(v1), v1.dot(v1)
    denom = d00 * d11 - d01 * d01
    if denom < 1e-20:
        return False
    d20, d21 = v2.dot(v0), v2.dot(v1)
    v = (d11 * d20 - d01 * d21) / denom
    w = (d00 * d21 - d01 * d20) / denom
    return min(1 - v - w, v, w) > TOL / max(v0.length, v1.length)


def crossing_report(coords, triangles_a, triangles_b, self_check=False):
    a = BVHTree.FromPolygons(coords, triangles_a, all_triangles=True, epsilon=0)
    # Separate trees are essential: BVHTree.overlap(the_same_tree) returns no
    # pairs in Blender 4.3, even for touching/crossing polygons.
    b = BVHTree.FromPolygons(coords, triangles_b, all_triangles=True, epsilon=0)
    pairs = sorted(set((min(i, j), max(i, j)) if self_check else (i, j)
                       for i, j in a.overlap(b) if not self_check or i != j))
    if self_check:
        pairs = [(i, j) for i, j in pairs if i < j]
    result = []
    shared = 0
    for i, j in pairs:
        av, bv = triangles_a[i], triangles_b[j]
        if set(av) & set(bv):
            shared += 1
            continue
        aa, bb = [coords[k] for k in av], [coords[k] for k in bv]
        if any(strict_crossing(aa[k], aa[(k + 1) % 3], *bb) for k in range(3)) or any(
                strict_crossing(bb[k], bb[(k + 1) % 3], *aa) for k in range(3)):
            result.append((i, j))
    return {"triangleCounts": [len(triangles_a), len(triangles_b)],
            "candidatePairs": len(pairs), "sharedVertexPairsExcluded": shared,
            "strictCrossings": len(result), "firstPairs": result[:12],
            "crossingBounds": [[min(coords[v][axis] for i, j in result for v in triangles_a[i] + triangles_b[j]),
                                max(coords[v][axis] for i, j in result for v in triangles_a[i] + triangles_b[j])]
                               for axis in range(3)] if result else None}


def sections(coords, tris, x):
    segments = []
    for tri in tris:
        pts = [coords[i] for i in tri]
        hits = []
        for p, q in ((pts[0], pts[1]), (pts[1], pts[2]), (pts[2], pts[0])):
            d = q.x - p.x
            if abs(d) < 1e-12:
                continue
            t = (x - p.x) / d
            if 0 <= t <= 1:
                h = p.lerp(q, t)
                hits.append([round(h.y, 7), round(h.z, 7)])
        if len(hits) == 2 and hits[0] != hits[1] and min(h[0] for h in hits) < -.045:
            segments.append(hits)
    return segments


def measure(obj):
    ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = ev.to_mesh()
    mesh.calc_loop_triangles()
    group_id = obj.vertex_groups["jaw"].index
    coords = [obj.matrix_world @ v.co for v in mesh.vertices]
    weights = [next((g.weight for g in v.groups if g.group == group_id), 0) for v in mesh.vertices]
    upper, lower, blend = [], [], []
    all_head = []
    for tri in mesh.loop_triangles:
        indices = tuple(tri.vertices)
        centroid_y = sum(coords[i].y for i in indices) / 3
        if centroid_y >= -.045:
            continue
        all_head.append(indices)
        mean_weight = sum(weights[i] for i in indices) / 3
        (lower if mean_weight >= .6 else upper if mean_weight <= .1 else blend).append(indices)
    combined_head = [tri for tri in all_head if sum(coords[i].y for i in tri) / 3 < -.06235]
    report = {"jawWeightThresholds": {"upperMax": .1, "lowerMin": .6},
              "headRangeY": "less than -0.045m", "headTriangles": len(all_head),
              "upperTriangles": len(upper), "lowerTriangles": len(lower),
              "transitionTrianglesOmittedFromCrossing": len(blend),
              "upperLower": crossing_report(coords, upper, lower),
              "upperSelf": crossing_report(coords, upper, upper, True),
              "lowerSelf": crossing_report(coords, lower, lower, True),
              "combinedHeadRoiYLessThanMinus0p06235M": {
                  "triangles": len(combined_head),
                  "selfCrossing": crossing_report(coords, combined_head, combined_head, True)},
              "midlineSectionAtX0p002M": sections(coords, all_head, .002),
              "midlineSectionAtX0p005M": sections(coords, all_head, .005)}
    ev.to_mesh_clear()
    return report


def main():
    a = options()
    obj = bpy.data.objects["body_mesh"]
    armature = next(o for o in bpy.data.objects if o.type == "ARMATURE" and "jaw" in o.pose.bones)
    if a.attach_armature:
        modifier = obj.modifiers.new("QA-only source jaw binding", "ARMATURE")
        modifier.object = armature
    if obj.animation_data:
        obj.animation_data_clear()
    if armature.animation_data:
        armature.animation_data_clear()
    armature.data.pose_position = "REST"
    bpy.context.view_layer.update()
    neutral = measure(obj)
    armature.data.pose_position = "POSE"
    jaw = armature.pose.bones["jaw"]
    jaw.rotation_mode = "XYZ"
    jaw.rotation_euler.x = math.radians(-25)
    bpy.context.view_layer.update()
    posed = measure(obj)
    report = {"source": bpy.data.filepath, "neutral": neutral, "jawOpen25": posed,
              "poseMethod": "Existing jaw bone local X=-25 degrees; temporary QA pose only",
              "qaArmatureModifierAttached": a.attach_armature,
              "crossingMethod": "BVH overlap with strict segment/triangle interiors, excluding shared-vertex pairs; only head triangles with clear evaluated jaw weight; coplanar contacts and transition triangles inconclusive"}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2))
    print("QA_SUPPLIED_MOUTH", a.output)


if __name__ == "__main__":
    main()

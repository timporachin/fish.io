"""Read-only geometric inventory of the supplied bass and prepared derivatives.

Run with Blender --disable-autoexec and an input .blend. This script never saves
the loaded scene. It reports source/evaluated topology and semantic bone weights
without assuming the custom authored C1 part names or manifold fin sheets.
"""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy


def args():
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--jaw-angle", type=float, default=0.0,
                   help="QA-only pose rotation about jaw bone local X, in degrees")
    return p.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])


def bounds(coords):
    return [[round(min(v[i] for v in coords), 7), round(max(v[i] for v in coords), 7)] for i in range(3)] if coords else None


def group_stats(obj):
    result = {}
    for group in obj.vertex_groups:
        members = []
        for v in obj.data.vertices:
            for assignment in v.groups:
                if assignment.group == group.index and assignment.weight > 1e-5:
                    members.append((v, assignment.weight))
        if members:
            result[group.name] = {
                "vertices": len(members), "fullWeightVertices": sum(w >= .999 for _, w in members),
                "weightSum": round(sum(w for _, w in members), 4),
                "bounds": bounds([obj.matrix_world @ v.co for v, _ in members]),
            }
    return result


def mesh_topology(obj, mesh):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.normal_update()
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    visited = set()
    components = []
    for seed in bm.verts:
        if seed in visited:
            continue
        stack = [seed]
        visited.add(seed)
        verts = []
        while stack:
            v = stack.pop()
            verts.append(v)
            for edge in v.link_edges:
                n = edge.other_vert(v)
                if n not in visited:
                    visited.add(n)
                    stack.append(n)
        vs = set(verts)
        edges = {e for v in verts for e in v.link_edges}
        faces = {f for v in verts for f in v.link_faces}
        boundary = [e for e in edges if len(e.link_faces) == 1]
        components.append({
            "vertices": len(verts), "edges": len(edges), "faces": len(faces),
            "triangles": sum(len(f.verts) - 2 for f in faces),
            "boundaryEdges": len(boundary),
            "nonManifoldEdges": sum(len(e.link_faces) > 2 for e in edges),
            "wireEdges": sum(len(e.link_faces) == 0 for e in edges),
            "windingConflicts": sum(len(e.link_faces) == 2 and not e.is_contiguous for e in edges),
            "bounds": bounds([obj.matrix_world @ v.co for v in verts]),
            "boundaryBounds": bounds([obj.matrix_world @ v.co for e in boundary for v in e.verts]),
        })
    components.sort(key=lambda c: c["triangles"], reverse=True)
    boundary_edges = {e for e in bm.edges if len(e.link_faces) == 1}
    boundary_groups = []
    while boundary_edges:
        stack = [boundary_edges.pop()]
        group = set(stack)
        while stack:
            edge = stack.pop()
            for vertex in edge.verts:
                for other in vertex.link_edges:
                    if other in boundary_edges:
                        boundary_edges.remove(other)
                        group.add(other)
                        stack.append(other)
        vertices = {v for e in group for v in e.verts}
        degree = Counter(v for e in group for v in e.verts)
        weights = Counter()
        for v in vertices:
            for assignment in mesh.vertices[v.index].groups:
                weights[obj.vertex_groups[assignment.group].name] += assignment.weight
        face_normals = [f.normal for e in group for f in e.link_faces]
        boundary_groups.append({"edges": len(group), "vertices": len(vertices),
                                "endpoints": sum(degree[v] == 1 for v in vertices),
                                "branches": sum(degree[v] > 2 for v in vertices),
                                "bounds": bounds([obj.matrix_world @ v.co for v in vertices]),
                                "weightSums": weights.most_common(6),
                                "adjacentFaceNormalBounds": bounds(face_normals)})
    boundary_groups.sort(key=lambda g: g["edges"], reverse=True)
    uv = []
    for layer in mesh.uv_layers:
        values = [tuple(d.uv) for d in layer.data]
        uv.append({"name": layer.name, "loops": len(values),
                   "invalid": sum(not all(math.isfinite(x) for x in v) for v in values),
                   "bounds": bounds([(u, v, 0) for u, v in values])})
    report = {
        "vertices": len(bm.verts), "faces": len(bm.faces),
        "triangles": sum(len(f.verts) - 2 for f in bm.faces),
        "looseVertices": sum(not v.link_edges for v in bm.verts),
        "zeroAreaFaces": sum(f.calc_area() <= 1e-12 for f in bm.faces),
        "invalidVertices": sum(not all(math.isfinite(x) for x in v.co) for v in bm.verts),
        "components": components, "boundaryGroups": boundary_groups, "uvLayers": uv,
    }
    bm.free()
    return report


def main():
    opt = args()
    for obj in bpy.data.objects:
        if obj.type == "ARMATURE":
            obj.data.pose_position = "POSE" if opt.jaw_angle else "REST"
        if obj.animation_data:
            obj.animation_data_clear()
    if opt.jaw_angle:
        armature = next((o for o in bpy.data.objects if o.type == "ARMATURE" and "jaw" in o.pose.bones), None)
        if armature is None:
            raise ValueError("QA jaw pose requested but no jaw bone exists")
        jaw = armature.pose.bones["jaw"]
        jaw.rotation_mode = "XYZ"
        jaw.rotation_euler.x = math.radians(opt.jaw_angle)
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    report = {"file": bpy.data.filepath, "qaJawAngleDeg": opt.jaw_angle,
              "objects": {}, "armatures": {}, "images": {}}
    for obj in bpy.data.objects:
        if obj.type == "ARMATURE":
            report["armatures"][obj.name] = {"bones": [{"name": b.name, "head": list(b.head_local),
                "tail": list(b.tail_local), "parent": b.parent.name if b.parent else None} for b in obj.data.bones]}
        elif obj.type == "MESH":
            ev = obj.evaluated_get(deps)
            evaluated_mesh = ev.to_mesh()
            report["objects"][obj.name] = {
                "matrixWorld": [list(row) for row in obj.matrix_world],
                "raw": mesh_topology(obj, obj.data),
                "evaluated": mesh_topology(obj, evaluated_mesh),
                "groups": group_stats(obj),
                "modifiers": [{"type": m.type, "name": m.name,
                    "enabledViewport": m.show_viewport,
                    "levels": m.levels if m.type == "SUBSURF" else None} for m in obj.modifiers],
            }
            ev.to_mesh_clear()
    for image in bpy.data.images:
        report["images"][image.name] = {"size": list(image.size), "path": image.filepath,
            "packed": bool(image.packed_file)}
    opt.output.parent.mkdir(parents=True, exist_ok=True)
    opt.output.write_text(json.dumps(report, indent=2))
    print("QA_SUPPLIED_BASS", opt.output)


if __name__ == "__main__":
    main()

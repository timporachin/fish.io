"""Independent structural checks for the authored Blender bass scene."""
import bmesh
import bpy
import json
import math
from mathutils import Matrix
import os


# Surface seams are deliberate on separate facial plates and fin membranes. The
# body is the watertight volume and must remain closed and outward-facing.
ALLOWED_OPEN_BOUNDARY_PREFIXES = (
    "Upper_lip_", "Upper_mouth_lip_arc", "Mouth_cavity_", "Operculum_plate_", "Dorsal_",
    "Caudal_", "Pectoral_", "Pelvic_", "Anal_fin",
)
REQUIRED_OBJECTS = (
    "Body_quadrilateral_loft", "Lower_mandible_volumetric", "Upper_mouth_lip_arc",
    "Mouth_cavity_left", "Mouth_cavity_right", "Operculum_plate_left", "Operculum_plate_right",
    "Dorsal_spiny_10_spines", "Dorsal_soft_14_rays", "Caudal_rounded_emarginate",
    "Pectoral_left", "Pectoral_right", "Pelvic_left", "Pelvic_right", "Anal_fin", "Fin_rays_combined",
    "Eye_orbit_left", "Eye_orbit_right", "Iris_left", "Iris_right", "Pupil_left", "Pupil_right",
    "Corneal_glint_left", "Corneal_glint_right",
)
EPSILON = 1e-10


def finite_vector(vector):
    return all(math.isfinite(component) for component in vector)


def inspect_bmesh(mesh, matrix_world):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    bm.transform(matrix_world)
    bm.normal_update()

    issues = []
    loose_vertices = sum(1 for vert in bm.verts if not vert.link_edges)
    boundary_edges = sum(1 for edge in bm.edges if len(edge.link_faces) == 1)
    wire_edges = sum(1 for edge in bm.edges if len(edge.link_faces) == 0)
    nonmanifold_edges = sum(1 for edge in bm.edges if len(edge.link_faces) > 2)
    inconsistent_winding_edges = sum(1 for edge in bm.edges if len(edge.link_faces) == 2 and not edge.is_contiguous)
    zero_area_faces = sum(1 for face in bm.faces if not math.isfinite(face.calc_area()) or face.calc_area() <= EPSILON)
    bad_normals = sum(1 for face in bm.faces if not finite_vector(face.normal) or face.normal.length <= EPSILON)
    invalid_vertices = sum(1 for vert in bm.verts if not finite_vector(vert.co) or not finite_vector(vert.normal))
    if loose_vertices:
        issues.append(f"{loose_vertices} loose vertices")
    if wire_edges:
        issues.append(f"{wire_edges} wire edges")
    if nonmanifold_edges:
        issues.append(f"{nonmanifold_edges} edges with more than two faces")
    if inconsistent_winding_edges:
        issues.append(f"{inconsistent_winding_edges} shared edges have inconsistent face winding")
    if zero_area_faces:
        issues.append(f"{zero_area_faces} zero-area faces")
    if bad_normals or invalid_vertices:
        issues.append(f"{bad_normals} invalid face normals and {invalid_vertices} invalid vertices/normals")
    volume = bm.calc_volume(signed=True) if bm.faces else 0.0
    closed = len(bm.faces) > 0 and boundary_edges == 0 and wire_edges == 0 and nonmanifold_edges == 0
    bm.free()
    return {
        "vertices": len(mesh.vertices), "edges": len(mesh.edges), "faces": len(mesh.polygons),
        "looseVertices": loose_vertices, "boundaryEdges": boundary_edges, "wireEdges": wire_edges,
        "nonmanifoldEdges": nonmanifold_edges, "inconsistentWindingEdges": inconsistent_winding_edges,
        "zeroAreaFaces": zero_area_faces,
        "invalidNormalsOrVertices": bad_normals + invalid_vertices, "closed": closed,
        "signedVolumeM3": volume if closed else None, "issues": issues,
    }


def inspect_uvs(mesh):
    uv_count = 0
    invalid = 0
    for layer in mesh.uv_layers:
        for loop in layer.data:
            uv_count += 1
            if not finite_vector(loop.uv):
                invalid += 1
    return uv_count, invalid


def missing_required_objects(object_names):
    return [name for name in REQUIRED_OBJECTS if name not in object_names]


def negative_self_check():
    # A known loose vertex must be rejected by the same geometry inspector.
    mesh = bpy.data.meshes.new("negative-loose-vertex")
    mesh.from_pydata([(0, 0, 0), (1, 0, 0), (0, 1, 0), (9, 9, 9)], [], [(0, 1, 2)])
    mesh.update()
    result = inspect_bmesh(mesh, Matrix.Identity(4))
    bpy.data.meshes.remove(mesh)
    assert any("loose vertices" in issue for issue in result["issues"]), "negative loose-vertex case was not rejected"
    mesh = bpy.data.meshes.new("negative-inconsistent-winding")
    mesh.from_pydata([(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0)], [], [(0, 1, 2), (1, 2, 3)])
    mesh.update()
    result = inspect_bmesh(mesh, Matrix.Identity(4))
    bpy.data.meshes.remove(mesh)
    assert any("inconsistent face winding" in issue for issue in result["issues"]), \
        "negative winding case was not rejected"
    assert "Dorsal_soft_14_rays" in missing_required_objects(set(REQUIRED_OBJECTS) - {"Dorsal_soft_14_rays"}), \
        "negative missing-fin case was not rejected"


negative_self_check()
scene_meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
assert scene_meshes, "No mesh objects were found in the Blender file"
assert bpy.app.version[:3] == (4, 3, 2), f"Blender 4.3.2 is required, found {bpy.app.version_string}"
names = {obj.name for obj in scene_meshes}
missing = missing_required_objects(names)
assert not missing, f"Missing expected anatomical mesh objects: {missing}"

records = []
failures = []
for obj in scene_meshes:
    metrics = inspect_bmesh(obj.data, obj.matrix_world)
    uv_count, invalid_uvs = inspect_uvs(obj.data)
    permitted_open = obj.name.startswith(ALLOWED_OPEN_BOUNDARY_PREFIXES)
    metrics["name"] = obj.name
    metrics["uvLayers"] = len(obj.data.uv_layers)
    metrics["uvLoopCoordinates"] = uv_count
    metrics["invalidUvCoordinates"] = invalid_uvs
    metrics["openBoundaryAllowed"] = permitted_open

    for issue in metrics["issues"]:
        failures.append(f"{obj.name}: {issue}")
    if metrics["boundaryEdges"] and not permitted_open:
        failures.append(f"{obj.name}: {metrics['boundaryEdges']} undeclared open boundary edges")
    if metrics["closed"] and metrics["signedVolumeM3"] is not None and metrics["signedVolumeM3"] <= EPSILON:
        failures.append(f"{obj.name}: closed mesh does not have positive signed volume/outward winding")
    if invalid_uvs:
        failures.append(f"{obj.name}: {invalid_uvs} non-finite UV coordinates")
    if obj.name == "Body_quadrilateral_loft":
        if not metrics["closed"]:
            failures.append(f"{obj.name}: fish body must be a closed manifold volume")
        if metrics["signedVolumeM3"] is not None and metrics["signedVolumeM3"] <= EPSILON:
            failures.append(f"{obj.name}: signed volume is not positive; face winding may point inward")
        if len(obj.data.uv_layers) == 0 or uv_count == 0:
            failures.append(f"{obj.name}: body UV coordinates are missing")
    if obj.name == "Lower_mandible_volumetric":
        if not metrics["closed"]:
            failures.append(f"{obj.name}: lower mandible must be a closed manifold volume")
        if metrics["signedVolumeM3"] is not None and metrics["signedVolumeM3"] <= EPSILON:
            failures.append(f"{obj.name}: signed volume is not positive; face winding may point inward")
    records.append(metrics)

blend_path = bpy.data.filepath
output_path = os.path.join(os.path.dirname(blend_path), "blender-geometry-validation.json")
report = {
    "check": "independent-blender-geometry",
    "blenderVersion": bpy.app.version_string,
    "blend": blend_path,
    "meshObjectCount": len(scene_meshes),
    "requiredAnatomicalObjects": list(REQUIRED_OBJECTS),
    "records": records,
    "failures": failures,
    "negativeCases": ["loose vertex rejected", "inconsistent winding rejected", "missing fin rejected"],
    "limitations": [
        "Positive signed body volume checks overall face winding, not every local inward patch.",
        "This checker does not detect self-intersections, establish anatomical accuracy, or prove deformation quality.",
    ],
}
with open(output_path, "w", encoding="utf-8") as report_file:
    json.dump(report, report_file, indent=2, sort_keys=True)
    report_file.write("\n")
print("GEOMETRY_VALIDATION_REPORT " + output_path)
print(json.dumps(report, indent=2))
if failures:
    raise RuntimeError("Bass geometry validation failed: " + "; ".join(failures))
print("BASS_GEOMETRY_OK")

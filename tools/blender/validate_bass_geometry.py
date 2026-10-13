"""Independent structural checks for the authored Blender bass scene."""
import bmesh
import bpy
import json
import math
from mathutils import Matrix
import os


# The revised authoring contract has one closed, continuous body with upper/lower
# jaw branches. Fins, eyes, and rays are separate closed source meshes.
EXPECTED_SOURCE_MESH_COUNT = 16
REQUIRED_OBJECTS = (
    "Body_quadrilateral_loft",
    "Dorsal_spiny_10_spines", "Dorsal_soft_14_rays", "Caudal_rounded_emarginate",
    "Pectoral_left", "Pectoral_right", "Pelvic_left", "Pelvic_right", "Anal_fin", "Fin_rays_combined",
    "Eye_orbit_left", "Eye_orbit_right", "Iris_left", "Iris_right", "Pupil_left", "Pupil_right",
)
FORBIDDEN_REPLACED_OVERLAYS = {
    "Lower_mandible_volumetric", "Upper_mouth_lip_arc", "Mouth_cavity_left", "Mouth_cavity_right",
    "Operculum_plate_left", "Operculum_plate_right",
}
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
    unseen = set(bm.verts)
    components = []
    while unseen:
        component = {unseen.pop()}
        stack = list(component)
        while stack:
            vertex = stack.pop()
            for edge in vertex.link_edges:
                other = edge.other_vert(vertex)
                if other in unseen:
                    unseen.remove(other)
                    component.add(other)
                    stack.append(other)
        components.append(component)
    component_by_vertex = {vertex: index for index, component in enumerate(components) for vertex in component}
    component_signed_volumes = [0.0 for _ in components]
    for face in bm.faces:
        vertices = list(face.verts)
        component_index = component_by_vertex[vertices[0]]
        origin = vertices[0].co
        for index in range(1, len(vertices) - 1):
            component_signed_volumes[component_index] += origin.dot(
                vertices[index].co.cross(vertices[index + 1].co)) / 6.0
    inward_components = sum(1 for volume in component_signed_volumes if not math.isfinite(volume) or volume <= 0)
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
    if inward_components:
        issues.append(f"{inward_components} connected components have non-positive signed volume/winding")
    volume = bm.calc_volume(signed=True) if bm.faces else 0.0
    closed = len(bm.faces) > 0 and boundary_edges == 0 and wire_edges == 0 and nonmanifold_edges == 0
    bm.free()
    return {
        "vertices": len(mesh.vertices), "edges": len(mesh.edges), "faces": len(mesh.polygons),
        "connectedComponents": len(components),
        "componentSignedVolumesM3": component_signed_volumes,
        "nonPositiveVolumeComponents": inward_components,
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


def inspect_anatomical_regions(mesh):
    attribute = mesh.attributes.get("anatomical_region")
    if attribute is None:
        return {"domain": None, "dataType": None, "counts": {}, "adjacentRegionPairs": [],
                "issues": ["missing anatomical_region face attribute"]}
    issues = []
    if attribute.domain != "FACE":
        issues.append(f"anatomical_region domain must be FACE, found {attribute.domain}")
    if attribute.data_type != "INT":
        issues.append(f"anatomical_region data type must be INT, found {attribute.data_type}")
    values = [item.value for item in attribute.data]
    if len(values) != len(mesh.polygons):
        issues.append(f"anatomical_region has {len(values)} values for {len(mesh.polygons)} polygons")
    unexpected_values = sorted(set(values) - {0, 1, 2})
    if unexpected_values:
        issues.append(f"anatomical_region contains undocumented values {unexpected_values}")
    counts = {str(region): values.count(region) for region in sorted(set(values))}
    for region, label in ((0, "torso"), (1, "upper jaw branch"), (2, "lower jaw branch")):
        if counts.get(str(region), 0) == 0:
            issues.append(f"anatomical_region is missing faces for {label} (value {region})")

    # Prove the semantic regions are physically joined by shared mesh edges.
    edge_regions = {}
    for polygon, region in zip(mesh.polygons, values):
        vertices = list(polygon.vertices)
        for index, vertex in enumerate(vertices):
            edge = tuple(sorted((vertex, vertices[(index + 1) % len(vertices)])))
            edge_regions.setdefault(edge, set()).add(region)
    adjacent_pairs = set()
    for regions in edge_regions.values():
        for left in regions:
            for right in regions:
                if left < right:
                    adjacent_pairs.add((left, right))
    required_pairs = {(0, 1), (0, 2), (1, 2)}
    missing_pairs = sorted(required_pairs - adjacent_pairs)
    if missing_pairs:
        issues.append(f"anatomical regions lack shared-edge joins for {missing_pairs}")
    return {
        "domain": attribute.domain,
        "dataType": attribute.data_type,
        "counts": counts,
        "adjacentRegionPairs": [list(pair) for pair in sorted(adjacent_pairs)],
        "issues": issues,
    }


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
    mesh = bpy.data.meshes.new("negative-missing-jaw-regions")
    mesh.from_pydata([(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0)], [], [(0, 1, 2), (1, 3, 2)])
    mesh.update()
    attribute = mesh.attributes.new("anatomical_region", "INT", "FACE")
    attribute.data[0].value = 0
    attribute.data[1].value = 0
    result = inspect_anatomical_regions(mesh)
    bpy.data.meshes.remove(mesh)
    assert any("upper jaw branch" in issue for issue in result["issues"]), \
        "negative missing-upper-jaw semantic region was not rejected"
    assert any("lower jaw branch" in issue for issue in result["issues"]), \
        "negative missing-lower-jaw semantic region was not rejected"


negative_self_check()
scene_meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
assert scene_meshes, "No mesh objects were found in the Blender file"
assert bpy.app.version[:3] == (4, 3, 2), f"Blender 4.3.2 is required, found {bpy.app.version_string}"
names = {obj.name for obj in scene_meshes}
assert len(scene_meshes) == EXPECTED_SOURCE_MESH_COUNT, \
    f"Expected {EXPECTED_SOURCE_MESH_COUNT} closed source mesh objects, found {len(scene_meshes)}"
stale_overlays = sorted(names & FORBIDDEN_REPLACED_OVERLAYS)
assert not stale_overlays, f"Legacy disconnected jaw/cheek overlays remain: {stale_overlays}"
missing = missing_required_objects(names)
assert not missing, f"Missing expected anatomical mesh objects: {missing}"

records = []
failures = []
for obj in scene_meshes:
    metrics = inspect_bmesh(obj.data, obj.matrix_world)
    uv_count, invalid_uvs = inspect_uvs(obj.data)
    metrics["name"] = obj.name
    metrics["uvLayers"] = len(obj.data.uv_layers)
    metrics["uvLoopCoordinates"] = uv_count
    metrics["invalidUvCoordinates"] = invalid_uvs
    metrics["openBoundaryAllowed"] = False

    for issue in metrics["issues"]:
        failures.append(f"{obj.name}: {issue}")
    if metrics["boundaryEdges"]:
        failures.append(f"{obj.name}: {metrics['boundaryEdges']} undeclared open boundary edges")
    if metrics["closed"] and metrics["signedVolumeM3"] is not None and metrics["signedVolumeM3"] <= EPSILON:
        failures.append(f"{obj.name}: closed mesh does not have positive signed volume/outward winding")
    if not metrics["closed"]:
        failures.append(f"{obj.name}: source mesh must be closed and manifold")
    if invalid_uvs:
        failures.append(f"{obj.name}: {invalid_uvs} non-finite UV coordinates")
    if obj.name == "Body_quadrilateral_loft":
        if not metrics["closed"]:
            failures.append(f"{obj.name}: fish body must be a closed manifold volume")
        if metrics["signedVolumeM3"] is not None and metrics["signedVolumeM3"] <= EPSILON:
            failures.append(f"{obj.name}: signed volume is not positive; face winding may point inward")
        if len(obj.data.uv_layers) == 0 or uv_count == 0:
            failures.append(f"{obj.name}: body UV coordinates are missing")
        if metrics["connectedComponents"] != 1:
            failures.append(f"{obj.name}: body must be one connected component, found {metrics['connectedComponents']}")
        regions = inspect_anatomical_regions(obj.data)
        metrics["anatomicalRegions"] = regions
        for issue in regions["issues"]:
            failures.append(f"{obj.name}: {issue}")
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
    "negativeCases": ["loose vertex rejected", "inconsistent winding rejected", "missing fin rejected",
                      "missing upper/lower jaw semantic regions rejected"],
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

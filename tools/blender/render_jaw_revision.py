"""Matched, neutral anatomical jaw inspection of two frozen C1 Blender files.

Example:
  blender --background --python-exit-code 1 --python tools/blender/render_jaw_revision.py -- \
    --before artifacts/c1/anatomy-before/largemouth-bass.blend \
    --after artifacts/c1/anatomical-revision/largemouth-bass.blend \
    --output-dir artifacts/c1/anatomical-revision/jaw-qa

Only temporary loaded scenes are changed. The source .blend files and GLBs are
never saved over. An articulated .blend is a QA fixture, not a production asset.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


VIEW_NAMES = (
    "full_body_lateral", "close_left_mouth", "close_right_mouth",
    "front_mouth", "top_snout_jaw", "front_three_quarter_head",
    "jaw_open_25deg",
)
ANGLE_DEG = 25.0
BODY_NAME = "Body_quadrilateral_loft"
CONTACT_TOLERANCE_M = 1e-5


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--after", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--views", default=",".join(VIEW_NAMES),
                        help="Comma-separated subset of the seven view names")
    parser.add_argument("--samples", type=int, default=128)
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--height", type=int, default=1000)
    parser.add_argument("--skip-renders", action="store_true")
    parser.add_argument("--skip-before-renders", action="store_true",
                        help="Check rebuilt baseline geometry; use separately preserved baseline image evidence")
    parser.add_argument("--require-geometry-pass", action="store_true",
                        help="Exit nonzero if any revision structural or opening check fails")
    parser.add_argument("--after-only", action="store_true",
                        help="Reuse a hash-verified prior baseline report and render only the revision")
    parser.add_argument("--baseline-report", type=Path,
                        help="Existing matched report required by --after-only")
    parser.add_argument("--open-three-quarter", action="store_true",
                        help="Use supplemental three-quarter camera for the opening view")
    parser.add_argument("--clay", action="store_true",
                        help="Additional geometry-only inspection with uniform matte material")
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = parser.parse_args(argv)
    args.views = tuple(args.views.split(","))
    unknown = set(args.views) - set(VIEW_NAMES)
    if unknown:
        parser.error("Unknown views: " + ", ".join(sorted(unknown)))
    if len(set(args.views)) != len(args.views):
        parser.error("Duplicate view")
    args.views = tuple(view for view in VIEW_NAMES if view in args.views)
    if min(args.samples, args.width, args.height) < 1:
        parser.error("Samples and dimensions must be positive")
    for path in (args.before, args.after):
        if not path.is_file():
            parser.error(f"Missing input: {path}")
    if args.after_only and (args.baseline_report is None or not args.baseline_report.is_file()):
        parser.error("--after-only requires an existing --baseline-report")
    return args


def neutral_scene(scene, args):
    # Remove saved inspection gear only. No mesh, material, texture, or fin edit.
    for obj in list(scene.objects):
        if obj.type in {"LIGHT", "CAMERA"}:
            bpy.data.objects.remove(obj, do_unlink=True)
    scene.render.engine = "CYCLES"
    scene.cycles.samples = args.samples
    scene.cycles.use_denoising = False  # OIDN is unavailable on this build.
    scene.render.resolution_x = args.width
    scene.render.resolution_y = args.height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Base Contrast"
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    world = bpy.data.worlds.new("Jaw QA neutral world")
    scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (.18, .18, .18, 1)
    background.inputs["Strength"].default_value = .45
    for name, xyz, watts, size in (
        ("QA key", (-.04, -.31, .36), 23, .28),
        ("QA fill", (.24, .30, .21), 11, .28),
        ("QA top", (-.15, .10, .40), 16, .23),
        ("QA underside", (.17, -.18, -.20), 4, .30),
    ):
        data = bpy.data.lights.new(name, "AREA")
        data.energy = watts
        data.shape = "DISK"
        data.size = size
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        obj.location = xyz
        obj.rotation_euler = (Vector((.05, 0, .01)) - obj.location).to_track_quat("-Z", "Y").to_euler()
    camera_data = bpy.data.cameras.new("QA matched camera")
    camera = bpy.data.objects.new("QA matched camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    return camera


def frame(camera, view, open_three_quarter=False):
    # Orthographic scales are identical between the two files, including pose.
    # Mouth crops all point at the same anatomical landmark in world space.
    frames = {
        "full_body_lateral": ((-.005, -.78, .028), (-.005, 0, .005), .53),
        "close_left_mouth": ((.16, .39, .034), (.16, 0, .012), .155),
        "close_right_mouth": ((.16, -.39, .034), (.16, 0, .012), .155),
        "front_mouth": ((.49, 0, .018), (.18, 0, .012), .145),
        "top_snout_jaw": ((.168, 0, .48), (.168, 0, .008), .155),
        "front_three_quarter_head": ((.43, -.37, .14), (.155, 0, .013), .175),
        "jaw_open_25deg": ((.16, -.39, .034), (.16, 0, .012), .155),
    }
    if view == "jaw_open_25deg" and open_three_quarter:
        frames[view] = ((.43, -.37, .08), (.175, 0, -.002), .175)
    location, target, scale = frames[view]
    camera.location = location
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = scale
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def region_vertex_sets(mesh):
    region = mesh.attributes.get("anatomical_region")
    if region is None or region.domain != "FACE" or region.data_type != "INT":
        raise ValueError("Body needs FACE/INT anatomical_region for aperture and collision checks")
    result = {0: set(), 1: set(), 2: set()}
    for polygon, datum in zip(mesh.polygons, region.data):
        if datum.value in result:
            result[datum.value].update(polygon.vertices)
    if not result[1] or not result[2]:
        raise ValueError("Upper and lower anatomical regions are required")
    return result


def jaw_weights(body, label):
    mesh = body.data
    attribute = mesh.attributes.get("jaw_open_weight")
    if attribute is not None:
        if attribute.domain != "POINT" or attribute.data_type != "FLOAT":
            raise ValueError("jaw_open_weight must be POINT/FLOAT")
        weights = [item.value for item in attribute.data]
        if len(weights) != len(mesh.vertices) or not all(math.isfinite(w) and 0 <= w <= 1 for w in weights):
            raise ValueError("jaw_open_weight must have one finite [0,1] value per vertex")
        source = "authored POINT/FLOAT jaw_open_weight"
    elif label == "before":
        # The frozen predecessor has no opening weights. This derived fixture
        # tests its geometry at the same angle, and is explicitly not rig proof.
        region = mesh.attributes.get("anatomical_region")
        if region is None or region.domain != "FACE" or region.data_type != "INT":
            raise ValueError("Frozen baseline lacks regions from which to derive jaw weights")
        total = [0] * len(mesh.vertices)
        lower = [0] * len(mesh.vertices)
        for polygon, datum in zip(mesh.polygons, region.data):
            for vi in polygon.vertices:
                total[vi] += 1
                lower[vi] += datum.value == 2
        weights = [n / t if t else 0 for n, t in zip(lower, total)]
        source = "derived from baseline FACE/INT anatomical_region incident-face ratio"
    else:
        raise ValueError("Revision must author POINT/FLOAT jaw_open_weight")
    return weights, source


def source_geometry(body):
    bm = bmesh.new()
    bm.from_mesh(body.data)
    bm.normal_update()
    issues = {
        "looseVertices": sum(not v.link_edges for v in bm.verts),
        "boundaryEdges": sum(len(e.link_faces) == 1 for e in bm.edges),
        "nonManifoldEdges": sum(len(e.link_faces) > 2 for e in bm.edges),
        "inconsistentWindingEdges": sum(len(e.link_faces) == 2 and not e.is_contiguous for e in bm.edges),
        "zeroAreaFaces": sum((not math.isfinite(f.calc_area())) or f.calc_area() <= 1e-10 for f in bm.faces),
        "invalidVertices": sum(not all(math.isfinite(x) for x in v.co) for v in bm.verts),
        "invalidNormals": sum(not all(math.isfinite(x) for x in f.normal) or f.normal.length < 1e-10 for f in bm.faces),
        "signedVolumeM3": bm.calc_volume(signed=True),
    }
    issues["closed"] = issues["boundaryEdges"] == issues["nonManifoldEdges"] == issues["looseVertices"] == 0
    issues["outwardWinding"] = issues["signedVolumeM3"] > 0 and issues["inconsistentWindingEdges"] == 0
    uv_bad = 0
    for layer in body.data.uv_layers:
        uv_bad += sum(not all(math.isfinite(x) for x in item.uv) for item in layer.data)
    issues["invalidUvCoordinates"] = uv_bad
    bm.free()
    return issues


def mesh_digest(obj):
    """Geometry-only fingerprint; textures/material changes cannot affect it."""
    digest = hashlib.sha256()
    for vertex in obj.data.vertices:
        digest.update(struct.pack("<3d", *vertex.co))
    for face in obj.data.polygons:
        digest.update(struct.pack("<I", len(face.vertices)))
        for vi in face.vertices:
            digest.update(struct.pack("<I", vi))
    return digest.hexdigest()


def rear_body_positions(body, max_x=.13):
    """Stable noncranial torso vertices; the jaw and cheek lie forward of this plane."""
    digest = hashlib.sha256()
    count = 0
    for vertex in body.data.vertices:
        if vertex.co.x <= max_x:
            digest.update(struct.pack("<I3d", vertex.index, *vertex.co))
            count += 1
    return {"maxAuthoringX": max_x, "vertexCount": count, "indexedPositionSha256": digest.hexdigest()}


def source_inventory(scene):
    fins = {}
    for obj in scene.objects:
        if obj.type != "MESH":
            continue
        if obj.name.startswith(("Dorsal", "Caudal", "Pectoral", "Pelvic", "Anal", "Fin_rays")):
            fins[obj.name] = {"vertices": len(obj.data.vertices), "triangles": len(obj.data.loop_triangles),
                              "geometrySha256": mesh_digest(obj)}
    body = scene.objects.get(BODY_NAME)
    return {"meshObjects": sum(obj.type == "MESH" for obj in scene.objects), "fins": fins,
            "noncranialBodyPositions": rear_body_positions(body) if body else None}


def lip_aperture(body, hinge_x):
    regions = region_vertex_sets(body.data)
    mesh = body.data
    # Use a narrow, central snout band to exclude far lateral cheek surfaces.
    threshold = max(hinge_x + .035, .194)
    band = .016
    def points(which):
        return [mesh.vertices[i].co for i in regions[which]
                if mesh.vertices[i].co.x >= threshold and abs(mesh.vertices[i].co.y) <= band]
    upper, lower = points(1), points(2)
    if not upper or not lower:
        return {"measurable": False, "reason": "No upper or lower lip vertices in central front band"}
    return {
        "measurable": True,
        "selection": {"minX": threshold, "maxAbsY": band, "upperVertices": len(upper), "lowerVertices": len(lower)},
        "upperLowestZM": min(v.z for v in upper),
        "lowerHighestZM": max(v.z for v in lower),
        "verticalApertureM": min(v.z for v in upper) - max(v.z for v in lower),
        "frontLipXM": max(v.x for v in upper + lower),
        "hingeToFrontDepthM": max(v.x for v in upper + lower) - hinge_x,
    }


def triangle_regions(mesh):
    face_region = mesh.attributes["anatomical_region"].data
    mesh.calc_loop_triangles()
    upper, lower = [], []
    for tri in mesh.loop_triangles:
        value = face_region[tri.polygon_index].value
        if value == 1:
            upper.append(tuple(tri.vertices))
        elif value == 2:
            lower.append(tuple(tri.vertices))
    return upper, lower


def proper_segment_triangle(a, b, p, q, r):
    """Strict interior crossing with meter-scale endpoint/contact tolerance."""
    direction = b - a
    normal = (q - p).cross(r - p)
    normal_length = normal.length
    if normal_length < 1e-12:
        return False
    denominator = normal.dot(direction)
    if abs(denominator) < 1e-12:
        return False  # Coplanar/parallel contacts are deliberately inconclusive.
    t = normal.dot(p - a) / denominator
    length = direction.length
    if length < CONTACT_TOLERANCE_M * 2 or t <= CONTACT_TOLERANCE_M / length or t >= 1 - CONTACT_TOLERANCE_M / length:
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
    u = 1 - v - w
    # Include interior and edge crossings except contacts within tolerance.
    return min(u, v, w) > CONTACT_TOLERANCE_M / max((q-p).length, (r-p).length)


def meaningful_jaw_intersections(body):
    mesh = body.data
    upper, lower = triangle_regions(mesh)
    vertices = [v.co.copy() for v in mesh.vertices]
    if not upper or not lower:
        return {"candidatePairs": 0, "properCrossings": 0, "error": "missing jaw triangles"}
    bvh_u = BVHTree.FromPolygons(vertices, upper, all_triangles=True, epsilon=0)
    bvh_l = BVHTree.FromPolygons(vertices, lower, all_triangles=True, epsilon=0)
    candidates = bvh_u.overlap(bvh_l)
    shared = 0
    crossings = []
    for ui, li in candidates:
        u, l = upper[ui], lower[li]
        if set(u) & set(l):
            shared += 1
            continue  # Continuous junction is an expected shared surface.
        up = [vertices[i] for i in u]
        lo = [vertices[i] for i in l]
        crossed = any(proper_segment_triangle(up[i], up[(i+1)%3], *lo) for i in range(3))
        crossed |= any(proper_segment_triangle(lo[i], lo[(i+1)%3], *up) for i in range(3))
        if crossed:
            crossings.append((ui, li))
    return {
        "upperTriangles": len(upper), "lowerTriangles": len(lower),
        "candidatePairs": len(candidates), "sharedVertexPairsExcluded": shared,
        "properCrossings": len(crossings), "firstCrossingPairs": crossings[:12],
        "crossingVertexBoundsM": {
            axis: [min(vertices[vi][axis] for ui, li in crossings for vi in upper[ui] + lower[li]),
                   max(vertices[vi][axis] for ui, li in crossings for vi in upper[ui] + lower[li])]
            for axis in range(3)
        } if crossings else None,
        "firstCrossingTriangles": {
            "upper": [list(vertices[vi]) for vi in upper[crossings[0][0]]],
            "lower": [list(vertices[vi]) for vi in lower[crossings[0][1]]],
        } if crossings else None,
        "contactToleranceM": CONTACT_TOLERANCE_M,
        "method": "BVH upper/lower overlap, shared-vertex exclusion, strict edge/triangle interior crossings; coplanar contacts inconclusive",
    }


def meaningful_head_self_intersections(body):
    """Detect nonadjacent folded head triangles within each jaw face region."""
    mesh = body.data
    upper, lower = triangle_regions(mesh)
    vertices = [v.co.copy() for v in mesh.vertices]
    result = {}
    for name, triangles in (("upper", upper), ("lower", lower)):
        bvh = BVHTree.FromPolygons(vertices, triangles, all_triangles=True, epsilon=0)
        candidates = bvh.overlap(bvh)
        shared = 0
        crossing_pairs = []
        unique = set()
        for i, j in candidates:
            if i >= j or (i, j) in unique:
                continue
            unique.add((i, j))
            a, b = triangles[i], triangles[j]
            if set(a) & set(b):
                shared += 1
                continue
            av = [vertices[vi] for vi in a]
            bv = [vertices[vi] for vi in b]
            crossed = any(proper_segment_triangle(av[k], av[(k + 1) % 3], *bv) for k in range(3))
            crossed |= any(proper_segment_triangle(bv[k], bv[(k + 1) % 3], *av) for k in range(3))
            if crossed:
                crossing_pairs.append((i, j))
        result[name] = {
            "triangles": len(triangles), "uniqueCandidatePairs": len(unique),
            "sharedVertexPairsExcluded": shared, "properCrossings": len(crossing_pairs),
            "firstCrossingPairs": crossing_pairs[:12],
            "crossingVertexBoundsM": {
                axis: [min(vertices[vi][axis] for i, j in crossing_pairs for vi in triangles[i] + triangles[j]),
                       max(vertices[vi][axis] for i, j in crossing_pairs for vi in triangles[i] + triangles[j])]
                for axis in range(3)
            } if crossing_pairs else None,
            "firstCrossingTriangles": {
                "a": [list(vertices[vi]) for vi in triangles[crossing_pairs[0][0]]],
                "b": [list(vertices[vi]) for vi in triangles[crossing_pairs[0][1]]],
            } if crossing_pairs else None,
        }
    result["method"] = "Separate upper/lower BVH self-overlap; nonadjacent strict segment/triangle crossings only; coplanar contacts and enclosed volumes inconclusive"
    result["contactToleranceM"] = CONTACT_TOLERANCE_M
    return result


def open_jaw(body, label):
    hinge = Vector((float(body.get("jaw_hinge_x", .151)),
                    float(body.get("jaw_hinge_y", 0)),
                    float(body.get("jaw_hinge_z", -.0087))))
    if str(body.get("jaw_open_axis", "Y")) != "Y":
        raise ValueError("QA assumes a Y hinge axis")
    weights, source = jaw_weights(body, label)
    body.data = body.data.copy()
    radians = math.radians(ANGLE_DEG)
    rotation = Vector((0, 1, 0))
    original = [v.co.copy() for v in body.data.vertices]
    rotation_matrix = Matrix.Rotation(radians, 3, rotation)
    for vertex, w in zip(body.data.vertices, weights):
        if w:
            rotated = hinge + rotation_matrix @ (vertex.co - hinge)
            vertex.co = vertex.co.lerp(rotated, w)
    body.data.update()
    max_displacement = max((v.co - old).length for v, old in zip(body.data.vertices, original))
    return hinge, {"angleDegrees": ANGLE_DEG, "maximumTestedOpeningDegrees": ANGLE_DEG,
                   "axis": "+Y", "weightSource": source,
                   "weightedVertices": sum(w > 0 for w in weights),
                   "weightRange": [min(weights), max(weights)],
                   "maxVertexDisplacementM": max_displacement}


def run_one(label, input_path, output, args):
    bpy.ops.wm.open_mainfile(filepath=str(input_path.resolve()))
    scene = bpy.context.scene
    body = bpy.data.objects.get(BODY_NAME)
    if body is None or body.type != "MESH":
        raise RuntimeError(f"{input_path}: missing {BODY_NAME}")
    camera = neutral_scene(scene, args)
    if args.clay:
        clay = bpy.data.materials.new("QA uniform geometry inspection")
        clay.use_nodes = True
        shader = clay.node_tree.nodes.get("Principled BSDF")
        shader.inputs["Base Color"].default_value = (.42,.42,.42,1)
        shader.inputs["Roughness"].default_value = .7
        for obj in scene.objects:
            if obj.type == "MESH":
                for index in range(len(obj.data.materials)):
                    obj.data.materials[index] = clay
    hinge_x = float(body.get("jaw_hinge_x", .151))
    record = {
        "input": str(input_path.resolve()), "inputSha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
        "label": label,
        "sourceInventory": source_inventory(scene),
        "neutral": {"body": source_geometry(body), "mouth": lip_aperture(body, hinge_x),
                    "jawIntersections": meaningful_jaw_intersections(body),
                    "headSelfIntersections": meaningful_head_self_intersections(body)},
        "renderFiles": [], "renderSha256": {},
    }
    label_output = output / label
    label_output.mkdir(parents=True, exist_ok=True)
    for view in args.views:
        frame(camera, view, args.open_three_quarter)
        if view == "jaw_open_25deg":
            hinge, pose = open_jaw(body, label)
            pose["hingeM"] = list(hinge)
            pose["body"] = source_geometry(body)
            pose["mouth"] = lip_aperture(body, hinge.x)
            pose["jawIntersections"] = meaningful_jaw_intersections(body)
            pose["headSelfIntersections"] = meaningful_head_self_intersections(body)
            articulated = label_output / "articulated.blend"
            bpy.ops.wm.save_as_mainfile(filepath=str(articulated), compress=True)
            pose["articulatedBlend"] = str(articulated)
            pose["articulatedSha256"] = hashlib.sha256(articulated.read_bytes()).hexdigest()
            record["posed"] = pose
        if not args.skip_renders:
            path = label_output / f"{view}.png"
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            record["renderFiles"].append(str(path))
            record["renderSha256"][view] = hashlib.sha256(path.read_bytes()).hexdigest()
    return record


def verified_prior_baseline(args):
    prior = json.loads(args.baseline_report.read_text(encoding="utf-8"))
    matching_render_fields = ("width", "height", "cyclesSamples", "views", "lighting", "camera")
    expected = {"width": args.width, "height": args.height, "cyclesSamples": args.samples,
                "views": list(args.views), "lighting": "fixed neutral gray world and four white area lights",
                "camera": "fixed orthographic world-space framing per view"}
    for key in matching_render_fields:
        if prior.get("render", {}).get(key) != expected[key]:
            raise ValueError(f"Prior baseline {key} differs from requested render setup")
    if bool(prior["render"].get("supplementalOpenThreeQuarter", False)) != args.open_three_quarter:
        raise ValueError("Prior baseline opening camera differs from requested render setup")
    mode = "uniform matte geometry inspection" if args.clay else "authored materials"
    if prior["render"].get("materialMode", "authored materials") != mode:
        raise ValueError("Prior baseline material mode differs from requested render setup")
    baseline = prior["before"]
    if hashlib.sha256(args.before.read_bytes()).hexdigest() != baseline["inputSha256"]:
        raise ValueError("Preserved baseline Blender file has changed")
    for name in args.views:
        image = Path(baseline["renderFiles"][list(prior["render"]["views"]).index(name)])
        if not image.is_file() or hashlib.sha256(image.read_bytes()).hexdigest() != baseline["renderSha256"][name]:
            raise ValueError(f"Preserved baseline image {name} is missing or differs from its report hash")
    if "noncranialBodyPositions" not in baseline["sourceInventory"]:
        bpy.ops.wm.open_mainfile(filepath=str(args.before.resolve()))
        body = bpy.data.objects.get(BODY_NAME)
        if body is None:
            raise ValueError("Preserved baseline body mesh is missing")
        baseline["sourceInventory"]["noncranialBodyPositions"] = rear_body_positions(body)
    return baseline


def main():
    args = arguments()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = {
        "check": "matched-neutral-jaw-revision",
        "blenderVersion": bpy.app.version_string,
        "render": {"width": args.width, "height": args.height, "cyclesSamples": args.samples,
                   "denoising": False, "views": args.views, "lighting": "fixed neutral gray world and four white area lights",
                   "camera": "fixed orthographic world-space framing per view",
                   "supplementalOpenThreeQuarter": args.open_three_quarter},
        "limitations": [
            "Baseline opening weights are derived from existing face regions and are a QA fixture, not authored articulation.",
            "A 25-degree weighted vertex rotation is a temporary deformation test, not a rig or animation clip.",
            "BVH strict segment/triangle checks exclude triangles sharing vertices and do not classify coplanar contacts or enclosed volumes.",
            "Intra-jaw self-overlap checks are limited to upper/lower head face regions and are not exhaustive self-intersection proof.",
            "The mouth aperture is a repeatable central-lip vertex-band estimate, not an anatomical landmark annotation.",
            "Hinge-to-front X span is a mouth-depth proxy; maximum tested opening is 25 degrees, not a biological maximum.",
        ],
    }
    report["render"]["materialMode"] = "uniform matte geometry inspection" if args.clay else "authored materials"
    if args.after_only:
        report["before"] = verified_prior_baseline(args)
        report["baselineGalleryReport"] = str(args.baseline_report.resolve())
    else:
        requested_skip = args.skip_renders
        args.skip_renders = requested_skip or args.skip_before_renders
        report["before"] = run_one("before", args.before, output, args)
        args.skip_renders = requested_skip
        report["baselineRendersSkipped"] = args.skip_before_renders
    report["after"] = run_one("after", args.after, output, args)
    baseline_fins = report["before"]["sourceInventory"]["fins"]
    revision_fins = report["after"]["sourceInventory"]["fins"]
    report["comparison"] = {
        "unchangedFinGeometry": baseline_fins == revision_fins,
        "changedFins": sorted(name for name in baseline_fins.keys() | revision_fins.keys()
                              if baseline_fins.get(name) != revision_fins.get(name)),
        "unchangedNoncranialBodyPositions":
            report["before"]["sourceInventory"].get("noncranialBodyPositions") ==
            report["after"]["sourceInventory"].get("noncranialBodyPositions"),
    }
    after = report["after"]
    pose = after.get("posed")
    report["revisionChecks"] = {
        "neutralClosedOutwardFinite": bool(after["neutral"]["body"]["closed"]
                                           and after["neutral"]["body"]["outwardWinding"]
                                           and not after["neutral"]["body"]["invalidVertices"]
                                           and not after["neutral"]["body"]["invalidNormals"]
                                           and not after["neutral"]["body"]["invalidUvCoordinates"]),
        "neutralJawCrossingsZero": after["neutral"]["jawIntersections"]["properCrossings"] == 0,
        "neutralHeadSelfCrossingsZero": all(after["neutral"]["headSelfIntersections"][part]["properCrossings"] == 0
                                            for part in ("upper", "lower")),
        "posedClosedOutwardFinite": None if pose is None else bool(pose["body"]["closed"]
                                                       and pose["body"]["outwardWinding"]
                                                       and not pose["body"]["invalidVertices"]
                                                       and not pose["body"]["invalidNormals"]
                                                       and not pose["body"]["invalidUvCoordinates"]),
        "posedJawCrossingsZero": None if pose is None else pose["jawIntersections"]["properCrossings"] == 0,
        "posedHeadSelfCrossingsZero": None if pose is None else all(
            pose["headSelfIntersections"][part]["properCrossings"] == 0 for part in ("upper", "lower")),
        "openingIncreasesAperture": None if pose is None else (
            pose["mouth"].get("verticalApertureM", float("-inf")) >
            after["neutral"]["mouth"].get("verticalApertureM", float("inf"))),
    }
    report_path = output / "jaw-qa-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("JAW_QA_REPORT " + str(report_path))
    print("REVISION_CHECKS " + json.dumps(report["revisionChecks"], sort_keys=True))
    print("FIN_COMPARISON " + json.dumps(report["comparison"], sort_keys=True))
    if args.require_geometry_pass:
        failed = [name for name, passed in report["revisionChecks"].items() if passed is False]
        if not report["comparison"]["unchangedFinGeometry"]:
            failed.append("unchangedFinGeometry")
        if not report["comparison"]["unchangedNoncranialBodyPositions"]:
            failed.append("unchangedNoncranialBodyPositions")
        if failed:
            raise RuntimeError("Jaw QA geometry checks failed: " + ", ".join(failed))


if __name__ == "__main__":
    main()

"""Render matched source/candidate anatomical views without saving the input .blend.

The source is nose -Y, while the prepared static candidate is nose +X. Camera
positions are defined in nose/lateral/up coordinates and scale with fish length.
The static candidate cannot render an opening. A separate weighted checkpoint
uses the exact decimated mesh with a QA-only temporary source jaw binding.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


VIEWS = ("full_body_lateral", "close_left_mouth", "close_right_mouth",
         "front_mouth", "top_snout_jaw", "front_three_quarter_head",
         "jaw_open_25deg", "jaw_open_three_quarter", "dorsal_root")


def arguments():
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--orientation", choices=("source", "weighted", "candidate"), required=True)
    p.add_argument("--views", default=",".join(VIEWS))
    p.add_argument("--samples", type=int, default=32)
    p.add_argument("--width", type=int, default=1200)
    p.add_argument("--height", type=int, default=800)
    a = p.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    a.views = tuple(v for v in VIEWS if v in a.views.split(","))
    return a


def neutral_setup(a):
    for o in bpy.data.objects:
        if o.animation_data:
            o.animation_data_clear()
        if o.type == "ARMATURE":
            o.data.pose_position = "REST"
    if a.orientation == "source":
        for image in bpy.data.images:
            if image.source == "FILE":
                replacement = Path("/workspace/fish.io/artifacts/c1/user-supplied/original") / Path(image.filepath.replace("\\", "/")).name
                if replacement.is_file():
                    image.filepath = str(replacement)
                    image.reload()
        for mat in bpy.data.materials:
            if not mat.use_nodes:
                continue
            nodes = mat.node_tree.nodes
            output = next((n for n in nodes if n.type == "OUTPUT_MATERIAL"), None)
            principled = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
            if output and principled:
                mat.node_tree.links.new(principled.outputs["BSDF"], output.inputs["Surface"])
            for n in nodes:
                if n.type == "TEX_IMAGE" and n.image:
                    low = n.image.name.lower()
                    if "roughness" in low or "normal" in low or "alpha" in low:
                        n.image.colorspace_settings.name = "Non-Color"
                    elif "color" in low:
                        n.image.colorspace_settings.name = "sRGB"
    for o in list(bpy.context.scene.objects):
        if o.type in ("CAMERA", "LIGHT"):
            bpy.data.objects.remove(o, do_unlink=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = a.samples
    scene.cycles.use_denoising = False
    scene.render.resolution_x = a.width
    scene.render.resolution_y = a.height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Base Contrast"
    scene.view_settings.exposure = 0
    world = bpy.data.worlds.new("Supplied bass QA neutral world")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (.15, .15, .15, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = .45
    scene.world = world
    return scene


def orient(a):
    if a.orientation in ("source", "weighted"):
        return Vector((0, -1, 0)), Vector((1, 0, 0)), Vector((0, 0, 1))
    return Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))


def bbox(a, nose):
    deps = bpy.context.evaluated_depsgraph_get()
    coords = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        ev = obj.evaluated_get(deps)
        mesh = ev.to_mesh()
        coords.extend(obj.matrix_world @ v.co for v in mesh.vertices)
        ev.to_mesh_clear()
    front = max(v.dot(nose) for v in coords)
    back = min(v.dot(nose) for v in coords)
    center = sum(coords, Vector()) / len(coords)
    center += nose * ((front + back) / 2 - center.dot(nose))
    return center, front, front - back


def lights(scene, center, length, nose, side, up):
    # Geometric camera/light setup scales with fish length. Area-light energy
    # scales as distance squared so source and 0.45 m candidate receive the
    # same approximate irradiance despite their different physical scales.
    energy_factor = (length / .45) ** 2
    for name, direction, energy, size in (
        ("key", nose * .3 + side * .9 + up * .9, 17, .5),
        ("fill", nose * .1 - side * .8 + up * .4, 12, .6),
        ("top", nose * -.3 + up * 1.1, 13, .6),
    ):
        data = bpy.data.lights.new("QA " + name, "AREA")
        data.energy = energy * energy_factor
        data.shape = "DISK"
        data.size = size * length
        obj = bpy.data.objects.new("QA " + name, data)
        scene.collection.objects.link(obj)
        obj.location = center + direction * length
        obj.rotation_euler = (center - obj.location).to_track_quat("-Z", "Y").to_euler()


def pose_open():
    armature = next((o for o in bpy.data.objects if o.type == "ARMATURE" and "jaw" in o.pose.bones), None)
    if armature is None:
        raise ValueError("25-degree view requires actual source jaw bone")
    body = bpy.data.objects.get("body_mesh")
    if body and not any(m.type == "ARMATURE" for m in body.modifiers):
        modifier = body.modifiers.new("QA-only source jaw binding", "ARMATURE")
        modifier.object = armature
    armature.data.pose_position = "POSE"
    jaw = armature.pose.bones["jaw"]
    jaw.rotation_mode = "XYZ"
    # Source bone roll makes negative local X lower the mandible in world Z.
    jaw.rotation_euler.x = math.radians(-25)
    bpy.context.view_layer.update()


def frame(camera, name, center, front, length, nose, side, up):
    head = center + nose * (front - .09 * length - center.dot(nose))
    if name == "dorsal_root":
        target = center + up * (.12 * length)
        direction = up + side * .18
        scale = length * .30
    elif name == "full_body_lateral":
        target = center
        direction = side + up * .08
        scale = length * 1.18
    else:
        target = head
        scale = length * (.50 if name in ("front_three_quarter_head", "jaw_open_three_quarter") else .43)
        if name == "close_left_mouth" or name == "jaw_open_25deg":
            direction = side + up * .12
        elif name == "close_right_mouth":
            direction = -side + up * .12
        elif name == "front_mouth":
            direction = nose + up * .03
        elif name == "top_snout_jaw":
            direction = up + nose * .05
        else:
            direction = nose * .72 + side * .80 + up * .32
    camera.location = target + direction.normalized() * length
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = scale
    return {"location": list(camera.location), "target": list(target), "orthoScale": scale}


def main():
    a = arguments()
    a.output_dir.mkdir(parents=True, exist_ok=True)
    scene = neutral_setup(a)
    nose, side, up = orient(a)
    center, front, length = bbox(a, nose)
    lights(scene, center, length, nose, side, up)
    data = bpy.data.cameras.new("QA camera")
    camera = bpy.data.objects.new("QA camera", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    report = {"input": bpy.data.filepath,
              "inputSha256": hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
              "orientation": a.orientation,
              "fishLengthM": length, "resolution": [a.width, a.height],
              "samples": a.samples,
              "lighting": "Area light positions/sizes scale with fish length; energy scales with (length/0.45 m)^2",
              "views": {}}
    for view in a.views:
        if view in ("jaw_open_25deg", "jaw_open_three_quarter"):
            pose_open()
        settings = frame(camera, view, center, front, length, nose, side, up)
        path = a.output_dir / (view + ".png")
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        settings["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        report["views"][view] = settings
    (a.output_dir / "render-report.json").write_text(json.dumps(report, indent=2))
    print("SUPPLIED_BASS_QA_RENDER", a.output_dir)


if __name__ == "__main__":
    main()

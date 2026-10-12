"""Create an intentionally non-fish fixture to exercise Blender's GLB exporter."""
import bpy
import math
import os
import sys
from mathutils import Vector


def arguments():
    try:
        return sys.argv[sys.argv.index("--") + 1:]
    except ValueError:
        return []


def material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*color, 1.0)
    return mat


args = arguments()
if len(args) != 1:
    raise SystemExit("usage: blender --background --python export_smoke_fixture.py -- OUTPUT.glb")
output_path = os.path.abspath(args[0])
os.makedirs(os.path.dirname(output_path), exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for collection in (bpy.data.meshes, bpy.data.materials, bpy.data.actions):
    for item in list(collection):
        if item.users == 0:
            collection.remove(item)

# A cube and a separate animated marker make this fixture unmistakably non-fish.
bpy.ops.mesh.primitive_cube_add(size=1.5, location=(0.0, 0.0, 0.0))
cube = bpy.context.object
cube.name = "Validation_Cube"
cube.data.name = "Validation_Cube_Mesh"
cube.data.materials.append(material("Validation_Cobalt", (0.04, 0.22, 0.82)))

bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.22, location=(1.1, 0.0, 0.35))
beacon = bpy.context.object
beacon.name = "Validation_Animated_Beacon"
beacon.data.name = "Validation_Animated_Beacon_Mesh"
beacon.data.materials.append(material("Validation_Amber", (1.0, 0.38, 0.025)))
beacon.rotation_mode = "XYZ"
for frame, loc, turn in ((1, (1.1, 0.0, 0.35), 0.0), (16, (1.1, 0.0, 0.8), math.pi), (31, (1.1, 0.0, 0.35), math.tau)):
    beacon.location = loc
    beacon.rotation_euler.z = turn
    beacon.keyframe_insert(data_path="location", frame=frame, group="Validation Motion")
    beacon.keyframe_insert(data_path="rotation_euler", frame=frame, group="Validation Motion")

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 31
scene.render.fps = 30
scene.frame_set(1)
# Select fixture objects explicitly; no cameras/lights are needed in an interchange file.
bpy.ops.object.select_all(action="DESELECT")
for obj in (cube, beacon):
    obj.select_set(True)
bpy.context.view_layer.objects.active = cube
bpy.ops.export_scene.gltf(
    filepath=output_path,
    export_format="GLB",
    use_selection=True,
    export_animations=True,
    export_frame_range=True,
    export_frame_step=1,
    export_force_sampling=True,
    export_nla_strips=False,
    export_def_bones=False,
)
print("SMOKE_FIXTURE", output_path)
print("SMOKE_FIXTURE_OBJECTS", cube.name, beacon.name)

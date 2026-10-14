"""C2 deterministic swim rig + baked loop for Blender 4.3.2.

Takes a C1 bind-pose .blend (procedural largemouth-bass.blend or supplied
candidate-static.blend), builds a small deform armature (nose +X, dorsal +Z,
metres), smooth-weights by X station, bakes a 1 s sine SwimCruise loop,
exports a skinned GLB with one active action, and writes a JSON report.

Run on a Blender 4.3.2 host:
  blender --background --python-exit-code 1 --python tools/blender/rig_swim.py -- \
    --input artifacts/c1/supplied-candidate/candidate-static.blend \
    --output-dir artifacts/c2 [--frames 30] [--fps 30]

Generated .blend/GLB/report go to ignored artifacts/; nothing is committed.
"""
import argparse
import json
import math
import sys
from pathlib import Path


def parse(argv):
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=True)
    p.add_argument('--output-dir', dest='output', default='artifacts/c2')
    p.add_argument('--frames', type=int, default=30)
    p.add_argument('--fps', type=int, default=30)
    return p.parse_args(argv)


def smooth01(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


ARGS = parse(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
SRC = Path(ARGS.input)
if not SRC.is_file():
    raise SystemExit(
        f'C2 rig input not found: {SRC}\n'
        'Provide the C1 bind-pose .blend (e.g. artifacts/c1/supplied-candidate/'
        'candidate-static.blend). Supplied sources are ignored artifacts and '
        'are not committed; copy them onto the Blender host first.')

try:
    import bpy
    from mathutils import Vector
except ImportError:
    raise SystemExit('This script must run inside Blender: blender --background --python ...')

if bpy.app.version != (4, 3, 2):
    raise RuntimeError('This rig requires Blender 4.3.2')

OUT = Path(ARGS.output).resolve()
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SRC.resolve()))

meshes = [o for o in bpy.data.objects if o.type == 'MESH']
if not meshes:
    raise RuntimeError(f'No mesh found in {SRC}')
# Largest mesh by vertex count is the body to skin.
body = max(meshes, key=lambda o: len(o.data.vertices))
xs = [body.matrix_world @ v.co for v in body.data.vertices]
min_x = min(p.x for p in xs)
max_x = max(p.x for p in xs)

# --- Armature: root + 8 spine + head + 3 caudal = 13 deform bones (<=24 budget).
bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
rig = bpy.context.object
rig.name = 'BassRig'
arm = rig.data
arm.name = 'BassRigData'
for b in list(arm.edit_bones):
    arm.edit_bones.remove(b)

SPAN = max_x - min_x
stations = [min_x + SPAN * (i / 8) for i in range(9)]  # spine.00 (tail) .. spine.07 (head-end)
prev = None
spines = []
for i, x in enumerate(stations):
    b = arm.edit_bones.new(f'spine.{i:02d}')
    b.head = Vector((x, 0, 0))
    b.tail = Vector((x + SPAN / 8 * 0.9, 0, 0))
    b.use_deform = True
    if prev:
        b.parent = prev
        b.use_connect = True
    prev = b
    spines.append(b.name)
head = arm.edit_bones.new('head')
head.head = Vector((stations[-1], 0, 0))
head.tail = Vector((max_x, 0, 0))
head.parent = arm.edit_bones[spines[-1]]
head.use_connect = True
head.use_deform = True
tail_parent = arm.edit_bones[spines[0]]
caudal_names = []
for i in range(3):
    b = arm.edit_bones.new(f'caudal.{i:02d}')
    x0 = min_x - SPAN * 0.04 * (i + 1)
    b.head = Vector((x0 + SPAN * 0.04, 0, 0))
    b.tail = Vector((x0, 0, 0))
    b.parent = tail_parent if i == 0 else arm.edit_bones[caudal_names[-1]]
    b.use_connect = True
    b.use_deform = True
    tail_parent = b
    caudal_names.append(b.name)
root = arm.edit_bones.new('root')
root.head = Vector((0, 0, 0))
root.tail = Vector((0, 0, 0.05))
root.use_deform = False
for name in spines + ['head'] + caudal_names:
    arm.edit_bones[name].parent = root if arm.edit_bones[name].parent is None else arm.edit_bones[name].parent
bpy.ops.object.mode_set(mode='OBJECT')

# --- Skinning: smooth X-station weights on body; others parented, not deformed.
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='OBJECT')
mod = body.modifiers.new('C2Skin', 'ARMATURE')
mod.object = rig
# Vertex groups per deform bone, weight = tent falloff around station.
groups = {name: body.vertex_groups.new(name=name)
          for name in spines + ['head'] + caudal_names}
width = SPAN / 8
for v in body.data.vertices:
    co = body.matrix_world @ v.co
    x = co.x
    if 'Eye_' in body.name or co.x > stations[-1] + width * 0.5:
        # Head region rigid to head bone.
        groups['head'].add([v.index], 1.0, 'REPLACE')
        continue
    # Find surrounding spine stations.
    placed = False
    for i in range(len(stations) - 1):
        if stations[i] <= x <= stations[i + 1]:
            t = (x - stations[i]) / width
            groups[spines[i]].add([v.index], 1.0 - smooth01(t), 'REPLACE')
            groups[spines[i + 1]].add([v.index], smooth01(t), 'REPLACE')
            placed = True
            break
    if not placed:
        name = spines[0] if x < stations[0] else spines[-1]
        groups[name].add([v.index], 1.0, 'REPLACE')
for ob in meshes:
    if ob is not body:
        ob.parent = rig

# --- Bake SwimCruise: traveling sine, amplitude growing toward tail.
scene = bpy.context.scene
scene.render.fps = ARGS.fps
scene.frame_start = 1
scene.frame_end = ARGS.frames
action = bpy.data.actions.new('SwimCruise')
action.use_fake_user = True
if rig.animation_data is None:
    rig.animation_data_create()
rig.animation_data.action = action
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='POSE')
for f in range(1, ARGS.frames + 1):
    scene.frame_set(f)
    phase = 2 * math.pi * (f - 1) / ARGS.frames
    for i, name in enumerate(spines):
        pb = rig.pose.bones[name]
        s = i / max(1, len(spines) - 1)  # 0 tail .. 1 head
        amp = 0.004 + 0.028 * smooth01((0.9 - s))
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = (0, 0, amp * 8 * math.sin(phase - s * 2.2) * 0.12)
        pb.keyframe_insert(data_path='rotation_euler', frame=f)
    for name in ['head'] + caudal_names:
        pb = rig.pose.bones[name]
        pb.rotation_mode = 'XYZ'
        k = 1.6 if 'caudal' in name else 0.4
        pb.rotation_euler = (0, 0, k * 0.02 * math.sin(phase - 2.4))
        pb.keyframe_insert(data_path='rotation_euler', frame=f)
bpy.ops.object.mode_set(mode='OBJECT')

# Loop continuity: compare frame 1 vs frame-end pose.
def pose_at(frame):
    scene.frame_set(frame)
    return [tuple(rig.pose.bones[n].rotation_euler) for n in spines + ['head'] + caudal_names]

p1 = pose_at(1)
pN = pose_at(ARGS.frames)
# Sample the looping wrap: last frame should nearly equal first (sine loop).
max_dev = max(abs(a - b) for ra, rb in zip(p1, pN) for a, b in zip(ra, rb))

bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
glb_path = OUT / 'bass-swim.glb'
bpy.ops.export_scene.gltf(
    filepath=str(glb_path), export_format='GLB', use_selection=True,
    export_animations=True, export_frame_range=True, export_force_sampling=True,
    export_nla_strips=False, export_def_bones=False)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'bass-swim.blend'))

report = {
    'input': str(SRC), 'body': body.name, 'bones': [b.name for b in rig.data.bones],
    'deform_bones': sum(1 for b in rig.data.bones if b.use_deform),
    'frames': ARGS.frames, 'fps': ARGS.fps, 'action': action.name,
    'loop_max_dev_rad': max_dev, 'glb': str(glb_path),
}
(OUT / 'bass-swim-report.json').write_text(json.dumps(report, indent=2) + '\n')
print('C2_SWIM', json.dumps(report))
if max_dev > 0.05:
    raise RuntimeError(f'Swim loop discontinuity too large: {max_dev}')

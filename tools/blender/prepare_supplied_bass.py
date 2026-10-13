"""Prepare a private, static C1 bass candidate from the owner-supplied source.

Run from the repository root:
  blender --background artifacts/c1/user-supplied/original/largemouthBass_065_johnson_sketchfab.blend \
    --python-exit-code 1 --python tools/blender/prepare_supplied_bass.py

The original files are read only. This is C1 geometry/material preparation; no
rig, skin, or animation is exported. The original rest-rig scene is preserved
separately as authoring-baseline.blend for anatomical QA.
"""
import bpy
import bmesh
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'artifacts/c1/user-supplied/original'
OUT = ROOT / 'artifacts/c1/supplied-candidate'
OUT.mkdir(parents=True, exist_ok=True)
TEXTURES = OUT / 'textures'
TEXTURES.mkdir(exist_ok=True)
SOURCE_TEXTURES = {
    'bass_color.png': 1024,
    'bass_normal.png': 1024,
    'bass_roughness.png': 1024,
    'bass_alpha.jpg': 512,
}
FIN_TEXTURE_SIZE = 512
TARGET_LENGTH = 0.45
TARGET_BODY_TRIANGLES = 10500


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relink_sources():
    for image in bpy.data.images:
        if image.source != 'FILE':
            continue
        path = SOURCE / Path(image.filepath.replace('\\', '/')).name
        if path.exists():
            image.filepath = str(path)
            image.reload()


def image_by_basename(basename):
    return next(im for im in bpy.data.images
                if im.source == 'FILE' and Path(im.filepath).name == basename)


def fix_source_material():
    material = bpy.data.materials['Material']
    nodes = material.node_tree.nodes
    bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    output = next(n for n in nodes if n.type == 'OUTPUT_MATERIAL')
    material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    image_by_basename('bass_roughness.png').colorspace_settings.name = 'Non-Color'
    image_by_basename('bass_normal.png').colorspace_settings.name = 'Non-Color'
    image_by_basename('bass_alpha.jpg').colorspace_settings.name = 'Non-Color'
    image_by_basename('bass_color.png').colorspace_settings.name = 'sRGB'
    return material


def write_textures():
    result = {}
    for filename, size in SOURCE_TEXTURES.items():
        original = image_by_basename(filename)
        image = original.copy()
        image.name = f'C1 {size}px {filename}'
        image.scale(size, size)
        derived = TEXTURES / (Path(filename).stem + '.png')
        image.filepath_raw = str(derived)
        image.file_format = 'PNG'
        image.save()
        result[filename] = {
            'source_sha256': sha256(SOURCE / filename),
            'derived': str(derived.relative_to(ROOT)),
            'derived_sha256': sha256(derived),
            'source_size': list(original.size),
            'derived_size': list(image.size),
            'source_bytes': (SOURCE / filename).stat().st_size,
            'derived_bytes': derived.stat().st_size,
        }
    return result


def configure_materials(texture_result):
    material = bpy.data.materials['Material']
    nodes = material.node_tree.nodes
    for node in nodes:
        if node.type != 'TEX_IMAGE' or not node.image:
            continue
        filename = Path(node.image.filepath).name
        if filename in texture_result:
            derived_path = ROOT / texture_result[filename]['derived']
            node.image = bpy.data.images.load(str(derived_path), check_existing=True)
            node.image.colorspace_settings.name = 'sRGB' if filename == 'bass_color.png' else 'Non-Color'
    material.name = 'Bass body PBR opaque'
    material.surface_render_method = 'DITHERED'
    material.use_backface_culling = True
    material.diffuse_color = (.35, .34, .22, 1)
    fin = material.copy()
    fin.name = 'Bass fin PBR alpha'
    f_nodes = fin.node_tree.nodes
    # The supplied grayscale map marks translucent fin membrane in light gray;
    # black fin roots/rays stay opaque. Bake that into a normal RGBA base-color
    # image because arbitrary Blender math nodes are not portable to glTF.
    color_image = next(n.image for n in f_nodes if n.type == 'TEX_IMAGE' and n.image
                       and Path(n.image.filepath).name == 'bass_color.png')
    mask_image = next(n.image for n in f_nodes if n.type == 'TEX_IMAGE' and n.image
                      and Path(n.image.filepath).name == 'bass_alpha.png')
    mask_scaled = mask_image.copy()
    mask_scaled.scale(FIN_TEXTURE_SIZE, FIN_TEXTURE_SIZE)
    color_scaled = color_image.copy()
    color_scaled.scale(FIN_TEXTURE_SIZE, FIN_TEXTURE_SIZE)
    fin_color = bpy.data.images.new('C1 fin color with baked opacity',
                                    width=FIN_TEXTURE_SIZE, height=FIN_TEXTURE_SIZE, alpha=True)
    color_pixels = np.empty(FIN_TEXTURE_SIZE * FIN_TEXTURE_SIZE * 4, dtype=np.float32)
    mask_pixels = np.empty_like(color_pixels)
    color_scaled.pixels.foreach_get(color_pixels)
    mask_scaled.pixels.foreach_get(mask_pixels)
    color_pixels[3::4] = 1.0 - 0.6 * mask_pixels[0::4]
    fin_color.pixels.foreach_set(color_pixels)
    fin_color.update()
    fin_color.alpha_mode = 'STRAIGHT'
    fin_color.filepath_raw = str(TEXTURES / 'bass_color_fin_rgba.png')
    fin_color.file_format = 'PNG'
    fin_color.save()
    bpy.data.images.remove(mask_scaled)
    bpy.data.images.remove(color_scaled)
    fin_color = bpy.data.images.load(str(TEXTURES / 'bass_color_fin_rgba.png'), check_existing=True)
    color_node = next(n for n in f_nodes if n.type == 'TEX_IMAGE' and n.image
                      and Path(n.image.filepath).name == 'bass_color.png')
    color_node.image = fin_color
    bsdf = next(n for n in f_nodes if n.type == 'BSDF_PRINCIPLED')
    fin.node_tree.links.new(color_node.outputs['Alpha'], bsdf.inputs['Alpha'])
    fin.surface_render_method = 'DITHERED'
    fin.use_backface_culling = True
    fin.use_transparency_overlap = False
    return material, fin


def set_rest():
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            obj.data.pose_position = 'REST'
        if obj.animation_data:
            obj.animation_data_clear()
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()


def active(obj):
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for other in bpy.context.view_layer.objects:
        other.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_mesh_modifiers(obj):
    active(obj)
    for modifier in list(obj.modifiers):
        if modifier.type == 'ARMATURE':
            obj.modifiers.remove(modifier)
        else:
            bpy.ops.object.modifier_apply(modifier=modifier.name)


def triangle_count(obj):
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


def clean_loose_geometry(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    wires = [edge for edge in bm.edges if not edge.link_faces]
    bmesh.ops.delete(bm, geom=wires, context='EDGES')
    loose = [vert for vert in bm.verts if not vert.link_edges]
    bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return {'wire_edges_removed': len(wires), 'loose_vertices_removed': len(loose)}


def classify_fins(body, fin_material):
    """Only polygons driven by named fin groups use the supplied fin alpha."""
    fin_group_indices = {g.index for g in body.vertex_groups if g.name.startswith('fin_')}
    body.data.materials.append(fin_material)
    fin_faces = 0
    for polygon in body.data.polygons:
        weights = []
        for vertex_index in polygon.vertices:
            vertex = body.data.vertices[vertex_index]
            weights.append(sum(group.weight for group in vertex.groups
                               if group.group in fin_group_indices))
        if sum(weights) / len(weights) >= 0.35:
            polygon.material_index = 1
            fin_faces += 1
    return fin_faces


def setup_render():
    for obj in list(bpy.context.scene.objects):
        if obj.type in {'LIGHT', 'CAMERA'}:
            bpy.data.objects.remove(obj, do_unlink=True)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 48
    scene.cycles.use_denoising = False
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 800
    scene.render.resolution_percentage = 100
    scene.world = bpy.data.worlds.new('Neutral C1 world')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.18, .18, .18, 1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .5
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Base Contrast'
    scene.view_settings.exposure = 0
    for name, pos, energy in [('Key', (1, -.3, 1), 6), ('Fill', (-1, .4, .5), 3), ('Top', (0, 0, 1.5), 4)]:
        lamp = bpy.data.lights.new(name, 'AREA')
        lamp.energy = energy
        lamp.shape = 'DISK'
        lamp.size = TARGET_LENGTH
        obj = bpy.data.objects.new(name, lamp)
        scene.collection.objects.link(obj)
        obj.location = Vector(pos) * TARGET_LENGTH
        obj.rotation_euler = (-obj.location).to_track_quat('-Z', 'Y').to_euler()
    data = bpy.data.cameras.new('C1 diagnostic camera')
    data.type = 'ORTHO'
    data.ortho_scale = TARGET_LENGTH * 1.2
    camera = bpy.data.objects.new('C1 diagnostic camera', data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    return camera


def render_views(camera):
    scene = bpy.context.scene
    positions = {
        'profile': (0, 2, .05),
        'three-quarter': (1.2, 1.6, .65),
        'front': (2, 0, .05),
        'head-close': (1.6, 1.4, .5),
    }
    for name, offset in positions.items():
        camera.location = Vector(offset) * TARGET_LENGTH
        target = Vector((.16, 0, 0)) if name == 'head-close' else Vector((0, 0, 0))
        camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
        camera.data.ortho_scale = TARGET_LENGTH * (.48 if name == 'head-close' else 1.2)
        scene.render.filepath = str(OUT / f'candidate-{name}.png')
        bpy.ops.render.render(write_still=True)


def main():
    source_path = SOURCE / 'largemouthBass_065_johnson_sketchfab.blend'
    assert Path(bpy.data.filepath).resolve() == source_path.resolve(), 'Open the exact supplied source .blend first'
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    relink_sources()
    set_rest()
    fix_source_material()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'authoring-baseline.blend'))
    textures = write_textures()
    opaque, fin_material = configure_materials(textures)
    body = bpy.data.objects['body_mesh']
    eyes = bpy.data.objects['eye_mesh']
    apply_mesh_modifiers(body)
    apply_mesh_modifiers(eyes)
    full_body_triangles = triangle_count(body)
    decimator = body.modifiers.new('C1 measured polygon reduction', 'DECIMATE')
    decimator.decimate_type = 'COLLAPSE'
    decimator.ratio = TARGET_BODY_TRIANGLES / full_body_triangles
    decimator.use_symmetry = True
    decimator.symmetry_axis = 'X'
    active(body)
    bpy.ops.object.modifier_apply(modifier=decimator.name)
    cleanup = clean_loose_geometry(body)
    fin_faces = classify_fins(body, fin_material)
    # A private QA snapshot retains original vertex weights and armature for
    # a temporary open-jaw check. It is never exported as the C1 GLB.
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'candidate-weighted-qa.blend'))
    # Source nose is -Y; a +90 degree Z rotation maps it to +X.
    for obj in (body, eyes):
        obj.rotation_euler.z = math.pi / 2
        obj.scale *= TARGET_LENGTH / .3535086512565613
        active(obj)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    # Center the complete model bounding box and bake the translation to vertices.
    all_x = [v.co.x for obj in (body, eyes) for v in obj.data.vertices]
    shift = -(min(all_x) + max(all_x)) / 2
    for obj in (body, eyes):
        for vertex in obj.data.vertices:
            vertex.co.x += shift
        for group in list(obj.vertex_groups):
            obj.vertex_groups.remove(group)
    all_x = [v.co.x for obj in (body, eyes) for v in obj.data.vertices]
    final_scale = TARGET_LENGTH / (max(all_x) - min(all_x))
    for obj in (body, eyes):
        for vertex in obj.data.vertices:
            vertex.co *= final_scale
    for obj in list(bpy.data.objects):
        if obj.type == 'ARMATURE':
            bpy.data.objects.remove(obj, do_unlink=True)
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)
    scene = bpy.context.scene
    for obj in list(scene.objects):
        if obj.type not in {'MESH', 'LIGHT', 'CAMERA'}:
            bpy.data.objects.remove(obj, do_unlink=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'candidate-static.blend'))
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    eyes.select_set(True)
    bpy.context.view_layer.objects.active = body
    glb = OUT / 'candidate-static.glb'
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format='GLB', use_selection=True,
                              export_animations=False, export_skins=False,
                              export_tangents=True,
                              export_cameras=False, export_lights=False,
                              export_apply=True)
    camera = setup_render()
    render_views(camera)
    counts = {obj.name: {'vertices': len(obj.data.vertices), 'triangles': triangle_count(obj)}
              for obj in (body, eyes)}
    xs = [v.co.x for obj in (body, eyes) for v in obj.data.vertices]
    ys = [v.co.y for obj in (body, eyes) for v in obj.data.vertices]
    zs = [v.co.z for obj in (body, eyes) for v in obj.data.vertices]
    report = {
        'source_blend_sha256': sha256(source_path),
        'source_license': 'CC BY-NC 4.0; personal noncommercial use confirmed by owner',
        'source_body_evaluated_triangles': full_body_triangles,
        'source_eye_triangles': 224,
        'candidate_counts': counts,
        'candidate_triangle_total': sum(c['triangles'] for c in counts.values()),
        'target_triangle_ceiling': 10976,
        'fin_alpha_polygon_count': fin_faces,
        'loose_geometry_cleanup': cleanup,
        'material_count': len(body.data.materials),
        'coordinates_meters': {'nose_axis': '+X', 'dorsal_axis': '+Z',
                               'length': max(xs) - min(xs),
                               'bounds': [[min(a), max(a)] for a in (xs, ys, zs)]},
        'static': {'armature_objects': sum(o.type == 'ARMATURE' for o in bpy.data.objects),
                   'actions': len(bpy.data.actions),
                   'armature_modifiers': sum(m.type == 'ARMATURE' for o in (body, eyes) for m in o.modifiers)},
        'textures': textures,
        'derived_fin_rgba': {'path': str((TEXTURES / 'bass_color_fin_rgba.png').relative_to(ROOT)),
                             'sha256': sha256(TEXTURES / 'bass_color_fin_rgba.png'),
                             'bytes': (TEXTURES / 'bass_color_fin_rgba.png').stat().st_size,
                             'alpha_formula': 'opacity = 1 - 0.6 * source_alpha_grayscale'},
        'estimated_four_image_rgba8_with_mips_mib': (3 * 1024 * 1024 + 512 * 512) * 4 * 4 / 3 / (1024 * 1024),
        'glb_bytes': glb.stat().st_size,
        'glb_sha256': sha256(glb),
        'candidate_blend_sha256': sha256(OUT / 'candidate-static.blend'),
    }
    (OUT / 'preparation-report.json').write_text(json.dumps(report, indent=2))
    print('PREPARATION_REPORT', json.dumps(report))


main()

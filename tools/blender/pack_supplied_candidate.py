"""Pack the four used images into a portable copy of the static C1 .blend.

Run after prepare_supplied_bass.py from the repository root:
  blender --background artifacts/c1/supplied-candidate/candidate-static.blend \
    --python-exit-code 1 --python tools/blender/pack_supplied_candidate.py
"""
import bpy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/c1/supplied-candidate'
SOURCE = OUT / 'candidate-static.blend'
DEST = OUT / 'candidate-portable.blend'
assert Path(bpy.data.filepath).resolve() == SOURCE.resolve(), 'Open candidate-static.blend first'

# Remove inactive source inspection nodes (Emission Viewer and disconnected
# alpha image) so only the rendered PBR branch and its four images are packed.
used_images = set()
for material in bpy.data.materials:
    if not material.use_nodes:
        continue
    tree = material.node_tree
    outputs = [node for node in tree.nodes if node.type == 'OUTPUT_MATERIAL' and node.is_active_output]
    reachable = set(outputs)
    pending = outputs[:]
    while pending:
        node = pending.pop()
        for link in tree.links:
            if link.to_node == node and link.from_node not in reachable:
                reachable.add(link.from_node)
                pending.append(link.from_node)
    for node in list(tree.nodes):
        if node not in reachable:
            tree.nodes.remove(node)
    used_images.update(node.image for node in tree.nodes if node.type == 'TEX_IMAGE' and node.image)
assert len(used_images) == 4, f'Expected exactly four active PBR images, got {len(used_images)}'
for image in list(bpy.data.images):
    if image not in used_images:
        bpy.data.images.remove(image, do_unlink=True)
for image in used_images:
    image.pack()
    image.filepath = '//textures/' + Path(image.filepath).name
    assert image.packed_file

bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
report = {
    'input': str(SOURCE.relative_to(ROOT)),
    'input_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'portable': str(DEST.relative_to(ROOT)),
    'portable_sha256': hashlib.sha256(DEST.read_bytes()).hexdigest(),
    'portable_bytes': DEST.stat().st_size,
    'packed_images': sorted(({'name': image.name, 'size': list(image.size),
                              'packed_bytes': len(image.packed_file.data)}
                             for image in used_images), key=lambda item: item['name']),
}
(OUT / 'portable-report.json').write_text(json.dumps(report, indent=2))
print('PORTABLE_REPORT', json.dumps(report))

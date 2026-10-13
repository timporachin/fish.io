"""Rerender preserved rejected C1 source under the rework inspection lighting.

Run with --baseline path/to/old.blend --output path/to/gallery.
Only lights/cameras/sampling change; no mesh or material edits occur.
"""
from pathlib import Path
import argparse
import sys
import bpy
from mathutils import Vector
p=argparse.ArgumentParser()
p.add_argument('--baseline',default='artifacts/c1/before/largemouth-bass.blend')
p.add_argument('--output',default='docs/evidence/c1/before-matched-lighting')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.open_mainfile(filepath=str(Path(a.baseline).resolve()))
scene=bpy.context.scene
for name,power,size in [('key',12,.30),('fill',6,.30),('top',5,.25)]:
    bpy.data.lights[name].energy=power
    bpy.data.lights[name].size=size
scene.cycles.samples=128
out=Path(a.output).resolve(); out.mkdir(parents=True,exist_ok=True)
cam=scene.camera
views={'left':(0,.8,0),'right':(0,-.8,0),'front':(.8,0,0),'rear':(-.8,0,0),'top':(0,0,.8),'front_three_quarter':(.62,-.64,.19)}
for view,pos in views.items():
    cam.location=pos
    cam.data.type='PERSP' if view=='front_three_quarter' else 'ORTHO'
    cam.data.lens=60
    cam.data.ortho_scale=.38 if view in ('front','rear') else .52 if view=='top' else .54
    cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(out/(view+'.png'))
    bpy.ops.render.render(write_still=True)

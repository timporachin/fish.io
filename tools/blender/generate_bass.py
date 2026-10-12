"""Deterministic, unrigged largemouth bass asset for Blender 4.3.2.

Run: blender -b --python tools/blender/generate_bass.py -- [--seed 1947] [--output artifacts/c1]
Coordinates are metres, nose +X, dorsal +Z. All source textures are generated here.
"""
import argparse
import json
import math
import random
import sys
from pathlib import Path

import bpy
import bmesh
import numpy as np
from mathutils import Vector


def args():
    p = argparse.ArgumentParser()
    p.add_argument('--seed', type=int, default=1947)
    p.add_argument('--output', '--output-dir', dest='output', default='artifacts/c1')
    p.add_argument('--render-samples', type=int, default=64)
    p.add_argument('--skip-renders', action='store_true')
    p.add_argument('--render-view', choices=('left','right','front','rear','top','front_three_quarter'))
    return p.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])

A = args()
if bpy.app.version != (4,3,2):
    raise RuntimeError('This generator requires Blender 4.3.2')
random.seed(A.seed)
np.random.seed(A.seed)
OUT = Path(A.output).resolve()
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.materials, bpy.data.images, bpy.data.meshes, bpy.data.curves):
    for block in list(datablocks):
        if block.users == 0:
            datablocks.remove(block)

FISH = []

def smooth_mat(name, rgb, roughness=.65, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*rgb, 1)
    b.inputs['Roughness'].default_value = roughness
    b.inputs['Metallic'].default_value = metallic
    return m


def noise(h, w, gh, gw, rng):
    lattice = rng.random((gh + 1, gw + 1), dtype=np.float32)
    yi = np.linspace(0, gh, h, endpoint=False, dtype=np.float32)
    xi = np.linspace(0, gw, w, endpoint=False, dtype=np.float32)
    y0 = yi.astype(np.int32); x0 = xi.astype(np.int32)
    fy = yi - y0; fx = xi - x0
    fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
    a = lattice[y0[:, None], x0[None, :]]
    b = lattice[y0[:, None] + 1, x0[None, :]]
    c = lattice[y0[:, None], x0[None, :] + 1]
    d = lattice[y0[:, None] + 1, x0[None, :] + 1]
    return (a * (1 - fy[:, None]) + b * fy[:, None]) * (1 - fx[None, :]) + (c * (1 - fy[:, None]) + d * fy[:, None]) * fx[None, :]


def save_image(name, rgba, path, noncolor=False):
    h, w, _ = rgba.shape
    img = bpy.data.images.new(name, width=w, height=h, alpha=True)
    if noncolor:
        img.colorspace_settings.name='Non-Color'
    img.filepath_raw = str(path)
    img.file_format = 'PNG'
    # Blender image buffer starts at lower left, same as UV v=0.
    img.pixels.foreach_set(np.ascontiguousarray(rgba.reshape(-1)).tolist())
    img.save()
    img.pack()
    return img


def textured_mat(name, image, roughness=.72):
    m = smooth_mat(name, (.35, .40, .23), roughness)
    nodes = m.node_tree.nodes
    tex = nodes.new('ShaderNodeTexImage')
    tex.image = image
    tex.interpolation = 'Linear'
    m.node_tree.links.new(tex.outputs['Color'], nodes.get('Principled BSDF').inputs['Base Color'])
    return m

# Circumferential v=0 is dorsal midline. The lateral pigment band sits on
# each flank near cos(theta)=0.18; belly lies around v=0.5.
H = W = 1024
rng = np.random.default_rng(A.seed)
u = np.linspace(0, 1, W, endpoint=False, dtype=np.float32)[None, :]
v = np.linspace(0, 1, H, endpoint=False, dtype=np.float32)[:, None]
c = np.cos(v * 2 * math.pi)
coarse = noise(H, W, 18, 45, rng) - .5
fine = noise(H, W, 90, 170, rng) - .5
olive = np.array([.16, .23, .085], dtype=np.float32)
green = np.array([.28, .36, .16], dtype=np.float32)
cream = np.array([.67, .65, .46], dtype=np.float32)
upper = np.clip((c + .05) * 1.2, 0, 1)
belly = np.clip((-c - .15) * 1.45, 0, 1)
base = green[None, None, :] * (1 - upper[..., None]) + olive[None, None, :] * upper[..., None]
base = base * (1 - belly[..., None]) + cream[None, None, :] * belly[..., None]
base = np.broadcast_to(base, (H, W, 3)).copy()
# Fine overlapping crescent boundaries, staggered between scale rows.
lx = np.mod(u*70 + np.floor(v*50)*.5, 1)-.5
ly = np.mod(v*50,1)
arc = .55+.32*np.sqrt(np.clip(1-(lx/.55)**2,0,1))
crescent = np.exp(-((ly-arc)/.035)**2)
scale_light = np.exp(-((ly-(arc-.09))/.065)**2)
scale_visibility = np.clip(1-np.abs(c),0,1)
base *= (1-.045*crescent[...,None]*scale_visibility[...,None])
base += .012*scale_light[...,None]*scale_visibility[...,None]
# Largemouth bass have a blotched rather than a ruler-straight lateral stripe.
stripe_center = .18 + .055 * np.sin(u * 31) + .033 * (noise(1, W, 1, 26, rng)[0:1, :] - .5)
stripe = np.exp(-((c - stripe_center) / (.105 + .035 * np.sin(u * 51) ** 2)) ** 2)
segment = .43 + .57 * np.clip((noise(H, W, 12, 65, rng) - .32) * 3.2, 0, 1)
stripe *= segment * (u > .07) * (u < .65)
base *= (1 - .66 * stripe[..., None])
# Scattered olive blotches above/below the band and small flecks in scales.
blotch = np.clip((coarse + .065) * 2.8, 0, 1) * np.exp(-((c - .34) / .43) ** 2)
base *= (1 - .20 * blotch[..., None])
base += (.10 * coarse + .045 * fine)[..., None]
base = np.clip(base, .025, .92)
rgba = np.concatenate((base, np.ones((H, W, 1), dtype=np.float32)), axis=2)
body_img = save_image('BassScaleOlive_1024', rgba, OUT / 'bass-scale-olive.png')
BODY_MAT = textured_mat('Bass skin - scale and broken lateral stripe', body_img)
height = .12*crescent*scale_visibility + .035*scale_light*scale_visibility + .02*fine
dv, du = np.gradient(height)
nx = -du * 2.0; ny = -dv * 2.0; nz = np.ones_like(nx)
normal_length = np.sqrt(nx*nx+ny*ny+nz*nz)
normal_rgb = np.stack((.5+.5*nx/normal_length,.5+.5*ny/normal_length,
                       .5+.5*nz/normal_length),axis=2).astype(np.float32)
normal_img = save_image('BassScaleNormal_1024',
                        np.concatenate((normal_rgb,np.ones((H,W,1),dtype=np.float32)),axis=2),
                        OUT/'bass-scale-normal.png',noncolor=True)
rough = np.clip(.48-.045*crescent*scale_visibility+.025*fine,.38,.58)
rough_img = save_image('BassScaleRoughness_1024',
                       np.concatenate((np.repeat(rough[...,None],3,axis=2),
                                       np.ones((H,W,1),dtype=np.float32)),axis=2),
                       OUT/'bass-scale-roughness.png',noncolor=True)
nodes=BODY_MAT.node_tree.nodes
bsdf=nodes.get('Principled BSDF')
ntex=nodes.new('ShaderNodeTexImage'); ntex.image=normal_img
nmap=nodes.new('ShaderNodeNormalMap'); nmap.inputs['Strength'].default_value=.46
BODY_MAT.node_tree.links.new(ntex.outputs['Color'],nmap.inputs['Color'])
BODY_MAT.node_tree.links.new(nmap.outputs['Normal'],bsdf.inputs['Normal'])
rtex=nodes.new('ShaderNodeTexImage'); rtex.image=rough_img
BODY_MAT.node_tree.links.new(rtex.outputs['Color'],bsdf.inputs['Roughness'])

# Fin pigment/ray base texture. Mesh rays are also modeled for silhouette and grazing light.
fw = fh = 512
fu = np.linspace(0, 1, fw, endpoint=False, dtype=np.float32)[None, :]
fv = np.linspace(0, 1, fh, endpoint=False, dtype=np.float32)[:, None]
fn = noise(fh, fw, 40, 40, rng) - .5
bands = .5 + .5 * np.sin(fv * 43 + 2.3 * np.sin(fu * 15))
fin_col = np.broadcast_to(np.array([.40, .43, .30], dtype=np.float32), (fh, fw, 3)).copy()
fin_col *= (1 - .075 * bands[..., None] * fv[..., None])
fin_col += .035 * fn[..., None]
fin_col *= (1-.16*np.exp(-((np.mod(fu*25,1)-.5)/.08)**2)[...,None])
fin_rgba = np.concatenate((np.clip(fin_col, 0, 1), np.ones((fh, fw, 1), dtype=np.float32)), axis=2)
fin_img = save_image('BassFinOlive_512', fin_rgba, OUT / 'bass-fin-olive.png')
pectoral_col=np.clip(fin_col*np.array([.55,.40,.27],dtype=np.float32),0,1)
pectoral_img=save_image('BassPectoralAmber_512',
                        np.concatenate((pectoral_col,np.ones((fh,fw,1),dtype=np.float32)),axis=2),
                        OUT/'bass-pectoral-amber.png')
FIN_MAT = textured_mat('Bass fin membranes', fin_img, .78)
FIN_RAY = smooth_mat('Olive fin rays', (.30, .34, .23), .67)
PECTORAL_RAY = smooth_mat('Amber pectoral rays', (.16, .12, .07), .78)
MOUTH = smooth_mat('Mouth cavity charcoal olive', (.050, .061, .045), .86)
LIP = smooth_mat('Fleshy lip', (.19, .25, .14), .75)
IRIS = smooth_mat('Amber iris', (.18, .13, .060), .34, .12)
PUPIL = smooth_mat('Black pupil', (.012, .018, .015), .08)
EYE_RIM = smooth_mat('Eye rim gold olive', (.13, .18, .08), .58)
EYE_HILITE = smooth_mat('Eye reflection', (.93, .94, .86), .09)
PECTORAL_MAT = textured_mat('Amber pectoral membrane', pectoral_img, .74)


def mesh(name, verts, faces, mat, uvs=None, smooth=True):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    me.materials.append(mat)
    if uvs:
        uv_layer = me.uv_layers.new(name='UVMap')
        for poly, face_uv in zip(me.polygons, uvs):
            for li, uv in zip(poly.loop_indices, face_uv):
                uv_layer.data[li].uv = uv
    if smooth:
        for poly in me.polygons:
            poly.use_smooth = True
    FISH.append(ob)
    return ob

# Measured-looking loft: max depth near forward midbody, stout head and narrow peduncle.
PROFILE = [
    (-.177, .011, .010, .000), (-.164, .018, .014, .000),
    (-.142, .032, .022, .001), (-.113, .047, .030, .002),
    (-.078, .058, .037, .003), (-.039, .064, .041, .004),
    (.000, .065, .042, .004), (.037, .062, .041, .005),
    (.074, .056, .038, .005), (.111, .048, .034, .006),
    (.145, .039, .029, .006), (.175, .030, .023, .006),
    (.195, .022, .027, .006), (.207, .017, .025, .005)
]

def shape(x):
    x = min(max(x, PROFILE[0][0]), PROFILE[-1][0])
    for j in range(len(PROFILE) - 1):
        a, b = PROFILE[j], PROFILE[j + 1]
        if a[0] <= x <= b[0]:
            t = (x - a[0]) / (b[0] - a[0])
            prev = PROFILE[max(j-1,0)]; following = PROFILE[min(j+2,len(PROFILE)-1)]
            span = b[0]-a[0]
            values=[]
            for k in (1,2,3):
                m0=(b[k]-prev[k])/(b[0]-prev[0])
                m1=(following[k]-a[k])/(following[0]-a[0])
                values.append((2*t**3-3*t*t+1)*a[k]+(t**3-2*t*t+t)*span*m0+
                              (-2*t**3+3*t*t)*b[k]+(t**3-t*t)*span*m1)
            return values
    return list(PROFILE[-1][1:])

def surface_y(x, z, side):
    if 'body' in globals():
        hit, location, _, _ = body.ray_cast(Vector((x,side*.2,z)),
                                             Vector((0,-side,0)),distance=.4)
        if hit:
            return location.y
    h, w, zc = shape(x)
    q = max(0, 1 - ((z - zc) / max(h, 1e-5)) ** 2)
    return side * w * math.sqrt(q)

# Body mesh has closed longitudinal rings and 40 sides. The texture seam is
# per-face UV data: no doubled/coincident mesh vertices or open seam edges.
NX, NR = 51, 36
xs = np.linspace(PROFILE[0][0], PROFILE[-1][0], NX)
verts = []
for x in xs:
    h, w, zc = shape(float(x))
    for k in range(NR):
        a = 2 * math.pi * k / NR
        nose_round=max(0,(float(x)-.175)/(.207-.175))*.006*math.sin(a)**2
        verts.append((float(x)-nose_round, w * math.sin(a), zc + h * math.cos(a)))
faces = []; uvs = []
for i in range(NX - 1):
    for k in range(NR):
        a = i * NR + k; b = (i + 1) * NR + k
        faces.append((a, b, (i + 1) * NR + (k + 1) % NR, i * NR + (k + 1) % NR))
        u0 = i / (NX - 1); u1 = (i + 1) / (NX - 1)
        v0 = k / NR; v1 = (k + 1) / NR
        uvs.append(((u0, v0), (u1, v0), (u1, v1), (u0, v1)))
faces.append(tuple(range(NR)))
uvs.append(tuple((0, k / NR) for k in range(NR)))
# The blunt head ends in a narrow recessed slit, rather than tapering all the
# way to the mouth. A small front annulus connects the snout to the aperture.
aperture_start=len(verts)
for k in range(NR):
    a=2*math.pi*k/NR
    verts.append((.208-.006*math.sin(a)**2,.024*math.sin(a),.007+.004*math.cos(a)))
for k in range(NR):
    kn=(k+1)%NR; outer=(NX-1)*NR
    faces.append((outer+k,aperture_start+k,aperture_start+kn,outer+kn))
    uvs.append(((.99,k/NR),(1,k/NR),(1,(k+1)/NR),(.99,(k+1)/NR)))
# Inward-curving cavity lining from the aperture rim to a dark throat.
inner_start=len(verts)
for x,h,w,zc in ((.196,.004,.021,.007),(.182,.003,.014,.006),(.175,.0012,.0015,.006)):
    for k in range(NR):
        a=2*math.pi*k/NR
        verts.append((x,w*math.sin(a),zc+h*math.cos(a)))
cavity_face_start=len(faces)
for r in range(3):
    outer=aperture_start if r==0 else inner_start+(r-1)*NR
    inner=inner_start+r*NR
    for k in range(NR):
        kn=(k+1)%NR
        faces.append((outer+k,inner+k,inner+kn,outer+kn))
        uvs.append(((1-r*.04,k/NR),(1-(r+1)*.04,k/NR),
                    (1-(r+1)*.04,(k+1)/NR),(1-r*.04,(k+1)/NR)))
faces.append(tuple(inner_start+2*NR+k for k in reversed(range(NR))))
uvs.append(tuple((.88,k/NR) for k in reversed(range(NR))))
body = mesh('Body_quadrilateral_loft', verts, faces, BODY_MAT, uvs)
body.data.materials.append(MOUTH)
for poly in list(body.data.polygons)[cavity_face_start:]: poly.material_index=1


def uv_sphere(name, loc, scale, material, segments=12, rings=6):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(material)
    for p in ob.data.polygons: p.use_smooth = True
    FISH.append(ob)
    return ob

# A narrow open-looking cavity on both cheeks: terminal mouth line runs back
# to the jaw hinge, which sits posterior to the eye's rear rim.
for side, label in ((-1, 'right'), (1, 'left')):
    slit = [( .202,.003),(.192,.000),(.169,-.005),(.145,-.010),(.119,-.016),(.094,-.020),(.079,-.021)]
    upper = [(x, z + .0013) for i, (x,z) in enumerate(slit)]
    lower = [(x, z - .0013) for i, (x,z) in enumerate(slit)]
    vv = [(x, surface_y(x,z,side) + side*.00025, z) for x,z in upper + lower]
    ff = [(i, i+1, 7+i+1, 7+i) for i in range(6)]
    mesh(f'Mouth_cavity_{label}', vv, ff, MOUTH, [((0,0),(1,0),(1,1),(0,1))]*6)
    # Posterior bony operculum is a separate curved plate, with exposed dark seam.
    outline_control=[(.112,.021),(.095,.042),(.060,.049),(.029,.032),(.014,.007),(.023,-.026),(.052,-.045),(.083,-.034),(.105,-.015)]
    outline=[]
    for i in range(len(outline_control)):
        p0=outline_control[(i-1)%len(outline_control)]
        p1=outline_control[i]
        p2=outline_control[(i+1)%len(outline_control)]
        p3=outline_control[(i+2)%len(outline_control)]
        for q in range(4):
            t=q/4
            outline.append(tuple(.5*((2*p1[k])+(-p0[k]+p2[k])*t+
                       (2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*t*t+
                       (-p0[k]+3*p1[k]-3*p2[k]+p3[k])*t*t*t) for k in (0,1)))
    center=(.061,.002)
    gv=[(center[0],surface_y(center[0],center[1],side)+side*.00065,center[1])]
    for radius in (.25,.50,.75,1.0):
        for ox,oz in outline:
            x=center[0]*(1-radius)+ox*radius; z=center[1]*(1-radius)+oz*radius
            gv.append((x,surface_y(x,z,side)+side*.00065,z))
    gf=[]
    for i in range(len(outline)):
        gf.append((0,1+i,1+(i+1)%len(outline)))
    for ring in range(3):
        off=1+ring*len(outline); nxt=off+len(outline)
        for i in range(len(outline)):
            j=(i+1)%len(outline)
            gf.append((off+i,nxt+i,nxt+j,off+j))
    if side==1:
        gf=[tuple(reversed(face)) for face in gf]
    guv=[]
    for face in gf:
        coords=[]
        for vi in face:
            x,y,z=gv[vi]; h,w,zc=shape(x)
            theta=math.atan2(y/max(w,1e-5), (z-zc)/max(h,1e-5))%(2*math.pi)
            coords.append(((x-PROFILE[0][0])/(PROFILE[-1][0]-PROFILE[0][0]),theta/(2*math.pi)))
        guv.append(tuple(coords))
    mesh(f'Operculum_plate_{label}',gv,gf,BODY_MAT,guv)
    # Eye is proud of cheek; iris and pupil are layered hemispheric spheres.
    ex,ez=.125,.029
    ey=abs(surface_y(ex,ez,side))
    uv_sphere(f'Eye_orbit_{label}',(ex,side*(ey-.0005),ez),(.0080,.0015,.0080),EYE_RIM)
    uv_sphere(f'Iris_{label}',(ex,side*(ey+.0008),ez),(.0072,.0017,.0072),IRIS)
    uv_sphere(f'Pupil_{label}',(ex+.0006,side*(ey+.0020),ez),(.0052,.0011,.0052),PUPIL)
    uv_sphere(f'Corneal_glint_{label}',(ex+.0026,side*(ey+.0029),ez+.0023),(.00085,.0003,.00085),EYE_HILITE,12,6)

# Lower mandible is a narrow U-shaped curved shell following the ventral head,
# not a solid cylinder in front of the chin. Its upper edges run behind the eye
# and its thin projecting anterior rim forms the lower edge of the mouth.
jaw_xs=(.079,.095,.115,.135,.155,.175,.195,.207,.210)
mouthline=((.079,-.021),(.145,-.010),(.195,.001),(.207,.007),(.210,.007))
J=16; I=len(jaw_xs); half=(J+1)*I
jv=[]; juv=[]; jf=[]
for layer in (0,1):
    for x in jaw_xs:
        if x>.207:
            alpha=math.pi/2; h=.005; w=.024; zc=.007
        else:
            h,w,zc=shape(x)
            zm=float(np.interp(x,[p[0] for p in mouthline],[p[1] for p in mouthline]))
            alpha=math.acos(max(-.95,min(.95,(zm-zc)/h)))
        for j in range(J+1):
            theta=alpha+(2*math.pi-2*alpha)*j/J
            blend=max(0,min(1,(x-.079)/.025)); blend=blend*blend*(3-2*blend)
            factor=(1.001+blend*.023) if layer==0 else (1.000+blend*.001)
            round_t=max(0,min(1,(x-.175)/(.207-.175)))
            xx=x-.006*round_t*math.sin(theta)**2
            if layer==1 and x>.207:
                xx-=.0005
            jv.append((xx,w*factor*math.sin(theta),zc+h*factor*math.cos(theta)))
            juv.append(((x-PROFILE[0][0])/(PROFILE[-1][0]-PROFILE[0][0]),theta/(2*math.pi)))
def jo(i,j): return i*(J+1)+j
def ji(i,j): return half+i*(J+1)+j
for i in range(I-1):
    for j in range(J):
        jf.append((jo(i,j),jo(i+1,j),jo(i+1,j+1),jo(i,j+1)))
        jf.append((ji(i,j+1),ji(i+1,j+1),ji(i+1,j),ji(i,j)))
    jf.append((jo(i,0),ji(i,0),ji(i+1,0),jo(i+1,0)))
    jf.append((jo(i,J),jo(i+1,J),ji(i+1,J),ji(i,J)))
for j in range(J):
    jf.append((jo(0,j+1),jo(0,j),ji(0,j),ji(0,j+1)))
    jf.append((jo(I-1,j),jo(I-1,j+1),ji(I-1,j+1),ji(I-1,j)))
mesh('Lower_mandible_volumetric',jv,jf,BODY_MAT,[tuple(juv[k] for k in f) for f in jf])

# Fleshy annular lip surrounds a recessed, genuinely open-looking cavity.
rv=[];rf=[]
for i in range(17):
    a=-math.pi/2+math.pi*i/16
    for j in range(6):
        b=2*math.pi*j/6
        rv.append((.207-.006*math.sin(a)**2+.00075*math.cos(b),
                   (.024+.00075*math.sin(b))*math.sin(a),
                   .007+(.004+.00075*math.sin(b))*math.cos(a)))
for i in range(16):
    for j in range(6):
        rf.append((i*6+j,(i+1)*6+j,(i+1)*6+(j+1)%6,i*6+(j+1)%6))
mesh('Upper_mouth_lip_arc',rv,rf,LIP)

# Fish membranes are two close quilted surfaces with real outer silhouette.
# Each ray is a single beveled polyline, merged into one mesh after generation.
ray_curves=[]

def fin_grid(name, bases, tips, material=FIN_MAT, ray_step=1, thick=.00055):
    assert len(bases)==len(tips)
    ray_bases=list(bases); ray_tips=list(tips)
    if name.startswith('Dorsal_spiny'):
        scalloped_bases=[]; scalloped_tips=[]
        for i in range(len(bases)-1):
            scalloped_bases.append(bases[i]); scalloped_tips.append(tips[i])
            scalloped_bases.append(tuple((bases[i][k]+bases[i+1][k])*.5 for k in range(3)))
            scalloped_tips.append(tuple((tips[i][k]+tips[i+1][k])*.5-(.005 if k==2 else 0) for k in range(3)))
        scalloped_bases.append(bases[-1]); scalloped_tips.append(tips[-1])
        bases=scalloped_bases; tips=scalloped_tips
    n=len(bases); ts=(0,.33,.66,1)
    vs=[]; fs=[]; uv=[]
    for sign in (-1,1):
        for i,(b,t) in enumerate(zip(bases,tips)):
            for q in ts:
                # Cambered membrane gives the fins an organic surface and edge light.
                camber=(.0006 if name.endswith('_left') else -.0006 if name.endswith('_right') else .0013)
                midpoint=math.sin(q*math.pi)*camber
                vs.append(tuple(b[k]*(1-q)+t[k]*q + (sign*thick if k==1 else 0) + (midpoint if k==1 else 0) for k in range(3)))
    stride=n*len(ts)
    for side_idx in (0,1):
        for i in range(n-1):
            for j in range(len(ts)-1):
                a=side_idx*stride+i*len(ts)+j
                face=(a,a+4,a+5,a+1) if side_idx==0 else (a+1,a+5,a+4,a)
                fs.append(face)
                uvpoints=[(i/(n-1),ts[j]),((i+1)/(n-1),ts[j]),
                          ((i+1)/(n-1),ts[j+1]),(i/(n-1),ts[j+1])]
                uv.append(tuple(uvpoints) if side_idx==0 else
                          (uvpoints[3],uvpoints[2],uvpoints[1],uvpoints[0]))
    for i in range(n-1):
        a=i*4+3; b=(i+1)*4+3
        fs.append((a,b,b+stride,a+stride)); uv.append(((0,0),(1,0),(1,1),(0,1)))
        a=i*4; b=(i+1)*4
        fs.append((a,a+stride,b+stride,b)); uv.append(((0,0),(0,1),(1,1),(1,0)))
    for i in (0,n-1):
        for j in range(3):
            a=i*4+j
            fs.append((a,a+1,a+1+stride,a+stride))
            uv.append(((0,0),(1,0),(1,1),(0,1)))
    ob=mesh(name,vs,fs,material,uv)
    for i in range(0,len(ray_bases),ray_step):
        b=Vector(ray_bases[i]); t=Vector(ray_tips[i]); d=t-b
        if d.length>.006:
            side_offset=(.0018 if name.endswith('_left') else -.0018 if name.endswith('_right') else .0)
            points=[b+d*q+Vector((0,side_offset*math.sin(q*math.pi),0)) for q in (0,.33,.67,1)]
            ray_curves.append((name+f'_ray{i}',points,.00028 if 'Caudal' not in name else .00036))
    return ob

# Dorsal fins: ten spines and a separately lobed soft portion; membranes meet at
# a low notch while remaining anatomically continuous at the base.
spiny_x=np.linspace(.054,-.077,10)
spiny_height=[.018,.027,.035,.039,.041,.042,.040,.035,.028,.010]
spiny_b=[];spiny_t=[]
for x,dh in zip(spiny_x,spiny_height):
    h,w,zc=shape(float(x)); z=zc+h*.96
    spiny_b.append((float(x),0,z-.003))
    spiny_t.append((float(x)-.003,0,z+dh))
fin_grid('Dorsal_spiny_10_spines',spiny_b,spiny_t)
soft_x=np.linspace(-.077,-.148,14)
soft_height=[.014,.022,.033,.041,.047,.051,.053,.052,.050,.047,.041,.033,.022,.009]
soft_b=[];soft_t=[]
for x,dh in zip(soft_x,soft_height):
    h,w,zc=shape(float(x)); z=zc+h*.96
    soft_b.append((float(x),0,z-.003))
    soft_t.append((float(x)-.012*dh/.06,0,z+dh))
fin_grid('Dorsal_soft_14_rays',soft_b,soft_t)

# Anal fin beneath the rear third of the fish.
ax=np.linspace(-.078,-.151,12)
anal_h=[.013,.029,.044,.052,.052,.049,.044,.038,.032,.025,.018,.009]
ab=[];at=[]
for x,dh in zip(ax,anal_h):
    h,w,zc=shape(float(x)); z=zc-h*.97
    ab.append((float(x),0,z+.002))
    at.append((float(x)-.012*dh/.052,0,z-dh))
fin_grid('Anal_fin',ab,at)

# Rounded, shallow-emarginate caudal fan. Its trailing boundary sweeps out
# farther above and below the midline, typical of adult Micropterus salmoides.
theta=np.linspace(-math.pi/2,math.pi/2,21)
cb=[];ct=[]
for a in theta:
    z=.010*math.sin(a)
    cb.append((-.176,0,z))
    depth=.069*math.sin(a)
    az=abs(depth)
    trailing=-.245+.003*(1-min(az/.04,1))**2+.033*max((az-.04)/.029,0)**2
    ct.append((trailing,0,depth))
fin_grid('Caudal_rounded_emarginate',cb,ct,ray_step=1)

# Broad mobile paired pectorals sweep back from opercula; pelvic fins sit below.
for side,label in ((-1,'right'),(1,'left')):
    n=13; pb=[];pt=[]
    origin=Vector((.050,surface_y(.050,-.007,side)+side*.0005,-.007))
    reach=Vector((-.80,side*.45,-.30)).normalized()
    spread=Vector((-.35,0,.94)).normalized()
    for i in range(n):
        a=i/(n-1)
        phi=-math.pi/3+2*math.pi/3*a
        base=origin+spread*(.003*math.sin(phi))
        tip=origin+reach*(.066*math.cos(phi))+spread*(.024*math.sin(phi))
        pb.append(tuple(base)); pt.append(tuple(tip))
    fin_grid(f'Pectoral_{label}',pb,pt,material=PECTORAL_MAT,ray_step=1)
    vb=[];vt=[]
    for i in range(11):
        a=i/10
        x=.005-.025*a
        h,w,zc=shape(x); z=zc-h*.94
        vb.append((x,side*.012,z))
        vt.append((-.030-.030*math.sin(a*math.pi),side*.040, -.087+.012*a))
    fin_grid(f'Pelvic_{label}',vb,vt,ray_step=1)

# Convert and join rays into one export object to avoid one draw call per ray.
for name,points,radius in ray_curves:
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.resolution_u=2
    cu.bevel_depth=radius; cu.bevel_resolution=0
    cu.use_fill_caps=True
    sp=cu.splines.new('POLY'); sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points): p.co=(*co,1)
    ob=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(ob)
    ob.data.materials.append(PECTORAL_RAY if name.startswith('Pectoral') else FIN_RAY)
    bpy.context.view_layer.objects.active=ob; ob.select_set(True)
    bpy.ops.object.convert(target='MESH'); ob.select_set(False)
    bm=bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
    for _ in range(3):
        boundary=[e for e in bm.edges if e.is_boundary]
        if not boundary: break
        bmesh.ops.holes_fill(bm,edges=boundary)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(ob.data); bm.free(); ob.data.update()
    FISH.append(ob)
ray_objects=[ob for ob in FISH if '_ray' in ob.name and ob.name.rsplit('_ray',1)[-1].isdigit()]
FISH=[ob for ob in FISH if ob not in ray_objects]
bpy.ops.object.select_all(action='DESELECT')
for ob in ray_objects: ob.select_set(True)
bpy.context.view_layer.objects.active=ray_objects[0]
bpy.ops.object.join()
ray_objects[0].name='Fin_rays_combined'
FISH.append(ray_objects[0])

# The fin membrane side/base caps and jaw ends must share consistent outward
# winding so the standard single-sided glTF material renders from every view.
for ob in FISH:
    bm=bmesh.new(); bm.from_mesh(ob.data)
    if all(e.is_manifold for e in bm.edges):
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(ob.data); ob.data.update()
    bm.free()

# Mild caudal peduncle scale highlight, rendered as a fine organic rim.
# Shared origin remains at body center, usable by a later dedicated rig stage.
for ob in FISH:
    ob.hide_render=False

# Export a joined copy for low draw-call playback. The anatomical source
# objects remain independent in the .blend for later skinning and review.
bpy.ops.object.select_all(action='DESELECT')
export_copies=[]
for source in FISH:
    copy=source.copy(); copy.data=source.data.copy(); copy.name='Export_'+source.name
    bpy.context.collection.objects.link(copy); copy.select_set(True)
    export_copies.append(copy)
bpy.context.view_layer.objects.active=export_copies[0]
bpy.ops.object.join()
export_mesh=export_copies[0]; export_mesh.name='Bass_LOD0'
export_bm=bmesh.new(); export_bm.from_mesh(export_mesh.data)
bmesh.ops.triangulate(export_bm,faces=[f for f in export_bm.faces if len(f.verts)>4])
export_bm.to_mesh(export_mesh.data); export_bm.free(); export_mesh.data.update()
glb_path=OUT/'largemouth-bass.glb'
bpy.ops.export_scene.gltf(filepath=str(glb_path),export_format='GLB',use_selection=True,
                          export_apply=True,export_yup=True,export_materials='EXPORT',
                          export_image_format='AUTO',export_texcoords=True,
                          export_normals=True,export_tangents=True)
bpy.data.objects.remove(export_mesh,do_unlink=True)

for ob in FISH:
    ob.data.calc_loop_triangles()
triangles=sum(len(ob.data.loop_triangles) for ob in FISH)
# Real extents include fin tips; validate orientation and size in source coordinates.
all_points=[ob.matrix_world @ v.co for ob in FISH for v in ob.data.vertices]
mins=[min(p[i] for p in all_points) for i in range(3)]
maxs=[max(p[i] for p in all_points) for i in range(3)]
stats={'species':'Micropterus salmoides','seed':A.seed,'blender':bpy.app.version_string,
       'vertices':sum(len(ob.data.vertices) for ob in FISH),'triangles':triangles,
       'mesh_objects':len(FISH),'materials':len({mat.name for ob in FISH for mat in ob.data.materials}),
       'bounds_min_m':mins,'bounds_max_m':maxs,'length_m':maxs[0]-mins[0],
       'textures':[{'name':body_img.name,'width':W,'height':H},
                   {'name':normal_img.name,'width':W,'height':H},
                   {'name':rough_img.name,'width':W,'height':H},
                   {'name':fin_img.name,'width':fw,'height':fh},
                   {'name':pectoral_img.name,'width':fw,'height':fh}],
       'rigged':False,'animated':False,
       'render_files':[]}

def topology_metrics(ob):
    bm=bmesh.new(); bm.from_mesh(ob.data); bm.normal_update()
    boundary=sum(1 for e in bm.edges if e.is_boundary)
    nonmanifold=sum(1 for e in bm.edges if not e.is_manifold)
    zero_area=sum(1 for f in bm.faces if f.calc_area()<1e-12)
    unseen=set(bm.verts); components=0
    while unseen:
        components+=1; stack=[unseen.pop()]
        while stack:
            vertex=stack.pop()
            for e in vertex.link_edges:
                other=e.other_vert(vertex)
                if other in unseen:
                    unseen.remove(other); stack.append(other)
    signed_volume=bm.calc_volume(signed=True) if boundary==0 and nonmanifold==0 else None
    bm.free()
    uv_finite=all(math.isfinite(coord) for layer in ob.data.uv_layers
                  for loop in layer.data for coord in loop.uv)
    normal_finite=all(all(math.isfinite(c) for c in poly.normal) for poly in ob.data.polygons)
    return {'vertices':len(ob.data.vertices),'triangles':len(ob.data.loop_triangles),
            'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,
            'zero_area_faces':zero_area,'connected_components':components,
            'signed_volume_m3':signed_volume,'uv_finite':uv_finite,
            'normals_finite':normal_finite}

stats['mesh_validation']={ob.name:topology_metrics(ob) for ob in FISH}
if stats['mesh_validation'][body.name]['boundary_edges'] or stats['mesh_validation'][body.name]['nonmanifold_edges']:
    raise RuntimeError('Body must be a closed manifold including the recessed mouth cavity')

# Six orthographic studio views on a neutral blue-gray background. Camera
# placement names describe the face of the fish visible in Blender coordinates.
world=bpy.context.scene.world
world.color=(.14,.19,.20)
world.use_nodes=True
bg=world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(.20,.27,.30,1); bg.inputs['Strength'].default_value=.65
bpy.context.scene.render.engine='CYCLES'
bpy.context.scene.cycles.samples=A.render_samples
bpy.context.scene.cycles.use_denoising=False
bpy.context.scene.render.resolution_x=1200
bpy.context.scene.render.resolution_y=800
bpy.context.scene.render.resolution_percentage=100
bpy.context.scene.render.image_settings.file_format='PNG'
bpy.context.scene.render.film_transparent=False
bpy.context.scene.view_settings.view_transform='AgX'
# Two large softboxes reveal the scales, head planes, and translucent-looking fins.
for name,loc,power,size in [('key',(.3,-.55,.5),20,1.0),('fill',(-.4,.38,.25),10,.8),('top',(.0,.0,.60),12,.7)]:
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size
    ob=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(ob); ob.location=loc
    ob.rotation_euler=(Vector((0,0,0))-ob.location).to_track_quat('-Z','Y').to_euler()
cam_data=bpy.data.cameras.new('Reference_camera'); cam=bpy.data.objects.new('Reference_camera',cam_data)
bpy.context.collection.objects.link(cam); bpy.context.scene.camera=cam
cam_data.type='ORTHO'; cam_data.ortho_scale=.56; cam_data.lens=50
views={
    'left':(.0,.8,0),
    'right':(.0,-.8,0),
    'front':(.8,0,0),
    'rear':(-.8,0,0),
    'top':(.0,0,.8),
    'front_three_quarter':(.62,-.64,.19)
}
for view,position in views.items():
    if A.render_view and view!=A.render_view:
        continue
    cam.location=position
    cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
    if view in ('front','rear'):
        cam_data.ortho_scale=.38
    elif view=='top':
        cam_data.ortho_scale=.52
    elif view=='front_three_quarter':
        cam_data.ortho_scale=.54
    else:
        cam_data.ortho_scale=.54
    path=OUT/f'{view}.png'
    bpy.context.scene.render.filepath=str(path)
    if not A.skip_renders:
        bpy.ops.render.render(write_still=True)
        stats['render_files'].append(path.name)
cam.location=views['front_three_quarter']
cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
cam_data.ortho_scale=.54
bpy.context.scene.render.filepath=str(OUT/'front_three_quarter.png')
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
bpy.context.view_layer.objects.active=body
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'largemouth-bass.blend'))
(OUT/'largemouth-bass-stats.json').write_text(json.dumps(stats,indent=2)+'\n')
print('BASS_STATS',json.dumps({key:stats[key] for key in
      ('species','seed','vertices','triangles','mesh_objects','materials','length_m','render_files')}))

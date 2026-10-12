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
from mathutils.geometry import tessellate_polygon


def args():
    p = argparse.ArgumentParser()
    p.add_argument('--seed', type=int, default=1947)
    p.add_argument('--output', '--output-dir', dest='output', default='artifacts/c1')
    p.add_argument('--render-samples', type=int, default=128)
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

# Physically scaled original maps calibrated against the three real photos.
sys.path.insert(0,str(Path(__file__).resolve().parent))
from bass_materials import build_materials


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
    (-.184, .019, .0028, .000), (-.176, .023, .010, .000),
    (-.164, .024, .014, .000), (-.142, .031, .022, .001),
    (-.113, .040, .028, .002),
    (-.078, .046, .032, .003), (-.039, .056, .038, .004),
    (.000, .063, .043, .004), (.037, .068, .045, .005),
    (.074, .068, .043, .005), (.111, .061, .039, .006),
    (.145, .047, .033, .006), (.175, .034, .027, .006),
    (.195, .025, .028, .006), (.207, .014, .029, .005)
]

globals().update(build_materials(OUT,A.seed,PROFILE))

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

# The torso is a single skin that bifurcates into an upper skull and a
# continuous lower mandible behind the eye. The two branches share a rear
# hinge; their inner palate/tongue faces open into the mouth towards the lip.
NR, SPLIT, BRIDGE = 56, 17, 12
HINGE = .151
TRUNK_X = np.unique(np.concatenate((np.linspace(PROFILE[0][0], HINGE, 39),
                                    np.arange(.078,HINGE,.003))))
NOSE_X = .2095
HEAD_X = np.linspace(HINGE, NOSE_X, 17)
# The corner lies behind/below the eye; the bite rises across a broad, blunt
# muzzle. The small resting gape is real space between two skinned surfaces.
mouth_marks=((HINGE,shape(HINGE)[2]+shape(HINGE)[0]*math.cos(2*math.pi*SPLIT/NR)),
             (.158,-.0083),(.167,-.0068),(.177,-.0038),
             (.187,-.0005),(.198,.0031),(.207,.0044))

def mouth_height(x):
    # Cubic tissue contour avoids the angular joins of a piecewise-linear slot.
    return cranial_curve_x(x,mouth_marks)

def mouth_gape(x):
    # A rounded commissure opens faster than a triangular vanishing slit,
    # then settles to a narrow, relaxed anterior bite.
    t=max(0,min(1,(x-HINGE)/(NOSE_X-HINGE)))
    return .0016*math.sin(math.pi*.5*t)**.65

OUTER_OPERCULUM = ((-.040,.124),(-.028,.106),(-.010,.096),
                   (.008,.098),(.022,.116),(.033,.135))
PREOPERCULUM = ((-.039,.155),(-.035,.140),(-.018,.130),
                (.008,.138),(.030,.145))

def cranial_curve_x(z, points):
    if z<=points[0][0]: return points[0][1]
    if z>=points[-1][0]: return points[-1][1]
    for i in range(len(points)-1):
        za,xa=points[i]; zb,xb=points[i+1]
        if za<=z<=zb:
            t=(z-za)/(zb-za)
            before=points[max(0,i-1)]; after=points[min(len(points)-1,i+2)]
            ma=(xb-before[1])/(zb-before[0])
            mb=(after[1]-xa)/(after[0]-za)
            return ((2*t**3-3*t*t+1)*xa+(t**3-2*t*t+t)*(zb-za)*ma+
                    (-2*t**3+3*t*t)*xb+(t**3-t*t)*(zb-za)*mb)
    return points[-1][1]

def smooth01(t):
    t=max(0,min(1,t))
    return t*t*(3-2*t)

def raw_lateral_width(x,z):
    h,w,zc=shape(x)
    radial=max(0,1-((z-zc)/h)**2)
    plane=.23*math.exp(-((x-.137)/.050)**2)
    return w*radial**((1-plane)/2)

def cranial_plane_y(x,z,base):
    outer_x=cranial_curve_x(z,OUTER_OPERCULUM)
    inner_x=cranial_curve_x(z,PREOPERCULUM)
    span=max(.012,inner_x-outer_x)
    across=(x-outer_x)/span
    vertical=smooth01((z+.045)/.018)*(1-smooth01((z-.018)/.020))
    outer_fade=.003/span
    blend=.85*smooth01(across/outer_fade)*(1-smooth01((across-.75)/.25))*vertical
    # An actual lateral plane anchored to the differently sized torso and
    # anterior skull sections. The rear bony cover sits slightly proud.
    outer_y=raw_lateral_width(outer_x,z)+.0030
    inner_y=raw_lateral_width(inner_x,z)+.0003
    target=outer_y+(inner_y-outer_y)*max(0,min(1,across))
    return base*(1-blend)+target*blend

def cheek_relief(x,z):
    # One low oblong maxillary form follows the side of the upper jaw. A
    # rounded rear terminal sits aft of the eye; the opposite end fades into
    # the upper lip. Its supported lower turn stays above the mouth corner.
    # Rounded oblong rear maxilla, below/behind the eye. Elliptic support
    # provides a return into the cheek rather than a rectangular wedge.
    terminal=math.sqrt(((x-.1535)/.0145)**2+((z-.0030)/.0105)**2)
    maxilla=.0048*(1-smooth01((terminal-.62)/.43))
    maxilla_edge=-.0008*math.exp(-((terminal-1.12)/.16)**2)
    # A narrower anterior arm blends the plate into the upper lip.
    arm=smooth01((x-.159)/.012)*(1-smooth01((x-.189)/.013))
    above=z-mouth_height(max(x,HINGE))
    maxilla+=.0022*arm*math.exp(-((above-.0048)/.0045)**2)
    orbital_r=math.sqrt(((x-.169)/.0118)**2+((z-.024)/.0106)**2)
    orbit=-.0024*math.exp(-(orbital_r/.72)**2)+.0012*math.exp(-((orbital_r-1)/.30)**2)
    return orbit+maxilla+maxilla_edge

def skin_point(x,theta,z_override=None,lower=False):
    h,w,zc=shape(x)
    z=zc+h*math.cos(theta) if z_override is None else z_override
    s=math.sin(theta)
    plane=.23*math.exp(-((x-.137)/.050)**2)
    width=cranial_plane_y(x,z,w*abs(s)**(1-plane))
    y=math.copysign(width,s)
    y+=math.copysign(cheek_relief(x,z)*abs(s)**2,y)
    if z_override is None:
        # Lift the skin into the median-fin insertions. The rounded shoulders
        # fade across the back/belly and into the adjoining body, so the fin
        # does not start at a straight intersection of two unrelated sheets.
        top_mask=smooth01((x+.126)/.022)*(1-smooth01((x-.082)/.026))
        bottom_mask=smooth01((x+.153)/.019)*(1-smooth01((x+.062)/.018))
        if z>zc:
            z+=.0015*top_mask*math.exp(-(y/.013)**2)
        else:
            z-=.0012*bottom_mask*math.exp(-(y/.010)**2)
    r=max(0,min(1,(x-.175)/.032))
    xx=x-(.0100 if lower else .0105)*r*math.sin(theta)**2
    if lower:
        # Set the ventral chin back from its rounded forward lip. Without
        # this, the underside and cap center sit almost in the same plane.
        xx+=.0024*r-.0090*r*max(0,-math.cos(theta))**2
    else:
        xx-=.0020*r*max(0,math.cos(theta))**2
    return (xx,y,z)

verts=[]; faces=[]; uvs=[]; face_mats=[]; face_regions=[]; jaw_weights=[]
def append_face(ids, texcoords, material=0, region=0):
    # A UV of exactly 1 repeats to column 0 (the caudal texture) on glTF
    # samplers. Keep the terminal snout inside the final head texel instead.
    head_u_limit=1-1/W
    faces.append(tuple(ids)); uvs.append(tuple((min(u,head_u_limit),v) for u,v in texcoords))
    face_mats.append(material); face_regions.append(region)

for x in TRUNK_X:
    for k in range(NR):
        verts.append(skin_point(float(x),2*math.pi*k/NR)); jaw_weights.append(0.0)
for i in range(len(TRUNK_X)-1):
    for k in range(NR):
        kn=(k+1)%NR
        u0=(float(TRUNK_X[i])-PROFILE[0][0])/(PROFILE[-1][0]-PROFILE[0][0])
        u1=(float(TRUNK_X[i+1])-PROFILE[0][0])/(PROFILE[-1][0]-PROFILE[0][0])
        append_face((i*NR+k,(i+1)*NR+k,(i+1)*NR+kn,i*NR+kn),
                    ((u0,k/NR),(u1,k/NR),(u1,(k+1)/NR),(u0,(k+1)/NR)))
append_face(tuple(range(NR)),tuple((0,k/NR) for k in range(NR)))

upper_keys=list(range(-SPLIT,SPLIT+1))
lower_keys=list(range(SPLIT,NR-SPLIT+1))
branch_rings={'upper':[],'lower':[]}
branch_uvs={'upper':[],'lower':[]}
# Extra lateral samples round the lip-to-palate turn on both sides. They are
# shared at the hinge, keeping one closed body while giving each oral surface
# enough actual geometry to roll in three dimensions.
inner_fracs=(.97,.90,.79,.64,.46,.25,0,-.25,-.46,-.64,-.79,-.90,-.97)
for i,x_raw in enumerate(HEAD_X):
    x=float(x_raw); h,w,zc=shape(x)
    r=max(0,min(1,(x-.175)/.032))
    base_edge=zc+h*math.cos(2*math.pi*SPLIT/NR)
    target=mouth_height(x); gap=mouth_gape(x)
    if i==0: target=base_edge; gap=0
    bridge=[]
    edge_width=abs(skin_point(x,2*math.pi*SPLIT/NR)[1])
    if i==0:
        for frac in inner_fracs:
            y=edge_width*frac
            bridge.append(len(verts)); verts.append((x,y,target)); jaw_weights.append(0.0)
    for part,keys in (('upper',upper_keys),('lower',lower_keys)):
        ring=[]; ring_uv=[]
        for key in keys:
            k=key%NR; a=2*math.pi*key/NR
            if i==0:
                vi=(len(TRUNK_X)-1)*NR+k
            else:
                baseline=zc+h*math.cos(a)
                if part=='upper':
                    influence=(1-math.cos(a))/(1-math.cos(2*math.pi*SPLIT/NR))
                    desired=target+gap*.5
                else:
                    influence=(1+math.cos(a))/(1+math.cos(2*math.pi*SPLIT/NR))
                    desired=target-gap*.5
                z=baseline+(desired-base_edge)*influence
                # Taper skull/chin thickness into the anterior lip itself.
                # The former full-height last section forced a blunt cap.
                nose=smooth01((x-.194)/(NOSE_X-.194))
                z=desired+(z-desired)*(1-(.30 if part=='upper' else .18)*nose)
                arch=max(0,1-(math.sin(a)/math.sin(2*math.pi*SPLIT/NR))**2)
                z+=.0048*smooth01((x-.177)/.030)*arch
                # Roll the outer skin into a fleshy premaxillary and dentary
                # lip. This acts on the last few circumferential skin loops,
                # with its greatest volume just outside the oral edge.
                from_lip=min(abs(key+SPLIT),abs(key-SPLIT)) if part=='upper' else min(abs(key-SPLIT),abs(key-(NR-SPLIT)))
                lip=math.exp(-(from_lip/3.1)**2)*smooth01((x-HINGE)/.020)
                # Keep the bite edge itself nearly closed; the thickening
                # peaks in the neighboring skin loop instead of opening it.
                shoulder=lip*(1-math.exp(-(from_lip/.95)**2))
                z+=(.0008 if part=='upper' else -.0013)*shoulder
                px,py,pz=skin_point(x,a,z,part=='lower')
                px+=.0010*lip
                py+=math.copysign(.0005*lip,py)
                if part=='upper':
                    # The front snout is a domed half-ellipse above the oral
                    # arch, not a compressed full skull section or tube.
                    front_angle=(key/SPLIT)*math.pi*.5
                    lip_width=abs(skin_point(x,2*math.pi*SPLIT/NR,desired)[1])+.0005*smooth01((x-HINGE)/.020)
                    snout=smooth01((x-.180)/(NOSE_X-.180))
                    top=cranial_curve_x(x,((HINGE,shape(HINGE)[2]+shape(HINGE)[0]),
                                          (.177,.039),(.190,.028),(.200,.021),
                                          (NOSE_X,.0172)))
                    py=py*(1-snout)+lip_width*math.sin(front_angle)*snout
                    pz=pz*(1-snout)+(desired+(top-desired)*math.cos(front_angle))*snout
                    px=x+.0005*r-.006*r*(py/lip_width)**2-.0070*snout*math.cos(front_angle)**2
                else:
                    front_angle=(key-SPLIT)/(NR-2*SPLIT)*math.pi
                    lip_width=abs(skin_point(x,2*math.pi*SPLIT/NR,desired,True)[1])+.0005*smooth01((x-HINGE)/.020)
                    py=py*(1-nose)+lip_width*math.cos(front_angle)*nose
                    pz=pz*(1-nose)+(desired-.012*math.sin(front_angle))*nose
                vi=len(verts); verts.append((px,py,pz))
                jaw_weights.append(smooth01((x-HINGE)/.030) if part=='lower' else 0.0)
            ring.append(vi); ring_uv.append(((x-PROFILE[0][0])/(PROFILE[-1][0]-PROFILE[0][0]),key/NR))
        lip_a=verts[ring[0]]; lip_b=verts[ring[-1]]
        # Interior samples must follow the actual deformed lip endpoints,
        # not the undeformed torso ellipse (which can put walls outside skin).
        actual_width=(abs(lip_a[1])+abs(lip_b[1]))*.5
        for j in (range(len(inner_fracs)) if part=='upper' else range(len(inner_fracs)-1,-1,-1)):
            if i==0:
                vi=bridge[j]
            else:
                frac=inner_fracs[j]
                y=actual_width*frac
                arch=max(0,1-frac**2)
                oral_t=max(0,min(1,(x-HINGE)/(NOSE_X-HINGE)))
                # The roof and floor deepen behind the rolled anterior rim;
                # carrying maximum depth to the cap made a broad flat scoop.
                depth=(.0050*math.sin(math.pi*oral_t)**1.4+.00015*oral_t if part=='upper'
                       else .0045*math.sin(math.pi*oral_t)**.8+.0015*oral_t**5)
                bow=depth*arch
                # Behind the horseshoe-shaped lip, a recessed roof and floor
                # carry the cavity aft to the common hinge. A tighter lateral
                # turn makes the oral edge a rounded lip instead of a sheet.
                lip_front=smooth01((x-.189)/.018)
                # Do not push the first cavity section through the shared
                # hinge plane: that would cross the upper/lower branch fan.
                inset=min(.0055,.35*(x-HINGE))
                edge_x=(lip_a[0]+lip_b[0])*.5
                bridge_x=edge_x+(x-inset*(1-.82*lip_front)-.0015*lip_front-edge_x)*arch
                inner_roll=(.0020*math.exp(-((abs(frac)-.79)/.15)**2)
                            *(1-.85*lip_front))
                # Both halves follow one raised anterior U across the face;
                # the common lift bends the bite without widening its gap.
                bite_arch=.0048*smooth01((x-.177)/.030)*arch
                z=target+bite_arch+(gap*.5+.0006*arch+inner_roll+bow)*(1 if part=='upper' else -1)
                vi=len(verts); verts.append((bridge_x,y,z))
                jaw_weights.append(smooth01((x-HINGE)/.030) if part=='lower' else 0.0)
            ring.append(vi)
            ring_uv.append(((x-PROFILE[0][0])/(PROFILE[-1][0]-PROFILE[0][0]),.5+(1-inner_fracs[j])*.06))
        if i==len(HEAD_X)-1:
            # A shared convex horseshoe section turns exterior skin into oral
            # tissue. Ordered X sections eliminate cap meridian overtaking.
            for vi in ring:
                px,py,pz=verts[vi]
                if vi not in ring[:len(keys)]:
                    px=x+.0005-.006*(py/actual_width)**2
                elif part=='lower':
                    px=x+.0005-.006*(py/actual_width)**2-.0080*max(0,math.sin((keys[ring.index(vi)]-SPLIT)/(NR-2*SPLIT)*math.pi))**2
                verts[vi]=(px,py,pz)
        branch_rings[part].append(ring)
        branch_uvs[part].append(ring_uv)

for part in ('upper','lower'):
    rings=branch_rings[part]; uv_rings=branch_uvs[part]
    outside_count=len(upper_keys if part=='upper' else lower_keys)
    for i in range(len(rings)-1):
        for j in range(len(rings[i])):
            jn=(j+1)%len(rings[i]); m=1 if j>=outside_count-1 else 0
            append_face((rings[i][j],rings[i+1][j],rings[i+1][jn],rings[i][jn]),
                        (uv_rings[i][j],uv_rings[i+1][j],uv_rings[i+1][jn],uv_rings[i][jn]),m,
                        1 if part=='upper' else 2)
    # Close the U-shaped tissue rim with a curved strip, not a radial cap.
    # An arched lip section is concave: contracting it to one center causes
    # folds or forces a thick planar panel. Its Y/Z outline is tessellated
    # while X follows the same horseshoe as the exterior and oral surfaces.
    last=rings[-1]; last_uv=uv_rings[-1]
    final_x=float(HEAD_X[-1]); h,w,zc=shape(final_x)
    # Each section retains full lateral width and converges in tissue
    # thickness around the bite arch; it never contracts to a center point.
    actual_width=max(abs(verts[vi][1]) for vi in last)
    boundary,boundary_uv=last,last_uv
    # One tissue turn replaces the redundant cap rails. A recessed crown
    # and chin give the turn axial depth without an applied bulb at the tip.
    for thickness,advance in ((.50,.0007),):
        next_ring=[]; next_uv=[]
        for vi,(u,v) in zip(boundary,boundary_uv):
            px,py,pz=verts[vi]
            arch=max(0,1-(py/actual_width)**2)
            if part=='upper':
                mid_z=mouth_height(final_x)+.0008+.5*(.0120*math.sqrt(arch)+.0055*arch)
            else:
                mid_z=mouth_height(final_x)-.0008+.5*(.0027*arch-.0120*math.sqrt(arch))
            front_x=final_x+.0005+advance-.006*(py/actual_width)**2
            nx=px+(front_x-px)*.85
            next_ring.append(len(verts))
            verts.append((nx,py,mid_z+(pz-mid_z)*thickness))
            jaw_weights.append(1.0 if part=='lower' else 0.0)
            next_uv.append((u,v))
        for j in range(len(last)):
            jn=(j+1)%len(last)
            append_face((last[j],next_ring[j],next_ring[jn],last[jn]),
                        (last_uv[j],next_uv[j],next_uv[jn],last_uv[jn]),0,
                        1 if part=='upper' else 2)
        last,last_uv=next_ring,next_uv
    contour=[Vector((verts[vi][1],verts[vi][2],0)) for vi in last]
    for triangle in tessellate_polygon([contour]):
        js=list(reversed(triangle))
        append_face(tuple(last[j] for j in js),tuple(last_uv[j] for j in js),0,
                    1 if part=='upper' else 2)

body=mesh('Body_quadrilateral_loft',verts,faces,BODY_MAT,uvs)
body.data.materials.append(MOUTH)
for poly,idx in zip(body.data.polygons,face_mats): poly.material_index=idx
region_attr=body.data.attributes.new(name='anatomical_region',type='INT',domain='FACE')
for datum,region in zip(region_attr.data,face_regions): datum.value=region
jaw_attr=body.data.attributes.new(name='jaw_open_weight',type='FLOAT',domain='POINT')
for datum,weight in zip(jaw_attr.data,jaw_weights): datum.value=weight
body['jaw_hinge_x']=HINGE
body['jaw_hinge_y']=0.0
body['jaw_hinge_z']=mouth_height(HINGE)
body['jaw_open_axis']='Y'

# Support the oblong maxillary return locally; two circumferential samples
# across its height cannot resolve a rounded plate. Subdivision is confined
# to exterior cheek faces forward of the preserved rear-body boundary.
bm=bmesh.new(); bm.from_mesh(body.data)
regions=bm.faces.layers.int.get('anatomical_region')
relief_layer=bm.verts.layers.float.new('maxillary_interpolation')
for vertex in bm.verts:
    vertex[relief_layer]=cheek_relief(vertex.co.x,vertex.co.z)
original_vertices={vertex:index for index,vertex in enumerate(bm.verts)}
original_positions={vertex:vertex.co.copy() for vertex in bm.verts}
support_edges=set()
for face in bm.faces:
    center=face.calc_center_median()
    if (face.material_index==0 and face[regions] in (0,1)
        and .142<=center.x<=.174 and -.008<=center.z<=.015
        and abs(center.y)>=.022 and all(v.co.x>.132 for v in face.verts)):
        support_edges.update(face.edges)
if support_edges:
    bmesh.ops.subdivide_edges(bm,edges=list(support_edges),cuts=1,use_grid_fill=True)
    for vertex in bm.verts:
        if vertex not in original_vertices:
            delta=cheek_relief(vertex.co.x,vertex.co.z)-vertex[relief_layer]
            vertex.co.y+=delta*(1 if vertex.co.y>=0 else -1)
        else:
            vertex.co=original_positions[vertex]
    # Preserve the source vertex IDs used by the rear-body regression hash.
    new_order={vertex:index+len(original_vertices) for index,vertex in enumerate(bm.verts)
               if vertex not in original_vertices}
    bm.verts.sort(key=lambda vertex: original_vertices.get(vertex,new_order.get(vertex)))
    bm.verts.index_update()
bm.verts.layers.float.remove(relief_layer)
bm.to_mesh(body.data); bm.free(); body.data.update()

def uv_sphere(name, loc, scale, material, segments=24, rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(material)
    for p in ob.data.polygons: p.use_smooth = True
    FISH.append(ob)
    return ob

# The eye nests into the continuous sculpted cheek on each side.
for side, label in ((-1, 'right'), (1, 'left')):
    ex,ez=.169,.024
    ey=surface_y(ex,ez,side)
    step=.001
    dx=(surface_y(ex+step,ez,side)-surface_y(ex-step,ez,side))/(2*step)
    dz=(surface_y(ex,ez+step,side)-surface_y(ex,ez-step,side))/(2*step)
    outward=Vector((-side*dx,side,-side*dz)).normalized()
    eye_base=Vector((ex,ey,ez))
    # A thin local-Y dome follows the actual skin normal on both sides.
    # Keep the pupil in front of the iris and the iris in front of the rim.
    eye_rotation=outward.to_track_quat('Y','Z')
    for eye_name,depth,offset,eye_size,eye_mat in (
        (f'Eye_orbit_{label}',-.0004,(0,0,0),(.0092,.0011,.0092),EYE_RIM),
        (f'Iris_{label}',.0006,(0,0,0),(.0086,.0013,.0086),IRIS),
        (f'Pupil_{label}',.0018,(.0004,0,0),(.0056,.0008,.0056),PUPIL)):
        eye=uv_sphere(eye_name,eye_base+outward*depth+Vector(offset),eye_size,eye_mat)
        if eye_name.startswith('Iris_'):
            iris_uv=eye.data.uv_layers.active or eye.data.uv_layers.new(name='UVMap')
            for loop in eye.data.loops:
                co=eye.data.vertices[loop.vertex_index].co
                iu=.5+.5*co.x/.0086; iv=.5+.5*co.z/.0086
                iris_uv.data[loop.index].uv=((.5+127*iu)/512,(384.5+127*iv)/512)
        eye.rotation_euler=eye_rotation.to_euler()

# The membrane follows gently curved rays; a shallow dip between rays avoids
# ruler-straight sheets without the repeated saw teeth of the first model.
ray_curves=[]

def fin_grid(name, bases, tips, material=FIN_MAT, ray_step=1, thick=.00022):
    assert len(bases)==len(tips)
    source_bases=[Vector(p) for p in bases]
    source_tips=[Vector(p) for p in tips]
    scallop=.0022 if name.startswith('Dorsal_spiny') else .00055
    interp_b=[]; interp_t=[]; ribs=[]; phases=[]
    for i in range(len(bases)-1):
        interp_b.append(source_bases[i]); interp_t.append(source_tips[i])
        ribs.append(.25); phases.append(.73*i+.2*math.sin(i*1.7))
        mid_b=(source_bases[i]+source_bases[i+1])*.5
        mid_t=(source_tips[i]+source_tips[i+1])*.5
        inward=(mid_b-mid_t).normalized()
        interp_b.append(mid_b); interp_t.append(mid_t+inward*scallop*(.88+.18*math.sin(i*2.3)))
        ribs.append(-.85+.12*math.sin(i*2.1)); phases.append(.73*(i+.5))
    interp_b.append(source_bases[-1]); interp_t.append(source_tips[-1])
    ribs.append(.25); phases.append(.73*(len(bases)-1))
    n=len(interp_b); ts=(0,.08,.20,.42,.70,1)
    stride=n*len(ts)
    vs=[]; fs=[]; uv=[]
    pair_sign=1 if name.endswith('_left') else -1 if name.endswith('_right') else 0
    curve_x=.0019 if 'Dorsal' in name else -.0016 if name.startswith('Anal') else .0008
    # Thickness follows the actual fan normal. A paired fin lies obliquely
    # against the flank; offsetting only in Y made a square, glued-on hinge.
    normals=[]
    for i,(b,t) in enumerate(zip(interp_b,interp_t)):
        lo=max(0,i-1); hi=min(n-1,i+1)
        lateral=interp_t[hi]-interp_t[lo]
        normal=(t-b).cross(lateral)
        if normal.length<1e-8:
            normal=Vector((0,pair_sign or 1,0))
        else:
            normal.normalize()
        if normal.y*(pair_sign or 1)<0: normal.negate()
        normals.append(normal)
    def point(b,t,q,side,rib,phase,normal):
        bend=math.sin(math.pi*q)
        # The first fifth stays inside the skin and swells into a rounded
        # root; the membrane grows out of it and thins towards the margin.
        span_q=q**(1.22 if pair_sign==0 else 1.43)
        p=b.lerp(t,span_q)
        p.x+=curve_x*bend*(1+.23*math.sin(b.x*390))+.0007*math.sin(phase+q*2.1)*bend
        p.z+=.00045*math.cos(phase+q*1.3)*bend
        median_camber=(.00125+.00028*math.sin(b.x*270))*bend if pair_sign==0 else 0
        slack_size=.00012 if name.startswith('Caudal') else .00065
        membrane_slack=(pair_sign if pair_sign else 1)*slack_size*rib*bend
        if name.startswith('Caudal'):
            # Embed the caudal shaft well ahead of the body tip. Its root is
            # oval in section, narrowing in Y towards dorsal/ventral rays.
            oval=math.sqrt(max(.25,1-.75*(b.z/.016)**2))
            root_thickness=.010*oval*(1-q)**3
        elif pair_sign==0:
            # The skin itself supplies the broad median root. Keep its
            # emerging edge close to the body's smooth dorsal/ventral tangent.
            root_thickness=.0020*(1-q)**8+.0008*math.exp(-((q-.34)/.16)**2)
        else:
            root_thickness=.0043*(1-q)**3
        half_thickness=thick+root_thickness
        p.y+=median_camber+pair_sign*.0011*bend+membrane_slack
        p+=normal*(half_thickness if side==1 else -half_thickness)
        return p
    for side in (0,1):
        for b,t,rib,phase,normal in zip(interp_b,interp_t,ribs,phases,normals):
            for q in ts:
                vs.append(tuple(point(b,t,q,side,rib,phase,normal)))
    for side in (0,1):
        for i in range(n-1):
            for j in range(len(ts)-1):
                a=side*stride+i*len(ts)+j
                b=a+len(ts)
                face=(a,b,b+1,a+1) if side==0 else (a+1,b+1,b,a)
                fs.append(face)
                uvpoints=((i/(n-1),ts[j]),((i+1)/(n-1),ts[j]),
                          ((i+1)/(n-1),ts[j+1]),(i/(n-1),ts[j+1]))
                uv.append(uvpoints if side==0 else tuple(reversed(uvpoints)))
    for i in range(n-1):
        a=i*len(ts)+len(ts)-1; b=(i+1)*len(ts)+len(ts)-1
        fs.append((a,b,b+stride,a+stride)); uv.append(((0,0),(1,0),(1,1),(0,1)))
        a=i*len(ts); b=(i+1)*len(ts)
        fs.append((a,a+stride,b+stride,b)); uv.append(((0,0),(0,1),(1,1),(1,0)))
    for i in (0,n-1):
        for j in range(len(ts)-1):
            a=i*len(ts)+j
            fs.append((a,a+1,a+1+stride,a+stride))
            uv.append(((0,0),(1,0),(1,1),(0,1)))
    ob=mesh(name,vs,fs,material,uv)
    if name.startswith('Pectoral_'):
        for loop in ob.data.uv_layers.active.data:
            loop.uv=((.5+511*loop.uv.x)/512,(.5+383*loop.uv.y)/512)
    for i in range(0,len(source_bases),ray_step):
        b=source_bases[i]; t=source_tips[i]
        if (t-b).length<=.006: continue
        outer=1 if pair_sign>=0 else 0
        phase=.73*i+.2*math.sin(i*1.7)
        normal=normals[2*i]
        points=[point(b,t,q,outer,.25,phase,normal) for q in (0,.25,.50,.75,1)]
        radius=.00024 if name.startswith('Dorsal_spiny') else .00018 if name.startswith('Caudal') else .00014
        ray_curves.append((name+f'_ray{i}',points,radius))
        if name.startswith(('Dorsal_soft','Anal','Pectoral','Pelvic')) and i<len(source_bases)-1:
            # Soft rays bifurcate only near the margin, as in the photograph.
            neighboring=source_tips[i+1]-t
            branch=[point(b,t,q,outer,.25,phase,normal)+neighboring*max(0,(q-.66)/.34)*.24
                    for q in (.66,.83,1)]
            ray_curves.append((name+f'_branch{i}',branch,radius*.68))
    return ob

# Dorsal fins: ten spines and a separately lobed soft portion; membranes meet at
# a low notch while remaining anatomically continuous at the base.
spiny_x=np.linspace(.091,-.035,10)
spiny_height=[.011,.021,.028,.034,.033,.038,.036,.030,.022,.006]
spiny_b=[];spiny_t=[]
for x,dh in zip(spiny_x,spiny_height):
    h,w,zc=shape(float(x)); z=zc+h*.96
    spiny_b.append((float(x),0,z-.006))
    spiny_t.append((float(x)-.003,0,z+dh))
fin_grid('Dorsal_spiny_10_spines',spiny_b,spiny_t)
soft_x=np.linspace(-.035,-.119,14)
soft_height=[.008,.019,.032,.044,.050,.053,.054,.052,.048,.041,.034,.025,.015,.006]
soft_b=[];soft_t=[]
for x,dh in zip(soft_x,soft_height):
    h,w,zc=shape(float(x)); z=zc+h*.96
    soft_b.append((float(x),0,z-.006))
    soft_t.append((float(x)-.020*dh/.06,0,z+dh))
fin_grid('Dorsal_soft_14_rays',soft_b,soft_t)

# Anal fin beneath the rear third of the fish.
ax=np.linspace(-.066,-.145,12)
anal_h=[.009,.021,.035,.044,.047,.046,.043,.037,.030,.023,.015,.006]
ab=[];at=[]
for x,dh in zip(ax,anal_h):
    h,w,zc=shape(float(x)); z=zc-h*.97
    ab.append((float(x),0,z+.005))
    at.append((float(x)-.017*dh/.052,0,z-dh))
fin_grid('Anal_fin',ab,at)

# Rounded, shallow-emarginate caudal fan. Its trailing boundary sweeps out
# farther above and below the midline, typical of adult Micropterus salmoides.
theta=np.linspace(-math.pi/2,math.pi/2,21)
cb=[];ct=[]
for a in theta:
    z=.016*math.sin(a)
    cb.append((-.166,0,z))
    depth=.052*math.sin(a)
    az=abs(depth)
    trailing=-.237-.005*math.exp(-((az/.052-.65)/.28)**2)
    if az/.052>.95:
        edge=(az/.052-.95)/.05
        depth-=math.copysign(.0006*edge,depth)
        trailing+=.004*edge
    ct.append((trailing,0,depth))
fin_grid('Caudal_rounded_emarginate',cb,ct,ray_step=2)

# Broad mobile paired pectorals sweep back from opercula; pelvic fins sit below.
for side,label in ((-1,'right'),(1,'left')):
    n=13; pb=[];pt=[]
    origin=Vector((.082,surface_y(.082,-.009,side)-side*.0055,-.009))
    reach=Vector((-.85,side*.53,-.10)).normalized()
    spread=Vector((-.15,side*.18,.97)).normalized()
    for i in range(n):
        a=i/(n-1)
        phi=-math.pi/3+2*math.pi/3*a
        base=origin+spread*(.005*math.sin(phi))
        # The covered attachment is a short oval: its middle appears first,
        # while the two ends emerge from under the cheek skin more gradually.
        rim_fraction=(math.sin(phi)/math.sin(math.pi/3))**2
        base.x+=.003*(1-rim_fraction)
        base.y=surface_y(base.x,base.z,side)-side*(.0055+.002*rim_fraction)
        tip=origin+reach*(.051+.015*math.cos(phi))+spread*(.024*math.sin(phi))
        pb.append(tuple(base)); pt.append(tuple(tip))
    fin_grid(f'Pectoral_{label}',pb,pt,material=PECTORAL_MAT,ray_step=2)
    vb=[];vt=[]
    px=.060; ph,pw,pzc=shape(px)
    pelvic_origin=Vector((px,side*.008,pzc-ph*.94))
    pelvic_reach=Vector((-1,side*.50,-.35)).normalized()
    pelvic_spread=Vector((-.25,side*.15,.96)).normalized()
    for i in range(11):
        phi=-math.pi/4+math.pi/2*i/10
        vb.append(tuple(pelvic_origin+pelvic_spread*(.002*math.sin(phi))))
        vt.append(tuple(pelvic_origin+pelvic_reach*(.047*math.cos(phi))+
                        pelvic_spread*(.014*math.sin(phi))))
    fin_grid(f'Pelvic_{label}',vb,vt,ray_step=2)

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
ray_objects=[ob for ob in FISH if any(tag in ob.name and ob.name.rsplit(tag,1)[-1].isdigit() for tag in ('_ray','_branch'))]
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

# Local refinement can leave subnormal numeric noise on the untouched dorsal
# axis. Keep analytically zero rear-axis coordinates exactly zero, preserving
# the existing indexed position fingerprint without weakening its check.
for vertex in body.data.vertices:
    if vertex.co.x<=.13 and abs(vertex.co.y)<1e-20:
        vertex.co.y=0.0

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
       'iris_atlas_region_pixels':{'image':pectoral_img.name,'x':0,'y':384,'width':128,'height':128},
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

# Five orthographic views and a perspective three-quarter studio view. Camera
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
# Compact studio softboxes reveal scale glints without washing out the dorsum.
for name,loc,power,size in [('key',(.3,-.55,.5),12,.30),('fill',(-.4,.38,.25),6,.30),('top',(.0,.0,.60),5,.25)]:
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
    cam_data.type='PERSP' if view=='front_three_quarter' else 'ORTHO'
    cam_data.lens=60
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
cam_data.type='PERSP'
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

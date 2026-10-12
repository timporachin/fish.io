"""Original, photographically referenced bass PBR maps; no stock pixels copied.

References are recorded in docs/C1_PHOTO_REFERENCES.md. Scale height is in
metres, so normal strength is derived from physical UV dimensions rather than
arbitrary painted lighting. The diffuse maps contain pigment, not reflections.
"""
from pathlib import Path
import math
import bpy
import numpy as np


def _noise(h, w, rows, columns, rng):
    lattice = rng.random((rows + 1, columns + 1))
    yy = np.arange(h) * rows / h
    xx = np.arange(w) * columns / w
    iy, ix = yy.astype(int), xx.astype(int)
    fy, fx = yy - iy, xx - ix
    fy, fx = fy * fy * (3 - 2 * fy), fx * fx * (3 - 2 * fx)
    return ((lattice[iy[:, None], ix] * (1-fy[:, None])
             + lattice[iy[:, None]+1, ix] * fy[:, None]) * (1-fx)
            + (lattice[iy[:, None], ix+1] * (1-fy[:, None])
               + lattice[iy[:, None]+1, ix+1] * fy[:, None]) * fx)


def _image(name, rgba, path, noncolor=False):
    h, w = rgba.shape[:2]
    image = bpy.data.images.new(name, width=w, height=h, alpha=True)
    image.colorspace_settings.name = 'Non-Color' if noncolor else 'sRGB'
    image.pixels.foreach_set(np.asarray(rgba, dtype=np.float32).reshape(-1))
    image.filepath_raw = str(path)
    image.file_format = 'PNG'
    image.save()
    image.pack()
    return image


def _solid(name, color, roughness=.45, specular=.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (*color, 1)
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = 0
    shader.inputs['Specular IOR Level'].default_value = specular
    return mat


def _textured(name, image, roughness=.45, opacity=False):
    mat = _solid(name, (.24, .29, .16), roughness)
    shader = mat.node_tree.nodes.get('Principled BSDF')
    tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex.image = image
    mat.node_tree.links.new(tex.outputs['Color'], shader.inputs['Base Color'])
    if opacity:
        tex.extension = 'EXTEND'
        shader.inputs['IOR'].default_value = 1.35
        shader.inputs['Specular IOR Level'].default_value = .18
        mat.node_tree.links.new(tex.outputs['Alpha'], shader.inputs['Alpha'])
        mat.surface_render_method = 'DITHERED'
        mat.use_transparency_overlap = False
        # Closed thin membranes already have outward faces on both sides.
        # Cull inward-facing triangles in glTF to avoid redundant alpha passes.
        mat.use_backface_culling = True
    return mat


def build_materials(output_dir, seed, profile):
    out = Path(output_dir)
    rng = np.random.default_rng(seed)
    h = w = 1024
    u = np.arange(w)[None, :] / w
    v = np.arange(h)[:, None] / h
    angle = v * math.tau
    c = np.cos(angle)
    fine = _noise(h, w, 190, 190, rng) - .5
    macro = _noise(h, w, 12, 24, rng) - .5
    # The profile photographs show a dark dorsum, brassy olive flank and
    # silvery cream belly, rather than a cloud texture painted across all parts.
    back = np.clip((c-.12)/.75, 0, 1)
    belly = np.clip((-c-.18)/.70, 0, 1)
    flank = np.array([.245, .285, .128])
    dorsum = np.array([.070, .095, .037])
    cream = np.array([.62, .60, .47])
    color = flank*(1-back[..., None]) + dorsum*back[..., None]
    color = color*(1-belly[..., None]) + cream*belly[..., None]
    color = np.broadcast_to(color, (h,w,3)).copy()

    # Approximately sixty columns between gill and peduncle. Each scale has
    # its own pigment and a shallow overlapping dome with a narrow trailing rim.
    rows, columns = 64, 90
    # Warp the orderly overlapping rows gently, then vary each scale's center,
    # crown and broken edge independently. Living skin is not a scallop stamp.
    sy = v*rows+.16*np.sin(u*19+angle*2)+.08*np.sin(u*43-angle*5)
    row = np.floor(sy).astype(int)%rows
    row_jitter = rng.uniform(-.16, .16, (rows+1, 1))
    sx = u*columns + row*.5 + row_jitter[row,0] + .12*np.sin(angle*3+u*23)
    column = np.floor(sx).astype(int) % columns
    lx = np.mod(sx,1)-.5
    ly = np.mod(sy,1)
    cell = rng.random((rows+1, columns))
    pigment = cell[row, column]-.5
    lx += .10*(cell[(row+9)%rows,(column+17)%columns]-.5)
    ly += .07*(cell[(row+4)%rows,(column+11)%columns]-.5)
    width = .48+.14*cell[row,column]
    crown = .35+.18*cell[(row+7)%rows,(column+13)%columns]
    ellipse = np.sqrt(np.clip(1-(lx/width)**2, 0, 1))
    edge_y = .34+crown*ellipse+.09*lx*pigment
    rim_width = .020+.020*cell[(row+11)%rows,(column+5)%columns]
    rim = np.exp(-((ly-edge_y)/rim_width)**2)
    rim *= (.45+.55*cell[(row+8)%rows,(column+2)%columns])*(.70+.30*ellipse)
    dome = np.clip(1-(lx/width)**2,0,1)*np.clip(1-((ly-.47-.08*pigment)/(.48+.10*cell[row,column]))**2,0,1)
    body_scales = 1-np.clip((u-.66)/.18,0,1)
    body_scales += .22*np.clip((u-.66)/.18,0,1)*np.clip((.94-u)/.10,0,1)
    body_scales = np.broadcast_to(body_scales,(h,w))
    # A slight reduction at dorsal/ventral extremes avoids large raised tiles
    # on the skull and underside. Scales remain visible as pigment throughout.
    relief_mask = body_scales*(.45+.55*(1-np.abs(c)))
    color *= (1+.24*pigment[...,None]*dome[...,None]*body_scales[...,None])
    color *= (1-(.31-.13*belly)[...,None]*rim[...,None]*body_scales[...,None])
    gold=np.clip((cell[(row+3)%rows,(column+19)%columns]-.30)/.70,0,1)
    gold *= np.clip(.70+1.1*fine,.25,1)
    flash=dome*np.exp(-((lx+.12*pigment)/(width*.58))**2-((ly-.47-.16*pigment)/(.18+.15*cell[row,column]))**2)
    color += (.018+.095*gold)[...,None]*flash[...,None]*body_scales[...,None]*np.array([1.0,.77,.22])

    # Joined mid-flank blotches resolve into dark individual scales. Boundaries
    # are irregular and run into short vertical pigment drops, not foggy noise.
    wiggle = .028*np.sin(u*47)+.035*(_noise(1,w,1,22,rng)-.5)
    band = np.exp(-((c-(.12+wiggle))/.13)**2)
    lobes=np.zeros((1,w)); drops=np.zeros((h,w))
    centers=np.linspace(.045,.78,13)+rng.uniform(-.016,.016,13)
    for center in centers:
        spread=rng.uniform(.012,.031); strength=rng.uniform(.35,.85)
        spot=np.exp(-((u-center)/spread)**2)
        lobes+=strength*spot
        drops+=strength*spot*np.exp(-((c+rng.uniform(.00,.14))/rng.uniform(.15,.26))**2)
    band = np.clip(band*(.60+.40*np.clip(lobes,0,1))+.30*drops,0,1)
    band *= np.clip((u-.018)/.045,0,1)*np.clip((.79-u)/.11,0,1)
    color *= (1-.70*band[...,None])
    color += (.018*macro+.009*fine)[...,None]

    # Subdued cheek chromatophores and tiny flecks avoid an untextured plastic
    # head. These are original pigment fields, not baked photographic lighting.
    head_mask=np.clip((u-.67)/.12,0,1)*np.clip((.995-u)/.07,0,1)
    cheek_grain=_noise(h,w,70,58,rng)-.5
    cheek_mottle=_noise(h,w,22,20,rng)-.5
    color *= (1+head_mask[...,None]*(.16*cheek_mottle+.10*cheek_grain)[...,None])
    pores=np.clip(-cheek_grain-.20,0,1)*head_mask
    color *= (1-.13*pores[...,None])

    # Fleshy terminal lip is a muted gray olive rather than the cream trunk
    # belly. Keep circumferential symmetry; a shifted polar UV produced swirls.
    snout=np.clip((u-.955)/.035,0,1)
    snout=snout*snout*(3-2*snout)
    lower_snout=np.clip((.45-c)/.30,0,1)
    lower_snout=lower_snout*lower_snout*(3-2*lower_snout)
    lip_zone=snout*lower_snout
    color=color*(1-lip_zone[...,None]) + np.array([.30,.33,.245])*lip_zone[...,None]

    # Registered curved cranial pigment follows the actual bony shield rather
    # than drawing the obsolete straight gill stripe across a sculpted plate.
    sin_a = np.abs(np.sin(angle))
    physical_x=u*.384-.177
    # Use the authored loft itself so remodeling shoulder proportions cannot
    # leave anatomical pigment registered to an obsolete duplicate profile.
    def profile_column(x,column):
        result=np.full_like(x,profile[-1][column])
        result=np.where(x<=profile[0][0],profile[0][column],result)
        for j in range(len(profile)-1):
            a,b=profile[j],profile[j+1]
            previous=profile[max(0,j-1)]; following=profile[min(j+2,len(profile)-1)]
            span=b[0]-a[0]; t=np.clip((x-a[0])/span,0,1)
            ma=(b[column]-previous[column])/(b[0]-previous[0])
            mb=(following[column]-a[column])/(following[0]-a[0])
            value=(2*t**3-3*t*t+1)*a[column]+(t**3-2*t*t+t)*span*ma+(-2*t**3+3*t*t)*b[column]+(t**3-t*t)*span*mb
            result=np.where((x>=a[0])&(x<=b[0]),value,result)
        return result
    cranial_h=profile_column(physical_x,1)
    cranial_z=profile_column(physical_x,3)+cranial_h*c
    outer_points=[(-.040,.124),(-.028,.106),(-.010,.096),(.008,.098),(.022,.116),(.033,.135)]
    inner_points=[(-.039,.155),(-.035,.140),(-.018,.130),(.008,.138),(.030,.145)]
    def curve_x(z,points):
        result=np.full_like(z,points[-1][1])
        result=np.where(z<=points[0][0],points[0][1],result)
        for i in range(len(points)-1):
            za,xa=points[i]; zb,xb=points[i+1]
            before=points[max(0,i-1)]; after=points[min(len(points)-1,i+2)]
            t=np.clip((z-za)/(zb-za),0,1)
            ma=(xb-before[1])/(zb-before[0]); mb=(after[1]-xa)/(after[0]-za)
            value=(2*t**3-3*t*t+1)*xa+(t**3-2*t*t+t)*(zb-za)*ma+(-2*t**3+3*t*t)*xb+(t**3-t*t)*(zb-za)*mb
            result=np.where((z>=za)&(z<=zb),value,result)
        return result
    outer_x=curve_x(cranial_z,outer_points); inner_x=curve_x(cranial_z,inner_points)
    lateral=np.clip((sin_a-.55)/.30,0,1)*np.clip((cranial_z+.044)/.010,0,1)*np.clip((.037-cranial_z)/.012,0,1)
    gill=np.exp(-((physical_x-outer_x)/.0018)**2)*lateral
    pre=np.exp(-((physical_x-inner_x)/.0016)**2)*lateral
    color *= (1-.075*gill[...,None]-.085*pre[...,None])
    shield=np.clip((physical_x-outer_x)/.008,0,1)*np.clip((inner_x-physical_x)/.010,0,1)*lateral
    flecks=np.clip(cheek_grain+.28,0,1)*shield
    silver_olive=np.array([.31,.345,.245])
    plate_pigment=.28*shield[...,None]
    color=color*(1-plate_pigment)+silver_olive*plate_pigment
    color += (.035*flecks)[...,None]*np.array([1.0,.83,.35])
    color *= (1+.15*shield[...,None]*cheek_mottle[...,None])
    maxilla_z=.007+.55*(physical_x-.180)
    rear_curl=np.clip((.164-physical_x)/.016,0,1)
    rear_curl=rear_curl*rear_curl*(3-2*rear_curl)
    maxilla_width=.011*(1-.55*rear_curl)
    maxillary_mask=np.exp(-((cranial_z-maxilla_z)/maxilla_width)**4)*np.clip((physical_x-.145)/.013,0,1)*np.clip((.190-physical_x)/.010,0,1)*np.clip((sin_a-.65)/.25,0,1)
    color=color*(1-.30*maxillary_mask[...,None])+np.array([.32,.35,.245])*(.30*maxillary_mask[...,None])
    color[0]=color[-1]=(color[0]+color[-1])*.5
    rgba = np.concatenate((np.clip(color,.008,.85),np.ones((h,w,1))),axis=2)
    body_img = _image('BassScaleOlive_1024',rgba,out/'bass-scale-olive.png')

    height = (.000085*dome-.000024*rim)*(1+.25*pigment)*relief_mask
    height += .0000018*fine
    height += .000003*cheek_grain*shield
    # Radial terminal UVs collapse at the lip pole; remove trunk microrelief
    # there rather than compressing it into artificial concentric bands.
    height *= 1-snout
    height[0]=height[-1]=(height[0]+height[-1])*.5
    dv=(np.roll(height,-1,axis=0)-np.roll(height,1,axis=0))*.5
    du=np.gradient(height,axis=1)
    dx,dy = du/(.384/w),dv/(.31/h)
    length = np.sqrt(dx*dx+dy*dy+1)
    normal = np.stack((.5-.5*dx/length,.5-.5*dy/length,.5+.5/length),axis=2)
    normal[0]=normal[-1]=(normal[0]+normal[-1])*.5
    normal_img = _image('BassScaleNormal_1024',np.concatenate((normal,np.ones((h,w,1))),axis=2),out/'bass-scale-normal.png',True)
    rough = np.clip(.37+.13*back-(.075+.07*gold)*dome*relief_mask+.075*rim*relief_mask+.14*pigment+.025*fine,.23,.60)
    rough=rough*(1-snout)+.42*snout
    rough=np.clip(rough-.05*shield+.08*shield*cheek_grain,.23,.60)
    rough[0]=rough[-1]=(rough[0]+rough[-1])*.5
    rough_img = _image('BassScaleRoughness_1024',np.concatenate((np.repeat(rough[...,None],3,axis=2),np.ones((h,w,1))),axis=2),out/'bass-scale-roughness.png',True)
    body_mat = _textured('Bass skin - scale and broken lateral stripe',body_img)
    shader = body_mat.node_tree.nodes.get('Principled BSDF')
    normal_tex = body_mat.node_tree.nodes.new('ShaderNodeTexImage'); normal_tex.image=normal_img
    normal_node = body_mat.node_tree.nodes.new('ShaderNodeNormalMap')
    normal_node.inputs['Strength'].default_value = 1
    body_mat.node_tree.links.new(normal_tex.outputs['Color'],normal_node.inputs['Color'])
    body_mat.node_tree.links.new(normal_node.outputs['Normal'],shader.inputs['Normal'])
    rough_tex = body_mat.node_tree.nodes.new('ShaderNodeTexImage'); rough_tex.image=rough_img
    body_mat.node_tree.links.new(rough_tex.outputs['Color'],shader.inputs['Roughness'])
    shader.inputs['IOR'].default_value=1.35
    shader.inputs['Specular IOR Level'].default_value=.12
    shader.inputs['Coat Weight'].default_value=.02
    shader.inputs['Coat Roughness'].default_value=.24

    fh=fw=512
    fu=np.arange(fw)[None,:]/fw; fv=np.arange(fh)[:,None]/fh
    fin_noise=_noise(fh,fw,70,65,rng)-.5
    phase=fu*44+.055*np.sin(fv*11+fu*17)
    strip=np.floor(phase).astype(int)%45
    widths=rng.uniform(.055,.14,45)[strip]
    strengths=rng.uniform(.40,1.0,45)[strip]
    striae=np.exp(-((np.mod(phase,1)-.5)/widths)**2)*strengths
    branch_shift=np.clip((fv-.52)/.48,0,1)*.33
    branch=np.exp(-((np.mod(phase+branch_shift,1)-.5)/(widths*.65))**2)
    branch*=np.clip((fv-.52)/.18,0,1)*rng.uniform(0,.70,45)[strip]
    striae=np.maximum(striae,branch)*(.65+.35*np.sin(fv*5+.6)**2)
    fin=np.broadcast_to(np.array([.26,.285,.17]),(fh,fw,3)).copy()
    fin*=1-.12*striae[...,None]
    membrane=_noise(fh,fw,9,13,rng)-.5
    fin+=(.014*fin_noise+.024*membrane)[...,None]
    margin=np.exp(-((fv-.985)/.027)**2)
    fin*=1-.17*margin[...,None]
    root=np.exp(-(fv/.18)**2)
    distal_fin=fin.copy()
    fin=fin*(1-root[...,None])+np.array([.09,.13,.047])*root[...,None]
    alpha=np.broadcast_to(.64-.14*fv+.34*root,(fh,fw)).copy()
    alpha=np.clip(alpha+.035*striae+.075*membrane,.40,.99)
    fin_img=_image('BassFinOlive_512',np.concatenate((fin,alpha[...,None]),axis=2),out/'bass-fin-olive.png')
    amber=distal_fin*np.array([1.06,.97,.80])
    amber=amber*(1-root[...,None])+np.array([.27,.303,.15])*root[...,None]
    pectoral_rgba=np.concatenate((amber,(alpha-.03)[...,None]),axis=2)

    # Dark bronze iris with fine sectors and a narrow gold pupil-border ring.
    # Planar iris UVs are assigned by the authoring generator, not lat/long UVs.
    iv,iu=np.mgrid[0:128,0:128]/127
    ix,iy=2*iu-1,2*iv-1
    radius=np.sqrt(ix*ix+iy*iy); theta=np.arctan2(iy,ix)
    sectors=.5+.5*np.sin(theta*37+2*np.sin(theta*9)+radius*12)
    iris_color=np.broadcast_to(np.array([.072,.082,.039]),(128,128,3)).copy()
    iris_color+=(.027*sectors*np.clip((radius-.63)/.20,0,1))[...,None]*np.array([1,.82,.40])
    gold_ring=np.exp(-((radius-.675)/.028)**2)
    iris_color=iris_color*(1-gold_ring[...,None])+np.array([.30,.275,.105])*gold_ring[...,None]
    iris_color*=1-.32*np.clip((radius-.88)/.12,0,1)[...,None]
    iris_color+=(.010*(_noise(128,128,40,40,rng)-.5))[...,None]
    # Share the existing 512² pectoral image with the 128² iris tile, keeping
    # the original five-image residency budget. Texel-centred UVs avoid bleed.
    atlas=np.zeros((512,512,4),dtype=np.float32)
    ys=np.linspace(0,511,384); low=np.floor(ys).astype(int); high=np.minimum(low+1,511)
    blend=(ys-low)[:,None,None]
    atlas[:384]=pectoral_rgba[low]*(1-blend)+pectoral_rgba[high]*blend
    atlas[384:, :128]=np.concatenate((np.clip(iris_color,0,1),np.ones((128,128,1))),axis=2)
    pectoral_img=_image('BassPectoralIrisAtlas_512',atlas,out/'bass-pectoral-iris-atlas.png')
    iris_img=pectoral_img
    iris_mat=_textured('Bronze iris - narrow gold pupil border',iris_img,.25)
    for node in iris_mat.node_tree.nodes:
        if node.type=='TEX_IMAGE': node.extension='EXTEND'
    iris_shader=iris_mat.node_tree.nodes.get('Principled BSDF')
    iris_shader.inputs['Specular IOR Level'].default_value=.35
    pupil_mat=_solid('Black pupil',(.003,.008,.010),.10,.25)
    pupil_mat.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.38
    return dict(H=h,W=w,fw=fw,fh=fh,body_img=body_img,normal_img=normal_img,
                rough_img=rough_img,fin_img=fin_img,pectoral_img=pectoral_img,iris_img=iris_img,
                BODY_MAT=body_mat,
                FIN_MAT=_textured('Bass fin membranes',fin_img,.42,True),
                PECTORAL_MAT=_textured('Amber pectoral membrane',pectoral_img,.40,True),
                FIN_RAY=_solid('Olive fin rays',(.050,.064,.028),.60,.12),
                PECTORAL_RAY=_solid('Amber pectoral rays',(.060,.065,.027),.60,.12),
                MOUTH=_solid('Mouth cavity tissue',(.10,.052,.040),.48),
                LIP=_solid('Fleshy lip',(.25,.28,.19),.30),
                IRIS=iris_mat,
                PUPIL=pupil_mat,
                EYE_RIM=_solid('Eye rim gold olive',(.045,.065,.025),.50,.15))

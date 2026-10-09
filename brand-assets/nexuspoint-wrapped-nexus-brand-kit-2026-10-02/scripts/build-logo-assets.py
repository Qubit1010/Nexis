"""Reconstruct approved raster contours as editable SVG paths.

This traces geometry; it does not recolour or edit the approved raster.
The new native SVG uses flat brand colours. Requires numpy, OpenCV, Pillow,
and scikit-image. PNG/ICO export uses the companion Node script.
"""
from pathlib import Path
import json
import math
import sys
import hashlib
import xml.etree.ElementTree as ET
import numpy as np
import cv2
from PIL import Image
from skimage import measure

KIT = Path(__file__).resolve().parent.parent
SOURCE = KIT / 'logos/reference/approved-wrapped-nexus-original.png'
OUT = KIT / 'logos'
BLUE = '#02A1E1'
NAVY = '#02040A'
BLACK = '#000000'
WHITE = '#FFFFFF'

def unit(v):
    n = np.linalg.norm(v)
    return v / n if n else v

def bez(c, t):
    return (1-t)**3*c[0] + 3*(1-t)**2*t*c[1] + 3*(1-t)*t*t*c[2] + t**3*c[3]

def generate(points, us, left, right):
    a = np.array([3*u*(1-u)**2*left for u in us])
    b = np.array([3*u*u*(1-u)*right for u in us])
    c00, c01, c11 = np.sum(a*a), np.sum(a*b), np.sum(b*b)
    residual = np.array([p-((1-u)**3+3*u*(1-u)**2)*points[0]-(u**3+3*u*u*(1-u))*points[-1] for p,u in zip(points,us)])
    x0, x1 = np.sum(a*residual), np.sum(b*residual)
    det = c00*c11-c01*c01
    alpha0 = (x0*c11-x1*c01)/det if abs(det)>1e-12 else 0
    alpha1 = (c00*x1-c01*x0)/det if abs(det)>1e-12 else 0
    seg = np.linalg.norm(points[-1]-points[0])
    if alpha0 < 1e-6*seg or alpha1 < 1e-6*seg:
        alpha0=alpha1=seg/3
    return np.array([points[0], points[0]+alpha0*left, points[-1]+alpha1*right, points[-1]])

def params(points):
    us=np.r_[0,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))]
    return us/us[-1] if us[-1] else np.linspace(0,1,len(points))

def error(points,c,us):
    errs=np.array([np.dot(bez(c,u)-p,bez(c,u)-p) for p,u in zip(points,us)])
    split=int(np.argmax(errs[1:-1]))+1 if len(errs)>2 else 1
    return float(errs[split]),split

def refine(points,c,us):
    d1=3*np.diff(c,axis=0)
    d2=2*np.diff(d1,axis=0)
    out=[]
    for p,u in zip(points,us):
        q=bez(c,u)
        q1=(1-u)**2*d1[0]+2*(1-u)*u*d1[1]+u*u*d1[2]
        q2=(1-u)*d2[0]+u*d2[1]
        r=q-p
        den=np.dot(q1,q1)+np.dot(r,q2)
        out.append(np.clip(u-np.dot(r,q1)/den,0,1) if abs(den)>1e-12 else u)
    return np.array(out)

def fit(points,left,right,tolerance=0.65):
    if len(points)==2:
        d=np.linalg.norm(points[0]-points[1])/3
        return [np.array([points[0],points[0]+left*d,points[1]+right*d,points[1]])]
    us=params(points)
    c=generate(points,us,left,right)
    e,split=error(points,c,us)
    if e<tolerance*tolerance:
        return [c]
    if e<4*tolerance*tolerance:
        for _ in range(6):
            us=refine(points,c,us)
            if np.any(np.diff(us)<0): break
            c=generate(points,us,left,right)
            e,split=error(points,c,us)
            if e<tolerance*tolerance:return [c]
    center=unit(points[split-1]-points[split+1])
    return fit(points[:split+1],left,center,tolerance)+fit(points[split:],-center,right,tolerance)

def fmt(n):
    return f'{float(n):.3f}'.rstrip('0').rstrip('.')

def contour_path(contour):
    # Retain dense marching-square samples during fitting. Removing collinear
    # samples before fitting permits Bezier overshoot between corner endpoints.
    pts=np.array(contour[:,::-1],dtype=float)
    # Start on a corner rather than splitting a smooth arc across the closing seam.
    angles=[]
    for i in range(len(pts)):
        a,b=unit(pts[i]-pts[i-1]),unit(pts[(i+1)%len(pts)]-pts[i])
        angles.append(math.acos(np.clip(np.dot(a,b),-1,1)))
    start=int(np.argmax(angles))
    pts=np.roll(pts,-start,axis=0)
    pts=np.vstack([pts,pts[0]])
    curves=fit(pts,unit(pts[1]-pts[0]),unit(pts[-2]-pts[-1]))
    parts=[f'M{fmt(curves[0][0][0])},{fmt(curves[0][0][1])}']
    for c in curves:
        # Preserve straight faces as line commands when controls lie on the segment.
        v=c[3]-c[0]
        cross=lambda p: v[0]*p[1]-v[1]*p[0]
        dist=max(abs(cross(c[1]-c[0])),abs(cross(c[2]-c[0])))/(np.linalg.norm(v) or 1)
        if dist < 0.1:
            parts.append(f'L{fmt(c[3][0])},{fmt(c[3][1])}')
        else:
            parts.append('C'+','.join(fmt(x) for x in c[1:].reshape(-1)))
    return ' '.join(parts)+' Z'

def paths_for(mask, bounds):
    x0,y0,x1,y1=bounds
    field=mask[y0:y1,x0:x1].astype(float)
    contours=measure.find_contours(field,160)
    result=[]
    for contour in contours:
        contour[:,0]+=y0
        contour[:,1]+=x0
        area=cv2.contourArea(contour[:,::-1].astype(np.float32))
        if area>8:result.append(contour_path(contour))
    return result

def svg_file(filename,w,h,body,background=None):
    bg=f'<rect width="{fmt(w)}" height="{fmt(h)}" fill="{background}"/>' if background else ''
    contents=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(w)}" height="{fmt(h)}" viewBox="0 0 {fmt(w)} {fmt(h)}" role="img" aria-label="NexusPoint Wrapped Nexus logo">\n'
              '<title>NexusPoint, Wrapped Nexus</title>\n'
              '<desc>Reconstructed outlines of the approved raster concept. The central connection point uses portfolio blue #02A1E1. All lettering is custom outlined geometry.</desc>\n'
              +bg+'\n'+body+'\n</svg>\n')
    (OUT/filename).write_text(contents,encoding='utf-8')

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    a=np.array(Image.open(SOURCE).convert('RGB'))
    # Minimum RGB channel distinguishes generated blue from neutral white.
    field=cv2.GaussianBlur(np.min(a,axis=2).astype(np.float32),(3,3),0.45)
    symbol_paths=paths_for(field,(230,300,540,605))
    word_paths=paths_for(field,(575,373,1475,531))
    # Circle fitted independently, eliminating raster shading in the master.
    dotmask=(a[:,:,1]>150)&(a[:,:,2]>200)&(a[:,:,0]<170)
    ys,xs=np.where(dotmask[400:505,330:440])
    xs,ys=xs+330,ys+400
    center=np.array([(xs.min()+xs.max())/2,(ys.min()+ys.max())/2])
    radius=(xs.max()-xs.min()+ys.max()-ys.min()+2)/4
    x0,y0=238,310
    iw,ih=292,284
    def icon(color=WHITE,dot=BLUE):
        return (f'<g id="wrapped-nexus-symbol" transform="translate({-x0} {-y0})" fill="{color}" fill-rule="evenodd">\n'
                +''.join(f'<path d="{p}"/>\n' for p in symbol_paths)
                +f'<circle id="nexus-point" cx="{fmt(center[0])}" cy="{fmt(center[1])}" r="{fmt(radius)}" fill="{dot}"/>\n</g>')
    def word(color=WHITE):
        return (f'<g id="outlined-wordmark" transform="translate(-585 -383)" fill="{color}" fill-rule="evenodd">\n'
                +f'<path d="{" ".join(word_paths)}"/>\n</g>')
    def horizontal(color=WHITE,dot=BLUE):
        return f'<g transform="translate(32 32)">{icon(color,dot)}</g>\n<g transform="translate(379 104)">{word(color)}</g>'
    def stacked(color=WHITE,dot=BLUE):
        return f'<g transform="translate(325 32)">{icon(color,dot)}</g>\n<g transform="translate(32 362)">{word(color)}</g>'
    # Master icon canvas is tightly cropped; do not call the transparent white
    # variant black because the artwork itself is white on a transparent ground.
    variants=[('dark',WHITE,BLUE,NAVY),('black',WHITE,BLUE,BLACK),('light',NAVY,BLUE,WHITE),('mono-white',WHITE,WHITE,None),('mono-navy',NAVY,NAVY,None),('mono-black',BLACK,BLACK,None),('transparent-white',WHITE,BLUE,None),('transparent-navy',NAVY,BLUE,None)]
    for name,color,dot,bg in variants:
        svg_file(f'nexuspoint-symbol-{name}.svg',iw,ih,icon(color,dot),bg)
        svg_file(f'nexuspoint-primary-{name}.svg',1290,348,horizontal(color,dot),bg)
        svg_file(f'nexuspoint-stacked-{name}.svg',942,532,stacked(color,dot),bg)
    svg_file('nexuspoint-outline-master.svg',1290,348,horizontal(),None)
    svg_file('nexuspoint-wordmark-white.svg',879,138,word(),None)
    svg_file('nexuspoint-wordmark-navy.svg',879,138,word(NAVY),None)
    # Favicon has a small protected inset; same symbol, no silent geometry change.
    svg_file('nexuspoint-favicon.svg',320,320,f'<g transform="translate(14 18)">{icon()}</g>',NAVY)
    geometry={'source':'reference/approved-wrapped-nexus-original.png','source_size':[int(a.shape[1]),int(a.shape[0])],'icon_bounds':[x0,y0,iw,ih],'dot_center_in_source':center.tolist(),'dot_radius':float(radius),'symbol_contours':len(symbol_paths),'wordmark_contours_including_counters':len(word_paths),'fit_error_pixels':0.65,'blue':BLUE,'navy':NAVY,'method':'Antialiased raster contour reconstruction with adaptive cubic Bezier fitting. The centre circle is replaced by a fitted native circle. The original wordmark is traced into outlines, not attributed to a named font.'}
    (OUT/'geometry-and-method.json').write_text(json.dumps(geometry,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(geometry,indent=2))

def verify():
    original=np.array(Image.open(SOURCE).convert('RGB'))
    result={}
    areas=[('symbol',(238,310,530,594),'nexuspoint-symbol-native-scale-qa.png'),('wordmark',(585,383,1464,521),'nexuspoint-wordmark-native-scale-qa.png')]
    for name,(x0,y0,x1,y1),file in areas:
        raster=original[y0:y1,x0:x1]
        native=np.array(Image.open(OUT/'png'/file).convert('RGBA'))
        mask=np.min(raster,axis=2)>160
        target=(np.min(native[:,:,:3],axis=2)>160)&(native[:,:,3]>128)
        edge_a=cv2.Canny(np.pad(mask,4).astype('uint8')*255,50,150)>0
        edge_b=cv2.Canny(np.pad(target,4).astype('uint8')*255,50,150)>0
        distances=cv2.distanceTransform((~edge_a).astype('uint8'),cv2.DIST_L2,5)[edge_b]
        stats={'white_outline_IoU':float(np.sum(mask&target)/np.sum(mask|target)),'boundary_distance_source_pixels_mean':float(np.mean(distances)),'boundary_distance_source_pixels_p95':float(np.percentile(distances,95)),'boundary_distance_source_pixels_max':float(np.max(distances))}
        result[name]=stats
        assert stats['white_outline_IoU']>(0.97 if name=='symbol' else 0.95)
        assert stats['boundary_distance_source_pixels_max']<1.5
    svgfiles=sorted(OUT.glob('*.svg'))
    for file in svgfiles:
        tree=ET.parse(file)
        tags=[e.tag.rsplit('}',1)[-1] for e in tree.iter()]
        assert 'image' not in tags and 'text' not in tags, file.name
        assert tree.getroot().attrib['viewBox'], file.name
    native=np.array(Image.open(OUT/'png/nexuspoint-symbol-native-scale-qa.png').convert('RGBA'))
    assert native[142,146].tolist()==[2,161,225,255]
    for file in (OUT/'png').glob('*.png'):
        with Image.open(file) as img:img.verify()
    with Image.open(OUT/'favicons/favicon.ico') as ico:
        ico_sizes=sorted(list(size) for size in ico.info['sizes'])
    result.update({'svg_count':len(svgfiles),'all_svgs_native_paths_no_embedded_raster_or_font_dependency':True,'portfolio_blue_core_rgba':native[142,146].tolist(),'ico_sizes':ico_sizes,'approved_reference_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'small_size_visual_review':'16px remains identifiable but fold seams and hooked tips lose detail. Full-detail symbol is clear at 32/64px. Recommended symbol minimum 32px and preferred 48px or more. No geometry simplification applied.','limitations':'This is an editable contour reconstruction of a generated raster, not an original designer vector. The fitted circle is flat exact blue. Slight original raster irregularities are retained. Wordmark is custom outlined geometry; no named typeface claim.'})
    (OUT/'validation-report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    if '--verify' in sys.argv:verify()
    else:main()

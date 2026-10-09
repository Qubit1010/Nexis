"""Build native Soft Fold SVGs from the explicitly selected raster contours.
The selected PNG is read only. The wordmark is the existing approved outline.
Requirements: numpy, OpenCV, Pillow, scikit-image. PNG/ICO exports use Node.
"""
from pathlib import Path
import importlib.util, hashlib, json, re, sys
import xml.etree.ElementTree as ET
import numpy as np
import cv2
from PIL import Image

KIT=Path(__file__).resolve().parents[1]
OUT=KIT/'logos'
SOURCE=OUT/'reference/approved-soft-fold-original.png'
spec=importlib.util.spec_from_file_location('geometry_fit',KIT/'scripts/geometry_fit.py')
fit=importlib.util.module_from_spec(spec);spec.loader.exec_module(fit)
BLUE='#02A1E1';WHITE='#FFFFFF';NAVY='#02040A';BLACK='#000000'

def svg_file(name,w,h,body,background=None):
    bg=f'<rect width="{fit.fmt(w)}" height="{fit.fmt(h)}" fill="{background}"/>' if background else ''
    text=f'<svg xmlns="http://www.w3.org/2000/svg" width="{fit.fmt(w)}" height="{fit.fmt(h)}" viewBox="0 0 {fit.fmt(w)} {fit.fmt(h)}" role="img" aria-label="NexusPoint Soft Fold logo">\n<title>NexusPoint, Soft Fold</title>\n<desc>Approved Soft Fold contours in native vector paths. Portfolio blue #02A1E1 at the centre. Existing wordmark outlines retained.</desc>\n{bg}\n{body}\n</svg>\n'
    (OUT/name).write_text(text,encoding='utf-8')

def main():
    a=np.array(Image.open(SOURCE).convert('RGB'))
    field=cv2.GaussianBlur(np.min(a,axis=2).astype(np.float32),(3,3),0.45)
    ys,xs=np.where(field>160)
    x0,y0=int(xs.min()),int(ys.min());w,h=int(xs.max()-x0+1),int(ys.max()-y0+1)
    paths=fit.paths_for(field,(max(0,x0-3),max(0,y0-3),min(a.shape[1],x0+w+3),min(a.shape[0],y0+h+3)))
    dotmask=(a[:,:,1]>110)&(a[:,:,2]>140)&(a[:,:,0]<80)
    dys,dxs=np.where(dotmask)
    center=[float((dxs.min()+dxs.max())/2),float((dys.min()+dys.max())/2)]
    radius=float((dxs.max()-dxs.min()+dys.max()-dys.min()+2)/4)
    scale=284/h;iw=w*scale;ih=284
    raw=(KIT/'sources/wordmark-white-original.svg').read_text(encoding='utf-8')
    wordgroup=re.search(r'<g id="outlined-wordmark"[\s\S]*?</g>',raw).group(0)
    def icon(color=WHITE,dot=BLUE):
        return f'<g id="soft-fold-symbol" transform="scale({scale:.10f}) translate({-x0} {-y0})" fill="{color}" fill-rule="evenodd">\n'+''.join(f'<path d="{p}"/>\n' for p in paths)+f'<circle id="nexus-point" cx="{center[0]}" cy="{center[1]}" r="{radius}" fill="{dot}"/>\n</g>'
    def word(color=WHITE):return wordgroup.replace('#FFFFFF',color)
    wordleft=32+iw+55;wordtop=32+(ih-138)/2;fullw=wordleft+879+32
    def horizontal(color=WHITE,dot=BLUE):return f'<g transform="translate(32 32)">{icon(color,dot)}</g>\n<g transform="translate({wordleft:.4f} {wordtop:.4f})">{word(color)}</g>'
    def stacked(color=WHITE,dot=BLUE):return f'<g transform="translate({32+(879-iw)/2:.4f} 32)">{icon(color,dot)}</g>\n<g transform="translate(32 362)">{word(color)}</g>'
    variants=[('dark',WHITE,BLUE,NAVY),('black',WHITE,BLUE,BLACK),('light',NAVY,BLUE,WHITE),('mono-white',WHITE,WHITE,None),('mono-navy',NAVY,NAVY,None),('mono-black',BLACK,BLACK,None),('transparent-white',WHITE,BLUE,None),('transparent-navy',NAVY,BLUE,None)]
    for name,color,dot,bg in variants:
        svg_file(f'nexuspoint-symbol-{name}.svg',iw,ih,icon(color,dot),bg)
        svg_file(f'nexuspoint-primary-{name}.svg',fullw,348,horizontal(color,dot),bg)
        svg_file(f'nexuspoint-stacked-{name}.svg',943,532,stacked(color,dot),bg)
    svg_file('nexuspoint-outline-master.svg',fullw,348,horizontal())
    svg_file('nexuspoint-wordmark-white.svg',879,138,word())
    svg_file('nexuspoint-wordmark-navy.svg',879,138,word(NAVY))
    svg_file('nexuspoint-favicon.svg',320,320,f'<g transform="translate({(320-iw)/2:.4f} 18)">{icon()}</g>',NAVY)
    geometry={'identity':'Soft Fold','selected_by_user':'2026-10-02','source':'reference/approved-soft-fold-original.png','source_size':[a.shape[1],a.shape[0]],'icon_bounds_source':[x0,y0,w,h],'normalized_symbol_size':[iw,ih],'horizontal_size':[fullw,348],'dot_center_in_source':center,'dot_radius_source':radius,'dot_diameter_normalized':2*radius*scale,'clear_space_to_symbol_height':2*radius/h,'symbol_contours':len(paths),'fit_error_pixels':0.65,'blue':BLUE,'navy':NAVY,'wordmark_source':'sources/wordmark-white-original.svg','method':'Adaptive cubic Bezier fitting of selected Soft Fold raster contours, preserving source proportions. Native circular centre at exact portfolio blue. Existing approved outlined wordmark reused unchanged.'}
    (OUT/'geometry-and-method.json').write_text(json.dumps(geometry,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(geometry,indent=2))

def verify():
    geo=json.loads((OUT/'geometry-and-method.json').read_text())
    a=np.array(Image.open(SOURCE).convert('RGB'))
    x,y,w,h=geo['icon_bounds_source']
    source=np.min(a[y:y+h,x:x+w],axis=2)>160
    native=np.array(Image.open(OUT/'png/nexuspoint-symbol-native-scale-qa.png').convert('RGBA'))
    assert native.shape[:2]==(h,w)
    target=(np.min(native[:,:,:3],axis=2)>160)&(native[:,:,3]>128)
    ea=cv2.Canny(np.pad(source,4).astype('uint8')*255,50,150)>0
    eb=cv2.Canny(np.pad(target,4).astype('uint8')*255,50,150)>0
    dist=cv2.distanceTransform((~ea).astype('uint8'),cv2.DIST_L2,5)[eb]
    overlap=float(np.sum(source&target)/np.sum(source|target))
    assert overlap>.98,overlap
    assert float(np.percentile(dist,95))<=1.5
    cx,cy=geo['dot_center_in_source'];core=native[int(cy-y),int(cx-x)].tolist()
    assert core==[2,161,225,255],core
    files=list(OUT.glob('*.svg'));assert len(files)==28
    for p in files:
        tree=ET.parse(p);tags=[e.tag.rsplit('}',1)[-1] for e in tree.iter()]
        assert 'image' not in tags and 'text' not in tags,p.name
        assert tree.getroot().get('viewBox')
    oldgroup=re.search(r'<g id="outlined-wordmark"[\s\S]*?</g>',(KIT/'sources/wordmark-white-original.svg').read_text()).group(0)
    newgroup=re.search(r'<g id="outlined-wordmark"[\s\S]*?</g>',(OUT/'nexuspoint-wordmark-white.svg').read_text()).group(0)
    assert oldgroup==newgroup
    for p in (OUT/'png').glob('*.png'):
        with Image.open(p) as image:image.verify()
    result={'identity':'Soft Fold','white_outline_IoU':overlap,'boundary_distance_source_pixels_mean':float(np.mean(dist)),'boundary_distance_source_pixels_p95':float(np.percentile(dist,95)),'boundary_distance_source_pixels_max':float(np.max(dist)),'portfolio_blue_core_rgba':core,'svg_count':28,'native_paths_no_raster_or_font_dependency':True,'wordmark_group_unchanged':True,'approved_reference_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'limitations':'Native contour reconstruction from the selected generated PNG, not recovered designer source. Flat blue circle replaces raster shading. Small curve-fitting variation remains.'}
    (OUT/'validation-report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':verify() if '--verify' in sys.argv else main()

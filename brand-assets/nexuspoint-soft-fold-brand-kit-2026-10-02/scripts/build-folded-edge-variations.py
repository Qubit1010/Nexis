"""Native Folded Edge refinements from the supplied outlined source artwork.
Preserves every foreground logo, QR and lettering group. Only fold geometry
changes. The divider is at y=550, with more than 25 px before the caption ink.
"""
from pathlib import Path
import copy,json,hashlib
import xml.etree.ElementTree as ET

KIT=Path(__file__).resolve().parents[1]
SOURCE=KIT/'applications/card-variations'
OUT=KIT/'applications/folded-edge-variations';OUT.mkdir(parents=True,exist_ok=True)
NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)
BLUE='#02A1E1';DEEP='#0079AA'
URL='https://nexus-point.co/work'

def path(d,fill=None,stroke=None,width=1,opacity=None):
    attrs={'d':d}
    if fill:attrs['fill']=fill
    if stroke:attrs.update({'stroke':stroke,'stroke-width':str(width),'fill':'none'})
    if opacity:attrs['opacity']=str(opacity)
    return ET.Element('{'+NS+'}path',attrs)

directions=[
 {'id':'3A','slug':'soft-edge','name':'Soft Edge','description':'A gently bowed blue edge and curved seam echo the softness of the logo.',
  'front':[
   path('M818 -20H1145V695H1045C1011 485 894 400 904 269C913 158 835 122 818 -20Z',BLUE),
   path('M818 -20C838 160 984 143 971 284C963 356 1027 448 1085 492C991 296 1121 172 916 -20Z',DEEP),
   path('M839 8C856 145 943 163 935 272C930 374 1043 470 1065 655',stroke='#FFFFFF',width=1.4,opacity=.22),
   path('M-20 636C254 608 512 583 636 611L725 695H-20Z','#0B2834')],
  'back':[
   path('M-20 -20H350C302 183 340 330 331 483C327 548 352 621 358 695H-20Z',BLUE),
   path('M271 -20H350C311 148 335 318 331 483L307 695H280C303 450 275 225 271 -20Z',DEEP),
   path('M323 -20C286 181 319 342 306 471C299 535 325 621 331 695',stroke='#FFF',width=1.4,opacity=.3)]},
 {'id':'3B','slug':'layered-fold','name':'Layered Fold','description':'Overlapping blue facets give the edge more structure and depth.',
  'front':[
   path('M858 -20H1145V695H1059L979 348L858 112Z',BLUE),
   path('M858 -20L979 348L1082 414L996 126Z',DEEP),
   path('M992 -20H1064L1145 310V459L1045 169Z','#0396D2'),
   path('M979 348L1082 414L1043 378L1013 275Z','#00648E'),
   path('M-20 619L606 587L722 695H-20Z','#0B2834'),
   path('M606 587L722 695H798L675 610Z','#083D53')],
  'back':[
   path('M-20 -20H350L325 112L365 695H-20Z',BLUE),
   path('M232 -20H350L325 112L232 175Z',DEEP),
   path('M325 112L365 695H331L264 186Z','#0396D2'),
   path('M264 186L325 112L280 163L283 345Z','#00648E')]},
 {'id':'3C','slug':'diagonal-wrap','name':'Diagonal Wrap','description':'A sweeping diagonal edge links the dark front and bright reverse.',
  'front':[
   path('M957 -20H1145V695H958L869 491L989 330L957 -20Z',BLUE),
   path('M957 -20L989 330L1070 240L1041 -20Z',DEEP),
   path('M869 491L958 695H1145V653L979 446Z','#0396D2'),
   path('M-20 631L501 593L675 695H-20Z','#0B2834'),
   path('M980 341L889 488',stroke='#FFF',width=1.4,opacity=.3)],
  'back':[
   path('M-20 -20H350L326 112L363 695H-20Z',BLUE),
   path('M205 -20H350L326 112L254 158Z',DEEP),
   path('M254 158L326 112L363 695H332L304 222Z','#0396D2'),
   path('M-20 559L363 695H-20Z',DEEP)]}
]

def build(direction,side):
    source=SOURCE/f'03-folded-edge-{side}.svg'
    tree=ET.fromstring(source.read_text(encoding='utf-8'))
    foreground=[ET.tostring(e,encoding='unicode') for e in tree if e.tag.endswith('g')]
    # Direct filled paths are background folds. Foreground glyph paths remain
    # nested inside their existing groups and are never selected here.
    for element in list(tree):
        if element.tag.endswith('path') and element.get('fill'):
            tree.remove(element)
    for i,element in enumerate(direction[side]):tree.insert(3+i,copy.deepcopy(element))
    for e in tree:
        if e.tag.endswith('path') and e.get('d') in ('M75 575L641 575','M75 550L641 550'):
            e.set('d','M75 550L641 550')
        if e.tag.endswith('title'):e.text=f"{direction['id']} {direction['name']}, {side}"
        if e.tag.endswith('desc'):
            e.text=f'Folded Edge refinement, 3.5 x 2 inch trim with 0.125 inch bleed. Approved Soft Fold logo, Conthrax and Inter outlines. QR opens {URL}. Divider has a clear gap above the service line.'
    tree.set('aria-label',f"{direction['id']} {direction['name']}, {side}")
    assert foreground==[ET.tostring(e,encoding='unicode') for e in tree if e.tag.endswith('g')]
    file=OUT/f"{direction['id'].lower()}-{direction['slug']}-{side}.svg"
    file.write_text(ET.tostring(tree,encoding='unicode'),encoding='utf-8')
    return file.name

files=[]
for direction in directions:
    for side in ('front','back'):files.append(build(direction,side))
original=json.loads((SOURCE/'design-manifest.json').read_text(encoding='utf-8'))
caption=[t for t in original['textBounds'] if t['text']=='AI SYSTEMS & AUTOMATION'][-1]
gap=caption['bounds'][1]-551 # divider stroke is 2 px, upper-to-ink gap below it
assert gap>=25,gap
report={'brand':'NexusPoint','identity':'Soft Fold','parentConcept':'03 Folded Edge','date':'2026-10-02',
        'qrDestination':URL,'visibleQRLabel':None,'contacts':original['contacts'],'card':original['card'],
        'directions':[{k:d[k] for k in ('id','slug','name','description')} for d in directions],
        'method':'Native SVG background refinements. All source logo, QR and lettering groups unchanged.',
        'textBounds':original['textBounds'][-13:],
        'serviceDivider':{'y':550,'strokePixels':2,'captionTopPixels':caption['bounds'][1],'gapToInkPixels':gap,'gapMillimetres':gap/300*25.4},
        'files':files,'sourceFrontSHA256':hashlib.sha256((SOURCE/'03-folded-edge-front.svg').read_bytes()).hexdigest()}
(OUT/'design-manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'variants':[d['id']+' '+d['name'] for d in directions],'nativeSVGs':len(files),'dividerGapPixels':round(gap,2),'QRdestination':URL},indent=2))

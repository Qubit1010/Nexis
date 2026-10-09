"""Three editable, native-vector Soft Fold card directions.

All lettering is outlined from the actual local Conthrax / Inter files.
Uses the approved logo unchanged and a standards-generated QR with quiet zone.
"""
from pathlib import Path
from html import escape
import json, re
import xml.etree.ElementTree as ET
import qrcode
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

KIT=Path(__file__).resolve().parents[1]
OUT=KIT/'applications/card-variations';OUT.mkdir(parents=True,exist_ok=True)
W,H=1125,675
BLUE='#02A1E1';BLACK='#000000';WHITE='#FFFFFF';DEEP='#0079AA'
URL='https://nexus-point.co/work'
fonts={
    'display':TTFont(KIT/'fonts/portfolio-local-use/conthrax-400.woff2'),
    'body':TTFont(KIT/'fonts/Inter-Regular.otf'),
    'medium':TTFont(KIT/'fonts/Inter-Medium.otf')
}
contacts=[('Aleem Ul Hassan','Co-founder','03108820568'),
          ('Kaleem Ul Hassan','Co-founder','03118340514'),
          ('M. Talha Zafar','Lead Developer','03184461377')]
text_reports=[]

def text(value,x,y,size=32,color=WHITE,family='body',max_width=None,tracking=0):
    font=fonts[family];cmap=font.getBestCmap();glyphs=font.getGlyphSet();units=font['head'].unitsPerEm
    width=sum(font['hmtx'][cmap[ord(c)]][0] for c in value)/units*size+max(0,len(value)-1)*tracking
    if max_width and width>max_width:
        factor=max_width/width;size*=factor;tracking*=factor;width=max_width
    scale=size/units;offset=0;paths=[];bounds=[]
    for char in value:
        name=cmap[ord(char)];pen=SVGPathPen(glyphs);glyphs[name].draw(pen);d=pen.getCommands()
        if d:paths.append(f'<path transform="translate({offset:.5f} 0)" d="{d}"/>')
        bp=BoundsPen(glyphs);glyphs[name].draw(bp)
        if bp.bounds:
            a,b,c,d=bp.bounds;bounds.append([x+(offset+a)*scale,y-d*scale,x+(offset+c)*scale,y-b*scale])
        offset+=font['hmtx'][name][0]+tracking/scale
    box=[min(b[0] for b in bounds),min(b[1] for b in bounds),max(b[2] for b in bounds),max(b[3] for b in bounds)]
    assert box[0]>=73 and box[1]>=73 and box[2]<=1052 and box[3]<=602,(value,box)
    text_reports.append({'text':value,'bounds':box,'fontSizePixels':size})
    return f'<g aria-label="{escape(value,quote=True)}" fill="{color}" transform="translate({x} {y}) scale({scale:.8f} {-scale:.8f})">'+''.join(paths)+'</g>'

def logo(filename,x,y,width,prefix):
    raw=(KIT/'logos'/filename).read_text(encoding='utf-8')
    view=ET.fromstring(raw).get('viewBox').split();ratio=width/float(view[2])
    body=re.sub(r'^.*?<svg[^>]*>','',raw,count=1,flags=re.S)
    body=re.sub(r'</svg>\s*$','',body)
    body=re.sub(r'<(?:title|desc)>.*?</(?:title|desc)>','',body,flags=re.S)
    body=re.sub(r'id="([^"]+)"',lambda m:'id="'+prefix+'-'+m.group(1)+'"',body)
    return f'<g transform="translate({x} {y}) scale({ratio:.8f})">{body}</g>'

qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=1,border=4)
qr.add_data(URL);qr.make(fit=True);matrix=qr.get_matrix();N=len(matrix)
cells=''.join(f'<rect x="{x}" y="{y}" width="1" height="1"/>' for y,row in enumerate(matrix) for x,cell in enumerate(row) if cell)
def QR(x,y,size=242):
    return f'<g aria-label="QR code to {URL}" transform="translate({x} {y}) scale({size/N})"><rect width="{N}" height="{N}" fill="#FFF"/><g fill="#000">{cells}</g></g>'

def svg(filename,body,title):
    raw=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(title)}"><title>{escape(title)}</title><desc>3.5 by 2 inch trim; 0.125 inch bleed. Approved Soft Fold mark, Conthrax and Inter outlines. QR destination {URL}. No label beneath the QR.</desc>{body}</svg>'
    ET.fromstring(raw);(OUT/filename).write_text(raw,encoding='utf-8')

def ribbon_flow():
    return '''<defs><linearGradient id="fold-blue" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#0079AA"/><stop offset="1" stop-color="#02A1E1"/></linearGradient></defs>
    <g transform="translate(110 0)"><path d="M1130 -45C930 46 854 143 933 254C1000 349 1183 378 1175 618L1059 727C1175 421 928 402 870 293C771 108 934 2 1002 -45Z" fill="url(#fold-blue)"/>
    <path d="M1030 -30C852 94 827 172 887 267C948 364 1154 393 1117 701" fill="none" stroke="#68CFFF" stroke-width="2" opacity=".65"/></g>
    <path d="M-40 376C184 402 111 680 460 719L179 735C-28 638 106 513 -40 482Z" fill="#0079AA" opacity=".72"/>
    <path d="M-30 420C122 450 67 665 311 691" fill="none" stroke="#02A1E1" stroke-width="2"/>
    '''

# 01. Ribbon Flow: foreground copy remains in quiet black regions.
front='<rect width="1125" height="675" fill="#000"/>'+ribbon_flow()
front+=logo('nexuspoint-primary-transparent-white.svg',76,112,884,'flow-front')
front+=text('SYSTEMS',90,443,59,family='display')+text('YOU OWN.',90,519,59,family='display')
front+=text('AI SYSTEMS & AUTOMATION',94,584,22,color=WHITE,family='medium',tracking=2.3)
svg('01-ribbon-flow-front.svg',front,'01 Ribbon Flow, front')
back='<rect width="1125" height="675" fill="#000"/><path d="M-30 650C110 520 49 122 322 -40" stroke="#02A1E1" stroke-width="5" fill="none" opacity=".3"/><path d="M-50 661C198 404 67 172 364 -40" stroke="#02A1E1" stroke-width="1.5" fill="none" opacity=".45"/>'
back+=logo('nexuspoint-symbol-transparent-white.svg',100,88,194,'flow-back')+QR(82,341,246)
for i,(name,role,phone) in enumerate(contacts):
    y=144+i*139
    back+=f'<circle cx="362" cy="{y-14}" r="4" fill="{BLUE}"/>'
    back+=text(name,394,y,35,family='display',max_width=650)
    back+=text(role,394,y+47,30,color=BLUE)+text(phone,749,y+47,29,family='medium')
    back+=f'<path d="M394 {y+74}H1035" stroke="#1D1E1F"/>'
back+=text('nexus-point.co',394,587,31,family='medium')
svg('01-ribbon-flow-back.svg',back,'01 Ribbon Flow, back')

# 02. Orbital Field: one enlarged mark, offset circular field, blue QR panel.
front='<rect width="1125" height="675" fill="#000"/>'
for radius in (242,296,350,408):
    front+=f'<circle cx="236" cy="326" r="{radius}" fill="none" stroke="#02A1E1" stroke-width="{2 if radius==296 else 1}" opacity="{.6 if radius==296 else .2}"/>'
front+='<path d="M30 42L92 88" stroke="#02A1E1" stroke-width="7"/><circle cx="15" cy="492" r="12" fill="#02A1E1"/>'
front+=logo('nexuspoint-symbol-transparent-white.svg',88,161,308,'orbit-symbol')
front+=logo('nexuspoint-wordmark-white.svg',501,170,532,'orbit-word')
front+=text('SYSTEMS',501,347,47,family='display')+text('YOU OWN.',501,413,47,family='display')
front+=text('AI SYSTEMS',502,490,23,color=BLUE,family='medium',tracking=2.4)+text('& AUTOMATION',502,526,23,color=BLUE,family='medium',tracking=2.4)
front+=text('nexus-point.co',502,591,24,family='medium')
svg('02-orbital-field-front.svg',front,'02 Orbital Field, front')
back='<rect width="1125" height="675" fill="#000"/><path d="M873 -20H1145V695H756L873 470Z" fill="#02A1E1"/><path d="M827 -25L705 227L784 248L908 -25Z" fill="#0079AA"/>'
back+='<rect x="852" y="74" width="209" height="225" rx="14" fill="#000"/>'
back+=logo('nexuspoint-symbol-transparent-white.svg',889,114,135,'orbit-back')+QR(790,343,250)
for i,(name,role,phone) in enumerate(contacts):
    y=148+i*143
    back+=text(name,82,y,35,family='display',max_width=630)
    back+=text(role,82,y+47,30,color=BLUE)+text(phone,443,y+47,29,family='medium')
    back+=f'<path d="M82 {y+79}H690" stroke="#1D1E1F"/>'
back+=text('nexus-point.co',82,592,31,family='medium')
svg('02-orbital-field-back.svg',back,'02 Orbital Field, back')

# 03. Folded Edge: architectural colour blocks, a bright reverse face.
front='<rect width="1125" height="675" fill="#000"/><path d="M784 -20H1145V695H1064L957 334L784 116Z" fill="#02A1E1"/><path d="M784 -20L957 334L1088 420L978 98Z" fill="#0079AA"/><path d="M-20 623L668 571L753 695H-20Z" fill="#0B2834"/><path d="M75 550L641 550" stroke="#02A1E1" stroke-width="2"/>'
front+=logo('nexuspoint-primary-transparent-white.svg',79,83,886,'fold-front')
front+=text('SYSTEMS',90,426,62,family='display')+text('YOU OWN.',90,509,62,family='display')
front+=text('AI SYSTEMS & AUTOMATION',91,593,22,family='medium',tracking=2.1)
svg('03-folded-edge-front.svg',front,'03 Folded Edge, front')
back='<rect width="1125" height="675" fill="#FFF"/><path d="M-20 -20H354L319 101L361 695H-20Z" fill="#02A1E1"/><path d="M228 -20H354L319 101L228 163Z" fill="#0079AA"/><path d="M319 101L361 695H320L259 169Z" fill="#0396D2"/>'
back+='<rect x="79" y="73" width="244" height="230" rx="14" fill="#FFF"/>'
back+=logo('nexuspoint-symbol-transparent-navy.svg',116,100,172,'fold-back')+QR(79,341,244)
for i,(name,role,phone) in enumerate(contacts):
    y=146+i*139
    back+=text(name,403,y,35,color=BLACK,family='display',max_width=632)
    back+=text(role,403,y+47,30,color=DEEP)+text(phone,751,y+47,29,color=BLACK,family='medium')
    back+=f'<path d="M403 {y+76}H1035" stroke="#D5DCE0"/>'
back+=text('nexus-point.co',403,592,31,color=BLACK,family='medium')
svg('03-folded-edge-back.svg',back,'03 Folded Edge, back')

manifest={'brand':'NexusPoint','identity':'Soft Fold','date':'2026-10-02','qrDestination':URL,
          'visibleQRLabel':None,'contacts':contacts,'card':{'trimInches':[3.5,2],'bleedInches':.125,'mediaInches':[3.75,2.25],'artboard':[W,H],'ppi':300},
          'directions':[{'id':'01','name':'Ribbon Flow','description':'Soft folded ribbons converge around a quiet black field.'},
                        {'id':'02','name':'Orbital Field','description':'Circular motion and an asymmetric blue reverse panel.'},
                        {'id':'03','name':'Folded Edge','description':'Architectural folded planes and a white reverse face.'}],
          'method':'Native vector layouts, unchanged approved logo paths, actual font outlines, qrcode modules with four-module quiet zone.',
          'textBounds':text_reports,'files':sorted(p.name for p in OUT.glob('*.svg'))}
(OUT/'design-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'directions':manifest['directions'],'nativeSVGs':len(manifest['files']),'qrDestination':URL,'textSafeAreaChecks':len(text_reports)},indent=2))

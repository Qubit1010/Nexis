"""Build exact-logo applications as native SVG, with outlined display lettering.
Uses fontTools and qrcode. Generated background is retained unchanged.
No private font binary is embedded in the finished SVG artwork.
"""
from pathlib import Path
import base64, json, re, shutil
from html import escape
import xml.etree.ElementTree as ET
import qrcode
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

KIT=Path(__file__).resolve().parents[1]
OUT=KIT/'applications';OUT.mkdir(exist_ok=True)
BLUE='#02A1E1';INK='#000000';WHITE='#FFFFFF'
fonts={
 'display':TTFont(KIT/'fonts/portfolio-local-use/conthrax-400.woff2'),
 'body':TTFont(KIT/'fonts/Inter-Regular.otf'),
 'medium':TTFont(KIT/'fonts/Inter-Medium.otf'),
 'bold':TTFont(KIT/'fonts/Inter-SemiBold.otf')
}

def text(value,x,y,size=32,color=WHITE,family='body',max_width=None,tracking=0):
    font=fonts[family];cmap=font.getBestCmap();glyphs=font.getGlyphSet();units=font['head'].unitsPerEm
    assert all(ord(c) in cmap for c in value),value
    advance=sum(font['hmtx'][cmap[ord(c)]][0] for c in value)/units*size+max(0,len(value)-1)*tracking
    if max_width and advance>max_width:
        factor=max_width/advance;size*=factor;tracking*=factor;advance=max_width
    s=size/units;offset=0;paths=[]
    for c in value:
        name=cmap[ord(c)];pen=SVGPathPen(glyphs);glyphs[name].draw(pen);d=pen.getCommands()
        if d:paths.append(f'<path transform="translate({offset:.5f} 0)" d="{d}"/>')
        offset+=font['hmtx'][name][0]+tracking/s
    return f'<g aria-label="{escape(value,quote=True)}" fill="{color}" transform="translate({x} {y}) scale({s:.8f} {-s:.8f})">'+''.join(paths)+'</g>'

def text_width(value,size=32,family='body',tracking=0):
    font=fonts[family];cmap=font.getBestCmap();units=font['head'].unitsPerEm
    return sum(font['hmtx'][cmap[ord(c)]][0] for c in value)/units*size+max(0,len(value)-1)*tracking

def logo(filename,x,y,width,prefix):
    raw=(KIT/'logos'/filename).read_text(encoding='utf-8')
    view=ET.fromstring(raw).get('viewBox').split();ratio=width/float(view[2])
    inner=re.sub(r'^.*?<svg[^>]*>','',raw,count=1,flags=re.S)
    inner=re.sub(r'</svg>\s*$','',inner)
    inner=re.sub(r'<(?:title|desc)>.*?</(?:title|desc)>','',inner,flags=re.S)
    inner=re.sub(r'id="([^"]+)"',lambda m:'id="'+prefix+'-'+m.group(1)+'"',inner)
    return f'<g transform="translate({x} {y}) scale({ratio:.8f})">{inner}</g>'

def svg(filename,w,h,body,title):
    result=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}"><title>{escape(title)}</title><desc>Soft Fold identity. Outlined artwork, exact portfolio blue, no installed font dependency.</desc>{body}</svg>'
    (OUT/filename).write_text(result,encoding='utf-8');ET.fromstring(result)

background=OUT/'background-master.png'
if not background.exists():
    shutil.copy2(KIT.parent/'linkedin-font-variations-2026-10-02/background-master.png',background)
    shutil.copy2(KIT.parent/'linkedin-font-variations-2026-10-02/background.prompt.txt',KIT/'sources/background.prompt.txt')
bg64=base64.b64encode(background.read_bytes()).decode('ascii')
def bg(w,h):return f'<rect width="{w}" height="{h}" fill="#000"/><image width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" href="data:image/png;base64,{bg64}"/>'

linkedin=bg(1584,396)+logo('nexuspoint-primary-transparent-white.svg',1120,24,336,'li-logo')
linkedin+=text('ALEEM UL HASSAN',516,200,62,family='display',max_width=942)
linkedin+=text('AI SYSTEMS & AUTOMATION',516,250,19,color=BLUE,family='medium',tracking=3)
linkedin+=text('Automate the work.',516,302,29,family='medium')+text('Own the system.',516+text_width('Automate the work.',29,'medium')+12,302,29,color=BLUE,family='medium')
linkedin+=text('aleemuh.com',1310,346,17,family='medium')+f'<path d="M1356 360H1456" stroke="{BLUE}"/>'
svg('LinkedIn-Banner-Conthrax-Soft-Fold.svg',1584,396,linkedin,'Aleem Ul Hassan, Conthrax LinkedIn banner with Soft Fold logo')

wide=bg(2172,724)+logo('nexuspoint-primary-transparent-white.svg',90,84,1250,'wa-wide')
wide+=text('AI SYSTEMS & AUTOMATION',116,456,31,color=BLUE,family='medium',tracking=4)
wide+=text('SYSTEMS YOU OWN.',108,581,78,family='display',max_width=1400)
wide+=text('Web platforms. Connected workflows. AI automation.',116,641,29)
wide+=text('nexus-point.co',1640,558,31,family='medium')+text('aleem@nexus-point.co',1500,617,31,family='medium')
svg('WhatsApp-Banner-Soft-Fold-Wide.svg',2172,724,wide,'NexusPoint Soft Fold WhatsApp wide banner')

square=bg(1080,1080)+logo('nexuspoint-primary-transparent-white.svg',70,83,940,'wa-square')
square+=text('AI SYSTEMS & AUTOMATION',86,474,23,color=BLUE,family='medium',tracking=3)
square+=text('SYSTEMS',82,593,78,family='display',max_width=900)
square+=text('YOU OWN.',82,693,78,family='display',max_width=900)
square+=text('Web platforms. Connected workflows.',86,770,30)+text('AI automation.',86,818,30)
square+=f'<path d="M86 866H648" stroke="{BLUE}"/>'
square+=text('nexus-point.co',86,926,31,family='medium')+text('aleem@nexus-point.co',86,979,31)
svg('WhatsApp-Banner-Soft-Fold-Square.svg',1080,1080,square,'NexusPoint Soft Fold WhatsApp square banner')

avatar=f'<rect width="1024" height="1024" fill="#000"/>'+logo('nexuspoint-symbol-transparent-white.svg',202,187,620,'avatar')
svg('Profile-Avatar-Soft-Fold.svg',1024,1024,avatar,'NexusPoint Soft Fold profile avatar, circular crop safe')

qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=1,border=4)
qr.add_data('https://nexus-point.co/work');qr.make(fit=True);matrix=qr.get_matrix();n=len(matrix)
cells=''.join(f'<rect x="{x}" y="{y}" width="1" height="1"/>' for y,row in enumerate(matrix) for x,cell in enumerate(row) if cell)
qr_svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{n}" height="{n}" viewBox="0 0 {n} {n}"><rect width="{n}" height="{n}" fill="#FFF"/><g fill="#000">{cells}</g></svg>'
(OUT/'portfolio-qr.svg').write_text(qr_svg,encoding='utf-8')

front=f'<rect width="1125" height="675" fill="#000"/><path d="M-30 680C330 610 180 160 570 -40" stroke="{BLUE}" stroke-width="2" opacity=".35" fill="none"/><path d="M1010 -40C800 260 1410 390 850 720" stroke="{BLUE}" stroke-width="2" opacity=".35" fill="none"/>'
front+=logo('nexuspoint-primary-transparent-white.svg',85,167,955,'card-front')
front+=text('AI SYSTEMS & AUTOMATION',160,524,32,family='display',max_width=805)
front+=f'<path d="M75 558H1050" stroke="#1D1E1F"/>'+text('SYSTEMS YOU OWN.',75,592,32,color=BLUE,family='medium',tracking=1.5)
svg('Business-Card-Soft-Fold-Front.svg',1125,675,front,'NexusPoint Soft Fold business card front, 3.75 by 2.25 inches with bleed')

back=f'<rect width="1125" height="675" fill="#000"/>'+logo('nexuspoint-symbol-transparent-white.svg',121,85,175,'card-back')
qr_size=242
back+=f'<g transform="translate(91 308) scale({qr_size/n})"><rect width="{n}" height="{n}" fill="#FFF"/><g fill="#000">{cells}</g></g>'
names=[('Aleem Ul Hassan','Co-founder','03108820568'),('Kaleem Ul Hassan','Co-founder','03118340514'),('M. Talha Zafar','Lead Developer','03184461377')]
for i,(name,role,phone) in enumerate(names):
    y=125+i*140
    back+=text(name,390,y,35,family='display',max_width=660)
    back+=text(role,390,y+45,32,color=BLUE)+text(phone,732,y+45,32,family='medium')
    back+=f'<path d="M390 {y+76}H1050" stroke="#1D1E1F"/>'
back+=text('nexus-point.co',390,592,34,family='medium')
svg('Business-Card-Soft-Fold-Back.svg',1125,675,back,'NexusPoint Soft Fold business card back, existing contacts and work QR')

specimen=f'<rect width="1000" height="430" fill="#000"/>'
for value,y,color in [('THE REPEATING',82,WHITE),('WORK GETS DONE.',180,WHITE),('YOU KEEP',278,BLUE),('THE SYSTEM.',376,BLUE)]:
    specimen+=text(value,0,y,70,color,family='display',max_width=980)
svg('type-specimen.svg',1000,430,specimen,'Actual portfolio Conthrax type specimen, outlined lettering')

manifest={'identity':'Soft Fold','date':'2026-10-02','selectedDisplayFont':'Conthrax SemiBold, portfolio file version 3.000','typeMethod':'Native outlines generated from local fonts for finished SVG graphics, no private font files embedded','backgroundSource':'Existing imagegen background, unchanged pixels','qrDestination':'https://nexus-point.co/work','contactsSource':'Existing NexusPoint-Card-2-Wrapped-Nexus.png contacts; QR destination updated by Aleem on 2 October 2026','contacts':names,'card':{'artboardPixels':[1125,675],'pngDensity':300,'bleedInches':0.125,'trimInches':[3.5,2],'mediaInches':[3.75,2.25]},'files':sorted(p.name for p in OUT.glob('*.svg'))}
selection_path=OUT/'business-card-selection.json'
if selection_path.exists():
    selection=json.loads(selection_path.read_text(encoding='utf-8'))
    assert selection['status']=='locked'
    selected=OUT/selection['sourceFolder']
    for side in ('front','back'):
        shutil.copy2(selected/(selection['sourcePrefix']+'-'+side+'.svg'),OUT/('Business-Card-Soft-Fold-'+side.title()+'.svg'))
    manifest['selectedCard']={'status':'locked','id':selection['directionId'],'name':selection['directionName'],'approvedDate':selection['approvedDate'],'sourceFolder':selection['sourceFolder'],'sourcePrefix':selection['sourcePrefix']}
    manifest['card']['selectedDirection']=selection['directionId']+' '+selection['directionName']
(OUT/'application-sources.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps(manifest,indent=2))

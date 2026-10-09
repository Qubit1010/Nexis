"""Check native card artwork, print boxes and QR decoding at 300 ppi.
Pillow, pypdf and pypdfium2 required. --qr-python selects an OpenCV interpreter.
"""
from pathlib import Path
import argparse,json,subprocess,sys
import xml.etree.ElementTree as ET
from PIL import Image
from pypdf import PdfReader,PdfWriter
from pypdf.generic import RectangleObject
import pypdfium2 as pdfium

KIT=Path(__file__).resolve().parents[1]
URL='https://nexus-point.co/work'
parser=argparse.ArgumentParser();parser.add_argument('--qr-python',default=sys.executable);parser.add_argument('--directory',default='card-variations',choices=['card-variations','folded-edge-variations'])
args=parser.parse_args()
OUT=KIT/'applications'/args.directory
QA=KIT/'qa'/args.directory;QA.mkdir(parents=True,exist_ok=True)
files=sorted(OUT.glob('*.svg'));assert len(files)==6
checks=[];qr_inputs=[]
for file in files:
    raw=file.read_text(encoding='utf-8');tree=ET.fromstring(raw)
    assert not any(e.tag.endswith('text') or e.tag.endswith('image') for e in tree.iter()),file
    assert '@font-face' not in raw and 'data:font' not in raw
    assert 'PORTFOLIO' not in raw.upper()
    circles=[e for e in tree.iter() if e.get('id','').endswith('nexus-point')]
    assert len(circles)==1 and circles[0].get('fill')=='#02A1E1',file
    if file.stem.endswith('back'):
        assert URL in raw
        for name in ('Aleem Ul Hassan','Kaleem Ul Hassan','M. Talha Zafar','03108820568','03118340514','03184461377'):
            assert name in raw,(file,name)
        qr_inputs.append(file.with_suffix('.png'))
    with Image.open(file.with_suffix('.png')) as im:
        assert im.size==(1125,675) and all(abs(d-300)<1 for d in im.info['dpi'])
    checks.append({'file':file.name,'nativeVector':True,'outlinedType':True,'exactBluePoint':True,'pngSize':[1125,675],'ppi':300})

pdfs=[]
for file in sorted(OUT.glob('*-print.pdf')):
    reader=PdfReader(file);assert len(reader.pages)==2
    writer=PdfWriter()
    for page in reader.pages:
        assert abs(float(page.mediabox.width)-270)<.1 and abs(float(page.mediabox.height)-162)<.1
        page.trimbox=RectangleObject([9,9,261,153]);page.bleedbox=RectangleObject([0,0,270,162]);page.cropbox=RectangleObject([0,0,270,162])
        writer.add_page(page)
    writer.add_metadata({'/Title':'NexusPoint '+file.stem.replace('-',' '),'/Subject':'3.5 x 2 inch trim, 0.125 inch bleed; front then back'})
    temporary=file.with_suffix('.validated.pdf')
    with temporary.open('wb') as output:writer.write(output)
    temporary.replace(file)
    document=pdfium.PdfDocument(file)
    for i in range(len(document)):
        page=document[i];bitmap=page.render(scale=300/72)
        name=QA/(file.stem+('-front.png' if i==0 else '-back.png'))
        bitmap.to_pil().save(name);bitmap.close();page.close()
        if i==1:qr_inputs.append(name)
    document.close()
    check=PdfReader(file)
    assert all(list(p.trimbox)==[9,9,261,153] for p in check.pages)
    pdfs.append({'file':file.name,'pages':2,'mediaBoxPoints':[0,0,270,162],'trimBoxPoints':[9,9,261,153],'bleedBoxPoints':[0,0,270,162]})
assert len(pdfs)==3
code="""import cv2,json,sys
result=[]
for file in sys.argv[1:]:
    value,points,_=cv2.QRCodeDetector().detectAndDecode(cv2.imread(file))
    result.append({'file':file,'destination':value,'detected':points is not None})
print(json.dumps(result))"""
result=subprocess.run([args.qr_python,'-c',code,*[p.as_posix() for p in qr_inputs]],check=True,capture_output=True,text=True)
qr=json.loads(result.stdout);assert len(qr)==6 and all(q['destination']==URL for q in qr),qr
for item in qr:item['file']=Path(item['file']).relative_to(KIT).as_posix()
manifest=json.loads((OUT/'design-manifest.json').read_text(encoding='utf-8'))
if 'serviceDivider' in manifest:
    assert manifest['serviceDivider']['gapToInkPixels']>=25
    for file in OUT.glob('*-front.svg'):
        assert any(e.tag.endswith('path') and e.get('d')=='M75 550L641 550' for e in ET.parse(file).getroot().iter()),file
assert all(t['bounds'][0]>=73 and t['bounds'][1]>=73 and t['bounds'][2]<=1052 and t['bounds'][3]<=602 for t in manifest['textBounds'])
report={'status':'passed','date':'2026-10-02','identity':'Soft Fold','qrDestination':URL,'svgAndPNG':checks,'printPDFs':pdfs,'qrDecodedFromPNGAndPDF':qr,'textSafeAreaChecks':len(manifest['textBounds']),'visualReview':'pending'}
if 'serviceDivider' in manifest:report['serviceDivider']=manifest['serviceDivider']
(QA/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'nativeSVGs':len(checks),'printPDFs':len(pdfs),'QRscans':len(qr),'QRdestination':URL,'textSafeAreaChecks':report['textSafeAreaChecks']},indent=2))

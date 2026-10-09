"""Validate export dimensions, QR, native artwork and business-card print boxes.

Requires Pillow and pypdf in the running Python. OpenCV can be in a separate
interpreter supplied with --qr-python. No font or image installation is needed.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
import pypdfium2 as pdfium

KIT = Path(__file__).resolve().parents[1]
APP = KIT / "applications"
QA = KIT / "qa"
parser = argparse.ArgumentParser()
parser.add_argument("--qr-python", default=sys.executable,
                    help="Python interpreter with OpenCV installed")
args = parser.parse_args()
checks = {"identity":"Soft Fold", "date":"2026-10-02"}

expected = {
    "LinkedIn-Banner-Conthrax-Soft-Fold.png":(1584,396),
    "WhatsApp-Banner-Soft-Fold-Wide.png":(2172,724),
    "WhatsApp-Banner-Soft-Fold-Square.png":(1080,1080),
    "Profile-Avatar-Soft-Fold.png":(1024,1024),
    "Business-Card-Soft-Fold-Front.png":(1125,675),
    "Business-Card-Soft-Fold-Back.png":(1125,675),
    "portfolio-qr.png":(370,370),
    "type-specimen.png":(1000,430),
}
checks["exports"] = []
for filename, size in expected.items():
    with Image.open(APP / filename) as im:
        assert im.size == size, (filename,im.size,size)
        density = im.info.get("dpi", (0,0))
        if filename.startswith("Business-Card"):
            assert all(abs(d-300)<1 for d in density), (filename,density)
        checks["exports"].append({"file":filename,"size":size,"dpi":density})

for svg in APP.glob("*.svg"):
    raw = svg.read_text(encoding="utf-8")
    tree = ET.fromstring(raw)
    assert not any(e.tag.endswith("text") for e in tree.iter()), svg.name
    assert "@font-face" not in raw and "data:font" not in raw, svg.name
checks["applicationLettering"] = "All finished application SVG lettering is outlined; no font binary embedded."
back = (APP / "Business-Card-Soft-Fold-Back.svg").read_text(encoding="utf-8")
assert not any(e.get("aria-label", "").strip().upper() == "PORTFOLIO" for e in ET.fromstring(back).iter()), "Remove the visible Portfolio label"
for label in ("Aleem Ul Hassan","Kaleem Ul Hassan","M. Talha Zafar",
              "03108820568","03118340514","03184461377"):
    assert label in back, label
checks["cardContacts"] = "Three existing names and phone numbers retained."

qr_code = """
import cv2,json,sys
out=[]
for file in sys.argv[1:]:
    image=cv2.imread(file)
    value,points,_=cv2.QRCodeDetector().detectAndDecode(image)
    out.append({'file':file.rsplit('/',1)[-1], 'destination':value, 'detected':points is not None})
print(json.dumps(out))
"""
qr_result = subprocess.run([args.qr_python,"-c",qr_code,
                           (APP/"portfolio-qr.png").as_posix(),
                           (APP/"Business-Card-Soft-Fold-Back.png").as_posix()],
                          check=True,capture_output=True,text=True)
qr = json.loads(qr_result.stdout)
assert all(q["destination"] == "https://nexus-point.co/work" for q in qr), qr
checks["qrDecode"] = qr

# Set the actual trim/bleed metadata, preserving the two native vector pages.
pdf_path = APP / "Business-Card-Soft-Fold-Print.pdf"
reader = PdfReader(pdf_path)
assert len(reader.pages) == 2
writer = PdfWriter()
for page in reader.pages:
    assert abs(float(page.mediabox.width)-270)<.1
    assert abs(float(page.mediabox.height)-162)<.1
    page.trimbox = RectangleObject([9,9,261,153])
    page.bleedbox = RectangleObject([0,0,270,162])
    page.cropbox = RectangleObject([0,0,270,162])
    writer.add_page(page)
writer.add_metadata({"/Title":"NexusPoint Soft Fold business card",
                     "/Subject":"3.5 x 2 inch trim, 0.125 inch bleed; front then back"})
temporary = pdf_path.with_suffix(".validated.pdf")
with temporary.open("wb") as output:
    writer.write(output)
temporary.replace(pdf_path)
reader = PdfReader(pdf_path)
checks["cardPDF"] = []
for page in reader.pages:
    media = [float(n) for n in page.mediabox]
    trim = [float(n) for n in page.trimbox]
    bleed = [float(n) for n in page.bleedbox]
    assert trim == [9,9,261,153] and bleed == [0,0,270,162]
    checks["cardPDF"].append({"mediaBoxPoints":media,"trimBoxPoints":trim,
                              "bleedBoxPoints":bleed})

# Decode the final printed-page rendering as well as the exported PNG.
document = pdfium.PdfDocument(pdf_path)
rendered = []
for index in range(len(document)):
    page = document[index]
    bitmap = page.render(scale=300/72)
    filename = QA / ("actual-card-front.png" if index == 0 else "actual-card-back.png")
    bitmap.to_pil().save(filename)
    bitmap.close()
    page.close()
    rendered.append(filename)
document.close()
result = subprocess.run([args.qr_python,"-c",qr_code,rendered[1].as_posix()],
                        check=True,capture_output=True,text=True)
checks["cardPDFQRDecode"] = json.loads(result.stdout)
assert checks["cardPDFQRDecode"][0]["destination"] == "https://nexus-point.co/work"

# Every visible part of the avatar must survive a centered circular crop.
with Image.open(APP / "Profile-Avatar-Soft-Fold.png") as image:
    im = image.convert("RGB")
    visible = [(x,y) for y in range(im.height) for x in range(im.width)
               if max(im.getpixel((x,y))) > 30]
    farthest = max(((x-511.5)**2+(y-511.5)**2)**.5 for x,y in visible)
    assert farthest < 512, farthest
    checks["avatar"] = {"farthestVisiblePixelFromCentre":round(farthest,2),
                        "cropRadius":512,"result":"all artwork inside circular crop"}

source = KIT / "logos/reference/approved-soft-fold-original.png"
expected_hash = "c78c8b67c72ed764516aaa0f8effca8ddef652de26722d1186145cbd0b6739c5"
assert hashlib.sha256(source.read_bytes()).hexdigest() == expected_hash
checks["approvedSourceSHA256"] = expected_hash
checks["status"] = "passed"
(QA/"production-validation.json").write_text(json.dumps(checks,indent=2)+"\n",encoding="utf-8")
export_report = json.loads((QA/"application-export-validation.json").read_text(encoding="utf-8"))
export_report["status"] = "dimensions, font outlines, QR destination and card trim/bleed validated"
(QA/"application-export-validation.json").write_text(json.dumps(export_report,indent=2)+"\n",encoding="utf-8")
print(json.dumps(checks,indent=2))

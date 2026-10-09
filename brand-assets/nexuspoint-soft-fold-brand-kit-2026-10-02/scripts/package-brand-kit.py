"""Validate and package the complete NexusPoint handoff.
Python dependencies: Pillow, pypdf and pypdfium2.
Does not include private, non-redistributable font binaries in shared ZIP.
"""
from pathlib import Path
import hashlib
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
from pypdf import PdfReader
import pypdfium2 as pdfium

KIT = Path(__file__).resolve().parents[1]
QA = KIT / "qa"
QA.mkdir(exist_ok=True)
checks = {}
tokens = json.loads((KIT / "brand-tokens.json").read_text(encoding="utf-8-sig"))
checks["accent"] = tokens["colors"]["accent"]
assert checks["accent"] == "#02A1E1"
assert tokens["colors"]["uiBoundary"] == "#646464"
svgs = sorted((KIT / "logos").glob("*.svg"))
assert len(svgs) == 28
for file in svgs:
    tree = ET.parse(file)
    assert not any(e.tag.endswith("image") for e in tree.iter())
    for element in tree.iter():
        if element.get("id") == "nexus-point" and "mono" not in file.name:
            assert element.get("fill") == "#02A1E1", file
checks["nativeLogoSVGs"] = len(svgs)
pngs = sorted((KIT / "logos" / "png").glob("*.png"))
for file in pngs:
    with Image.open(file) as im:
        im.verify()
checks["logoPNGExports"] = len(pngs)
for file in KIT.rglob("*.json"):
    if "private-font-reference" not in str(file):
        json.loads(file.read_text(encoding="utf-8-sig"))

for file, expected in [("NexusPoint-Soft-Fold-Brand-Guide.pdf", 12), ("templates/proposal-cover.pdf", 1)]:
    reader = PdfReader(KIT / file)
    assert len(reader.pages) == expected, (file, len(reader.pages))
    dimensions = []
    lengths = []
    for page in reader.pages:
        lengths.append(len(page.extract_text() or ""))
        dimensions.append([round(float(page.mediabox.width),2), round(float(page.mediabox.height),2)])
    assert all(n > 100 for n in lengths), (file, lengths)
    checks[file] = {"pages":len(reader.pages), "pageSizesPoints":dimensions, "textCharacters":lengths}
    if file == "NexusPoint-Soft-Fold-Brand-Guide.pdf":
        guide_text = "\n".join(p.extract_text() or "" for p in reader.pages)
        for term in ["#02A1E1","Ethnocentric","Mokoto","Conthrax","Nasalization","Gambetta","Inter","Soft Fold"]:
            assert term.lower() in guide_text.lower(), term

# Inspect actual PDF rendering, not only the browser's screenshots.
doc = pdfium.PdfDocument(KIT / "NexusPoint-Soft-Fold-Brand-Guide.pdf")
thumbs = []
for index in range(len(doc)):
    bitmap = doc[index].render(scale=1)
    im = bitmap.to_pil().convert("RGB")
    name = f"actual-pdf-page-{index+1:02}.png"
    im.save(QA / name)
    im.thumbnail((420, 297))
    tile = Image.new("RGB", (440, 326), "#DADADA")
    tile.paste(im, ((440-im.width)//2, 10))
    ImageDraw.Draw(tile).text((10,310), f"{index+1:02}", fill="#000000")
    thumbs.append(tile)
sheet = Image.new("RGB",(1320,1304),"#DADADA")
for index, im in enumerate(thumbs):
    sheet.paste(im, ((index%3)*440, (index//3)*326))
sheet.save(QA / "actual-pdf-contact-sheet.png")
checks["actualPDFPagesRendered"] = len(thumbs)

browser_report = json.loads((QA / "pdf-validation.json").read_text(encoding="utf-8"))
assert browser_report["pageCount"] == 12
assert browser_report["fontCheck"]
assert not browser_report["missingApplicationAssets"]
assert all(not item["offPage"] and item["scrollHeight"] <= item["clientHeight"]+1 for item in browser_report["pageOverflow"])
template_report = json.loads((QA / "templates" / "validation-report.json").read_text(encoding="utf-8"))
assert not template_report["errors"]
checks["browserLayout"] = "12 pages, no clipping or missing artwork; bundled Inter loaded"
checks["templateRenders"] = len(template_report["reports"])
checks["fontHandoff"] = "Inter only; OFL notices present"
assert (KIT / "fonts" / "Inter-OFL.txt").is_file()
assert (KIT / "fonts" / "Inter-v4.1-OFL.txt").is_file()
for file in (KIT / "fonts").iterdir():
    if file.suffix.lower() in (".woff", ".woff2", ".ttf", ".otf"):
        assert file.name.lower().startswith("inter"), file
assert (KIT / "templates" / "social-cover.png").is_file()
assert (KIT / "templates" / "proposal-cover.pdf").is_file()

def permitted(file):
    relative = file.relative_to(KIT)
    if relative.as_posix() == "applications/Business-Card-Soft-Fold-Proof.png":
        return False
    if relative.as_posix() == "applications/Business-Card-Soft-Fold-Proof-v2.png":
        return False
    if relative.as_posix() == "applications/card-variations/03-folded-edge-proof.png":
        return False
    if "private-font-reference" in relative.parts or "portfolio-local-use" in relative.parts or "__pycache__" in relative.parts:
        return False
    if file.name in ("Inter-4.1-official.zip", "brand-guide.pdf", "brand-guide.next.pdf"):
        return False
    if relative.parts[0] == "qa" and file.suffix.lower() in (".png", ".jpg", ".jpeg"):
        return False
    if file.name in ("handoff-manifest.json", "package-validation.json"):
        return False
    return True

production = json.loads((QA / "production-validation.json").read_text(encoding="utf-8"))
assert production["status"] == "passed", production
checks["productionValidation"] = production
selection_file = KIT / "applications/business-card-selection.json"
if selection_file.exists():
    selection = json.loads(selection_file.read_text(encoding="utf-8"))
    assert selection["status"] == "locked" and selection["directionId"] == "3C"
    for side in ("front", "back"):
        selected = KIT / "applications" / selection["sourceFolder"] / (selection["sourcePrefix"]+"-"+side+".svg")
        master = KIT / "applications" / ("Business-Card-Soft-Fold-"+side.title()+".svg")
        assert selected.read_bytes() == master.read_bytes(), "Master must match the approved card artwork"
    checks["approvedBusinessCard"] = {"id":selection["directionId"],"name":selection["directionName"],"status":"locked"}
variant_file = QA / "card-variations/validation.json"
if variant_file.exists():
    variants = json.loads(variant_file.read_text(encoding="utf-8"))
    assert variants["status"] == "passed" and variants["visualReview"] == "passed"
    assert variants["qrDestination"] == "https://nexus-point.co/work"
    checks["cardVariationValidation"] = {"nativeSVGs":len(variants["svgAndPNG"]),"printPDFs":len(variants["printPDFs"]),"QRscans":len(variants["qrDecodedFromPNGAndPDF"]),"status":"passed"}
folded_file = QA / "folded-edge-variations/validation.json"
if folded_file.exists():
    folded = json.loads(folded_file.read_text(encoding="utf-8"))
    assert folded["status"] == "passed" and folded["visualReview"] == "passed"
    assert folded["serviceDivider"]["gapToInkPixels"] >= 25
    checks["foldedEdgeRefinements"] = {"nativeSVGs":len(folded["svgAndPNG"]),"printPDFs":len(folded["printPDFs"]),"QRscans":len(folded["qrDecodedFromPNGAndPDF"]),"dividerGapPixels":folded["serviceDivider"]["gapToInkPixels"],"status":"passed"}
visual_file = QA / "visual-review.json"
visual = json.loads(visual_file.read_text(encoding="utf-8")) if visual_file.exists() else {"status":"pending"}
if visual["status"] == "passed":
    for item in visual["reviewedFiles"]:
        assert hashlib.sha256((KIT/item["path"]).read_bytes()).hexdigest() == item["sha256"], "Visual review is stale: "+item["path"]
checks["status"] = "passed automated validation; visual review " + visual["status"]
checks["visualReview"] = visual
checks["sharedZIPExclusions"] = ["fonts/portfolio-local-use/**", "sources/private-font-reference/**", "sources/Inter-4.1-official.zip", "qa image renders", "__pycache__", "superseded draft brand-guide.pdf"]
(QA / "handoff-validation.json").write_text(json.dumps(checks, indent=2)+"\n", encoding="utf-8")

files = sorted(f for f in KIT.rglob("*") if f.is_file() and permitted(f))
manifest = {
    "brand":"NexusPoint", "identity":"Soft Fold", "date":"2026-10-02",
    "hashAlgorithm":"SHA-256", "files":[
        {"path":f.relative_to(KIT).as_posix(),"bytes":f.stat().st_size,"sha256":hashlib.sha256(f.read_bytes()).hexdigest()}
        for f in files
    ],
    "excluded":checks["sharedZIPExclusions"],
    "note":"Manifest does not hash itself or package-validation.json."
}
(KIT / "handoff-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n", encoding="utf-8")
output = KIT.parent / (KIT.name + ".zip")
with zipfile.ZipFile(output,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=8) as archive:
    for file in files + [KIT / "handoff-manifest.json"]:
        archive.write(file, (Path(KIT.name) / file.relative_to(KIT)).as_posix())
with zipfile.ZipFile(output) as archive:
    names=archive.namelist()
    assert archive.testzip() is None
    assert not any("private-font-reference" in n or "portfolio-local-use" in n or "Inter-4.1-official.zip" in n for n in names)
    for item in manifest["files"]:
        key=KIT.name+"/"+item["path"]
        assert hashlib.sha256(archive.read(key)).hexdigest()==item["sha256"]
package = {"archive":output.name,"bytes":output.stat().st_size,"entries":len(names),"sha256":hashlib.sha256(output.read_bytes()).hexdigest(),"crc":"passed","manifestHashes":"passed","privateFontsExcluded":True}
(KIT / "package-validation.json").write_text(json.dumps(package,indent=2)+"\n", encoding="utf-8")
print(json.dumps({"checks":checks,"package":package},indent=2))

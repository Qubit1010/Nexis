"""Build portable examples and recalculate the supplied colour contrast report.
Requires Python's standard library. Run from any working directory.
"""
from pathlib import Path
import base64
import json
import math
import re
import shutil
import xml.etree.ElementTree as ET

KIT = Path(__file__).resolve().parents[1]
TEMPLATES = KIT / "templates"
TEMPLATES.mkdir(exist_ok=True)

def luminance(value):
    rgb = [int(value[i:i+2], 16) / 255 for i in (1, 3, 5)]
    rgb = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
    return sum(v * w for v, w in zip(rgb, (0.2126, 0.7152, 0.0722)))

report_path = KIT / "contrast-report.json"
report = json.loads(report_path.read_text(encoding="utf-8-sig"))
report["date"] = "2026-10-02"
report["method"] = "WCAG 2.2 sRGB relative luminance; unrounded ratios determine pass/fail"
report["thresholds"] = {"bodyAA": 4.5, "largeAA": 3, "nonTextAA": 3}
for pair in report["pairs"]:
    if pair["foreground"] == "#5A5A5A":
        pair["foreground"] = "#646464"
    a, b = luminance(pair["foreground"]), luminance(pair["background"])
    pair["ratio"] = (max(a, b) + 0.05) / (min(a, b) + 0.05)
    for test, floor in report["thresholds"].items():
        pair[test] = pair["ratio"] >= floor
report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

def logo_svg(file, x, y, width, prefix):
    raw = (KIT / "logos" / file).read_text(encoding="utf-8")
    inner = re.sub(r"^.*?<svg[^>]*>", "", raw, count=1, flags=re.S)
    inner = re.sub(r"</svg>\s*$", "", inner)
    inner = re.sub(r"<(?:title|desc)>.*?</(?:title|desc)>", "", inner, flags=re.S)
    inner = re.sub(r'id="([^"]+)"', lambda m: 'id="' + prefix + "-" + m.group(1) + '"', inner)
    canvas_width=float(ET.fromstring(raw).get('viewBox').split()[2])
    return '<g transform="translate(' + str(x) + " " + str(y) + ") scale(" + str(width / canvas_width) + ')">' + inner + "</g>"

font64 = base64.b64encode((KIT / "fonts" / "InterVariable.woff2").read_bytes()).decode("ascii")
font_style = '<style>@font-face{font-family:Inter;src:url(data:font/woff2;base64,' + font64 + ') format("woff2");font-weight:100 900}text{font-family:Inter,Arial,sans-serif}</style>'

social = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1584" height="396" viewBox="0 0 1584 396" role="img" aria-label="NexusPoint social cover, Systems you own">
<title>NexusPoint social cover</title><desc>Editable 1584 by 396 cover. Keep the lower-left area clear for profile overlays. Inter is embedded under OFL.</desc>
{font_style}
<defs><pattern id="grid" width="76" height="76" patternUnits="userSpaceOnUse"><path d="M76 0H0V76" fill="none" stroke="#FFFFFF" stroke-opacity=".043"/></pattern></defs>
<rect width="1584" height="396" fill="#000000"/><rect width="1584" height="396" fill="url(#grid)"/>
<path d="M1120 -80H1450Q1508 -80 1508 -22V92Q1508 152 1448 152H1358Q1298 152 1298 212V476" stroke="#02A1E1" stroke-opacity=".16" stroke-width="38" fill="none"/>
<circle cx="1298" cy="246" r="19" fill="#02A1E1"/>
{logo_svg("nexuspoint-primary-transparent-white.svg", 424, 40, 440, "cover-logo")}
<text x="436" y="232" fill="#FFFFFF" font-size="54" font-weight="650" letter-spacing="-1.8">Systems you own.</text>
<text x="438" y="282" fill="#CCCCCC" font-size="20" font-weight="400">Web platforms. Connected workflows. AI automation.</text>
<path d="M438 322H970" stroke="#1D1E1F"/>
<text x="438" y="354" fill="#8A8A8A" font-size="14" font-weight="500" letter-spacing="1.5">NEXUS-POINT.CO</text>
</svg>'''
(TEMPLATES / "social-cover.svg").write_text(social, encoding="utf-8")

proposal = f'''<svg xmlns="http://www.w3.org/2000/svg" width="794" height="1123" viewBox="0 0 794 1123" role="img" aria-label="NexusPoint editable project proposal cover">
<title>NexusPoint project proposal cover</title><desc>A4 portrait template with labelled fields. Replace client, project and date before export. Inter is embedded under OFL.</desc>
{font_style}
<rect width="794" height="1123" fill="#FFFFFF"/>
<rect x="0" y="0" width="794" height="8" fill="#02A1E1"/>
{logo_svg("nexuspoint-primary-transparent-navy.svg", 50, 60, 360, "proposal-logo")}
<text x="62" y="310" fill="#0079AA" font-size="13" font-weight="600" letter-spacing="2">BUILT FOR YOUR BUSINESS</text>
<text x="58" y="405" fill="#000000" font-size="69" font-weight="650" letter-spacing="-2.5">Project</text>
<text x="58" y="483" fill="#000000" font-size="69" font-weight="650" letter-spacing="-2.5">proposal.</text>
<text x="62" y="542" fill="#333333" font-size="24">Systems you own.</text>
<path d="M62 602H732" stroke="#D6D6D6"/>
<text x="62" y="660" fill="#4D4D4D" font-size="12" font-weight="600" letter-spacing="1.5">PREPARED FOR</text>
<text x="62" y="701" fill="#000000" font-size="29" font-weight="600">[Client name]</text>
<text x="62" y="770" fill="#4D4D4D" font-size="12" font-weight="600" letter-spacing="1.5">PROJECT</text>
<text x="62" y="808" fill="#000000" font-size="24" font-weight="500">[Project title]</text>
<text x="62" y="886" fill="#4D4D4D" font-size="12" font-weight="600" letter-spacing="1.5">DATE</text>
<text x="62" y="921" fill="#000000" font-size="20">[Day month year]</text>
<circle cx="695" cy="968" r="28" fill="#02A1E1"/>
<path d="M62 1006H732" stroke="#D6D6D6"/>
<text x="62" y="1043" fill="#000000" font-size="14" font-weight="500">NexusPoint</text>
<text x="732" y="1043" fill="#4D4D4D" font-size="13" text-anchor="end">nexus-point.co</text>
</svg>'''
(TEMPLATES / "proposal-cover.svg").write_text(proposal, encoding="utf-8")

email = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NexusPoint email signature template</title>
<style>body{margin:40px;color:#000;background:#fff;font:15px/1.6 Arial,sans-serif}.instructions{max-width:680px;padding:18px;background:#f2f2f2;margin-bottom:32px}code{font-size:13px}.signature-wrap{padding:20px;border:1px solid #ddd;display:inline-block}</style></head><body>
<div class="instructions"><strong>Email signature preview</strong><br>Copy only the signature table into your email settings. Before sending, upload the supplied transparent PNG to your website and replace its relative image URL with a public HTTPS URL. Local file references will not display for recipients. No phone number or email address has been invented.</div>
<div class="signature-wrap">
<!-- START SIGNATURE. Replace image src with your hosted HTTPS logo URL. -->
<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="font-family:Arial,sans-serif;color:#000000;font-size:13px;line-height:1.5">
<tr><td style="padding:0 0 15px"><a href="https://nexus-point.co/" style="text-decoration:none"><img src="../logos/png/nexuspoint-primary-transparent-navy.png" width="258" height="70" alt="NexusPoint" style="display:block;border:0;width:258px;height:70px"></a></td></tr>
<tr><td style="font-size:16px;font-weight:bold;padding:0 0 2px">Aleem Ul Hassan</td></tr>
<tr><td style="padding:0 0 12px">Founder, NexusPoint</td></tr>
<tr><td style="padding:0 0 12px;border-bottom:2px solid #02A1E1">Web platforms. Connected workflows. AI automation.</td></tr>
<tr><td style="padding-top:10px"><a href="https://nexus-point.co/" style="color:#0079AA;text-decoration:underline">nexus-point.co</a><span style="color:#646464;padding:0 9px">|</span><a href="https://www.aleemuh.com/" style="color:#0079AA;text-decoration:underline">aleemuh.com</a></td></tr>
</table>
<!-- END SIGNATURE -->
</div></body></html>
'''
(TEMPLATES / "email-signature.html").write_text(email, encoding="utf-8")

components = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NexusPoint interface examples</title>
<link rel="stylesheet" href="../brand-tokens.css">
<style>*{box-sizing:border-box}body{margin:0;background:var(--color-ink);color:var(--color-white);font:400 16px/1.6 var(--font-body)}main{max-width:1120px;margin:auto;padding:64px 32px}header{margin-bottom:64px}header img{width:340px;max-width:100%}.eyebrow{font-size:13px;letter-spacing:.115em;text-transform:uppercase;color:var(--color-text-muted)}h1{font-size:clamp(32px,5vw,60px);line-height:1.08;letter-spacing:-.03em;margin:16px 0}h2{font-size:28px;line-height:1.15}p{max-width:62ch}.grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}.panel{padding:32px;border-radius:var(--radius-card);background:var(--color-ink-soft)}.brand-light{background:#fff;color:#000}.muted{color:var(--color-text-secondary)}.brand-light .muted{color:#4D4D4D}label{display:block;margin:24px 0 8px}input{font:inherit;padding:12px;width:100%}.brand-button{cursor:pointer;display:inline-block}.actions{display:flex;align-items:center;gap:24px;flex-wrap:wrap;margin-top:24px}.status{display:inline-block;border:1px solid var(--color-success);color:var(--color-success);padding:4px 10px;border-radius:500px;font-size:13px}.brand-light .status{color:#000;border-color:#646464}footer{margin-top:48px;color:#8A8A8A;font-size:13px}@media(max-width:768px){.grid{grid-template-columns:1fr}main{padding:32px 20px}.panel{padding:24px}}</style>
</head><body><main><header><img src="../logos/nexuspoint-primary-transparent-white.svg" alt="NexusPoint"><p class="eyebrow">Reusable interface examples</p><h1>The repeating work gets done.</h1><p class="muted">These examples use the portable Inter family and supplied CSS tokens. Text remains readable in dark and light layouts.</p></header>
<section class="grid" aria-label="Dark and light components"><div class="panel"><span class="status">System connected</span><h2>Tell us what your team repeats.</h2><p class="muted">Describe the handoffs, copy-and-paste work, and disconnected tools.</p><label for="dark-work">Repeating task</label><input id="dark-work" class="brand-field" type="text" placeholder="For example: moving enquiries into the CRM"><div class="actions"><button type="button" class="brand-button">Explore the system</button><a class="brand-link" href="https://nexus-point.co/">See the work</a></div></div>
<div class="panel brand-light"><span class="status">System connected</span><h2>Systems you own.</h2><p class="muted">A clear implementation, documented workflows, and the access to run them.</p><p><a class="brand-link" href="https://nexus-point.co/">Read about the approach</a></p><div class="actions"><button type="button" class="brand-button">Explore the system</button></div><p class="muted">Light-surface link blue: #0079AA. Logo centre and action fill: #02A1E1.</p></div></section>
<footer>Demonstration components only. Buttons have no form submission or tracking. The input shows accessible boundary and focus treatments.</footer></main></body></html>
'''
(TEMPLATES / "components.html").write_text(components, encoding="utf-8")

template_readme = """# Application templates

- social-cover.svg: 1584 x 396, editable SVG with the lower-left area left clear for a profile overlay. Review the crop in the destination platform before publishing.
- proposal-cover.svg: A4 portrait (794 x 1123 SVG units). Replace the labelled client, project and date fields, then export as PDF for the final proposal.
- email-signature.html: safe table layout with Arial fallback. Copy only the marked table. Publish the supplied transparent PNG to an HTTPS URL and replace the relative image source before use in email.
- components.html: responsive dark/light interface examples using ../brand-tokens.css. Buttons are visual examples with no submission or tracking.

The SVG covers embed the redistributable Inter variable webfont for consistent previews. Inter is supplied under OFL, with its notices in ../fonts/. The logo remains outlined artwork.
Suggested public messaging comes from the existing NexusPoint strategy. Client names, phone numbers, email addresses and results have not been invented.
"""
(TEMPLATES / "README.md").write_text(template_readme, encoding="utf-8")

preview = KIT / 'logos/png/nexuspoint-primary-black.png'
if preview.is_file():
    (KIT / "previews").mkdir(exist_ok=True)
    shutil.copy2(preview, KIT / "previews" / "soft-fold-primary.png")

for path in TEMPLATES.glob("*.svg"):
    ET.parse(path)
for path in TEMPLATES.glob("*.html"):
    text = path.read_text(encoding="utf-8")
    for ref in re.findall(r'(?:src|href)="([^"]+)"', text):
        if ref.startswith("../") and not (path.parent / ref).resolve().is_file():
            raise RuntimeError("Missing local dependency: " + ref)
print(json.dumps({"templates": sorted(p.name for p in TEMPLATES.iterdir()), "contrastPairs": len(report["pairs"]), "exactAccent": "#02A1E1"}, indent=2))

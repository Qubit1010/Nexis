"""Render an authored SVG to PNG via headless Chromium.

Why a browser and not a rasteriser: cairosvg, rsvg-convert, inkscape and magick are all
absent on this machine (checked 2026-08-22). Playwright is installed with cached Chromium
builds, so the browser is the render path that already exists.

Fonts are inlined as base64 data URIs, never linked. A network font load has hung a render
in this repo before (see the remotion font-loading note), and a hung render looks identical
to a slow one.

    python render.py diagram.svg --out diagram.png
    python render.py --selftest
"""
from __future__ import annotations

import argparse
import base64
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
FONT_DIR = REPO / "projects" / "reel-engine" / "public" / "fonts"
FACES = {"Urbanist-Regular.woff2": 400, "Urbanist-Bold.woff2": 700}

# The palette contract from 15-brand-visual-identity.md sections 3 and 6.
# #475569 is deliberately absent: it is retired and fails AA at 2.71:1.
PALETTE = {
    "#02040A": "ground",
    "#06090F": "deep surface",
    "#0B0F17": "raised surface",
    "#00B7FF": "secondary",
    "#A6DAFF": "accent",
    "#BAE6FD": "accent light",
    "#F1F5F9": "text high",
    "#CBD5E1": "text mid",
    "#94A3B8": "text muted",
    "#64748B": "border / non-text UI",
    "#4ADE80": "success",
    "#FBBF24": "warning",
    "#F87171": "error",
}
RETIRED = "#475569"


def font_css() -> str:
    """@font-face blocks with the woff2 payload inlined."""
    out = []
    for name, weight in FACES.items():
        p = FONT_DIR / name
        if not p.exists():
            raise SystemExit(f"font missing: {p}")
        b64 = base64.b64encode(p.read_bytes()).decode()
        out.append(
            "@font-face{font-family:'Urbanist';font-style:normal;"
            f"font-weight:{weight};font-display:block;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
        )
    return "".join(out)


def svg_size(svg: str) -> tuple[int, int]:
    m = re.search(r'viewBox=["\']\s*[\d.-]+\s+[\d.-]+\s+([\d.]+)\s+([\d.]+)', svg)
    if m:
        return int(float(m.group(1))), int(float(m.group(2)))
    w = re.search(r'\bwidth=["\'](\d+)', svg)
    h = re.search(r'\bheight=["\'](\d+)', svg)
    if w and h:
        return int(w.group(1)), int(h.group(1))
    raise SystemExit("cannot determine SVG size: add a viewBox")


def audit(svg: str) -> list[str]:
    """Palette and hierarchy checks, run before the render rather than after."""
    problems = []
    hexes = {h.upper() for h in re.findall(r"#[0-9A-Fa-f]{6}", svg)}
    if RETIRED in hexes:
        problems.append(f"{RETIRED} is retired (2.71:1, fails AA) and must not appear")
    stray = hexes - {k.upper() for k in PALETTE}
    if stray:
        problems.append(f"off-palette colours: {sorted(stray)}")
    accent = len(re.findall(r"#A6DAFF", svg, re.I))
    if accent == 0:
        problems.append("no accent element: the single subject under discussion is unmarked")
    return problems


def render(svg_path: Path, out: Path, scale: int = 2) -> Path:
    from playwright.sync_api import sync_playwright

    svg = svg_path.read_text(encoding="utf-8")
    w, h = svg_size(svg)
    html = (
        "<!doctype html><meta charset='utf-8'><style>"
        f"{font_css()}"
        "html,body{margin:0;padding:0;background:#02040A;}"
        f"svg{{display:block;width:{w}px;height:{h}px;}}"
        "</style>" + svg
    )
    tmp = Path(tempfile.mkdtemp()) / "page.html"
    tmp.write_text(html, encoding="utf-8")

    out.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=scale)
        pg.goto(tmp.as_uri())
        pg.wait_for_timeout(300)  # let the inlined face swap in before the shot
        pg.screenshot(path=str(out), omit_background=False)
        b.close()
    return out


def selftest() -> int:
    print("1. fonts present and inlinable")
    try:
        css = font_css()
        print(f"   PASS: {len(FACES)} face(s), {len(css)} chars of inlined CSS")
    except SystemExit as e:
        print(f"   FAIL: {e}")
        return 1

    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 300">
  <rect width="600" height="300" fill="#02040A"/>
  <rect x="40" y="40" width="240" height="120" rx="10" fill="#0B0F17" stroke="#64748B"/>
  <text x="60" y="88" font-family="Urbanist" font-weight="700" font-size="26"
        fill="#F1F5F9">Legible at 26px</text>
  <text x="60" y="124" font-family="Urbanist" font-weight="400" font-size="16"
        fill="#94A3B8">Muted label, 8.00:1 on ground</text>
  <rect x="320" y="40" width="240" height="120" rx="10" fill="#0B0F17" stroke="#A6DAFF"/>
  <text x="340" y="88" font-family="Urbanist" font-weight="700" font-size="26"
        fill="#A6DAFF">The subject</text>
  <text x="40" y="230" font-family="ui-monospace, Consolas, monospace" font-size="15"
        fill="#CBD5E1">mono: 0123456789 / machine output</text>
</svg>"""
    t = Path(tempfile.mkdtemp())
    (t / "s.svg").write_text(svg, encoding="utf-8")

    print("2. palette audit catches a retired colour")
    bad = audit(svg.replace("#64748B", RETIRED))
    if any(RETIRED in p for p in bad):
        print("   PASS: retired colour rejected")
    else:
        print("   FAIL: retired colour not caught")
        return 1

    print("3. palette audit passes a clean SVG")
    problems = audit(svg)
    if problems:
        print(f"   FAIL: {problems}")
        return 1
    print("   PASS: no problems")

    print("4. renders to PNG at the viewBox size x scale")
    try:
        png = render(t / "s.svg", t / "s.png", scale=2)
    except Exception as e:
        print(f"   FAIL: {type(e).__name__}: {e}")
        return 1
    from PIL import Image
    im = Image.open(png)
    if im.size != (1200, 600):
        print(f"   FAIL: expected (1200, 600), got {im.size}")
        return 1
    print(f"   PASS: {im.size}, {png.stat().st_size} bytes")

    print("5. the rendered ground is the brand ground, not white")
    px = im.convert("RGB").getpixel((5, 5))
    if px != (0x02, 0x04, 0x0A):
        print(f"   FAIL: corner pixel {px}, expected (2, 4, 10)")
        return 1
    print("   PASS: ground is #02040A")

    print("6. text actually rendered (ink present where the headline sits)")
    crop = im.convert("RGB").crop((110, 130, 560, 190))
    if len({crop.getpixel((x, y)) for x in range(0, 450, 7) for y in range(0, 60, 7)}) < 3:
        print("   FAIL: headline area is flat, the font did not render")
        return 1
    print("   PASS: glyph ink present")

    print("\nRESULT: PASS")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("svg", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--scale", type=int, default=2)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if not a.svg:
        ap.error("give an SVG path or --selftest")

    src = Path(a.svg)
    svg = src.read_text(encoding="utf-8")
    problems = audit(svg)
    if problems:
        for p in problems:
            print(f"AUDIT: {p}", file=sys.stderr)
        return 2
    out = Path(a.out) if a.out else src.with_suffix(".png")
    render(src, out, a.scale)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

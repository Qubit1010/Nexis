"""Save an offline, single-file copy of a demo hub for meetings when mobile internet is cut.

    python scripts/snapshot.py <slug> [<slug> ...] | --all  [--base=https://nexuspoint-demo.vercel.app]
    -> projects/quetta-local-market/deliverables/Offline-Demo-<slug>-<lang>.html

Loads the hub with ?snapshot=1 (a pre-played conversation built from the business's facts, no live
polling), then writes ONE self-contained .html: CSS inlined, logos and fonts embedded as data URIs,
scripts removed. Works in any browser, on any phone, with no network. Each file is re-opened with the
network OFF to prove it renders (name present, chat bubbles present, fonts embedded).
"""
import asyncio
import base64
import json
import re
import sys
import urllib.request
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
DEMOS = ROOT.parent / "quetta-local-market" / "data" / "demos"
OUT = ROOT.parent / "quetta-local-market" / "deliverables"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
KEEP_SUBSETS = ("/* latin */", "/* arabic */")


def get(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()


def inline_fonts(css_url: str, lang: str) -> str:
    """Download Google Fonts CSS, keep latin (+ arabic for Urdu) subsets, embed each woff2 as base64."""
    css = get(css_url).decode("utf-8")
    blocks = re.findall(r"(/\* [\w-]+ \*/\s*@font-face\s*\{[^}]+\})", css)
    out = []
    for blk in blocks:
        if not blk.startswith(KEEP_SUBSETS):
            continue
        if "Nastaliq" in blk and lang != "ur":
            continue
        url = re.search(r"url\((https://[^)]+)\)", blk).group(1)
        data = base64.b64encode(get(url)).decode()
        out.append(blk.replace(url, f"data:font/woff2;base64,{data}"))
    return "\n".join(out)


async def snap(slugs: list[str], base: str) -> None:
    OUT.mkdir(exist_ok=True)
    img_cache: dict[str, str] = {}
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for slug in slugs:
            d = json.loads((DEMOS / f"{slug}.json").read_text(encoding="utf-8"))
            for lang in ("en", "ur"):
                ctx = await b.new_context(viewport={"width": 1280, "height": 900})
                pg = await ctx.new_page()
                url = f"{base}/d/{slug}?t={d['token']}&snapshot=1" + ("&lang=ur" if lang == "ur" else "")
                await pg.goto(url, wait_until="networkidle")
                await pg.evaluate("document.fonts.ready")
                await pg.wait_for_timeout(600)
                html = await pg.evaluate("document.documentElement.outerHTML")
                css_links = await pg.evaluate("[...document.querySelectorAll('link[rel=stylesheet]')].map(l => l.href)")
                await ctx.close()
                styles = []
                for href in css_links:
                    styles.append(inline_fonts(href, lang) if "fonts.googleapis.com" in href else get(href).decode("utf-8"))
                html = re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.S)
                html = re.sub(r"<link\b[^>]*>", "", html)
                for src in set(re.findall(r'src="(/[^"]+\.png)"', html)):
                    if src not in img_cache:
                        img_cache[src] = "data:image/png;base64," + base64.b64encode(get(base + src)).decode()
                    html = html.replace(f'src="{src}"', f'src="{img_cache[src]}"')
                html = html.replace("</head>", "<style>" + "\n".join(styles) + "</style></head>", 1)
                # static copy: make every in-page link inert except section anchors
                html = re.sub(r'href="(?!#)[^"]*"', 'href="#"', html)
                path = OUT / f"Offline-Demo-{slug}-{lang}.html"
                path.write_text("<!doctype html>" + html, encoding="utf-8")
                off = await b.new_context(offline=True, viewport={"width": 390, "height": 844})
                op = await off.new_page()
                await op.goto(path.as_uri())
                await op.evaluate("document.fonts.ready")
                ok = await op.evaluate(f"document.body.innerText.includes({json.dumps(d['name'])})")
                bubbles = await op.evaluate("document.querySelectorAll('.bub').length")
                fonts = await op.evaluate("[...document.fonts].filter(f => f.status === 'loaded').map(f => f.family).filter((v,i,a)=>a.indexOf(v)===i)")
                await op.screenshot(path=str(ROOT / "tests" / "qa" / f"offline-{slug[:12]}-{lang}.png"), full_page=False)
                await off.close()
                print(f"{path.name}: {path.stat().st_size // 1024} KB | offline {'OK' if ok and bubbles else 'FAILED'} | {bubbles} bubbles | fonts {fonts}")
        await b.close()


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--base")]
    base = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--base=")), "https://nexuspoint-demo.vercel.app")
    slugs = [f.stem for f in DEMOS.glob("*-*.json")] if args in (["--all"], []) else args
    asyncio.run(snap(slugs, base))

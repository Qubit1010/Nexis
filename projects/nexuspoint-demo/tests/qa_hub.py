"""Hub QA: full-page screenshots of each demo at 390px and 1440px, dark and light, EN and UR,
plus a horizontal-overflow check. Also checks the expired and bad-token states.

    python tests/qa_hub.py [base_url]     -> tests/qa/*.png
"""
import asyncio
import json
import sys
from pathlib import Path

from playwright.async_api import async_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4400"
DEMOS = Path(__file__).resolve().parents[2] / "quetta-local-market" / "data" / "demos"
OUT = Path(__file__).resolve().parent / "qa"
OVERFLOW = """() => { const W = document.documentElement.clientWidth; const bad = [];
  document.querySelectorAll('body *').forEach(e => { const r = e.getBoundingClientRect();
    if (r.width && (r.right > W + 1 || r.left < -1) && !e.closest('.chips') && getComputedStyle(e).position !== 'fixed') bad.push((e.className || e.tagName) + ''); });
  return bad.slice(0, 5); }"""


async def main():
    OUT.mkdir(exist_ok=True)
    demos = [json.loads(f.read_text(encoding="utf-8")) for f in sorted(DEMOS.glob("*-*.json"))]
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for vname, (w, h) in {"mob": (390, 844), "desk": (1440, 900)}.items():
            for theme in ("dark", "light"):
                ctx = await b.new_context(viewport={"width": w, "height": h}, color_scheme=theme, reduced_motion="reduce")
                pg = await ctx.new_page()
                for d in demos:
                    for lang in ("en", "ur"):
                        url = f"{BASE}/d/{d['slug']}?t={d['token']}" + ("&lang=ur" if lang == "ur" else "")
                        await pg.goto(url, wait_until="networkidle")
                        await pg.evaluate("document.fonts.ready")
                        await pg.wait_for_timeout(600)
                        bad = await pg.evaluate(OVERFLOW)
                        name = f"{d['slug'].rsplit('-', 1)[0][:14]}-{lang}-{vname}-{theme}.png"
                        await pg.screenshot(path=str(OUT / name), full_page=True)
                        print(f"{name:48} {'OVERFLOW ' + str(bad) if bad else 'ok'}")
                await ctx.close()
        pg = await b.new_page()
        d = demos[0]
        r = await pg.goto(f"{BASE}/d/{d['slug']}?t=wrong-token")
        print("bad token ->", r.status)
        await pg.goto(f"{BASE}/d/{d['slug']}?t={d['token']}&chat=1", wait_until="networkidle")
        await pg.set_viewport_size({"width": 390, "height": 844})
        await pg.screenshot(path=str(OUT / "chatmode.png"))
        print("chat mode screenshot ok")
        await b.close()


asyncio.run(main())

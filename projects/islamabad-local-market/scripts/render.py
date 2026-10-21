"""Render the Islamabad sales kit: Jinja templates + data/kit.json -> HTML -> PDF (Playwright) -> PNG previews.

Same API as projects/quetta-local-market/scripts/render.py (load_context, qr_svg, A4, render), so
make_demo.py can render per-prospect Health Checks through it. Every document reads the same
kit.json, so a price or proof change propagates everywhere. Design: Soft Fold v2.0 (templates/brand.css).

Usage (unsandboxed):
    python scripts/render.py                    # everything
    python scripts/render.py onepager report    # named targets only
Targets: onepager, report, deck, healthcheck-sample
"""
import asyncio
import json
import re
import statistics
import sys
from datetime import date
from pathlib import Path

import fitz  # PyMuPDF
import segno
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from playwright.async_api import async_playwright

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]
TPL = PROJECT / "templates"
BUILD = PROJECT / "build"
OUT = PROJECT / "deliverables"
PREVIEW = BUILD / "preview"
DATA = PROJECT / "data"

LOGOS = REPO / "brand-assets" / "nexuspoint-soft-fold-brand-kit-2026-10-02" / "logos"  # approved identity v2.0
ASSETS = {
    "css": (TPL / "brand.css").as_uri(),
    "logo_white": (LOGOS / "nexuspoint-primary-transparent-white.svg").as_uri(),
    "logo_navy": (LOGOS / "nexuspoint-primary-transparent-navy.svg").as_uri(),
    "symbol_white": (LOGOS / "nexuspoint-symbol-transparent-white.svg").as_uri(),
    "symbol_navy": (LOGOS / "nexuspoint-symbol-transparent-navy.svg").as_uri(),
}
FONTS = "https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;600;700&display=block"

A4 = {"format": "A4", "print_background": True, "prefer_css_page_size": True}
SLIDE = {"width": "338.67mm", "height": "190.5mm", "print_background": True}


def flowing(title: str) -> dict:
    """A4 with margins and a running footer, for long documents (cover rendered separately)."""
    foot = ("<div style='width:100%;font:500 6.5px/1 Segoe UI,Arial,sans-serif;letter-spacing:.16em;"
            "text-transform:uppercase;color:#6B6B6B;padding:0 16mm;display:flex;justify-content:space-between'>"
            f"<span>NexusPoint &middot; {title}</span>"
            "<span><span class='pageNumber'></span> / <span class='totalPages'></span></span></div>")
    return {"format": "A4", "print_background": True, "display_header_footer": True,
            "header_template": "<div></div>", "footer_template": foot,
            "margin": {"top": "16mm", "bottom": "18mm", "left": "0", "right": "0"}}


def qr_svg(data: str) -> str:
    return segno.make(data, error="m").svg_inline(scale=4, border=0, dark="#000000")


def _sources() -> list[dict]:
    """[Sn]/[Nn] lines from the research brief's Sources section."""
    brief = (PROJECT / "research" / "islamabad-market-brief.md").read_text(encoding="utf-8")
    out = []
    for line in brief.split("## Sources", 1)[-1].splitlines():
        m = re.match(r"- \[(S\d+|N\d+)\] (?:([PS]) — )?(?:Internal — )?(.*)", line)
        if m:
            text = re.sub(r"(https?://\S+?)(\s;|\s*$)", r"<span style='color:#0079AA'>\1</span>\2", m.group(3))
            out.append({"id": m.group(1), "tier": m.group(2) or "N", "text": text})
    return out


def load_context() -> dict:
    kit = json.loads((DATA / "kit.json").read_text(encoding="utf-8"))
    summary_path = DATA / "maps_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    try:
        from build_prospects import load as load_prospects
        prospects = sorted(load_prospects(), key=lambda r: (-r["score"], -r["reviews"]))
    except (ImportError, FileNotFoundError):
        prospects = []
    return {"kit": kit, "summary": summary, "prospects": prospects, "a": ASSETS, "fonts": FONTS,
            "sources": _sources(),
            "symbol_svg": (LOGOS / "nexuspoint-symbol-transparent-white.svg").read_text(encoding="utf-8"),
            "qr_whatsapp": qr_svg(kit["meta"]["whatsapp_link"]),
            "qr_site": qr_svg("https://" + kit["meta"]["website"]),
            "today": date.today().strftime("%d %B %Y")}


def env() -> Environment:
    e = Environment(loader=FileSystemLoader(str(TPL)), undefined=StrictUndefined, autoescape=False,
                    trim_blocks=True, lstrip_blocks=True)
    e.filters["pkr"] = lambda v: f"PKR {int(v):,}" if isinstance(v, (int, float)) else v
    e.filters["k"] = lambda v: f"{int(v) // 1000:,}k" if isinstance(v, (int, float)) else v
    latin = re.compile(r"([A-Za-z0-9][A-Za-z0-9%.,:+/@\-]*(?: [A-Za-z0-9%.,:+/@\-]+)*%?)")
    e.filters["bidi"] = lambda v: latin.sub(lambda m: f"<bdi dir=\"ltr\">{m.group(0)}</bdi>", str(v))
    e.filters["cite"] = lambda v: re.sub(r"\[((?:S|N)\d+)\]", r"<sup>\1</sup>", str(v))
    e.filters["median"] = lambda xs: statistics.median(xs) if xs else 0
    e.filters["sstats"] = sector_stats
    return e


def sector_stats(rows: list[dict]) -> dict:
    """Headline numbers for a list of prospect rows (build_prospects.load format)."""
    n = len(rows) or 1
    pct = lambda f: round(100 * sum(1 for r in rows if f(r)) / n)  # noqa: E731
    return {
        "n": len(rows),
        "no_site": pct(lambda r: r["website_status"] in ("none", "social-only")
                       or r["website_status"].startswith(("broken", "down"))),
        "unclaimed": pct(lambda r: r["listing_claimed"] == "no"),
        "mobile": pct(lambda r: (r["phone"] or "").replace(" ", "").startswith(("+923", "03"))),
        "median_reviews": int(statistics.median([r["reviews"] for r in rows])) if rows else 0,
        "r100": sum(1 for r in rows if r["reviews"] >= 100),
        "low": sum(1 for r in rows if r["rating"] and r["reviews"] >= 20 and r["rating"] < 4),
        "s70": sum(1 for r in rows if r["score"] >= 70),
    }


def _sample_demo() -> dict:
    """Layout fixture for the Health Check template only: illustrative, never sent to a prospect."""
    return {"name": "Sample Aesthetic Clinic, F-7 Markaz", "slug": "sample", "sector": "healthcare",
            "health": {"score": 58, "items": [
                {"ok": True, "en": "Google listing claimed", "ur": "گوگل لسٹنگ آپ کے نام"},
                {"ok": False, "en": "No reply to 7 of your last 10 reviews", "ur": "آخری 10 میں سے 7 ریویوز کا جواب نہیں"},
                {"ok": True, "en": "Website loads on mobile", "ur": "ویب سائٹ موبائل پر کھلتی ہے"},
                {"ok": False, "en": "No booking button on Google", "ur": "گوگل پر بکنگ کا بٹن نہیں"},
                {"ok": True, "en": "Opening hours listed", "ur": "اوقات درج ہیں"},
                {"ok": False, "en": "Fewer than 10 photos", "ur": "دس سے کم تصاویر"}]},
            "xray": {"stats": {"analysed": 80, "owner_reply_pct": 30},
                     "complaints": [{"theme_en": "Waiting time past appointment", "theme_ur": "وقت پر باری نہیں", "count": 9},
                                    {"theme_en": "Price not shared on WhatsApp", "theme_ur": "واٹس ایپ پر قیمت نہیں بتائی", "count": 6}],
                     "praise": [{"theme_en": "Results after laser sessions", "theme_ur": "لیزر سیشنز کے نتائج", "count": 31},
                                {"theme_en": "Friendly doctor", "theme_ur": "خوش اخلاق ڈاکٹر", "count": 22}],
                     "fixes": [{"en": "Reply to every enquiry in under a minute", "ur": "ہر سوال کا ایک منٹ میں جواب"},
                               {"en": "Remind patients before each session", "ur": "ہر سیشن سے پہلے یاد دہانی"},
                               {"en": "Ask for a review after every visit", "ur": "ہر وزٹ کے بعد ریویو کی درخواست"}]}}


# target name -> list of (template, output stem, pdf options, extra context)
def targets(ctx: dict) -> dict:
    kit = ctx["kit"]
    t = {
        "report": [("report.html.j2", "Islamabad-Market-Intelligence-Report", flowing("Islamabad Market Intelligence"),
                    {"_cover": "report_cover.html.j2"})],
        "deck": [("deck.html.j2", "NexusPoint-Islamabad-Company-Profile", SLIDE, {})],
    }
    t["onepager"] = [("onepager.html.j2", f"OnePager-{s['key']}-{lang}", A4, {"s": s, "lang": lang})
                     for s in kit["sectors"] if s.get("onepager") and s.get("op") for lang in ("en", "ur")]
    sample = {"demo": _sample_demo(), "qr_hub": qr_svg("https://nexus-point.co"), "qr_chat": ctx["qr_whatsapp"],
              "prepared": date.today().isoformat()}
    # re-render every saved prospect demo (written by make_demo.py), e.g. after a template change
    t["healthcheck"] = []
    for f in sorted((DATA / "demos").glob("*.json")):
        demo = json.loads(f.read_text(encoding="utf-8"))
        if "health" not in demo:
            continue
        hub = f"https://nexuspoint-demo.vercel.app/d/{demo['slug']}?t={demo['token']}"
        extra = {"demo": demo, "qr_hub": qr_svg(hub), "qr_chat": qr_svg(f"{hub}&chat=1"), "prepared": date.today().isoformat()}
        t["healthcheck"] += [("healthcheck.html.j2", f"Health-Check-{demo['slug']}-{lang}", A4, {**extra, "lang": lang})
                             for lang in ("en", "ur")]
    t["healthcheck-sample"] =[("healthcheck.html.j2", f"Health-Check-SAMPLE-{lang}", A4, {**sample, "lang": lang})
                               for lang in ("en", "ur")]
    return t


async def render(jobs: list, ctx: dict) -> list[Path]:
    e = env()
    BUILD.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    made = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        for tpl, stem, opts, extra in jobs:
            if not (TPL / tpl).exists():
                print(f"[skip] {tpl} missing")
                continue
            pdf_path = OUT / f"{stem}.pdf"
            parts = [(extra["_cover"], A4, f"{stem}-cover")] if extra.get("_cover") else []
            parts.append((tpl, opts, stem))
            part_pdfs = []
            for part_tpl, part_opts, part_stem in parts:
                html = e.get_template(part_tpl).render(**{**ctx, **extra})
                html_path = BUILD / f"{part_stem}.html"
                html_path.write_text(html, encoding="utf-8")
                await page.goto(html_path.as_uri(), wait_until="networkidle")
                await page.evaluate("document.fonts.ready")
                await page.wait_for_timeout(400)
                over = await page.evaluate("""[...document.querySelectorAll('.page, .slide')].map((p, i) => {
                    const bottom = p.getBoundingClientRect().bottom;
                    const worst = Math.max(0, ...[...p.querySelectorAll('*')]
                      .filter(el => !el.closest('.mark') && !el.classList.contains('point')
                        && !(el.closest('svg') && el.tagName.toLowerCase() !== 'svg'))
                      .map(el => el.getBoundingClientRect().bottom - bottom));
                    return [i + 1, Math.round(worst)]; }).filter(([, d]) => d > 2)""")
                if over:
                    print(f"[overflow] {part_stem}: " + ", ".join(f"page {i} +{d}px" for i, d in over))
                part_pdf = BUILD / f"{part_stem}.pdf"
                await page.pdf(path=str(part_pdf), **part_opts)
                part_pdfs.append(part_pdf)
            merged = fitz.open()
            for pp in part_pdfs:
                merged.insert_pdf(fitz.open(pp))
            merged.save(str(pdf_path))
            made.append(pdf_path)
            doc = fitz.open(pdf_path)
            for i, pg in enumerate(doc):
                pg.get_pixmap(dpi=70).save(str(PREVIEW / f"{stem}-p{i + 1:02d}.png"))
            print(f"[ok] {pdf_path.name}: {len(doc)} page(s)")
        await browser.close()
    return made


def main() -> None:
    ctx = load_context()
    all_targets = targets(ctx)
    names = sys.argv[1:] or list(all_targets)
    jobs = [job for n in names for job in all_targets.get(n, [])]
    asyncio.run(render(jobs, ctx))


if __name__ == "__main__":
    main()

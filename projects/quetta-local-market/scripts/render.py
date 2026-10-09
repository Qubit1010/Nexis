"""Render the Quetta sales kit: Jinja templates + data/kit.json -> HTML -> PDF (Playwright) -> PNG previews.

Every document reads the same data file, so a price or proof change propagates everywhere.

Usage (unsandboxed, Python312):
    python scripts/render.py                 # everything
    python scripts/render.py report onepager # named targets only
Targets: see TARGETS below.
"""
import asyncio
import csv
import json
import re
import sys
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

KIT = REPO / "brand-assets" / "nexuspoint-soft-fold-brand-kit-2026-10-02" / "logos"  # approved identity v2.0, 2 Oct 2026
ASSETS = {
    "css": (TPL / "brand.css").as_uri(),
    "logo_white": (KIT / "nexuspoint-primary-transparent-white.svg").as_uri(),
    "logo_black": (KIT / "nexuspoint-primary-transparent-navy.svg").as_uri(),
    "mark_black": (KIT / "nexuspoint-symbol-transparent-navy.svg").as_uri(),
}
FONTS = ("https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,400;0,500;0,600;0,700;0,800;1,600"
         "&family=Noto+Nastaliq+Urdu:wght@400;600;700&display=block")

A4 = {"format": "A4", "print_background": True, "prefer_css_page_size": True}
SLIDE = {"width": "338.67mm", "height": "190.5mm", "print_background": True}


def flowing(title: str) -> dict:
    """A4 with margins and a running footer, for long documents (cover rendered separately)."""
    foot = ("<div style='width:100%;font:500 7px/1 Consolas,monospace;letter-spacing:.12em;"
            "text-transform:uppercase;color:#475569;padding:0 16mm;display:flex;justify-content:space-between'>"
            f"<span>NexusPoint &middot; {title}</span>"
            "<span><span class='pageNumber'></span> / <span class='totalPages'></span></span></div>")
    return {"format": "A4", "print_background": True, "display_header_footer": True,
            "header_template": "<div></div>", "footer_template": foot,
            "margin": {"top": "16mm", "bottom": "18mm", "left": "0", "right": "0"}}


def qr_svg(data: str) -> str:
    return segno.make(data, error="m").svg_inline(scale=4, border=0, dark="#02040A")


def load_context() -> dict:
    kit = json.loads((PROJECT / "data" / "kit.json").read_text(encoding="utf-8"))
    summary_path = PROJECT / "data" / "prospects_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    # prospect sectors only: drop competitors and any query that under-returned (<10 rows)
    summary = {k: v for k, v in summary.items() if k != "competitor" and v["businesses"] >= 10}
    prospects = []
    csv_path = PROJECT / "data" / "prospects.csv"
    if csv_path.exists():
        with open(csv_path, encoding="utf-8-sig") as fh:
            prospects = list(csv.DictReader(fh))
    for p in prospects:
        p["score"], p["reviews"] = int(p["score"]), int(p["reviews"] or 0)
    sources = []
    for line in (PROJECT / "research" / "sources.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"- \[(S\d+|N\d+)\] (?:([PS]) — )?(.*)", line)
        if m:
            text = re.sub(r"(https?://\S+)", r"<span class='num' style='color:#0369A1'>\1</span>", m.group(3))
            sources.append({"id": m.group(1), "tier": m.group(2) or "N", "text": text})
    sources.sort(key=lambda s: (s["id"][0] != "S", int(s["id"][1:])))
    comp_path = PROJECT / "data" / "competitors.json"
    competitors = json.loads(comp_path.read_text(encoding="utf-8")) if comp_path.exists() else {}
    return {"kit": kit, "summary": summary, "prospects": prospects, "a": ASSETS, "fonts": FONTS,
            "sources": sources, "competitors": competitors,
            "qr_whatsapp": qr_svg(kit["meta"]["whatsapp_link"]),
            "qr_site": qr_svg("https://" + kit["meta"]["website"])}


def env() -> Environment:
    e = Environment(loader=FileSystemLoader(str(TPL)), undefined=StrictUndefined, autoescape=False,
                    trim_blocks=True, lstrip_blocks=True)
    e.filters["pkr"] = lambda v: f"PKR {int(v):,}" if isinstance(v, (int, float)) else v
    e.filters["k"] = lambda v: f"{int(v) // 1000:,}k" if isinstance(v, (int, float)) else v
    latin = re.compile(r"([A-Za-z0-9][A-Za-z0-9%.,:+/@\-]*(?: [A-Za-z0-9%.,:+/@\-]+)*%?)")
    e.filters["bidi"] = lambda v: latin.sub(lambda m: f"<bdi dir=\"ltr\">{m.group(0)}</bdi>", str(v))
    e.filters["top"] = lambda rows, sector, n=10: [r for r in rows if r["sector"] == sector][:n]
    return e


# target name -> list of (template, output stem, pdf options, extra context)
def targets(ctx: dict) -> dict:
    kit = ctx["kit"]
    t = {
        "report": [("report.html.j2", "Quetta-Market-Intelligence-Report", flowing("Quetta Market Intelligence"),
                    {"_cover": "report_cover.html.j2"})],
        "deck": [("deck.html.j2", "NexusPoint-Quetta-Company-Profile", SLIDE, {})],
        "playbook": [("playbook.html.j2", "Quetta-Outreach-Playbook", flowing("Quetta Outreach Playbook"),
                      {"_cover": "playbook_cover.html.j2"})],
        "cases": [("cases.html.j2", "NexusPoint-Case-Sheets", A4, {})],
        "healthcheck": [("healthcheck.html.j2", "Digital-Health-Check", A4, {})],
        "launchkit": [("launchkit.html.j2", "Quetta-Launch-Kit", A4, {})],
        "agreement": [("agreement.html.j2", "NexusPoint-Service-Agreement", A4, {})],
        "pricing": [("pricing.html.j2", "NexusPoint-Quetta-Pricing", A4, {})],
    }
    sectors = kit.get("sectors", [])
    t["onepager"] = [("onepager.html.j2", f"OnePager-{s['key']}-{lang}", A4, {"s": s, "lang": lang})
                     for s in sectors if s.get("onepager") and s.get("op") for lang in ("en", "ur")]
    t["proposal"] = [("proposal.html.j2", f"Proposal-{s['key']}", A4, {"s": s})
                     for s in sectors if s.get("proposal")]
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
            parts = []
            if extra.get("_cover"):
                parts.append((extra["_cover"], A4, f"{stem}-cover"))
            parts.append((tpl, opts, stem))
            part_pdfs = []
            for part_tpl, part_opts, part_stem in parts:
                html = e.get_template(part_tpl).render(**ctx, **extra)
                html_path = BUILD / f"{part_stem}.html"
                html_path.write_text(html, encoding="utf-8")
                await page.goto(html_path.as_uri(), wait_until="networkidle")
                await page.evaluate("document.fonts.ready")
                await page.wait_for_timeout(400)
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

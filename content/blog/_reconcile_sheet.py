"""Repoint the Sheet's image columns at the portfolio, and mark what shipped.

Run after publishing an article into aleem-portfolio. The Sheet was built when
the images lived only in this repo under a public-URL shape (/blog/images/...).
Astro content-hashes the emitted filenames, so a fixed URL there would be wrong
on every build. The columns now carry SOURCE paths, and the note says so.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / ".claude" / "skills" / "leads-to-crm" / "scripts"))
import sheets  # noqa: E402

SID = "1irhRYKXlDz94VqCi43y1jPBjNLa3UFGI7Uk2pOCKH7s"
BLOG = Path(__file__).resolve().parent
NL = chr(10)
SITE = "https://aleemuh.com"

# Sheet row order, set by _build_sheet.ORDER. Row 2 is the first article.
ORDER = [
    "ai-agent-vs-skill",
    "how-to-outsource-web-development",
    "ai-automation-cost",
    "ai-agent-evaluation-framework",
    "best-n8n-projects",
    "ai-agent-vs-automation",
]
PUBLISHED = {"ai-agent-vs-skill": "2026-08-23"}


def image_cells(slug: str):
    d = BLOG / "images" / slug
    cover, support, alt, svg = "", [], [], []
    for f in sorted(d.glob("*.svg")):
        dest = f"src/assets/blog/{slug}/{f.stem}.png"
        m = re.search(r'aria-label="([^"]+)"', f.read_text(encoding="utf-8"))
        a = " ".join(m.group(1).split()) if m else ""
        if f.stem == "cover":
            cover = dest
            alt.insert(0, f"cover: {a}")
        else:
            support.append(dest)
            alt.append(f"{f.stem}: {a}")
        # SVGs stay here. The PNG is a build artifact; the SVG is the source.
        svg.append(f"content/blog/images/{slug}/{f.name}")
    return [cover, NL.join(support), NL.join(alt), NL.join(svg)]


def main():
    hdr = ["Cover Image (portfolio src)", "Supporting Images (portfolio src)",
           "Image Alt Text", "SVG Source (Nexis)", "Live URL"]
    sheets.update_range(SID, "Articles!V1:Z1", [hdr])
    for i, slug in enumerate(ORDER, start=2):
        live = f"{SITE}/blog/{slug}" if slug in PUBLISHED else ""
        sheets.update_range(SID, f"Articles!V{i}:Z{i}", [image_cells(slug) + [live]])
        print(f"  row {i}: {slug}{'  -> ' + live if live else ''}")

    for i, slug in enumerate(ORDER, start=2):
        if slug in PUBLISHED:
            status = f"Published {PUBLISHED[slug]}"
            sheets.update_range(SID, f"Articles!A{i}", [[status]])
            sheets.update_range(SID, f"Calendar!H{i}", [[status]])
            print(f"  status row {i}: {status}")

    note = ("Image columns hold SOURCE paths, not live URLs. Astro content-hashes "
            "the emitted filenames at build time (cover.BxQ8_jYs_*.webp), so any "
            "fixed URL here would be wrong on the next build. Copy the PNGs to "
            "src/assets/blog/<slug>/ and reference them by relative markdown path; "
            "alt text is authored in each SVG's aria-label, so it cannot drift.")
    sheets.update_range(SID, "Validation!A20:B20", [["Images", note]])
    print(f"\nhttps://docs.google.com/spreadsheets/d/{SID}/edit")


if __name__ == "__main__":
    main()

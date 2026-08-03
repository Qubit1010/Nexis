#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render the SEO course markdown into per-section PDFs and one merged master.

    python build_course_pdf.py sections        # render every section PDF
    python build_course_pdf.py section 07      # render one section
    python build_course_pdf.py full            # render all + TOC + merge

Design note: the markdown in `references/course/` is the SINGLE source of truth.
The Claude Playbook build required a hand-written `section_NN.py` carrying a parallel
block-dict copy of every section, so each edit had to land in two places. Here the
markdown is parsed directly, so it cannot drift.

Supported markdown subset (matches the section template in SKILL.md):
    # <Tier> - Section <N>: <Title>     -> kicker + title + rule
    *deck line*                          -> deck
    **Bottom line:** ...                 -> callout
    ## / ###                             -> h2 / h3
    > **Label:** text                    -> callout
    - item   /   1. item                 -> bullets / numbers
    | a | b |  (with a --- separator row) -> table
    ---                                  -> rule
    everything else                      -> body paragraph
Inline: **bold**, *italic*, `code`, [text](url).
"""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import seo_pdf  # noqa: E402
from seo_pdf import build  # noqa: E402

SKILL_DIR = Path(__file__).resolve().parent.parent
COURSE_DIR = SKILL_DIR / "references" / "course"

# Output paths are overridable so a build can still run when a PDF viewer has the
# canonical files open (Windows locks them, and reportlab dies with PermissionError).
OUT_DIR = Path(os.environ.get("SEO_PDF_OUT_DIR") or COURSE_DIR / "pdf")
MASTER = Path(
    os.environ.get("SEO_PDF_MASTER") or COURSE_DIR / "The-2026-SEO-Playbook-FULL.pdf"
)

FOOTER = "NexusPoint  |  The 2026 SEO Playbook"

# ------------------------------------------------------------------ front + back matter

COVER = {
    "doc_title": "The 2026 SEO Playbook",
    "kicker": "NexusPoint",
    "title_lines": ["The 2026", "SEO Playbook"],
    "deck": "Four tiers. Forty-two sections. One climb.",
    "stats": ["4 TIERS", "·", "42 SECTIONS", "·", "BEGINNER TO ADVANCED"],
    "blurb": [
        "A complete, practical course in how search works now: the classic",
        "four disciplines, and the AI answer layer that broke the old model.",
        "Every section ends with a lab you run on a real site, and a step in",
        "one capstone project carried from the first page to the last.",
    ],
    "provenance": "Built on a cited 320-source 2026 corpus. Every load-bearing claim "
                  "tagged [confirmed] or [practitioner].",
    "date": "August 2026",
}

CLOSING_TITLE = "Where You Are Now"

CLOSING_BLOCKS = [
    {"type": "kicker", "text": "Closing"},
    {"type": "title", "text": "Where You Are Now"},
    {"type": "deck", "text": "Forty-two sections in. What you have, and what to keep."},
    {"type": "rule"},

    {"type": "body", "text":
     "You started with a site and a vague sense that SEO was a list of tactics. "
     "You finish with a map of four disciplines, a capstone site that has been "
     "audited and rebuilt against every one of them, and a way of judging claims "
     "that outlives any specific tactic in this book."},

    {"type": "h2", "text": "What the capstone has"},
    {"type": "bullets", "items": [
        "<b>Foundations.</b> A keyword map built on intent, a first properly "
        "optimized page, and measurement wired up before any of the work began.",
        "<b>On-page.</b> Titles and metas rewritten, content restructured into "
        "clusters, internal linking deliberate, E-E-A-T demonstrated rather than "
        "claimed, and a prune-and-consolidate pass done.",
        "<b>Technical.</b> Crawlable, indexable, canonically clean, correctly "
        "redirected, sensibly structured, renderable without JavaScript, fast "
        "enough on mobile, and marked up with schema that matches what is visible.",
        "<b>Authority and AI.</b> A baselined link profile, reclaimed brand "
        "mentions, entity identity anchored in Wikidata and <i>sameAs</i>, a "
        "deliberate AI crawler policy, and citation share tracked across four "
        "answer engines.",
    ]},

    {"type": "h2", "text": "The three things worth carrying"},
    {"type": "numbers", "items": [
        "<b>Evidence tiers.</b> You now separate what Google confirmed from what a "
        "vendor asserted. Only seven ranking factors are confirmed. The corpus "
        "behind this book is 18 confirmed sources against 302 practitioner ones, "
        "and pretending otherwise is how bad advice spreads.",
        "<b>Floors versus levers.</b> Core Web Vitals, mobile-friendliness and "
        "HTTPS are floors: failing suppresses you, exceeding buys nothing. Content, "
        "authority and topical coverage are levers. Most wasted SEO budget is "
        "someone optimizing a floor.",
        "<b>Coverage beats optimization.</b> Query fan-out turns one prompt into "
        "ten to twenty searches, so comprehensive topical coverage catches what a "
        "single optimized page misses. 80%+ coverage retains 85.4% of AI visibility.",
    ]},

    {"type": "callout", "title": "The honest summary of 2026",
     "text": "Informational click volume is structurally down and will not recover. "
             "Commercial intent is far more resilient. AI-referred traffic converts "
             "4 to 5x better than traditional search. Ranking and being cited have "
             "come apart, so they are two reports now, not one. None of that means "
             "SEO is dead. It means the thing being optimized changed from a "
             "position to a selection."},

    {"type": "h2", "text": "The cadence from here"},
    {"type": "body", "text":
     "SEO has no finish line, it has a rhythm: <b>audit, fix, publish, measure, "
     "adjust</b>. Section 42's 90-day plan is one turn of it. Run the technical "
     "audit quarterly, refresh important content on the same schedule because "
     "Perplexity deprioritizes anything over 90 days, check citation share monthly, "
     "and keep an action log so the six-month lag before results is survivable."},

    {"type": "h2", "text": "When this book is wrong"},
    {"type": "body", "text":
     "It will be, in places, and sooner than you would like. Search is moving fast "
     "enough that specific numbers age in months. What should hold longer is the "
     "method: ask who measured a claim, whether it was causal or correlational, and "
     "whether the source sells the thing it is recommending. When a number here "
     "conflicts with something you can verify directly, trust what you can verify."},

    {"type": "h2", "text": "How this was built"},
    {"type": "body", "text":
     "Fourteen deep research passes through a multi-engine pipeline produced 399 raw "
     "sources, deduped to <b>320</b> and split across six notebooks. Every claim was "
     "synthesized with citations and tagged by evidence tier. Where sources "
     "disagreed, both numbers are shown rather than averaged. Where no evidence "
     "existed, the gap is stated instead of filled. The full cited synthesis lives "
     "in the skill at <i>references/research-synthesis.md</i>, and every [sN] marker "
     "there resolves to a real URL in <i>_research/sources.json</i>."},

    {"type": "spacer", "h": 6},
    {"type": "rule"},
    {"type": "lead", "text": "Now go and rank something."},
]


# ------------------------------------------------------------------ inline

def inline(text):
    """Markdown inline -> reportlab mini-HTML. Escape entities FIRST."""
    t = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"`([^`]+)`", r'<font face="Courier">\1</font>', t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
               r'<link href="\2" color="#0F766E">\1</link>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![*\w])\*([^*]+)\*(?!\*)", r"<i>\1</i>", t)
    return t.strip()


# ------------------------------------------------------------------ parse

_H1 = re.compile(r"^#\s+(?:(.+?)\s+-\s+)?(Section\s+\d+):\s*(.+)$", re.I)
_CALLOUT = re.compile(r"^>\s*\*\*(.+?):\*\*\s*(.*)$")


def parse_markdown(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    blocks, meta = [], {"title": path.stem, "footer": FOOTER}
    i, n = 0, len(lines)
    seen_rule = False
    seen_h1 = False

    def is_structural(s):
        return (not s or s.startswith(("#", ">", "|"))
                or re.match(r"^[-*]\s+", s) or re.match(r"^\d+[.)]\s+", s)
                or re.fullmatch(r"-{3,}|\*{3,}|_{3,}", s))

    def take_continuations(idx):
        """Markdown lazy continuation: unindented wrapped lines belong to the item
        above. Without this, every hard-wrapped bullet splits into a stray paragraph."""
        extra = []
        while idx < n:
            nxt = lines[idx].strip()
            if is_structural(nxt):
                break
            extra.append(nxt)
            idx += 1
        return idx, extra

    while i < n:
        raw = lines[i]
        line = raw.rstrip()
        s = line.strip()

        if not s:
            i += 1
            continue

        # H1 -> kicker + title
        if s.startswith("# "):
            m = _H1.match(s)
            if m:
                tier, sec, title = m.group(1), m.group(2), m.group(3)
                kicker = f"{tier}  -  {sec}" if tier else sec
                blocks.append({"type": "kicker", "text": kicker})
                blocks.append({"type": "title", "text": inline(title)})
                # Only the FIRST h1 names the document. A later h1 (tier divider in
                # the curriculum) must not rename the whole PDF.
                if not seen_h1:
                    meta["title"] = title
                    meta["tier"] = tier or "Sections"
                    meta["footer"] = f"{FOOTER}  |  {tier}" if tier else FOOTER
            else:
                blocks.append({"type": "title", "text": inline(s[2:])})
                if not seen_h1:
                    meta["title"] = s[2:]
            seen_h1 = True
            i += 1
            continue

        if s.startswith("### "):
            blocks.append({"type": "h3", "text": inline(s[4:])})
            i += 1
            continue

        if s.startswith("## "):
            blocks.append({"type": "h2", "text": inline(s[3:])})
            i += 1
            continue

        # Horizontal rule. Only the first one (under the deck) draws the accent bar;
        # later ones are just section breathing room.
        if re.fullmatch(r"-{3,}|\*{3,}|_{3,}", s):
            if not seen_rule:
                blocks.append({"type": "rule"})
                seen_rule = True
            else:
                blocks.append({"type": "spacer", "h": 6})
            i += 1
            continue

        # Deck: a lone fully-italic line, before the first rule.
        if not seen_rule and re.fullmatch(r"\*[^*].*[^*]\*", s):
            blocks.append({"type": "deck", "text": inline(s[1:-1])})
            i += 1
            continue

        # Blockquote callout (possibly multi-line).
        if s.startswith(">"):
            quote = []
            while i < n and lines[i].strip().startswith(">"):
                quote.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            joined = " ".join(q for q in quote if q).strip()
            m = _CALLOUT.match("> " + joined)
            if m:
                blocks.append({"type": "callout", "title": inline(m.group(1)),
                               "text": inline(m.group(2))})
            else:
                blocks.append({"type": "callout", "title": None, "text": inline(joined)})
            continue

        # Table
        if s.startswith("|") and i + 1 < n and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            headers = [c.strip() for c in s.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([inline(c.strip()) for c in lines[i].strip().strip("|").split("|")])
                i += 1
            blocks.append({"type": "table",
                           "headers": [inline(h) for h in headers],
                           "rows": rows})
            continue

        # Lists
        if re.match(r"^[-*]\s+", s):
            items = []
            while i < n and re.match(r"^[-*]\s+", lines[i].strip()):
                item = re.sub(r"^[-*]\s+", "", lines[i].strip())
                i += 1
                i, extra = take_continuations(i)
                items.append(inline(" ".join([item] + extra)))
            blocks.append({"type": "bullets", "items": items})
            continue

        if re.match(r"^\d+[.)]\s+", s):
            items = []
            while i < n and re.match(r"^\d+[.)]\s+", lines[i].strip()):
                item = re.sub(r"^\d+[.)]\s+", "", lines[i].strip())
                i += 1
                i, extra = take_continuations(i)
                items.append(inline(" ".join([item] + extra)))
            blocks.append({"type": "numbers", "items": items})
            continue

        # Paragraph (join until a blank line or a structural marker).
        para = []
        while i < n:
            cur = lines[i].strip()
            if (not cur or cur.startswith(("#", ">", "|", "- ", "* "))
                    or re.match(r"^\d+[.)]\s+", cur)
                    or re.fullmatch(r"-{3,}|\*{3,}|_{3,}", cur)):
                break
            para.append(cur)
            i += 1
        text = " ".join(para).strip()
        if not text:
            continue
        m = re.match(r"^\*\*(Bottom line|Key insight|The rule)\:?\*\*\s*(.+)$", text, re.I)
        if m:
            blocks.append({"type": "callout", "title": m.group(1),
                           "text": inline(m.group(2))})
        else:
            blocks.append({"type": "body", "text": inline(text)})

    return meta, blocks


# ------------------------------------------------------------------ render

def section_files():
    return sorted(p for p in COURSE_DIR.glob("*.md")
                  if re.match(r"^\d{2}-", p.name) and not p.name.startswith("00-"))


def render_section(md_path, start_page=1):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    meta, blocks = parse_markdown(md_path)
    seo_pdf._START_PAGE = start_page
    out = OUT_DIR / (md_path.stem + ".pdf")
    build(meta, blocks, str(out))
    return out


def render_all():
    files = section_files()
    if not files:
        raise SystemExit(f"no section markdown found in {COURSE_DIR}")
    for f in files:
        out = render_section(f)
        print(f"  {f.name} -> {out.name}")
    return files


# ------------------------------------------------------------------ merge

def _pages(pdf):
    from PyPDF2 import PdfReader
    return len(PdfReader(str(pdf)).pages)


def build_cover():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "_cover.pdf"
    seo_pdf.cover(COVER, str(out))
    return out


def build_toc(entries, start_page):
    """entries: [(tier, title, start_page)] -> a TOC pdf."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    blocks = [
        {"type": "kicker", "text": "Contents"},
        {"type": "title", "text": "The 2026 SEO Playbook"},
        {"type": "deck", "text": "Four tiers. Forty-two sections. One climb."},
        {"type": "rule"},
    ]
    by_tier = {}
    for tier, title, page in entries:
        by_tier.setdefault(tier, []).append((title, page))
    from reportlab.lib.units import inch
    for tier, rows in by_tier.items():
        blocks.append({"type": "h2", "text": tier})
        blocks.append({"type": "table",
                       "headers": ["Section", "Page"],
                       "rows": [[t, str(p)] for t, p in rows],
                       "widths": [5.65 * inch, 0.95 * inch]})
    seo_pdf._START_PAGE = start_page
    out = OUT_DIR / "_toc.pdf"
    build({"title": "Contents", "footer": FOOTER}, blocks, str(out))
    return out


def build_closing(start_page=1):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    seo_pdf._START_PAGE = start_page
    out = OUT_DIR / "_closing.pdf"
    build({"title": CLOSING_TITLE, "footer": f"{FOOTER}  |  Closing"},
          CLOSING_BLOCKS, str(out))
    return out


def build_full():
    from PyPDF2 import PdfMerger
    files = section_files()
    if not files:
        raise SystemExit(f"no section markdown found in {COURSE_DIR}")

    # First pass: page counts with provisional numbering.
    for f in files:
        render_section(f)
    counts = [_pages(OUT_DIR / (f.stem + ".pdf")) for f in files]
    metas = [parse_markdown(f)[0] for f in files]

    cover = build_cover()
    cover_pages = _pages(cover)

    closing_pages = _pages(build_closing())

    # The TOC's own length shifts every section's start page, which shifts the TOC.
    # Iterate to a fixpoint (converges in 2-3 rounds). Printed page numbers are kept
    # equal to physical PDF pages, so the cover counts but prints no footer.
    toc_pages = 1
    for _ in range(6):
        toc_start = cover_pages + 1
        page = toc_start + toc_pages
        entries = []
        for m, c in zip(metas, counts):
            entries.append((m.get("tier", "Sections"), m["title"], page))
            page += c
        entries.append(("Closing", CLOSING_TITLE, page))
        toc = build_toc(entries, toc_start)
        new_toc_pages = _pages(toc)
        if new_toc_pages == toc_pages:
            break
        toc_pages = new_toc_pages

    # Re-render each part with its true start page so numbering is continuous.
    starts = [e[2] for e in entries]
    for f, sp in zip(files, starts):
        render_section(f, start_page=sp)
    closing = build_closing(start_page=starts[-1])

    merger = PdfMerger()
    merger.append(str(cover))
    merger.append(str(toc))
    for f in files:
        merger.append(str(OUT_DIR / (f.stem + ".pdf")))
    merger.append(str(closing))
    merger.write(str(MASTER))
    merger.close()
    total = _pages(MASTER)
    print(f"\n{MASTER.name}: {len(files)} sections, {total} pages "
          f"(cover {cover_pages}p, TOC {toc_pages}p, sections start p{starts[0]}, "
          f"closing {closing_pages}p at p{starts[-1]})")
    return MASTER


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "sections"
    if cmd == "sections":
        render_all()
    elif cmd == "section":
        which = sys.argv[2]
        hits = [p for p in section_files() if p.name.startswith(which)]
        if not hits:
            raise SystemExit(f"no section matching {which!r}")
        print(render_section(hits[0]))
    elif cmd == "cover":
        print(build_cover())
    elif cmd == "closing":
        print(build_closing())
    elif cmd == "full":
        build_full()
    else:
        raise SystemExit(
            f"unknown command: {cmd} (sections | section NN | cover | closing | full)")

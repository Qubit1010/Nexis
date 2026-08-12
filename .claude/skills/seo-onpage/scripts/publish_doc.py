#!/usr/bin/env python3
"""Publish an on-page audit report as a properly formatted Google Doc.

Why this exists rather than reusing blog-writer/scripts/publish.py:

That script is a thin adapter built for blog posts, and it does three things that are
correct there and destructive here.

  1. `strip_inline_md()` removes **bold**, so every "Evidence:", "Fix:", "Expected effect:"
     label in an audit collapses into plain running text. Those labels are the scan
     structure of the document - without them a client reads six identical grey paragraphs.
  2. It flattens `[text](url)` to bare text, which silently deletes the link to the working
     Sheet. On an audit the Sheet IS the deliverable.
  3. Its bullet parser treats a wrapped continuation line as a new paragraph, so a bullet
     that runs past the line width splits in half and the tail becomes an orphan paragraph
     sitting outside the list.

So this builds the `save_content.py` payload directly from a structured spec instead of
round-tripping through markdown. `save_content.py` already supports everything needed -
`bold_bullets` with a bolded label, real `table` blocks with computed column widths, and
heading levels - none of which survives a markdown flatten.

Markdown remains the source of truth on disk. This renders it.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO = SKILL_DIR.parents[2]
SAVE_CONTENT = REPO / ".claude" / "skills" / "content-engine" / "scripts" / "save_content.py"

# save_content.py normalizes the whole payload: smart quotes, em dash -> " - ", ellipsis.
# So write plain ASCII here and let it pass through unchanged.
LABELS = ("Evidence", "Fix", "Expected effect", "Effort", "Scope note", "Confidence",
          "Built from", "Working artifact", "Date", "Page audited", "Primary query",
          # Added for seo-technical's report, which is a site audit rather than a page one.
          # A label missing from this list renders as unbolded running text, so the header
          # block silently loses its scan structure.
          "Site audited", "Scope", "Deployable fixes", "Why it matters")


def _inline(text: str) -> str:
    """Drop markdown emphasis marks but keep the words, and keep a link's URL visible."""
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"\1: \2", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"\1", text)
    text = text.replace("`", "")
    return re.sub(r"\s+", " ", text).strip()


def _table(lines: list[str]) -> dict | None:
    rows = [l for l in lines if l.strip().startswith("|")]
    if len(rows) < 2:
        return None
    def cells(r):
        return [_inline(c) for c in r.strip().strip("|").split("|")]
    header = cells(rows[0])
    body = [cells(r) for r in rows[2:] if r.strip().strip("|").strip()]
    body = [r for r in body if any(c for c in r)]
    if not body:
        return None
    width = len(header)
    body = [(r + [""] * width)[:width] for r in body]
    return {"headers": header, "rows": body}


def parse(md: str) -> list[dict]:
    """Markdown -> save_content sections, preserving labels, bullets and tables."""
    sections: list[dict] = []
    buf: list[str] = []          # paragraph accumulator
    bullets: list[str] = []      # bullet accumulator
    table_lines: list[str] = []

    def flush_para():
        nonlocal buf
        if not buf:
            return
        text = _inline(" ".join(buf))
        buf = []
        if not text:
            return
        # "Evidence. ..." / "Fix. ..." become bolded labels so the doc is scannable.
        m = re.match(r"^(%s)[.:]\s+(.*)$" % "|".join(LABELS), text)
        if m:
            sections.append({"bold_bullets": [{"label": m.group(1) + ": ", "text": m.group(2)}]})
        else:
            sections.append({"body": text})

    def flush_bullets():
        """Bullets, keeping a `**lead-in.**` bold instead of flattening it.

        `_inline()` strips every `**`, which is right inside running prose and wrong at the
        start of a bullet: a list like "**Crawlability is correct.** robots.txt returns
        200..." is written as label-plus-explanation, and without the label the reader gets
        eight identical grey paragraphs with no scan structure. That is the same failure
        this module's docstring describes fixing for `Evidence:`/`Fix:` labels, and it was
        still happening one level down inside lists.

        A run of bullets is emitted as one list either way, so a mixed list (some with a
        lead-in, some without) stays visually a single list rather than splitting in two.
        """
        nonlocal bullets
        if not bullets:
            return
        parsed = []
        for b in bullets:
            m = re.match(r"^\*\*(.+?)\*\*\s*(.*)$", b.strip(), re.S)
            if m:
                rest = _inline(m.group(2))
                parsed.append({"label": _inline(m.group(1)),
                               "text": (" " + rest) if rest else ""})
            else:
                parsed.append({"label": "", "text": _inline(b)})
        if any(p["label"] for p in parsed):
            sections.append({"bold_bullets": parsed})
        else:
            sections.append({"bullets": [p["text"] for p in parsed]})
        bullets = []

    def flush_table():
        nonlocal table_lines
        if table_lines:
            t = _table(table_lines)
            if t:
                sections.append({"table": t})
            table_lines = []

    for raw in md.splitlines():
        line = raw.rstrip()
        stripped = line.strip()

        if stripped.startswith("|"):
            flush_para(); flush_bullets()
            table_lines.append(stripped)
            continue
        flush_table()

        if not stripped or stripped == "---":
            flush_para(); flush_bullets()
            continue

        h = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if h:
            flush_para(); flush_bullets()
            sections.append({"heading": _inline(h.group(2)),
                             "level": min(3, len(h.group(1)))})
            continue

        b = re.match(r"^[-*]\s+(.*)$", stripped)
        if b:
            flush_para()
            bullets.append(b.group(1))
            continue

        # A continuation line under a bullet belongs to that bullet, not to a new paragraph.
        # This is the specific bug that split "...on a" / "200-acre site outside town" apart.
        if bullets and raw.startswith(("  ", "\t")):
            bullets[-1] += " " + stripped
            continue
        if buf or not bullets:
            buf.append(stripped)
        else:
            bullets[-1] += " " + stripped

    flush_para(); flush_bullets(); flush_table()
    return [s for s in sections if s]


def main() -> int:
    ap = argparse.ArgumentParser(description="Publish an on-page audit as a formatted Google Doc.")
    ap.add_argument("path", nargs="?", help="the report markdown file")
    ap.add_argument("--title", help="Doc title (defaults to the first H1)")
    ap.add_argument("--dry-run", action="store_true", help="print the payload, do not publish")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        md = ("# T\n\n## S\n\n**Evidence.** A measured thing.\n\n"
              "- first bullet that wraps\n  onto a second line\n- second bullet\n\n"
              "| A | B |\n|---|---|\n| 1 | 2 |\n\n"
              "See the [Sheet](https://docs.google.com/x) for detail.\n")
        secs = parse(md)
        ok = True
        checks = [
            ("heading kept", any(s.get("heading") == "T" for s in secs)),
            ("Evidence became a bold label",
             any(s.get("bold_bullets", [{}])[0].get("label") == "Evidence: " for s in secs)),
            ("wrapped bullet stayed one bullet",
             any(s.get("bullets") == ["first bullet that wraps onto a second line", "second bullet"]
                 for s in secs)),
            ("table parsed",
             any(s.get("table", {}).get("headers") == ["A", "B"] for s in secs)),
            ("link URL survived",
             any("docs.google.com/x" in (s.get("body") or "") for s in secs)),
        ]
        for name, passed in checks:
            print(f"   {'PASS' if passed else 'FAIL'}: {name}")
            ok &= passed
        print("\nRESULT:", "PASS" if ok else "FAIL")
        return 0 if ok else 1

    if not args.path:
        ap.error("path required (or use --selftest)")
    md = Path(args.path).read_text(encoding="utf-8")
    sections = parse(md)
    title = args.title or next((s["heading"] for s in sections if s.get("level") == 1), "On-Page Audit")
    sections = [s for s in sections if not (s.get("heading") == title and s.get("level") == 1)]

    payload = {"title": title, "sections": sections}
    if args.dry_run:
        print(json.dumps(payload, indent=1)[:3000])
        print(f"\n[{len(sections)} sections, "
              f"{sum(1 for s in sections if 'table' in s)} table(s), "
              f"{sum(1 for s in sections if 'bullets' in s)} bullet list(s), "
              f"{sum(1 for s in sections if 'bold_bullets' in s)} label(s)]")
        return 0

    r = subprocess.run([sys.executable, str(SAVE_CONTENT)],
                       input=json.dumps(payload), text=True, encoding="utf-8",
                       capture_output=True)
    sys.stdout.write(r.stdout)
    if r.stderr:
        sys.stderr.write(r.stderr)
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())

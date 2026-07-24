#!/usr/bin/env python3
"""Publish a finished blog markdown file as a formatted Google Doc.

Thin wrapper: parses a blog .md into the section payload that content-engine's
save_content.py expects, then shells to it (it owns the gws/Docs plumbing and
smart-quote normalization). The first H1 (# ...) becomes the doc title.

Usage:
    python publish.py path/to/blog.md
    python publish.py path/to/blog.md --title "Custom Doc Title"

Output (stdout): {"status":"ok","doc_url":"https://docs.google.com/..."}
Markdown supported: #/##/### headings, paragraphs, -/* bullets, and pipe tables.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SAVE_CONTENT = REPO_ROOT / ".claude" / "skills" / "content-engine" / "scripts" / "save_content.py"


def parse_markdown(md: str):
    """Flat list of save_content sections. First H1 is returned as the title."""
    lines = md.replace("\r\n", "\n").split("\n")
    title = None
    sections = []
    i = 0
    para = []

    def flush_para():
        nonlocal para
        text = " ".join(l.strip() for l in para).strip()
        if text:
            sections.append({"body": text})
        para = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # heading
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            flush_para()
            level = len(m.group(1))
            text = m.group(2).strip()
            if level == 1 and title is None:
                title = text  # H1 -> doc title, not a body heading
            else:
                sections.append({"heading": text, "level": min(level - 1 if level > 1 else 1, 3)})
            i += 1
            continue

        # pipe table (header row + separator row of ---)
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?[\s:|-]+\|?\s*$", lines[i + 1]) and "-" in lines[i + 1]:
            flush_para()
            headers = [c.strip() for c in stripped.strip("|").split("|")]
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            sections.append({"table": {"headers": headers, "rows": rows}})
            i = j
            continue

        # bullets
        if re.match(r"^\s*[-*]\s+", line):
            flush_para()
            bullets = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                bullets.append(re.sub(r"^\s*[-*]\s+", "", lines[i]).strip())
                i += 1
            sections.append({"bullets": bullets})
            continue

        # blank line -> paragraph break
        if not stripped:
            flush_para()
            i += 1
            continue

        para.append(line)
        i += 1

    flush_para()
    return title, sections


def strip_inline_md(sections):
    """Docs body is plain text; drop **bold**/*italic*/`code` markers and [text](url) -> text."""
    def clean(s):
        s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)   # links
        s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)          # bold
        s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", s) # italic
        s = re.sub(r"`([^`]+)`", r"\1", s)                # inline code
        return s
    for sec in sections:
        if "body" in sec:
            sec["body"] = clean(sec["body"])
        if "heading" in sec:
            sec["heading"] = clean(sec["heading"])
        if "bullets" in sec:
            sec["bullets"] = [clean(b) for b in sec["bullets"]]
        if "table" in sec:
            sec["table"]["headers"] = [clean(h) for h in sec["table"]["headers"]]
            sec["table"]["rows"] = [[clean(c) for c in r] for r in sec["table"]["rows"]]
    return sections


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md_path")
    ap.add_argument("--title", default=None)
    args = ap.parse_args()

    md = Path(args.md_path).read_text(encoding="utf-8")
    title, sections = parse_markdown(md)
    title = args.title or title or Path(args.md_path).stem
    sections = strip_inline_md(sections)
    if not sections:
        print(json.dumps({"status": "error", "message": "no content parsed from markdown"}))
        sys.exit(1)

    payload = json.dumps({"title": title, "sections": sections})
    result = subprocess.run(
        [sys.executable, str(SAVE_CONTENT)],
        input=payload, capture_output=True, text=True, encoding="utf-8",
    )
    sys.stdout.write(result.stdout)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()

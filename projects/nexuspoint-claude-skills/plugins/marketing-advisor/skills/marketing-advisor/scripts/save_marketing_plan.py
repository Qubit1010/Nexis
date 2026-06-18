#!/usr/bin/env python3
"""Save a marketing plan as a local Markdown file.

Reads a plan JSON from stdin and writes a formatted Markdown document
(headings, body text, bullets, tables) to disk. No external accounts or
auth required - it just writes a file you can read, commit, or convert to
PDF/Docs however you like.

Usage:
    echo '{"title":"...","sections":[...]}' | python save_marketing_plan.py
    cat plan.json | python save_marketing_plan.py
    cat plan.json | python save_marketing_plan.py --out ./my-plan.md

Output (stdout):
    {"status": "ok", "path": "C:/.../linkedin-content-system.md"}

JSON structure (per section, any combination of):
    { "heading": "Title", "level": 1, "body": "paragraph",
      "bullets": ["a", "b"],
      "bold_bullets": [{"label": "Lead: ", "text": "rest"}, "all bold"],
      "table": { "headers": ["A", "B"], "rows": [["1", "2"]] } }
"""

import json
import re
import sys
from datetime import date
from pathlib import Path


def error_exit(message):
    print(json.dumps({"status": "error", "message": message}))
    sys.exit(1)


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "marketing-plan"


def render_table(table):
    headers = table.get("headers", [])
    rows = table.get("rows", [])
    if not headers:
        return ""
    lines = ["| " + " | ".join(headers) + " |",
             "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        cells = [str(c) for c in row] + [""] * (len(headers) - len(row))
        lines.append("| " + " | ".join(cells[:len(headers)]) + " |")
    return "\n".join(lines)


def render_section(section):
    out = []
    heading = section.get("heading", "")
    level = int(section.get("level", 1))
    if heading:
        out.append("#" * max(1, min(level, 6)) + " " + heading)
        out.append("")

    body = section.get("body", "")
    if body:
        out.append(body)
        out.append("")

    for bullet in section.get("bullets", []):
        out.append(f"- {bullet}")
    if section.get("bullets"):
        out.append("")

    for bullet in section.get("bold_bullets", []):
        if isinstance(bullet, dict):
            label = bullet.get("label", "")
            rest = bullet.get("text", "")
            out.append(f"- **{label.strip()}** {rest}".rstrip())
        else:
            out.append(f"- **{bullet}**")
    if section.get("bold_bullets"):
        out.append("")

    table = section.get("table")
    if table:
        rendered = render_table(table)
        if rendered:
            out.append(rendered)
            out.append("")

    return "\n".join(out)


def validate_plan(plan):
    if not isinstance(plan, dict):
        error_exit("Input must be a JSON object")
    if "title" not in plan:
        error_exit("Missing required field: 'title'")
    if "sections" not in plan or not plan["sections"]:
        error_exit("Missing or empty 'sections' array")
    for i, section in enumerate(plan["sections"]):
        if not isinstance(section, dict):
            error_exit(f"Section {i} must be a JSON object")
        if not any(k in section for k in ["heading", "body", "bullets", "bold_bullets", "table"]):
            error_exit(f"Section {i} has no content")


def main():
    out_path = None
    args = sys.argv[1:]
    if "--out" in args:
        i = args.index("--out")
        try:
            out_path = Path(args[i + 1])
        except IndexError:
            error_exit("--out requires a path argument")

    try:
        # utf-8-sig strips a leading BOM if present (PowerShell pipes add one).
        sys.stdin.reconfigure(encoding="utf-8-sig", errors="replace")
        raw = sys.stdin.read()
        if not raw.strip():
            error_exit("No input received on stdin. Pipe plan JSON to this script.")
        plan = json.loads(raw.lstrip("﻿"))
    except json.JSONDecodeError as e:
        error_exit(f"Invalid JSON input: {e}")

    validate_plan(plan)

    title = plan["title"]
    parts = [f"# {title}", "", f"_Generated {date.today().isoformat()}_", ""]
    for section in plan["sections"]:
        parts.append(render_section(section))

    document = "\n".join(parts).rstrip() + "\n"

    if out_path is None:
        out_path = Path.cwd() / f"{slugify(title)}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(document, encoding="utf-8")

    print(json.dumps({"status": "ok", "path": str(out_path.resolve())}))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Extract plain text from a Google Doc (proposal or discovery note) for downstream parsing.

Usage:
    python extract_proposal.py <doc_id_or_url>

Output (stdout, JSON):
    {"status": "ok", "doc_id": "...", "title": "...", "text": "...full plain text..."}
    {"status": "error", "message": "..."}

The skill itself parses the returned text to extract client fields. Keeping extraction
dumb (just text) lets the model handle messy proposal formats without hard-coded rules.
"""

import json
import re
import sys

from _gws import run_gws


def normalize_doc_id(raw):
    """Accept either a raw ID or a docs.google.com URL."""
    raw = raw.strip()
    m = re.search(r"/document/d/([a-zA-Z0-9_-]+)", raw)
    if m:
        return m.group(1)
    return raw


def doc_to_text(doc):
    """Walk a Google Docs API document and concatenate visible text."""
    parts = []
    for element in doc.get("body", {}).get("content", []):
        if "paragraph" in element:
            for run in element["paragraph"].get("elements", []):
                tr = run.get("textRun")
                if tr:
                    parts.append(tr.get("content", ""))
        elif "table" in element:
            for row in element["table"].get("tableRows", []):
                row_cells = []
                for cell in row.get("tableCells", []):
                    cell_text = []
                    for cell_el in cell.get("content", []):
                        if "paragraph" in cell_el:
                            for run in cell_el["paragraph"].get("elements", []):
                                tr = run.get("textRun")
                                if tr:
                                    cell_text.append(tr.get("content", "").strip())
                    row_cells.append(" ".join(t for t in cell_text if t))
                parts.append(" | ".join(row_cells) + "\n")
    return "".join(parts)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "Usage: extract_proposal.py <doc_id_or_url>"}))
        sys.exit(1)

    doc_id = normalize_doc_id(sys.argv[1])

    try:
        doc = run_gws([
            "docs", "documents", "get",
            "--params", json.dumps({"documentId": doc_id}),
        ])
    except RuntimeError as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)

    title = doc.get("title", "")
    text = doc_to_text(doc)

    print(json.dumps({
        "status": "ok",
        "doc_id": doc_id,
        "title": title,
        "text": text,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

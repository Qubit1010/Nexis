"""
Publishes a podcast-repurposer output .md as a formatted Google Doc.

Fixes the problems plain `pandoc md -> docx -> gws upload` produces:
  - The compact "**Client:** X  ·  **Method:** Y" header line splits into its
    own bold-labeled paragraph per field (blank line between), instead of
    pandoc rendering the "  ·  " join as a cramped in-paragraph line break.
  - Every consecutive run of "**Label:** value" lines with no blank line
    between them (Pillar / Why this segment / Transcript excerpt, and the
    Segment metadata block) gets a blank line inserted before each one, so
    every field renders as its own spaced paragraph instead of running
    together on one line.
  - Every H2 ("## Segment N ...") starts on a fresh page via a raw OOXML
    page-break, inserted before pandoc converts to docx.

Usage:
  python md_to_gdoc.py path/to/05-hybrid.md
  python md_to_gdoc.py path/to/05-hybrid.md --update <driveFileId>   # overwrite an existing Doc instead of creating a new one

Requires: pandoc on PATH, gws authenticated (gws auth login).
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
GDOC_MIME = "application/vnd.google-apps.document"

PAGE_BREAK = ['```{=openxml}', '<w:p><w:r><w:br w:type="page"/></w:r></w:p>', '```']

# content-engine's Docs-API tab builder (reused unchanged for the --tabs path)
SAVE_CONTENT = REPO_ROOT / ".claude" / "skills" / "content-engine" / "scripts" / "save_content.py"


def sanitize(text: str) -> str:
    """Em/en dashes corrupt through the pandoc->docx->Drive-convert pipeline; plain hyphens don't."""
    return text.replace("—", "-").replace("–", "-")


def split_header_fields(text: str) -> str:
    """'**Client:** X  ·  **Method:** Y' on one line -> two blank-line-separated paragraphs."""
    out = []
    pattern = re.compile(r"^(\*\*[^:*]+:\*\* .+?)  ·  (\*\*[^:*]+:\*\* .+)$")
    for line in text.splitlines():
        m = pattern.match(line)
        if m:
            out.append(m.group(1))
            out.append("")
            out.append(m.group(2))
        else:
            out.append(line)
    return "\n".join(out)


def space_out_bold_labels(text: str) -> str:
    """A '**Label:** value' line directly following another non-blank line
    (no blank line between) gets a blank line inserted before it, so each
    labeled field becomes its own paragraph."""
    label_re = re.compile(r"^\*\*[^*:]+:\*\*")
    out = []
    prev_blank = True
    for line in text.splitlines():
        if label_re.match(line) and not prev_blank:
            out.append("")
        out.append(line)
        prev_blank = (line.strip() == "")
    return "\n".join(out)


def insert_page_breaks(text: str) -> str:
    """Every H2 heading starts on a new page."""
    out = []
    for line in text.splitlines():
        if line.startswith("## "):
            out.extend(PAGE_BREAK)
            out.append("")
        out.append(line)
    return "\n".join(out)


def build_doc_title(text: str, fallback: str) -> str:
    m = re.search(r"^# (.+)$", text, re.MULTILINE)
    if not m:
        return fallback
    title = re.sub(r"\*\*(.+?)\*\*", r"\1", m.group(1)).strip()
    return re.sub(r"\s+·\s+Candidate.*$", "", title) or title


def run(cmd: list, **kw) -> subprocess.CompletedProcess:
    # shell=True: gws/pandoc resolve through npm .cmd shims on Windows, which
    # bare CreateProcess (shell=False) can't locate without the .cmd suffix.
    result = subprocess.run(subprocess.list2cmdline(cmd), cwd=str(REPO_ROOT),
                             capture_output=True, text=True, shell=True, **kw)
    if result.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)}\n{result.stdout}\n{result.stderr}")
    return result


def publish(md_path: Path, update_id: str = None) -> str:
    text = md_path.read_text(encoding="utf-8")
    text = sanitize(text)
    text = split_header_fields(text)
    text = space_out_bold_labels(text)
    text = insert_page_breaks(text)

    tmp_md = md_path.with_name(md_path.stem + "-gdoc-tmp.md")
    tmp_docx = md_path.with_name(md_path.stem + "-gdoc-tmp.docx")
    tmp_md.write_text(text, encoding="utf-8")

    try:
        run(["pandoc", str(tmp_md.relative_to(REPO_ROOT)),
             "-o", str(tmp_docx.relative_to(REPO_ROOT)), "--standalone"])

        title = build_doc_title(text, md_path.stem)
        docx_rel = str(tmp_docx.relative_to(REPO_ROOT))

        if update_id:
            result = run(["gws", "drive", "files", "update",
                          "--params", json.dumps({"fileId": update_id}),
                          "--upload", docx_rel, "--upload-content-type", DOCX_MIME])
        else:
            result = run(["gws", "drive", "files", "create",
                          "--json", json.dumps({"name": title, "mimeType": GDOC_MIME}),
                          "--upload", docx_rel, "--upload-content-type", DOCX_MIME])

        file_id = json.loads(result.stdout)["id"]
        return f"https://docs.google.com/document/d/{file_id}/edit"
    finally:
        tmp_md.unlink(missing_ok=True)
        tmp_docx.unlink(missing_ok=True)


# ---- Tabbed export: one tab per segment + a Report tab, via save_content.py ----

BOLD_KV = re.compile(r"^\*\*([^*:]+):\*\*\s*(.*)$")


def strip_inline(s: str) -> str:
    """Drop markdown bold markers so text doesn't render literal ** in the Doc."""
    return s.replace("**", "").strip()


def parse_kv_line(line: str) -> list:
    """'**Client:** X  ·  **Method:** Y' -> [{'label':'Client: ','text':'X'}, ...]."""
    out = []
    for part in re.split(r"\s+·\s+", line.strip()):
        m = BOLD_KV.match(part.strip())
        if m:
            out.append({"label": m.group(1).strip() + ": ", "text": strip_inline(m.group(2))})
    return out


def parse_table(tbl_lines: list):
    rows = []
    for ln in tbl_lines:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if cells and all(re.match(r"^:?-+:?$", c) for c in cells if c != ""):
            continue  # markdown separator row (|---|---|)
        rows.append([strip_inline(c) for c in cells])
    if len(rows) < 1:
        return None
    return {"headers": rows[0], "rows": rows[1:]}


def block_to_sections(block_lines: list, include_heading: bool = True) -> list:
    """Map one '## ...' block of the fixed output-spec md into save_content.py sections."""
    sections = []
    lines = block_lines
    i = 0
    if include_heading and lines and lines[0].startswith("## "):
        sections.append({"heading": lines[0][3:].strip(), "level": 2})
        i = 1
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if s == "" or s == "---":
            i += 1
            continue
        if ln.startswith("### "):
            sections.append({"heading": ln[4:].strip(), "level": 3})
            i += 1
            continue
        if s.startswith("|"):
            tbl = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl.append(lines[i])
                i += 1
            parsed = parse_table(tbl)
            if parsed:
                sections.append({"table": parsed})
            continue
        m = BOLD_KV.match(ln)
        if m and m.group(2).strip():        # **Label:** value  -> bold-label bullet(s)
            group = []
            while i < len(lines):
                mm = BOLD_KV.match(lines[i])
                if mm and mm.group(2).strip():
                    group.append({"label": mm.group(1).strip() + ": ", "text": strip_inline(mm.group(2))})
                    i += 1
                else:
                    break
            sections.append({"bold_bullets": group})
            continue
        if m:                                # **Label:**  (no value) -> bold header line
            sections.append({"bold_bullets": [{"label": m.group(1).strip() + ":", "text": ""}]})
            i += 1
            continue
        buf = []                             # plain prose -> one body block (keeps paragraph breaks)
        while i < len(lines):
            cur = lines[i]
            cs = cur.strip()
            if cur.startswith("### ") or cur.startswith("## ") or cs.startswith("|") or BOLD_KV.match(cur):
                break
            if cs == "---":
                i += 1
                continue
            buf.append(strip_inline(cur.lstrip("> ").rstrip()) if cs else "")
            i += 1
        body = "\n".join(buf).strip("\n")
        if body.strip():
            sections.append({"body": body})
    return sections


def split_blocks(text: str):
    lines = text.splitlines()
    idxs = [k for k, l in enumerate(lines) if l.startswith("## ")]
    if not idxs:
        return lines, []
    header = lines[:idxs[0]]
    blocks = [lines[idxs[j]:(idxs[j + 1] if j + 1 < len(idxs) else len(lines))] for j in range(len(idxs))]
    return header, blocks


def header_sections(header_lines: list) -> list:
    secs, meta, note = [], [], []
    for ln in header_lines:
        s = ln.strip()
        if s.startswith("# ") or s == "" or s == "---":
            continue                         # doc title / blanks / rules
        if s.startswith(">"):
            note.append(strip_inline(s.lstrip("> ").rstrip()) if s.strip("> ").strip() else "")
            continue
        if BOLD_KV.match(ln):
            meta.extend(parse_kv_line(ln))
            continue
        note.append(strip_inline(ln))
    if meta:
        secs.append({"bold_bullets": meta})
    note_body = "\n".join(note).strip("\n")
    if note_body.strip():
        secs.append({"heading": "Selection note", "level": 3})
        secs.append({"body": note_body})
    return secs


def build_tab_payload(text: str, fallback: str) -> dict:
    """One Report tab (header note + ranking + QA) then one tab per segment."""
    text = sanitize(text)
    header, blocks = split_blocks(text)
    seg_re = re.compile(r"^##\s+Segment\s+\d+", re.I)
    seg_blocks = [b for b in blocks if seg_re.match(b[0])]
    other_blocks = [b for b in blocks if not seg_re.match(b[0])]

    report = header_sections(header)
    for b in other_blocks:
        report += block_to_sections(b)
    if not report:
        report = [{"body": "(no report content)"}]
    tabs = [{"title": "Report", "sections": report}]

    for b in seg_blocks:
        m = re.match(r"^##\s+(Segment\s+\d+)", b[0], re.I)
        tabs.append({"title": m.group(1) if m else b[0][3:].strip()[:40],
                     "sections": block_to_sections(b)})

    title = build_doc_title(text, fallback)
    title = re.split(r"\s+[-·]\s+Candidate", title)[0].strip().replace("&", "and")
    return {"title": title or fallback, "tabs": tabs}


def publish_tabs(md_path: Path) -> str:
    payload = build_tab_payload(md_path.read_text(encoding="utf-8"), md_path.stem)
    proc = subprocess.run([sys.executable, str(SAVE_CONTENT)],
                          input=json.dumps(payload), cwd=str(REPO_ROOT),
                          capture_output=True, text=True, encoding="utf-8")
    out = (proc.stdout or "").strip()
    if proc.returncode != 0:
        raise RuntimeError(f"save_content.py failed:\n{out}\n{proc.stderr}")
    try:
        result = json.loads(out)
    except json.JSONDecodeError:
        jsons = [l for l in out.splitlines() if l.strip().startswith("{")]
        if not jsons:
            raise RuntimeError(f"save_content.py gave no JSON:\n{out}\n{proc.stderr}")
        result = json.loads(jsons[-1])
    if result.get("status") == "error":
        raise RuntimeError(f"save_content.py error: {result}")
    return result["doc_url"]


SELFTEST_MD = '''# Sample Episode - Candidate Set 05: Hybrid (recommended)
**Client:** Test  ·  **Method:** Hybrid
**Episode:** sample  ·  **Generated:** 2026-07-21

> How the segments were chosen.
>
> Second paragraph of the note.

---

## Segment Ranking

| Rank | Segment | Complete | Resonate | Conviction | Concise | Total | Ship? | Note |
|------|---------|----------|----------|-----------|---------|-------|-------|------|
| 1 | "A" · 00:00-00:30 | 5 | 5 | 5 | 4 | 19 | Yes | strong |
| 2 | "B" · 01:00-01:40 | 4 | 4 | 4 | 4 | 16 | Yes | good |

---

## Segment 1 - "A"  ·  00:00-00:30 (~30s)
**Pillar:** Feel Secure
**Why this segment:** It lands.
**Transcript excerpt:** "quote"

### Text hooks (5) - 6-12 words
1. hook one (recommended)
2. hook two (2nd option)

**Self-scores:** 5, 5 - clear.

### Captions (3) - 80-150 words
**A (Instagram - save-bait):**
Line one.

Line two.

**Segment metadata:**
**Pillar:** Feel Secure
**Trigger:** loss aversion

---

## Segment 2 - "B"  ·  01:00-01:40 (~40s)
**Pillar:** Belong Fully
**Why this segment:** It connects.

### Text hooks (5) - 6-12 words
1. hook (recommended)

---

## QA Summary
- [x] Checks pass
**Pillar coverage:** Feel Secure, Belong Fully
'''


def selftest():
    payload = build_tab_payload(SELFTEST_MD, "sample")
    titles = [t["title"] for t in payload["tabs"]]
    assert titles[0] == "Report", titles
    assert titles[1:] == ["Segment 1", "Segment 2"], titles
    assert payload["title"] == "Sample Episode", payload["title"]
    report = payload["tabs"][0]["sections"]
    assert any("table" in s for s in report), "report tab missing ranking table"
    assert any(s.get("heading") == "QA Summary" for s in report), "report tab missing QA"
    for t in payload["tabs"][1:]:
        assert t["sections"], f"empty segment tab {t['title']}"
        assert t["sections"][0].get("heading", "").startswith("Segment "), t["sections"][0]
    for t in payload["tabs"]:              # every section must be valid for save_content.py
        for s in t["sections"]:
            assert any(k in s for k in ("heading", "body", "bullets", "bold_bullets", "table")), s
    print("selftest passed:", len(payload["tabs"]), "tabs ->", titles)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md_file", nargs="?")
    ap.add_argument("--update", metavar="DRIVE_FILE_ID", help="overwrite an existing Google Doc instead of creating a new one")
    ap.add_argument("--tabs", action="store_true", help="one tab per segment + a Report tab (via content-engine save_content.py) instead of a flat page-break doc")
    ap.add_argument("--selftest", action="store_true", help="parse a built-in sample and check the tab payload, offline")
    args = ap.parse_args()

    if args.selftest:
        selftest()
        return

    if not args.md_file:
        ap.error("md_file is required (or pass --selftest)")
    md_path = Path(args.md_file).resolve()
    if not md_path.is_file():
        print(f"Not found: {md_path}")
        sys.exit(1)

    print(publish_tabs(md_path) if args.tabs else publish(md_path, update_id=args.update))


if __name__ == "__main__":
    main()

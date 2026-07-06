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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md_file")
    ap.add_argument("--update", metavar="DRIVE_FILE_ID", help="overwrite an existing Google Doc instead of creating a new one")
    args = ap.parse_args()

    md_path = Path(args.md_file).resolve()
    if not md_path.is_file():
        print(f"Not found: {md_path}")
        sys.exit(1)

    url = publish(md_path, update_id=args.update)
    print(url)


if __name__ == "__main__":
    main()

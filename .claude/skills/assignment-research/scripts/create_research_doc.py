#!/usr/bin/env python3
"""Create a formatted Google Doc with research notes via gws CLI.

Reads research JSON from stdin, creates a Google Doc with proper formatting
(headings, body text, bullets, tables), and saves it to the University Research Notes
folder in Google Drive.

Usage:
    echo '{"title":"...","sections":[...]}' | python create_research_doc.py
    cat research.json | python create_research_doc.py

Output (stdout):
    {"status": "ok", "doc_url": "https://docs.google.com/...", "doc_id": "..."}
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
FOLDER_CACHE = SKILL_DIR / ".folder_id"
DRIVE_FOLDER_NAME = "University Research Notes"


def find_gws():
    """Find gws and return (cmd_list, use_shell).

    On Windows, prefer calling node + run-gws.js directly to bypass
    the cmd.exe 8191-char command line limit. Falls back to gws.cmd with shell.
    """
    npm_dir = Path(os.environ.get("APPDATA", "")) / "npm"
    gws_js = npm_dir / "node_modules" / "@googleworkspace" / "cli" / "run-gws.js"

    if gws_js.exists():
        # Find node.exe
        node_exe = None
        for candidate in [
            npm_dir / "node.exe",
            Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "nodejs" / "node.exe",
            Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "nodejs" / "node.exe",
        ]:
            if candidate.exists():
                node_exe = str(candidate)
                break
        if not node_exe:
            node_exe = shutil.which("node")
        if node_exe:
            # Direct node invocation — no shell needed, 32K arg limit via CreateProcess
            return ([node_exe, str(gws_js)], False)

    # Fallback: use gws.cmd through shell
    gws_path = shutil.which("gws")
    if gws_path:
        return ([gws_path], True)
    gws_cmd = npm_dir / "gws.cmd"
    if gws_cmd.exists():
        return ([str(gws_cmd)], True)
    return (["gws"], True)


def error_exit(message):
    """Print error JSON and exit."""
    print(json.dumps({"status": "error", "message": message}))
    sys.exit(1)


GWS_CMD, GWS_USE_SHELL = find_gws()


def run_gws(args, json_body=None):
    """Run a gws CLI command and return parsed JSON output.

    Uses direct node invocation (no shell) when available, which bypasses
    the Windows cmd.exe 8191-char command line limit (CreateProcess allows 32K).
    """
    cmd = GWS_CMD + args
    if json_body is not None:
        cmd += ["--json", json.dumps(json_body)]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120,
                            shell=GWS_USE_SHELL,
                            encoding="utf-8", errors="replace")
    if result.returncode != 0:
        stderr = result.stderr.strip() if result.stderr else "Unknown error"
        raise RuntimeError(f"gws command failed: {' '.join(args[:3])}... | {stderr}")

    stdout = result.stdout.strip()
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"raw": stdout}


def find_or_create_folder():
    """Find or create the University Research Notes folder in Google Drive."""
    # Check cache first
    if FOLDER_CACHE.exists():
        cached_id = FOLDER_CACHE.read_text().strip()
        if cached_id:
            # Verify folder still exists
            try:
                result = run_gws([
                    "drive", "files", "list",
                    "--params", json.dumps({
                        "q": f"name='{DRIVE_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                        "fields": "files(id,name)"
                    })
                ])
                files = result.get("files", [])
                for f in files:
                    if f.get("id") == cached_id:
                        return cached_id
            except RuntimeError:
                pass

    # Search for existing folder
    try:
        result = run_gws([
            "drive", "files", "list",
            "--params", json.dumps({
                "q": f"name='{DRIVE_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                "fields": "files(id,name)"
            })
        ])
        files = result.get("files", [])
        if files:
            folder_id = files[0]["id"]
            FOLDER_CACHE.write_text(folder_id)
            return folder_id
    except RuntimeError:
        pass

    # Create new folder
    result = run_gws(
        ["drive", "files", "create"],
        json_body={"name": DRIVE_FOLDER_NAME, "mimeType": "application/vnd.google-apps.folder"}
    )
    folder_id = result.get("id")
    if not folder_id:
        error_exit(f"Failed to create Drive folder. Response: {result}")
    FOLDER_CACHE.write_text(folder_id)
    return folder_id


def create_doc(title, folder_id):
    """Create a blank Google Doc and move it to the research notes folder."""
    # Create the doc
    result = run_gws(
        ["docs", "documents", "create"],
        json_body={"title": title}
    )
    doc_id = result.get("documentId")
    if not doc_id:
        error_exit(f"Failed to create document. Response: {result}")

    # Move to research notes folder
    try:
        run_gws([
            "drive", "files", "update",
            "--params", json.dumps({
                "fileId": doc_id,
                "addParents": folder_id
            }),
            "--json", "{}"
        ])
    except RuntimeError as e:
        print(f"Warning: Could not move doc to folder: {e}", file=sys.stderr)

    return doc_id


def latex_to_url(latex):
    """Convert a LaTeX expression to a CodeCogs PNG image URL."""
    encoded = quote(latex)
    return f"https://latex.codecogs.com/png.image?\\dpi{{150}}{encoded}"


def split_text_segments(text):
    """Split text on $$...$$ equation markers.

    Returns list of (type, content) tuples: 'text' or 'equation'.
    """
    segments = []
    last_end = 0
    for m in re.finditer(r'\$\$(.+?)\$\$', text):
        if m.start() > last_end:
            segments.append(("text", text[last_end:m.start()]))
        segments.append(("equation", m.group(1)))
        last_end = m.end()
    if last_end < len(text):
        segments.append(("text", text[last_end:]))
    return segments if segments else [("text", text)]


def parse_bold_markers(text):
    """Parse **bold** markers from text.

    Returns (plain_text, bold_ranges) where bold_ranges is a list of
    (start, end) tuples relative to the plain text.
    """
    bold_ranges = []
    plain = ""
    last_end = 0
    for m in re.finditer(r'\*\*(.+?)\*\*', text):
        plain += text[last_end:m.start()]
        bold_start = len(plain)
        plain += m.group(1)
        bold_ranges.append((bold_start, len(plain)))
        last_end = m.end()
    plain += text[last_end:]
    return plain, bold_ranges


def insert_formatted_content(requests, idx, raw_text):
    """Insert text with inline $$LaTeX$$ equations and **bold** markers.

    Processes text segments in order, inserting plain text and inline equation
    images. Returns (new_idx, bold_ranges_absolute) where bold_ranges_absolute
    contains (start, end) tuples for bold formatting.
    """
    segments = split_text_segments(raw_text)
    bold_ranges_abs = []

    for seg_type, content in segments:
        if seg_type == "text":
            plain, bolds = parse_bold_markers(content)
            if plain:
                requests.append({
                    "insertText": {
                        "location": {"index": idx},
                        "text": plain
                    }
                })
                for bs, be in bolds:
                    bold_ranges_abs.append((idx + bs, idx + be))
                idx += len(plain)
        elif seg_type == "equation":
            url = latex_to_url(content)
            requests.append({
                "insertInlineImage": {
                    "location": {"index": idx},
                    "uri": url,
                    "objectSize": {
                        "height": {"magnitude": 18, "unit": "PT"},
                        "width": {"magnitude": max(40, len(content) * 4), "unit": "PT"}
                    }
                }
            })
            idx += 1  # Inline image occupies 1 index position

    return idx, bold_ranges_abs


def build_text_requests(sections):
    """Build batchUpdate requests for all text content with local index tracking.

    Supports **bold** markers and $$LaTeX$$ equations in body text and bullets.

    Returns (requests_list, table_locations) where table_locations is a list of
    (insert_index, table_data) tuples for second-pass table insertion.
    """
    requests = []
    table_locations = []
    idx = 1  # Google Docs body starts at index 1

    for section in sections:
        heading = section.get("heading", "")
        level = section.get("level", 1)
        body = section.get("body", "")
        bullets = section.get("bullets", [])
        table = section.get("table")

        # Insert heading (no inline formatting in headings)
        if heading:
            heading_text = heading + "\n"
            requests.append({
                "insertText": {
                    "location": {"index": idx},
                    "text": heading_text
                }
            })
            style_map = {1: "HEADING_1", 2: "HEADING_2", 3: "HEADING_3"}
            named_style = style_map.get(level, "HEADING_1")
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": idx, "endIndex": idx + len(heading_text)},
                    "paragraphStyle": {"namedStyleType": named_style},
                    "fields": "namedStyleType"
                }
            })
            idx += len(heading_text)

        # Insert body text (with bold + equation support)
        if body:
            body_start = idx
            idx, bold_ranges = insert_formatted_content(requests, idx, body)
            # Add newline
            requests.append({
                "insertText": {
                    "location": {"index": idx},
                    "text": "\n"
                }
            })
            idx += 1
            # Paragraph style
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": body_start, "endIndex": idx},
                    "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                    "fields": "namedStyleType"
                }
            })
            # Bold ranges
            for bs, be in bold_ranges:
                requests.append({
                    "updateTextStyle": {
                        "range": {"startIndex": bs, "endIndex": be},
                        "textStyle": {"bold": True},
                        "fields": "bold"
                    }
                })

        # Insert bullets (with bold + equation support)
        if bullets:
            for bullet in bullets:
                bullet_start = idx
                idx, bold_ranges = insert_formatted_content(requests, idx, bullet)
                # Add newline
                requests.append({
                    "insertText": {
                        "location": {"index": idx},
                        "text": "\n"
                    }
                })
                idx += 1
                # Paragraph style + bullet
                requests.append({
                    "updateParagraphStyle": {
                        "range": {"startIndex": bullet_start, "endIndex": idx},
                        "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                        "fields": "namedStyleType"
                    }
                })
                requests.append({
                    "createParagraphBullets": {
                        "range": {"startIndex": bullet_start, "endIndex": idx},
                        "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
                    }
                })
                # Bold ranges
                for bs, be in bold_ranges:
                    requests.append({
                        "updateTextStyle": {
                            "range": {"startIndex": bs, "endIndex": be},
                            "textStyle": {"bold": True},
                            "fields": "bold"
                        }
                    })

        # Record table location for second pass
        if table:
            table_locations.append((idx, table))
            requests.append({
                "insertText": {
                    "location": {"index": idx},
                    "text": "\n"
                }
            })
            idx += 1

        # Add spacing between sections
        requests.append({
            "insertText": {
                "location": {"index": idx},
                "text": "\n"
            }
        })
        idx += 1

    return requests, table_locations


def insert_tables(doc_id, table_locations):
    """Second pass: insert and populate tables.

    For each table, we insert the table structure, read the doc to get cell
    indices, then populate cells.
    """
    if not table_locations:
        return

    # Process tables in reverse order to avoid index shifting
    for insert_idx, table_data in reversed(table_locations):
        headers = table_data.get("headers", [])
        rows = table_data.get("rows", [])

        if not headers:
            continue

        num_rows = len(rows) + 1  # +1 for header row
        num_cols = len(headers)

        # Insert empty table
        try:
            run_gws(
                ["docs", "documents", "batchUpdate",
                 "--params", json.dumps({"documentId": doc_id})],
                json_body={"requests": [{
                    "insertTable": {
                        "location": {"index": insert_idx},
                        "rows": num_rows,
                        "columns": num_cols
                    }
                }]}
            )
        except RuntimeError as e:
            print(f"Warning: Failed to insert table: {e}", file=sys.stderr)
            continue

        # Read document to get table cell indices
        try:
            doc = run_gws([
                "docs", "documents", "get",
                "--params", json.dumps({"documentId": doc_id})
            ])
        except RuntimeError as e:
            print(f"Warning: Failed to read doc for table population: {e}", file=sys.stderr)
            continue

        # Find the table element near our insert index
        body_content = doc.get("body", {}).get("content", [])
        target_table = None
        for element in body_content:
            if "table" in element:
                start = element.get("startIndex", 0)
                # Find the table closest to our insert index
                if start >= insert_idx - 2:
                    target_table = element["table"]
                    break

        if not target_table:
            print(f"Warning: Could not find inserted table near index {insert_idx}", file=sys.stderr)
            continue

        # Build cell population requests
        cell_requests = []
        table_rows = target_table.get("tableRows", [])

        for row_idx, table_row in enumerate(table_rows):
            cells = table_row.get("tableCells", [])
            for col_idx, cell in enumerate(cells):
                # Get the cell's content start index
                cell_content = cell.get("content", [])
                if not cell_content:
                    continue
                cell_start = cell_content[0].get("startIndex", 0)

                # Determine text to insert
                if row_idx == 0:
                    # Header row
                    if col_idx < len(headers):
                        text = headers[col_idx]
                    else:
                        continue
                else:
                    # Data row
                    data_row_idx = row_idx - 1
                    if data_row_idx < len(rows) and col_idx < len(rows[data_row_idx]):
                        text = rows[data_row_idx][col_idx]
                    else:
                        continue

                if text:
                    cell_requests.append({
                        "insertText": {
                            "location": {"index": cell_start},
                            "text": text
                        }
                    })

                    # Bold header row
                    if row_idx == 0:
                        cell_requests.append({
                            "updateTextStyle": {
                                "range": {
                                    "startIndex": cell_start,
                                    "endIndex": cell_start + len(text)
                                },
                                "textStyle": {"bold": True},
                                "fields": "bold"
                            }
                        })

        if cell_requests:
            # Sort by index descending to avoid shift issues
            cell_requests.sort(
                key=lambda r: (
                    r.get("insertText", r.get("updateTextStyle", {}))
                    .get("location", r.get("insertText", r.get("updateTextStyle", {})).get("range", {}))
                    .get("index", r.get("insertText", r.get("updateTextStyle", {})).get("range", {}).get("startIndex", 0))
                ),
                reverse=True
            )
            try:
                run_gws(
                    ["docs", "documents", "batchUpdate",
                     "--params", json.dumps({"documentId": doc_id})],
                    json_body={"requests": cell_requests}
                )
            except RuntimeError as e:
                print(f"Warning: Failed to populate table cells: {e}", file=sys.stderr)


def validate_research(data):
    """Validate research JSON has required fields."""
    if not isinstance(data, dict):
        error_exit("Input must be a JSON object")
    if "title" not in data:
        error_exit("Missing required field: 'title'")
    if "sections" not in data or not data["sections"]:
        error_exit("Missing or empty 'sections' array")
    for i, section in enumerate(data["sections"]):
        if not isinstance(section, dict):
            error_exit(f"Section {i} must be a JSON object")
        if not any(k in section for k in ["heading", "body", "bullets", "table"]):
            error_exit(f"Section {i} has no content (needs heading, body, bullets, or table)")


def main():
    # Read JSON from stdin
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            error_exit("No input received on stdin. Pipe research JSON to this script.")
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        error_exit(f"Invalid JSON input: {e}")

    validate_research(data)

    title = data["title"]
    sections = data["sections"]

    # Find or create the research notes folder
    folder_id = find_or_create_folder()

    # Create blank document
    doc_id = create_doc(title, folder_id)

    # Build and execute text content requests (pass 1)
    # Split into batches to avoid Windows command line length limits
    text_requests, table_locations = build_text_requests(sections)
    if text_requests:
        MAX_CMD_LEN = 28000  # Stay well under 32K CreateProcess limit
        batch = []
        batch_len = 0
        base_overhead = len(json.dumps({"requests": []})) + len(json.dumps({"documentId": doc_id})) + 200

        for req in text_requests:
            req_str = json.dumps(req)
            if batch and (batch_len + len(req_str) + base_overhead > MAX_CMD_LEN):
                # Send current batch
                try:
                    run_gws(
                        ["docs", "documents", "batchUpdate",
                         "--params", json.dumps({"documentId": doc_id})],
                        json_body={"requests": batch}
                    )
                except RuntimeError as e:
                    error_exit(f"Failed to insert text content: {e}")
                batch = []
                batch_len = 0
            batch.append(req)
            batch_len += len(req_str)

        # Send remaining batch
        if batch:
            try:
                run_gws(
                    ["docs", "documents", "batchUpdate",
                     "--params", json.dumps({"documentId": doc_id})],
                    json_body={"requests": batch}
                )
            except RuntimeError as e:
                error_exit(f"Failed to insert text content: {e}")

    # Insert and populate tables (pass 2)
    if table_locations:
        insert_tables(doc_id, table_locations)

    # Output result
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(json.dumps({
        "status": "ok",
        "doc_url": doc_url,
        "doc_id": doc_id,
        "folder_id": folder_id
    }))


if __name__ == "__main__":
    main()

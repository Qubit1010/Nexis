#!/usr/bin/env python3
"""Save a marketing plan as a formatted Google Doc via gws CLI.

Reads plan JSON from stdin, creates a Google Doc with proper formatting
(headings, body text, bullets, tables), and saves it to the NexusPoint Marketing
folder in Google Drive.

Usage:
    echo '{"title":"...","sections":[...]}' | python save_marketing_plan.py
    cat plan.json | python save_marketing_plan.py

Output (stdout):
    {"status": "ok", "doc_url": "https://docs.google.com/...", "doc_id": "..."}
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
FOLDER_CACHE = SKILL_DIR / ".folder_id"
DRIVE_FOLDER_NAME = "NexusPoint Marketing"


def find_gws():
    """Find gws and return (cmd_list, use_shell).

    On Windows, prefer calling node + run-gws.js directly to bypass
    the cmd.exe 8191-char command line limit. Falls back to gws.cmd with shell.
    """
    npm_dir = Path(os.environ.get("APPDATA", "")) / "npm"
    gws_js = npm_dir / "node_modules" / "@googleworkspace" / "cli" / "run-gws.js"

    if gws_js.exists():
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
            return ([node_exe, str(gws_js)], False)

    gws_path = shutil.which("gws")
    if gws_path:
        return ([gws_path], True)
    gws_cmd = npm_dir / "gws.cmd"
    if gws_cmd.exists():
        return ([str(gws_cmd)], True)
    return (["gws"], True)


def error_exit(message):
    print(json.dumps({"status": "error", "message": message}))
    sys.exit(1)


GWS_CMD, GWS_USE_SHELL = find_gws()


def run_gws(args, json_body=None):
    cmd = GWS_CMD + args
    if json_body is not None:
        cmd += ["--json", json.dumps(json_body)]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120,
                            shell=GWS_USE_SHELL,
                            encoding="utf-8", errors="replace")
    if result.returncode != 0:
        stderr = result.stderr.strip() if result.stderr else "Unknown error"
        raise RuntimeError(f"gws command failed: {' '.join(str(a) for a in args[:3])}... | {stderr}")

    stdout = result.stdout.strip()
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"raw": stdout}


def find_or_create_folder():
    """Find or create the NexusPoint Marketing folder in Google Drive."""
    if FOLDER_CACHE.exists():
        cached_id = FOLDER_CACHE.read_text().strip()
        if cached_id:
            try:
                result = run_gws([
                    "drive", "files", "list",
                    "--params", json.dumps({
                        "q": f"name='{DRIVE_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                        "fields": "files(id,name)"
                    })
                ])
                for f in result.get("files", []):
                    if f.get("id") == cached_id:
                        return cached_id
            except RuntimeError:
                pass

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
    """Create a blank Google Doc and move it to the marketing folder."""
    result = run_gws(
        ["docs", "documents", "create"],
        json_body={"title": title}
    )
    doc_id = result.get("documentId")
    if not doc_id:
        error_exit(f"Failed to create document. Response: {result}")

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


def build_text_requests(sections):
    """Build batchUpdate requests for all text content.

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

        if body:
            body_text = body + "\n"
            requests.append({
                "insertText": {
                    "location": {"index": idx},
                    "text": body_text
                }
            })
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": idx, "endIndex": idx + len(body_text)},
                    "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                    "fields": "namedStyleType"
                }
            })
            idx += len(body_text)

        if bullets:
            for bullet in bullets:
                bullet_text = bullet + "\n"
                requests.append({
                    "insertText": {
                        "location": {"index": idx},
                        "text": bullet_text
                    }
                })
                requests.append({
                    "updateParagraphStyle": {
                        "range": {"startIndex": idx, "endIndex": idx + len(bullet_text)},
                        "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                        "fields": "namedStyleType"
                    }
                })
                requests.append({
                    "createParagraphBullets": {
                        "range": {"startIndex": idx, "endIndex": idx + len(bullet_text)},
                        "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
                    }
                })
                idx += len(bullet_text)

        # bold_bullets: each item is {"label": "bold text", "text": "normal text"}
        # or a plain string (entire bullet rendered bold)
        bold_bullets = section.get("bold_bullets", [])
        for bullet in bold_bullets:
            if isinstance(bullet, dict):
                label = bullet.get("label", "")
                rest = bullet.get("text", "")
                bullet_text = (label + rest + "\n") if rest else (label + "\n")
                label_len = len(label)
            else:
                bullet_text = str(bullet) + "\n"
                label_len = len(str(bullet))

            requests.append({
                "insertText": {
                    "location": {"index": idx},
                    "text": bullet_text
                }
            })
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": idx, "endIndex": idx + len(bullet_text)},
                    "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                    "fields": "namedStyleType"
                }
            })
            requests.append({
                "createParagraphBullets": {
                    "range": {"startIndex": idx, "endIndex": idx + len(bullet_text)},
                    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
                }
            })
            # Bold the label portion (or entire bullet if plain string)
            if label_len > 0:
                requests.append({
                    "updateTextStyle": {
                        "range": {"startIndex": idx, "endIndex": idx + label_len},
                        "textStyle": {"bold": True},
                        "fields": "bold"
                    }
                })
            idx += len(bullet_text)

        if table:
            table_locations.append((idx, table))
            placeholder = "\n"
            requests.append({
                "insertText": {
                    "location": {"index": idx},
                    "text": placeholder
                }
            })
            idx += len(placeholder)

        spacing = "\n"
        requests.append({
            "insertText": {
                "location": {"index": idx},
                "text": spacing
            }
        })
        idx += len(spacing)

    return requests, table_locations


def insert_tables(doc_id, table_locations):
    """Second pass: insert and populate tables."""
    if not table_locations:
        return

    for insert_idx, table_data in reversed(table_locations):
        headers = table_data.get("headers", [])
        rows = table_data.get("rows", [])

        if not headers:
            continue

        num_rows = len(rows) + 1
        num_cols = len(headers)

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

        try:
            doc = run_gws([
                "docs", "documents", "get",
                "--params", json.dumps({"documentId": doc_id})
            ])
        except RuntimeError as e:
            print(f"Warning: Failed to read doc for table population: {e}", file=sys.stderr)
            continue

        body_content = doc.get("body", {}).get("content", [])
        target_table = None
        for element in body_content:
            if "table" in element:
                start = element.get("startIndex", 0)
                if start >= insert_idx - 2:
                    target_table = element["table"]
                    break

        if not target_table:
            print(f"Warning: Could not find inserted table near index {insert_idx}", file=sys.stderr)
            continue

        cell_requests = []
        table_rows = target_table.get("tableRows", [])

        for row_idx, table_row in enumerate(table_rows):
            cells = table_row.get("tableCells", [])
            for col_idx, cell in enumerate(cells):
                cell_content = cell.get("content", [])
                if not cell_content:
                    continue
                cell_start = cell_content[0].get("startIndex", 0)

                if row_idx == 0:
                    if col_idx < len(headers):
                        text = headers[col_idx]
                    else:
                        continue
                else:
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
        if not any(k in section for k in ["heading", "body", "bullets", "table"]):
            error_exit(f"Section {i} has no content (needs heading, body, bullets, or table)")


def main():
    try:
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
        raw = sys.stdin.read()
        if not raw.strip():
            error_exit("No input received on stdin. Pipe plan JSON to this script.")
        plan = json.loads(raw)
    except json.JSONDecodeError as e:
        error_exit(f"Invalid JSON input: {e}")

    validate_plan(plan)

    title = plan["title"]
    sections = plan["sections"]

    folder_id = find_or_create_folder()
    doc_id = create_doc(title, folder_id)

    text_requests, table_locations = build_text_requests(sections)
    if text_requests:
        # Batch into chunks of 30 to avoid Windows command line length limits
        chunk_size = 30
        for i in range(0, len(text_requests), chunk_size):
            chunk = text_requests[i:i + chunk_size]
            try:
                run_gws(
                    ["docs", "documents", "batchUpdate",
                     "--params", json.dumps({"documentId": doc_id})],
                    json_body={"requests": chunk}
                )
            except RuntimeError as e:
                error_exit(f"Failed to insert text content (chunk {i // chunk_size + 1}): {e}")

    if table_locations:
        insert_tables(doc_id, table_locations)

    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(json.dumps({
        "status": "ok",
        "doc_url": doc_url,
        "doc_id": doc_id,
        "folder_id": folder_id
    }))


if __name__ == "__main__":
    main()

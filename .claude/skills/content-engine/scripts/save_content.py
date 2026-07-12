#!/usr/bin/env python3
"""Save a content piece as a formatted Google Doc via gws CLI.

Reads content JSON from stdin, creates a Google Doc with proper formatting
(headings, body text, bullets, tables), and saves it to the Nexis Content
folder in Google Drive.

Two payload shapes:
    {"title": "...", "sections": [...]}                 single doc, one (default) tab
    {"title": "...", "tabs": [{"title","sections"},...]} one real Google Docs tab per entry

Usage:
    echo '{"title":"...","sections":[...]}' | python save_content.py
    echo '{"title":"...","tabs":[{"title":"LinkedIn","sections":[...]},...]}' | python save_content.py
    cat content.json | python save_content.py

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
DRIVE_FOLDER_NAME = "Nexis Content"


def find_gws():
    """Find gws and return (cmd_list, use_shell).

    On Windows, prefer the standalone compiled gws.exe (shipped in the CLI
    package's bin/) so calls run with shell=False: no cmd.exe re-tokenization,
    which is what breaks on JSON bodies containing quotes/`>`/markdown.
    Falls back to node + run-gws.js, then gws.cmd with shell=True.
    """
    npm_dir = Path(os.environ.get("APPDATA", "")) / "npm"
    gws_exe = npm_dir / "node_modules" / "@googleworkspace" / "cli" / "bin" / "gws.exe"
    if gws_exe.exists():
        return ([str(gws_exe)], False)

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
    """Find or create the Nexis Content folder in Google Drive."""
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
    """Create a blank Google Doc and move it to the content folder."""
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


def get_default_tab_id(doc_id):
    """A freshly-created doc has one default tab. Read its id (usually 't.0',
    but don't hardcode it)."""
    doc = run_gws([
        "docs", "documents", "get",
        "--params", json.dumps({"documentId": doc_id, "includeTabsContent": True})
    ])
    tabs = doc.get("tabs", [])
    if tabs:
        return tabs[0]["tabProperties"]["tabId"]
    return None


def rename_tab(doc_id, tab_id, title):
    run_gws(
        ["docs", "documents", "batchUpdate",
         "--params", json.dumps({"documentId": doc_id})],
        json_body={"requests": [{
            "updateDocumentTabProperties": {
                "tabProperties": {"tabId": tab_id, "title": title},
                "fields": "title"
            }
        }]}
    )


def create_tab(doc_id, title):
    """Add a new tab to the document and rename it. Returns the new tabId."""
    result = run_gws(
        ["docs", "documents", "batchUpdate",
         "--params", json.dumps({"documentId": doc_id})],
        json_body={"requests": [{"addDocumentTab": {}}]}
    )
    tab_id = result["replies"][0]["addDocumentTab"]["tabProperties"]["tabId"]
    rename_tab(doc_id, tab_id, title)
    return tab_id


def write_tab_content(doc_id, tab_id, sections, tab_title):
    """Insert all sections' content into one tab, chunked to stay under the
    Windows command line length limit."""
    text_requests, table_locations = build_text_requests(sections, tab_id=tab_id)
    if text_requests:
        for i, chunk in enumerate(chunk_by_size(text_requests)):
            try:
                run_gws(
                    ["docs", "documents", "batchUpdate",
                     "--params", json.dumps({"documentId": doc_id})],
                    json_body={"requests": chunk}
                )
            except RuntimeError as e:
                error_exit(f"Failed to insert content into tab '{tab_title}' (chunk {i + 1}): {e}")
    if table_locations:
        insert_tables(doc_id, table_locations, tab_id=tab_id)


def build_text_requests(sections, tab_id=None):
    """Build batchUpdate requests for all text content in one tab.

    tab_id: when set (multi-tab documents), stamped onto every location/range so
    the request targets that tab instead of the document's default tab.

    Returns (requests_list, table_locations) where table_locations is a list of
    (insert_index, table_data) tuples for second-pass table insertion.
    """
    def loc(index):
        return {"index": index, "tabId": tab_id} if tab_id else {"index": index}

    def rng(start, end):
        if tab_id:
            return {"startIndex": start, "endIndex": end, "tabId": tab_id}
        return {"startIndex": start, "endIndex": end}

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
                    "location": loc(idx),
                    "text": heading_text
                }
            })
            style_map = {1: "HEADING_1", 2: "HEADING_2", 3: "HEADING_3"}
            named_style = style_map.get(level, "HEADING_1")
            requests.append({
                "updateParagraphStyle": {
                    "range": rng(idx, idx + len(heading_text)),
                    "paragraphStyle": {"namedStyleType": named_style},
                    "fields": "namedStyleType"
                }
            })
            idx += len(heading_text)

        if body:
            body_text = body + "\n"
            requests.append({
                "insertText": {
                    "location": loc(idx),
                    "text": body_text
                }
            })
            requests.append({
                "updateParagraphStyle": {
                    "range": rng(idx, idx + len(body_text)),
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
                        "location": loc(idx),
                        "text": bullet_text
                    }
                })
                requests.append({
                    "updateParagraphStyle": {
                        "range": rng(idx, idx + len(bullet_text)),
                        "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                        "fields": "namedStyleType"
                    }
                })
                requests.append({
                    "createParagraphBullets": {
                        "range": rng(idx, idx + len(bullet_text)),
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
                    "location": loc(idx),
                    "text": bullet_text
                }
            })
            requests.append({
                "updateParagraphStyle": {
                    "range": rng(idx, idx + len(bullet_text)),
                    "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                    "fields": "namedStyleType"
                }
            })
            requests.append({
                "createParagraphBullets": {
                    "range": rng(idx, idx + len(bullet_text)),
                    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
                }
            })
            # Bold the label portion (or entire bullet if plain string)
            if label_len > 0:
                requests.append({
                    "updateTextStyle": {
                        "range": rng(idx, idx + label_len),
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
                    "location": loc(idx),
                    "text": placeholder
                }
            })
            idx += len(placeholder)

        spacing = "\n"
        requests.append({
            "insertText": {
                "location": loc(idx),
                "text": spacing
            }
        })
        idx += len(spacing)

    return requests, table_locations


def chunk_by_size(requests, max_chars=6000):
    """Group batchUpdate requests so each chunk's serialized JSON stays under
    max_chars, regardless of request count (Windows command line limit is ~8191
    chars total, and the gws/node wrapper adds its own overhead)."""
    chunks = []
    current, current_len = [], 0
    for req in requests:
        req_len = len(json.dumps(req))
        if current and current_len + req_len > max_chars:
            chunks.append(current)
            current, current_len = [], 0
        current.append(req)
        current_len += req_len
    if current:
        chunks.append(current)
    return chunks


def get_tab_body_content(doc_id, tab_id):
    """Read a specific tab's body content (multi-tab documents nest content under
    tabs[].documentTab.body instead of the top-level body)."""
    doc = run_gws([
        "docs", "documents", "get",
        "--params", json.dumps({"documentId": doc_id, "includeTabsContent": True})
    ])
    for tab in doc.get("tabs", []):
        if tab.get("tabProperties", {}).get("tabId") == tab_id:
            return tab.get("documentTab", {}).get("body", {}).get("content", [])
    return []


def insert_tables(doc_id, table_locations, tab_id=None):
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

        table_location = {"index": insert_idx, "tabId": tab_id} if tab_id else {"index": insert_idx}
        try:
            run_gws(
                ["docs", "documents", "batchUpdate",
                 "--params", json.dumps({"documentId": doc_id})],
                json_body={"requests": [{
                    "insertTable": {
                        "location": table_location,
                        "rows": num_rows,
                        "columns": num_cols
                    }
                }]}
            )
        except RuntimeError as e:
            print(f"Warning: Failed to insert table: {e}", file=sys.stderr)
            continue

        try:
            if tab_id:
                body_content = get_tab_body_content(doc_id, tab_id)
            else:
                doc = run_gws([
                    "docs", "documents", "get",
                    "--params", json.dumps({"documentId": doc_id})
                ])
                body_content = doc.get("body", {}).get("content", [])
        except RuntimeError as e:
            print(f"Warning: Failed to read doc for table population: {e}", file=sys.stderr)
            continue

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
                    cell_loc = {"index": cell_start, "tabId": tab_id} if tab_id else {"index": cell_start}
                    cell_requests.append({
                        "insertText": {
                            "location": cell_loc,
                            "text": text
                        }
                    })
                    if row_idx == 0:
                        cell_range = ({"startIndex": cell_start, "endIndex": cell_start + len(text), "tabId": tab_id}
                                       if tab_id else
                                       {"startIndex": cell_start, "endIndex": cell_start + len(text)})
                        cell_requests.append({
                            "updateTextStyle": {
                                "range": cell_range,
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


_SMART_QUOTE_TABLE = str.maketrans({
    "‘": "'",   # left single quotation mark
    "’": "'",   # right single quotation mark / apostrophe
    "“": '"',   # left double quotation mark
    "”": '"',   # right double quotation mark
    "—": " - ", # em dash
    "–": "-",   # en dash
    "…": "...", # ellipsis
})


def normalize_text(value):
    """Recursively replace smart quotes, em/en dashes with ASCII equivalents."""
    if isinstance(value, str):
        return value.translate(_SMART_QUOTE_TABLE)
    if isinstance(value, dict):
        return {k: normalize_text(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalize_text(item) for item in value]
    return value


def validate_section(section, label):
    if not isinstance(section, dict):
        error_exit(f"Section {label} must be a JSON object")
    if not any(k in section for k in ["heading", "body", "bullets", "bold_bullets", "table"]):
        error_exit(f"Section {label} has no content (needs heading, body, bullets, bold_bullets, or table)")


def validate_content(content):
    """Two payload shapes:
    - {"title", "sections": [...]}  -> single doc, all sections in one (default) tab.
    - {"title", "tabs": [{"title", "sections": [...]}, ...]}  -> one real Docs tab
      per entry, in order. Use this when the content has natural top-level groupings
      (e.g. LinkedIn / Instagram / Source) that should be separately navigable.
    """
    if not isinstance(content, dict):
        error_exit("Input must be a JSON object")
    if "title" not in content:
        error_exit("Missing required field: 'title'")

    if "tabs" in content:
        if not content["tabs"]:
            error_exit("'tabs' array is empty")
        for i, tab in enumerate(content["tabs"]):
            if not isinstance(tab, dict) or "title" not in tab:
                error_exit(f"tabs[{i}] must be an object with a 'title'")
            if not tab.get("sections"):
                error_exit(f"tabs[{i}] ('{tab.get('title')}') has no 'sections'")
            for j, section in enumerate(tab["sections"]):
                validate_section(section, f"tabs[{i}].sections[{j}]")
        return

    if "sections" not in content or not content["sections"]:
        error_exit("Missing or empty 'sections' array (or use 'tabs' for a multi-tab doc)")
    for i, section in enumerate(content["sections"]):
        validate_section(section, str(i))


def main():
    try:
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
        raw = sys.stdin.read()
        if not raw.strip():
            error_exit("No input received on stdin. Pipe content JSON to this script.")
        content = json.loads(raw)
    except json.JSONDecodeError as e:
        error_exit(f"Invalid JSON input: {e}")

    validate_content(content)
    content = normalize_text(content)

    title = content["title"]
    folder_id = find_or_create_folder()
    doc_id = create_doc(title, folder_id)

    if "tabs" in content:
        default_tab_id = get_default_tab_id(doc_id)
        for i, tab_spec in enumerate(content["tabs"]):
            tab_title = tab_spec["title"]
            if i == 0 and default_tab_id:
                tab_id = default_tab_id
                rename_tab(doc_id, tab_id, tab_title)
            else:
                tab_id = create_tab(doc_id, tab_title)
            write_tab_content(doc_id, tab_id, tab_spec["sections"], tab_title)
    else:
        text_requests, table_locations = build_text_requests(content["sections"])
        if text_requests:
            # Chunk by serialized size, not request count: a handful of long bullets
            # (e.g. full image-generation prompts) can blow the Windows command line
            # limit well before 30 requests are reached.
            for i, chunk in enumerate(chunk_by_size(text_requests)):
                try:
                    run_gws(
                        ["docs", "documents", "batchUpdate",
                         "--params", json.dumps({"documentId": doc_id})],
                        json_body={"requests": chunk}
                    )
                except RuntimeError as e:
                    error_exit(f"Failed to insert text content (chunk {i + 1}): {e}")
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

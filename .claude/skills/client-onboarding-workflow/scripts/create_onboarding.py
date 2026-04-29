#!/usr/bin/env python3
"""Create the full client onboarding kit via gws.

Reads an onboarding spec from stdin (JSON) and produces:
  1. Drive folder structure: NexusPoint Clients / [Client] / {01-Onboarding, 02-Assets,
     03-Deliverables, 04-Communication, 05-Invoices}
  2. Onboarding Google Doc inside 01-Onboarding (sections schema mirrors proposal-generator)
  3. Project Checklist Google Sheet inside 01-Onboarding (one row per checklist item)
  4. Gmail draft to the client contact (saved as DRAFT, never sent)

Input JSON shape (see references/checklist-templates.md and welcome-email-voice.md for
how the model assembles each piece):

{
  "client_name": "Acme Corp",
  "project_name": "Acme website rebuild",
  "contact_name": "Sarah Chen",
  "contact_email": "sarah@acme.com",
  "doc": {
    "title": "Acme Corp -- Onboarding",
    "sections": [
      {"heading": "...", "level": 1, "body": "..."},
      {"heading": "...", "level": 2, "bullets": ["..."]},
      {"heading": "...", "level": 1, "table": {"headers": [...], "rows": [[...]]}}
    ]
  },
  "checklist": {
    "title": "Acme Corp -- Project Checklist",
    "headers": ["Stage", "Task", "Owner", "Due", "Status", "Notes"],
    "rows": [["Discovery", "Kickoff call", "Aleem", "", "Not started", ""], ...]
  },
  "email": {
    "subject": "Welcome to NexusPoint -- Acme website rebuild kickoff",
    "body": "Hi Sarah,\\n\\n..."
  }
}

Output (stdout, JSON):
  {"status": "ok", "client_folder_url": "...", "onboarding_doc_url": "...",
   "checklist_sheet_url": "...", "draft_id": "..."}
"""

import base64
import json
import sys
from email.message import EmailMessage
from pathlib import Path

from _gws import find_or_create_folder, move_to_folder, run_gws

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
PARENT_FOLDER_CACHE = SKILL_DIR / ".clients_folder_id"
PARENT_FOLDER_NAME = "NexusPoint Clients"
SUBFOLDERS = [
    "01-Onboarding",
    "02-Assets",
    "03-Deliverables",
    "04-Communication",
    "05-Invoices",
]


def error_exit(message):
    print(json.dumps({"status": "error", "message": message}))
    sys.exit(1)


# ---------- Doc creation (mirrors proposal-generator's batchUpdate flow) ----------


def create_doc(title, folder_id):
    result = run_gws(["docs", "documents", "create"], json_body={"title": title})
    doc_id = result.get("documentId")
    if not doc_id:
        raise RuntimeError(f"Failed to create document. Response: {result}")
    try:
        move_to_folder(doc_id, folder_id)
    except RuntimeError as e:
        print(f"Warning: could not move doc to folder: {e}", file=sys.stderr)
    return doc_id


def build_text_requests(sections):
    """Build batchUpdate requests for text content. Returns (requests, table_locations)."""
    requests = []
    table_locations = []
    idx = 1

    for section in sections:
        heading = section.get("heading", "")
        level = section.get("level", 1)
        body = section.get("body", "")
        bullets = section.get("bullets", [])
        table = section.get("table")

        if heading:
            heading_text = heading + "\n"
            requests.append({"insertText": {"location": {"index": idx}, "text": heading_text}})
            style_map = {1: "HEADING_1", 2: "HEADING_2", 3: "HEADING_3"}
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": idx, "endIndex": idx + len(heading_text)},
                    "paragraphStyle": {"namedStyleType": style_map.get(level, "HEADING_1")},
                    "fields": "namedStyleType",
                }
            })
            idx += len(heading_text)

        if body:
            body_text = body + "\n"
            requests.append({"insertText": {"location": {"index": idx}, "text": body_text}})
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": idx, "endIndex": idx + len(body_text)},
                    "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                    "fields": "namedStyleType",
                }
            })
            idx += len(body_text)

        if bullets:
            for bullet in bullets:
                bullet_text = bullet + "\n"
                requests.append({"insertText": {"location": {"index": idx}, "text": bullet_text}})
                requests.append({
                    "updateParagraphStyle": {
                        "range": {"startIndex": idx, "endIndex": idx + len(bullet_text)},
                        "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                        "fields": "namedStyleType",
                    }
                })
                requests.append({
                    "createParagraphBullets": {
                        "range": {"startIndex": idx, "endIndex": idx + len(bullet_text)},
                        "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE",
                    }
                })
                idx += len(bullet_text)

        if table:
            table_locations.append((idx, table))
            placeholder = "\n"
            requests.append({"insertText": {"location": {"index": idx}, "text": placeholder}})
            idx += len(placeholder)

        spacing = "\n"
        requests.append({"insertText": {"location": {"index": idx}, "text": spacing}})
        idx += len(spacing)

    return requests, table_locations


def insert_tables(doc_id, table_locations):
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
                        "columns": num_cols,
                    }
                }]},
            )
        except RuntimeError as e:
            print(f"Warning: failed to insert table: {e}", file=sys.stderr)
            continue

        try:
            doc = run_gws([
                "docs", "documents", "get",
                "--params", json.dumps({"documentId": doc_id}),
            ])
        except RuntimeError as e:
            print(f"Warning: failed to read doc for table population: {e}", file=sys.stderr)
            continue

        target_table = None
        for element in doc.get("body", {}).get("content", []):
            if "table" in element and element.get("startIndex", 0) >= insert_idx - 2:
                target_table = element["table"]
                break
        if not target_table:
            print(f"Warning: could not find inserted table near {insert_idx}", file=sys.stderr)
            continue

        cell_requests = []
        for row_idx, table_row in enumerate(target_table.get("tableRows", [])):
            for col_idx, cell in enumerate(table_row.get("tableCells", [])):
                cell_content = cell.get("content", [])
                if not cell_content:
                    continue
                cell_start = cell_content[0].get("startIndex", 0)
                if row_idx == 0:
                    if col_idx >= len(headers):
                        continue
                    text = headers[col_idx]
                else:
                    data_row_idx = row_idx - 1
                    if data_row_idx >= len(rows) or col_idx >= len(rows[data_row_idx]):
                        continue
                    text = rows[data_row_idx][col_idx]
                if not text:
                    continue
                cell_requests.append({
                    "insertText": {"location": {"index": cell_start}, "text": text}
                })
                if row_idx == 0:
                    cell_requests.append({
                        "updateTextStyle": {
                            "range": {"startIndex": cell_start, "endIndex": cell_start + len(text)},
                            "textStyle": {"bold": True},
                            "fields": "bold",
                        }
                    })

        if cell_requests:
            cell_requests.sort(
                key=lambda r: (
                    r.get("insertText", r.get("updateTextStyle", {}))
                    .get("location", r.get("insertText", r.get("updateTextStyle", {})).get("range", {}))
                    .get("index", r.get("insertText", r.get("updateTextStyle", {})).get("range", {}).get("startIndex", 0))
                ),
                reverse=True,
            )
            try:
                run_gws(
                    ["docs", "documents", "batchUpdate",
                     "--params", json.dumps({"documentId": doc_id})],
                    json_body={"requests": cell_requests},
                )
            except RuntimeError as e:
                print(f"Warning: failed to populate cells: {e}", file=sys.stderr)


def write_doc(doc_spec, folder_id):
    title = doc_spec.get("title", "Onboarding")
    sections = doc_spec.get("sections", [])
    doc_id = create_doc(title, folder_id)
    text_requests, table_locations = build_text_requests(sections)
    if text_requests:
        run_gws(
            ["docs", "documents", "batchUpdate",
             "--params", json.dumps({"documentId": doc_id})],
            json_body={"requests": text_requests},
        )
    if table_locations:
        insert_tables(doc_id, table_locations)
    return doc_id


# ---------- Checklist Sheet creation ----------


def create_checklist_sheet(checklist, folder_id):
    title = checklist.get("title", "Project Checklist")
    headers = checklist.get("headers", [])
    rows = checklist.get("rows", [])

    result = run_gws(
        ["sheets", "spreadsheets", "create"],
        json_body={"properties": {"title": title}},
    )
    sheet_id = result.get("spreadsheetId")
    if not sheet_id:
        raise RuntimeError(f"Failed to create spreadsheet. Response: {result}")

    try:
        move_to_folder(sheet_id, folder_id)
    except RuntimeError as e:
        print(f"Warning: could not move sheet to folder: {e}", file=sys.stderr)

    values = [headers] + rows if headers else rows
    if values:
        run_gws(
            ["sheets", "spreadsheets", "values", "update",
             "--params", json.dumps({
                 "spreadsheetId": sheet_id,
                 "range": "A1",
                 "valueInputOption": "USER_ENTERED",
             })],
            json_body={"values": values},
        )

        sheet_tab_id = result.get("sheets", [{}])[0].get("properties", {}).get("sheetId", 0)
        format_requests = [
            {
                "repeatCell": {
                    "range": {"sheetId": sheet_tab_id, "startRowIndex": 0, "endRowIndex": 1},
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {"bold": True},
                            "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9},
                        }
                    },
                    "fields": "userEnteredFormat(textFormat,backgroundColor)",
                }
            },
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_tab_id,
                        "gridProperties": {"frozenRowCount": 1},
                    },
                    "fields": "gridProperties.frozenRowCount",
                }
            },
        ]
        try:
            run_gws(
                ["sheets", "spreadsheets", "batchUpdate",
                 "--params", json.dumps({"spreadsheetId": sheet_id})],
                json_body={"requests": format_requests},
            )
        except RuntimeError as e:
            print(f"Warning: failed to format header row: {e}", file=sys.stderr)

    return sheet_id


# ---------- Gmail draft ----------


def create_gmail_draft(email_spec, contact_email):
    msg = EmailMessage()
    msg["To"] = contact_email
    msg["Subject"] = email_spec.get("subject", "Welcome")
    msg.set_content(email_spec.get("body", ""))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")

    result = run_gws(
        ["gmail", "users", "drafts", "create",
         "--params", json.dumps({"userId": "me"})],
        json_body={"message": {"raw": raw}},
    )
    draft_id = result.get("id")
    if not draft_id:
        raise RuntimeError(f"Failed to create draft. Response: {result}")
    return draft_id


# ---------- Main orchestration ----------


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            error_exit("No input on stdin. Pipe onboarding JSON to this script.")
        spec = json.loads(raw)
    except json.JSONDecodeError as e:
        error_exit(f"Invalid JSON input: {e}")

    for field in ("client_name", "contact_email", "doc", "checklist", "email"):
        if field not in spec:
            error_exit(f"Missing required field: {field}")

    client_name = spec["client_name"]
    contact_email = spec["contact_email"]

    try:
        parent_id = find_or_create_folder(
            PARENT_FOLDER_NAME,
            cache_path=str(PARENT_FOLDER_CACHE),
        )
    except RuntimeError as e:
        error_exit(f"Failed to set up parent folder: {e}")

    try:
        client_folder_id = find_or_create_folder(client_name, parent_id=parent_id)
    except RuntimeError as e:
        error_exit(f"Failed to create client folder: {e}")

    subfolder_ids = {}
    for sub in SUBFOLDERS:
        try:
            subfolder_ids[sub] = find_or_create_folder(sub, parent_id=client_folder_id)
        except RuntimeError as e:
            print(f"Warning: failed to create subfolder {sub}: {e}", file=sys.stderr)

    onboarding_folder_id = subfolder_ids.get("01-Onboarding", client_folder_id)

    try:
        doc_id = write_doc(spec["doc"], onboarding_folder_id)
    except RuntimeError as e:
        error_exit(f"Failed to create onboarding doc: {e}")

    try:
        sheet_id = create_checklist_sheet(spec["checklist"], onboarding_folder_id)
    except RuntimeError as e:
        error_exit(f"Failed to create checklist sheet: {e}")

    draft_id = None
    draft_error = None
    try:
        draft_id = create_gmail_draft(spec["email"], contact_email)
    except RuntimeError as e:
        draft_error = str(e)

    output = {
        "status": "ok",
        "client_name": client_name,
        "client_folder_url": f"https://drive.google.com/drive/folders/{client_folder_id}",
        "client_folder_id": client_folder_id,
        "subfolders": {name: f"https://drive.google.com/drive/folders/{fid}"
                       for name, fid in subfolder_ids.items()},
        "onboarding_doc_url": f"https://docs.google.com/document/d/{doc_id}/edit",
        "onboarding_doc_id": doc_id,
        "checklist_sheet_url": f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit",
        "checklist_sheet_id": sheet_id,
        "draft_id": draft_id,
    }
    if draft_error:
        output["draft_error"] = draft_error

    print(json.dumps(output))


if __name__ == "__main__":
    main()

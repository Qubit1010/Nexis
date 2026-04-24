#!/usr/bin/env python3
"""Create a formatted Google Doc audit report via gws CLI.

Reads audit JSON from stdin (produced by analyze_audit.py), transforms it into
the Doc section schema, creates the doc in the "NexusPoint Website Audits"
Drive folder, and prints the URL.

Usage:
    cat audit.json | python create_audit_doc.py

Output (stdout):
    {"status": "ok", "doc_url": "...", "doc_id": "..."}
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
FOLDER_CACHE = SKILL_DIR / ".folder_id"
DRIVE_FOLDER_NAME = "NexusPoint Website Audits"


def find_gws():
    """Find gws: prefer direct node+run-gws.js to bypass Windows 8191-char cmd limit."""
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


GWS_CMD, GWS_USE_SHELL = find_gws()


def error_exit(message):
    print(json.dumps({"status": "error", "message": message}))
    sys.exit(1)


def run_gws(args, json_body=None):
    cmd = GWS_CMD + args
    if json_body is not None:
        cmd += ["--json", json.dumps(json_body)]
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=120,
        shell=GWS_USE_SHELL, encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        stderr = result.stderr.strip() if result.stderr else "Unknown error"
        raise RuntimeError(f"gws failed: {' '.join(args[:3])}... | {stderr}")
    stdout = result.stdout.strip()
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"raw": stdout}


def find_or_create_folder():
    if FOLDER_CACHE.exists():
        cached = FOLDER_CACHE.read_text().strip()
        if cached:
            try:
                result = run_gws([
                    "drive", "files", "list",
                    "--params", json.dumps({
                        "q": f"name='{DRIVE_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                        "fields": "files(id,name)"
                    })
                ])
                for f in result.get("files", []) or []:
                    if f.get("id") == cached:
                        return cached
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
        files = result.get("files", []) or []
        if files:
            folder_id = files[0]["id"]
            FOLDER_CACHE.write_text(folder_id)
            return folder_id
    except RuntimeError:
        pass

    result = run_gws(
        ["drive", "files", "create"],
        json_body={"name": DRIVE_FOLDER_NAME, "mimeType": "application/vnd.google-apps.folder"},
    )
    folder_id = result.get("id")
    if not folder_id:
        error_exit(f"Failed to create Drive folder. Response: {result}")
    FOLDER_CACHE.write_text(folder_id)
    return folder_id


def create_doc(title, folder_id):
    result = run_gws(["docs", "documents", "create"], json_body={"title": title})
    doc_id = result.get("documentId")
    if not doc_id:
        error_exit(f"Failed to create document. Response: {result}")
    try:
        run_gws([
            "drive", "files", "update",
            "--params", json.dumps({"fileId": doc_id, "addParents": folder_id}),
            "--json", "{}",
        ])
    except RuntimeError as e:
        print(f"Warning: Could not move doc to folder: {e}", file=sys.stderr)
    return doc_id


def severity_label(sev: str) -> str:
    return {
        "critical": "Critical",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
    }.get((sev or "").lower(), "Note")


def build_sections_quick(audit: dict) -> list:
    """Build section list for quick mode audit."""
    company = audit.get("company") or "Your Site"
    url = audit.get("url", "")
    summary = audit.get("summary", "")
    findings = audit.get("findings", []) or []

    sections = [
        {"heading": f"Website Audit: {company}", "level": 1,
         "body": f"Site: {url}\nAudit date: {datetime.now().strftime('%Y-%m-%d')}\nPrepared by NexusPoint"},
        {"heading": "Summary", "level": 2, "body": summary},
        {"heading": "Top findings", "level": 2,
         "body": "Prioritized by impact. Each finding includes the issue, what it costs you, and the fix."},
    ]

    for i, f in enumerate(findings, start=1):
        title = f.get("title", "")
        heading = f"{i}. [{severity_label(f.get('severity'))}] {title}"
        body_lines = []
        if f.get("dimension"):
            body_lines.append(f"Area: {f['dimension']}")
        if f.get("evidence"):
            body_lines.append(f"What we saw: {f['evidence']}")
        if f.get("business_impact"):
            body_lines.append(f"Why it matters: {f['business_impact']}")
        if f.get("fix"):
            body_lines.append(f"Fix: {f['fix']}")
        if f.get("effort"):
            body_lines.append(f"Effort: {f['effort']}")
        sections.append({"heading": heading, "level": 3, "body": "\n".join(body_lines)})

    sections.append({
        "heading": "Next steps", "level": 2,
        "body": "Happy to walk through any of these in more detail, or handle the fixes directly. Reply to the email that sent this and we will set up 15 minutes, or skip straight to the quick wins above.",
    })

    return sections


def build_sections_deep(audit: dict) -> list:
    """Build section list for deep mode audit."""
    company = audit.get("company") or "Your Site"
    url = audit.get("url", "")
    summary = audit.get("summary", "")
    findings = audit.get("findings", []) or []
    scores = audit.get("scores") or {}

    sections = [
        {"heading": f"Website Audit: {company}", "level": 1,
         "body": f"Site: {url}\nAudit date: {datetime.now().strftime('%Y-%m-%d')}\nPrepared by NexusPoint"},
        {"heading": "Executive summary", "level": 2, "body": summary},
    ]

    if scores:
        table = {
            "headers": ["Dimension", "Score (1-10)", "Status"],
            "rows": [],
        }
        label_map = {
            "ux": "UX & Messaging",
            "seo": "SEO Basics",
            "performance": "Performance",
            "conversion": "Conversion",
        }
        for key, label in label_map.items():
            val = scores.get(key)
            if val is None:
                continue
            if val >= 9:
                status = "Exceptional"
            elif val >= 7:
                status = "Strong"
            elif val >= 5:
                status = "Mixed"
            elif val >= 3:
                status = "Weak"
            else:
                status = "Severe"
            table["rows"].append([label, str(val), status])
        sections.append({"heading": "Scorecard", "level": 2, "table": table})

    # Group findings by dimension
    by_dim = {}
    for f in findings:
        by_dim.setdefault(f.get("dimension", "Other"), []).append(f)

    for dim in ["UX & Messaging", "SEO Basics", "Performance", "Conversion"]:
        dim_findings = by_dim.get(dim, [])
        if not dim_findings:
            continue
        sections.append({"heading": dim, "level": 2})
        for f in dim_findings:
            title = f.get("title", "")
            heading = f"[{severity_label(f.get('severity'))}] {title}"
            body_lines = []
            if f.get("evidence"):
                body_lines.append(f"What we saw: {f['evidence']}")
            if f.get("business_impact"):
                body_lines.append(f"Why it matters: {f['business_impact']}")
            if f.get("fix"):
                body_lines.append(f"Fix: {f['fix']}")
            if f.get("effort"):
                body_lines.append(f"Effort: {f['effort']}")
            sections.append({"heading": heading, "level": 3, "body": "\n".join(body_lines)})

    # Prioritized action list
    sev_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    ranked = sorted(findings, key=lambda f: sev_rank.get((f.get("severity") or "").lower(), 9))
    sections.append({
        "heading": "Prioritized action list",
        "level": 2,
        "bullets": [f"[{severity_label(f.get('severity'))}] {f.get('title', '')} ({f.get('effort', '?')} effort)" for f in ranked],
    })

    sections.append({
        "heading": "How NexusPoint can help",
        "level": 2,
        "body": "NexusPoint builds and optimizes websites for startups and growing businesses. We handle the fixes above directly, or integrate with your existing team on whichever items you want to prioritize. If you want to move on any of these, reply to the email that sent this audit and we will scope the work.",
    })

    return sections


# Reuse the text+table request builder from proposal-generator pattern.
def build_text_requests(sections):
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

        for bullet in bullets or []:
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
            requests.append({"insertText": {"location": {"index": idx}, "text": "\n"}})
            idx += 1

        requests.append({"insertText": {"location": {"index": idx}, "text": "\n"}})
        idx += 1

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
                    "insertTable": {"location": {"index": insert_idx}, "rows": num_rows, "columns": num_cols}
                }]},
            )
        except RuntimeError as e:
            print(f"Warning: Failed to insert table: {e}", file=sys.stderr)
            continue

        try:
            doc = run_gws([
                "docs", "documents", "get",
                "--params", json.dumps({"documentId": doc_id}),
            ])
        except RuntimeError as e:
            print(f"Warning: Failed to read doc: {e}", file=sys.stderr)
            continue

        body_content = doc.get("body", {}).get("content", [])
        target_table = None
        for element in body_content:
            if "table" in element and element.get("startIndex", 0) >= insert_idx - 2:
                target_table = element["table"]
                break
        if not target_table:
            continue

        cell_requests = []
        for row_idx, table_row in enumerate(target_table.get("tableRows", [])):
            for col_idx, cell in enumerate(table_row.get("tableCells", [])):
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
                    r = row_idx - 1
                    if r < len(rows) and col_idx < len(rows[r]):
                        text = rows[r][col_idx]
                    else:
                        continue
                if text:
                    cell_requests.append({"insertText": {"location": {"index": cell_start}, "text": text}})
                    if row_idx == 0:
                        cell_requests.append({
                            "updateTextStyle": {
                                "range": {"startIndex": cell_start, "endIndex": cell_start + len(text)},
                                "textStyle": {"bold": True},
                                "fields": "bold",
                            }
                        })

        if cell_requests:
            def sort_key(r):
                if "insertText" in r:
                    return r["insertText"]["location"]["index"]
                return r["updateTextStyle"]["range"]["startIndex"]
            cell_requests.sort(key=sort_key, reverse=True)
            try:
                run_gws(
                    ["docs", "documents", "batchUpdate",
                     "--params", json.dumps({"documentId": doc_id})],
                    json_body={"requests": cell_requests},
                )
            except RuntimeError as e:
                print(f"Warning: Failed to populate table: {e}", file=sys.stderr)


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            error_exit("No input. Pipe audit JSON to this script.")
        audit = json.loads(raw)
    except json.JSONDecodeError as e:
        error_exit(f"Invalid JSON: {e}")

    mode = audit.get("mode", "quick")
    company = audit.get("company") or "Website"
    today = datetime.now().strftime("%Y-%m-%d")
    title = f"Website Audit - {company} - {today}"

    folder_id = find_or_create_folder()
    doc_id = create_doc(title, folder_id)

    sections = build_sections_deep(audit) if mode == "deep" else build_sections_quick(audit)
    text_requests, table_locations = build_text_requests(sections)

    if text_requests:
        try:
            run_gws(
                ["docs", "documents", "batchUpdate",
                 "--params", json.dumps({"documentId": doc_id})],
                json_body={"requests": text_requests},
            )
        except RuntimeError as e:
            error_exit(f"Failed to insert text: {e}")

    if table_locations:
        insert_tables(doc_id, table_locations)

    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(json.dumps({"status": "ok", "doc_url": doc_url, "doc_id": doc_id, "folder_id": folder_id}))


if __name__ == "__main__":
    main()

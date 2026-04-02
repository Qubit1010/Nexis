#!/usr/bin/env python3
"""Log a content post to the Content Log sheet tab.

Reads post metadata from stdin, appends a row to the "Content Log" tab of the
saved-topics spreadsheet, and optionally marks the source row in Sheet1 as "Used"
when the content came from a saved topic.

Also auto-creates the "Content Log" tab with headers on first run if it doesn't exist.

Usage:
    echo '<JSON>' | python log_post.py

Input JSON:
    {
      "platform": "LinkedIn",
      "format": "Text Post",
      "goal": "Thought leadership",
      "title": "...",
      "hook": "...",
      "doc_url": "https://docs.google.com/...",
      "source_title": "..."   (optional — exact title from saved-topics Sheet1 to mark as Used)
    }

Output (stdout):
    {"status": "ok", "row": N}
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SHEET_ID = "1TwAuLDKak3hpPWqlojpNL_OTsUyCOBaAVjRRncOpb9Q"
LOG_TAB = "Content Log"
SOURCE_TAB = "Sheet1"

LOG_HEADERS = [
    "Date Posted",
    "Platform",
    "Format",
    "Title/Topic",
    "Goal",
    "Hook",
    "Doc URL",
    "Status",
]


# ---------------------------------------------------------------------------
# gws helpers
# ---------------------------------------------------------------------------

def find_gws():
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


def run_gws(args, json_body=None):
    cmd = GWS_CMD + args
    if json_body is not None:
        cmd += ["--json", json.dumps(json_body)]
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=60,
        shell=GWS_USE_SHELL, encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        raise RuntimeError(f"gws failed: {result.stderr.strip()}")
    stdout = result.stdout.strip()
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"raw": stdout}


def error_exit(message):
    print(json.dumps({"status": "error", "message": message}))
    sys.exit(1)


# ---------------------------------------------------------------------------
# Sheet helpers
# ---------------------------------------------------------------------------

def get_sheet_tabs():
    """Return list of sheet tab titles."""
    try:
        result = run_gws([
            "sheets", "spreadsheets", "get",
            "--params", json.dumps({
                "spreadsheetId": SHEET_ID,
                "fields": "sheets.properties.title"
            })
        ])
        return [s["properties"]["title"] for s in result.get("sheets", [])]
    except RuntimeError:
        return []


def ensure_log_tab():
    """Create Content Log tab with headers if it doesn't exist. Returns row count."""
    tabs = get_sheet_tabs()
    if LOG_TAB not in tabs:
        # Create the sheet tab
        try:
            run_gws(
                ["sheets", "spreadsheets", "batchUpdate",
                 "--params", json.dumps({"spreadsheetId": SHEET_ID})],
                json_body={"requests": [{"addSheet": {"properties": {"title": LOG_TAB}}}]}
            )
        except RuntimeError as e:
            error_exit(f"Failed to create Content Log tab: {e}")

        # Write headers
        try:
            run_gws([
                "sheets", "spreadsheets", "values", "update",
                "--params", json.dumps({
                    "spreadsheetId": SHEET_ID,
                    "range": f"{LOG_TAB}!A1",
                    "valueInputOption": "RAW"
                }),
                "--json", json.dumps({"values": [LOG_HEADERS]})
            ])
        except RuntimeError as e:
            error_exit(f"Failed to write Content Log headers: {e}")

        return 1  # 1 row (headers)

    # Tab exists — get current row count
    try:
        result = run_gws([
            "sheets", "spreadsheets", "values", "get",
            "--params", json.dumps({
                "spreadsheetId": SHEET_ID,
                "range": f"{LOG_TAB}!A:A"
            })
        ])
        values = result.get("values", [])
        return len(values)
    except RuntimeError:
        return 1


def append_log_row(post):
    """Append one row to the Content Log tab."""
    today = datetime.now().strftime("%Y-%m-%d")
    row = [
        today,
        post.get("platform", ""),
        post.get("format", ""),
        post.get("title", ""),
        post.get("goal", ""),
        post.get("hook", ""),
        post.get("doc_url", ""),
        "Draft",
    ]
    try:
        run_gws([
            "sheets", "spreadsheets", "values", "append",
            "--params", json.dumps({
                "spreadsheetId": SHEET_ID,
                "range": f"{LOG_TAB}!A1",
                "valueInputOption": "RAW",
                "insertDataOption": "INSERT_ROWS"
            }),
            "--json", json.dumps({"values": [row]})
        ])
    except RuntimeError as e:
        error_exit(f"Failed to append to Content Log: {e}")


def mark_source_used(source_title):
    """Find the row in Sheet1 matching source_title and set Status = 'Used'."""
    if not source_title:
        return

    try:
        result = run_gws([
            "sheets", "spreadsheets", "values", "get",
            "--params", json.dumps({
                "spreadsheetId": SHEET_ID,
                "range": SOURCE_TAB
            })
        ])
        values = result.get("values", [])
    except RuntimeError as e:
        print(f"Warning: Could not read Sheet1 to mark source as Used: {e}", file=sys.stderr)
        return

    if not values:
        return

    headers = [h.strip() for h in values[0]]
    try:
        title_col = headers.index("Title")
        status_col = headers.index("Status")
    except ValueError:
        print("Warning: Could not find Title or Status column in Sheet1", file=sys.stderr)
        return

    # Find matching row (1-indexed for Sheets API, row 1 = headers)
    for i, row in enumerate(values[1:], start=2):
        row_title = row[title_col].strip() if title_col < len(row) else ""
        if row_title.lower() == source_title.lower():
            # Determine the column letter for Status
            col_letter = chr(ord("A") + status_col)
            cell_range = f"{SOURCE_TAB}!{col_letter}{i}"
            try:
                run_gws([
                    "sheets", "spreadsheets", "values", "update",
                    "--params", json.dumps({
                        "spreadsheetId": SHEET_ID,
                        "range": cell_range,
                        "valueInputOption": "RAW"
                    }),
                    "--json", json.dumps({"values": [["Used"]]})
                ])
            except RuntimeError as e:
                print(f"Warning: Could not mark source row as Used: {e}", file=sys.stderr)
            return


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    try:
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
        raw = sys.stdin.read()
        if not raw.strip():
            error_exit("No input received on stdin. Pipe post JSON to this script.")
        post = json.loads(raw)
    except json.JSONDecodeError as e:
        error_exit(f"Invalid JSON input: {e}")

    if not isinstance(post, dict):
        error_exit("Input must be a JSON object")

    row_count = ensure_log_tab()
    append_log_row(post)

    # If idea came from saved-topics, mark source row as Used
    source_title = post.get("source_title", "")
    if source_title:
        mark_source_used(source_title)

    print(json.dumps({
        "status": "ok",
        "row": row_count + 1,
        "logged_at": datetime.now().isoformat(),
    }))


if __name__ == "__main__":
    main()

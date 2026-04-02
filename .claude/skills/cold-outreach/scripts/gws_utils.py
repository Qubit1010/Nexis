#!/usr/bin/env python3
"""Shared utilities for cold-outreach skill scripts.

Provides:
- gws CLI subprocess wrapper (Windows-safe, batched)
- Google Sheets CRUD: create, append, read, update rows
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
SHEET_CACHE = SKILL_DIR / ".sheet_id"
SHEET_NAME = "NexusPoint Cold Outreach CRM"

# Tab names
TAB_RAW = "Raw Leads"
TAB_ENRICHED = "Enriched Leads"
TAB_STATS = "Daily Stats"
TAB_LF = "LF Leads"          # Leads Finder actor tab
TAB_GMAPS = "GMaps Leads"    # Google Maps actor tab
TAB_GSEARCH = "GSearch Leads" # Google Search actor tab

# Column definitions
RAW_HEADERS = ["Company", "LinkedIn URL", "Job Title Posted", "Pain Signal",
               "Industry", "Date Added", "Status",
               "Company Website", "First Name", "Last Name", "Decision Maker Title"]
ENRICHED_HEADERS = ["First Name", "Last Name", "Title", "Company", "Email",
                    "Verified", "LinkedIn URL", "Pain Signal", "Enrolled",
                    "Email 1 Date", "Email 2 Date", "Email 3 Date", "Email 4 Date",
                    "Status", "Reply Date", "Source"]
ACTOR_HEADERS = ["First Name", "Last Name", "Title", "Company", "Email",
                 "LinkedIn URL", "Pain Signal", "Date Added", "Source"]
STATS_HEADERS = ["Date", "Scraped", "Enriched", "Sent", "Replies", "Calls Booked"]


# ---------------------------------------------------------------------------
# gws subprocess setup
# ---------------------------------------------------------------------------

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


GWS_CMD, GWS_USE_SHELL = find_gws()


def error_exit(message):
    print(json.dumps({"status": "error", "message": message}), file=sys.stderr)
    sys.exit(1)


def run_gws(args, json_body=None):
    """Run a gws CLI command and return parsed JSON output."""
    cmd = GWS_CMD + args
    if json_body is not None:
        cmd += ["--json", json.dumps(json_body)]

    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=120,
        shell=GWS_USE_SHELL, encoding="utf-8", errors="replace"
    )

    if result.returncode != 0:
        stderr = result.stderr.strip() if result.stderr else "Unknown error"
        raise RuntimeError(
            f"gws command failed: {' '.join(str(a) for a in args[:3])}... | {stderr}"
        )

    stdout = result.stdout.strip()
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"raw": stdout}


# ---------------------------------------------------------------------------
# Google Sheets helpers
# ---------------------------------------------------------------------------

def get_or_create_sheet():
    """Find or create the CRM Google Sheet. Returns spreadsheetId."""
    if SHEET_CACHE.exists():
        cached = SHEET_CACHE.read_text().strip()
        if cached:
            try:
                # Verify it still exists
                run_gws(["sheets", "spreadsheets", "get",
                         "--params", json.dumps({"spreadsheetId": cached})])
                return cached
            except RuntimeError:
                pass  # Cache stale, recreate

    # Search Drive for existing sheet
    try:
        result = run_gws([
            "drive", "files", "list",
            "--params", json.dumps({
                "q": f"name='{SHEET_NAME}' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false",
                "fields": "files(id,name)"
            })
        ])
        files = result.get("files", [])
        if files:
            sheet_id = files[0]["id"]
            SHEET_CACHE.write_text(sheet_id)
            return sheet_id
    except RuntimeError:
        pass

    # Create new sheet
    result = run_gws(
        ["sheets", "spreadsheets", "create"],
        json_body={"properties": {"title": SHEET_NAME}}
    )
    sheet_id = result["spreadsheetId"]
    SHEET_CACHE.write_text(sheet_id)

    # Create tabs and headers
    _setup_tabs(sheet_id)
    return sheet_id


def _setup_tabs(sheet_id):
    """Create all CRM tabs with headers, replacing Sheet1."""
    tabs = [
        (TAB_RAW, RAW_HEADERS),
        (TAB_ENRICHED, ENRICHED_HEADERS),
        (TAB_STATS, STATS_HEADERS),
        (TAB_LF, ACTOR_HEADERS),
        (TAB_GMAPS, ACTOR_HEADERS),
        (TAB_GSEARCH, ACTOR_HEADERS),
    ]

    # Rename default Sheet1 to first tab
    first_tab, first_headers = tabs[0]
    try:
        run_gws(
            ["sheets", "spreadsheets", "batchUpdate",
             "--params", json.dumps({"spreadsheetId": sheet_id})],
            json_body={"requests": [{"updateSheetProperties": {
                "properties": {"sheetId": 0, "title": first_tab},
                "fields": "title"
            }}]}
        )
    except RuntimeError:
        pass

    # Add remaining tabs
    for tab_name, _ in tabs[1:]:
        try:
            run_gws(
                ["sheets", "spreadsheets", "batchUpdate",
                 "--params", json.dumps({"spreadsheetId": sheet_id})],
                json_body={"requests": [{"addSheet": {
                    "properties": {"title": tab_name}
                }}]}
            )
        except RuntimeError:
            pass

    # Write headers to each tab
    for tab_name, headers in tabs:
        _write_range(sheet_id, f"{tab_name}!A1", [headers])


def _write_range(sheet_id, range_notation, values):
    """Write values to a range using Sheets API."""
    run_gws(
        ["sheets", "spreadsheets", "values", "update",
         "--params", json.dumps({
             "spreadsheetId": sheet_id,
             "range": range_notation,
             "valueInputOption": "RAW"
         })],
        json_body={"values": values}
    )


def append_rows(sheet_id, tab, rows):
    """Append rows to a tab. rows = list of lists."""
    if not rows:
        return
    run_gws(
        ["sheets", "spreadsheets", "values", "append",
         "--params", json.dumps({
             "spreadsheetId": sheet_id,
             "range": f"{tab}!A1",
             "valueInputOption": "RAW",
             "insertDataOption": "INSERT_ROWS"
         })],
        json_body={"values": rows}
    )


def read_all_rows(sheet_id, tab):
    """Read all rows from a tab. Returns list of lists (no header)."""
    try:
        result = run_gws([
            "sheets", "spreadsheets", "values", "get",
            "--params", json.dumps({
                "spreadsheetId": sheet_id,
                "range": f"{tab}!A:Z"
            })
        ])
        values = result.get("values", [])
        if len(values) <= 1:
            return []
        return values[1:]  # skip header row
    except RuntimeError:
        return []


def read_rows_where(sheet_id, tab, col_index, col_value):
    """Read rows where column at col_index equals col_value."""
    all_rows = read_all_rows(sheet_id, tab)
    return [
        (i + 2, row)  # i+2 because row 1 = header, i is 0-indexed
        for i, row in enumerate(all_rows)
        if len(row) > col_index and row[col_index] == col_value
    ]


def update_cell(sheet_id, tab, row_num, col_letter, value):
    """Update a single cell. row_num is 1-indexed (1 = header)."""
    run_gws(
        ["sheets", "spreadsheets", "values", "update",
         "--params", json.dumps({
             "spreadsheetId": sheet_id,
             "range": f"{tab}!{col_letter}{row_num}",
             "valueInputOption": "RAW"
         })],
        json_body={"values": [[value]]}
    )


def get_headers(tab):
    """Return the header list for a given tab name."""
    return {
        TAB_RAW: RAW_HEADERS,
        TAB_ENRICHED: ENRICHED_HEADERS,
        TAB_STATS: STATS_HEADERS,
        TAB_LF: ACTOR_HEADERS,
        TAB_GMAPS: ACTOR_HEADERS,
        TAB_GSEARCH: ACTOR_HEADERS,
    }.get(tab, [])


def col_index(tab, col_name):
    """Return 0-based column index for a column name in a tab."""
    headers = get_headers(tab)
    try:
        return headers.index(col_name)
    except ValueError:
        return -1


def col_letter(index):
    """Convert 0-based column index to letter (0=A, 1=B, ...)."""
    result = ""
    while index >= 0:
        result = chr(index % 26 + ord("A")) + result
        index = index // 26 - 1
    return result

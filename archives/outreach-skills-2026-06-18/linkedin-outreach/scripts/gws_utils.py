"""Shared Google Sheets utilities for the LinkedIn Outreach skill."""

import json
import os
import shutil
import subprocess
from pathlib import Path

SHEET_NAME = "NexusPoint LinkedIn Outreach CRM"
TAB_LEADS = "Leads"

LEADS_HEADERS = [
    "Name", "First Name", "Company", "Role", "LinkedIn URL",
    "Location", "Recent Post", "Connection Message", "Status", "Date Added",
]

SKILL_DIR = Path(__file__).parent.parent
SHEET_ID_FILE = SKILL_DIR / ".sheet_id"


def find_gws():
    """Locate gws CLI. Returns (cmd_list, use_shell).

    Uses node + run-gws.js directly to avoid cmd.exe 8191-char limit on Windows.
    Falls back to gws.cmd with shell=True if node path not found.
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
            return ([node_exe, str(gws_js)], False)

    # Fallback: gws.cmd or plain gws
    gws_path = shutil.which("gws")
    if gws_path:
        return ([gws_path], True)
    gws_cmd = npm_dir / "gws.cmd"
    if gws_cmd.exists():
        return ([str(gws_cmd)], True)
    return (["gws"], True)


GWS_CMD, GWS_USE_SHELL = find_gws()


def run_gws(args, json_body=None):
    """Run a gws CLI command and return parsed JSON output.

    args      — CLI positional/flag args (e.g. ["sheets", "spreadsheets", "get", "--params", ...])
    json_body — request body dict, passed via --json flag
    """
    cmd = GWS_CMD + args
    if json_body is not None:
        cmd += ["--json", json.dumps(json_body)]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
        shell=GWS_USE_SHELL,
        encoding="utf-8",
        errors="replace",
    )

    if result.returncode != 0:
        stderr = result.stderr.strip() if result.stderr else ""
        stdout = result.stdout.strip() if result.stdout else ""
        raise RuntimeError(
            f"gws error: {stderr or stdout}"
        )

    stdout = result.stdout.strip()
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"raw": stdout}


def get_or_create_sheet():
    """Find or create the LinkedIn Outreach CRM sheet. Returns sheet_id."""
    # Use cached ID if available and still valid
    if SHEET_ID_FILE.exists():
        cached = SHEET_ID_FILE.read_text().strip()
        if cached:
            try:
                run_gws([
                    "sheets", "spreadsheets", "get",
                    "--params", json.dumps({"spreadsheetId": cached}),
                ])
                return cached
            except RuntimeError:
                pass  # Stale cache, recreate

    # Search Drive for existing sheet
    try:
        result = run_gws([
            "drive", "files", "list",
            "--params", json.dumps({
                "q": (
                    f"name='{SHEET_NAME}' "
                    "and mimeType='application/vnd.google-apps.spreadsheet' "
                    "and trashed=false"
                ),
                "fields": "files(id,name)",
            }),
        ])
        files = result.get("files", [])
        if files:
            sheet_id = files[0]["id"]
            SHEET_ID_FILE.write_text(sheet_id)
            return sheet_id
    except RuntimeError:
        pass

    # Create new sheet — include the tab name so it's created as "Leads" not "Sheet1"
    result = run_gws(
        ["sheets", "spreadsheets", "create"],
        json_body={
            "properties": {"title": SHEET_NAME},
            "sheets": [{"properties": {"title": TAB_LEADS}}],
        },
    )
    sheet_id = result["spreadsheetId"]
    SHEET_ID_FILE.write_text(sheet_id)

    # Write headers
    _write_range(sheet_id, f"{TAB_LEADS}!A1", [LEADS_HEADERS])
    print(f"Created: https://docs.google.com/spreadsheets/d/{sheet_id}")
    return sheet_id


def _write_range(sheet_id, range_notation, values):
    """Write a list of rows to a range."""
    run_gws(
        [
            "sheets", "spreadsheets", "values", "update",
            "--params", json.dumps({
                "spreadsheetId": sheet_id,
                "range": range_notation,
                "valueInputOption": "RAW",
            }),
        ],
        json_body={"values": values},
    )


def append_rows(sheet_id, rows):
    """Append rows to the Leads tab."""
    if not rows:
        return
    run_gws(
        [
            "sheets", "spreadsheets", "values", "append",
            "--params", json.dumps({
                "spreadsheetId": sheet_id,
                "range": f"{TAB_LEADS}!A1",
                "valueInputOption": "RAW",
                "insertDataOption": "INSERT_ROWS",
            }),
        ],
        json_body={"values": rows},
    )


def read_all_rows(sheet_id):
    """Read all data rows from the Leads tab. Returns list of dicts with '_row' key."""
    result = run_gws([
        "sheets", "spreadsheets", "values", "get",
        "--params", json.dumps({
            "spreadsheetId": sheet_id,
            "range": f"{TAB_LEADS}!A:Z",
        }),
    ])
    values = result.get("values", [])
    if len(values) < 2:
        return []
    headers = values[0]
    rows = []
    for i, row in enumerate(values[1:], start=2):
        padded = row + [""] * (len(headers) - len(row))
        d = dict(zip(headers, padded))
        d["_row"] = i
        rows.append(d)
    return rows


def update_cell(sheet_id, row_number, col_name, value):
    """Update a single cell by 1-based row number and column name."""
    ltr = col_letter(col_index(col_name))
    run_gws(
        [
            "sheets", "spreadsheets", "values", "update",
            "--params", json.dumps({
                "spreadsheetId": sheet_id,
                "range": f"{TAB_LEADS}!{ltr}{row_number}",
                "valueInputOption": "RAW",
            }),
        ],
        json_body={"values": [[value]]},
    )


def col_index(col_name):
    """Return 0-based column index for a header name."""
    return LEADS_HEADERS.index(col_name)


def col_letter(idx):
    """Convert 0-based column index to spreadsheet letter (0→A, 25→Z, 26→AA)."""
    result = ""
    idx += 1
    while idx:
        idx, rem = divmod(idx - 1, 26)
        result = chr(65 + rem) + result
    return result

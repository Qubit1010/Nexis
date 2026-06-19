"""Google Sheets access via the gws CLI (Windows-friendly, no gspread).

Ported from the lead-gen push scripts because that invocation pattern already
works on Aleem's machine: it calls `node run.js` directly to dodge cmd.exe's
8191-char limit when appending batches of rows.

Everything here is channel-agnostic plumbing. Channel-specific column logic
lives in channels.py; the orchestration lives in push.py.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path


# ---------------------------------------------------------------------------
# Locate + run the gws CLI
# ---------------------------------------------------------------------------

def _find_gws():
    npm_dir = Path(os.environ.get("APPDATA", "")) / "npm"
    for js_name in ("run.js", "run-gws.js"):
        gws_js = npm_dir / "node_modules" / "@googleworkspace" / "cli" / js_name
        if gws_js.exists():
            for candidate in [
                npm_dir / "node.exe",
                Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "nodejs" / "node.exe",
                Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "nodejs" / "node.exe",
            ]:
                if candidate.exists():
                    return ([str(candidate), str(gws_js)], False)
            node = shutil.which("node")
            if node:
                return ([node, str(gws_js)], False)
    gws = shutil.which("gws")
    if gws:
        return ([gws], True)
    gws_cmd = npm_dir / "gws.cmd"
    if gws_cmd.exists():
        return ([str(gws_cmd)], True)
    return (["gws"], True)


_GWS_CMD, _GWS_SHELL = _find_gws()


def run_gws(args, json_body=None):
    """Run a gws command and return parsed JSON (or {} / {"raw": ...})."""
    cmd = _GWS_CMD + args
    if json_body is not None:
        cmd += ["--json", json.dumps(json_body)]
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=120,
        shell=_GWS_SHELL, encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "gws error")
    stdout = result.stdout.strip()
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"raw": stdout}


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def read_values(sheet_id, rng):
    """Return all rows in a range (or whole tab if rng is just a tab name)."""
    try:
        data = run_gws([
            "sheets", "spreadsheets", "values", "get",
            "--params", json.dumps({"spreadsheetId": sheet_id, "range": rng}),
        ])
        return data.get("values", [])
    except RuntimeError as e:
        print(f"  ERROR reading {sheet_id} [{rng}]: {e}", flush=True)
        return []


def get_metadata(sheet_id):
    return run_gws([
        "sheets", "spreadsheets", "get",
        "--params", json.dumps({"spreadsheetId": sheet_id}),
    ])


def get_gid(sheet_id, tab):
    """Resolve a tab title to its numeric sheetId (gid). None if not found."""
    meta = get_metadata(sheet_id)
    for sh in meta.get("sheets", []):
        props = sh.get("properties", {})
        if props.get("title", "").strip().lower() == tab.strip().lower():
            return props.get("sheetId")
    return None


def first_tab_title(sheet_id):
    meta = get_metadata(sheet_id)
    sheets = meta.get("sheets", [])
    if sheets:
        return sheets[0].get("properties", {}).get("title", "Sheet1")
    return "Sheet1"


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

def col_letter(idx0):
    """0-based column index -> A1 letter (handles columns past Z)."""
    s = ""
    n = idx0 + 1
    while n:
        n, rem = divmod(n - 1, 26)
        s = chr(65 + rem) + s
    return s


def update_column(sheet_id, tab, col_letter_str, start_row, values):
    """Write a list of single values down one column from start_row (1-based)."""
    if not values:
        return True
    end_row = start_row + len(values) - 1
    range_str = f"{tab}!{col_letter_str}{start_row}:{col_letter_str}{end_row}"
    try:
        run_gws(
            ["sheets", "spreadsheets", "values", "update",
             "--params", json.dumps({
                 "spreadsheetId": sheet_id,
                 "range": range_str,
                 "valueInputOption": "RAW",
             })],
            json_body={"values": [[v] for v in values]},
        )
        return True
    except RuntimeError as e:
        print(f"  ERROR updating column {col_letter_str}: {e}", flush=True)
        return False


def append_rows(sheet_id, tab, rows, batch_size=10):
    """Append rows (list of lists) in small batches to stay under CLI limits."""
    if not rows:
        return True
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        try:
            run_gws(
                ["sheets", "spreadsheets", "values", "append",
                 "--params", json.dumps({
                     "spreadsheetId": sheet_id,
                     "range": f"{tab}!A1",
                     "valueInputOption": "RAW",
                     "insertDataOption": "INSERT_ROWS",
                 })],
                json_body={"values": batch},
            )
        except RuntimeError as e:
            print(f"  ERROR appending batch {i // batch_size + 1}: {e}", flush=True)
            return False
    return True


def delete_rows(sheet_id, gid, row_indices_1based, batch_size=25):
    """Delete rows by 1-based index. Reverse order so indices don't shift."""
    requests = []
    for row_1based in sorted(set(row_indices_1based), reverse=True):
        row_0based = row_1based - 1
        requests.append({
            "deleteDimension": {
                "range": {
                    "sheetId": gid,
                    "dimension": "ROWS",
                    "startIndex": row_0based,
                    "endIndex": row_0based + 1,
                }
            }
        })
    for i in range(0, len(requests), batch_size):
        batch = requests[i:i + batch_size]
        run_gws(
            ["sheets", "spreadsheets", "batchUpdate",
             "--params", json.dumps({"spreadsheetId": sheet_id})],
            json_body={"requests": batch},
        )
        print(f"  deleted {min(i + batch_size, len(requests))}/{len(requests)}", flush=True)


# ---------------------------------------------------------------------------
# Header helpers
# ---------------------------------------------------------------------------

def header_index(header_row, names):
    """Return the index of the first header in `names` (case-insensitive), or None."""
    wanted = {n.strip().lower() for n in names}
    for i, h in enumerate(header_row):
        if h.strip().lower() in wanted:
            return i
    return None

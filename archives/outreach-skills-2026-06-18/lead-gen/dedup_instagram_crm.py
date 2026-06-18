"""Deduplicate Instagram Outreach CRM by username and URL.

Reads the CRM sheet, finds duplicate rows (by username or extracted handle),
removes junk /popular/ explore-page entries, and deletes them.
Keeps the first occurrence of each real profile.

Usage:
  python dedup_instagram_crm.py           # live run
  python dedup_instagram_crm.py --dry-run # preview without deleting
"""

import json
import os
import re
import shutil
import subprocess
import sys

CRM_SHEET_ID = "1xql6icDspoJxzP1_vIQpjqBWK1RYQBN1C8N28OzkGs8"
CRM_TAB = "Leads"
SHEET_GID = 731597620  # gid from sheet URL


# ---------------------------------------------------------------------------
# gws helpers (same pattern as instagram_push.py)
# ---------------------------------------------------------------------------

def _find_gws():
    npm_dir = os.path.join(os.environ.get("APPDATA", ""), "npm")
    for js_name in ("run.js", "run-gws.js"):
        gws_js = os.path.join(npm_dir, "node_modules", "@googleworkspace", "cli", js_name)
        if os.path.exists(gws_js):
            for candidate in [
                os.path.join(npm_dir, "node.exe"),
                os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "nodejs", "node.exe"),
                os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "nodejs", "node.exe"),
            ]:
                if os.path.exists(candidate):
                    return ([candidate, gws_js], False)
            node = shutil.which("node")
            if node:
                return ([node, gws_js], False)
    gws = shutil.which("gws")
    if gws:
        return ([gws], True)
    gws_cmd = os.path.join(npm_dir, "gws.cmd")
    if os.path.exists(gws_cmd):
        return ([gws_cmd], True)
    return (["gws"], True)


_GWS_CMD, _GWS_SHELL = _find_gws()


def _run_gws(args, json_body=None):
    cmd = _GWS_CMD + args
    if json_body is not None:
        cmd += ["--json", json.dumps(json_body)]
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=120,
        shell=_GWS_SHELL, encoding="utf-8", errors="replace"
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


def _read_sheet():
    data = _run_gws([
        "sheets", "spreadsheets", "values", "get",
        "--params", json.dumps({"spreadsheetId": CRM_SHEET_ID, "range": CRM_TAB})
    ])
    return data.get("values", [])


def _delete_rows(row_indices_1based: list[int]):
    """Delete rows by 1-based sheet index.

    Sends requests in reverse order so earlier deletions don't shift
    subsequent row indices within the same batch.
    """
    sorted_indices = sorted(row_indices_1based, reverse=True)

    requests = []
    for row_1based in sorted_indices:
        row_0based = row_1based - 1
        requests.append({
            "deleteDimension": {
                "range": {
                    "sheetId": SHEET_GID,
                    "dimension": "ROWS",
                    "startIndex": row_0based,
                    "endIndex": row_0based + 1,
                }
            }
        })

    batch_size = 25
    for i in range(0, len(requests), batch_size):
        batch = requests[i:i + batch_size]
        _run_gws(
            ["sheets", "spreadsheets", "batchUpdate",
             "--params", json.dumps({"spreadsheetId": CRM_SHEET_ID})],
            json_body={"requests": batch},
        )
        print(f"  Deleted rows {i + 1}-{min(i + batch_size, len(requests))} of {len(requests)}", flush=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _extract_handle(url: str) -> str:
    """Extract Instagram handle from a URL. Returns '' if not a real profile URL."""
    url = url.strip().lower()
    m = re.match(r"https?://[^/]*instagram\.com/([^/?#]+)", url)
    if not m:
        return ""
    handle = m.group(1).rstrip("/")
    # Skip Instagram system paths — these are explore/popular pages, not profiles
    if handle in ("popular", "p", "tv", "reel", "reels", "explore", "stories", "live"):
        return ""
    return handle


def _is_junk_url(url: str) -> bool:
    """True if the URL is an Instagram explore/popular page, not a real profile."""
    url = url.strip().lower()
    return bool(re.search(r"instagram\.com/popular/", url))


def main():
    dry_run = "--dry-run" in sys.argv

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if dry_run:
        print("[DRY RUN] No rows will be deleted.\n")

    print("Reading CRM sheet...", flush=True)
    all_rows = _read_sheet()

    if not all_rows or len(all_rows) < 2:
        print("Sheet is empty or has only headers.")
        return

    header = all_rows[0]
    data_rows = all_rows[1:]
    print(f"Total rows in sheet: {len(data_rows)}", flush=True)

    # Locate columns
    username_col = next((i for i, h in enumerate(header) if h.strip().lower() == "username"), 1)
    url_col      = next((i for i, h in enumerate(header) if h.strip().lower() in ("instagram url", "instagram", "url")), 4)
    name_col     = next((i for i, h in enumerate(header) if h.strip().lower() == "name"), 0)

    seen_handles: dict[str, int] = {}  # handle → first row_1based
    to_remove: list[tuple[int, str, str, str]] = []  # (row_1based, label, handle, reason)

    for i, row in enumerate(data_rows):
        row_1based = i + 2

        def _get(col):
            return row[col].strip() if col < len(row) else ""

        username = _get(username_col)
        url      = _get(url_col)
        name     = _get(name_col)

        # Junk: Instagram /popular/ explore pages
        if _is_junk_url(url) or _is_junk_url(name):
            label = name[:60] or url[:60]
            to_remove.append((row_1based, label, "", "junk /popular/ explore page"))
            continue

        # Resolve handle: prefer @username column, fall back to extracting from URL or Name
        handle = username.lower().lstrip("@").strip()
        if not handle:
            handle = _extract_handle(url) or _extract_handle(name)

        if not handle:
            continue  # can't identify — skip

        if handle in seen_handles:
            label = f"{name} ({username})" if name and username else name or username or url[:40]
            to_remove.append((row_1based, label, handle, f"dup of row {seen_handles[handle]}"))
        else:
            seen_handles[handle] = row_1based

    junk_count = sum(1 for r in to_remove if "junk" in r[3])
    dup_count  = len(to_remove) - junk_count
    print(f"Junk entries (explore pages): {junk_count}", flush=True)
    print(f"Duplicate profiles:           {dup_count}", flush=True)
    print(f"Total to remove:              {len(to_remove)}", flush=True)

    if not to_remove:
        print("Sheet is clean.")
        return

    print("\nRows to remove:")
    for row_idx, label, handle, reason in to_remove:
        handle_str = f"@{handle}" if handle else ""
        print(f"  Row {row_idx:>4}: {label[:55]:<57} {handle_str:<30} | {reason}")

    if dry_run:
        print(f"\n[DRY RUN] Would delete {len(to_remove)} rows.")
        return

    print(f"\nDeleting {len(to_remove)} rows...", flush=True)
    _delete_rows([r[0] for r in to_remove])
    print(f"\nDone. {len(to_remove)} rows removed ({junk_count} junk + {dup_count} duplicates).")
    print(f"Sheet: https://docs.google.com/spreadsheets/d/{CRM_SHEET_ID}")


if __name__ == "__main__":
    main()

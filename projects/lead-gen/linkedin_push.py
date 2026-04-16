"""LinkedIn Sheet Push — Filter, generate Touch 1 message, export to CRM.

Reads manually scraped LinkedIn leads from a source Google Sheet, applies
quality filters, generates a connection note for each kept lead, and
appends directly to the LinkedIn Outreach CRM.

Filters applied:
  - Skip duplicates already in the CRM (matched by LinkedIn URL)
  - Skip if followers < 100
  - Skip if location is South Asian (Pakistan, India, etc.)

Usage:
  python linkedin_push.py           # live run
  python linkedin_push.py --dry-run # preview without writing
"""

import argparse
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from transformers.linkedin_transformer import generate_connection_note

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SOURCE_SHEET_ID = "1NpBUSFEgofelZ_BZjs6F3IQiOa34MIvLdDUtv1Ebw5Q"
SOURCE_TAB      = "Raw"

CRM_SHEET_ID    = "1rJM42Hd1kh8G4d3MGIO1SMILSyM86iU5nSD7QQTdOoo"
CRM_TAB         = "Leads"

MIN_FOLLOWERS   = 100

SOUTH_ASIA_KEYWORDS = [
    "pakistan", "india", "bangladesh", "sri lanka", "nepal",
    "bhutan", "maldives", "afghanistan",
    "karachi", "lahore", "islamabad", "rawalpindi", "faisalabad",
    "mumbai", "delhi", "bangalore", "bengaluru", "chennai",
    "hyderabad", "pune", "ahmedabad", "kolkata",
    "dhaka", "colombo", "kathmandu",
]

# ---------------------------------------------------------------------------
# Column aliases — maps source sheet header variants to canonical field name
# ---------------------------------------------------------------------------

_COL_ALIASES = {
    # Name
    "name":                      "full_name",
    "full name":                 "full_name",
    "first name":                "first_name",
    "firstname":                 "first_name",
    "last name":                 "last_name",
    "lastname":                  "last_name",

    # Title
    "title":                     "title",
    "position":                  "title",
    "headline":                  "title",
    "job title":                 "title",
    "occupation":                "title",
    "role":                      "title",
    "designation":               "title",

    # Company
    "company":                   "company",
    "company name":              "company",
    "organization":              "company",
    "current company":           "company",

    # Location
    "location":                  "location",
    "city":                      "location",
    "country":                   "location",
    "region":                    "location",

    # Followers / connections
    "followers":                 "followers",
    "connections":               "followers",
    "number of connections":     "followers",
    "follower count":            "followers",
    "linkedin followers":        "followers",

    # LinkedIn URL
    "linkedin url":              "linkedin_url",
    "linkedin profile url":      "linkedin_url",
    "profile url":               "linkedin_url",
    "linkedin":                  "linkedin_url",
    "url":                       "linkedin_url",
    "profile link":              "linkedin_url",
    "link":                      "linkedin_url",

    # Industry
    "industry":                  "industry",
}

# ---------------------------------------------------------------------------
# gws helpers (same pattern as exporters/gws_exporter.py)
# ---------------------------------------------------------------------------

def _find_gws():
    import os
    npm_dir = Path(os.environ.get("APPDATA", "")) / "npm"
    gws_js = npm_dir / "node_modules" / "@googleworkspace" / "cli" / "run-gws.js"
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


def _run_gws(args: list, json_body: dict = None) -> dict:
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


def _read_sheet(sheet_id: str, tab: str) -> list[list]:
    """Return all rows from a sheet tab as list of lists."""
    try:
        data = _run_gws([
            "sheets", "spreadsheets", "values", "get",
            "--params", json.dumps({"spreadsheetId": sheet_id, "range": tab})
        ])
        return data.get("values", [])
    except RuntimeError as e:
        print(f"  ERROR reading sheet {sheet_id} tab {tab}: {e}", flush=True)
        return []


def _update_column(sheet_id: str, tab: str, col_letter: str, start_row: int, values: list) -> bool:
    """Write a list of values to a single column starting at start_row (1-based)."""
    if not values:
        return True
    end_row = start_row + len(values) - 1
    range_str = f"{tab}!{col_letter}{start_row}:{col_letter}{end_row}"
    try:
        _run_gws(
            ["sheets", "spreadsheets", "values", "update",
             "--params", json.dumps({
                 "spreadsheetId": sheet_id,
                 "range": range_str,
                 "valueInputOption": "RAW",
             })],
            json_body={"values": [[v] for v in values]}
        )
        return True
    except RuntimeError as e:
        print(f"  ERROR updating column {col_letter}: {e}", flush=True)
        return False


def _append_rows(sheet_id: str, tab: str, rows: list[list], batch_size: int = 10) -> bool:
    """Append rows to a sheet tab in batches to avoid Windows CLI length limits."""
    if not rows:
        return True
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        try:
            _run_gws(
                ["sheets", "spreadsheets", "values", "append",
                 "--params", json.dumps({
                     "spreadsheetId": sheet_id,
                     "range": f"{tab}!A1",
                     "valueInputOption": "RAW",
                     "insertDataOption": "INSERT_ROWS"
                 })],
                json_body={"values": batch}
            )
        except RuntimeError as e:
            print(f"  ERROR appending batch {i//batch_size + 1}: {e}", flush=True)
            return False
    return True

# ---------------------------------------------------------------------------
# Column parsing
# ---------------------------------------------------------------------------

def _build_col_map(header_row: list) -> dict:
    """Return {canonical_field: column_index} from header row."""
    col_map = {}
    for i, cell in enumerate(header_row):
        key = cell.strip().lower()
        canonical = _COL_ALIASES.get(key)
        if canonical and canonical not in col_map:
            col_map[canonical] = i
    return col_map


def _get(row: list, col_map: dict, field: str, default: str = "") -> str:
    idx = col_map.get(field)
    if idx is None or idx >= len(row):
        return default
    return row[idx].strip()

# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------

def _is_south_asia(location: str) -> bool:
    loc = location.lower()
    return any(kw in loc for kw in SOUTH_ASIA_KEYWORDS)


def _parse_followers(raw: str) -> int | None:
    """Parse follower count from strings like '1,234', '500+', '1.2K', etc."""
    if not raw:
        return None
    cleaned = raw.strip().lower().replace(",", "").replace("+", "").replace(" ", "")
    # Handle '1.2k', '500', etc.
    if cleaned.endswith("k"):
        try:
            return int(float(cleaned[:-1]) * 1000)
        except ValueError:
            return None
    try:
        return int(float(cleaned))
    except ValueError:
        return None


def _normalize_linkedin_url(url: str) -> str:
    """Normalize LinkedIn URL for dedup comparison."""
    url = url.strip().lower().rstrip("/")
    # Remove tracking params
    if "?" in url:
        url = url.split("?")[0]
    return url

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LinkedIn Sheet Push")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing to CRM")
    args = parser.parse_args()

    dry_run = args.dry_run
    if dry_run:
        print("[DRY RUN] No changes will be written.\n")

    # 1. Read source sheet
    print(f"Reading source sheet: {SOURCE_SHEET_ID} | Tab: {SOURCE_TAB}", flush=True)
    source_rows = _read_sheet(SOURCE_SHEET_ID, SOURCE_TAB)
    if not source_rows:
        print("No data found in source sheet. Exiting.")
        sys.exit(1)

    header = source_rows[0]
    data_rows = source_rows[1:]
    col_map = _build_col_map(header)
    print(f"  Source rows: {len(data_rows)}", flush=True)

    # Find "Include to CRM" column for writeback (convert 0-based index → A1 letter)
    include_col_idx = None
    for i, h in enumerate(header):
        if h.strip().lower() in ("include to crm", "include", "include in crm"):
            include_col_idx = i
            break
    include_col_letter = None
    existing_include_values = {}  # {row_idx: current cell value}
    if include_col_idx is not None:
        include_col_letter = chr(ord("A") + include_col_idx)  # works for A-Z
        # Read existing values so we can preserve "Added" from prior runs
        for i, row in enumerate(data_rows):
            val = row[include_col_idx].strip() if include_col_idx < len(row) else ""
            existing_include_values[i] = val

    # Warn if key columns are missing
    for field in ("full_name", "linkedin_url"):
        if field not in col_map and (field == "full_name" and "first_name" not in col_map):
            print(f"  WARNING: No '{field}' column found in source sheet.", flush=True)

    # 2. Read existing CRM to build dedup set
    print(f"Reading CRM sheet for dedup: {CRM_SHEET_ID} | Tab: {CRM_TAB}", flush=True)
    crm_rows = _read_sheet(CRM_SHEET_ID, CRM_TAB)
    existing_urls: set[str] = set()
    if crm_rows and len(crm_rows) > 1:
        crm_header = crm_rows[0]
        # LinkedIn URL is column index 4 in the CRM (0-indexed)
        # CRM columns: Name | First Name | Company | Role | LinkedIn URL | ...
        li_idx = None
        for i, h in enumerate(crm_header):
            if h.strip().lower() in ("linkedin url", "linkedin profile url", "linkedin", "url"):
                li_idx = i
                break
        if li_idx is None:
            li_idx = 4  # fallback to position

        for row in crm_rows[1:]:
            if li_idx < len(row) and row[li_idx].strip():
                existing_urls.add(_normalize_linkedin_url(row[li_idx]))

    print(f"  Existing CRM entries: {len(existing_urls)}", flush=True)

    # 3. Process each source row
    kept_rows = []
    stats = {"kept": 0, "dup": 0, "low_followers": 0, "south_asia": 0, "blank": 0}
    # writeback[i] = status string for source row i (0-based data index)
    writeback = {}

    for row_idx, row in enumerate(data_rows):
        # Skip blank rows
        if not any(cell.strip() for cell in row):
            stats["blank"] += 1
            writeback[row_idx] = ""
            continue

        # Parse fields
        first_name  = _get(row, col_map, "first_name")
        last_name   = _get(row, col_map, "last_name")
        full_name   = _get(row, col_map, "full_name") or f"{first_name} {last_name}".strip()
        title       = _get(row, col_map, "title")
        company     = _get(row, col_map, "company")
        location    = _get(row, col_map, "location")
        followers   = _get(row, col_map, "followers")
        linkedin_url = _get(row, col_map, "linkedin_url")
        industry    = _get(row, col_map, "industry")

        # Skip blank name + no LinkedIn URL
        if not full_name.strip() and not linkedin_url.strip():
            stats["blank"] += 1
            writeback[row_idx] = ""
            continue

        # Filter: duplicate
        if linkedin_url:
            normalized = _normalize_linkedin_url(linkedin_url)
            if normalized in existing_urls:
                stats["dup"] += 1
                writeback[row_idx] = "Dropped - Duplicate"
                continue

        # Filter: low followers
        if followers:
            count = _parse_followers(followers)
            if count is not None and count < MIN_FOLLOWERS:
                stats["low_followers"] += 1
                writeback[row_idx] = "Dropped - Low Followers"
                continue

        # Filter: South Asian location
        if location and _is_south_asia(location):
            stats["south_asia"] += 1
            writeback[row_idx] = "Dropped - South Asia"
            continue

        # Build lead dict for message generation
        lead = {
            "first_name": first_name or (full_name.split()[0] if full_name else ""),
            "title":      title,
            "company":    company,
            "industry":   industry,
            "company_size": "",
        }

        # Generate connection note — GPT-4o-mini with deterministic fallback
        connection_note = generate_connection_note(lead, personalization={})

        # Build CRM row — exact LinkedIn CRM column order (13 columns):
        # Name | First Name | Company | Role | LinkedIn URL | Location | Recent Post |
        # Touch 1 Message | Touch 2 Message | Touch 3 Message | Touch 4 Message | Status | Date Added
        crm_row = [
            full_name,
            first_name or (full_name.split()[0] if full_name else ""),
            company,
            title,
            linkedin_url,
            location,
            "",                          # Recent Post
            connection_note,             # Touch 1 Message
            "",                          # Touch 2 Message
            "",                          # Touch 3 Message
            "",                          # Touch 4 Message
            "New",                       # Status
            date.today().isoformat(),    # Date Added
        ]

        kept_rows.append(crm_row)
        writeback[row_idx] = "Added"
        stats["kept"] += 1

        # Add to dedup set so same-run duplicates are also caught
        if linkedin_url:
            existing_urls.add(_normalize_linkedin_url(linkedin_url))

    # 4. Summary
    print(f"\n--- Filter Results ---")
    print(f"  Kept:           {stats['kept']}")
    print(f"  Duplicate:      {stats['dup']}")
    print(f"  Low followers:  {stats['low_followers']} (< {MIN_FOLLOWERS})")
    print(f"  South Asia:     {stats['south_asia']}")
    print(f"  Blank/skipped:  {stats['blank']}")

    if not kept_rows:
        print("\nNothing to push.")

    # Dry run preview
    if dry_run:
        if kept_rows:
            print(f"\n[DRY RUN] Would append {len(kept_rows)} rows to CRM. Sample:")
            for row in kept_rows[:5]:
                name, _, company, role, url, loc, _, msg, *_ = row
                print(f"  {name} @ {company} [{role}]")
                print(f"    URL: {url}")
                print(f"    Msg ({len(msg)} chars): {msg[:80]}...")
        return

    # 5. Append to CRM (skip if nothing to push)
    if kept_rows:
        print(f"\nAppending {len(kept_rows)} rows to LinkedIn CRM...", flush=True)
        success = _append_rows(CRM_SHEET_ID, CRM_TAB, kept_rows)
        if success:
            print(f"Done. {len(kept_rows)} leads added to LinkedIn CRM.")
        else:
            print("Failed to write to CRM sheet.")
            sys.exit(1)

    # 6. Write back status to source sheet "Include to CRM" column
    if include_col_letter:
        print(f"\nWriting status back to source sheet column {include_col_letter}...", flush=True)
        # Never overwrite a finalised status — only write to empty cells
        # (or update to "Added" when the current run actually added it)
        col_values = []
        for i in range(len(data_rows)):
            existing = existing_include_values.get(i, "")
            new_val = writeback.get(i, "")
            if new_val == "Added":
                col_values.append(new_val)      # always stamp Added
            elif existing:
                col_values.append(existing)     # preserve prior status
            else:
                col_values.append(new_val)      # fill empty cell
        _update_column(SOURCE_SHEET_ID, SOURCE_TAB, include_col_letter, 2, col_values)
        print("  Done.", flush=True)
    else:
        print("\n  WARNING: 'Include to CRM' column not found in source sheet — skipping writeback.", flush=True)


def refresh_touch1(dry_run: bool = False) -> None:
    """Regenerate Touch 1 messages for all 'New' leads in the CRM using GPT-4o-mini.

    CRM column layout (0-indexed):
      0: Name | 1: First Name | 2: Company | 3: Role | 4: LinkedIn URL |
      5: Location | 6: Recent Post | 7: Touch 1 Message | 8-10: Touch 2-4 |
      11: Status | 12: Date Added
    """
    from transformers.linkedin_transformer import generate_connection_note

    print(f"Reading CRM: {CRM_SHEET_ID} | Tab: {CRM_TAB}", flush=True)
    crm_rows = _read_sheet(CRM_SHEET_ID, CRM_TAB)
    if not crm_rows or len(crm_rows) < 2:
        print("CRM is empty.")
        return

    header = crm_rows[0]
    data_rows = crm_rows[1:]

    # Resolve column indices from header (fall back to positional defaults)
    def _col(names: list[str], default: int) -> int:
        for i, h in enumerate(header):
            if h.strip().lower() in names:
                return i
        return default

    touch1_col_idx = _col(["touch 1 message", "touch1 message", "touch 1"], 7)
    status_col_idx = _col(["status"], 11)
    touch1_col_letter = chr(ord("A") + touch1_col_idx)

    print(f"Touch 1 column: {touch1_col_letter} (index {touch1_col_idx})", flush=True)

    new_touch1_values = []
    updated = 0

    for row in data_rows:
        status = row[status_col_idx].strip() if status_col_idx < len(row) else ""
        current_msg = row[touch1_col_idx].strip() if touch1_col_idx < len(row) else ""

        if status != "New":
            new_touch1_values.append(current_msg)
            continue

        first_name = row[1].strip() if len(row) > 1 else ""
        company    = row[2].strip() if len(row) > 2 else ""
        title      = row[3].strip() if len(row) > 3 else ""
        industry   = ""  # not stored in CRM; GPT will work with name+title+company

        lead = {
            "first_name": first_name,
            "title":      title,
            "company":    company,
            "industry":   industry,
            "company_size": "",
        }

        note = generate_connection_note(lead, personalization={})
        new_touch1_values.append(note)
        updated += 1

        if dry_run:
            print(f"  [DRY RUN] {first_name} @ {company} [{title}]")
            print(f"    Old: {current_msg[:80]}")
            print(f"    New: {note[:80]}")
        else:
            print(f"  Refreshed: {first_name} @ {company}".encode("ascii", "replace").decode(), flush=True)

    print(f"\n{updated} leads refreshed.", flush=True)

    if dry_run or updated == 0:
        return

    print(f"Writing updated Touch 1 messages to column {touch1_col_letter}...", flush=True)
    batch_size = 20
    for i in range(0, len(new_touch1_values), batch_size):
        batch = new_touch1_values[i:i + batch_size]
        _update_column(CRM_SHEET_ID, CRM_TAB, touch1_col_letter, 2 + i, batch)
        print(f"  Wrote rows {2 + i}–{2 + i + len(batch) - 1}", flush=True)
    print("Done.", flush=True)


if __name__ == "__main__":
    if "--refresh-touch1" in sys.argv:
        dry_run = "--dry-run" in sys.argv
        refresh_touch1(dry_run=dry_run)
    else:
        main()

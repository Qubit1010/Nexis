"""Instagram Sheet Push — Filter, generate Touch 1 DM, export to CRM.

Reads manually scraped Instagram leads from a source Google Sheet, applies
quality filters, generates a Touch 1 DM for each kept lead, and
appends directly to the Instagram Outreach CRM.

Filters applied:
  - Skip duplicates already in the CRM (matched by Instagram URL or username)
  - Skip if followers < 100
  - Skip if location is South Asian (Pakistan, India, etc.)

Usage:
  python instagram_push.py           # live run
  python instagram_push.py --dry-run # preview without writing
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from transformers.instagram_transformer import generate_touch1_dm

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SOURCE_SHEET_ID = "1kOEaNhwD3fsbpAJM6l6-dR0z6n06xgJyyWr3EHKmzyg"
SOURCE_TAB      = "Raw"

CRM_SHEET_ID    = "1xql6icDspoJxzP1_vIQpjqBWK1RYQBN1C8N28OzkGs8"
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
    "name":                  "full_name",
    "full name":             "full_name",

    # Instagram URL
    "link":                  "instagram_url",
    "instagram url":         "instagram_url",
    "instagram":             "instagram_url",
    "url":                   "instagram_url",
    "profile url":           "instagram_url",
    "profile link":          "instagram_url",

    # Followers
    "followers":             "followers",
    "follower count":        "followers",

    # Bio
    "note":                  "bio",
    "bio":                   "bio",
    "notes":                 "bio",

    # Title / designation (combined location/designation field)
    "location/designation":  "title",
    "designation":           "title",
    "title":                 "title",
    "role":                  "title",
    "position":              "title",

    # Location (if separate)
    "location":              "location",

    # Company
    "company":               "company",
    "company name":          "company",

    # Username (if separate column)
    "username":              "username",
}

# ---------------------------------------------------------------------------
# gws helpers (same pattern as linkedin_push.py)
# ---------------------------------------------------------------------------

def _find_gws():
    import os
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
    """Parse follower count from strings like '1,234', '500+', '24.8K+', etc."""
    if not raw:
        return None
    cleaned = raw.strip().lower().replace(",", "").replace("+", "").replace(" ", "")
    if cleaned.endswith("k"):
        try:
            return int(float(cleaned[:-1]) * 1000)
        except ValueError:
            return None
    try:
        return int(float(cleaned))
    except ValueError:
        return None


def _normalize_instagram_url(url: str) -> str:
    """Normalize Instagram URL for dedup comparison."""
    url = url.strip().lower().rstrip("/")
    if "?" in url:
        url = url.split("?")[0]
    return url


_BUSINESS_WORDS = {
    "agency", "marketing", "digital", "studio", "media", "group",
    "llc", "inc", "ltd", "co", "services", "solutions", "consulting",
    "design", "creative", "brand", "brands", "ventures", "labs",
    "tech", "technologies", "management", "productions", "collective",
}

def _extract_first_name(clean_name: str) -> str:
    """Return a person first name from a clean name, or '' if it looks like a business."""
    if not clean_name:
        return ""
    # Strip anything after | or - (e.g. "Gill Valerio | Digital Marketing")
    base = re.split(r'\s*[|\-–]\s*', clean_name)[0].strip()
    words = base.split()
    if not words:
        return ""
    # If any word (lowercased) is a known business word, skip the name
    lower_words = {w.lower().rstrip(".,") for w in words}
    if lower_words & _BUSINESS_WORDS:
        return ""
    # If more than 3 words and no business word, still likely not a person name
    if len(words) > 3:
        return ""
    first = words[0]
    # All-caps or all-lowercase first word = brand/acronym, not a person name
    if first == first.upper() and len(first) > 1:
        return ""
    if not first[0].isupper():
        return ""
    return first


def _parse_name_and_username(raw_name: str) -> tuple[str, str]:
    """Extract clean name and @username from 'Name (@handle)' format.

    Returns: (clean_name, username_with_at)
    """
    match = re.search(r'\(@([^)]+)\)', raw_name)
    username = "@" + match.group(1) if match else ""
    clean_name = re.sub(r'\s*\(@[^)]+\)', '', raw_name).strip()
    return clean_name, username

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Instagram Sheet Push")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing to CRM")
    args = parser.parse_args()

    dry_run = args.dry_run

    # Reconfigure stdout to handle emoji/unicode in lead data on Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

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
    print(f"  Detected columns: {list(col_map.keys())}", flush=True)

    # Find "Include to CRM" column for writeback (col letter for A-Z range)
    include_col_idx = None
    for i, h in enumerate(header):
        if h.strip().lower() in ("include to crm", "include", "include in crm"):
            include_col_idx = i
            break
    include_col_letter = None
    existing_include_values = {}  # {row_idx: current cell value}
    if include_col_idx is not None:
        include_col_letter = chr(ord("A") + include_col_idx)
        # Read existing values so we can preserve "Added" from prior runs
        for i, row in enumerate(data_rows):
            val = row[include_col_idx].strip() if include_col_idx < len(row) else ""
            existing_include_values[i] = val

    # 2. Read existing CRM to build dedup sets
    print(f"Reading CRM sheet for dedup: {CRM_SHEET_ID} | Tab: {CRM_TAB}", flush=True)
    crm_rows = _read_sheet(CRM_SHEET_ID, CRM_TAB)
    existing_urls: set[str] = set()
    existing_usernames: set[str] = set()

    if crm_rows and len(crm_rows) > 1:
        crm_header = crm_rows[0]
        # CRM columns: Name | Username | Company | Role | Instagram URL | ...
        url_idx = None
        uname_idx = None
        for i, h in enumerate(crm_header):
            h_lower = h.strip().lower()
            if h_lower in ("instagram url", "instagram", "url", "link") and url_idx is None:
                url_idx = i
            if h_lower in ("username",) and uname_idx is None:
                uname_idx = i
        if url_idx is None:
            url_idx = 4   # fallback: col E (0-indexed)
        if uname_idx is None:
            uname_idx = 1  # fallback: col B (0-indexed)

        for row in crm_rows[1:]:
            if url_idx < len(row) and row[url_idx].strip():
                existing_urls.add(_normalize_instagram_url(row[url_idx]))
            if uname_idx < len(row) and row[uname_idx].strip():
                existing_usernames.add(row[uname_idx].strip().lower().lstrip("@"))

    print(f"  Existing CRM URLs: {len(existing_urls)} | Usernames: {len(existing_usernames)}", flush=True)

    # 3. Process each source row
    kept_rows = []
    stats = {"kept": 0, "dup": 0, "low_followers": 0, "south_asia": 0, "blank": 0}
    writeback = {}  # {row_idx: status string}

    for row_idx, row in enumerate(data_rows):
        # Skip blank rows
        if not any(cell.strip() for cell in row):
            stats["blank"] += 1
            writeback[row_idx] = ""
            continue

        # Parse fields
        raw_name       = _get(row, col_map, "full_name")
        instagram_url  = _get(row, col_map, "instagram_url")
        followers_raw  = _get(row, col_map, "followers")
        bio            = _get(row, col_map, "bio")
        title          = _get(row, col_map, "title")
        location       = _get(row, col_map, "location") or title  # title col often has location too
        company        = _get(row, col_map, "company")
        username_col   = _get(row, col_map, "username")  # if there's a dedicated username column

        # Parse name and username from "Name (@handle)" format
        clean_name, username = _parse_name_and_username(raw_name)
        if not username and username_col:
            username = username_col if username_col.startswith("@") else "@" + username_col

        first_name = _extract_first_name(clean_name)

        # Skip blank name + no URL
        if not clean_name.strip() and not instagram_url.strip():
            stats["blank"] += 1
            writeback[row_idx] = ""
            continue

        # Filter: duplicate by URL
        if instagram_url:
            normalized = _normalize_instagram_url(instagram_url)
            if normalized in existing_urls:
                stats["dup"] += 1
                writeback[row_idx] = "Dropped - Duplicate"
                continue

        # Filter: duplicate by username
        if username:
            uname_clean = username.lstrip("@").lower()
            if uname_clean in existing_usernames:
                stats["dup"] += 1
                writeback[row_idx] = "Dropped - Duplicate"
                continue

        # Filter: low followers
        if followers_raw:
            count = _parse_followers(followers_raw)
            if count is not None and count < MIN_FOLLOWERS:
                stats["low_followers"] += 1
                writeback[row_idx] = "Dropped - Low Followers"
                continue

        # Filter: South Asian location/designation
        check_loc = location or title
        if check_loc and _is_south_asia(check_loc):
            stats["south_asia"] += 1
            writeback[row_idx] = "Dropped - South Asia"
            continue

        # Build lead dict for DM generation
        lead = {
            "first_name": first_name,
            "title":      title,
            "company":    company,
            "bio":        bio,
        }

        touch1_dm = generate_touch1_dm(lead)

        # Build CRM row — exact Instagram CRM column order (13 columns):
        # Name | Username | Company | Role | Instagram URL | Followers |
        # Bio | Touch 1 Message | Touch 2 Message | Touch 3 Message | Touch 4 Message | Status | Date Added
        crm_row = [
            clean_name,
            username,
            company,
            title,
            instagram_url,
            followers_raw,
            bio,
            touch1_dm,
            "",                          # Touch 2 Message
            "",                          # Touch 3 Message
            "",                          # Touch 4 Message
            "New",                       # Status
            date.today().isoformat(),    # Date Added
        ]

        kept_rows.append(crm_row)
        writeback[row_idx] = "Added"
        stats["kept"] += 1

        # Add to dedup sets so same-run duplicates are also caught
        if instagram_url:
            existing_urls.add(_normalize_instagram_url(instagram_url))
        if username:
            existing_usernames.add(username.lstrip("@").lower())

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
                name, uname, company, role, url, followers, bio, msg, *_ = row
                print(f"  {name} {uname} @ {company} [{role}]")
                print(f"    URL: {url} | Followers: {followers}")
                print(f"    DM ({len(msg)} chars): {msg[:100]}")
        return

    # 5. Append to CRM (skip if nothing to push)
    if kept_rows:
        print(f"\nAppending {len(kept_rows)} rows to Instagram CRM...", flush=True)
        success = _append_rows(CRM_SHEET_ID, CRM_TAB, kept_rows)
        if success:
            print(f"Done. {len(kept_rows)} leads added to Instagram CRM.")
        else:
            print("Failed to write to CRM sheet.")
            sys.exit(1)

    # 6. Write back status to source sheet "Include to CRM" column
    if include_col_letter:
        print(f"\nWriting status back to source sheet column {include_col_letter}...", flush=True)
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
    """Regenerate Touch 1 DMs for all 'New' leads in the Instagram CRM using GPT-4o-mini.

    CRM column layout (0-indexed):
      0: Name | 1: Username | 2: Company | 3: Role | 4: Instagram URL |
      5: Followers | 6: Bio | 7: Touch 1 Message | 8-10: Touch 2-4 |
      11: Status | 12: Date Added
    """
    from transformers.instagram_transformer import generate_touch1_dm

    print(f"Reading CRM: {CRM_SHEET_ID} | Tab: {CRM_TAB}", flush=True)
    crm_rows = _read_sheet(CRM_SHEET_ID, CRM_TAB)
    if not crm_rows or len(crm_rows) < 2:
        print("CRM is empty.")
        return

    header = crm_rows[0]
    data_rows = crm_rows[1:]

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

        first_name = _extract_first_name(row[0].strip()) if len(row) > 0 else ""
        company    = row[2].strip() if len(row) > 2 else ""
        title      = row[3].strip() if len(row) > 3 else ""
        bio        = row[6].strip() if len(row) > 6 else ""

        lead = {
            "first_name": first_name,
            "title":      title,
            "company":    company,
            "bio":        bio,
        }

        dm = generate_touch1_dm(lead)
        new_touch1_values.append(dm)
        updated += 1

        if dry_run:
            print(f"  [DRY RUN] {first_name} @ {company}")
            print(f"    Old: {current_msg[:80]}")
            print(f"    New: {dm[:80]}")
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
        print(f"  Wrote rows {2 + i}-{2 + i + len(batch) - 1}", flush=True)
    print("Done.", flush=True)


if __name__ == "__main__":
    if "--refresh-touch1" in sys.argv:
        dry_run = "--dry-run" in sys.argv
        refresh_touch1(dry_run=dry_run)
    else:
        main()

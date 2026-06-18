"""Google Sheets lead importer.

Reads from a manually-curated Google Sheet where each row is a lead.
Filters to rows where Include == "Yes" (case-insensitive).
Maps LinkedIn export column names to the standard lead dict schema.

Sheet format (LinkedIn export style):
  First Name | Last Name | Title | Company | Email | LinkedIn URL |
  Company Website | Industry | Company Size | Location | Include

Usage:
  python main.py import --source sheets
  python main.py import --source sheets --sheet-id <SHEET_ID>
  python main.py import --source sheets --dry-run
"""

import json
import subprocess
import sys
from datetime import date


# ---------------------------------------------------------------------------
# Column name aliases (maps sheet header variants -> canonical field)
# ---------------------------------------------------------------------------

_COL_ALIASES = {
    # Name
    "first name":                "first_name",
    "firstname":                 "first_name",
    "last name":                 "last_name",
    "lastname":                  "last_name",
    "full name":                 "full_name",
    "name":                      "full_name",

    # Title
    "title":                     "title",
    "position":                  "title",
    "job title":                 "title",
    "role":                      "title",

    # Company
    "company":                   "company",
    "company name":              "company",
    "organization":              "company",

    # Contact
    "email":                     "email",
    "email address":             "email",
    "work email":                "email",
    "linkedin url":              "linkedin_url",
    "linkedin profile url":      "linkedin_url",
    "linkedin":                  "linkedin_url",
    "profile url":               "linkedin_url",

    # Website
    "company website":           "company_website",
    "website":                   "company_website",
    "website url":               "company_website",
    "url":                       "company_website",

    # Firmographics
    "industry":                  "industry",
    "company size":              "company_size",
    "employees":                 "company_size",
    "company employees":         "company_size",
    "location":                  "location",
    "country":                   "location",
    "city":                      "location",

    # Filter column
    "include":                   "__include",
}


def _read_sheet(sheet_id: str, tab: str) -> list[list]:
    """Read all values from a Google Sheet tab via gws CLI.
    Returns a list of rows (each row is a list of cell strings).
    """
    params = json.dumps({"spreadsheetId": sheet_id, "range": tab})
    cmd = ["gws", "sheets", "spreadsheets", "values", "get",
           "--params", params]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"  ERROR: gws returned non-zero exit: {result.stderr.strip()}", flush=True)
            return []
        data = json.loads(result.stdout)
        return data.get("values", [])
    except subprocess.TimeoutExpired:
        print("  ERROR: gws timed out reading sheet.", flush=True)
        return []
    except json.JSONDecodeError as e:
        print(f"  ERROR: Could not parse gws response: {e}", flush=True)
        return []


def _build_col_map(header_row: list) -> dict:
    """Return {canonical_field: column_index} from the header row."""
    col_map = {}
    for i, cell in enumerate(header_row):
        key = cell.strip().lower()
        canonical = _COL_ALIASES.get(key)
        if canonical and canonical not in col_map:
            col_map[canonical] = i
    return col_map


def _row_to_lead(row: list, col_map: dict) -> dict:
    """Map a data row to a lead dict using the column map."""
    def get(field):
        idx = col_map.get(field)
        if idx is None or idx >= len(row):
            return ""
        return row[idx].strip()

    first_name = get("first_name")
    last_name = get("last_name")
    full_name = get("full_name") or f"{first_name} {last_name}".strip()

    return {
        "first_name":     first_name,
        "last_name":      last_name,
        "full_name":      full_name,
        "title":          get("title"),
        "company":        get("company"),
        "email":          get("email"),
        "linkedin_url":   get("linkedin_url"),
        "company_website": get("company_website"),
        "industry":       get("industry"),
        "company_size":   get("company_size"),
        "location":       get("location"),
        "source":         "sheets_import",
        "date_discovered": date.today().isoformat(),
    }


def run(sheet_id: str = None, tab: str = None, dry_run: bool = False) -> list[dict]:
    """Read leads from Google Sheet, filter by Include == 'Yes', return lead dicts.

    Args:
        sheet_id: Google Sheet ID (overrides config). Required if not set in config.
        tab: Sheet tab name. Defaults to config value or 'Sheet1'.
        dry_run: If True, print what would be imported without returning rows.

    Returns:
        List of lead dicts ready for DB insertion.
    """
    from config import DISCOVERY

    # Resolve sheet ID
    resolved_id = sheet_id or DISCOVERY.get("input_sheet_id", "")
    if not resolved_id:
        print("  ERROR: No sheet ID provided. Pass --sheet-id or set input_sheet_id in config.py.", flush=True)
        return []

    # Resolve tab
    resolved_tab = tab or DISCOVERY.get("input_sheet_tab", "Sheet1")
    include_col_name = DISCOVERY.get("include_column", "Include")
    include_value = DISCOVERY.get("include_value", "yes").lower()

    print(f"  Reading sheet: {resolved_id} | Tab: {resolved_tab}", flush=True)

    rows = _read_sheet(resolved_id, resolved_tab)
    if not rows:
        print("  No data found in sheet.", flush=True)
        return []

    header = rows[0]
    data_rows = rows[1:]
    col_map = _build_col_map(header)

    if "__include" not in col_map:
        print(f"  WARNING: '{include_col_name}' column not found. Importing all rows.", flush=True)
        include_all = True
    else:
        include_all = False

    leads = []
    skipped = 0

    for row in data_rows:
        # Skip blank rows
        if not any(cell.strip() for cell in row):
            continue

        # Apply Include filter
        if not include_all:
            idx = col_map["__include"]
            val = row[idx].strip().lower() if idx < len(row) else ""
            if val != include_value:
                skipped += 1
                continue

        lead = _row_to_lead(row, col_map)

        # Skip rows with no name and no company
        if not lead["full_name"].strip() and not lead["company"].strip():
            skipped += 1
            continue

        leads.append(lead)

    print(f"  Rows parsed: {len(data_rows)} | Included: {len(leads)} | Skipped: {skipped}", flush=True)

    if dry_run:
        print("\n  [DRY RUN] Sample leads:")
        for lead in leads[:5]:
            name = lead.get("full_name") or lead.get("first_name", "?")
            company = lead.get("company", "?")
            email = lead.get("email", "")
            linkedin = lead.get("linkedin_url", "")
            print(f"    {name} @ {company} | email={email or '-'} | li={linkedin or '-'}", flush=True)
        return []

    return leads

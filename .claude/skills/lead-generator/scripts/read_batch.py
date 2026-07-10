"""Reads the next batch of unprocessed businesses from an "Instant Google Maps Data" sheet
(Aleem's manual Instant Data Scraper output), applying two cleanup rules before handing rows
to the agent for WebSearch resolution:

  - Phone: keep only if it starts with "+" (a real country code). Bare local-format numbers
    ("0322 9966458") are almost always Pakistani/Indian junk from this data source, per
    Aleem's own example, and get blanked rather than passed downstream.
  - Geo exclusion: drop the row entirely if its Experience/Company text matches leads-to-crm's
    own SOUTH_ASIA list (push.py) -- confirmed live on the real sheet, which already mixes an
    Islamabad-based agency into a San Diego batch. Caught here, before spending a WebSearch
    call resolving socials for a lead that would get filtered downstream anyway.

Resume-safe: appends a "Social Search Status" column (if missing) and skips any row already
marked, so re-running the same sheet only surfaces new rows.

Usage:
  python read_batch.py --sheet-id <id> --tab <tab-name> --limit 10
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "leads-to-crm" / "scripts"))
import sheets  # noqa: E402

STATUS_HEADER = "Social Search Status"

# Same list leads-to-crm's push.py already excludes downstream (SOUTH_ASIA) -- reused here so
# a bad-geography lead never gets a WebSearch call spent on it in the first place.
SOUTH_ASIA = [
    "pakistan", "india", "bangladesh", "sri lanka", "nepal", "karachi", "lahore",
    "islamabad", "mumbai", "delhi", "bangalore", "bengaluru", "chennai", "hyderabad",
    "pune", "kolkata", "dhaka", "colombo",
]

HEADER_ALIASES = {
    "company name": "company", "business name": "company", "name": "company",
    "category": "category",
    "rating": "rating",
    "experience": "experience",
    "number": "phone", "phone": "phone", "phone number": "phone",
    "note": "note", "notes": "note",
    "website link": "website", "website": "website", "url": "website",
    "google map link": "map_link",
}


def _strip_bullet(raw):
    """Instant Data Scraper prepends a middot/bullet to some cells ('· +1 619-...')."""
    return re.sub(r"^[·•\s]+", "", (raw or "").strip())


def _clean_phone(raw):
    cleaned = _strip_bullet(raw)
    return cleaned if cleaned.startswith("+") else ""


def _is_south_asia(text):
    hay = (text or "").lower()
    return any(k in hay for k in SOUTH_ASIA)


def build_col_map(header):
    col_map = {}
    for i, h in enumerate(header):
        key = HEADER_ALIASES.get(h.strip().lower())
        if key:
            col_map[key] = i
    return col_map


def cell(row, col_map, key):
    idx = col_map.get(key)
    return row[idx].strip() if idx is not None and idx < len(row) else ""


def ensure_status_column(sheet_id, tab, header):
    """Append the Social Search Status header if it isn't already there. Returns its 0-based index."""
    for i, h in enumerate(header):
        if h.strip().lower() == STATUS_HEADER.lower():
            return i
    idx = len(header)
    col = sheets.col_letter(idx)
    sheets.update_range(sheet_id, f"{tab}!{col}1", [[STATUS_HEADER]])
    return idx


def mark_status(sheet_id, tab, status_col_letter, row_num, status):
    sheets.update_range(sheet_id, f"{tab}!{status_col_letter}{row_num}", [[status]])


def next_batch(sheet_id, tab, limit):
    rows = sheets.read_values(sheet_id, tab)
    if not rows:
        raise SystemExit(f"Could not read {sheet_id} [{tab}] — check the sheet ID/tab name.")
    header = rows[0]
    col_map = build_col_map(header)
    if "company" not in col_map:
        raise SystemExit(
            f"No 'Company Name'/'Business Name'/'Name' column found in header: {header}"
        )
    status_idx = ensure_status_column(sheet_id, tab, header)
    status_letter = sheets.col_letter(status_idx)

    batch = []
    skipped_geo = 0
    for row_num, row in enumerate(rows[1:], start=2):
        if not any(c.strip() for c in row):
            continue
        status = row[status_idx].strip() if status_idx < len(row) else ""
        if status:
            continue  # already processed on a prior run

        company = cell(row, col_map, "company")
        if not company:
            continue
        experience = cell(row, col_map, "experience")

        if _is_south_asia(experience) or _is_south_asia(company):
            mark_status(sheet_id, tab, status_letter, row_num, "Skipped - geo")
            skipped_geo += 1
            continue

        batch.append({
            "row": row_num,
            "company": company,
            "category": _strip_bullet(cell(row, col_map, "category")),
            "rating": cell(row, col_map, "rating"),
            "experience": experience,
            "phone": _clean_phone(cell(row, col_map, "phone")),
            "note": cell(row, col_map, "note"),
            "website": cell(row, col_map, "website"),
        })
        if len(batch) >= limit:
            break

    return {
        "sheet_id": sheet_id,
        "tab": tab,
        "status_col": status_letter,
        "skipped_geo_this_run": skipped_geo,
        "businesses": batch,
    }


def main():
    p = argparse.ArgumentParser(description="Read the next batch of unprocessed Google Maps leads to resolve.")
    p.add_argument("--sheet-id", required=True)
    p.add_argument("--tab", required=True)
    p.add_argument("--limit", type=int, default=10)
    args = p.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    result = next_batch(args.sheet_id, args.tab, args.limit)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

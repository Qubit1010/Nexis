"""Same read/cleanup rules as read_batch.py, adapted for a consolidated "Main" lead sheet whose
header already carries its own Location column (rather than location embedded in Experience text)
and its own Instagram/LinkedIn/Facebook Link + Social Search Status columns to fill in place --
no separate leads-to-crm Instant sheet involved.

Usage:
  python read_batch_main.py --sheet-id <id> --tab Main --limit 12
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "leads-to-crm" / "scripts"))
import sheets  # noqa: E402
from read_batch import SOUTH_ASIA, _strip_bullet, _clean_phone, _is_south_asia  # noqa: E402

STATUS_HEADER = "Social Search Status"

HEADER_ALIASES = {
    "company name": "company",
    "category": "category",
    "rating": "rating",
    "experience": "experience",
    "location": "location",
    "number": "phone",
    "note": "note",
    "link": "directory_link",  # Clutch/DesignRush profile URL (no site link on the card itself)
    "website link": "website",
    "instagram link": "instagram",
    "linkedin link": "linkedin",
    "facebook link": "facebook",
    "founder": "founder",
    "founder instagram link": "founder_instagram",
    "founder linkedin link": "founder_linkedin",
    "founder facebook link": "founder_facebook",
}


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


def status_col_index(header):
    for i, h in enumerate(header):
        if h.strip().lower() == STATUS_HEADER.lower():
            return i
    raise SystemExit(f"No '{STATUS_HEADER}' column found in header: {header}")


def row_to_biz(row_num, row, col_map):
    """One Main row -> the biz dict resolve.py consumes. Existing social/founder values ride along so
    resolve fills only gaps and never re-searches a filled field."""
    insta = cell(row, col_map, "instagram")
    linkd = cell(row, col_map, "linkedin")
    fbook = cell(row, col_map, "facebook")
    return {
        "row": row_num,
        "company": cell(row, col_map, "company"),
        "category": _strip_bullet(cell(row, col_map, "category")),
        "rating": cell(row, col_map, "rating"),
        "experience": cell(row, col_map, "experience"),
        "location": cell(row, col_map, "location"),
        "phone": _clean_phone(cell(row, col_map, "phone")),
        "note": cell(row, col_map, "note"),
        "website": cell(row, col_map, "website"),
        "directory_link": cell(row, col_map, "directory_link"),
        "instagram": insta,
        "linkedin": linkd,
        "facebook": fbook,
        "founder": cell(row, col_map, "founder"),
        "founder_instagram": cell(row, col_map, "founder_instagram"),
        "founder_linkedin": cell(row, col_map, "founder_linkedin"),
        "founder_facebook": cell(row, col_map, "founder_facebook"),
    }


def next_batch(sheet_id, tab, limit):
    rows = sheets.read_values(sheet_id, tab)
    if not rows:
        raise SystemExit(f"Could not read {sheet_id} [{tab}]")
    header = rows[0]
    col_map = build_col_map(header)
    status_idx = status_col_index(header)
    status_letter = sheets.col_letter(status_idx)

    batch = []
    skipped_geo = 0
    already_has_socials = 0
    for row_num, row in enumerate(rows[1:], start=2):
        if not any(c.strip() for c in row):
            continue
        status = row[status_idx].strip() if status_idx < len(row) else ""
        if status.lower().startswith("skipped"):
            continue

        company = cell(row, col_map, "company")
        if not company:
            continue

        insta = cell(row, col_map, "instagram")
        linkd = cell(row, col_map, "linkedin")
        fbook = cell(row, col_map, "facebook")
        founder = cell(row, col_map, "founder")
        # Fully resolved already (has a company social AND founder data) -- don't re-search. A row
        # with company socials but no founder still surfaces (even if it has an old v1 "Resolved..."
        # status from before founder columns existed), so v2 can fill the founder gap.
        if (insta or linkd or fbook) and founder:
            already_has_socials += 1
            continue

        experience = cell(row, col_map, "experience")
        location = cell(row, col_map, "location")
        geo_text = f"{experience} {location}"

        if _is_south_asia(geo_text) or _is_south_asia(company):
            sheets.update_range(sheet_id, f"{tab}!{status_letter}{row_num}", [["Skipped - geo"]])
            skipped_geo += 1
            continue

        batch.append(row_to_biz(row_num, row, col_map))
        if len(batch) >= limit:
            break

    return {
        "sheet_id": sheet_id,
        "tab": tab,
        "status_col": status_letter,
        "skipped_geo_this_run": skipped_geo,
        "already_resolved_this_run": already_has_socials,
        "businesses": batch,
    }


def rows_in_range(sheet_id, tab, start_row, end_row, *, skip_status_substr=None):
    """Businesses for an explicit row range, bypassing next_batch's 'already resolved' skip -- used to
    REprocess rows that already carry (possibly wrong) data after a resolver logic change. Still applies
    geo exclusion. `skip_status_substr` makes a re-run resume-safe: pass a marker (e.g. 'v3:') and rows
    whose status already contains it are skipped, so a batch that died partway continues where it left
    off without redoing finished rows."""
    rows = sheets.read_values(sheet_id, tab)
    if not rows:
        raise SystemExit(f"Could not read {sheet_id} [{tab}]")
    header = rows[0]
    col_map = build_col_map(header)
    status_idx = status_col_index(header)

    batch, skipped_geo, skipped_done = [], 0, 0
    for row_num, row in enumerate(rows[1:], start=2):
        if row_num < start_row or row_num > end_row:
            continue
        if not any(c.strip() for c in row):
            continue
        company = cell(row, col_map, "company")
        if not company:
            continue
        status = row[status_idx].strip() if status_idx < len(row) else ""
        if skip_status_substr and skip_status_substr.lower() in status.lower():
            skipped_done += 1
            continue
        geo_text = f"{cell(row, col_map, 'experience')} {cell(row, col_map, 'location')}"
        if _is_south_asia(geo_text) or _is_south_asia(company):
            skipped_geo += 1
            continue
        batch.append(row_to_biz(row_num, row, col_map))

    return {
        "sheet_id": sheet_id, "tab": tab,
        "skipped_geo_this_run": skipped_geo,
        "already_done_this_run": skipped_done,
        "businesses": batch,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sheet-id", required=True)
    p.add_argument("--tab", required=True)
    p.add_argument("--limit", type=int, default=12)
    args = p.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print(json.dumps(next_batch(args.sheet_id, args.tab, args.limit), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

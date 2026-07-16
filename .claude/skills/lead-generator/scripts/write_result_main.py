"""Writes a resolved business back onto specific columns of its own row in the "Main" sheet
(Website Link if freshly discovered, company Instagram/LinkedIn/Facebook Link, Founder + founder
Instagram/LinkedIn/Facebook Link, Social Search Status) -- no separate Instant sheet involved,
unlike write_resolved.py.

Usage:
  python write_result_main.py --sheet-id <id> --tab Main --row 42 --status "Resolved - instagram, linkedin" \
      [--website URL] [--instagram URL] [--linkedin URL] [--facebook URL] \
      [--founder NAME] [--founder-instagram URL] [--founder-linkedin URL] [--founder-facebook URL]
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "leads-to-crm" / "scripts"))
import sheets  # noqa: E402

FIELD_HEADERS = {
    "website": "Website Link",
    "instagram": "Instagram Link",
    "linkedin": "LinkedIn Link",
    "facebook": "Facebook Link",
    "founder": "Founder",
    "founder_instagram": "Founder Instagram Link",
    "founder_linkedin": "Founder LinkedIn Link",
    "founder_facebook": "Founder Facebook Link",
}
STATUS_HEADER = "Social Search Status"


def col_letter_for(header, name):
    for i, h in enumerate(header):
        if h.strip().lower() == name.lower():
            return sheets.col_letter(i)
    raise SystemExit(f"Column '{name}' not found in header: {header}")


def ensure_columns(sheet_id, tab, header):
    """Append any missing Founder/link/status headers (mirrors read_batch.ensure_status_column) so a
    write never crashes mid-batch on a Main sheet that predates the founder columns. Returns the
    updated header list."""
    header = list(header)
    for name in list(FIELD_HEADERS.values()) + [STATUS_HEADER]:
        if not any(h.strip().lower() == name.lower() for h in header):
            col = sheets.col_letter(len(header))
            sheets.update_range(sheet_id, f"{tab}!{col}1", [[name]])
            header.append(name)
    return header


def clear_fields(sheet_id, tab, row, keys):
    """Blank specific columns on a row. write_row/write CLI can't do this -- their `if not value:
    continue` skip-if-falsy logic ignores empty-string args -- so wiping a stale/wrong value (e.g. a
    founder that failed re-verification on a reprocess) needs this direct update_range path. `keys` are
    FIELD_HEADERS keys (e.g. 'founder', 'founder_instagram')."""
    header = sheets.read_values(sheet_id, f"{tab}!1:1")[0]
    header = ensure_columns(sheet_id, tab, header)
    for key in keys:
        col = col_letter_for(header, FIELD_HEADERS[key])
        sheets.update_range(sheet_id, f"{tab}!{col}{row}", [[""]])


def write_row(sheet_id, tab, row, status, *, website=None, instagram=None, linkedin=None, facebook=None,
              founder=None, founder_instagram=None, founder_linkedin=None, founder_facebook=None):
    """Write whichever fields are given onto one Main row + set the status. Shared by the CLI (below)
    and run_batch.py, so both write through the exact same column-mapping/ensure-columns logic --
    no drift between an ad-hoc single-row write and a batch run."""
    header = sheets.read_values(sheet_id, f"{tab}!1:1")[0]
    header = ensure_columns(sheet_id, tab, header)

    updates = {
        "website": website, "instagram": instagram, "linkedin": linkedin, "facebook": facebook,
        "founder": founder, "founder_instagram": founder_instagram,
        "founder_linkedin": founder_linkedin, "founder_facebook": founder_facebook,
    }
    written = []
    for key, value in updates.items():
        if not value:
            continue
        col = col_letter_for(header, FIELD_HEADERS[key])
        sheets.update_range(sheet_id, f"{tab}!{col}{row}", [[value]])
        written.append(key)

    status_col = col_letter_for(header, STATUS_HEADER)
    sheets.update_range(sheet_id, f"{tab}!{status_col}{row}", [[status]])
    return written


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sheet-id", required=True)
    p.add_argument("--tab", required=True)
    p.add_argument("--row", type=int, required=True)
    p.add_argument("--status", required=True)
    p.add_argument("--website", default=None)
    p.add_argument("--instagram", default=None)
    p.add_argument("--linkedin", default=None)
    p.add_argument("--facebook", default=None)
    p.add_argument("--founder", default=None)
    p.add_argument("--founder-instagram", default=None)
    p.add_argument("--founder-linkedin", default=None)
    p.add_argument("--founder-facebook", default=None)
    args = p.parse_args()

    written = write_row(args.sheet_id, args.tab, args.row, args.status, website=args.website,
                        instagram=args.instagram, linkedin=args.linkedin, facebook=args.facebook,
                        founder=args.founder, founder_instagram=args.founder_instagram,
                        founder_linkedin=args.founder_linkedin, founder_facebook=args.founder_facebook)
    print(f"row {args.row}: wrote {written} + status='{args.status}'")


if __name__ == "__main__":
    main()

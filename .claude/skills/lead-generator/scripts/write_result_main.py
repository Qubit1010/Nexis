"""Writes a resolved business back onto specific columns of its own row in the "Main" sheet
(Website Link if freshly discovered, Instagram/LinkedIn/Facebook Link, Social Search Status) --
no separate Instant sheet involved, unlike write_resolved.py.

Usage:
  python write_result_main.py --sheet-id <id> --tab Main --row 42 --status "Resolved - instagram, linkedin" \
      [--website URL] [--instagram URL] [--linkedin URL] [--facebook URL]
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
}
STATUS_HEADER = "Social Search Status"


def col_letter_for(header, name):
    for i, h in enumerate(header):
        if h.strip().lower() == name.lower():
            return sheets.col_letter(i)
    raise SystemExit(f"Column '{name}' not found in header: {header}")


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
    args = p.parse_args()

    header = sheets.read_values(args.sheet_id, f"{args.tab}!1:1")[0]

    updates = {
        "website": args.website,
        "instagram": args.instagram,
        "linkedin": args.linkedin,
        "facebook": args.facebook,
    }
    for key, value in updates.items():
        if not value:
            continue
        col = col_letter_for(header, FIELD_HEADERS[key])
        sheets.update_range(args.sheet_id, f"{args.tab}!{col}{args.row}", [[value]])

    status_col = col_letter_for(header, STATUS_HEADER)
    sheets.update_range(args.sheet_id, f"{args.tab}!{status_col}{args.row}", [[args.status]])
    print(f"row {args.row}: wrote {[k for k, v in updates.items() if v]} + status='{args.status}'")


if __name__ == "__main__":
    main()

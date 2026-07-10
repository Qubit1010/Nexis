"""Given one business (from read_batch.py's output) plus whichever social profile URLs the
agent found for it via WebSearch, appends a row into each matching channel's EXISTING "Instant
X Leads" sheet and marks the source row processed. A business with no resolved channel falls
back to the Google Maps channel's own Instant sheet for email/phone outreach via its website.

The Note/Bio column each channel writes gets a combined string of Google rating + years in
business + the testimonial quote, so leads-to-crm's existing message generator (which already
treats a non-empty bio as a personalization signal, see messages.py's has_signal check) picks it
up automatically — no leads-to-crm changes needed beyond the one GoogleMapsChannel bio alias
already added.

Usage:
  python write_resolved.py --business '<json from read_batch.py>' \
      --source-sheet-id <id> --source-tab <tab> --status-col I \
      [--instagram URL] [--linkedin URL] [--facebook URL]
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sheet_writer  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "leads-to-crm" / "scripts"))
import sheets  # noqa: E402

INSTAGRAM_SHEET = "1kOEaNhwD3fsbpAJM6l6-dR0z6n06xgJyyWr3EHKmzyg"
LINKEDIN_SHEET = "1NpBUSFEgofelZ_BZjs6F3IQiOa34MIvLdDUtv1Ebw5Q"
FACEBOOK_SHEET = "1ao7_Aam6bsI6D4xk-Mfc-EM54WZYivN9petcZU2P68U"
MAPS_SHEET = "1-shiCVpIryTYKcnAfI3XQ4phHi77jP94n9r07GM6IVw"

CHANNEL_SHEETS = {
    "instagram": {
        "sheet_id": INSTAGRAM_SHEET, "tab": "Raw",
        "fields": {"Name": "company", "Link": "url", "Note": "note_full",
                   "Location/Designation": "category"},
    },
    "linkedin": {
        "sheet_id": LINKEDIN_SHEET, "tab": "Raw",
        "fields": {"Name": "company", "Link": "url", "Note": "note_full",
                   "Designation": "category", "Company Name": "company"},
    },
    "facebook": {
        "sheet_id": FACEBOOK_SHEET, "tab": "Sheet1",
        "fields": {"Name": "company", "Link": "url", "Note": "note_full",
                   "Designation": "category", "Company Name": "company"},
    },
    "google_maps": {
        "sheet_id": MAPS_SHEET, "tab": "Raw",
        "fields": {"Business Name": "company", "Category": "category", "Phone": "phone",
                   "Website": "website", "Address": "experience", "Note": "note_full"},
    },
}


def build_note(business):
    parts = []
    if business.get("rating"):
        parts.append(f"{business['rating']} Google rating")
    if business.get("experience"):
        parts.append(business["experience"])
    if business.get("note"):
        parts.append(business["note"])
    return ". ".join(p.strip() for p in parts if p.strip())


def write_channel(channel, business, url):
    cfg = CHANNEL_SHEETS[channel]
    lead = dict(business)
    lead["url"] = url
    lead["note_full"] = build_note(business)
    sheet_writer.append_qualified(cfg["sheet_id"], cfg["tab"], [lead], cfg["fields"])


LINK_HEADERS = {
    "instagram": "Instagram Link",
    "linkedin": "LinkedIn Link",
    "facebook": "Facebook Link",
}


def ensure_link_columns(sheet_id, tab, header):
    """Append the 3 per-channel link headers if missing (mirrors read_batch.py's
    ensure_status_column). Returns {channel: 0-based column index}."""
    idx = {}
    for channel, label in LINK_HEADERS.items():
        found = next((i for i, h in enumerate(header) if h.strip().lower() == label.lower()), None)
        if found is None:
            found = len(header)
            header = header + [label]
            col = sheets.col_letter(found)
            sheets.update_range(sheet_id, f"{tab}!{col}1", [[label]])
        idx[channel] = found
    return idx


def main():
    p = argparse.ArgumentParser(
        description="Write a resolved business's social profiles into the matching leads-to-crm Instant sheet(s)."
    )
    p.add_argument("--business", required=True, help="JSON string: the business dict from read_batch.py")
    p.add_argument("--instagram", default="", help="Resolved Instagram profile URL, if found")
    p.add_argument("--linkedin", default="", help="Resolved LinkedIn profile/company URL, if found")
    p.add_argument("--facebook", default="", help="Resolved Facebook page URL, if found")
    p.add_argument("--source-sheet-id", required=True)
    p.add_argument("--source-tab", required=True)
    p.add_argument("--status-col", required=True, help="Status column letter from read_batch.py, e.g. 'I'")
    args = p.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    business = json.loads(args.business)
    header = sheets.read_values(args.source_sheet_id, f"{args.source_tab}!1:1")[0]
    link_cols = ensure_link_columns(args.source_sheet_id, args.source_tab, header)

    matched = []
    found_urls = {"instagram": args.instagram, "linkedin": args.linkedin, "facebook": args.facebook}
    for channel, url in found_urls.items():
        if url:
            write_channel(channel, business, url)
            matched.append(channel)
            col = sheets.col_letter(link_cols[channel])
            sheets.update_range(
                args.source_sheet_id, f"{args.source_tab}!{col}{business['row']}", [[url]]
            )

    if matched:
        status = "Resolved - " + ",".join(matched)
    else:
        write_channel("google_maps", business, "")
        status = "Fallback - maps/email"

    sheets.update_range(
        args.source_sheet_id, f"{args.source_tab}!{args.status_col}{business['row']}", [[status]]
    )
    print(f"Row {business['row']} ({business['company']}): {status}")


if __name__ == "__main__":
    main()

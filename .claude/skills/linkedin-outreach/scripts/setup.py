"""Create the LinkedIn Outreach CRM Google Sheet.

Run once before first use:
  cd .claude/skills/linkedin-outreach
  python scripts/setup.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gws_utils import get_or_create_sheet, SHEET_NAME, LEADS_HEADERS, SHEET_ID_FILE


def main():
    print(f"Setting up '{SHEET_NAME}'...")

    # If cached sheet_id exists, confirm before recreating
    if SHEET_ID_FILE.exists():
        existing_id = SHEET_ID_FILE.read_text().strip()
        if existing_id:
            print(f"Sheet already exists: https://docs.google.com/spreadsheets/d/{existing_id}")
            print("To recreate, delete the .sheet_id file and run again.")
            return

    sheet_id = get_or_create_sheet()

    print(f"\nSheet ready: https://docs.google.com/spreadsheets/d/{sheet_id}")
    print(f"\nColumns ({len(LEADS_HEADERS)}):")
    for i, h in enumerate(LEADS_HEADERS, 1):
        print(f"  {i}. {h}")
    print("\nNext step: python scripts/scrape_leads.py --dry-run")


if __name__ == "__main__":
    main()

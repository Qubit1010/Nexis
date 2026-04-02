#!/usr/bin/env python3
"""Check Gmail inbox for replies from leads and update CRM.

Scans Gmail inbox for emails from leads in the Enriched Leads tab.
Marks matching leads as "Replied" in Google Sheets and prints a summary.

Usage:
    python check_replies.py            # check last 2 days
    python check_replies.py --days 7   # check last 7 days
"""

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gws_utils import (
    get_or_create_sheet, read_all_rows, update_cell, run_gws,
    TAB_ENRICHED, col_index, col_letter
)


def get_inbox_senders(days_back):
    """Fetch sender emails from Gmail inbox for the past N days."""
    since_date = (date.today() - timedelta(days=days_back)).strftime("%Y/%m/%d")
    query = f"in:inbox after:{since_date} -from:me"

    try:
        result = run_gws([
            "gmail", "users", "messages", "list",
            "--params", json.dumps({
                "userId": "me",
                "q": query,
                "maxResults": 100,
            })
        ])
    except RuntimeError as e:
        print(f"Failed to list inbox: {e}", file=sys.stderr)
        return {}

    messages = result.get("messages", [])
    if not messages:
        return {}

    sender_map = {}  # email -> {subject, message_id, snippet}

    for msg in messages:
        msg_id = msg.get("id", "")
        if not msg_id:
            continue

        try:
            msg_detail = run_gws([
                "gmail", "users", "messages", "get",
                "--params", json.dumps({
                    "userId": "me",
                    "id": msg_id,
                    "format": "metadata",
                    "metadataHeaders": ["From", "Subject"],
                })
            ])
        except RuntimeError:
            continue

        headers = msg_detail.get("payload", {}).get("headers", [])
        from_header = next((h["value"] for h in headers if h["name"] == "From"), "")
        subject_header = next((h["value"] for h in headers if h["name"] == "Subject"), "")
        snippet = msg_detail.get("snippet", "")

        # Extract email from "Name <email>" format
        import re
        email_match = re.search(r'[\w.+-]+@[\w.-]+\.\w+', from_header)
        if email_match:
            sender_email = email_match.group(0).lower()
            sender_map[sender_email] = {
                "subject": subject_header,
                "snippet": snippet[:100],
                "message_id": msg_id,
            }

    return sender_map


def main():
    parser = argparse.ArgumentParser(description="Check Gmail inbox for lead replies")
    parser.add_argument("--days", type=int, default=2, help="How many days back to check (default 2)")
    args = parser.parse_args()

    print("Cold Outreach — Reply Checker")
    print(f"Checking last {args.days} days of inbox...")
    print("-" * 40)

    sheet_id = get_or_create_sheet()
    print(f"CRM: https://docs.google.com/spreadsheets/d/{sheet_id}\n")

    # Get inbox senders
    print("Reading Gmail inbox...", flush=True)
    sender_map = get_inbox_senders(args.days)

    if not sender_map:
        print("No new emails in inbox.")
        sys.exit(0)

    print(f"Found {len(sender_map)} unique senders in inbox.\n")

    # Load Enriched Leads
    all_rows = read_all_rows(sheet_id, TAB_ENRICHED)
    email_col = col_index(TAB_ENRICHED, "Email")
    company_col = col_index(TAB_ENRICHED, "Company")
    status_col = col_index(TAB_ENRICHED, "Status")
    reply_date_col = col_index(TAB_ENRICHED, "Reply Date")

    today = date.today().isoformat()
    replies_found = []
    already_marked = 0

    for i, row in enumerate(all_rows):
        row_num = i + 2

        lead_email = (row[email_col] if len(row) > email_col else "").lower().strip()
        if not lead_email:
            continue

        current_status = row[status_col] if len(row) > status_col else ""
        if current_status == "Replied":
            already_marked += 1
            continue

        if lead_email in sender_map:
            company = row[company_col] if len(row) > company_col else lead_email
            reply_info = sender_map[lead_email]

            print(f"REPLY: {company} ({lead_email})")
            print(f"  Subject: {reply_info['subject']}")
            print(f"  Preview: {reply_info['snippet']}\n")

            # Update Sheets
            update_cell(sheet_id, TAB_ENRICHED, row_num, col_letter(status_col), "Replied")
            update_cell(sheet_id, TAB_ENRICHED, row_num, col_letter(reply_date_col), today)

            replies_found.append({
                "company": company,
                "email": lead_email,
                "subject": reply_info["subject"],
            })

    print("-" * 40)
    if replies_found:
        print(f"Replies found: {len(replies_found)}")
        print("\nNext step: respond manually via Gmail. Use tactical empathy.")
        print("Remember: mirror their language, no 'just following up'.")
    else:
        print("No replies from leads found in inbox.")

    print(f"\nAlready marked as Replied: {already_marked}")

    print(json.dumps({
        "status": "ok",
        "replies": len(replies_found),
        "leads": [r["company"] for r in replies_found],
        "sheet_id": sheet_id
    }))


if __name__ == "__main__":
    main()

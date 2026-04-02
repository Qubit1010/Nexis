#!/usr/bin/env python3
"""Send the 4-email cold outreach sequence via Gmail (gws) or Hostinger SMTP.

Reads Enriched Leads from the CRM, determines which email in the sequence
each lead should receive based on days elapsed, sends via the configured
senders (rotating), and updates the Sheets CRM with send dates and status.

Usage:
    python send_sequence.py              # send today's batch (50 max)
    python send_sequence.py --limit 10   # send fewer
    python send_sequence.py --dry-run    # preview without sending
    python send_sequence.py --test-to hassanaleem86@gmail.com  # send to self only

Senders (rotate automatically):
    - hassanaleem86@gmail.com       via gws CLI
    - HOSTINGER_EMAIL_1 env var     via Hostinger SMTP (smtp.hostinger.com:465)
    - HOSTINGER_EMAIL_2 env var     via Hostinger SMTP (smtp.hostinger.com:465)

Safety:
    - Never sends more than 50 emails per run
    - 30-second sleep between sends to avoid spam detection
    - Skips leads that have replied or are marked Not Interested
"""

import argparse
import imaplib
import json
import os
import smtplib
import ssl
import sys
import time
from datetime import date, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gws_utils import (
    get_or_create_sheet, read_all_rows, update_cell,
    run_gws, TAB_ENRICHED, ENRICHED_HEADERS, col_index, col_letter
)


# ---------------------------------------------------------------------------
# Sender configuration — rotate across all available senders
# ---------------------------------------------------------------------------

def build_senders():
    """Build the list of available senders."""
    senders = [{"email": "hassanaleem86@gmail.com", "type": "gws", "name": "Aleem | NexusPoint"}]
    for i in (1, 2):
        email = os.getenv(f"HOSTINGER_EMAIL_{i}", "")
        password = os.getenv(f"HOSTINGER_PASS_{i}", "")
        if email and password:
            senders.append({
                "email": email,
                "type": "smtp",
                "name": "Aleem | NexusPoint",
                "host": "smtp.hostinger.com",
                "port": 465,
                "user": email,
                "password": password,
            })
    return senders

MAX_SENDS_PER_RUN = 50
SEND_DELAY_SECONDS = 30  # between each email


# ---------------------------------------------------------------------------
# Email templates — the 4-email sequence
# Merge tags: [FIRST_NAME], [COMPANY], [INDUSTRY], [PAIN_SIGNAL]
# ---------------------------------------------------------------------------

TEMPLATES = {
    1: {
        "subject": "quick question about [COMPANY]'s workflows",
        "body": """Hey [FIRST_NAME],

I know you probably get a lot of emails like this — I'll keep it short.

It seems like [COMPANY] is scaling fast, and that usually means a few operational bottlenecks start eating your team's time.

I run NexusPoint, an AI automation agency. I'm doing free custom workflow teardowns this week for a handful of founders — I map out exactly how to automate your biggest bottleneck using tools like n8n and AI, recorded as a 5-minute Loom video.

No pitch. Just the blueprint. You can hand it to your devs or build it yourself.

Would it be a bad idea if I sent over a quick 3-question link so I know which bottleneck to look at for [COMPANY]?

Aleem
NexusPoint | AI Automation & Web Systems""",
    },
    2: {
        "subject": "re: quick question about [COMPANY]'s workflows",
        "body": """Hey [FIRST_NAME],

Wanted to share a quick example. Last month I mapped out an automation for a [INDUSTRY] company that was spending hours a week manually managing data and reporting. The teardown showed them how to cut it to near-zero with a simple n8n workflow.

Still happy to do the same for [COMPANY] if you're open to it.

Worth a look?

Aleem
NexusPoint""",
    },
    3: {
        "subject": "noticed something about [COMPANY]",
        "body": """Hey [FIRST_NAME],

[PAIN_SIGNAL_LINE]

Not pitching anything — just figured it was worth flagging since it's probably costing your team a few hours a week.

If you want, I can record a quick Loom showing exactly how to fix it. Takes me 5 minutes.

Aleem
NexusPoint""",
    },
    4: {
        "subject": "should I close your file?",
        "body": """Hey [FIRST_NAME],

It sounds like the timing isn't right or this isn't a priority for [COMPANY] right now.

No hard feelings. If you ever want a fresh set of eyes on your workflows, the offer stands.

Should I close your file, or is this worth revisiting down the line?

Aleem
NexusPoint""",
    },
}

# Days after previous email to send next one
SEND_DELAYS = {
    2: 3,   # Email 2: send 3 days after Email 1
    3: 4,   # Email 3: send 4 days after Email 2
    4: 7,   # Email 4: send 7 days after Email 3
}


# ---------------------------------------------------------------------------
# Template rendering
# ---------------------------------------------------------------------------

def render_template(template_num, lead):
    """Fill merge tags in a template for a specific lead."""
    first_name = lead.get("first_name") or lead.get("company", "there").split()[0]
    company = lead.get("company", "")
    industry = lead.get("industry", "your industry")
    pain_signal = lead.get("pain_signal", "")

    # Email 3 has a dynamic pain signal line
    pain_signal_line = (
        f"I noticed {company} might be dealing with some manual workflow overhead."
        if not pain_signal
        else pain_signal
    )

    subject = TEMPLATES[template_num]["subject"]
    body = TEMPLATES[template_num]["body"]

    replacements = {
        "[FIRST_NAME]": first_name or "there",
        "[COMPANY]": company,
        "[INDUSTRY]": industry or "your industry",
        "[PAIN_SIGNAL]": pain_signal,
        "[PAIN_SIGNAL_LINE]": pain_signal_line,
    }

    for tag, value in replacements.items():
        subject = subject.replace(tag, value)
        body = body.replace(tag, value)

    return subject, body


# ---------------------------------------------------------------------------
# Sequence logic
# ---------------------------------------------------------------------------

def parse_date(date_str):
    """Parse a date string to date object. Returns None if empty/invalid."""
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None


def get_next_email_num(row):
    """Determine which email number to send next for this lead."""
    def get(col_name):
        idx = col_index(TAB_ENRICHED, col_name)
        return row[idx] if idx >= 0 and len(row) > idx else ""

    status = get("Status")
    if status in ("Replied", "Not Interested", "Call Booked", "Unsubscribed"):
        return None  # skip

    email1_date = parse_date(get("Email 1 Date"))
    email2_date = parse_date(get("Email 2 Date"))
    email3_date = parse_date(get("Email 3 Date"))
    email4_date = parse_date(get("Email 4 Date"))

    today = date.today()

    if not email1_date:
        return 1  # haven't started yet

    if not email2_date:
        if (today - email1_date).days >= SEND_DELAYS[2]:
            return 2
        return None  # too soon

    if not email3_date:
        if (today - email2_date).days >= SEND_DELAYS[3]:
            return 3
        return None

    if not email4_date:
        if (today - email3_date).days >= SEND_DELAYS[4]:
            return 4
        return None

    return None  # sequence complete


# ---------------------------------------------------------------------------
# Send via gws or Hostinger SMTP
# ---------------------------------------------------------------------------

def send_email_smtp(sender, to_email, subject, body):
    """Send via Hostinger SMTP and save copy to Sent folder via IMAP. Returns True on success."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{sender['name']} <{sender['email']}>"
    msg["To"] = to_email
    msg.attach(MIMEText(body, "plain"))
    raw = msg.as_bytes()

    ctx = ssl.create_default_context()

    # Send
    with smtplib.SMTP_SSL(sender["host"], sender["port"], context=ctx) as s:
        s.login(sender["user"], sender["password"])
        s.sendmail(sender["email"], to_email, raw)

    # Save to Sent folder via IMAP
    try:
        with imaplib.IMAP4_SSL("imap.hostinger.com", 993) as imap:
            imap.login(sender["user"], sender["password"])
            imap.append("INBOX.Sent", "\\Seen", imaplib.Time2Internaldate(time.time()), raw)
    except Exception as e:
        print(f"    Warning: could not save to Sent folder: {e}", file=sys.stderr)

    return True


def send_email(sender, to_email, subject, body, dry_run=False):
    """Dispatch send via gws or SMTP depending on sender type. Returns True on success."""
    if dry_run:
        print(f"    [DRY RUN] Would send to {to_email} via {sender['email']}")
        print(f"    Subject: {subject}")
        return True

    try:
        if sender["type"] == "smtp":
            return send_email_smtp(sender, to_email, subject, body)
        else:
            run_gws([
                "gmail", "+send",
                "--to", to_email,
                "--subject", subject,
                "--body", body,
            ])
            return True
    except Exception as e:
        print(f"    Send failed: {e}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Send cold email sequence via Gmail or Hostinger SMTP")
    parser.add_argument("--limit", type=int, default=MAX_SENDS_PER_RUN, help="Max emails to send")
    parser.add_argument("--dry-run", action="store_true", help="Preview without sending")
    parser.add_argument("--test-to", default="", help="Send all emails to this address instead (for testing)")
    args = parser.parse_args()

    senders = build_senders()

    print("Cold Outreach — Sequence Sender")
    print(f"  Senders: {', '.join(s['email'] for s in senders)}")
    if args.dry_run:
        print("  [DRY RUN MODE — no emails will be sent]")
    if args.test_to:
        print(f"  [TEST MODE — all emails going to {args.test_to}]")
    print("-" * 40)

    sheet_id = get_or_create_sheet()
    print(f"CRM: https://docs.google.com/spreadsheets/d/{sheet_id}\n")

    all_rows = read_all_rows(sheet_id, TAB_ENRICHED)

    if not all_rows:
        print("No leads in Enriched Leads tab. Run find_emails.py first.")
        sys.exit(0)

    today = date.today().isoformat()
    sent_count = 0
    skipped_count = 0
    error_count = 0

    for i, row in enumerate(all_rows):
        if sent_count >= args.limit:
            print(f"\nReached limit of {args.limit} sends. Stopping.")
            break

        row_num = i + 2  # +2 because row 1 = header, i is 0-indexed

        def get(col_name):
            idx = col_index(TAB_ENRICHED, col_name)
            return row[idx] if idx >= 0 and len(row) > idx else ""

        email = get("Email")
        company = get("Company")
        verified = get("Verified")
        status = get("Status")

        if not email or not company:
            continue

        # Skip if status is terminal
        if status in ("Replied", "Not Interested", "Call Booked", "Unsubscribed", "No Email Found"):
            continue

        # Determine which email to send
        email_num = get_next_email_num(row)
        if email_num is None:
            skipped_count += 1
            continue

        # Build lead dict for template rendering
        lead = {
            "first_name": get("First Name"),
            "company": company,
            "industry": get("Title"),  # using Title as industry proxy if no industry col
            "pain_signal": get("Pain Signal"),
        }

        subject, body = render_template(email_num, lead)
        to = args.test_to if args.test_to else email

        sender = senders[sent_count % len(senders)]
        print(f"[{company}] Email {email_num} -> {to} (via {sender['email']})", flush=True)

        success = send_email(sender, to, subject, body, dry_run=args.dry_run)

        if success:
            sent_count += 1
            if not args.dry_run:
                # Update the relevant date column
                date_col_name = f"Email {email_num} Date"
                date_col_idx = col_index(TAB_ENRICHED, date_col_name)
                if date_col_idx >= 0:
                    update_cell(sheet_id, TAB_ENRICHED, row_num, col_letter(date_col_idx), today)

                # Mark as Enrolled on first email
                if email_num == 1:
                    enrolled_idx = col_index(TAB_ENRICHED, "Enrolled")
                    if enrolled_idx >= 0:
                        update_cell(sheet_id, TAB_ENRICHED, row_num, col_letter(enrolled_idx), "Y")

                # Update status to In Sequence
                if status != "In Sequence":
                    status_idx = col_index(TAB_ENRICHED, "Status")
                    if status_idx >= 0:
                        update_cell(sheet_id, TAB_ENRICHED, row_num, col_letter(status_idx), "In Sequence")

            # Rate limit between sends
            if sent_count < args.limit and not args.dry_run:
                print(f"  Waiting {SEND_DELAY_SECONDS}s before next send...", flush=True)
                time.sleep(SEND_DELAY_SECONDS)
        else:
            error_count += 1

    print("\n" + "-" * 40)
    print("Done.")
    print(f"  Sent:    {sent_count}")
    print(f"  Skipped: {skipped_count} (not yet due)")
    print(f"  Errors:  {error_count}")

    print(json.dumps({
        "status": "ok",
        "sent": sent_count,
        "skipped": skipped_count,
        "errors": error_count,
        "sheet_id": sheet_id
    }))


if __name__ == "__main__":
    main()

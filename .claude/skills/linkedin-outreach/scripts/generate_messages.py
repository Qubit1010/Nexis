"""Generate personalized LinkedIn connection request messages using OpenAI (ChatGPT).

Reads leads from Google Sheets, generates 300-char connection notes, writes them back.

Usage:
  python scripts/generate_messages.py               # generate for all leads without messages
  python scripts/generate_messages.py --dry-run     # preview without saving
  python scripts/generate_messages.py --overwrite   # regenerate all messages
  python scripts/generate_messages.py --limit 20    # process N leads at a time
"""

import argparse
import os
import sys
import time
from pathlib import Path

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).parent))
from gws_utils import get_or_create_sheet, read_all_rows, update_cell

# OpenAI model — gpt-4o-mini is fast, cheap, and good enough for 300-char messages
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = """\
You write LinkedIn connection request notes for Aleem Ul Hassan.

HARD LIMIT: 300 characters total — LinkedIn rejects longer notes. Count carefully.

RULES:
- Start with: Hey [FirstName],
- Use cold reading: reference something specific and observable — their recent post topic, their company
  stage, their role + industry challenge, or what their growth trajectory signals. Not generic praise.
- Apply shared identity: acknowledge the founder/operator journey they're on. Reference struggles
  or realities they'd recognize, not compliments they've heard before.
- Zero pitch, zero ask — just a genuine human reason to connect.
- Sound like someone who actually read their profile for 30 seconds, not a bot with a template.
- End naturally — no CTA, no "let me know if...", no "I'd love to chat", no "Would love to connect"
  (unless it fits naturally within the char limit).
- NO fake compliments ("Your work is truly inspiring!")
- NO generic openers ("I came across your profile and was really impressed...")

Return ONLY the connection note. No quotes. No explanation. No extra text.\
"""


def generate_message(client, lead):
    """Call OpenAI to generate a single LinkedIn connection note."""
    first_name = (
        lead.get("First Name")
        or (lead.get("Name", "").split()[0] if lead.get("Name") else "there")
    )
    company = lead.get("Company", "")
    role = lead.get("Role", "")
    recent_post = lead.get("Recent Post", "")
    location = lead.get("Location", "")

    # Build the context for this lead
    context_parts = [f"- First Name: {first_name}"]
    if company:
        context_parts.append(f"- Company: {company}")
    if role:
        context_parts.append(f"- Role: {role}")
    if location:
        context_parts.append(f"- Location: {location}")
    if recent_post:
        context_parts.append(f"- Recent post/activity: {recent_post}")
    else:
        context_parts.append("- Recent post/activity: not available")

    user_prompt = "Lead info:\n" + "\n".join(context_parts) + "\n\nWrite the connection note."

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=120,
        temperature=0.85,  # Slightly creative for variety across many leads
    )

    message = response.choices[0].message.content.strip()
    # Strip surrounding quotes if OpenAI added them
    if message.startswith('"') and message.endswith('"'):
        message = message[1:-1].strip()

    # Enforce 300-char hard limit
    if len(message) > 300:
        # Truncate at last word boundary before 297
        message = message[:297].rsplit(" ", 1)[0] + "..."

    return message


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Generate LinkedIn connection messages using OpenAI"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview generated messages without saving to sheet",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Regenerate messages for leads that already have one",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Max number of leads to process (default: 100)",
    )
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set.")
        print("Get your key from: https://platform.openai.com/api-keys")
        print("Then run: $env:OPENAI_API_KEY = 'your_key'")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    sheet_id = get_or_create_sheet()
    all_leads = read_all_rows(sheet_id)

    if not all_leads:
        print("No leads in CRM. Run scrape_leads.py first.")
        return

    # Filter leads to process
    if args.overwrite:
        to_process = [l for l in all_leads if l.get("LinkedIn URL")]
    else:
        to_process = [
            l for l in all_leads
            if l.get("LinkedIn URL") and not l.get("Connection Message", "").strip()
        ]

    if not to_process:
        print("No leads need messages generated.")
        if not args.overwrite:
            status_counts = {}
            for l in all_leads:
                s = l.get("Status", "Unknown")
                status_counts[s] = status_counts.get(s, 0) + 1
            print(f"CRM has {len(all_leads)} total leads:")
            for status, count in sorted(status_counts.items()):
                print(f"  {status}: {count}")
            print("Use --overwrite to regenerate existing messages.")
        return

    # Apply limit
    to_process = to_process[: args.limit]

    print(f"Generating messages for {len(to_process)} leads using {OPENAI_MODEL}...")
    if args.dry_run:
        print("(DRY RUN — not saving to sheet)\n")

    generated = 0
    errors = 0

    for i, lead in enumerate(to_process, 1):
        name = lead.get("Name", "Unknown")
        company = lead.get("Company", "")
        label = f"{name} @ {company}" if company else name

        try:
            message = generate_message(client, lead)
            char_count = len(message)

            if args.dry_run:
                print(f"[{i}/{len(to_process)}] {label}")
                print(f"  {char_count} chars: {message}")
                print()
            else:
                update_cell(sheet_id, lead["_row"], "Connection Message", message)
                print(f"[{i}/{len(to_process)}] {label} ({char_count} chars)")
                generated += 1

            # Avoid OpenAI rate limits
            if i < len(to_process):
                time.sleep(0.3)

        except Exception as e:
            print(f"[{i}/{len(to_process)}] ERROR — {label}: {e}")
            errors += 1
            continue

    print()
    if args.dry_run:
        print(f"Dry run complete. {len(to_process)} messages previewed.")
        print("Remove --dry-run to save them to the sheet.")
    else:
        print(f"Done. Generated: {generated} | Errors: {errors}")
        print(f"Sheet: https://docs.google.com/spreadsheets/d/{sheet_id}")
        print(
            "\nNext step: Open the sheet, review the messages, "
            "then send connection requests manually from LinkedIn."
        )
        print("Tip: Update the 'Status' column to 'Sent' as you send each one.")


if __name__ == "__main__":
    main()

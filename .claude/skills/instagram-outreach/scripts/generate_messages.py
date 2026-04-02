"""Generate personalized Instagram Touch 1 DM messages using OpenAI.

Reads leads from Google Sheets, generates personalized opening DMs,
writes them back to the sheet. Messages are reviewed and sent manually.

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

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = """\
You write personalized Instagram DM opening messages for Aleem Ul Hassan, \
co-founder of NexusPoint (an AI automation and web development agency).

Goal: Start a real conversation with a founder or business owner — not pitch them. \
This is Touch 1 of a 4-touch sequence. No pitch, no ask, no mention of NexusPoint.

Rules:
- Keep it under 300 characters (Instagram DMs should feel casual, not essay-length)
- Start with "Hey [FirstName]" or "Hey @[username]" — natural, not formal
- Reference something specific about them: their bio, what they're building, their niche, \
  or something from their recent post caption
- Include a Voss tactical empathy label: "It looks like...", "It seems like...", or \
  "It sounds like..." — use it to acknowledge what they're working on
- End with ONE genuine question about their work or business — not a sales question
- Zero pitch. Zero mention of services. Sound like a curious peer, not a vendor.
- Tone: warm, direct, human — Instagram is more casual than LinkedIn

Return ONLY the DM message. No quotes. No explanation. No extra text.\
"""


def generate_message(client, lead):
    """Call OpenAI to generate a single Instagram Touch 1 DM."""
    full_name = lead.get("Name", "")
    username = lead.get("Username", "").lstrip("@")
    first_name = full_name.split()[0] if full_name and full_name != username else username
    company = lead.get("Company", "")
    role = lead.get("Role", "")
    bio = lead.get("Bio", "")
    followers = lead.get("Followers", "")

    context_parts = [f"- Name: {first_name}"]
    if username:
        context_parts.append(f"- Instagram username: @{username}")
    if role:
        context_parts.append(f"- Role/title: {role}")
    if company:
        context_parts.append(f"- Company/brand: {company}")
    if followers:
        context_parts.append(f"- Followers: {followers}")
    if bio:
        context_parts.append(f"- Bio: {bio}")
    else:
        context_parts.append("- Bio: not available")

    user_prompt = "Lead info:\n" + "\n".join(context_parts) + "\n\nWrite the opening DM."

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=150,
        temperature=0.85,
    )

    message = response.choices[0].message.content.strip()
    if message.startswith('"') and message.endswith('"'):
        message = message[1:-1].strip()

    # Soft cap — Instagram DMs have no hard limit but long openers get ignored
    if len(message) > 400:
        message = message[:397].rsplit(" ", 1)[0] + "..."

    return message


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Generate Instagram DM messages using OpenAI"
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

    if args.overwrite:
        to_process = [l for l in all_leads if l.get("Instagram URL")]
    else:
        to_process = [
            l for l in all_leads
            if l.get("Instagram URL") and not l.get("Touch 1 Message", "").strip()
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

    to_process = to_process[: args.limit]

    print(f"Generating DMs for {len(to_process)} leads using {OPENAI_MODEL}...")
    if args.dry_run:
        print("(DRY RUN — not saving to sheet)\n")

    generated = 0
    errors = 0

    for i, lead in enumerate(to_process, 1):
        name = lead.get("Name", "Unknown")
        username = lead.get("Username", "")
        label = f"{name} ({username})" if username else name

        try:
            message = generate_message(client, lead)
            char_count = len(message)

            if args.dry_run:
                print(f"[{i}/{len(to_process)}] {label}")
                print(f"  {char_count} chars: {message}")
                print()
            else:
                update_cell(sheet_id, lead["_row"], "Touch 1 Message", message)
                print(f"[{i}/{len(to_process)}] {label} ({char_count} chars)")
                generated += 1

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
            "then send DMs manually from Instagram."
        )
        print("Tip: Update the 'Status' column to 'DM Sent T1' as you send each one.")


if __name__ == "__main__":
    main()

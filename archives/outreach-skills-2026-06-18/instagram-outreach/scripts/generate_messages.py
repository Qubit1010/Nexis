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
import random
import sys
import time
from pathlib import Path

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).parent))
from gws_utils import get_or_create_sheet, read_all_rows, update_cell

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Anti-cadence rotation: opener archetypes from sales-playbook/frameworks/opener-archetypes.md
# Instagram-specific tone: lowercase OK, contractions required, no sign-offs, 1-3 emojis MAX (often zero).
# Source: NotebookLM research synthesis (CreatorFlow IG benchmarks, Jotform templates, Josh Braun, Becc Holland).

IG_ARCHETYPE_PROMPTS = {
    "observation_specific": """\
Use the OBSERVATION (Touch 1) archetype, IG-native voice.
- Open with a SPECIFIC observation about something they posted/wrote (a reel, a post caption, a story).
- State why it caught Aleem's attention (one line).
- NO ask. NO CTA. NO mention of NexusPoint.
- Sourced example: "Hey [Name], saw the post about [specific thing]. That's the exact pattern I just helped another [niche] founder automate. Wanted to flag it. No ask."
""",
    "anti_pitch_casual": """\
Use the LAID-BACK ANTI-PITCH archetype, IG-casual.
- Open with a soft disqualifier ("probably not a fit but...", "no pitch, just...").
- Drop a specific value claim about AI workflow / hours saved for similar founders.
- Close with low-pressure curiosity.
- Sourced example: "probably not a fit but had to ask - is the manual [specific task] still on your plate or did you guys automate it already? asking because most [role] at your stage haven't and I'm trying to figure out the pattern."
""",
    "peer_pattern": """\
Use the PEER PATTERN archetype.
- Reference a pattern Aleem sees in their niche based on real conversations.
- Ask if they hit the same thing.
- NO ask for a call. Just curiosity.
- Sourced example: "every [niche] founder I've talked to this month is stuck doing [specific manual thing] by hand. wondering if you're hitting the same or if you've figured out a way around it."
""",
    "quantified_peer": """\
Use the QUANTIFIED PEER RESULT archetype.
- Lead with a specific number from a peer build (hours/week, days saved).
- Connect it to the prospect's likely pain.
- End with "same problem here?" type question.
- Sourced example: "took 12 hrs/week off another [niche] founder by wiring [tool] into [tool]. same bottleneck on your end or already solved?"
""",
}

# Banned phrases (Instagram-specific from sales-playbook/references/what-not-to-do.md Tier 4)
IG_BANNED_PHRASES_LIST = """\
- "Love your content" / "Love the shit you're doing" - #1 copy-paste tell
- "Bro" - kill on sight, especially DMing women
- "Thank you for your inquiry regarding..." - robotic
- "I came across your profile" / "I noticed you're in..."
- "Hey [Name], hope this finds you well"
- "I'd love to chat" / "Worth a quick call?" / "Open to a 15-min chat?"
- "Free money" / "Limited time offer" / "Click here" - spam triggers
- Any em-dash (-, em-dash character)
- Any formal sign-off (no "- Aleem", no "Cheers", no "Best regards")
- 3+ URLs in single DM - spam trigger
- ALL CAPS WORDS
- Excessive emojis (10+)
- Repeated punctuation (!!!)
"""

SYSTEM_PROMPT_BASE = """\
You write Instagram cold Touch 1 DMs for Aleem Ul Hassan, founder of NexusPoint.

POSITIONING (locked):
NexusPoint builds AI workflows that take manual ops work off founder/CEO plates.
Lead positioning: AI automation as premium wedge - never lead with web dev.
The one-liner (use rarely, only in archetypes that allow it): "AI workflows that take 10+ hrs/week off founder plates, usually inside 14 days."

INSTAGRAM-NATIVE VOICE:
- Lowercase OK (like real DMs)
- Contractions required (you're, I'm, here's)
- Casual peer tone - not professional, not corporate
- ZERO sign-offs (no "- Aleem", no closing)
- Under 100 words STRICT (CreatorFlow data: 30% reply drop past 200 words)
- 1-2 emojis MAX, often zero. Never 10+.
- Touch 1 has ZERO ASK. NO CTA. Just observation/question/value-drop.

ARCHETYPE FOR THIS MESSAGE:
{archetype_instruction}

UNIVERSAL RULES:
- Reference ONE specific detail about this prospect (post, caption, bio phrase)
- Sound like a real human at 11pm DMing a peer
- Max 2 instances of "I" / "we" / "my" - make it about them
- No em-dashes (use hyphens with spaces or commas)

BANNED PHRASES (instant rewrite if any appear):
{banned_phrases}

OUTPUT:
Return ONLY the DM text. No quotes. No explanation. No header. Just the message.
"""


def pick_ig_archetype(lead):
    """Pick archetype based on signal available.

    If recent post caption is available - favor observation_specific or peer_pattern.
    If only bio - fall back to anti_pitch_casual.
    """
    has_post = bool(lead.get("Recent Post") or lead.get("Recent Caption"))

    if has_post:
        return random.choices(
            ["observation_specific", "peer_pattern", "quantified_peer", "anti_pitch_casual"],
            weights=[5, 3, 2, 2],
            k=1,
        )[0]
    else:
        return random.choices(
            ["anti_pitch_casual", "peer_pattern", "quantified_peer"],
            weights=[5, 3, 2],
            k=1,
        )[0]


def build_ig_system_prompt(archetype):
    return SYSTEM_PROMPT_BASE.format(
        archetype_instruction=IG_ARCHETYPE_PROMPTS[archetype],
        banned_phrases=IG_BANNED_PHRASES_LIST,
    )


def generate_message(client, lead):
    """Call OpenAI to generate a single Instagram Touch 1 DM with rotated archetypes."""
    full_name = lead.get("Name", "")
    username = lead.get("Username", "").lstrip("@")
    first_name = full_name.split()[0] if full_name and full_name != username else username
    company = lead.get("Company", "")
    role = lead.get("Role", "")
    bio = lead.get("Bio", "")
    followers = lead.get("Followers", "")
    recent_caption = lead.get("Recent Caption") or lead.get("Recent Post", "")

    archetype = pick_ig_archetype(lead)
    system_prompt = build_ig_system_prompt(archetype)

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
    if recent_caption:
        context_parts.append(f"- Recent post/caption: {recent_caption}")
    else:
        context_parts.append("- Recent post/caption: not available")

    user_prompt = "Lead info:\n" + "\n".join(context_parts) + "\n\nWrite the opening DM following the archetype instructions."

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=180,
        temperature=0.9,
    )

    message = response.choices[0].message.content.strip()
    if message.startswith('"') and message.endswith('"'):
        message = message[1:-1].strip()

    # Strip em-dashes (banned per what-not-to-do.md)
    message = message.replace("—", " - ").replace("–", " - ")

    # Soft cap — IG data: 30% reply drop past 200 words (~1200 chars)
    if len(message) > 500:
        message = message[:497].rsplit(" ", 1)[0] + "..."

    return message, archetype


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
    parser.add_argument(
        "--date-filter",
        type=str,
        default=None,
        metavar="YYYY-MM-DD",
        help="Only regenerate leads added on this date (overrides --overwrite filter for that date)",
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

    if args.date_filter:
        to_process = [
            l for l in all_leads
            if l.get("Instagram URL") and l.get("Date Added", "").startswith(args.date_filter)
        ]
        print(f"Date filter: {args.date_filter} — found {len(to_process)} leads")
    elif args.overwrite:
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
            message, archetype = generate_message(client, lead)
            char_count = len(message)

            if args.dry_run:
                print(f"[{i}/{len(to_process)}] {label} [{archetype}]")
                print(f"  {char_count} chars: {message}")
                print()
            else:
                update_cell(sheet_id, lead["_row"], "Touch 1 Message", message)
                print(f"[{i}/{len(to_process)}] {label} [{archetype}] ({char_count} chars)")
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

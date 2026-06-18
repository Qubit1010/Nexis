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
import random
import sys
import time
from pathlib import Path

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).parent))
from gws_utils import get_or_create_sheet, read_all_rows, update_cell

# OpenAI model — gpt-4o-mini is fast, cheap, and good enough for 300-char messages
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Anti-cadence rotation: 5 documented opener archetypes from sales-playbook/frameworks/opener-archetypes.md
# Each prospect gets ONE archetype based on available signal. Never use the same archetype twice
# back-to-back. Source: NotebookLM research (Justin Welsh, Becc Holland, Josh Braun, Outbound Squad).

ARCHETYPE_PROMPTS = {
    "trigger_zero_ask": """\
Use the TRIGGER-AWARE ZERO-ASK archetype (Justin Welsh's documented passive DM).
- Reference a SPECIFIC recent trigger from their profile (post, hire, funding, launch)
- Congratulate or react genuinely
- State Aleem's one-line credibility (AI automation founder, Pakistan-based)
- ZERO ask. ZERO pitch. End on a "following from over here" type close.
- Sourced example: "Congrats on the recent round, [Name]. I'm a healthcare technology veteran (ZocDoc/PatientPop) and love what you're doing. Following you all from way over here in Los Angeles."
""",
    "specific_signal_peer": """\
Use the SPECIFIC SIGNAL + NAMED PEER archetype (Becc Holland's trigger-aware Day 0).
- Reference a SPECIFIC trigger event
- Connect it to a problem Aleem solves (manual ops, AI workflows)
- Reference a peer result generically (since we don't have real names yet): e.g., "took 12+ hrs/week off a similar founder"
- VARY THE CLOSE - pick ONE of these phrasings at random, do not default to the first:
   a) "Worth a 12-min call Tuesday or Thursday?"
   b) "Worth comparing notes?"
   c) "Mind if I send you the build playbook? No demo needed."
   d) "Open to swapping notes briefly next week?"
   e) "Want me to walk you through how it was wired? Loom or live, your call."
   f) [no close — end on the proof statement, let curiosity pull them]
- Sourced example: "[Name] - saw [specific trigger] yesterday. Companies hitting that milestone in [segment] typically face [specific pain] inside 60 days. [Peer 1] and [Peer 2] solved it with [outcome]. Worth comparing notes?"
""",
    "no_pitch_connection": """\
Use the NO-PITCH CONNECTION REQUEST archetype (highest-converting LinkedIn note format).
- Reference their post or recent activity with specificity
- State what pattern you see in similar teams
- End EXPLICITLY with "No pitch." or "Not pitching."
- Sourced example: "Hi [name], came across your post on [topic], the point about [specific detail] matched what I'm seeing with [similar company type] teams. Would be useful to be connected. No pitch."
""",
    "anti_pitch": """\
Use the LAID-BACK ANTI-PITCH archetype (Josh Braun).
- Open with a disqualifier ("Probably not a fit but had to ask...")
- Drop a specific value claim (AI workflow, 10+ hrs/week saved)
- Close with low-pressure curiosity ("Not sure if it's a fit but figured I'd flag it")
- Sourced example: "We show info product creators like yourself a lesser-known approach to reach salespeople who miss your posts on LinkedIn, ultimately driving more sales of your guide. Not sure if it's a fit, but I thought you might be interested."
""",
    "post_connection_question": """\
Use the POST-CONNECTION GENUINE QUESTION archetype.
- Open with "Thanks for connecting" or "Appreciate the connect"
- Ask ONE specific operational question about their stack/workflow
- Reference a pattern Aleem sees in similar [role]s
- NO CTA. NO pitch. Just a peer question.
- Sourced example: "Thanks for connecting, [first name]. Genuine question: how is your team handling [specific operational problem] right now? I keep running into [similar role] who are doing X but say Y is still broken. Curious where you've landed."
""",
}

# Banned phrases (from sales-playbook/references/what-not-to-do.md, Tier 1-3 cadence-smell)
BANNED_PHRASES_LIST = """\
- "Hey [Name], hope this finds you well"
- "I came across your profile"
- "I noticed you're in [industry]"
- "Love your content" / "Love the shit you're doing"
- "Your work is truly inspiring"
- "I'd love to learn more about your business"
- "Just following up" / "circling back" / "bumping this"
- "Did I catch you at a bad time?"
- "How are you today?"
- "I know you're busy, but..."
- "Let me know..." / "I'd be happy to..."
- "Does that make sense?"
- "We are the #1 provider..."
- "Worth a quick chat?" / "Open to a 15-min call?" / "Hop on a quick call"
- Any em-dash (—)
- Any formal sign-off ("Best regards," / "Cheers,")
- "Bro" (kill on sight)
"""

SYSTEM_PROMPT_BASE = """\
You write LinkedIn cold outreach for Aleem Ul Hassan, founder of NexusPoint.

POSITIONING (locked):
NexusPoint builds AI workflows that take manual ops work off founder/CEO plates.
The lead one-liner: "AI workflows that take the manual ops work off founder plates — 10+ hours per week back, usually inside 14 days."
Never lead with web dev. Web is the upsell, not the wedge.

HARD CONSTRAINT: 280-character maximum (LinkedIn caps at 300; leave buffer). Count carefully.

ARCHETYPE FOR THIS MESSAGE:
{archetype_instruction}

UNIVERSAL RULES (apply on top of archetype):
- Reference at least one SPECIFIC detail about this prospect — not generic ("you're scaling" applies to everyone, "your post about [exact topic]" is specific).
- Sound like a real human wrote it at 11pm to a peer — not a tool generating 30 messages.
- No more than 2 instances of "I" / "we" / "my" / "our" — make it about them.
- No emojis.
- No em-dashes (—). Use hyphens with spaces ( - ) or commas.
- Aleem is Pakistan-based (PKT timezone). Don't fake American slang.

BANNED PHRASES (instant rewrite if any appear):
{banned_phrases}

OUTPUT:
Return ONLY the connection note text. No quotes. No explanation. No "Here is the note:". Just the message.
"""


def pick_archetype(lead):
    """Select archetype based on available signal for this prospect.

    Logic (per sales-playbook/frameworks/opener-archetypes.md rotation rules):
    - If recent post available → favor specific_signal_peer or no_pitch_connection
    - If limited signal → favor anti_pitch (works with minimal data)
    - Always include some trigger_zero_ask variety
    - post_connection_question is reserved for DM responder, not for cold connection notes here
    """
    has_post = bool(lead.get("Recent Post"))

    if has_post:
        # Weight toward signal-using archetypes
        return random.choices(
            ["specific_signal_peer", "no_pitch_connection", "anti_pitch", "trigger_zero_ask"],
            weights=[4, 4, 2, 2],
            k=1,
        )[0]
    else:
        # No post signal — fall back to archetypes that work with minimal data
        return random.choices(
            ["anti_pitch", "trigger_zero_ask", "specific_signal_peer"],
            weights=[5, 3, 2],
            k=1,
        )[0]


def build_system_prompt(archetype):
    """Inject the archetype-specific instruction into the base prompt."""
    return SYSTEM_PROMPT_BASE.format(
        archetype_instruction=ARCHETYPE_PROMPTS[archetype],
        banned_phrases=BANNED_PHRASES_LIST,
    )


def generate_message(client, lead):
    """Call OpenAI to generate a single LinkedIn connection note using rotated archetypes."""
    first_name = (
        lead.get("First Name")
        or (lead.get("Name", "").split()[0] if lead.get("Name") else "there")
    )
    company = lead.get("Company", "")
    role = lead.get("Role", "")
    recent_post = lead.get("Recent Post", "")
    location = lead.get("Location", "")

    archetype = pick_archetype(lead)
    system_prompt = build_system_prompt(archetype)

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

    user_prompt = "Lead info:\n" + "\n".join(context_parts) + "\n\nWrite the connection note following the archetype instructions."

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=120,
        temperature=0.9,  # Higher temp for archetype variety
    )

    message = response.choices[0].message.content.strip()
    if message.startswith('"') and message.endswith('"'):
        message = message[1:-1].strip()

    # Strip em-dashes (banned per what-not-to-do.md)
    message = message.replace("—", " - ").replace("–", " - ")

    # Enforce 300-char hard limit
    if len(message) > 300:
        message = message[:297].rsplit(" ", 1)[0] + "..."

    return message, archetype


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
            message, archetype = generate_message(client, lead)
            char_count = len(message)

            if args.dry_run:
                print(f"[{i}/{len(to_process)}] {label} [{archetype}]")
                print(f"  {char_count} chars: {message}")
                print()
            else:
                update_cell(sheet_id, lead["_row"], "Connection Message", message)
                print(f"[{i}/{len(to_process)}] {label} [{archetype}] ({char_count} chars)")
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

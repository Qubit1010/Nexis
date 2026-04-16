"""Instagram outreach sequence transformer.

Generates:
  - Pre-DM engagement strategy (like, comment, story reply before DM)
  - 4-DM sequence using Voss tactical empathy

Principles:
  - Never pitch in first 3 touches
  - Voss labels: "It looks like...", "It seems like...", "It sounds like..."
  - Casual Instagram tone — not business email language
  - Pre-engagement builds familiarity before the cold DM
  - Only generated for HOT tier leads with confirmed instagram_url
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _generate_touch1_dm_gpt(lead: dict) -> str | None:
    """Generate a personalized Touch 1 DM via GPT-4o-mini.

    Returns the message string, or None if the API call fails.
    """
    try:
        from openai import OpenAI
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parent.parent / ".env")
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            return None
        client = OpenAI(api_key=api_key)

        first_name = (lead.get("first_name") or "").strip()
        title = (lead.get("title") or "").strip()
        company = (lead.get("company") or "").strip()
        bio = (lead.get("bio") or "").strip()

        context_parts = []
        if bio:
            context_parts.append(f"Bio: {bio[:150]}")
        if title:
            context_parts.append(f"Title: {title}")
        if company:
            context_parts.append(f"Company: {company}")
        context = "\n".join(context_parts) if context_parts else "No additional context."

        prompt = f"""Write a cold Instagram DM to this person:

Name: {first_name}
{context}

Rules:
- Casual Instagram tone, not business email language
- Start with: Hey {first_name} -
- One specific observation about their work, content, or bio (1 sentence) — rooted in what's visible, not generic praise
- End with ONE open question that invites a reply (not a pitch)
- No CTA, no services mention, no ask to book a call
- Max 200 characters total
- No emojis, no symbols

Output ONLY the message. No quotes, no explanation."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            temperature=0.9,
        )
        note = response.choices[0].message.content.strip().replace("\n", " ").replace("  ", " ")
        return note[:200] if note else None
    except Exception:
        return None


def generate_touch1_dm(lead: dict) -> str:
    """Generate a standalone Touch 1 DM for cold Instagram outreach.

    Tries GPT-4o-mini first, falls back to templates if unavailable.
    """
    gpt_dm = _generate_touch1_dm_gpt(lead)
    if gpt_dm:
        return gpt_dm

    first_name = (lead.get("first_name") or "").strip()
    company = (lead.get("company") or "").strip()
    bio = (lead.get("bio") or "").strip()

    greeting = f"Hey {first_name}" if first_name else "Hey"

    if bio:
        snippet = bio[:80].rstrip("., ")
        return f'{greeting} - saw your bio: "{snippet}..." Curious what\'s been the hardest thing to systemize as you\'ve scaled?'
    elif company:
        return f"{greeting} - came across {company} and your content caught my attention. What's the biggest thing you're focused on scaling right now?"
    else:
        return f"{greeting} - came across your profile and it caught my attention. Curious - what's the biggest thing you're focused on right now?"


def generate_instagram_sequence(lead: dict, personalization: dict) -> dict:
    """Generate Instagram engagement strategy + 4-DM sequence.

    Args:
        lead: Lead dict from DB (must have instagram_url)
        personalization: Personalization dict from DB

    Returns:
        Instagram sequence dict
    """
    first_name = (lead.get("first_name") or lead.get("instagram_handle") or "").strip()
    company = (lead.get("company") or "your brand").strip()
    industry = (lead.get("industry") or "your space").strip()
    company_size = (lead.get("company_size") or "").strip()
    pain_signal = (lead.get("pain_signal") or "").strip()
    instagram_handle = (lead.get("instagram_handle") or "").strip()

    pain_points = personalization.get("pain_points", [])
    hook_3 = personalization.get("hook_3", "")

    # Pre-DM engagement plan (do this before sending DM 1)
    engagement_plan = [
        {"day": 1, "action": "Follow their account", "notes": ""},
        {"day": 1, "action": "Like their 3 most recent posts", "notes": "Use genuine recent posts, not old ones"},
        {"day": 2, "action": "Leave a genuine comment on their best post", "notes": "Reference something specific about the content — not just 'Great post!'"},
        {"day": 3, "action": "Watch and reply to their story if they post one", "notes": "Use a short, casual reaction that sparks conversation"},
        {"day": 4, "action": "Send DM 1", "notes": "Now they recognize your name"},
    ]

    # DM 1: Cold reading opener — rooted in observable facts, not generic praise
    if hook_3:
        dm_1 = f"Hey {first_name} - {hook_3}\n\nCurious what made you go that route?"
    elif company_size and company_size.isdigit() and int(company_size) <= 5:
        dm_1 = (
            f"Hey {first_name} - it looks like you're running {company} pretty lean. "
            f"That usually means you're doing more than one job at once. "
            f"What's the part you wish you could hand off?"
        )
    elif company_size and company_size.isdigit() and int(company_size) >= 20:
        dm_1 = (
            f"Hey {first_name} - it sounds like {company} has hit that stage where coordination "
            f"starts eating time that used to go into actual work. "
            f"What's your biggest ops headache right now?"
        )
    else:
        dm_1 = (
            f"Hey {first_name} - it looks like you're building {company} in the {industry} space. "
            f"Curious — what's been the hardest thing to systemize as you've grown?"
        )

    # DM 2: Value add — use actual pain signal if available, not a generic pattern
    pain_1 = ""
    if pain_points:
        pp = pain_points[0]
        pain_1 = pp.get("pain", "") if isinstance(pp, dict) else str(pp)

    if pain_1:
        dm_2 = (
            f"Hey — not looking for a reply, just thought this was relevant. "
            f"{pain_1[:200]} "
            f"Figured it might be worth flagging given what you're building."
        )
    elif pain_signal:
        dm_2 = (
            f"Hey — not looking for a reply, just something I noticed. "
            f"{pain_signal[:200]} "
            f"Might be worth a look if it's on your radar."
        )
    else:
        dm_2 = (
            f"Hey — not looking for a reply, just thought this was useful. "
            f"Most {industry} founders I know hit a scaling wall around operations — "
            f"the manual work compounds faster than the team does. "
            f"Happy to share what I've seen work if you're curious."
        )

    # DM 3: Soft transition (Day 12)
    dm_3 = (
        f"Hey {first_name} - it seems like {company} is at an interesting stage. "
        f"I work with founders building in this space on the tech side — AI automation, web systems, that kind of thing. "
        f"Would it be weird to jump on a call and share what I've seen work at your stage?"
    )

    # DM 4: Final touch (Day 18)
    dm_4 = (
        f"Hey {first_name}, last one from me — "
        f"if this isn't relevant right now that's totally fine. "
        f"Just wanted to make sure I wasn't leaving something on the table that could be useful for {company}. "
        f"Either way, keep building!"
    )

    return {
        "platform": "instagram",
        "instagram_handle": instagram_handle,
        "pre_dm_engagement": engagement_plan,
        "dms": [
            {"number": 1, "send_day": 4, "text": dm_1, "trigger": "After 3-day pre-engagement"},
            {"number": 2, "send_day": 7, "text": dm_2, "trigger": "No reply to DM 1"},
            {"number": 3, "send_day": 12, "text": dm_3, "trigger": "No reply to DM 2"},
            {"number": 4, "send_day": 18, "text": dm_4, "trigger": "No reply to DM 3"},
        ],
        "notes": "All sending is manual — Instagram bans automation bots.",
    }

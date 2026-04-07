"""LinkedIn outreach sequence transformer.

Generates:
  - Connection request note (≤300 chars, hard LinkedIn limit)
  - 4-DM sequence after acceptance

Principles:
  - Connection note: never pitch, reference something specific, genuine reason to connect
  - DM sequence: warm opener → value → bridge → direct ask
  - Uses Proxycurl recent posts data when available for hyper-personalization
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _truncate(text: str, max_len: int) -> str:
    """Truncate text to max_len chars, breaking at word boundary."""
    if len(text) <= max_len:
        return text
    truncated = text[:max_len - 3].rsplit(" ", 1)[0]
    return truncated + "..."


def generate_connection_note(lead: dict, personalization: dict, enrichment: dict = None) -> str:
    """Generate a LinkedIn connection request note (≤300 chars).

    References something specific — post, company, or industry context.
    Never pitches. Just creates a reason to connect.
    """
    first_name = (lead.get("first_name") or "").strip()
    company = (lead.get("company") or "your company").strip()
    industry = (lead.get("industry") or "").strip()

    # Try to use a recent LinkedIn post for personalization
    recent_posts = []
    if enrichment:
        import json
        posts_raw = enrichment.get("recent_posts", [])
        if isinstance(posts_raw, str):
            try:
                recent_posts = json.loads(posts_raw)
            except (json.JSONDecodeError, TypeError):
                recent_posts = []
        else:
            recent_posts = posts_raw or []

    if recent_posts and recent_posts[0].get("text"):
        # Reference their most recent post
        post_text = recent_posts[0]["text"][:100]
        note = f"Hey {first_name}, saw your post about {post_text[:60].rstrip('., ')}... resonated with what I'm seeing in the {industry} space. Would love to connect."
    elif personalization.get("hook_2"):
        # Use the pain hook
        hook = personalization["hook_2"][:150]
        note = f"Hey {first_name} — {hook} Working with {industry} founders on this. Would love to connect."
    else:
        # Generic but specific connection note
        note = f"Hey {first_name}, building in the {industry} space and came across {company}. Doing similar work with AI automation. Would love to connect."

    return _truncate(note, 300)


def generate_linkedin_sequence(lead: dict, personalization: dict, enrichment: dict = None) -> dict:
    """Generate a LinkedIn connection note + 4-DM sequence.

    Args:
        lead: Lead dict from DB
        personalization: Personalization dict from DB
        enrichment: Enrichment dict (optional — used for recent posts)

    Returns:
        LinkedIn sequence dict
    """
    first_name = (lead.get("first_name") or "there").strip()
    company = (lead.get("company") or "your company").strip()
    industry = (lead.get("industry") or "your industry").strip()

    connection_note = generate_connection_note(lead, personalization, enrichment)

    pain_points = personalization.get("pain_points", [])
    pain_1 = ""
    if pain_points:
        pp = pain_points[0]
        pain_1 = pp.get("pain", "") if isinstance(pp, dict) else str(pp)

    value_prop = personalization.get("value_prop", "")

    # DM 1: Warm opener after connection (Day 0)
    dm_1 = (
        f"Hey {first_name}, thanks for connecting!\n\n"
        f"I came across {company} while researching {industry} companies — "
        f"you're doing interesting work there.\n\n"
        f"What's the biggest challenge on your plate right now?"
    )

    # DM 2: Value add (Day 4)
    if pain_1:
        dm_2 = (
            f"Hey {first_name}, something you might find useful —\n\n"
            f"{pain_1}\n\n"
            f"Sharing because it's a pattern I see a lot in {industry} companies at your stage. "
            f"Let me know if it resonates."
        )
    else:
        dm_2 = (
            f"Hey {first_name}, sharing something that's been useful for {industry} founders I work with:\n\n"
            f"The biggest scaling bottleneck usually isn't the product — it's the manual operational "
            f"work that compounds as the team grows.\n\n"
            f"Happy to share what we've done to fix it if that's relevant."
        )

    # DM 3: Bridge (Day 9)
    dm_3 = (
        f"Hey {first_name} — just want to connect the dots.\n\n"
        f"{value_prop}\n\n"
        f"We've helped similar {industry} companies build systems that handle this without adding headcount. "
        f"Happy to share a quick example if you'd find that useful."
    )

    # DM 4: Direct ask (Day 16)
    dm_4 = (
        f"Hey {first_name}, last message from me —\n\n"
        f"Would it make sense to hop on a 20-min call to see if there's a fit? "
        f"I can show you what we've built for similar companies and you can decide if it's worth exploring.\n\n"
        f"If not, no worries at all."
    )

    return {
        "platform": "linkedin",
        "connection_note": connection_note,
        "dms": [
            {"number": 1, "send_day": 0, "text": dm_1, "trigger": "After connection accepted"},
            {"number": 2, "send_day": 4, "text": dm_2, "trigger": "No reply to DM 1"},
            {"number": 3, "send_day": 9, "text": dm_3, "trigger": "No reply to DM 2"},
            {"number": 4, "send_day": 16, "text": dm_4, "trigger": "No reply to DM 3"},
        ],
    }

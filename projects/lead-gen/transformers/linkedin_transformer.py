"""LinkedIn outreach sequence transformer.

Generates:
  - Connection request note (≤300 chars, hard LinkedIn limit)
  - 4-DM sequence after acceptance

Principles:
  - Connection note: never pitch, reference something specific, genuine reason to connect
  - DM sequence: warm opener → value → bridge → direct ask
  - Uses Proxycurl recent posts data when available for hyper-personalization
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _truncate(text: str, max_len: int) -> str:
    """Truncate text to max_len chars, breaking at word boundary."""
    if len(text) <= max_len:
        return text
    truncated = text[:max_len - 3].rsplit(" ", 1)[0]
    return truncated + "..."


def generate_connection_note_gpt(lead: dict) -> str | None:
    """Generate a personalized connection note via GPT-4o-mini.

    Returns the note string, or None if the API call fails.
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
        industry = (lead.get("industry") or "").strip()

        prompt = f"""Write a LinkedIn connection request note for this person:

Name: {first_name}
Title: {title}
Company: {company}
Industry: {industry}

Rules:
- Start with: Hey {first_name},
- One specific observation about their work, role, or company (1 sentence) — not generic praise
- Why you want to connect — peer angle, not sales
- End with: Looking forward to being in your network.
- Max 300 characters total — count carefully
- No CTA, no ask, no pitch
- Sound natural and human, not corporate
- No emojis, no symbols

Output ONLY the message text. No quotes, no explanation."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
            temperature=0.9,
        )
        note = response.choices[0].message.content.strip().replace("\n", " ").replace("  ", " ")
        return _truncate(note, 300)
    except Exception:
        return None


def generate_connection_note(lead: dict, personalization: dict, enrichment: dict = None) -> str:
    """Generate a LinkedIn connection request note (≤300 chars).

    Tries GPT-4o-mini first for genuine personalization, falls back to
    deterministic templates if the API is unavailable.
    """
    gpt_note = generate_connection_note_gpt(lead)
    if gpt_note:
        return gpt_note

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

    company_size = (lead.get("company_size") or "").strip()

    if recent_posts and recent_posts[0].get("text"):
        # Reference their most recent post — most specific signal available
        post_snippet = recent_posts[0]["text"][:60].rstrip("., ")
        note = f"Hey {first_name}, saw your recent post on {post_snippet}. Exploring similar ideas in the {industry} space and would love to exchange perspectives. Looking forward to being in your network."
    elif personalization.get("hook_2"):
        # Use the pain hook — cold reading based on observable signals
        hook = personalization["hook_2"][:120].rstrip("., ")
        note = f"Hey {first_name}, {hook}. Doing similar work in the {industry} space and would love to connect with someone thinking about this the same way. Looking forward to being in your network."
    elif company_size and company_size.isdigit() and int(company_size) <= 5:
        # Small team cold read — lean ops reality
        note = f"Hey {first_name}, noticed {company} is staying intentionally lean. That's a deliberate call most people don't make. Would love to connect with a founder building it that way. Looking forward to being in your network."
    elif company_size and company_size.isdigit() and int(company_size) >= 20:
        # Larger team cold read — coordination overhead reality
        note = f"Hey {first_name}, {company} looks like it's past the scrappy stage and into the scale-without-losing-speed phase. That's where things get genuinely interesting. Looking forward to being in your network."
    elif industry:
        # Cold read on industry + company
        note = f"Hey {first_name}, came across {company} while exploring the {industry} space. The stage you're building through is one I find genuinely interesting to follow. Looking forward to being in your network."
    else:
        # No industry — lean on company name alone
        note = f"Hey {first_name}, came across {company} and the work you're building caught my attention. The founder-led stage is one I find genuinely interesting to follow. Looking forward to being in your network."

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
    company_size = (lead.get("company_size") or "").strip()

    connection_note = generate_connection_note(lead, personalization, enrichment)

    pain_points = personalization.get("pain_points", [])
    pain_1 = ""
    if pain_points:
        pp = pain_points[0]
        pain_1 = pp.get("pain", "") if isinstance(pp, dict) else str(pp)

    value_prop = personalization.get("value_prop", "")

    # DM 1: Warm opener after connection (Day 0)
    # Cold reading label + genuine question — no pitch, no mention of services
    if company_size and company_size.isdigit() and int(company_size) <= 5:
        dm_1 = (
            f"Hey {first_name}, thanks for connecting!\n\n"
            f"It looks like you're running {company} pretty lean — that usually means "
            f"you're wearing more hats than you'd like.\n\n"
            f"What's the part of the business that's eating the most of your time right now?"
        )
    elif company_size and company_size.isdigit() and int(company_size) >= 20:
        dm_1 = (
            f"Hey {first_name}, thanks for connecting!\n\n"
            f"It sounds like {company} has scaled to the point where keeping everyone "
            f"moving in the same direction becomes its own full-time job.\n\n"
            f"What's the biggest friction point at your stage right now?"
        )
    else:
        dm_1 = (
            f"Hey {first_name}, thanks for connecting!\n\n"
            f"It looks like {company} is at an interesting stage in the {industry} space — "
            f"the kind where the decisions you make now compound fast.\n\n"
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

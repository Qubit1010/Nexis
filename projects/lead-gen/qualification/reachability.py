"""Layer 5: Reachability Score (0-15).

How likely are we to actually reach this person?
Active LinkedIn users reply to connection requests.
Professional email domains have better deliverability.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import SCORING

# Free email providers — lower deliverability, lower signal quality
FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "live.com", "icloud.com", "me.com", "aol.com",
    "protonmail.com", "zoho.com",
}


def score_reachability(lead: dict, enrichment: dict = None) -> tuple[int, dict]:
    """Score how reachable this lead is.

    Args:
        lead: Lead dict from DB
        enrichment: Enrichment dict (optional — Proxycurl data used if available)

    Returns:
        (score: int, breakdown: dict)
    """
    score = 0
    breakdown = {}

    email = (lead.get("email") or "").strip().lower()

    # +4 if professional email domain (not free provider)
    if email and "@" in email:
        domain = email.split("@")[-1].lower()
        if domain not in FREE_EMAIL_DOMAINS:
            points = SCORING["professional_email"]
            score += points
            breakdown["professional_email"] = points

    # +3 if Instagram/Twitter active (social presence = reachable on multiple channels)
    instagram_url = (lead.get("instagram_url") or "").strip()
    if instagram_url:
        points = SCORING["twitter_active"]
        score += points
        breakdown["social_active"] = points

    # +5 if LinkedIn recent activity (from Proxycurl enrichment or recent_activity field)
    if enrichment:
        import json
        recent_posts = enrichment.get("recent_posts", [])
        if isinstance(recent_posts, str):
            try:
                recent_posts = json.loads(recent_posts)
            except (json.JSONDecodeError, TypeError):
                recent_posts = []
        if recent_posts:
            points = SCORING["linkedin_active"]
            score += points
            breakdown["linkedin_active"] = points

        # +3 if 2nd-degree connection (from Proxycurl)
        proxycurl_data = enrichment.get("proxycurl_data", {})
        if isinstance(proxycurl_data, str):
            try:
                proxycurl_data = json.loads(proxycurl_data)
            except (json.JSONDecodeError, TypeError):
                proxycurl_data = {}
        if proxycurl_data.get("distance") == "DISTANCE_2":
            points = SCORING["second_degree"]
            score += points
            breakdown["second_degree"] = points
    else:
        # If no enrichment yet, check if recent_activity field has content
        if lead.get("recent_activity"):
            points = SCORING["linkedin_active"]
            score += points
            breakdown["linkedin_activity_signal"] = points

    return score, breakdown

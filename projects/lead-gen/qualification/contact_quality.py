"""Layer 1: Contact Quality Score (0-20).

Measures how reachable this person actually is.
A lead with no verified email AND no LinkedIn is essentially unreachable.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import ICP, SCORING


def score_contact_quality(lead: dict) -> tuple[int, dict]:
    """Score contact quality for a lead.

    Args:
        lead: Lead dict from DB

    Returns:
        (score: int, breakdown: dict)
    """
    score = 0
    breakdown = {}

    email = (lead.get("email") or "").strip().lower()
    email_verified = (lead.get("email_verified") or "").strip()
    linkedin_url = (lead.get("linkedin_url") or "").strip()
    instagram_url = (lead.get("instagram_url") or "").strip()

    # +8 for verified email
    if email and email_verified in ("Y", "Unverified") and email_verified != "N":
        points = SCORING["email_verified"]
        score += points
        breakdown["email_verified"] = points

    # -5 penalty for generic email prefix
    if email:
        prefix = email.split("@")[0].lower()
        if prefix in ICP["generic_email_prefixes"]:
            penalty = SCORING["generic_email_penalty"]
            score += penalty
            breakdown["generic_email_penalty"] = penalty

    # +6 for LinkedIn profile URL present
    if linkedin_url and "linkedin.com/in/" in linkedin_url:
        points = SCORING["linkedin_present"]
        score += points
        breakdown["linkedin_present"] = points

    # +3 for Instagram/Twitter social presence
    if instagram_url or lead.get("instagram_handle"):
        points = SCORING["social_present"]
        score += points
        breakdown["social_present"] = points

    # Ensure floor of 0
    score = max(0, score)

    return score, breakdown

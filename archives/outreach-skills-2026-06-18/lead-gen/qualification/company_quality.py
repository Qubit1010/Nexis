"""Layer 2: Company Quality Score (0-20).

Evaluates if the company is a good fit — right size, real business, credible.
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import ICP, SCORING


# LinkedIn company size strings and their employee midpoint
SIZE_MAP = {
    "1-10": 5,
    "2-10": 5,
    "11-50": 30,
    "51-200": 125,
    "201-500": 350,
    "501-1000": 750,
    "1001-5000": 3000,
    "5001-10000": 7500,
    "10001+": 15000,
}

# URLs that indicate it's not a real company website
NOT_A_WEBSITE = [
    "linktree", "linktr.ee", "beacons.ai", "bit.ly", "t.co",
    "twitter.com", "instagram.com", "facebook.com",
]


def is_real_website(url: str) -> bool:
    """Return True if the URL looks like a real company website."""
    if not url:
        return False
    url_lower = url.lower()
    for placeholder in NOT_A_WEBSITE:
        if placeholder in url_lower:
            return False
    # Must have at least a domain with a TLD
    return bool(re.search(r'https?://[^/]+\.[a-z]{2,}', url_lower))


def parse_company_size(size_str: str) -> int | None:
    """Convert a company size string to approximate employee count."""
    if not size_str:
        return None
    size_str = size_str.strip()
    return SIZE_MAP.get(size_str)


def score_company_quality(lead: dict) -> tuple[int, dict]:
    """Score company quality.

    Args:
        lead: Lead dict from DB

    Returns:
        (score: int, breakdown: dict)
    """
    score = 0
    breakdown = {}

    company_website = (lead.get("company_website") or "").strip()
    company_size = (lead.get("company_size") or "").strip()
    industry = (lead.get("industry") or "").strip().lower()

    # +5 if has real company website
    if is_real_website(company_website):
        points = SCORING["has_website"]
        score += points
        breakdown["has_website"] = points
    else:
        # -10 penalty for no website
        penalty = SCORING["no_website_penalty"]
        score += penalty
        breakdown["no_website_penalty"] = penalty

    # +5 if company size is in sweet spot (11-50)
    if company_size:
        employee_count = parse_company_size(company_size)
        if employee_count is not None:
            if company_size in ICP["sweet_spot_sizes"]:
                points = SCORING["size_sweet_spot"]
                score += points
                breakdown["size_sweet_spot"] = points
            elif company_size in ICP["disqualify_sizes"]:
                # Too large — don't add anything but don't penalize
                breakdown["size_too_large"] = 0

    # +4 for industry match (NexusPoint ICP industries)
    if industry:
        icp_industries_lower = [i.lower() for i in ICP["industries"]]
        if any(icp_ind in industry or industry in icp_ind for icp_ind in icp_industries_lower):
            points = SCORING["company_age"]  # Using company_age slot for industry match
            score += points
            breakdown["industry_match"] = points

    # Ensure floor of 0
    score = max(0, score)

    return score, breakdown

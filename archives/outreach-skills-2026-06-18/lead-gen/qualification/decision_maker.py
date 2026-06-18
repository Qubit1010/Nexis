"""Layer 4: Decision Maker Access Score (0-20).

Are we talking to the person who can actually sign the check?
Founders and CEOs say yes or no in one call. Managers need 3 meetings.

Scoring reflects the conversion likelihood by title level:
  - Founder/Owner: +20 (they built it, they decide everything)
  - CEO/CTO/COO: +16 (C-suite, fast decisions)
  - Head of Product/Ops/Eng: +12 (budget authority, often champion internal decisions)
  - Manager level: +6 (need to escalate)
  - IC or unknown: +0 (flag for manual review)
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import ICP, SCORING


def classify_title(title: str) -> str:
    """Classify a job title into a decision-maker tier.

    Returns:
        "founder" | "csuite" | "head" | "manager" | "ic" | "unknown"
    """
    if not title:
        return "unknown"

    t = title.lower().strip()

    # Check disqualifiers first
    for excl in ICP["disqualify_titles"]:
        if excl in t:
            return "ic"

    # Tier 1: Founder/Owner
    for kw in ICP["decision_maker_titles_tier1"]:
        if kw in t:
            return "founder"

    # Tier 2: C-suite
    for kw in ICP["decision_maker_titles_tier2"]:
        if kw in t:
            return "csuite"

    # Tier 3: Head of / Director / VP
    for kw in ICP["decision_maker_titles_tier3"]:
        if kw in t:
            return "head"

    # Tier 4: Manager / Lead
    for kw in ICP["decision_maker_titles_tier4"]:
        if kw in t:
            return "manager"

    return "unknown"


def score_decision_maker(lead: dict) -> tuple[int, dict]:
    """Score decision maker access.

    Args:
        lead: Lead dict from DB

    Returns:
        (score: int, breakdown: dict)
    """
    title = (lead.get("title") or "").strip()
    title_tier = classify_title(title)

    score_map = {
        "founder": SCORING["title_founder"],
        "csuite": SCORING["title_csuite"],
        "head": SCORING["title_head"],
        "manager": SCORING["title_manager"],
        "ic": 0,
        "unknown": 0,
    }

    score = score_map.get(title_tier, 0)
    breakdown = {}
    if score > 0:
        breakdown[f"title_{title_tier}"] = score
    elif title_tier == "ic":
        breakdown["title_ic_flagged"] = 0
    else:
        breakdown["title_unknown"] = 0

    return score, breakdown

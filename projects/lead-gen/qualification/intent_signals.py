"""Layer 3: Intent & Pain Signal Score (0-25).

This is the most important layer — companies with visible pain signals
are actively advertising their need for NexusPoint's services.

Signals:
  - Job posting with pain keywords (+8) — already detected by linkedin_jobs.py
  - Website built on Wix/Squarespace (+8) — detected during enrichment
  - Recent funding (+6) — from Perplexity news or Product Hunt
  - Product Hunt launch (+5) — source = product_hunt or recent_activity mentions PH
  - Low PageSpeed score (+4) — from enrichment
  - SSL/link issues (+3) — from enrichment
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import ICP, SCORING


def score_intent_signals(lead: dict, enrichment: dict = None) -> tuple[int, dict]:
    """Score intent and pain signals.

    Args:
        lead: Lead dict from DB
        enrichment: Enrichment dict from DB (optional — scored at discovery or after enrichment)

    Returns:
        (score: int capped at 25, breakdown: dict)
    """
    score = 0
    breakdown = {}

    # +8 if pain keywords were found in job posting (detected at discovery)
    pain_keywords = (lead.get("pain_keywords") or "").strip()
    if pain_keywords:
        points = SCORING["job_posting_pain"]
        score += points
        breakdown["job_posting_pain"] = points

    # +5 if from Product Hunt (funding/launch signal)
    if lead.get("source") == "product_hunt" or lead.get("funding_signal"):
        if lead.get("source") == "product_hunt":
            points = SCORING["product_hunt_launch"]
            score += points
            breakdown["product_hunt_launch"] = points

    # +6 if funding signal (from any source)
    if lead.get("funding_signal") and lead.get("source") != "product_hunt":
        points = SCORING["funding_signal"]
        score += points
        breakdown["funding_signal"] = points

    # +8 if pain_signal already identifies a tech-debt platform (set at import by Apollo importer)
    # This fires pre-enrichment so Apollo leads score correctly without waiting for Firecrawl.
    # Guard: don't double-count if enrichment later also detects it via website_tech.
    if not breakdown.get("tech_debt_signal"):
        pain_sig_lower = (lead.get("pain_signal") or "").lower()
        tech_debt_terms = [td.lower() for td in ICP["tech_debt_signals"]] + ["webflow", "wordpress"]
        if any(term in pain_sig_lower for term in tech_debt_terms):
            points = SCORING["tech_debt_signal"]
            score += points
            breakdown["tech_debt_signal"] = points

    # --- Enrichment-dependent signals (only if enrichment data is available) ---
    if enrichment:
        # +8 if website built on tech-debt platform (Wix/Squarespace/etc.)
        website_tech = enrichment.get("website_tech")
        if isinstance(website_tech, str):
            try:
                website_tech = json.loads(website_tech)
            except (json.JSONDecodeError, TypeError):
                website_tech = {}

        if isinstance(website_tech, dict):
            cms = (website_tech.get("cms") or "").lower()
            if any(td in cms for td in ICP["tech_debt_signals"]):
                points = SCORING["tech_debt_signal"]
                score += points
                breakdown["tech_debt_signal"] = points

        # +4 if PageSpeed mobile score < threshold
        pagespeed_mobile = enrichment.get("pagespeed_mobile", -1)
        if isinstance(pagespeed_mobile, (int, float)) and 0 <= pagespeed_mobile < 60:
            points = SCORING["pagespeed_low"]
            score += points
            breakdown["pagespeed_low"] = points

        # +3 if SSL issues or broken links found
        site_issues = enrichment.get("site_issues", [])
        if isinstance(site_issues, str):
            try:
                site_issues = json.loads(site_issues)
            except (json.JSONDecodeError, TypeError):
                site_issues = []
        if site_issues:
            points = SCORING["ssl_issues"]
            score += points
            breakdown["ssl_issues"] = points

        # +6 if funding news found in Perplexity research
        funding_news = (enrichment.get("funding_news") or "").strip()
        if funding_news and "funding" not in str(breakdown):
            points = SCORING["funding_signal"]
            score += points
            breakdown["funding_news"] = points

    # Cap at 25
    score = min(score, 25)
    return score, breakdown

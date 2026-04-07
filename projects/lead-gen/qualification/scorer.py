"""ICP Scoring orchestrator — runs all 5 layers and assigns tier.

Tier thresholds:
  HOT    90-100: Perfect ICP + pain signal → all 3 platforms + Proxycurl enrichment
  STRONG 75-89:  High quality → cold email + LinkedIn
  WARM   60-74:  Good potential → cold email only
  REJECTED <60:  Auto-archived, no outreach

Usage:
    python scorer.py              # score all unscored leads
    python scorer.py --rescore    # rescore all leads (including already scored)
    python scorer.py --dry-run    # print scores without saving
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database import get_leads, upsert_score, get_enrichment, get_stats
from config import TIER_HOT, TIER_STRONG, TIER_WARM

from qualification.contact_quality import score_contact_quality
from qualification.company_quality import score_company_quality
from qualification.intent_signals import score_intent_signals
from qualification.decision_maker import score_decision_maker
from qualification.reachability import score_reachability


def assign_tier(total_score: int) -> str:
    if total_score >= TIER_HOT:
        return "HOT"
    elif total_score >= TIER_STRONG:
        return "STRONG"
    elif total_score >= TIER_WARM:
        return "WARM"
    else:
        return "REJECTED"


def score_lead(lead: dict, enrichment: dict = None) -> dict:
    """Run all 5 scoring layers on a lead.

    Args:
        lead: Lead dict from DB
        enrichment: Enrichment dict from DB (optional)

    Returns:
        Score dict with all layer scores, total, tier, and breakdown
    """
    l1_score, l1_breakdown = score_contact_quality(lead)
    l2_score, l2_breakdown = score_company_quality(lead)
    l3_score, l3_breakdown = score_intent_signals(lead, enrichment)
    l4_score, l4_breakdown = score_decision_maker(lead)
    l5_score, l5_breakdown = score_reachability(lead, enrichment)

    total = l1_score + l2_score + l3_score + l4_score + l5_score
    tier = assign_tier(total)

    breakdown = {
        "L1_contact": {"score": l1_score, "max": 20, **l1_breakdown},
        "L2_company": {"score": l2_score, "max": 20, **l2_breakdown},
        "L3_intent": {"score": l3_score, "max": 25, **l3_breakdown},
        "L4_decision_maker": {"score": l4_score, "max": 20, **l4_breakdown},
        "L5_reachability": {"score": l5_score, "max": 15, **l5_breakdown},
    }

    return {
        "contact_quality": l1_score,
        "company_quality": l2_score,
        "intent_signal": l3_score,
        "decision_maker": l4_score,
        "reachability": l5_score,
        "total_score": total,
        "tier": tier,
        "breakdown": breakdown,
    }


def run_scoring(rescore: bool = False, dry_run: bool = False) -> dict:
    """Score all unscored (or all) leads and save results.

    Args:
        rescore: If True, rescore leads that already have scores
        dry_run: If True, print scores without writing to DB

    Returns:
        Summary dict with counts by tier
    """
    if rescore:
        leads = get_leads()
        print(f"Scoring all {len(leads)} leads (rescore mode)...", flush=True)
    else:
        leads = get_leads(filters={"not_scored": True})
        print(f"Scoring {len(leads)} unscored leads...", flush=True)

    if not leads:
        print("No leads to score.")
        return {}

    tier_counts = {"HOT": 0, "STRONG": 0, "WARM": 0, "REJECTED": 0}

    for lead in leads:
        lead_id = lead["lead_id"]

        # Load enrichment if available (improves Layer 3 and Layer 5 accuracy)
        enrichment = get_enrichment(lead_id)

        scores = score_lead(lead, enrichment)
        tier = scores["tier"]
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

        if not dry_run:
            upsert_score(lead_id, scores)
        else:
            print(
                f"  {lead_id} | {lead.get('full_name', '?')} @ {lead.get('company', '?')} | "
                f"Score: {scores['total_score']} | Tier: {tier}"
            )

    print("\nScoring complete.")
    print(f"  HOT:      {tier_counts.get('HOT', 0)}")
    print(f"  STRONG:   {tier_counts.get('STRONG', 0)}")
    print(f"  WARM:     {tier_counts.get('WARM', 0)}")
    print(f"  REJECTED: {tier_counts.get('REJECTED', 0)}")

    return tier_counts


def main():
    parser = argparse.ArgumentParser(description="Score leads against NexusPoint ICP")
    parser.add_argument("--rescore", action="store_true", help="Rescore all leads, including already-scored")
    parser.add_argument("--dry-run", action="store_true", help="Print scores without saving to DB")
    args = parser.parse_args()

    from database import init_db
    init_db()

    run_scoring(rescore=args.rescore, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

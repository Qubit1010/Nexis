"""NexusPoint Lead Generation Pipeline — CLI Orchestrator.

Usage:
  python main.py                          # full pipeline run
  python main.py run [--limit 20]         # full pipeline with limit
  python main.py discover [--source all]  # discovery only
  python main.py score [--rescore]        # scoring only
  python main.py enrich [--tier hot]      # enrichment only
  python main.py personalize              # personalization only
  python main.py export [--platform all]  # export only
  python main.py stats                    # pipeline stats
  python main.py lead LG-20260402-0001    # show full lead profile
  python main.py leads [--tier hot]       # list leads

Flags:
  --dry-run    Print what would happen without writing
  --limit N    Cap number of items to process
"""

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from pathlib import Path

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Load .env before anything else
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

from database import (
    init_db, insert_lead, update_lead, get_lead, get_leads, get_stats,
    upsert_enrichment, upsert_score, upsert_personalization, upsert_sequence,
    get_enrichment, get_personalization, get_score, get_sequence,
    check_duplicate
)
from config import ENRICHMENT as ENRICH_CFG, PERSONALIZATION as PERS_CFG, EXPORT_TIERS

from utils.dedup import dedup_lead_list, build_existing_keys_from_db

# Scrapers
from scrapers import linkedin_jobs, linkedin_profiles, google_search, product_hunt

# Qualification
from qualification.scorer import score_lead, run_scoring

# Enrichment
from enrichment.website_intel import enrich_website
from enrichment.email_finder import find_email
from enrichment.linkedin_enricher import enrich_linkedin
from enrichment.news_intel import enrich_news

# Personalization
from personalization.generator import generate_personalization_with_fallback

# Transformers
from transformers.email_transformer import generate_email_sequence
from transformers.linkedin_transformer import generate_linkedin_sequence
from transformers.instagram_transformer import generate_instagram_sequence

# Exporters
from exporters.gws_exporter import run_export
from exporters.csv_exporter import run_csv_export

# Google Search (for Instagram URL discovery)
from scrapers.google_search import find_instagram_url


# ---------------------------------------------------------------------------
# Discover phase
# ---------------------------------------------------------------------------

def cmd_discover(sources: list, limit: int, dry_run: bool):
    """Run discovery from specified sources and write new leads to DB."""
    print("\n=== DISCOVERY PHASE ===")

    all_new_leads = []

    # Priority order: founder/CEO profiles first, job-poster leads last.
    # This ensures the --limit cap fills with high-quality decision makers.

    if "all" in sources or "linkedin-profiles" in sources or "profiles" in sources:
        leads = linkedin_profiles.run(dry_run=dry_run)
        all_new_leads.extend(leads)

    if "all" in sources or "product-hunt" in sources or "ph" in sources:
        leads = product_hunt.run(dry_run=dry_run)
        all_new_leads.extend(leads)

    if "all" in sources or "google" in sources or "google-search" in sources:
        leads = google_search.run(dry_run=dry_run)
        all_new_leads.extend(leads)

    if "all" in sources or "linkedin-jobs" in sources or "jobs" in sources:
        leads = linkedin_jobs.run(dry_run=dry_run)
        all_new_leads.extend(leads)

    if not all_new_leads:
        print("No leads discovered.")
        return 0

    # Dedup against each other and existing DB leads
    print(f"\nDeduplicating {len(all_new_leads)} discovered leads...")
    existing_keys = build_existing_keys_from_db()
    unique_leads, skipped = dedup_lead_list(all_new_leads, existing_keys)
    print(f"  Unique new leads: {len(unique_leads)} | Duplicates skipped: {skipped}")

    if dry_run:
        print("\n[DRY RUN] Sample leads:")
        for lead in unique_leads[:5]:
            print(f"  {lead.get('full_name', '?')} @ {lead.get('company', '?')} [{lead.get('source')}]")
        return len(unique_leads)

    # Apply limit
    if limit:
        unique_leads = unique_leads[:limit]

    # Write to DB
    inserted = 0
    for lead in unique_leads:
        lead_id = insert_lead(lead)
        if lead_id:
            inserted += 1

    print(f"\nDiscovery complete: {inserted} new leads added to database.")
    return inserted


# ---------------------------------------------------------------------------
# Enrich phase
# ---------------------------------------------------------------------------

def cmd_enrich(tiers: list, dry_run: bool, limit: int):
    """Run enrichment for leads in specified tiers."""
    print("\n=== ENRICHMENT PHASE ===")

    # Get leads to enrich
    filters = {"tier_in": tiers}
    leads = get_leads(filters=filters)

    # Filter to only leads that haven't been enriched yet
    unenriched = []
    for lead in leads:
        enrichment = get_enrichment(lead["lead_id"])
        if not enrichment:
            unenriched.append(lead)

    if not unenriched:
        print("All qualifying leads already enriched.")
        return

    if limit:
        unenriched = unenriched[:limit]

    total = len(unenriched)
    print(f"Enriching {total} leads ({', '.join(tiers)} tier)...")

    if dry_run:
        for lead in unenriched:
            name = lead.get("full_name", "?")
            company = lead.get("company", "?")
            print(f"  [DRY RUN] Would enrich: {name} @ {company}", flush=True)
        print("\nEnrichment complete.")
        return

    def _enrich_single(lead: dict):
        lead_id = lead["lead_id"]
        name = lead.get("full_name") or f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip()
        company = lead.get("company", "?")
        tier = lead.get("tier", "?")

        print(f"\n  {name} @ {company} [{tier}]", flush=True)

        enrichment_data = {}

        # 1. Website intelligence (Firecrawl + PageSpeed)
        if lead.get("company_website"):
            website_data = enrich_website(lead)
            enrichment_data.update(website_data)

        # 2. Email finding
        if not lead.get("email"):
            use_hunter = tier in ENRICH_CFG.get("proxycurl_tiers", ["HOT"])
            email_data = find_email(lead, use_hunter=use_hunter)
            if email_data.get("email"):
                update_lead(lead_id, email_data)
                lead.update(email_data)

        # 3. Proxycurl LinkedIn enrichment (HOT only)
        if tier in ENRICH_CFG.get("proxycurl_tiers", ["HOT"]) and lead.get("linkedin_url"):
            linkedin_data = enrich_linkedin(lead)
            if linkedin_data:
                lead_updates = linkedin_data.pop("lead_updates", {})
                if lead_updates:
                    update_lead(lead_id, lead_updates)
                enrichment_data.update(linkedin_data)

        # 4. Company news
        news_data = enrich_news(lead)
        enrichment_data.update(news_data)

        # 5. Instagram URL discovery (HOT only)
        if tier in ENRICH_CFG.get("instagram_discovery_tiers", ["HOT"]) and not lead.get("instagram_url"):
            co = lead.get("company", "")
            full_name = lead.get("full_name", "")
            if co or full_name:
                website = lead.get("company_website", "")
                insta_url, insta_handle = find_instagram_url(co, full_name, company_website=website)
                if insta_url:
                    update_lead(lead_id, {"instagram_url": insta_url, "instagram_handle": insta_handle})
                    print(f"  Instagram found: @{insta_handle}", flush=True)

        # Save enrichment data
        if enrichment_data:
            upsert_enrichment(lead_id, enrichment_data)

        # Re-score with enrichment data
        updated_lead = get_lead(lead_id)
        new_enrichment = get_enrichment(lead_id)
        if updated_lead and new_enrichment:
            scores = score_lead(updated_lead, new_enrichment)
            upsert_score(lead_id, scores)
            print(f"  Re-scored {name}: {scores['total_score']} [{scores['tier']}]", flush=True)

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(_enrich_single, lead): lead for lead in unenriched}
        for future in as_completed(futures):
            lead = futures[future]
            try:
                future.result()
            except Exception as exc:
                name = lead.get("full_name", "?")
                print(f"  ERROR enriching {name}: {exc}", flush=True)

    print("\nEnrichment complete.")


# ---------------------------------------------------------------------------
# Personalize phase
# ---------------------------------------------------------------------------

def cmd_personalize(tiers: list, dry_run: bool, limit: int):
    """Generate personalization packages for leads in specified tiers."""
    print("\n=== PERSONALIZATION PHASE ===")

    leads = get_leads(filters={"tier_in": tiers})

    # Filter to only leads without personalization
    unpersonalized = []
    for lead in leads:
        p = get_personalization(lead["lead_id"])
        if not p:
            unpersonalized.append(lead)

    if not unpersonalized:
        print("All qualifying leads already personalized.")
        return

    if limit:
        unpersonalized = unpersonalized[:limit]

    print(f"Personalizing {len(unpersonalized)} leads...")

    for i, lead in enumerate(unpersonalized, 1):
        lead_id = lead["lead_id"]
        name = lead.get("full_name") or lead.get("first_name", "?")
        company = lead.get("company", "?")
        tier = lead.get("tier", "?")

        print(f"\n[{i}/{len(unpersonalized)}] {name} @ {company} [{tier}]", flush=True)

        if dry_run:
            print("  [DRY RUN] Would generate personalization")
            continue

        enrichment = get_enrichment(lead_id)
        personalization = generate_personalization_with_fallback(lead, enrichment)

        if personalization:
            upsert_personalization(lead_id, personalization)

            # Generate outreach sequences
            _generate_sequences(lead, personalization, enrichment, tier)

    print(f"\nPersonalization complete.")


def _generate_sequences(lead: dict, personalization: dict, enrichment: dict, tier: str):
    """Generate all applicable outreach sequences for a lead."""
    lead_id = lead["lead_id"]

    # Cold email sequence (all tiers)
    email_seq = generate_email_sequence(lead, personalization)
    upsert_sequence(lead_id, "cold_email", email_seq)

    # LinkedIn sequence (HOT + STRONG)
    if tier in ("HOT", "STRONG") and lead.get("linkedin_url"):
        linkedin_seq = generate_linkedin_sequence(lead, personalization, enrichment)
        upsert_sequence(lead_id, "linkedin", linkedin_seq)

    # Instagram sequence (HOT + STRONG, needs instagram_url)
    if tier in ("HOT", "STRONG") and lead.get("instagram_url"):
        insta_seq = generate_instagram_sequence(lead, personalization)
        upsert_sequence(lead_id, "instagram", insta_seq)


# ---------------------------------------------------------------------------
# Stats display
# ---------------------------------------------------------------------------

def cmd_stats():
    """Display pipeline stats."""
    stats = get_stats()

    print("\n=== LEAD GENERATION PIPELINE STATS ===")
    print(f"Total leads:  {stats['total']}")
    print(f"Unscored:     {stats['unscored']}")
    print(f"Unenriched:   {stats['unenriched']} (qualifying tier, not yet enriched)")
    print()

    print("By Source:")
    for source, count in (stats.get("by_source") or {}).items():
        print(f"  {source:<25} {count}")

    print()
    print("By Tier:")
    tier_order = ["HOT", "STRONG", "WARM", "REJECTED"]
    tier_emojis = {"HOT": "FIRE", "STRONG": "OK", "WARM": "WARM", "REJECTED": "X"}
    for tier in tier_order:
        count = (stats.get("by_tier") or {}).get(tier, 0)
        print(f"  {tier:<12} {count}")

    print()
    print("Exported to CRMs:")
    for platform, count in (stats.get("exported") or {}).items():
        print(f"  {platform:<20} {count}")


# ---------------------------------------------------------------------------
# Lead detail display
# ---------------------------------------------------------------------------

def cmd_lead(lead_id: str):
    """Show full profile for a single lead."""
    lead = get_lead(lead_id)
    if not lead:
        print(f"Lead {lead_id} not found.")
        return

    score = get_score(lead_id)
    enrichment = get_enrichment(lead_id)
    personalization = get_personalization(lead_id)

    print(f"\n=== LEAD: {lead_id} ===")
    print(f"Name:     {lead.get('full_name') or lead.get('first_name', '')} {lead.get('last_name', '')}")
    print(f"Title:    {lead.get('title', '')}")
    print(f"Company:  {lead.get('company', '')}")
    print(f"Website:  {lead.get('company_website', '')}")
    print(f"LinkedIn: {lead.get('linkedin_url', '')}")
    print(f"Email:    {lead.get('email', '')} ({lead.get('email_verified', '')})")
    print(f"Source:   {lead.get('source', '')}")
    print(f"Found:    {lead.get('date_discovered', '')}")

    if score:
        print(f"\nScore: {score['total_score']}/100 — {score['tier']}")
        breakdown = score.get("score_breakdown", "{}")
        if isinstance(breakdown, str):
            try:
                breakdown = json.loads(breakdown)
            except (json.JSONDecodeError, TypeError):
                breakdown = {}
        for layer, data in breakdown.items():
            if isinstance(data, dict):
                print(f"  {layer}: {data.get('score', 0)}/{data.get('max', '?')}")

    if lead.get("pain_signal"):
        print(f"\nPain signal: {lead['pain_signal']}")

    if enrichment:
        wt = enrichment.get("website_tech", {})
        if isinstance(wt, dict):
            print(f"\nWebsite tech: {wt.get('cms', 'unknown')}")
        ps_m = enrichment.get("pagespeed_mobile", -1)
        if ps_m >= 0:
            print(f"PageSpeed mobile: {ps_m}/100")
        if enrichment.get("company_news"):
            print(f"\nCompany news: {enrichment['company_news'][:300]}")

    if personalization:
        print("\nPersonalization:")
        for i, hook_key in enumerate(["hook_1", "hook_2", "hook_3"], 1):
            hook = personalization.get(hook_key, "")
            if hook:
                print(f"  Hook {i}: {hook}")
        if personalization.get("value_prop"):
            print(f"  Value prop: {personalization['value_prop']}")
        print(f"  Best channel: {personalization.get('best_channel', '')}")

    # Show available sequences
    for platform in ["cold_email", "linkedin", "instagram"]:
        seq = get_sequence(lead_id, platform)
        if seq:
            print(f"\n{platform.upper()} sequence: ready")


def cmd_leads_list(tier: str = None, limit: int = 20):
    """List leads with optional tier filter."""
    filters = {}
    if tier:
        filters["tier"] = tier.upper()

    leads = get_leads(filters=filters, limit=limit)
    if not leads:
        print("No leads found.")
        return

    print(f"\n{'ID':<22} {'Name':<25} {'Company':<20} {'Tier':<8} {'Score'}")
    print("-" * 85)
    for lead in leads:
        name = (lead.get("full_name") or f"{lead.get('first_name','')} {lead.get('last_name','')}").strip()[:24]
        company = (lead.get("company") or "")[:19]
        tier = (lead.get("tier") or "?")
        score = lead.get("total_score", "?")
        print(f"{lead['lead_id']:<22} {name:<25} {company:<20} {tier:<8} {score}")


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

def cmd_run(sources: list, limit: int, dry_run: bool):
    """Run the full pipeline end-to-end."""
    print(f"\n{'='*50}")
    print(f"NexusPoint Lead Generation Pipeline")
    print(f"{'='*50}")
    print(f"Date: {date.today().isoformat()} | Limit: {limit} | Dry-run: {dry_run}")

    # Phase 1: Discover
    cmd_discover(sources, limit=limit, dry_run=dry_run)

    # Phase 2: Score
    if not dry_run:
        print("\n=== SCORING PHASE ===")
        run_scoring(rescore=False, dry_run=False)

    # Phase 3: Enrich
    cmd_enrich(tiers=["HOT", "STRONG"], dry_run=dry_run, limit=limit)

    # Phase 4: Personalize
    cmd_personalize(tiers=["HOT", "STRONG"], dry_run=dry_run, limit=limit)

    # Phase 5: Export to Google Sheets
    print("\n=== EXPORT PHASE ===")
    if not dry_run:
        results = run_export(platform="all", dry_run=False)
        for platform, result in results.items():
            print(f"  {platform}: {result}")

    # Final stats
    if not dry_run:
        cmd_stats()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    init_db()

    parser = argparse.ArgumentParser(
        description="NexusPoint Lead Generation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  discover    Find new leads from LinkedIn Jobs, Profile Search, Google, Product Hunt
  score       Score unscored leads against ICP (5-layer, 0-100)
  enrich      Enrich qualified leads (website, email, LinkedIn, news)
  personalize Generate personalized hooks and outreach sequences
  export      Push leads to existing outreach CRMs
  stats       Show pipeline statistics
  lead        Show full profile for a specific lead ID
  leads       List leads with optional filters
  run         Full pipeline (default)
        """
    )

    subparsers = parser.add_subparsers(dest="command")

    # discover
    p_discover = subparsers.add_parser("discover")
    p_discover.add_argument("--source", default="all",
        help="Sources: all, linkedin-jobs, linkedin-profiles, google, product-hunt")
    p_discover.add_argument("--limit", type=int, default=None)
    p_discover.add_argument("--dry-run", action="store_true")

    # score
    p_score = subparsers.add_parser("score")
    p_score.add_argument("--rescore", action="store_true")
    p_score.add_argument("--dry-run", action="store_true")

    # enrich
    p_enrich = subparsers.add_parser("enrich")
    p_enrich.add_argument("--tier", default="hot,strong",
        help="Tiers to enrich: hot, strong, warm, all (comma-separated)")
    p_enrich.add_argument("--limit", type=int, default=None)
    p_enrich.add_argument("--dry-run", action="store_true")

    # personalize
    p_pers = subparsers.add_parser("personalize")
    p_pers.add_argument("--tier", default="hot,strong")
    p_pers.add_argument("--limit", type=int, default=None)
    p_pers.add_argument("--dry-run", action="store_true")

    # export
    p_export = subparsers.add_parser("export")
    p_export.add_argument("--platform", default="all",
        help="Platforms: all, cold-email, linkedin, instagram")
    p_export.add_argument("--format", default="sheets",
        help="Export format: sheets, csv, both")
    p_export.add_argument("--dry-run", action="store_true")

    # stats
    subparsers.add_parser("stats")

    # lead
    p_lead = subparsers.add_parser("lead")
    p_lead.add_argument("lead_id", help="Lead ID (e.g. LG-20260402-0001)")

    # leads
    p_leads = subparsers.add_parser("leads")
    p_leads.add_argument("--tier", default=None, help="Filter by tier: hot, strong, warm, rejected")
    p_leads.add_argument("--limit", type=int, default=20)

    # import (load pre-downloaded harvestapi JSON or Apollo CSV export)
    p_import = subparsers.add_parser("import")
    p_import.add_argument("path", help="Path to import file (JSON or CSV)")
    p_import.add_argument("--source", default="harvestapi", choices=["harvestapi", "apollo"],
        help="Import format: harvestapi (JSON) or apollo (CSV)")
    p_import.add_argument("--dry-run", action="store_true")
    p_import.add_argument("--limit", type=int, default=None)

    # run (full pipeline)
    p_run = subparsers.add_parser("run")
    p_run.add_argument("--source", default="all")
    p_run.add_argument("--limit", type=int, default=20)
    p_run.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if not args.command or args.command == "run":
        sources = getattr(args, "source", "all").split(",")
        limit = getattr(args, "limit", 20)
        dry_run = getattr(args, "dry_run", False)
        cmd_run(sources=sources, limit=limit, dry_run=dry_run)

    elif args.command == "discover":
        sources = args.source.split(",")
        cmd_discover(sources=sources, limit=args.limit, dry_run=args.dry_run)

    elif args.command == "score":
        run_scoring(rescore=args.rescore, dry_run=args.dry_run)

    elif args.command == "enrich":
        tiers_raw = args.tier.upper().split(",")
        if "ALL" in tiers_raw:
            tiers = ["HOT", "STRONG", "WARM"]
        else:
            tiers = [t.strip() for t in tiers_raw]
        cmd_enrich(tiers=tiers, dry_run=args.dry_run, limit=args.limit)

    elif args.command == "personalize":
        tiers_raw = args.tier.upper().split(",")
        tiers = [t.strip() for t in tiers_raw]
        cmd_personalize(tiers=tiers, dry_run=args.dry_run, limit=args.limit)

    elif args.command == "export":
        dry_run = args.dry_run
        fmt = args.format.lower()
        platform = args.platform.lower().replace("-", "_")

        if fmt in ("sheets", "both"):
            results = run_export(platform=platform, dry_run=dry_run)
            for p, r in results.items():
                print(f"  Sheets — {p}: {r}")

        if fmt in ("csv", "both"):
            paths = run_csv_export(platform=platform.replace("_", "-"), dry_run=dry_run)
            for path in paths:
                print(f"  CSV: {path}")

    elif args.command == "import":
        from utils.dedup import dedup_lead_list, build_existing_keys_from_db
        source = getattr(args, "source", "harvestapi")
        if source == "apollo":
            from scrapers.apollo_import import run as import_run
        else:
            from scrapers.json_import import run as import_run
        leads = import_run(args.path, dry_run=args.dry_run)
        if leads and not args.dry_run:
            existing_keys = build_existing_keys_from_db()
            unique, skipped = dedup_lead_list(leads, existing_keys)
            print(f"  Unique new leads: {len(unique)} | Duplicates skipped: {skipped}")
            if args.limit:
                unique = unique[:args.limit]
            inserted = sum(1 for lead in unique if insert_lead(lead))
            print(f"  Inserted {inserted} leads into database.")
            print("  Run 'python main.py score' to score them.")

    elif args.command == "stats":
        cmd_stats()

    elif args.command == "lead":
        cmd_lead(args.lead_id)

    elif args.command == "leads":
        cmd_leads_list(tier=args.tier, limit=args.limit)


if __name__ == "__main__":
    main()

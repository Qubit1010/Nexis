"""LinkedIn Jobs scraper — finds companies with pain signals.

Companies posting for "data entry", "operations admin", "reporting analyst" etc.
are advertising their automation bottleneck. These are the warmest leads.

Uses Apify LinkedIn Jobs Scraper (actor: hKByXkMQaC5Qt9UMN).
"""

import os
import sys
import re
import urllib.parse
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.apify import apify_run
from config import APIFY_ACTORS, DISCOVERY, ICP

JOBS_ACTOR = APIFY_ACTORS["linkedin_jobs"]

# Pain keywords — any of these in a job description signals a manual process bottleneck
PAIN_KEYWORDS = ICP["pain_keywords"]


def extract_pain_signal(description: str) -> tuple[str, str]:
    """Scan job description for pain keywords.

    Returns:
        (pain_signal: str, pain_keywords_csv: str)
        pain_signal is a 1-sentence human-readable description.
        pain_keywords_csv is comma-separated matched keywords.
    """
    if not description:
        return "", ""

    desc_lower = description.lower()
    found = [kw for kw in PAIN_KEYWORDS if kw in desc_lower]
    if not found:
        return "", ""

    keywords_csv = ", ".join(found[:5])

    if "data entry" in found or "copy-paste" in found or "copy paste" in found:
        return "Team is doing manual data entry or copy-paste work that could be automated.", keywords_csv
    if "spreadsheet" in found or "excel" in found:
        return "Team managing data manually in spreadsheets — strong automation opportunity.", keywords_csv
    if "tracking" in found or "reporting" in found:
        return "Team spending time on manual tracking and reporting that could be automated.", keywords_csv
    if "administrative" in found or "repetitive" in found:
        return "Role involves repetitive administrative tasks — automation signal.", keywords_csv

    return f"Manual process signals detected in job posting: {keywords_csv}.", keywords_csv


def scrape_linkedin_jobs(query: str, limit: int = None, dry_run: bool = False) -> list[dict]:
    """Scrape LinkedIn Jobs for a query and return lead dicts.

    Args:
        query: Job search query (e.g. "operations admin")
        limit: Max jobs to scrape
        dry_run: If True, print what would be scraped without calling Apify

    Returns:
        List of lead dicts in the standard lead schema
    """
    if limit is None:
        limit = DISCOVERY["linkedin_jobs_limit"]

    print(f"  Searching LinkedIn Jobs: '{query}' (limit {limit})", flush=True)

    if dry_run:
        print(f"  [DRY RUN] Would call Apify actor {JOBS_ACTOR} with query '{query}'")
        return []

    api_key = os.environ.get("APIFY_API_KEY", "").strip()
    if not api_key:
        print("  ERROR: APIFY_API_KEY not set", flush=True)
        return []

    search_url = f"https://www.linkedin.com/jobs/search/?keywords={urllib.parse.quote(query)}"
    input_data = {
        "urls": [search_url],
        "maxJobs": limit,
    }

    try:
        items = apify_run(JOBS_ACTOR, input_data, api_key=api_key)
    except Exception as exc:
        print(f"  LinkedIn Jobs scraper failed: {exc}", flush=True)
        return []

    leads = []
    today = date.today().isoformat()

    for item in items:
        company = (item.get("companyName") or "").strip()
        if not company:
            continue

        # Extract industry
        industry = item.get("industries", "")
        if isinstance(industry, list):
            industry = ", ".join(str(i) for i in industry)
        industry = str(industry).strip()

        # Job poster as proxy for decision maker
        poster_name = (item.get("jobPosterName") or "").strip()
        poster_title = (item.get("jobPosterTitle") or "").strip()
        name_parts = poster_name.split() if poster_name else []
        first_name = name_parts[0] if name_parts else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        # Extract pain signal from job description
        description = item.get("descriptionText") or item.get("descriptionHtml") or ""
        pain_signal, pain_keywords = extract_pain_signal(description)

        leads.append({
            "source": "linkedin_jobs",
            "first_name": first_name,
            "last_name": last_name,
            "full_name": poster_name,
            "title": poster_title,
            "company": company,
            "company_size": "",
            "industry": industry,
            "company_website": (item.get("companyWebsite") or "").strip(),
            "linkedin_url": "",  # poster profile URL not always available
            "company_linkedin": (item.get("companyLinkedinUrl") or "").strip(),
            "instagram_url": "",
            "instagram_handle": "",
            "email": "",
            "email_verified": "",
            "location": (item.get("location") or "").strip(),
            "pain_signal": pain_signal,
            "pain_keywords": pain_keywords,
            "recent_activity": (item.get("title") or query),  # job title as context
            "funding_signal": False,
            "date_discovered": today,
        })

    # Deduplicate within this batch by company name
    seen = set()
    unique = []
    for lead in leads:
        key = lead["company"].lower().strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(lead)

    print(f"  Found {len(unique)} unique companies from LinkedIn Jobs.", flush=True)
    return unique


def run(dry_run: bool = False) -> list[dict]:
    """Run all configured LinkedIn Jobs queries and return combined leads."""
    queries = DISCOVERY["linkedin_jobs_queries"]
    limit_per_query = DISCOVERY["linkedin_jobs_limit"]

    print(f"\nLinkedIn Jobs Discovery ({len(queries)} queries)...", flush=True)

    all_leads = []
    for query in queries:
        leads = scrape_linkedin_jobs(query, limit=limit_per_query, dry_run=dry_run)
        all_leads.extend(leads)

    print(f"LinkedIn Jobs total: {len(all_leads)} leads before dedup", flush=True)
    return all_leads

"""LinkedIn Profile Search scraper — finds founders/CEOs by title + industry.

Uses Apify's harvestapi/linkedin-profile-search actor.
This is the primary source for finding decision makers directly.

Confirmed working input schema (from actor build inspection):
  searchQuery: str  — keyword search (e.g. "Founder SaaS")
  currentJobTitles: list[str]  — filter by current title
  locations: list[str]  — filter by location
  profileScraperMode: "Short" | "Profile"
  maxItems: int
  takePages: int  — pages of 25 results each
"""

import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.apify import apify_run
from config import APIFY_ACTORS, DISCOVERY

PROFILES_ACTOR = APIFY_ACTORS["linkedin_profiles"]

# Primary geographies to target
TARGET_LOCATIONS = ["United States", "United Kingdom", "Australia", "Canada"]


def _parse_profile(item: dict, industry: str) -> dict | None:
    """Convert a harvestapi Short-mode profile to the standard lead schema."""
    first_name = (item.get("firstName") or "").strip()
    last_name = (item.get("lastName") or "").strip()
    full_name = f"{first_name} {last_name}".strip()
    if not full_name:
        return None

    linkedin_url = (item.get("linkedinUrl") or "").strip()

    # Title and company come from currentPositions[0]
    positions = item.get("currentPositions") or []
    pos = positions[0] if positions else {}
    role = (pos.get("title") or "").strip()
    company = (pos.get("companyName") or "").strip()
    company_linkedin = (pos.get("companyLinkedinUrl") or "").strip()

    # Location — can be string or dict
    raw_loc = item.get("location") or {}
    if isinstance(raw_loc, dict):
        location = (raw_loc.get("linkedinText") or raw_loc.get("city") or "").strip()
    else:
        location = str(raw_loc).strip()

    about = (item.get("summary") or "").strip()[:300]

    return {
        "source": "linkedin_profiles",
        "first_name": first_name,
        "last_name": last_name,
        "full_name": full_name,
        "title": role,
        "company": company,
        "company_size": "",
        "industry": industry,
        "company_website": "",
        "linkedin_url": linkedin_url,
        "company_linkedin": company_linkedin,
        "instagram_url": "",
        "instagram_handle": "",
        "email": "",
        "email_verified": "",
        "location": location,
        "pain_signal": "",
        "pain_keywords": "",
        "recent_activity": about,
        "funding_signal": False,
        "date_discovered": date.today().isoformat(),
    }


def scrape_linkedin_profiles(title: str, industry: str, limit: int = None, dry_run: bool = False) -> list[dict]:
    """Search LinkedIn for profiles matching title + industry."""
    if limit is None:
        limit = DISCOVERY["linkedin_profiles_limit"]

    print(f"  LinkedIn Profile Search: '{title}' in '{industry}' (limit {limit})", flush=True)

    if dry_run:
        print(f"  [DRY RUN] Would call Apify actor {PROFILES_ACTOR}")
        return []

    api_key = os.environ.get("APIFY_API_KEY", "").strip()
    if not api_key:
        print("  ERROR: APIFY_API_KEY not set", flush=True)
        return []

    input_data = {
        "searchQuery": f"{title} {industry}",
        "currentJobTitles": [title],
        "locations": TARGET_LOCATIONS,
        "profileScraperMode": "Short",
        "maxItems": limit,
        "takePages": max(1, limit // 25 + 1),
    }

    try:
        items = apify_run(PROFILES_ACTOR, input_data, api_key=api_key)
    except Exception as exc:
        print(f"  LinkedIn Profile Search failed: {exc}", flush=True)
        return []

    leads = []
    for item in items:
        lead = _parse_profile(item, industry)
        if lead:
            leads.append(lead)

    print(f"  Found {len(leads)} profiles for '{title}' + '{industry}'.", flush=True)
    return leads


def run(dry_run: bool = False) -> list[dict]:
    """Run all configured (title, industry) queries and return combined leads."""
    print(f"\nLinkedIn Profile Search Discovery...", flush=True)

    all_leads = []
    queries = DISCOVERY.get("linkedin_profiles_queries", [])
    limit = DISCOVERY.get("linkedin_profiles_limit", 15)

    for title, industry in queries:
        leads = scrape_linkedin_profiles(title, industry, limit=limit, dry_run=dry_run)
        all_leads.extend(leads)

    print(f"LinkedIn Profile Search total: {len(all_leads)} leads before dedup", flush=True)
    return all_leads

"""JSON importer — load a saved harvestapi LinkedIn profile dataset into the pipeline.

Accepts any JSON file exported from Apify's harvestapi~linkedin-profile-search actor.
Use this when you have a pre-downloaded dataset and want to push it through the
scoring, enrichment, and personalization pipeline without making live API calls.

Usage:
    python main.py import path/to/dataset.json
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _extract_title_company(headline: str, current_position: list) -> tuple[str, str]:
    """Extract job title and company from headline + currentPosition."""
    company = ""
    title = ""

    # Company from currentPosition (most reliable)
    if current_position:
        pos = current_position[0]
        company = (pos.get("companyName") or "").strip()

    # Title from headline — strip emoji, extract role
    if headline:
        # Remove emoji characters
        clean = re.sub(r'[^\x00-\x7F]+', '', headline).strip()
        # Common patterns: "Founder at Acme" / "CEO @ Acme" / "Founder | Acme"
        match = re.match(r'^(.+?)\s+(?:at|@)\s+(.+?)(?:\s*[|,]|$)', clean)
        if match:
            title = match.group(1).strip()
            if not company:
                company = match.group(2).strip()
        else:
            # Just take up to the first pipe/dash/comma as the title
            parts = re.split(r'\s*[|,]\s*', clean)
            title = parts[0].strip() if parts else clean

    return title, company


def _get_website(record: dict) -> str:
    """Extract best company website URL."""
    sites = record.get("companyWebsites") or []
    for s in sites:
        url = (s.get("url") or "").strip()
        if url:
            return url
    websites = record.get("websites") or []
    for w in websites:
        if isinstance(w, str) and w.strip():
            return w.strip()
    return ""


def _get_location(record: dict) -> str:
    loc = record.get("location") or {}
    return (loc.get("linkedinText") or "").strip()


def _get_company_size(record: dict) -> str:
    """Infer size bucket from follower/connection count as rough proxy."""
    followers = record.get("followerCount") or 0
    connections = record.get("connectionsCount") or 0
    signal = max(followers, connections)
    if signal < 500:
        return "1-10"
    if signal < 2000:
        return "11-50"
    if signal < 5000:
        return "51-200"
    return ""


def parse_harvestapi_record(record: dict) -> dict | None:
    """Convert one harvestapi profile record to the standard lead schema.

    Returns None if the record lacks enough data to be useful.
    """
    first_name = (record.get("firstName") or "").strip()
    last_name = (record.get("lastName") or "").strip()
    full_name = f"{first_name} {last_name}".strip()

    if not full_name:
        return None

    linkedin_url = (record.get("linkedinUrl") or "").strip()
    headline = (record.get("headline") or "").strip()
    current_position = record.get("currentPosition") or []

    title, company = _extract_title_company(headline, current_position)

    # Extract email if available
    emails = record.get("emails") or []
    email = emails[0].get("email", "") if emails and isinstance(emails[0], dict) else (emails[0] if emails and isinstance(emails[0], str) else "")

    website = _get_website(record)
    location = _get_location(record)
    company_size = _get_company_size(record)
    about = (record.get("about") or "")[:300]

    return {
        "source": "json_import",
        "first_name": first_name,
        "last_name": last_name,
        "full_name": full_name,
        "title": title,
        "company": company,
        "company_size": company_size,
        "industry": "",
        "company_website": website,
        "linkedin_url": linkedin_url,
        "company_linkedin": "",
        "instagram_url": "",
        "instagram_handle": "",
        "email": email,
        "email_verified": "",
        "location": location,
        "pain_signal": "",
        "pain_keywords": "",
        "recent_activity": about,
        "funding_signal": False,
        "date_discovered": date.today().isoformat(),
    }


def load_json_file(path: str | Path) -> list[dict]:
    """Load a harvestapi JSON export and return a list of lead dicts."""
    path = Path(path)
    if not path.exists():
        print(f"  ERROR: File not found: {path}", flush=True)
        return []

    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    if not isinstance(raw, list):
        print(f"  ERROR: Expected a JSON array, got {type(raw).__name__}", flush=True)
        return []

    print(f"  Loaded {len(raw)} records from {path.name}", flush=True)

    leads = []
    skipped = 0
    for record in raw:
        lead = parse_harvestapi_record(record)
        if lead:
            leads.append(lead)
        else:
            skipped += 1

    if skipped:
        print(f"  Skipped {skipped} records (missing name).", flush=True)

    print(f"  Parsed {len(leads)} leads from JSON import.", flush=True)
    return leads


def run(path: str | Path, dry_run: bool = False) -> list[dict]:
    """Import a JSON file and return leads."""
    print(f"\nJSON Import: {path}", flush=True)

    if dry_run:
        print("  [DRY RUN] Would import and parse records.", flush=True)
        return []

    return load_json_file(path)

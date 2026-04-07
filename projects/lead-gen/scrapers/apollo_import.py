"""Apollo.io CSV importer — load an Apollo export into the pipeline.

Apollo.io is a B2B contact database with 200M+ verified contacts.
Export a filtered list from Apollo and import it here to get pre-verified,
pre-enriched leads that score at STRONG tier immediately.

Setup:
    1. Sign up at apollo.io (free — no credit card required)
    2. Filter: Title = Founder/CEO, Industry = SaaS/E-commerce/Agency,
       Size = 1-50 employees, Location = US/UK/AU/CA
    3. Export as CSV (50 free/month on free plan)
    4. Run: python main.py import --source apollo path/to/apollo_export.csv

Why Apollo leads score STRONG immediately:
    - Email already verified (Apollo email_status = "Verified" → email_verified = "Y")
    - Company size in export → Layer 2 sweet_spot +5
    - Industry in export → Layer 2 industry match +4
    - Technologies column → Squarespace/Wix detected → Layer 3 tech_debt +8
    - LinkedIn URL present → Layer 1 +6
    - Professional email domain → Layer 5 +4
    - Founder/CEO title → Layer 4 +16 to +20
    Typical total: 56-64 pts → STRONG without enrichment
"""

import csv
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import ICP

# Tech debt platforms (Apollo's Technologies column uses these names)
_TECH_DEBT = set(ICP["tech_debt_signals"]) | {"webflow", "wordpress"}

# Apollo email_status → our email_verified field
_EMAIL_STATUS_MAP = {
    "verified": "Y",
    "likely to engage": "Y",
    "unverified": "Unverified",
    "bounced": "N",
    "invalid": "N",
    "do not email": "N",
    "spam": "N",
}


def _parse_technologies(tech_string: str) -> tuple[str, str]:
    """Parse Apollo's Technologies column for tech debt signals.

    Returns:
        (pain_signal, pain_keywords) — both empty strings if no signal found
    """
    if not tech_string:
        return "", ""

    techs = [t.strip().lower() for t in tech_string.split(",") if t.strip()]
    detected = []
    for tech in techs:
        for td in _TECH_DEBT:
            if td in tech:
                detected.append(tech)
                break

    if not detected:
        return "", ""

    # Use the first detected platform as the primary signal
    primary = detected[0].title()
    pain_signal = f"Uses {primary} — likely limited by platform capabilities"
    pain_keywords = ", ".join(detected)
    return pain_signal, pain_keywords


def _parse_location(row: dict) -> str:
    """Build location string from Apollo's City/State/Country columns."""
    parts = [
        (row.get("City") or "").strip(),
        (row.get("State") or "").strip(),
        (row.get("Country") or "").strip(),
    ]
    return ", ".join(p for p in parts if p)


def _parse_email_verified(status: str) -> str:
    """Map Apollo email_status to our email_verified field."""
    return _EMAIL_STATUS_MAP.get((status or "").strip().lower(), "Unverified")


def parse_apollo_row(row: dict) -> dict | None:
    """Convert one Apollo CSV row to the standard lead schema.

    Returns None if the row lacks a usable name.
    """
    first_name = (row.get("First Name") or "").strip()
    last_name = (row.get("Last Name") or "").strip()
    full_name = f"{first_name} {last_name}".strip()

    if not full_name:
        return None

    pain_signal, pain_keywords = _parse_technologies(row.get("Technologies") or "")

    # Build recent_activity from founding year + revenue range
    activity_parts = []
    founded = (row.get("Founded Year") or "").strip()
    revenue = (row.get("Revenue Range") or "").strip()
    if founded:
        activity_parts.append(f"Founded {founded}")
    if revenue:
        activity_parts.append(f"Revenue: {revenue}")
    recent_activity = " | ".join(activity_parts)

    return {
        "source": "apollo",
        "first_name": first_name,
        "last_name": last_name,
        "full_name": full_name,
        "title": (row.get("Title") or "").strip(),
        "company": (row.get("Company") or "").strip(),
        "company_size": (row.get("# Employees") or row.get("Employees") or "").strip(),
        "industry": (row.get("Industry") or "").strip(),
        "company_website": (row.get("Website") or row.get("Company Website") or "").strip(),
        "linkedin_url": (row.get("LinkedIn URL") or row.get("Person Linkedin Url") or "").strip(),
        "company_linkedin": (row.get("Company Linkedin Url") or "").strip(),
        "instagram_url": "",
        "instagram_handle": "",
        "email": (row.get("Email") or "").strip(),
        "email_verified": _parse_email_verified(row.get("Email Status") or ""),
        "location": _parse_location(row),
        "pain_signal": pain_signal,
        "pain_keywords": pain_keywords,
        "recent_activity": recent_activity,
        "funding_signal": False,
        "date_discovered": date.today().isoformat(),
    }


def load_apollo_csv(path: str | Path) -> list[dict]:
    """Load an Apollo.io CSV export and return standard lead dicts."""
    path = Path(path)
    if not path.exists():
        print(f"  ERROR: File not found: {path}", flush=True)
        return []

    leads = []
    skipped = 0

    with open(path, encoding="utf-8-sig") as f:  # utf-8-sig handles BOM from Excel exports
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"  Loaded {len(rows)} rows from {path.name}", flush=True)

    for row in rows:
        lead = parse_apollo_row(row)
        if lead:
            leads.append(lead)
        else:
            skipped += 1

    if skipped:
        print(f"  Skipped {skipped} rows (missing name).", flush=True)

    # Report tech debt signal coverage
    with_signal = sum(1 for l in leads if l["pain_signal"])
    print(f"  Parsed {len(leads)} leads ({with_signal} with tech debt signal).", flush=True)
    return leads


def run(path: str | Path, dry_run: bool = False) -> list[dict]:
    """Import an Apollo CSV and return leads."""
    print(f"\nApollo CSV Import: {path}", flush=True)

    if dry_run:
        print("  [DRY RUN] Would import and parse Apollo CSV.", flush=True)
        # Still parse to show preview
        leads = load_apollo_csv(path)
        if leads:
            sample = leads[0]
            print(f"  Sample: {sample['full_name']} @ {sample['company']} | {sample['title']}", flush=True)
            print(f"  Email: {sample['email']} ({sample['email_verified']})", flush=True)
            if sample['pain_signal']:
                print(f"  Pain signal: {sample['pain_signal']}", flush=True)
        return []

    return load_apollo_csv(path)

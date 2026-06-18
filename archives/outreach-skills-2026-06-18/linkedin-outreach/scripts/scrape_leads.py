"""Scrape LinkedIn leads using Apify and store in Google Sheets CRM.

Single-step pipeline: Google Search Scraper → extract name, role, company, location
directly from organic results (no second actor needed).

Usage:
  python scripts/scrape_leads.py
  python scripts/scrape_leads.py --titles "Founder,CEO,COO" --industry "SaaS,Agency"
  python scripts/scrape_leads.py --limit 30
  python scripts/scrape_leads.py --dry-run
"""

import argparse
import os
import sys
import time
from datetime import date
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from gws_utils import append_rows, get_or_create_sheet, read_all_rows

APIFY_API_BASE = "https://api.apify.com/v2"
GOOGLE_SEARCH_ACTOR = "nFJndFXA5zjCTuudP"  # apify/google-search-scraper

# Default target audience for NexusPoint outreach
DEFAULT_TITLES = ["Founder", "Co-Founder", "CEO", "COO", "Head of Operations"]
DEFAULT_INDUSTRIES = ["SaaS", "Software", "Marketing Agency", "Digital Agency", "E-commerce"]


# ---------------------------------------------------------------------------
# Apify helpers
# ---------------------------------------------------------------------------

def apify_run(actor_id, actor_input, api_key, timeout=300):
    """Start an Apify actor run, poll until done, return dataset items."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    resp = requests.post(
        f"{APIFY_API_BASE}/acts/{actor_id}/runs",
        headers=headers,
        json=actor_input,
        timeout=30,
    )

    if resp.status_code == 402:
        print("ERROR: Apify credits exhausted. Check https://console.apify.com")
        sys.exit(1)
    if resp.status_code == 403:
        print(f"ERROR: Apify actor '{actor_id}' access denied. Check API key or actor permissions.")
        sys.exit(1)
    if resp.status_code == 404:
        print(f"ERROR: Actor '{actor_id}' not found on Apify.")
        sys.exit(1)
    resp.raise_for_status()

    run_id = resp.json()["data"]["id"]
    print(f"  Run {run_id} started...", end="", flush=True)

    # Poll for completion
    start = time.time()
    while time.time() - start < timeout:
        for attempt in range(4):
            try:
                status_resp = requests.get(
                    f"{APIFY_API_BASE}/actor-runs/{run_id}",
                    headers=headers,
                    timeout=20,
                )
                status_resp.raise_for_status()
                break
            except requests.exceptions.Timeout:
                if attempt < 3:
                    time.sleep(5)
                    continue
                raise
        run_data = status_resp.json()["data"]
        status = run_data["status"]

        if status == "SUCCEEDED":
            print(" done.")
            break
        if status in ("FAILED", "ABORTED", "TIMED-OUT"):
            print(f"\n  Run {status}.")
            return []

        print(".", end="", flush=True)
        time.sleep(10)
    else:
        print(f"\n  Timeout after {timeout}s.")
        return []

    # Fetch results
    dataset_id = run_data["defaultDatasetId"]
    items_resp = requests.get(
        f"{APIFY_API_BASE}/datasets/{dataset_id}/items?format=json&clean=true",
        headers=headers,
        timeout=30,
    )
    items_resp.raise_for_status()
    return items_resp.json()


# ---------------------------------------------------------------------------
# Google Search → leads (single step)
# ---------------------------------------------------------------------------

def build_search_queries(titles, industries):
    """Build Google search queries that find LinkedIn profiles matching our criteria."""
    queries = []
    for title in titles[:3]:
        for industry in industries[:2]:
            queries.append(f'site:linkedin.com/in "{title}" "{industry}"')
        queries.append(f'site:linkedin.com/in "{title}" founder OR CEO OR COO')
    return queries[:6]  # cap at 6 to stay within free tier


def parse_name_from_title(title_str):
    """Extract person name from Google result title like 'John Smith - SaaS Founder'."""
    if " - " in title_str:
        return title_str.split(" - ")[0].strip()
    if " | " in title_str:
        return title_str.split(" | ")[0].strip()
    # Fallback: take first 1-3 words that look like a name
    words = title_str.split()
    name_words = []
    for w in words:
        if w[0].isupper() and not w.isupper():
            name_words.append(w)
        else:
            break
    return " ".join(name_words[:3]) if name_words else ""


def extract_leads_from_search(search_results):
    """Extract structured lead data directly from Google Search organic results."""
    leads = []
    seen_urls = set()

    for item in search_results:
        for organic in item.get("organicResults", []):
            url = (organic.get("url") or organic.get("link") or "").split("?")[0].rstrip("/")
            if not url or "linkedin.com/in/" not in url or url in seen_urls:
                continue
            seen_urls.add(url)

            # Name from title
            raw_title = organic.get("title", "")
            name = parse_name_from_title(raw_title)
            first_name = name.split()[0] if name else "there"

            # Role and company from personalInfo (rich structured field)
            personal = organic.get("personalInfo") or {}
            role = personal.get("jobTitle") or ""
            company = personal.get("companyName") or ""
            location = personal.get("location") or ""

            # If personalInfo is sparse, try parsing from title suffix
            if not role and " - " in raw_title:
                role = raw_title.split(" - ", 1)[1].strip()

            # Description as context for message generation
            description = organic.get("description") or ""
            if len(description) > 250:
                description = description[:250].rsplit(" ", 1)[0] + "..."

            leads.append({
                "Name": name or "Unknown",
                "First Name": first_name,
                "Company": company,
                "Role": role,
                "LinkedIn URL": url,
                "Location": location,
                "Recent Post": description,
            })

    return leads


def google_search_for_leads(titles, industries, api_key, limit):
    """Run Google Search Scraper and extract lead data from results."""
    queries = build_search_queries(titles, industries)
    results_per_query = max(10, limit // len(queries))

    print(f"Searching Google ({len(queries)} queries, ~{results_per_query} results each)")
    actor_input = {
        "queries": "\n".join(queries),
        "maxPagesPerQuery": 1,
        "resultsPerPage": results_per_query,
        "countryCode": "us",
    }
    raw = apify_run(GOOGLE_SEARCH_ACTOR, actor_input, api_key)
    leads = extract_leads_from_search(raw)
    print(f"  Extracted {len(leads)} leads from search results")
    return leads[:limit]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Scrape LinkedIn leads into Google Sheets CRM (via Google Search)"
    )
    parser.add_argument(
        "--titles",
        default=",".join(DEFAULT_TITLES),
        help="Comma-separated job titles to target",
    )
    parser.add_argument(
        "--industry",
        default=",".join(DEFAULT_INDUSTRIES),
        help="Comma-separated industries to target",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=30,
        help="Max leads to find (default: 30)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show results without writing to sheet",
    )
    args = parser.parse_args()

    api_key = os.getenv("APIFY_API_KEY")
    if not api_key:
        print("ERROR: APIFY_API_KEY not set.")
        print("Set it with: $env:APIFY_API_KEY = 'your_key'")
        sys.exit(1)

    titles = [t.strip() for t in args.titles.split(",") if t.strip()]
    industries = [i.strip() for i in args.industry.split(",") if i.strip()]

    print(f"Targeting: {', '.join(titles[:4])}")
    print(f"Industries: {', '.join(industries[:3])}")
    print(f"Limit: {args.limit}")
    print()

    leads = google_search_for_leads(titles, industries, api_key, args.limit)

    if not leads:
        print("No leads found. Try different titles or industries.")
        return

    if args.dry_run:
        print(f"\n--- DRY RUN: First 10 leads ---")
        for i, l in enumerate(leads[:10], 1):
            print(f"  {i}. {l['Name']} | {l['Role']} @ {l['Company']}")
            print(f"     {l['LinkedIn URL']}")
            if l["Recent Post"]:
                print(f"     Snippet: {l['Recent Post'][:80]}...")
        print(f"\nTotal: {len(leads)} leads (not saved — remove --dry-run to save)")
        return

    # Load existing leads for deduplication
    sheet_id = get_or_create_sheet()
    existing = read_all_rows(sheet_id)
    existing_urls = {
        r.get("LinkedIn URL", "").strip().lower().rstrip("/")
        for r in existing
        if r.get("LinkedIn URL")
    }

    new_leads = [
        l for l in leads
        if l["LinkedIn URL"].lower().rstrip("/") not in existing_urls
    ]
    skipped = len(leads) - len(new_leads)
    print(f"After dedup: {len(new_leads)} new | {skipped} already in CRM")

    if not new_leads:
        print("No new leads to add.")
        return

    today = date.today().isoformat()
    rows = [
        [
            l["Name"], l["First Name"], l["Company"], l["Role"],
            l["LinkedIn URL"], l["Location"], l["Recent Post"],
            "", "New", today,
        ]
        for l in new_leads
    ]

    append_rows(sheet_id, rows)
    print(f"\nAdded {len(new_leads)} leads to CRM.")
    print(f"Sheet: https://docs.google.com/spreadsheets/d/{sheet_id}")
    print(f"\nNext step: python scripts/generate_messages.py --dry-run")


if __name__ == "__main__":
    main()

"""Scrape Instagram leads using Apify and store in Google Sheets CRM.

Searches by hashtag to find founders, CEOs, and ops leads at small businesses.
Extracts profile data directly from Apify's Instagram Hashtag Scraper results.

Usage:
  python scripts/scrape_leads.py
  python scripts/scrape_leads.py --hashtags "saasfounder,agencyowner,startupCEO"
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
INSTAGRAM_HASHTAG_ACTOR = "reGe1ST3OBgYZSsZJ"  # apify/instagram-hashtag-scraper

# Default hashtags that surface founders/operators at small businesses
DEFAULT_HASHTAGS = [
    "saasfounder",
    "startupfounder",
    "agencyowner",
    "ecommercefounder",
    "startupCEO",
    "techfounder",
    "b2bsaas",
]

# ICP filter — follower range signals real business, not influencer or ghost account
MIN_FOLLOWERS = 100
MAX_FOLLOWERS = 100_000

# Keywords that signal a business decision-maker in the bio
BIO_SIGNALS = [
    "founder", "co-founder", "ceo", "coo", "head of", "owner", "operator",
    "building", "scaling", "startup", "saas", "agency", "e-commerce", "ecommerce",
    "entrepreneur", "bootstrapped", "b2b",
]


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

    dataset_id = run_data["defaultDatasetId"]
    items_resp = requests.get(
        f"{APIFY_API_BASE}/datasets/{dataset_id}/items?format=json&clean=true",
        headers=headers,
        timeout=30,
    )
    items_resp.raise_for_status()
    return items_resp.json()


# ---------------------------------------------------------------------------
# Lead extraction and filtering
# ---------------------------------------------------------------------------

def is_icp(profile):
    """Return True if the profile looks like a business decision-maker.

    The Instagram Hashtag Scraper returns post data only — no follower count
    or biography on the owner. We use the post caption as a bio proxy and
    treat the hashtag context itself as the primary ICP qualifier.
    """
    # Caption serves as bio proxy (owner bio is not in hashtag scraper output)
    bio = (profile.get("biography") or profile.get("caption") or "").lower()

    # Follower count often unavailable — skip that check when data is missing
    followers = profile.get("followersCount") or 0
    if followers > 0 and (followers < MIN_FOLLOWERS or followers > MAX_FOLLOWERS):
        return False

    # Accept if there's any ICP signal in bio/caption, OR if no text at all
    # (hashtag context alone qualifies them — e.g. #saasfounder)
    if bio and not any(signal in bio for signal in BIO_SIGNALS):
        return False

    return True


def extract_name_from_full_name(full_name):
    """Return first name from a full name string."""
    if not full_name:
        return "there"
    parts = full_name.strip().split()
    return parts[0] if parts else "there"


def infer_role_from_bio(bio):
    """Best-effort role extraction from Instagram bio text."""
    if not bio:
        return ""
    bio_lower = bio.lower()
    role_keywords = [
        ("Founder", ["founder", "co-founder"]),
        ("CEO", ["ceo", "chief executive"]),
        ("COO", ["coo", "chief operating"]),
        ("Head of Operations", ["head of ops", "head of operations"]),
        ("Owner", ["owner"]),
        ("Operator", ["operator"]),
        ("Entrepreneur", ["entrepreneur"]),
    ]
    for label, keywords in role_keywords:
        if any(kw in bio_lower for kw in keywords):
            return label
    return ""


def infer_company_from_bio(bio, username):
    """Try to find a company name in the bio (rough heuristic)."""
    if not bio:
        return ""
    # Look for @mention (often the business account)
    words = bio.split()
    for w in words:
        if w.startswith("@") and len(w) > 2:
            return w[1:]  # Strip the @
    return ""


def extract_leads_from_hashtag_results(results, limit):
    """Extract unique lead profiles from Apify hashtag scraper output."""
    leads = []
    seen_usernames = set()

    for item in results:
        # Each item is a post — the owner is our lead
        owner = item.get("ownerUsername") or item.get("owner", {}).get("username", "")
        if not owner or owner in seen_usernames:
            continue

        # Build a profile dict from post metadata.
        # Note: Instagram Hashtag Scraper returns post data only — owner bio
        # and follower count are NOT available. We use caption as context.
        caption = (item.get("caption") or "")[:300]
        profile = {
            "username": owner,
            "fullName": item.get("ownerFullName") or item.get("owner", {}).get("fullName", ""),
            "biography": item.get("ownerBiography") or item.get("biography") or "",
            "caption": caption,
            "followersCount": (
                item.get("ownerFollowersCount")
                or item.get("followersCount")
                or item.get("owner", {}).get("followersCount", 0)
            ),
            "profileUrl": f"https://www.instagram.com/{owner}/",
        }

        if not is_icp(profile):
            continue

        seen_usernames.add(owner)

        full_name = profile["fullName"] or owner
        bio = profile["biography"]
        role = infer_role_from_bio(bio)
        company = infer_company_from_bio(bio, owner)

        # Use caption as bio context when biography isn't available
        display_bio = (profile["biography"] or profile["caption"])[:300]

        leads.append({
            "Name": full_name,
            "Username": f"@{owner}",
            "Company": company,
            "Role": role,
            "Instagram URL": profile["profileUrl"],
            "Followers": str(profile["followersCount"]) if profile["followersCount"] else "",
            "Bio": display_bio,
        })

        if len(leads) >= limit:
            break

    return leads


def scrape_instagram_leads(hashtags, api_key, limit):
    """Run the Apify Instagram Hashtag Scraper and return filtered leads."""
    posts_per_hashtag = max(20, (limit * 5) // len(hashtags))  # over-fetch to allow filtering

    print(f"Scraping {len(hashtags)} hashtags (~{posts_per_hashtag} posts each)")
    actor_input = {
        "hashtags": hashtags,
        "resultsLimit": posts_per_hashtag,
        "scrapeType": "posts",
        "proxy": {"useApifyProxy": True},
    }

    raw = apify_run(INSTAGRAM_HASHTAG_ACTOR, actor_input, api_key)
    if not raw:
        return []

    leads = extract_leads_from_hashtag_results(raw, limit)
    print(f"  Extracted {len(leads)} ICP-matching leads from {len(raw)} posts")
    return leads


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Scrape Instagram leads into Google Sheets CRM (via Apify)"
    )
    parser.add_argument(
        "--hashtags",
        default=",".join(DEFAULT_HASHTAGS),
        help="Comma-separated hashtags to search (without #)",
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

    hashtags = [h.strip().lstrip("#") for h in args.hashtags.split(",") if h.strip()]

    print(f"Hashtags: {', '.join('#' + h for h in hashtags[:5])}")
    print(f"ICP filter: {MIN_FOLLOWERS}-{MAX_FOLLOWERS} followers + bio signal")
    print(f"Limit: {args.limit}")
    print()

    leads = scrape_instagram_leads(hashtags, api_key, args.limit)

    if not leads:
        print("No ICP-matching leads found. Try different hashtags or relax the follower filter.")
        return

    if args.dry_run:
        print(f"\n--- DRY RUN: First 10 leads ---")
        for i, l in enumerate(leads[:10], 1):
            print(f"  {i}. {l['Name']} ({l['Username']}) | {l['Role']} | {l['Followers']} followers")
            print(f"     {l['Instagram URL']}")
            if l["Bio"]:
                print(f"     Bio: {l['Bio'][:80]}...")
        print(f"\nTotal: {len(leads)} leads (not saved — remove --dry-run to save)")
        return

    sheet_id = get_or_create_sheet()
    existing = read_all_rows(sheet_id)
    existing_urls = {
        r.get("Instagram URL", "").strip().lower().rstrip("/")
        for r in existing
        if r.get("Instagram URL")
    }

    new_leads = [
        l for l in leads
        if l["Instagram URL"].lower().rstrip("/") not in existing_urls
    ]
    skipped = len(leads) - len(new_leads)
    print(f"After dedup: {len(new_leads)} new | {skipped} already in CRM")

    if not new_leads:
        print("No new leads to add.")
        return

    today = date.today().isoformat()
    rows = [
        [
            l["Name"], l["Username"], l["Company"], l["Role"],
            l["Instagram URL"], l["Followers"], l["Bio"],
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

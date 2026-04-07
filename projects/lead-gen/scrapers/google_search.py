"""Google Search scraper — supplemental LinkedIn profile discovery.

Uses Google Custom Search JSON API (free, 100 queries/day) to find LinkedIn
profiles by title + industry when harvestapi doesn't return results.

Also used during enrichment to find Instagram URLs for HOT leads.

Setup required:
  1. Enable "Custom Search API" in Google Cloud Console (same project as PAGESPEED_API_KEY)
  2. Create a Custom Search Engine at programmablesearchengine.google.com
     → Set to "Search the entire web"
     → Copy the Search Engine ID (cx)
  3. Add to .env: GOOGLE_CSE_ID=<your cx value>
     (PAGESPEED_API_KEY is reused as the API key)
"""

import os
import sys
import re
import time
from datetime import date
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DISCOVERY

GOOGLE_CSE_ENDPOINT = "https://www.googleapis.com/customsearch/v1"


def _get_cse_credentials() -> tuple[str, str]:
    """Return (api_key, cse_id) or ("", "") if not configured."""
    api_key = os.environ.get("PAGESPEED_API_KEY", "").strip()
    cse_id = os.environ.get("GOOGLE_CSE_ID", "").strip()
    return api_key, cse_id


def parse_linkedin_name_from_snippet(title: str, snippet: str) -> tuple[str, str, str]:
    """Extract name, role, and company from a LinkedIn Google Search result.

    Google typically returns: "John Doe - Founder at Acme Corp | LinkedIn"
    """
    full_name = ""
    role = ""
    company = ""

    # Try to parse from result title: "Name - Role at Company | LinkedIn"
    if title:
        # Remove LinkedIn suffix
        clean_title = re.sub(r'\s*\|\s*LinkedIn.*$', '', title, flags=re.IGNORECASE).strip()
        # Pattern: "Name - Role at Company"
        match = re.match(r'^(.+?)\s*[-–]\s*(.+?)\s+(?:at|@)\s+(.+)$', clean_title)
        if match:
            full_name = match.group(1).strip()
            role = match.group(2).strip()
            company = match.group(3).strip()
        else:
            # Just name and role
            match = re.match(r'^(.+?)\s*[-–]\s*(.+)$', clean_title)
            if match:
                full_name = match.group(1).strip()
                role = match.group(2).strip()
            else:
                full_name = clean_title

    # Fallback: extract from snippet
    if not company and snippet:
        match = re.search(r'(?:at|@)\s+([A-Z][^\n,|]{2,40})', snippet)
        if match:
            company = match.group(1).strip()

    return full_name, role, company


def _cse_search(query: str, num: int = 10, api_key: str = "", cse_id: str = "") -> list[dict]:
    """Run a single Google Custom Search query. Returns list of result dicts."""
    if not api_key or not cse_id:
        return []

    results = []
    # CSE returns max 10 per request; fetch up to `num` results
    fetched = 0
    start = 1

    while fetched < num:
        batch = min(10, num - fetched)
        params = {
            "key": api_key,
            "cx": cse_id,
            "q": query,
            "num": batch,
            "start": start,
        }
        try:
            resp = requests.get(GOOGLE_CSE_ENDPOINT, params=params, timeout=15)
            if resp.status_code == 429:
                # Rate limited — stop gracefully
                print("  Google CSE rate limit hit, stopping.", flush=True)
                break
            resp.raise_for_status()
        except requests.RequestException as exc:
            print(f"  Google CSE request failed: {exc}", flush=True)
            break

        data = resp.json()
        items = data.get("items", [])
        if not items:
            break

        results.extend(items)
        fetched += len(items)

        if not data.get("queries", {}).get("nextPage"):
            break
        start += batch
        time.sleep(0.2)  # polite delay between pages

    return results


def scrape_linkedin_profiles_via_google(query: str, limit: int = 10, dry_run: bool = False) -> list[dict]:
    """Run a Google Search for LinkedIn profiles and return lead dicts."""
    if dry_run:
        print(f"  [DRY RUN] Would Google Search: {query}")
        return []

    api_key, cse_id = _get_cse_credentials()
    if not api_key or not cse_id:
        print("  Google CSE not configured (need PAGESPEED_API_KEY + GOOGLE_CSE_ID)", flush=True)
        return []

    raw_results = _cse_search(query, num=limit, api_key=api_key, cse_id=cse_id)

    leads = []
    today = date.today().isoformat()

    for result in raw_results:
        url = (result.get("link") or "").strip()

        # Only process LinkedIn profile URLs
        if "linkedin.com/in/" not in url:
            continue

        title = (result.get("title") or "").strip()
        snippet = (result.get("snippet") or "").strip()

        full_name, role, company = parse_linkedin_name_from_snippet(title, snippet)
        if not full_name:
            continue

        name_parts = full_name.split()
        first_name = name_parts[0] if name_parts else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        leads.append({
            "source": "google_search",
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "title": role,
            "company": company,
            "company_size": "",
            "industry": "",
            "company_website": "",
            "linkedin_url": url,
            "company_linkedin": "",
            "instagram_url": "",
            "instagram_handle": "",
            "email": "",
            "email_verified": "",
            "location": "",
            "pain_signal": "",
            "pain_keywords": "",
            "recent_activity": snippet[:300] if snippet else "",
            "funding_signal": False,
            "date_discovered": today,
        })

    return leads


def _extract_instagram_from_text(text: str) -> tuple[str, str]:
    """Extract first Instagram handle found in HTML/markdown text.

    Returns (url, handle) or ("", "").
    """
    SKIP_HANDLES = {"p", "explore", "accounts", "reel", "stories", "share", "sharer"}
    for match in re.finditer(r'instagram\.com/([^/?&#\s"\'<>]+)', text):
        handle = match.group(1).strip("/")
        if handle.lower() not in SKIP_HANDLES and len(handle) >= 2:
            return f"https://instagram.com/{handle}", handle
    return "", ""


def find_instagram_url(
    company: str,
    full_name: str,
    company_website: str = "",
    dry_run: bool = False,
) -> tuple[str, str]:
    """Find a company's Instagram profile.

    Strategy (in order):
      1. Crawl company website via Firecrawl — most reliable (links on site footer/header)
      2. Fall back to Google CSE search if Firecrawl finds nothing

    Returns:
        (instagram_url, instagram_handle) or ("", "")
    """
    if dry_run:
        return "", ""

    # --- Strategy 1: Firecrawl the company website ---
    if company_website:
        fc_key = os.environ.get("FIRECRAWL_API_KEY", "").strip()
        if fc_key:
            url = company_website if company_website.startswith("http") else f"https://{company_website}"
            try:
                resp = requests.post(
                    "https://api.firecrawl.dev/v1/scrape",
                    headers={"Authorization": f"Bearer {fc_key}", "Content-Type": "application/json"},
                    json={"url": url, "formats": ["html"], "onlyMainContent": False, "waitFor": 1000},
                    timeout=20,
                )
                if resp.status_code == 200:
                    html = (resp.json().get("data") or {}).get("html", "")
                    insta_url, handle = _extract_instagram_from_text(html)
                    if insta_url:
                        return insta_url, handle
            except requests.RequestException:
                pass

    # --- Strategy 2: Google CSE fallback ---
    api_key, cse_id = _get_cse_credentials()
    if api_key and cse_id:
        query = f'site:instagram.com "{company}" OR "{full_name}"'
        raw_results = _cse_search(query, num=5, api_key=api_key, cse_id=cse_id)
        for result in raw_results:
            url = (result.get("link") or "").strip()
            if "instagram.com/" not in url:
                continue
            match = re.search(r'instagram\.com/([^/?&#]+)', url)
            if match:
                handle = match.group(1).strip("/")
                if handle.lower() not in ("p", "explore", "accounts", "reel", "stories"):
                    return f"https://instagram.com/{handle}", handle

    return "", ""


def run(dry_run: bool = False) -> list[dict]:
    """Run all configured Google Search queries for LinkedIn profiles."""
    queries = DISCOVERY.get("google_search_queries", [])
    limit_per_query = DISCOVERY.get("google_search_limit", 10)

    if not queries:
        return []

    api_key, cse_id = _get_cse_credentials()
    if not api_key or not cse_id:
        print("\nGoogle Search Discovery: SKIPPED (GOOGLE_CSE_ID not set).", flush=True)
        print("  To enable: create a Custom Search Engine at programmablesearchengine.google.com", flush=True)
        print("  then add GOOGLE_CSE_ID=<your cx> to .env", flush=True)
        return []

    print(f"\nGoogle Search Discovery ({len(queries)} queries)...", flush=True)

    all_leads = []
    for query in queries:
        print(f"  Query: {query}", flush=True)
        leads = scrape_linkedin_profiles_via_google(query, limit=limit_per_query, dry_run=dry_run)
        print(f"    Found {len(leads)} LinkedIn profiles.", flush=True)
        all_leads.extend(leads)
        time.sleep(0.5)  # polite delay between queries

    print(f"Google Search total: {len(all_leads)} leads before dedup.", flush=True)
    return all_leads

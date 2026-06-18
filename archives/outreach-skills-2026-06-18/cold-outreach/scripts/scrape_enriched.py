#!/usr/bin/env python3
"""Multi-actor lead scraper — fetches leads that already include emails.

Two actors (both official Apify, free plan API access):

  - contact_pages  → reads company websites from Raw Leads, scrapes /contact
                     pages for emails using apify~cheerio-scraper → "LF Leads" tab
  - google_search  → searches Google for companies + emails → "GSearch Leads" tab

Results merged (deduplicated by email) into Enriched Leads with Status="Ready".

Usage:
    python scrape_enriched.py                          # enrich Raw Leads via contact scraper
    python scrape_enriched.py --actors google_search --query "operations manager" --limit 50
    python scrape_enriched.py --actors contact_pages,google_search --query "ops manager"
    python scrape_enriched.py --test                   # dry run, print without saving
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gws_utils import (
    get_or_create_sheet, append_rows, read_all_rows,
    TAB_RAW, TAB_ENRICHED, TAB_LF, TAB_GSEARCH,
    ENRICHED_HEADERS, ACTOR_HEADERS,
    col_index
)

APIFY_BASE = "https://api.apify.com/v2"

PAIN_KEYWORDS = [
    "manual", "data entry", "spreadsheet", "excel", "tracking", "reporting",
    "copy-paste", "copy paste", "update records", "maintain records",
    "data management", "administrative", "repetitive", "time-consuming"
]

ACTOR_SLUGS = {
    "contact_pages": "apify~cheerio-scraper",
    "google_search": "apify~google-search-scraper",
}

ACTOR_TABS = {
    "contact_pages": TAB_LF,
    "google_search": TAB_GSEARCH,
}

EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
EMAIL_EXTRACT = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')

# Noise emails to filter out (image filenames, CDN, logging services)
EMAIL_NOISE = re.compile(r'(@2x|\.png|\.jpg|\.gif|\.svg|sentry\.|@example\.|@test\.)', re.IGNORECASE)


# ---------------------------------------------------------------------------
# Apify helpers
# ---------------------------------------------------------------------------

def apify_run(actor_slug, input_data, api_key, timeout=600, limit=200):
    """Start an Apify actor run, wait for completion, return dataset items."""
    headers = {"Content-Type": "application/json"}
    params = {"token": api_key}

    resp = requests.post(
        f"{APIFY_BASE}/acts/{actor_slug}/runs",
        headers=headers, params=params,
        json=input_data, timeout=30
    )
    if resp.status_code in (402, 403):
        print(f"\nApify credits exhausted or forbidden (HTTP {resp.status_code}).", file=sys.stderr)
        print("Upgrade at: https://console.apify.com/billing", file=sys.stderr)
        return []
    if not resp.ok:
        print(f"  Actor start failed ({resp.status_code}): {resp.text[:300]}", file=sys.stderr)
        return []

    run_id = resp.json()["data"]["id"]
    print(f"  Run started: {run_id}", flush=True)

    status = "RUNNING"
    deadline = time.time() + timeout
    status_resp = None
    while time.time() < deadline:
        time.sleep(10)
        try:
            status_resp = requests.get(
                f"{APIFY_BASE}/actor-runs/{run_id}",
                params=params, timeout=15
            )
            status_resp.raise_for_status()
            status = status_resp.json()["data"]["status"]
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code >= 500:
                print(f"  Poll error (retrying): {e}", flush=True)
                continue
            raise
        print(f"  Status: {status}", flush=True)
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            break

    if status == "FAILED":
        print(f"  Actor run {run_id} failed.", file=sys.stderr)
        return []

    if status == "RUNNING":
        print(f"  Timeout reached. Aborting and using partial results...", flush=True)
        requests.post(f"{APIFY_BASE}/actor-runs/{run_id}/abort", params=params, timeout=10)
        time.sleep(3)

    if not status_resp:
        return []

    dataset_id = status_resp.json()["data"]["defaultDatasetId"]
    items_resp = requests.get(
        f"{APIFY_BASE}/datasets/{dataset_id}/items",
        params={**params, "format": "json", "clean": "true", "limit": limit},
        timeout=30
    )
    items_resp.raise_for_status()
    return items_resp.json()


# ---------------------------------------------------------------------------
# Pain signal
# ---------------------------------------------------------------------------

def extract_pain_signal(text):
    if not text:
        return ""
    text_lower = text.lower()
    found = [kw for kw in PAIN_KEYWORDS if kw in text_lower]
    if not found:
        return ""
    if "data entry" in found or "copy-paste" in found or "copy paste" in found:
        return "Team is doing manual data entry or copy-paste work that could be automated."
    if "spreadsheet" in found or "excel" in found:
        return "Team is managing data manually in spreadsheets instead of automated systems."
    if "tracking" in found or "reporting" in found:
        return "Team is spending time on manual tracking and reporting tasks."
    if "administrative" in found or "repetitive" in found:
        return "Role involves repetitive administrative tasks — strong automation signal."
    return f"Manual process signals detected: {', '.join(found[:3])}."


def clean_emails(raw_emails):
    """Filter and deduplicate a list of raw email strings."""
    seen = set()
    result = []
    for e in raw_emails:
        e = e.lower().strip(".")
        if not EMAIL_RE.match(e):
            continue
        if EMAIL_NOISE.search(e):
            continue
        if e in seen:
            continue
        seen.add(e)
        result.append(e)
    return result


# ---------------------------------------------------------------------------
# Actor: contact_pages — scrape company /contact pages using Raw Leads websites
# ---------------------------------------------------------------------------

CONTACT_PAGE_FN = r"""
async function pageFunction(context) {
    const $ = context.$;
    const body = $('body').html() || '';
    const text = $('body').text() || '';
    const combined = body + ' ' + text;
    const emailRegex = /[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}/g;
    const raw = combined.match(emailRegex) || [];
    const emails = [...new Set(raw.map(e => e.toLowerCase()))]
        .filter(e => !/@2x|\.png|\.jpg|\.gif|\.svg|sentry\.|@example\.|@test\./.test(e));
    return { url: context.request.url, emails };
}
"""


def build_contact_page_urls(raw_leads_rows):
    """
    For each raw lead with a company website, generate candidate URLs to scrape.
    Returns list of (url, company_index) tuples.
    """
    website_col = col_index(TAB_RAW, "Company Website")
    company_col = col_index(TAB_RAW, "Company")
    urls = []

    for i, row in enumerate(raw_leads_rows):
        website = row[website_col].strip() if len(row) > website_col else ""
        company = row[company_col].strip() if len(row) > company_col else ""
        if not website or not company:
            continue

        # Normalize URL
        if not website.startswith("http"):
            website = "https://" + website

        base = website.rstrip("/")
        # Try root + common contact paths
        for path in ["", "/contact", "/contact-us", "/about", "/team", "/about-us"]:
            urls.append((base + path, i))

    return urls


def run_contact_pages_actor(raw_leads_rows, api_key, limit=200):
    """Scrape contact pages from Raw Leads company websites. Returns list of leads."""
    url_pairs = build_contact_page_urls(raw_leads_rows)
    if not url_pairs:
        print("  No company websites found in Raw Leads.", flush=True)
        return []

    print(f"  Scraping {len(url_pairs)} URLs from {len(raw_leads_rows)} companies...", flush=True)

    start_urls = [{"url": url} for url, _ in url_pairs]
    input_data = {
        "startUrls": start_urls[:limit],
        "pageFunction": CONTACT_PAGE_FN,
        "maxRequestsPerCrawl": min(len(start_urls), limit),
    }

    items = apify_run("apify~cheerio-scraper", input_data, api_key, timeout=600, limit=limit)
    print(f"  Pages scraped: {len(items)}", flush=True)

    # Build URL → index map for matching
    url_to_idx = {}
    for url, idx in url_pairs:
        # Map both exact URL and normalized
        url_to_idx[url.lower().rstrip("/")] = idx

    # Get company info columns
    company_col = col_index(TAB_RAW, "Company")
    first_col = col_index(TAB_RAW, "First Name")
    last_col = col_index(TAB_RAW, "Last Name")
    title_col = col_index(TAB_RAW, "Decision Maker Title")
    linkedin_col = col_index(TAB_RAW, "LinkedIn URL")
    pain_col = col_index(TAB_RAW, "Pain Signal")

    def get_raw(row, col):
        return row[col].strip() if col >= 0 and len(row) > col else ""

    # Collect emails per company index
    company_emails = {}  # idx → [email, ...]
    for item in items:
        page_url = (item.get("url") or "").lower().rstrip("/")
        raw_emails = item.get("emails") or []
        emails = clean_emails(raw_emails)
        if not emails:
            continue

        # Match page URL back to a company
        matched_idx = None
        for candidate_url, idx in url_pairs:
            if candidate_url.lower().rstrip("/") == page_url:
                matched_idx = idx
                break

        if matched_idx is None:
            # Try partial match (base domain)
            try:
                page_domain = urlparse(page_url).netloc
                for candidate_url, idx in url_pairs:
                    if urlparse(candidate_url).netloc == page_domain:
                        matched_idx = idx
                        break
            except Exception:
                pass

        if matched_idx is not None:
            existing = company_emails.setdefault(matched_idx, [])
            existing.extend(emails)

    # Build leads from matched emails
    leads = []
    for idx, emails in company_emails.items():
        row = raw_leads_rows[idx]
        emails = clean_emails(emails)
        if not emails:
            continue
        email = emails[0]  # use first (most likely to be a real contact email)

        company = get_raw(row, company_col)
        first_name = get_raw(row, first_col)
        last_name = get_raw(row, last_col)
        title = get_raw(row, title_col)
        linkedin = get_raw(row, linkedin_col)
        pain = get_raw(row, pain_col)

        leads.append({
            "first_name": first_name,
            "last_name": last_name,
            "title": title,
            "company": company,
            "email": email,
            "linkedin_url": linkedin,
            "pain_signal": pain,
            "source": "contact_pages",
        })

    return leads


# ---------------------------------------------------------------------------
# Actor: google_search — find companies + emails from SERP
# ---------------------------------------------------------------------------

def build_input_google_search(query, _location, limit):
    """Build Google Search actor input. Returns input dict."""
    # Multiple targeted queries to maximize email hits
    queries = "\n".join([
        f'"{query}" email contact "@"',
        f'"{query}" "email:" site:linkedin.com OR inurl:contact',
        f'"{query}" "@" hiring -job -jobs -careers',
    ])
    return {
        "queries": queries,
        "maxPagesPerQuery": max(1, limit // 30),
        "resultsPerPage": 10,
        "countryCode": "us",
    }


def parse_google_search(items):
    """Parse Google Search Results Scraper output — extract emails from snippets."""
    leads = []
    for item in items:
        organic = item.get("organicResults") or []
        for result in organic:
            description = result.get("description") or result.get("snippet") or ""
            title_text = result.get("title") or ""
            full_text = f"{title_text} {description}"

            emails_found = EMAIL_EXTRACT.findall(full_text)
            emails = clean_emails(emails_found)
            if not emails:
                continue

            email = emails[0]
            company = title_text.split("|")[0].split("-")[0].strip() if title_text else ""
            leads.append({
                "first_name": "",
                "last_name": "",
                "title": "",
                "company": company[:100],
                "email": email,
                "linkedin_url": result.get("url") or "",
                "pain_signal": extract_pain_signal(description),
                "source": "google_search",
            })

    return leads


# ---------------------------------------------------------------------------
# Sheets helpers
# ---------------------------------------------------------------------------

def load_existing_emails(sheet_id, tab):
    """Return set of lowercase emails already in a tab."""
    rows = read_all_rows(sheet_id, tab)
    email_col = col_index(tab, "Email")
    if email_col < 0:
        return set()
    return {
        row[email_col].lower().strip()
        for row in rows
        if len(row) > email_col and row[email_col]
    }


def build_actor_row(lead, today):
    return [
        lead["first_name"],
        lead["last_name"],
        lead["title"],
        lead["company"],
        lead["email"],
        lead["linkedin_url"],
        lead["pain_signal"],
        today,
        lead["source"],
    ]


def build_enriched_row(lead):
    return [
        lead["first_name"],
        lead["last_name"],
        lead["title"],
        lead["company"],
        lead["email"],
        "Unverified",
        lead["linkedin_url"],
        lead["pain_signal"],
        "",            # Enrolled
        "", "", "", "", # Email 1-4 Dates
        "Ready",       # Status
        "",            # Reply Date
        lead["source"],
    ]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Multi-actor lead scraper with built-in emails")
    parser.add_argument("--query", default="operations manager",
                        help="Search query for google_search actor (default: 'operations manager')")
    parser.add_argument("--location", default="United States", help="Location filter")
    parser.add_argument("--limit", type=int, default=100, help="Max items per actor (default 100)")
    parser.add_argument("--actors", default="contact_pages,google_search",
                        help="Comma-separated actors (default: contact_pages,google_search)")
    parser.add_argument("--test", action="store_true", help="Dry run — print results without saving")
    args = parser.parse_args()

    api_key = os.environ.get("APIFY_API_KEY", "").strip()
    if not api_key:
        print("Error: APIFY_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    actors_to_run = [a.strip() for a in args.actors.split(",") if a.strip() in ACTOR_SLUGS]
    if not actors_to_run:
        print(f"Error: no valid actors. Valid: {', '.join(ACTOR_SLUGS)}", file=sys.stderr)
        sys.exit(1)

    print("Cold Outreach — Multi-Actor Lead Scraper")
    print(f"Actors: {', '.join(actors_to_run)} | Limit: {args.limit}/actor")
    print("-" * 40)

    sheet_id = get_or_create_sheet()
    print(f"CRM: https://docs.google.com/spreadsheets/d/{sheet_id}\n")

    today = date.today().isoformat()
    total_actor_saved = 0
    total_new_enriched = 0

    existing_enriched_emails = load_existing_emails(sheet_id, TAB_ENRICHED)
    seen_this_run = set()

    # Load Raw Leads once (used by contact_pages actor)
    raw_leads_rows = None
    if "contact_pages" in actors_to_run:
        raw_leads_rows = read_all_rows(sheet_id, TAB_RAW)
        status_col = col_index(TAB_RAW, "Status")
        # Only process Unprocessed leads with a company website
        website_col = col_index(TAB_RAW, "Company Website")
        raw_leads_rows = [
            r for r in raw_leads_rows
            if len(r) > status_col and r[status_col] == "Unprocessed"
            and len(r) > website_col and r[website_col].strip()
        ]
        print(f"Raw Leads available for contact scraping: {len(raw_leads_rows)}\n", flush=True)

    for actor_name in actors_to_run:
        tab = ACTOR_TABS[actor_name]
        print(f"\n[{actor_name}]", flush=True)

        # Run actor
        try:
            if actor_name == "contact_pages":
                if not raw_leads_rows:
                    print("  No unprocessed leads with websites. Add leads via scrape_leads.py first.")
                    continue
                leads = run_contact_pages_actor(raw_leads_rows, api_key, limit=args.limit * 6)
            elif actor_name == "google_search":
                print(f"  Query: '{args.query}'", flush=True)
                input_data = build_input_google_search(args.query, args.location, args.limit)
                items = apify_run(ACTOR_SLUGS[actor_name], input_data, api_key,
                                  timeout=300, limit=args.limit * 3)
                print(f"  Raw SERP results: {len(items)}", flush=True)
                leads = parse_google_search(items)
            else:
                continue
        except Exception as e:
            print(f"  Actor failed: {e}", file=sys.stderr)
            continue

        print(f"  Leads with valid email: {len(leads)}", flush=True)

        if not leads:
            print(f"  No email leads from {actor_name}.", flush=True)
            continue

        existing_actor_emails = load_existing_emails(sheet_id, tab)
        actor_new = []
        enriched_new = []

        for lead in leads:
            email = lead["email"]
            if email in existing_actor_emails or email in seen_this_run:
                continue
            existing_actor_emails.add(email)
            seen_this_run.add(email)
            actor_new.append(lead)

            if email not in existing_enriched_emails:
                existing_enriched_emails.add(email)
                enriched_new.append(lead)

        print(f"  New to actor tab: {len(actor_new)}", flush=True)
        print(f"  New to Enriched Leads: {len(enriched_new)}", flush=True)

        if args.test:
            for lead in actor_new[:5]:
                print(f"    {lead['company']} | {lead['email']} | {lead['first_name']} {lead['last_name']}")
        else:
            if actor_new:
                append_rows(sheet_id, tab, [build_actor_row(l, today) for l in actor_new])
                total_actor_saved += len(actor_new)
            if enriched_new:
                append_rows(sheet_id, TAB_ENRICHED, [build_enriched_row(l) for l in enriched_new])
                total_new_enriched += len(enriched_new)

    print("\n" + "-" * 40)
    if args.test:
        print("DRY RUN — no data written.")
    else:
        print(f"Done.")
        print(f"  Leads saved to actor tabs:    {total_actor_saved}")
        print(f"  New entries in Enriched Leads: {total_new_enriched}")
        print(f"  CRM: https://docs.google.com/spreadsheets/d/{sheet_id}")
        if total_new_enriched > 0:
            print(f"  Next step: Run 'send emails' to start the sequence.")

    print(json.dumps({
        "status": "ok",
        "actor_saved": total_actor_saved,
        "enriched_new": total_new_enriched,
        "sheet_id": sheet_id,
    }))


if __name__ == "__main__":
    main()

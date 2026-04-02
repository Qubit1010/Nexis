#!/usr/bin/env python3
"""Scrape leads via Apify LinkedIn Jobs + Profile scrapers.

Calls Apify API to run LinkedIn Jobs Scraper, extracts companies + pain signals,
then runs LinkedIn Profile Scraper to find decision maker names, and appends
everything to the Google Sheets CRM "Raw Leads" tab.

Usage:
    python scrape_leads.py --query "operations manager" --limit 50
    python scrape_leads.py --query "data entry" --industry "saas" --limit 100

Required env var:
    APIFY_API_KEY  — your Apify API token (free tier is fine)
"""

import argparse
import json
import os
import sys
import time
import re
from datetime import date
from pathlib import Path

import requests

# Add parent scripts dir to path for gws_utils
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gws_utils import (
    get_or_create_sheet, append_rows, read_all_rows,
    TAB_RAW, col_index
)

# ---------------------------------------------------------------------------
# Apify actor IDs (official Apify actors, free to use on free tier)
# ---------------------------------------------------------------------------
JOBS_ACTOR = "hKByXkMQaC5Qt9UMN"   # LinkedIn Jobs Scraper by curious_coder
PROFILE_ACTOR = "2SyF0bVxmgGr8IVCZ"  # LinkedIn Profile Scraper by Apify

APIFY_BASE = "https://api.apify.com/v2"

# Pain signal keywords — if job description contains these, company has a bottleneck
PAIN_KEYWORDS = [
    "manual", "data entry", "spreadsheet", "excel", "tracking", "reporting",
    "copy-paste", "copy paste", "update records", "maintain records",
    "data management", "administrative", "repetitive", "time-consuming"
]


# ---------------------------------------------------------------------------
# Apify helpers
# ---------------------------------------------------------------------------

def apify_run(actor_id, input_data, api_key, timeout=600):
    """Start an Apify actor run, wait for completion, return dataset items."""
    headers = {"Content-Type": "application/json"}
    params = {"token": api_key}

    # Start run
    resp = requests.post(
        f"{APIFY_BASE}/acts/{actor_id}/runs",
        headers=headers, params=params,
        json=input_data, timeout=30
    )
    resp.raise_for_status()
    run_id = resp.json()["data"]["id"]
    print(f"  Apify run started: {run_id}", flush=True)

    # Poll until finished
    status = "RUNNING"
    deadline = time.time() + timeout
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
        raise RuntimeError(f"Apify run {run_id} failed.")

    if status in ("RUNNING",):
        # Still running at deadline — abort and use partial data
        print(f"  Timeout reached. Aborting and using partial results...", flush=True)
        requests.post(f"{APIFY_BASE}/actor-runs/{run_id}/abort", params=params, timeout=10)
        time.sleep(3)

    # SUCCEEDED, ABORTED, TIMED-OUT: fetch partial or full results
    # Fetch results — limit at dataset level since maxJobs is a soft cap
    dataset_id = status_resp.json()["data"]["defaultDatasetId"]
    items_resp = requests.get(
        f"{APIFY_BASE}/datasets/{dataset_id}/items",
        params={**params, "format": "json", "clean": "true", "limit": input_data.get("maxJobs", 50)},
        timeout=30
    )
    items_resp.raise_for_status()
    return items_resp.json()


# ---------------------------------------------------------------------------
# Pain signal extraction
# ---------------------------------------------------------------------------

def extract_pain_signal(description):
    """Scan job description for pain keywords, return 1-sentence signal."""
    if not description:
        return ""
    desc_lower = description.lower()
    found = [kw for kw in PAIN_KEYWORDS if kw in desc_lower]
    if not found:
        return ""
    # Build a natural sentence from what was found
    if "data entry" in found or "copy-paste" in found or "copy paste" in found:
        return "Team is doing manual data entry or copy-paste work that could be automated."
    if "spreadsheet" in found or "excel" in found:
        return "Team is managing data manually in spreadsheets instead of automated systems."
    if "tracking" in found or "reporting" in found:
        return "Team is spending time on manual tracking and reporting tasks."
    if "administrative" in found or "repetitive" in found:
        return "Role involves repetitive administrative tasks — strong automation signal."
    return f"Manual process signals detected: {', '.join(found[:3])}."


# ---------------------------------------------------------------------------
# LinkedIn Jobs Scraper
# ---------------------------------------------------------------------------

def scrape_jobs(query, limit, api_key):
    """Run LinkedIn Jobs Scraper and return list of company dicts."""
    import urllib.parse
    print(f"\nScraping LinkedIn Jobs for: '{query}' (limit {limit})...", flush=True)

    search_url = f"https://www.linkedin.com/jobs/search/?keywords={urllib.parse.quote(query)}"
    # maxJobs is a soft hint to the actor; actual limiting is done at dataset fetch
    input_data = {
        "urls": [search_url],
        "maxJobs": limit,
    }

    try:
        items = apify_run(JOBS_ACTOR, input_data, api_key)
    except Exception as e:
        print(f"  Jobs scraper failed: {e}", file=sys.stderr)
        return []

    companies = []
    for item in items:
        company_name = item.get("companyName", "").strip()
        if not company_name:
            continue

        company_url = item.get("companyLinkedinUrl", "").strip()
        company_website = item.get("companyWebsite", "").strip()
        job_title = item.get("title", "") or query
        description = item.get("descriptionText", "") or item.get("descriptionHtml", "")
        industry = item.get("industries", "")
        if isinstance(industry, list):
            industry = ", ".join(industry)

        # Decision maker from job poster (no extra scraper needed)
        poster_name = item.get("jobPosterName", "").strip()
        poster_title = item.get("jobPosterTitle", "").strip()
        first_name = poster_name.split()[0] if poster_name else ""
        last_name = " ".join(poster_name.split()[1:]) if len(poster_name.split()) > 1 else ""

        pain_signal = extract_pain_signal(description)

        companies.append({
            "company": company_name,
            "linkedin_url": company_url,
            "company_website": company_website,
            "job_title": job_title.strip(),
            "pain_signal": pain_signal,
            "industry": str(industry).strip(),
            "first_name": first_name,
            "last_name": last_name,
            "decision_maker_title": poster_title,
        })

    # Deduplicate by company name
    seen = set()
    unique = []
    for c in companies:
        key = c["company"].lower().strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(c)

    print(f"  Found {len(unique)} unique companies.", flush=True)
    return unique


# ---------------------------------------------------------------------------
# LinkedIn Profile Scraper — find decision maker
# ---------------------------------------------------------------------------

def scrape_decision_makers(companies, api_key):
    """For each company, find founder/CEO via LinkedIn Profile Scraper."""
    if not companies:
        return companies

    print(f"\nFinding decision makers for {len(companies)} companies...", flush=True)

    # Build search URLs for each company
    profile_urls = []
    for c in companies:
        if c.get("linkedin_url"):
            # Search for people at this company
            company_slug = re.sub(r'https?://(www\.)?linkedin\.com/company/', '', c["linkedin_url"]).strip("/")
            if company_slug:
                search_url = f"https://www.linkedin.com/search/results/people/?company={company_slug}&title=founder%20OR%20CEO%20OR%20COO"
                profile_urls.append(search_url)

    if not profile_urls:
        return companies

    # Batch: only scrape first 30 to stay in free tier
    profile_urls = profile_urls[:30]
    input_data = {
        "startUrls": [{"url": u} for u in profile_urls],
        "maxProfiles": len(profile_urls) * 2,
    }

    try:
        profiles = apify_run(PROFILE_ACTOR, input_data, api_key, timeout=240)
    except Exception as e:
        print(f"  Profile scraper failed (non-fatal): {e}", file=sys.stderr)
        return companies

    # Build a map: company name -> (first_name, last_name, title)
    profile_map = {}
    for p in profiles:
        company = (p.get("currentCompany") or p.get("company") or "").lower().strip()
        first = p.get("firstName") or p.get("first_name") or ""
        last = p.get("lastName") or p.get("last_name") or ""
        title = p.get("currentTitle") or p.get("title") or ""
        if company and first:
            profile_map.setdefault(company, (first, last, title))

    # Attach to companies
    for c in companies:
        key = c["company"].lower().strip()
        if key in profile_map:
            first, last, title = profile_map[key]
            c["first_name"] = first
            c["last_name"] = last
            c["decision_maker_title"] = title

    return companies


# ---------------------------------------------------------------------------
# Write to Sheets
# ---------------------------------------------------------------------------

def write_to_sheets(companies, sheet_id):
    """Append new companies to Raw Leads tab, skip duplicates."""
    if not companies:
        return 0

    # Get existing companies to deduplicate
    existing = read_all_rows(sheet_id, TAB_RAW)
    company_col = col_index(TAB_RAW, "Company")
    existing_names = {
        row[company_col].lower().strip()
        for row in existing
        if len(row) > company_col and row[company_col]
    }

    today = date.today().isoformat()
    rows_to_add = []

    for c in companies:
        name = c["company"].lower().strip()
        if name in existing_names:
            continue
        existing_names.add(name)

        # Map to RAW_HEADERS order:
        # Company, LinkedIn URL, Job Title Posted, Pain Signal, Industry, Date Added, Status
        # Extra fields appended: Company Website, First Name, Last Name, Title
        rows_to_add.append([
            c.get("company", ""),
            c.get("linkedin_url", ""),
            c.get("job_title", ""),
            c.get("pain_signal", ""),
            c.get("industry", ""),
            today,
            "Unprocessed",
            c.get("company_website", ""),
            c.get("first_name", ""),
            c.get("last_name", ""),
            c.get("decision_maker_title", ""),
        ])

    if rows_to_add:
        append_rows(sheet_id, TAB_RAW, rows_to_add)

    return len(rows_to_add)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Scrape leads via Apify into Google Sheets CRM")
    parser.add_argument("--query", required=True, help="Job search query (e.g. 'operations manager')")
    parser.add_argument("--industry", default="", help="Industry hint for context (not a filter)")
    parser.add_argument("--limit", type=int, default=50, help="Max jobs to scrape (default 50)")
    args = parser.parse_args()

    api_key = os.environ.get("APIFY_API_KEY", "").strip()
    if not api_key:
        print("Error: APIFY_API_KEY environment variable not set.", file=sys.stderr)
        print("Get your free API key at: https://console.apify.com/account/integrations", file=sys.stderr)
        sys.exit(1)

    print(f"Cold Outreach — Lead Scraper")
    print(f"Query: '{args.query}' | Limit: {args.limit}")
    print("-" * 40)

    # Get or create CRM sheet
    print("Connecting to Google Sheets CRM...")
    sheet_id = get_or_create_sheet()
    print(f"CRM sheet ready: https://docs.google.com/spreadsheets/d/{sheet_id}")

    # Scrape jobs
    companies = scrape_jobs(args.query, args.limit, api_key)
    if not companies:
        print("\nNo companies found. Try a different query.")
        sys.exit(0)

    # Write to Sheets
    print(f"\nWriting to Google Sheets...")
    new_count = write_to_sheets(companies, sheet_id)

    print(f"\nDone.")
    print(f"  Companies scraped: {len(companies)}")
    print(f"  New leads added:   {new_count}")
    print(f"  CRM: https://docs.google.com/spreadsheets/d/{sheet_id}")

    print(json.dumps({
        "status": "ok",
        "scraped": len(companies),
        "new_leads": new_count,
        "sheet_id": sheet_id
    }))


if __name__ == "__main__":
    main()

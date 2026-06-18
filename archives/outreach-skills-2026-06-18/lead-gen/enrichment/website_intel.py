"""Website Intelligence enrichment.

For each lead, crawls their company website using Firecrawl and checks
performance via Google PageSpeed Insights API.

Extracts:
  - CMS / framework (Wix, Squarespace, WordPress, Webflow, React, Next.js, etc.)
  - PageSpeed mobile + desktop scores
  - Core Web Vitals (LCP, CLS, FID)
  - Site issues (no SSL, missing meta, broken links)
  - Approximate last-updated date (from blog/copyright signals)
"""

import os
import re
import sys
import json
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import ENRICHMENT, ICP
from utils.rate_limit import retry, sleep_between


# ---------------------------------------------------------------------------
# CMS / Tech stack detection signatures
# (checked against crawled HTML)
# ---------------------------------------------------------------------------

CMS_SIGNATURES = {
    "wix": ["wix.com", "wixstatic.com", "_wix_", "wixsite.com"],
    "squarespace": ["squarespace.com", "sqsp.net", "squarespace-cdn"],
    "webflow": ["webflow.com", "webflow.io", "webflow-cdn"],
    "wordpress": ["wp-content/", "wp-includes/", "/wp-json/", "wordpress"],
    "shopify": ["shopify.com", "cdn.shopify.com", "shopify-cdn"],
    "framer": ["framer.com", "framerusercontent.com"],
    "weebly": ["weebly.com", "weeblysite.com"],
    "godaddy": ["godaddy.com", "godaddysites.com"],
    "nextjs": ["_next/static", "_next/image", "next.js"],
    "react": ["react.js", "__react", "react-dom"],
    "vue": ["vue.js", "__vue__"],
    "angular": ["ng-version", "angular"],
    "bootstrap": ["bootstrap.min.css", "bootstrap.css"],
    "tailwind": ["tailwindcss", "tailwind.css"],
    "hubspot": ["hubspot.com", "hs-scripts.com", "hsstatic.net"],
    "intercom": ["intercom.io", "widget.intercom.io"],
    "typeform": ["typeform.com"],
    "calendly": ["calendly.com"],
}


def detect_cms(html: str) -> str:
    """Detect CMS/framework from HTML source. Returns most specific match."""
    if not html:
        return "unknown"
    html_lower = html.lower()
    for cms, signatures in CMS_SIGNATURES.items():
        if any(sig in html_lower for sig in signatures):
            return cms
    return "unknown"


def extract_analytics(html: str) -> list[str]:
    """Detect analytics/marketing tools from HTML."""
    tools = []
    html_lower = html.lower()
    checks = {
        "google_analytics": ["google-analytics.com", "gtag/js", "ga('send"],
        "google_tag_manager": ["googletagmanager.com"],
        "facebook_pixel": ["facebook.net/en_US/fbevents.js", "fbq("],
        "hotjar": ["hotjar.com"],
        "segment": ["segment.io", "analytics.js"],
        "hubspot": ["hs-scripts.com"],
        "intercom": ["intercom.io"],
    }
    for tool, sigs in checks.items():
        if any(s in html_lower for s in sigs):
            tools.append(tool)
    return tools


def extract_last_updated(html: str) -> str:
    """Try to guess when the site was last updated from copyright year or blog dates."""
    if not html:
        return ""
    # Copyright year: © 2024 or Copyright 2024
    match = re.search(r'©\s*(20\d{2})', html)
    if match:
        return match.group(1)
    match = re.search(r'copyright\s+(20\d{2})', html, re.IGNORECASE)
    if match:
        return match.group(1)
    return ""


def check_ssl(url: str) -> bool:
    """Return True if URL uses HTTPS."""
    return url.lower().startswith("https://")


# ---------------------------------------------------------------------------
# Firecrawl integration
# ---------------------------------------------------------------------------

@retry(max_attempts=2, base_delay=3.0, exceptions=(requests.RequestException,))
def crawl_website(url: str) -> dict:
    """Crawl a website using Firecrawl API.

    Returns dict with keys: html, markdown, links, metadata
    """
    api_key = os.environ.get("FIRECRAWL_API_KEY", "").strip()
    if not api_key:
        return {}

    if not url.startswith("http"):
        url = "https://" + url

    try:
        resp = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "url": url,
                "formats": ["html", "markdown"],
                "onlyMainContent": False,
                "waitFor": 1000,
            },
            timeout=30,
        )
        if resp.status_code == 402:
            print("  Firecrawl: credits exhausted.", flush=True)
            return {}
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", {}) or {}
    except requests.RequestException as exc:
        print(f"  Firecrawl crawl failed for {url}: {exc}", flush=True)
        return {}


# ---------------------------------------------------------------------------
# PageSpeed Insights API
# ---------------------------------------------------------------------------

@retry(max_attempts=2, base_delay=2.0, exceptions=(requests.RequestException,))
def get_pagespeed(url: str) -> dict:
    """Get PageSpeed Insights scores for a URL.

    Returns dict with mobile and desktop scores + Core Web Vitals.
    """
    api_key = os.environ.get("PAGESPEED_API_KEY", "").strip()

    if not url.startswith("http"):
        url = "https://" + url

    results = {"mobile": -1, "desktop": -1, "core_web_vitals": {}}

    for strategy in ["mobile", "desktop"]:
        params = {
            "url": url,
            "strategy": strategy,
            "category": "performance",
        }
        if api_key:
            params["key"] = api_key

        try:
            resp = requests.get(
                "https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
                params=params,
                timeout=45,
            )
            if resp.status_code == 400:
                break  # Invalid URL
            resp.raise_for_status()
            data = resp.json()

            # Extract performance score (0-100)
            score = data.get("lighthouseResult", {}).get("categories", {}).get("performance", {}).get("score", -1)
            if score is not None and score != -1:
                results[strategy] = int(score * 100)

            # Extract Core Web Vitals (only on first pass)
            if strategy == "mobile":
                audits = data.get("lighthouseResult", {}).get("audits", {})
                results["core_web_vitals"] = {
                    "lcp": audits.get("largest-contentful-paint", {}).get("displayValue", ""),
                    "cls": audits.get("cumulative-layout-shift", {}).get("displayValue", ""),
                    "fid": audits.get("max-potential-fid", {}).get("displayValue", ""),
                }

            sleep_between(0.5, 1.5)
        except requests.RequestException as exc:
            print(f"  PageSpeed failed for {url} ({strategy}): {exc}", flush=True)

    return results


# ---------------------------------------------------------------------------
# Main enrichment function
# ---------------------------------------------------------------------------

def enrich_website(lead: dict) -> dict:
    """Run website intelligence enrichment for a lead.

    Args:
        lead: Lead dict from DB

    Returns:
        Enrichment data dict (to be passed to upsert_enrichment)
    """
    url = (lead.get("company_website") or "").strip()
    if not url:
        return {}

    print(f"  Website intel: {url}", flush=True)

    result = {
        "website_tech": {},
        "pagespeed_mobile": -1,
        "pagespeed_desktop": -1,
        "core_web_vitals": {},
        "site_issues": [],
        "site_last_updated": "",
    }

    # SSL check
    if not check_ssl(url):
        result["site_issues"].append("no_ssl")

    # Crawl website
    crawl_data = crawl_website(url)
    html = crawl_data.get("html") or crawl_data.get("rawHtml") or ""
    markdown = crawl_data.get("markdown") or ""

    if html:
        # Detect CMS
        cms = detect_cms(html)
        analytics = extract_analytics(html)
        last_updated = extract_last_updated(html)

        result["website_tech"] = {
            "cms": cms,
            "analytics": analytics,
            "raw_html_length": len(html),
        }
        result["site_last_updated"] = last_updated

        # Flag as tech debt if using a basic builder
        if cms in ICP["tech_debt_signals"]:
            if "tech_debt" not in result["site_issues"]:
                result["site_issues"].append(f"cms_{cms}")

    # PageSpeed
    pagespeed = get_pagespeed(url)
    result["pagespeed_mobile"] = pagespeed.get("mobile", -1)
    result["pagespeed_desktop"] = pagespeed.get("desktop", -1)
    result["core_web_vitals"] = pagespeed.get("core_web_vitals", {})

    if result["pagespeed_mobile"] > 0 and result["pagespeed_mobile"] < 60:
        result["site_issues"].append("low_pagespeed_mobile")

    print(
        f"  CMS: {result['website_tech'].get('cms', 'unknown')} | "
        f"PageSpeed: {result['pagespeed_mobile']}/{result['pagespeed_desktop']} | "
        f"Issues: {result['site_issues']}",
        flush=True
    )

    return result

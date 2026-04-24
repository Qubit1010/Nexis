#!/usr/bin/env python3
"""Crawl a prospect's website via the Firecrawl API.

Quick mode: scrapes only the homepage.
Deep mode: crawls homepage + up to N internal pages (about, services, pricing, contact).

Usage:
    python crawl_site.py --url https://example.com --mode quick
    python crawl_site.py --url https://example.com --mode deep --max-pages 8

Requires FIRECRAWL_API_KEY in the environment. If missing, exits with an error
so the caller (SKILL.md) can fall back to invoking the Firecrawl MCP tool
directly and passing the data in via analyze_audit.py --crawl-file.

Output (stdout): JSON
    {
      "status": "ok",
      "mode": "quick" | "deep",
      "url": "...",
      "pages": [
        {"url": "...", "markdown": "...", "html_snippet": "...", "metadata": {...}}
      ]
    }
"""

import argparse
import json
import os
import sys
import time

try:
    import requests
except ImportError:
    print(json.dumps({"status": "error", "message": "requests package not installed. Run: pip install requests"}))
    sys.exit(1)


FIRECRAWL_SCRAPE = "https://api.firecrawl.dev/v1/scrape"
FIRECRAWL_CRAWL = "https://api.firecrawl.dev/v1/crawl"

# We only care about HTML head + key meta signals, not the full DOM.
# Keep ~60KB per page to stay within downstream LLM token budgets.
HTML_SNIPPET_CHARS = 60_000
MARKDOWN_SNIPPET_CHARS = 40_000


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith("http"):
        url = "https://" + url
    return url.rstrip("/")


def scrape_page(url: str, api_key: str) -> dict:
    """Scrape a single page via Firecrawl /v1/scrape."""
    resp = requests.post(
        FIRECRAWL_SCRAPE,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "url": url,
            "formats": ["html", "markdown"],
            "onlyMainContent": False,
            "waitFor": 1500,
        },
        timeout=45,
    )
    if resp.status_code == 402:
        raise RuntimeError("Firecrawl credits exhausted")
    if resp.status_code == 401:
        raise RuntimeError("Firecrawl API key invalid")
    resp.raise_for_status()
    data = resp.json().get("data", {}) or {}
    return {
        "url": data.get("metadata", {}).get("sourceURL") or url,
        "markdown": (data.get("markdown") or "")[:MARKDOWN_SNIPPET_CHARS],
        "html_snippet": (data.get("html") or data.get("rawHtml") or "")[:HTML_SNIPPET_CHARS],
        "metadata": data.get("metadata") or {},
    }


def crawl_multi(url: str, api_key: str, max_pages: int) -> list:
    """Start a Firecrawl crawl job and poll until complete or timeout."""
    resp = requests.post(
        FIRECRAWL_CRAWL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "url": url,
            "limit": max_pages,
            "maxDepth": 2,
            "scrapeOptions": {
                "formats": ["html", "markdown"],
                "onlyMainContent": False,
            },
        },
        timeout=30,
    )
    if resp.status_code == 402:
        raise RuntimeError("Firecrawl credits exhausted")
    resp.raise_for_status()
    job = resp.json()
    job_id = job.get("id")
    if not job_id:
        raise RuntimeError(f"Firecrawl crawl did not return a job id: {job}")

    status_url = f"{FIRECRAWL_CRAWL}/{job_id}"
    deadline = time.time() + 180  # 3 min cap
    pages = []
    while time.time() < deadline:
        time.sleep(4)
        status = requests.get(
            status_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )
        status.raise_for_status()
        body = status.json()
        state = body.get("status")
        if state == "completed":
            for item in body.get("data", []) or []:
                pages.append({
                    "url": item.get("metadata", {}).get("sourceURL") or "",
                    "markdown": (item.get("markdown") or "")[:MARKDOWN_SNIPPET_CHARS],
                    "html_snippet": (item.get("html") or item.get("rawHtml") or "")[:HTML_SNIPPET_CHARS],
                    "metadata": item.get("metadata") or {},
                })
            return pages
        if state == "failed":
            raise RuntimeError(f"Firecrawl crawl failed: {body.get('error')}")

    raise RuntimeError("Firecrawl crawl timed out after 3 minutes")


def main():
    parser = argparse.ArgumentParser(description="Crawl a prospect site via Firecrawl")
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument("--mode", choices=["quick", "deep"], default="quick")
    parser.add_argument("--max-pages", type=int, default=8,
                        help="Max pages for deep mode (default 8)")
    args = parser.parse_args()

    api_key = os.environ.get("FIRECRAWL_API_KEY", "").strip()
    if not api_key:
        print(json.dumps({
            "status": "error",
            "message": "FIRECRAWL_API_KEY not set. Either set the env var, or have the caller use the Firecrawl MCP tool and pass the result to analyze_audit.py --crawl-file.",
        }))
        sys.exit(1)

    url = normalize_url(args.url)

    try:
        if args.mode == "quick":
            pages = [scrape_page(url, api_key)]
        else:
            pages = crawl_multi(url, api_key, args.max_pages)
            if not pages:
                # Deep crawl returned nothing (small site, or blocked) — fall back to homepage scrape
                pages = [scrape_page(url, api_key)]
    except (requests.RequestException, RuntimeError) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}))
        sys.exit(1)

    print(json.dumps({
        "status": "ok",
        "mode": args.mode,
        "url": url,
        "page_count": len(pages),
        "pages": pages,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

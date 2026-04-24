#!/usr/bin/env python3
"""Fetch PageSpeed Insights scores + Core Web Vitals for a URL.

Usage:
    python pagespeed.py --url https://example.com

Optional PAGESPEED_API_KEY env var increases daily quota. Without a key,
Google still responds but is stricter on rate limits.

Output (stdout): JSON
    {
      "status": "ok" | "partial" | "error",
      "url": "...",
      "mobile": {"score": 0-100, "lcp": "...", "cls": "...", "tbt": "...", "fcp": "...", "si": "..."},
      "desktop": {"score": 0-100, ...},
      "notes": "..."
    }

Score of -1 means "not measured". The caller should handle both mobile and
desktop being -1 by marking performance as "unavailable" in the audit.
"""

import argparse
import json
import os
import sys

try:
    import requests
except ImportError:
    print(json.dumps({"status": "error", "message": "requests package not installed. Run: pip install requests"}))
    sys.exit(1)


PAGESPEED_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith("http"):
        url = "https://" + url
    return url


def fetch_strategy(url: str, strategy: str, api_key: str) -> dict:
    """Fetch one strategy (mobile or desktop) from PageSpeed Insights."""
    params = {"url": url, "strategy": strategy, "category": "performance"}
    if api_key:
        params["key"] = api_key

    try:
        resp = requests.get(PAGESPEED_URL, params=params, timeout=60)
    except requests.RequestException as exc:
        return {"score": -1, "error": str(exc)}

    if resp.status_code == 400:
        return {"score": -1, "error": "PageSpeed returned 400 (invalid URL or not crawlable)"}
    if resp.status_code == 429:
        return {"score": -1, "error": "PageSpeed rate-limited (429). Try again later or set PAGESPEED_API_KEY."}
    if resp.status_code != 200:
        return {"score": -1, "error": f"PageSpeed HTTP {resp.status_code}"}

    data = resp.json()
    lighthouse = data.get("lighthouseResult", {}) or {}
    categories = lighthouse.get("categories", {}) or {}
    perf = categories.get("performance", {}) or {}
    raw_score = perf.get("score")
    score = int(raw_score * 100) if isinstance(raw_score, (int, float)) else -1

    audits = lighthouse.get("audits", {}) or {}

    def display(audit_id):
        return (audits.get(audit_id, {}) or {}).get("displayValue", "")

    return {
        "score": score,
        "lcp": display("largest-contentful-paint"),
        "cls": display("cumulative-layout-shift"),
        "tbt": display("total-blocking-time"),
        "fcp": display("first-contentful-paint"),
        "si": display("speed-index"),
    }


def main():
    parser = argparse.ArgumentParser(description="PageSpeed Insights audit")
    parser.add_argument("--url", required=True)
    args = parser.parse_args()

    url = normalize_url(args.url)
    api_key = os.environ.get("PAGESPEED_API_KEY", "").strip()

    mobile = fetch_strategy(url, "mobile", api_key)
    desktop = fetch_strategy(url, "desktop", api_key)

    both_failed = mobile.get("score") == -1 and desktop.get("score") == -1
    status = "error" if both_failed else ("partial" if -1 in (mobile.get("score"), desktop.get("score")) else "ok")

    notes = []
    if mobile.get("error"):
        notes.append(f"mobile: {mobile['error']}")
    if desktop.get("error"):
        notes.append(f"desktop: {desktop['error']}")
    if not api_key:
        notes.append("no PAGESPEED_API_KEY set (using anonymous quota)")

    print(json.dumps({
        "status": status,
        "url": url,
        "mobile": mobile,
        "desktop": desktop,
        "notes": " | ".join(notes) if notes else "",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

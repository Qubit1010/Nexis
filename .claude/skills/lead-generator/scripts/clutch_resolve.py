"""Resolve a business's real website from its Clutch.co profile page.

Clutch profiles don't publish the business's website directly - the "Visit Website" button
links to a Clutch redirect/tracking URL (`r.clutch.co/redirect?...`) that carries the real
site two ways: a clean `provider_website` domain param, and a full `u` param (with UTM params
attached). Clutch is Cloudflare-protected, so a plain http fetch gets blocked -- this uses the
web-scraper skill's own auto-escalation ladder (crawl4ai -> firecrawl -> apify -> scrapingant)
via `scrape.py`, same as the rest of this skill's website work.

Usage:
  python clutch_resolve.py --url https://clutch.co/profile/accelerated-digital-media
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

SKILLS = Path(__file__).resolve().parents[2]  # .claude/skills
WEBSCRAPER = SKILLS / "web-scraper" / "scripts" / "scrape.py"

_REDIRECT_URL = re.compile(r"https://r\.clutch\.co/redirect\?[^\s)\]]+")


def website_from_markdown(md: str) -> str:
    """Pull the real website out of Clutch's 'Visit Website' redirect URL. The link text/wrapper
    varies by fetch engine (firecrawl renders `[Visit Website](url)`, crawl4ai often wraps the
    same url in an image link `[![logo](img)](url)`) -- match on the redirect URL itself, which is
    engine-independent, and take the first one (Clutch's own "visit website" button)."""
    m = _REDIRECT_URL.search(md or "")
    if not m:
        return ""
    qs = parse_qs(urlparse(m.group(0)).query)
    domain = (qs.get("provider_website") or [""])[0]
    if domain:
        return domain if "://" in domain else f"https://{domain}"
    full = (qs.get("u") or [""])[0]
    return full.split(" ")[0] if full else ""  # strip a trailing `"Visit website"` title token


def resolve_website(clutch_url: str, timeout: int = 150) -> dict:
    """Fetch a Clutch profile (escalating through the web-scraper ladder) and extract the
    business's real website. Returns {"website": "", "engine": "", "error": ""}."""
    cmd = [sys.executable, str(WEBSCRAPER), "--url", clutch_url, "--engine", "crawl4ai",
           "--extract", "raw", "--out", "json"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"website": "", "engine": "", "error": "timeout"}
    if p.returncode != 0 or not p.stdout.strip():
        return {"website": "", "engine": "", "error": (p.stderr or "no output")[:300]}
    try:
        data = json.loads(p.stdout)
    except json.JSONDecodeError:
        return {"website": "", "engine": "", "error": "non-JSON output"}
    row = data[0] if isinstance(data, list) and data else (data if isinstance(data, dict) else {})
    website = website_from_markdown(row.get("markdown", ""))
    return {"website": website, "engine": row.get("engine", ""), "error": "" if website else "no Visit Website link found"}


def demo():
    """Self-check: markdown -> website extraction (no network), both engine renderings."""
    firecrawl_style = ('[Visit Website](https://r.clutch.co/redirect?content_group=profile&provider_website=example.com'
                        '&u=https%3A%2F%2Fwww.example.com%2Fpath%3Futm_source%3Dclutch.co "Visit website")')
    assert website_from_markdown(firecrawl_style) == "https://example.com", website_from_markdown(firecrawl_style)
    crawl4ai_style = ('[![logo](https://img.example/x.png) ](https://r.clutch.co/redirect?content_group=profile'
                      '&provider_website=another.com&u=https%3A%2F%2Fwww.another.com%2F)')
    assert website_from_markdown(crawl4ai_style) == "https://another.com", website_from_markdown(crawl4ai_style)
    assert website_from_markdown("no redirect link here") == ""
    print("clutch_resolve self-check OK")


def main():
    p = argparse.ArgumentParser(description="Resolve a business's real website from its Clutch profile.")
    p.add_argument("--url", help="Clutch profile URL")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()
    if args.selftest:
        demo()
        return
    if not args.url:
        raise SystemExit("--url is required (or pass --selftest)")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(json.dumps(resolve_website(args.url), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

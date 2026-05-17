#!/usr/bin/env python3
"""
Firecrawl extraction for the landing-rebuild skill.

Usage:
    python extract.py <url> <output-dir>

Writes into <output-dir>/extraction/:
  - page.md
  - page.html
  - metadata.json
  - firecrawl-screenshot.png (may be small/empty — Playwright provides the real one)
  - slug.txt  (derived site slug for downstream naming)
"""

import base64
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


FIRECRAWL_SCRAPE = "https://api.firecrawl.dev/v1/scrape"


def find_dotenv() -> Path | None:
    """Walk up from CWD looking for a .env file."""
    here = Path.cwd().resolve()
    for p in [here, *here.parents]:
        candidate = p / ".env"
        if candidate.exists():
            return candidate
    return None


def derive_slug(url: str) -> str:
    host = urlparse(url).hostname or "site"
    # aleemuh001.framer.ai → aleemuh001
    # linear.app → linear
    # www.example.com → example
    parts = host.split(".")
    if parts[0] == "www" and len(parts) > 1:
        parts = parts[1:]
    return parts[0].lower().replace("-", "")


def scrape(url: str, api_key: str) -> dict:
    resp = requests.post(
        FIRECRAWL_SCRAPE,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "url": url,
            "formats": ["markdown", "html", "links", "screenshot@fullPage"],
            "onlyMainContent": False,
            "waitFor": 3000,
            "actions": [
                {"type": "scroll", "direction": "down", "amount": 500},
                {"type": "wait", "milliseconds": 500},
                {"type": "scroll", "direction": "down", "amount": 500},
                {"type": "wait", "milliseconds": 500},
                {"type": "scroll", "direction": "up", "amount": 99999},
                {"type": "wait", "milliseconds": 800},
            ],
        },
        timeout=120,
    )
    if resp.status_code == 402:
        raise RuntimeError("Firecrawl credits exhausted")
    if resp.status_code == 401:
        raise RuntimeError("Firecrawl API key invalid or missing")
    if not resp.ok:
        raise RuntimeError(f"Firecrawl error {resp.status_code}: {resp.text[:400]}")
    return resp.json().get("data") or {}


def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: extract.py <url> <output-dir>")

    url = sys.argv[1]
    out_root = Path(sys.argv[2])
    extraction = out_root / "extraction"
    extraction.mkdir(parents=True, exist_ok=True)

    if load_dotenv:
        env_path = find_dotenv()
        if env_path:
            load_dotenv(env_path)

    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        sys.exit("FIRECRAWL_API_KEY not set (looked in env and .env up the tree)")

    slug = derive_slug(url)
    (extraction / "slug.txt").write_text(slug, encoding="utf-8")
    print(f"slug: {slug}")

    print(f"Scraping {url} ...", flush=True)
    data = scrape(url, api_key)

    markdown = data.get("markdown") or ""
    html = data.get("html") or data.get("rawHtml") or ""
    metadata = data.get("metadata") or {}
    links = data.get("links") or []
    screenshot_b64 = data.get("screenshot") or ""

    (extraction / "page.md").write_text(markdown, encoding="utf-8")
    print(f"  page.md          {len(markdown):,} chars")

    (extraction / "page.html").write_text(html, encoding="utf-8")
    print(f"  page.html        {len(html):,} chars")

    meta_out = {**metadata, "links": links, "source_url": url}
    (extraction / "metadata.json").write_text(
        json.dumps(meta_out, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  metadata.json    {len(links)} links")

    if screenshot_b64:
        if "," in screenshot_b64:
            screenshot_b64 = screenshot_b64.split(",", 1)[1]
        try:
            img_bytes = base64.b64decode(screenshot_b64)
            (extraction / "firecrawl-screenshot.png").write_bytes(img_bytes)
            print(f"  firecrawl-screenshot.png  {len(img_bytes):,} bytes")
        except Exception as e:
            print(f"  (firecrawl screenshot decode failed: {e})")
    else:
        print("  (no firecrawl screenshot — Playwright will provide it)")

    print("\nExtraction complete.")


if __name__ == "__main__":
    main()

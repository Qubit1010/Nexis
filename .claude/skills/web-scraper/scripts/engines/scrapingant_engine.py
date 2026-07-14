"""Tier 5: ScrapingAnt proxy/unblocker API. Last resort when everything else is blocked.

Rotating residential proxies + headless browser + JS render. Use only after http/crawl4ai/firecrawl fail
and no purpose-built actor exists. Single key (SCRAPING_ANT_API_KEY). Returns HTML -> markdown.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _env import get_key  # noqa: E402
from engines.base import BlockedError, EngineError, QuotaError, looks_blocked, normalize_url, result  # noqa: E402

ENDPOINT = "https://api.scrapingant.com/v2/general"
TIMEOUT = 60


def _html_to_markdown(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    return re.sub(r"\n{3,}", "\n\n", soup.get_text(separator="\n", strip=True))


def fetch(url: str, *, browser: bool = True) -> dict:
    url = normalize_url(url)
    key = get_key("SCRAPING_ANT_API_KEY")
    params = {"url": url, "x-api-key": key, "browser": "true" if browser else "false",
              "proxy_type": "residential"}
    try:
        r = requests.get(ENDPOINT, params=params, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise EngineError(f"scrapingant request failed: {e}") from e
    if r.status_code in (402, 429):
        raise QuotaError(f"scrapingant {r.status_code}")
    if r.status_code == 423:  # ScrapingAnt: target blocked even via proxy
        raise BlockedError("scrapingant 423 (target blocked)")
    if r.status_code >= 400:
        raise EngineError(f"scrapingant {r.status_code}: {r.text[:200]}")
    html = r.text
    if looks_blocked(html):
        raise BlockedError("empty/challenge page after unblocker")
    return result(url, html=html, markdown=_html_to_markdown(html), engine="scrapingant")


if __name__ == "__main__":
    d = fetch("https://example.com")
    print("engine:", d["engine"], "| md_len:", len(d["markdown"]))

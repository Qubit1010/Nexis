"""Website crawler with Firecrawl primary and direct-HTTP fallback.

Adapted from `.claude/skills/website-audit-system/scripts/crawl_site.py`.
Converted from CLI script to importable module for FastAPI use.

Strategy:
  1. Try Firecrawl API (handles JS-rendered pages, JS-heavy SPAs).
  2. If Firecrawl is unreachable (DNS/network error) or key is missing,
     fall back to fetching HTML directly via requests + BeautifulSoup.
     This works for most static/server-rendered sites.
"""

from __future__ import annotations

import os
import re
import time
from ipaddress import ip_address
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

FIRECRAWL_SCRAPE = "https://api.firecrawl.dev/v1/scrape"

HTML_SNIPPET_CHARS = 60_000
MARKDOWN_SNIPPET_CHARS = 40_000
CRAWL_TIMEOUT_SECONDS = 30

_DIRECT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


class CrawlError(Exception):
    pass


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith("http"):
        url = "https://" + url
    return url.rstrip("/")


def _is_safe_url(url: str) -> bool:
    """Block private/loopback IPs to prevent SSRF."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    host = parsed.hostname
    if not host:
        return False
    try:
        ip = ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
            return False
    except ValueError:
        pass
    if host in {"localhost", "metadata.google.internal"}:
        return False
    return True


def _html_to_markdown(html: str) -> str:
    """Crude but sufficient markdown extraction from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    # Collapse blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text[:MARKDOWN_SNIPPET_CHARS]


def _extract_metadata(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.find("title") or "").get_text(strip=True) if soup.find("title") else ""
    description = ""
    og_title = ""
    for meta in soup.find_all("meta"):
        name = (meta.get("name") or meta.get("property") or "").lower()
        content = meta.get("content") or ""
        if name == "description":
            description = content
        elif name == "og:title":
            og_title = content
    return {
        "sourceURL": url,
        "title": title,
        "description": description,
        "ogTitle": og_title,
    }


def _crawl_direct(url: str, retries: int = 3) -> dict:
    """Fetch HTML directly without Firecrawl. Retries on DNS/network errors (Windows DNS is intermittent)."""
    last_exc: Exception = RuntimeError("No attempts made")
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=_DIRECT_HEADERS, timeout=CRAWL_TIMEOUT_SECONDS, allow_redirects=True)
            if resp.status_code >= 400:
                raise CrawlError(f"Site returned HTTP {resp.status_code}")
            html = resp.text[:HTML_SNIPPET_CHARS]
            return {
                "url": resp.url,
                "html": html,
                "markdown": _html_to_markdown(html),
                "metadata": _extract_metadata(html, resp.url),
            }
        except requests.exceptions.ConnectionError as exc:
            last_exc = exc
            if attempt < retries - 1:
                print(f"[crawler] DNS/connection error (attempt {attempt + 1}/{retries}), retrying in 2s...")
                time.sleep(2)
        except requests.RequestException as exc:
            raise CrawlError(f"Direct crawl failed: {exc}") from exc
    raise CrawlError(f"Direct crawl failed after {retries} attempts: {last_exc}")


def _crawl_firecrawl(url: str, api_key: str) -> dict:
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
        timeout=CRAWL_TIMEOUT_SECONDS,
    )
    if resp.status_code == 402:
        raise CrawlError("Firecrawl credits exhausted")
    if resp.status_code == 401:
        raise CrawlError("Firecrawl API key invalid")
    if resp.status_code >= 400:
        raise CrawlError(f"Firecrawl HTTP {resp.status_code}: {resp.text[:200]}")

    data = (resp.json() or {}).get("data") or {}
    return {
        "url": (data.get("metadata") or {}).get("sourceURL") or url,
        "html": (data.get("html") or data.get("rawHtml") or "")[:HTML_SNIPPET_CHARS],
        "markdown": (data.get("markdown") or "")[:MARKDOWN_SNIPPET_CHARS],
        "metadata": data.get("metadata") or {},
    }


def crawl(url: str, api_key: Optional[str] = None) -> dict:
    """Crawl a URL. Tries Firecrawl first, falls back to direct HTTP fetch.

    Returns:
        { "url": str, "html": str, "markdown": str, "metadata": dict }

    Raises:
        CrawlError: if the URL is unsafe or all crawl methods fail.
    """
    url = normalize_url(url)
    if not _is_safe_url(url):
        raise CrawlError(f"URL is not safe to crawl: {url}")

    api_key = api_key or os.environ.get("FIRECRAWL_API_KEY", "").strip()

    if api_key:
        try:
            return _crawl_firecrawl(url, api_key)
        except requests.RequestException as exc:
            # Network-level failure (DNS, timeout, connection refused) — fall through
            print(f"[crawler] Firecrawl unreachable ({exc}), falling back to direct crawl")
        except CrawlError as exc:
            # API-level errors (credits, bad key) — don't fall through, surface to user
            raise

    # Direct HTTP fallback
    return _crawl_direct(url)

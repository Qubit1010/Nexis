"""Tier 1: direct HTTP + BeautifulSoup. Free, fast, for static / server-rendered sites.

Lifts the proven fetch + parse pattern from website-audit-system/crawl_site.py and
lead-generator/scrape_socials.py (browser UA, DNS retry, HTML->markdown, link extraction).
Raises BlockedError when the response looks like a challenge/empty page so the router escalates.
"""
from __future__ import annotations

import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engines.base import (  # noqa: E402
    BlockedError, EngineError, is_safe_url, looks_blocked, normalize_url, result,
)

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
TIMEOUT = 30


def _html_to_markdown(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    return re.sub(r"\n{3,}", "\n\n", text)


def _links(html: str, base: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    out, seen = [], set()
    for a in soup.find_all("a", href=True):
        href = urljoin(base, a["href"].strip())
        if href.startswith("http") and href not in seen:
            seen.add(href)
            out.append(href)
    return out


def _metadata(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find("title")
    desc = ""
    for m in soup.find_all("meta"):
        if (m.get("name") or m.get("property") or "").lower() == "description":
            desc = m.get("content") or ""
            break
    return {"sourceURL": url, "title": title.get_text(strip=True) if title else "", "description": desc}


def fetch(url: str, *, retries: int = 3, timeout: int = TIMEOUT) -> dict:
    url = normalize_url(url)
    if not is_safe_url(url):
        raise EngineError(f"unsafe url: {url}")
    last = None
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
            if r.status_code in (403, 429, 503):
                raise BlockedError(f"http {r.status_code}")
            if r.status_code >= 400:
                raise EngineError(f"http {r.status_code}")
            html = r.text
            if looks_blocked(html):
                raise BlockedError("empty/challenge page")
            md = _html_to_markdown(html)
            return result(r.url, html=html, markdown=md, links=_links(html, r.url),
                          metadata=_metadata(html, r.url), engine="http")
        except requests.exceptions.ConnectionError as e:
            last = e
            if attempt < retries - 1:
                time.sleep(1.5)  # Windows DNS is intermittent; retry
        except requests.RequestException as e:
            raise EngineError(f"request failed: {e}") from e
    raise EngineError(f"connection failed after {retries} tries: {last}")


if __name__ == "__main__":
    d = fetch("https://example.com")
    print("engine:", d["engine"], "| md_len:", len(d["markdown"]), "| links:", len(d["links"]))
    print(d["markdown"][:120])

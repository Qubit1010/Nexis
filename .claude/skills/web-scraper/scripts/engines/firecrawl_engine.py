"""Tier 3: Firecrawl managed API. Paid. Clean markdown, /scrape /crawl /map, JS + light anti-bot.

Lifts the request pattern from website-quality-scorer/firecrawl_client.py, adds:
- numbered-key rotation (FIRECRAWL_API_KEY, _2): on 402/429 rotate to the next key before failing.
- /map for URL discovery (--extract links).
Raises QuotaError once every key is exhausted; BlockedError on a challenge/empty page.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _env import get_keys  # noqa: E402
from engines.base import BlockedError, EngineError, QuotaError, looks_blocked, normalize_url, result  # noqa: E402

BASE = "https://api.firecrawl.dev/v1"
TIMEOUT = 45


def _keys() -> list[str]:
    return get_keys("FIRECRAWL_API_KEY")


def _post(path: str, key: str, payload: dict, timeout: int = TIMEOUT) -> dict:
    r = requests.post(f"{BASE}/{path}", headers={"Authorization": f"Bearer {key}",
                      "Content-Type": "application/json"}, json=payload, timeout=timeout)
    if r.status_code in (402, 429):
        raise QuotaError(f"firecrawl {r.status_code}")
    if r.status_code == 401:
        raise QuotaError("firecrawl 401 (bad key)")  # treat as rotate-able
    if r.status_code >= 400:
        raise EngineError(f"firecrawl {r.status_code}: {r.text[:200]}")
    return r.json() or {}


def _rotate(fn):
    """Try each key; rotate on QuotaError; raise QuotaError only when all are spent."""
    keys = _keys()
    last = None
    for i, key in enumerate(keys):
        try:
            return fn(key)
        except QuotaError as e:
            last = e
            print(f"[firecrawl] key #{i+1} exhausted ({e}); rotating", file=sys.stderr)
    raise QuotaError(f"all {len(keys)} firecrawl keys exhausted: {last}")


def fetch(url: str) -> dict:
    url = normalize_url(url)

    def _do(key: str) -> dict:
        data = _post("scrape", key, {"url": url, "formats": ["markdown", "html"],
                                     "onlyMainContent": False, "waitFor": 1500}).get("data") or {}
        md = data.get("markdown") or ""
        if looks_blocked(md):
            raise BlockedError("empty/challenge page")
        return result((data.get("metadata") or {}).get("sourceURL") or url,
                      html=data.get("html") or data.get("rawHtml") or "", markdown=md,
                      metadata=data.get("metadata") or {}, engine="firecrawl")

    return _rotate(_do)


def map_site(url: str, *, limit: int = 500) -> dict:
    """/map — discover all URLs on a domain fast. Returns links in the result."""
    url = normalize_url(url)

    def _do(key: str) -> dict:
        data = _post("map", key, {"url": url, "limit": limit})
        links = data.get("links") or []
        links = [l.get("url") if isinstance(l, dict) else l for l in links]
        return result(url, links=[l for l in links if l], engine="firecrawl", note="map")

    return _rotate(_do)


def crawl(url: str, *, max_pages: int = 20) -> list[dict]:
    """Start a crawl job, poll to completion, return page results."""
    url = normalize_url(url)

    def _start(key: str) -> str:
        job = _post("crawl", key, {"url": url, "limit": max_pages, "maxDepth": 2,
                    "scrapeOptions": {"formats": ["markdown", "html"], "onlyMainContent": False}})
        jid = job.get("id")
        if not jid:
            raise EngineError(f"no crawl job id: {job}")
        return f"{jid}|{key}"

    jid_key = _rotate(_start)
    jid, key = jid_key.split("|", 1)
    deadline = time.time() + 180
    while time.time() < deadline:
        time.sleep(4)
        r = requests.get(f"{BASE}/crawl/{jid}", headers={"Authorization": f"Bearer {key}"}, timeout=30)
        r.raise_for_status()
        body = r.json()
        if body.get("status") == "completed":
            return [result((it.get("metadata") or {}).get("sourceURL") or "",
                           html=it.get("html") or "", markdown=it.get("markdown") or "",
                           metadata=it.get("metadata") or {}, engine="firecrawl")
                    for it in body.get("data", []) or []]
        if body.get("status") == "failed":
            raise EngineError(f"firecrawl crawl failed: {body.get('error')}")
    raise EngineError("firecrawl crawl timed out (180s)")


if __name__ == "__main__":
    print("keys:", len(_keys()))
    d = fetch("https://example.com")
    print("engine:", d["engine"], "| md_len:", len(d["markdown"]))

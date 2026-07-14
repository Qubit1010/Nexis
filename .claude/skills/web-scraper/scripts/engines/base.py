"""Shared engine contract: result shape, block detection, SSRF guard, error taxonomy.

Every engine returns the same dict so router.py / scrape.py can treat them interchangeably:
    {url, html, markdown, links[], rows[]|None, metadata{}, engine, note}

Error taxonomy drives the two control flows:
- QuotaError  -> the caller rotates to the next numbered API key (Apify/Firecrawl).
- BlockedError-> the router escalates to the next engine tier (http->crawl4ai->firecrawl->apify->scrapingant).
- EngineError -> a hard failure specific to this engine (bad input, unreachable) — try next tier too.
"""
from __future__ import annotations

import re
from ipaddress import ip_address
from urllib.parse import urlparse

MD_MAX = 60_000  # keep pages within downstream LLM token budgets


class EngineError(RuntimeError):
    pass


class QuotaError(EngineError):
    """Credits/rate exhausted for the current key — caller should rotate keys."""


class BlockedError(EngineError):
    """Target blocked us (403/429/CAPTCHA/empty) — router should escalate engine tier."""


# Signals that an HTTP 200 is actually a challenge/empty page, not real content (Q1 [9], Q2).
_BLOCK_SIGNS = re.compile(
    r"(just a moment|attention required|verify you are human|access denied|error 1010|"
    r"cf-browser-verification|captcha|enable javascript to|request unsuccessful|"
    r"unusual traffic|are you a robot)",
    re.I,
)


def looks_blocked(text: str | None, *, min_len: int = 50) -> bool:
    """True if the payload reads like a block/challenge page or is essentially empty.

    The reliable signal is the challenge-phrase regex; the length floor only catches a near-empty
    response (a real 200-with-nothing). Kept low so genuinely small pages (example.com ~150 chars) pass.
    """
    if not text or len(text.strip()) < min_len:
        return True
    return bool(_BLOCK_SIGNS.search(text[:4000]))


def normalize_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return url
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url.rstrip("/")


def is_safe_url(url: str) -> bool:
    """Block private/loopback/link-local hosts (SSRF guard). Lifted from website-audit-system."""
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
    return host not in {"localhost", "metadata.google.internal"}


def result(url: str, *, html: str = "", markdown: str = "", links: list[str] | None = None,
           rows: list[dict] | None = None, metadata: dict | None = None,
           engine: str = "", note: str = "") -> dict:
    return {
        "url": url,
        "html": (html or "")[:MD_MAX],
        "markdown": (markdown or "")[:MD_MAX],
        "links": links or [],
        "rows": rows,
        "metadata": metadata or {},
        "engine": engine,
        "note": note,
    }

"""Tier 2: Crawl4AI (self-hosted, Playwright-backed). Free. JS/dynamic, deep crawl, clean markdown.

The self-hosted engine Aleem asked for. Async under the hood; wrapped in asyncio.run() so callers stay
sync like the other engines. `fetch()` = one page; `crawl()` = BFS deep crawl to N pages.
Returns the shared result shape (markdown is the value here — it's the LLM-ready output crawl4ai is built for).
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engines.base import BlockedError, EngineError, looks_blocked, normalize_url, result  # noqa: E402


def _one(page) -> dict:
    md = getattr(page, "markdown", "") or ""
    if hasattr(md, "raw_markdown"):  # crawl4ai MarkdownGenerationResult
        md = md.raw_markdown or str(md)
    md = str(md)
    html = getattr(page, "html", "") or ""
    links_obj = getattr(page, "links", {}) or {}
    links = [l.get("href") for l in (links_obj.get("internal", []) + links_obj.get("external", []))
             if isinstance(l, dict) and l.get("href")]
    meta = getattr(page, "metadata", {}) or {}
    return result(getattr(page, "url", ""), html=html, markdown=md, links=links,
                  metadata=meta, engine="crawl4ai")


async def _afetch(url: str) -> dict:
    from crawl4ai import AsyncWebCrawler
    async with AsyncWebCrawler() as crawler:
        page = await crawler.arun(url=url)
        if not getattr(page, "success", False):
            raise EngineError(f"crawl4ai failed: {getattr(page, 'error_message', 'unknown')}")
        d = _one(page)
        if looks_blocked(d["markdown"]):
            raise BlockedError("empty/challenge page")
        return d


async def _acrawl(url: str, max_pages: int, max_depth: int) -> list[dict]:
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
    from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
    cfg = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(max_depth=max_depth, max_pages=max_pages,
                                                 include_external=False),
        stream=False,
    )
    async with AsyncWebCrawler() as crawler:
        pages = await crawler.arun(url=url, config=cfg)
        return [_one(p) for p in pages if getattr(p, "success", False)]


def fetch(url: str) -> dict:
    return asyncio.run(_afetch(normalize_url(url)))


def crawl(url: str, *, max_pages: int = 20, max_depth: int = 2) -> list[dict]:
    """BFS deep crawl. Returns a list of page results (markdown each) — ideal for LLM corpora."""
    return asyncio.run(_acrawl(normalize_url(url), max_pages, max_depth))


if __name__ == "__main__":
    d = fetch("https://example.com")
    print("engine:", d["engine"], "| md_len:", len(d["markdown"]))
    print(d["markdown"][:120])

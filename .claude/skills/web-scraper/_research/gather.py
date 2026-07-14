#!/usr/bin/env python3
"""Research-first gather: Exa full-text passes for the 8 web-scraping questions.

Produces the citation audit trail the research-backed rule requires:
  _research/exa/<qkey>.json   raw per-question sources (title, url, text, score)
  _research/sources.json      global deduped index; inline [n] in research-synthesis.md == index

Run:  python .claude/skills/web-scraper/_research/gather.py
Rerun-safe: overwrites the JSON each time. Needs EXA_API_KEY (unsandboxed for api.exa.ai).
Mirrors research/_research/gather.py exactly (same audit-trail shape).
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))
from tools.exa.exa_client import search  # noqa: E402

QUESTIONS: dict[str, list[str]] = {
    "q1_architecture": [
        "web scraping architecture best practices 2026 HTTP vs headless browser vs API",
        "how to build a robust web scraping pipeline design patterns",
        "when to use requests vs playwright vs managed scraping API decision",
    ],
    "q2_antibot": [
        "how to avoid getting blocked web scraping cloudflare captcha bypass 2026",
        "residential rotating proxies user agent fingerprint scraping evasion",
        "web scraping rate limiting retry backoff respectful crawling best practices",
    ],
    "q3_extraction": [
        "structured data extraction css selectors xpath vs LLM extraction web scraping",
        "LLM based web scraping structured output json schema extraction accuracy",
        "cleaning deduplicating scraped data quality validation pipeline",
    ],
    "q4_directory_leadgen": [
        "scraping business directories lead generation google maps yelp data",
        "handle pagination infinite scroll web scraping techniques",
        "lead generation web scraping data quality contact enrichment 2026",
    ],
    "q5_ml_data": [
        "collecting training data for LLM web scraping papers forums repositories",
        "building dataset from web scraping quality deduplication provenance JSONL",
        "scraping arxiv reddit github for machine learning dataset licensing",
    ],
    "q6_realestate": [
        "scraping real estate listings zillow redfin property data 2026",
        "real estate investment data scraping price square feet financial metrics",
        "legal considerations scraping real estate property listing data",
    ],
    "q7_legal_ethics": [
        "is web scraping legal 2026 robots.txt terms of service public data",
        "web scraping GDPR personal data compliance ethics best practices",
        "web scraping legal cases hiQ vs LinkedIn public data ruling",
    ],
    "q8_tool_comparison": [
        "crawl4ai vs firecrawl vs apify web scraping tool comparison 2026",
        "firecrawl vs apify vs scrapingbee pricing capability benchmark",
        "best open source web scraping framework self hosted crawl4ai review",
    ],
}


def norm(url: str) -> str:
    try:
        p = urlparse(url)
        return (p.netloc.lower().removeprefix("www.") + p.path.rstrip("/")).lower()
    except ValueError:
        return url.lower()


def main() -> int:
    exa_dir = HERE / "exa"
    exa_dir.mkdir(parents=True, exist_ok=True)
    global_sources: list[dict] = []
    seen: dict[str, int] = {}

    for qkey, queries in QUESTIONS.items():
        q_sources: list[dict] = []
        for query in queries:
            try:
                data = search(query, num_results=6, type="auto", text=True, highlights=True)
            except Exception as e:  # noqa: BLE001
                print(f"[warn] {qkey}: {query!r} failed: {e}", file=sys.stderr)
                continue
            for r in data.get("results", []):
                url = r.get("url") or ""
                if not url:
                    continue
                rec = {
                    "title": r.get("title") or "",
                    "url": url,
                    "published_date": r.get("published_date"),
                    "score": r.get("score"),
                    "text": (r.get("text") or "")[:2600],
                    "query": query,
                }
                q_sources.append(rec)
                key = norm(url)
                if key not in seen:
                    idx = len(global_sources) + 1
                    seen[key] = idx
                    global_sources.append({"index": idx, "title": rec["title"],
                                           "url": url, "q": qkey, "origin": "exa"})
        (exa_dir / f"{qkey}.json").write_text(
            json.dumps({"question": qkey, "queries": queries, "sources": q_sources},
                       indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"{qkey}: {len(q_sources)} raw sources")

    (HERE / "sources.json").write_text(
        json.dumps({"origin": "exa", "generated": date.today().isoformat(),
                    "note": "inline [n] in research-synthesis.md resolves to sources[index-1]",
                    "total": len(global_sources), "sources": global_sources},
                   indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"total deduped sources: {len(global_sources)} -> sources.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())

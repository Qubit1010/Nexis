"""Tier 4: Apify actors. Paid. General crawling + purpose-built scrapers for hard platforms.

Actor policy (per Aleem): default to the Website Content Crawler (apify/website-content-crawler) for
generic jobs; use a specialized actor (Google Maps, Zillow, etc.) when the target has one — the scenario
recipes name them. Any actor id can be passed via `--actor`.

Key rotation: APIFY_API_KEY(+_2/_3/_4). On a usage/rate limit, rotate to the next key.
Returns dataset items as `rows` (already-structured) plus a markdown roll-up for generic crawls.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _env import get_keys  # noqa: E402
from engines.base import EngineError, QuotaError, normalize_url, result  # noqa: E402

DEFAULT_ACTOR = "apify/website-content-crawler"
_QUOTA_HINTS = ("usage", "limit", "quota", "exceeded", "429", "monthly", "payment", "insufficient")


def _keys() -> list[str]:
    return get_keys("APIFY_API_KEY")


def _looks_quota(exc: Exception) -> bool:
    return any(h in str(exc).lower() for h in _QUOTA_HINTS)


def run_actor(actor_id: str, run_input: dict, *, max_items: int = 200, timeout_secs: int = 300) -> list[dict]:
    """Run an actor to completion and return its dataset items. Rotates keys on quota errors."""
    from apify_client import ApifyClient
    keys = _keys()
    last = None
    for i, key in enumerate(keys):
        try:
            client = ApifyClient(key)
            run = client.actor(actor_id).call(run_input=run_input, timeout_secs=timeout_secs)
            if not run or not run.get("defaultDatasetId"):
                raise EngineError(f"actor {actor_id} returned no dataset")
            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            return items[:max_items]
        except Exception as e:  # noqa: BLE001 - apify raises various client errors
            if _looks_quota(e) and i < len(keys) - 1:
                print(f"[apify] key #{i+1} quota/limit ({e}); rotating", file=sys.stderr)
                last = e
                continue
            if _looks_quota(e):
                raise QuotaError(f"all {len(keys)} apify keys exhausted: {e}") from e
            raise EngineError(f"apify actor {actor_id} failed: {e}") from e
    raise QuotaError(f"all apify keys exhausted: {last}")


def fetch(url: str, *, actor: str = DEFAULT_ACTOR, max_items: int = 50) -> dict:
    """Generic single-target crawl via the Website Content Crawler (or a given actor)."""
    url = normalize_url(url)
    run_input = {"startUrls": [{"url": url}], "maxCrawlPages": max_items,
                 "crawlerType": "playwright:adaptive", "saveMarkdown": True}
    items = run_actor(actor, run_input, max_items=max_items)
    md = "\n\n---\n\n".join((it.get("markdown") or it.get("text") or "") for it in items if it)
    return result(url, markdown=md, rows=items, engine="apify",
                  note=f"actor={actor} items={len(items)}")


def actor(actor_id: str, run_input: dict, *, max_items: int = 200) -> dict:
    """Direct actor run (specialized actors: Maps, Zillow, etc.). rows = raw structured dataset items."""
    items = run_actor(actor_id, run_input, max_items=max_items)
    return result(run_input.get("startUrls", [{}])[0].get("url", "") if run_input.get("startUrls") else "",
                  rows=items, engine="apify", note=f"actor={actor_id} items={len(items)}")


if __name__ == "__main__":
    print("keys:", len(_keys()), "| default actor:", DEFAULT_ACTOR)

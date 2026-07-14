"""Tavily client — LLM-optimized web search with an optional synthesized answer.

Best for a fast, clean answer + ranked sources (the 'light' default).
"""
from __future__ import annotations

import sys

from _env import get_key
from _http import post_json

ENDPOINT = "https://api.tavily.com/search"


def _norm(r: dict) -> dict:
    return {
        "title": r.get("title", ""),
        "url": r.get("url", ""),
        "snippet": (r.get("content") or "")[:500],
        "source": "tavily",
        "score": r.get("score"),
        "published_date": r.get("published_date"),
        "raw_content": r.get("raw_content"),
    }


def search(query: str, *, depth: str = "basic", max_results: int = 10,
           include_answer: bool = True, include_raw: bool = False,
           topic: str = "general") -> dict:
    """depth: 'basic' (fast) | 'advanced' (deeper). topic: 'general' | 'news'."""
    payload = {
        "query": query,
        "search_depth": depth,
        "max_results": max_results,
        "include_answer": include_answer,
        "include_raw_content": include_raw,
        "topic": topic,
    }
    headers = {"Authorization": f"Bearer {get_key('TAVILY_API_KEY')}"}
    data = post_json(ENDPOINT, payload, headers=headers)
    return {
        "query": query,
        "answer": data.get("answer"),
        "results": [_norm(r) for r in (data.get("results") or [])],
    }


if __name__ == "__main__":  # smoke test
    q = sys.argv[1] if len(sys.argv) > 1 else "best open source vector databases 2026"
    out = search(q, max_results=5)
    print(f"tavily: {len(out['results'])} results for {q!r}")
    if out["answer"]:
        print(f"  answer: {out['answer'][:200]}")
    for r in out["results"]:
        print(f"  - {r['title']}  {r['url']}")

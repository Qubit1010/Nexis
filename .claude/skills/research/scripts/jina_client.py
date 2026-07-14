"""Jina client — s.jina.ai search + r.jina.ai reader (clean URL -> markdown extraction).

Search is a secondary web source; the reader is the content-extraction engine for deep mode
(turns any URL into clean markdown). The paid key raises rate limits vs the keyless floor.
"""
from __future__ import annotations

import sys

from _env import get_key
from _http import get_json, get_text, quote

SEARCH_ENDPOINT = "https://s.jina.ai/"
READER_ENDPOINT = "https://r.jina.ai/"


def _auth() -> dict:
    key = get_key("JINA_AI_API_KEY", required=False)
    return {"Authorization": f"Bearer {key}"} if key else {}


def _norm(r: dict, i: int) -> dict:
    return {
        "title": r.get("title", ""),
        "url": r.get("url", ""),
        "snippet": (r.get("description") or r.get("content") or "")[:500],
        "source": "jina",
        "score": round(1.0 - i * 0.03, 3),
        "published_date": r.get("date"),
    }


def search(query: str, *, num: int = 10, with_content: bool = False) -> dict:
    """Web search via s.jina.ai. with_content=False keeps it fast (title/url/description only)."""
    headers = {**_auth()}
    if not with_content:
        headers["X-Respond-With"] = "no-content"
    url = f"{SEARCH_ENDPOINT}?q={quote(query)}&count={num}"
    data = get_json(url, headers=headers, timeout=30)
    items = data.get("data", []) if isinstance(data, dict) else (data or [])
    return {"query": query, "results": [_norm(r, i) for i, r in enumerate(items[:num])]}


def read(url: str, *, timeout: int = 30) -> str:
    """Fetch a URL as clean markdown (r.jina.ai). Auth optional but raises rate limits."""
    headers = {"X-Return-Format": "markdown", **_auth()}
    return get_text(f"{READER_ENDPOINT}{url}", headers=headers, timeout=timeout)


if __name__ == "__main__":  # smoke test
    q = sys.argv[1] if len(sys.argv) > 1 else "agentic RAG best practices 2026"
    out = search(q, num=5)
    print(f"jina: {len(out['results'])} results for {q!r}")
    for r in out["results"]:
        print(f"  - {r['title']}  {r['url']}")

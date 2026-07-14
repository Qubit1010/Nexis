"""Adapter over the canonical tools/exa/exa_client.py -> the shared normalized result schema.

No new Exa client: reuses search / answer / get_contents / research from the repo helper.
"""
from __future__ import annotations

import sys

from _env import repo_root

sys.path.insert(0, str(repo_root()))
from tools.exa.exa_client import answer as _answer  # noqa: E402
from tools.exa.exa_client import get_contents as _get_contents  # noqa: E402
from tools.exa.exa_client import research as _research  # noqa: E402
from tools.exa.exa_client import search as _search  # noqa: E402


def _norm(r: dict) -> dict:
    return {
        "title": r.get("title") or "",
        "url": r.get("url") or "",
        "snippet": (r.get("summary") or (r.get("highlights") or [""])[0] or (r.get("text") or ""))[:500],
        "source": "exa",
        "score": r.get("score"),
        "published_date": r.get("published_date"),
        "text": r.get("text"),
    }


def search(query: str, *, num: int = 10, category: str | None = None,
           type: str = "auto", text: bool = False) -> dict:
    data = _search(query, num_results=num, type=type, category=category,
                   text=text, highlights=True, summary=False)
    return {"query": query, "results": [_norm(r) for r in data.get("results", [])]}


def answer(query: str) -> dict:
    """Exa cited answer -> {answer, results(citations)}."""
    data = _answer(query, text=False)
    cites = [{"title": c.get("title") or "", "url": c.get("url") or "", "snippet": "",
              "source": "exa", "score": None, "published_date": c.get("published_date")}
             for c in data.get("citations", [])]
    return {"query": query, "answer": data.get("answer"), "results": cites}


def contents(urls: list[str]) -> dict:
    data = _get_contents(urls, text=True)
    return {"results": [_norm(r) for r in data.get("results", [])]}


def deep_research(instructions: str, *, model: str = "exa-research-fast") -> dict:
    """Agentic Exa research (the single-service deep path)."""
    return _research(instructions, model=model)


if __name__ == "__main__":  # smoke test
    q = sys.argv[1] if len(sys.argv) > 1 else "best open source vector databases 2026"
    out = search(q, num=5)
    print(f"exa: {len(out['results'])} results for {q!r}")
    for r in out["results"]:
        print(f"  - {r['title']}  {r['url']}")

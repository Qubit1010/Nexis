"""Serper.dev client — real Google SERP results (best for Google-dorks, people, companies).

Query IS the dork: pass `site:linkedin.com/in "acme" founder` etc. verbatim.
Returns normalized dicts + exposes knowledge-graph / people-also-ask for entity mode.
"""
from __future__ import annotations

import sys

from _env import get_key
from _http import post_json

ENDPOINT = "https://google.serper.dev/search"


def _norm(r: dict, i: int) -> dict:
    return {
        "title": r.get("title", ""),
        "url": r.get("link", ""),
        "snippet": r.get("snippet", ""),
        "source": "serper",
        "score": round(1.0 - i * 0.03, 3),  # SERP rank -> pseudo-score (position 0 = best)
        "published_date": r.get("date"),
    }


def search(query: str, *, num: int = 10, gl: str = "us", hl: str = "en",
           tbs: str | None = None) -> dict:
    """Google search. Returns {results, answer_box, knowledge_graph, people_also_ask, related}."""
    payload = {"q": query, "num": num, "gl": gl, "hl": hl}
    if tbs:
        payload["tbs"] = tbs
    data = post_json(ENDPOINT, payload, headers={"X-API-KEY": get_key("SERPER_API_KEY")})
    organic = data.get("organic", []) or []
    return {
        "query": query,
        "results": [_norm(r, i) for i, r in enumerate(organic[:num])],
        "answer_box": data.get("answerBox"),
        "knowledge_graph": data.get("knowledgeGraph"),
        "people_also_ask": data.get("peopleAlsoAsk"),
        "related": data.get("relatedSearches"),
    }


if __name__ == "__main__":  # smoke test
    q = sys.argv[1] if len(sys.argv) > 1 else "site:linkedin.com/in anthropic founder"
    out = search(q, num=5)
    print(f"serper: {len(out['results'])} results for {q!r}")
    for r in out["results"]:
        print(f"  - {r['title']}  {r['url']}")
    if out["knowledge_graph"]:
        print(f"  KG: {out['knowledge_graph'].get('title')}")

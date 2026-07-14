"""Cross-service result fusion: dedupe by normalized URL, rank by cross-source agreement.

The ranking signal that matters most is agreement: a URL returned by 3 engines outranks one
returned by 1. Ties break on best per-service score, then first-seen order.
"""
from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

_TRACKING = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
             "ref", "fbclid", "gclid", "mc_cid", "mc_eid", "_hsenc", "_hsmi"}


def normalize_url(url: str) -> str:
    """Canonical key for dedupe: drop scheme case, www., trailing slash, fragment, tracking params."""
    if not url:
        return ""
    try:
        p = urlparse(url.strip())
    except ValueError:
        return url.strip().lower()
    netloc = p.netloc.lower().removeprefix("www.")
    path = p.path.rstrip("/") or "/"
    query = urlencode([(k, v) for k, v in parse_qsl(p.query) if k.lower() not in _TRACKING])
    return urlunparse(("", netloc, path, "", query, "")).lstrip("/") or netloc


def _score(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def fuse(*result_lists: list[dict]) -> list[dict]:
    """Merge normalized result dicts ({title,url,snippet,source,score,...}) into a ranked list."""
    merged: dict[str, dict] = {}
    order = 0
    for results in result_lists:
        for r in results or []:
            key = normalize_url(r.get("url", ""))
            if not key:
                continue
            if key not in merged:
                merged[key] = {
                    "title": r.get("title") or "",
                    "url": r.get("url") or "",
                    "snippet": r.get("snippet") or "",
                    "sources": [],
                    "best_score": _score(r.get("score")),
                    "published_date": r.get("published_date"),
                    "_order": order,
                }
                order += 1
            m = merged[key]
            src = r.get("source") or "?"
            if src not in m["sources"]:
                m["sources"].append(src)
            m["best_score"] = max(m["best_score"], _score(r.get("score")))
            if len(r.get("snippet") or "") > len(m["snippet"]):
                m["snippet"] = r["snippet"]
            if not m["title"] and r.get("title"):
                m["title"] = r["title"]
            if not m["published_date"] and r.get("published_date"):
                m["published_date"] = r["published_date"]

    ranked = sorted(
        merged.values(),
        key=lambda m: (-len(m["sources"]), -m["best_score"], m["_order"]),
    )
    for m in ranked:
        m.pop("_order", None)
    return ranked


def _demo() -> None:
    a = [{"title": "Weaviate", "url": "https://www.Weaviate.io/blog?utm_source=x", "source": "exa", "score": 0.9},
         {"title": "Only Exa", "url": "https://only-exa.com/", "source": "exa", "score": 0.95}]
    b = [{"title": "weaviate", "url": "http://weaviate.io/blog/", "source": "tavily", "score": 0.5},
         {"title": "Only Tavily", "url": "https://only-tavily.com", "source": "tavily", "score": 0.99}]
    out = fuse(a, b)
    # The two weaviate URLs (different scheme/case/www/trailing-slash/tracking) collapse to one.
    assert len(out) == 3, f"expected 3 unique, got {len(out)}"
    top = out[0]
    assert set(top["sources"]) == {"exa", "tavily"}, top["sources"]
    assert top["title"].lower() == "weaviate"
    # Multi-source beats single-source even with a lower single score (0.99 tavily-only).
    assert len(out[1]["sources"]) == 1 and len(out[2]["sources"]) == 1
    assert normalize_url("https://WWW.Foo.com/a/?b=1&utm_medium=z#frag") == "foo.com/a?b=1"
    print("fuse self-check passed")


if __name__ == "__main__":
    _demo()

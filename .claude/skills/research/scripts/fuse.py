"""Cross-service result fusion: dedupe by normalized URL, rank by cross-source agreement.

The ranking signal that matters most is agreement: a URL returned by 3 engines outranks one
returned by 1. Ties break on best per-service rank position, then first-seen order.

The tie-break is deliberately a *position* and not the `score` field each engine reports,
because those scores live on four mutually incomparable scales: serper and jina synthesize
`1.0 - i*0.03` from SERP rank (so ~1.00 down to ~0.70), tavily passes through a real
relevance score (which in practice clusters around 0.50-0.60), and exa passes through a
field its default `type="auto"` search never populates at all (None). Ranking on the raw
value therefore sorted by engine rather than by relevance, and buried every exa-only result
under every result from any other engine - which is exactly backwards, since exa is in the
stack to find what keyword search misses. Position within an engine's own list is the one
comparable signal all four actually provide.
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


def _rank_normalize(results: list[dict]) -> list[tuple[dict, float]]:
    """Pair each result with a rank-normalized score in (0, 1], scoped to its own engine.

    Engines are expected to return their results already in their own preferred order, so
    position carries the ranking and the incomparable `score` field can be ignored. Grouping
    by `source` rather than assuming one list is one engine costs nothing and keeps the
    result correct if a caller ever passes a pre-merged list.
    """
    counts: dict[str, int] = {}
    for r in results or []:
        src = r.get("source") or "?"
        counts[src] = counts.get(src, 0) + 1

    seen: dict[str, int] = {}
    paired: list[tuple[dict, float]] = []
    for r in results or []:
        src = r.get("source") or "?"
        i = seen.get(src, 0)
        seen[src] = i + 1
        paired.append((r, 1.0 - i / counts[src]))
    return paired


def fuse(*result_lists: list[dict]) -> list[dict]:
    """Merge normalized result dicts ({title,url,snippet,source,score,...}) into a ranked list."""
    merged: dict[str, dict] = {}
    order = 0
    for results in result_lists:
        for r, rank_score in _rank_normalize(results):
            key = normalize_url(r.get("url", ""))
            if not key:
                continue
            if key not in merged:
                merged[key] = {
                    "title": r.get("title") or "",
                    "url": r.get("url") or "",
                    "snippet": r.get("snippet") or "",
                    "sources": [],
                    "best_score": rank_score,
                    "published_date": r.get("published_date"),
                    "_order": order,
                }
                order += 1
            m = merged[key]
            src = r.get("source") or "?"
            if src not in m["sources"]:
                m["sources"].append(src)
            m["best_score"] = max(m["best_score"], rank_score)
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
    # score=None on every exa result is not an edge case, it is what production always looks
    # like: exa_adapter.py passes `score` through untouched and exa's default type="auto"
    # search does not populate it. The previous fixture used 0.9/0.95 here, values the adapter
    # cannot emit, so this check passed while the real path was broken.
    a = [{"title": "Weaviate", "url": "https://www.Weaviate.io/blog?utm_source=x", "source": "exa", "score": None},
         {"title": "Only Exa", "url": "https://only-exa.com/", "source": "exa", "score": None}]
    b = [{"title": "weaviate", "url": "http://weaviate.io/blog/", "source": "tavily", "score": 0.5},
         {"title": "Only Tavily", "url": "https://only-tavily.com", "source": "tavily", "score": 0.99}]
    out = fuse(a, b)
    # The two weaviate URLs (different scheme/case/www/trailing-slash/tracking) collapse to one.
    assert len(out) == 3, f"expected 3 unique, got {len(out)}"
    top = out[0]
    assert set(top["sources"]) == {"exa", "tavily"}, top["sources"]
    assert top["title"].lower() == "weaviate"
    # Agreement is still the primary key: multi-source beats single-source.
    assert len(out[1]["sources"]) == 1 and len(out[2]["sources"]) == 1

    # Regression for the cross-engine scale bug. Exa reports no score at all, which the old
    # _score() floored to 0.0, so every exa-only URL sorted below every tavily-only URL no
    # matter what it contained. Exa's own #1 must be able to outrank tavily's #3.
    exa_only = [{"title": f"exa{i}", "url": f"https://e{i}.com", "source": "exa", "score": None}
                for i in range(3)]
    tavily_only = [{"title": f"tav{i}", "url": f"https://t{i}.com", "source": "tavily",
                    "score": round(0.6 - i * 0.1, 2)} for i in range(3)]
    urls = [m["url"] for m in fuse(exa_only, tavily_only)]
    assert urls.index("https://e0.com") < urls.index("https://t2.com"), urls
    # and the two engines interleave by position rather than segregating by engine
    assert urls.index("https://e1.com") < urls.index("https://t2.com"), urls

    assert normalize_url("https://WWW.Foo.com/a/?b=1&utm_medium=z#frag") == "foo.com/a?b=1"
    print("fuse self-check passed")


if __name__ == "__main__":
    _demo()

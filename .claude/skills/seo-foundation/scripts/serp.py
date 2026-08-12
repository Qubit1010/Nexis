"""Raw Serper SERP fetcher with a disk cache.

Why this exists rather than reusing research/scripts/serper_client.py: that client's
`_norm()` keeps only title/url/snippet and throws away `position`, `sitelinks`, `rating`
and the raw feature blocks. Every one of those is a signal the difficulty read depends on,
so this keeps the whole response.

The cache is the point. Phases 4 through 7 all read the same SERPs (features, then
clustering, then mapping), and a re-run after a scoring tweak should cost nothing. Cache
keys are query+gl+hl+num only, so the same SERP is shared across clients.

Serper reality, measured 2026-08-06 against 5 query shapes:
  - always present: organic[] with position/title/link/snippet, peopleAlsoAsk, relatedSearches
  - sometimes:      date (0-5 of 10 results), sitelinks, rating/ratingCount
  - never returned: aiOverview. answerBox effectively never (absent even on "what is a crm").
So AI Overview presence cannot be read from this source. serp_features.py marks it unknown
rather than guessing, and the report tells the user to check it manually in incognito.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO = SKILL_DIR.parents[2]
sys.path.insert(0, str(REPO / ".claude" / "skills" / "research" / "scripts"))

from _env import get_keys  # noqa: E402
from _http import post_json, with_key_rotation  # noqa: E402

ENDPOINT = "https://google.serper.dev/search"
CACHE_DIR = SKILL_DIR / ".cache" / "serp"

# Counts live calls in this process so a run can report what it actually spent.
CREDITS_SPENT = 0
CACHE_HITS = 0


def _cache_path(query: str, gl: str, hl: str, num: int) -> Path:
    key = f"{query.strip().lower()}|{gl}|{hl}|{num}"
    return CACHE_DIR / f"{hashlib.sha1(key.encode('utf-8')).hexdigest()}.json"


def fetch(query: str, *, gl: str = "us", hl: str = "en", num: int = 10,
          refresh: bool = False, cache: bool = True) -> dict:
    """One SERP, whole response. Cached unless refresh=True.

    Adds `_meta` with the query and whether it came from cache, so downstream scripts can
    report cost honestly instead of assuming every row was a live call.
    """
    global CREDITS_SPENT, CACHE_HITS
    path = _cache_path(query, gl, hl, num)

    if cache and not refresh and path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            CACHE_HITS += 1
            data.setdefault("_meta", {})["cached"] = True
            return data
        except (json.JSONDecodeError, OSError):
            pass  # corrupt cache entry, fall through and refetch

    payload = {"q": query, "num": num, "gl": gl, "hl": hl}
    data = with_key_rotation(
        get_keys("SERPER_API_KEY"),
        lambda k: post_json(ENDPOINT, payload, headers={"X-API-KEY": k}))
    CREDITS_SPENT += int(data.get("credits") or 1)
    data["_meta"] = {"query": query, "gl": gl, "hl": hl, "num": num,
                     "cached": False, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S")}

    if cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return data


def fetch_many(queries: list[str], *, gl: str = "us", hl: str = "en", num: int = 10,
               refresh: bool = False, delay: float = 0.25,
               progress: bool = True) -> dict[str, dict]:
    """Sequential because the cache absorbs re-runs and Serper credits are the scarce
    resource here, not wall-clock. Sleeps only between live calls."""
    out: dict[str, dict] = {}
    total = len(queries)
    for i, q in enumerate(queries, 1):
        data = fetch(q, gl=gl, hl=hl, num=num, refresh=refresh)
        out[q] = data
        if progress and (i % 10 == 0 or i == total):
            print(f"  [serp] {i}/{total}  live={CREDITS_SPENT} cached={CACHE_HITS}",
                  file=sys.stderr)
        if not data.get("_meta", {}).get("cached"):
            time.sleep(delay)
    return out


def urls_of(data: dict, limit: int = 10) -> list[str]:
    """Top-N organic URLs. The unit SERP-overlap clustering compares."""
    return [r.get("link", "") for r in (data.get("organic") or [])[:limit] if r.get("link")]


def cost_report() -> str:
    return f"Serper: {CREDITS_SPENT} live credit(s), {CACHE_HITS} cache hit(s)"


def _selftest() -> int:
    q = "best crm for small business"
    print("1. live fetch (or existing cache)...")
    a = fetch(q, refresh=True)
    ok = True

    org = a.get("organic") or []
    print(f"   organic results: {len(org)}")
    if not org:
        print("   FAIL: no organic results"); ok = False
    elif "position" not in org[0]:
        print("   FAIL: `position` missing - _norm-style stripping happened"); ok = False
    else:
        print("   PASS: raw fields kept ->", sorted(org[0].keys()))

    paa = a.get("peopleAlsoAsk")
    rel = a.get("relatedSearches")
    print(f"   peopleAlsoAsk: {len(paa) if paa else 0}   relatedSearches: {len(rel) if rel else 0}")
    if not paa and not rel:
        print("   FAIL: neither PAA nor related searches returned"); ok = False
    else:
        print("   PASS: expansion sources present")

    spent_before = CREDITS_SPENT
    print("2. second fetch should hit cache and cost 0...")
    b = fetch(q)
    if CREDITS_SPENT != spent_before:
        print(f"   FAIL: cache miss, spent {CREDITS_SPENT - spent_before} more credit(s)"); ok = False
    elif not b.get("_meta", {}).get("cached"):
        print("   FAIL: response not flagged as cached"); ok = False
    else:
        print("   PASS: cache hit, 0 credits")

    if urls_of(a) != urls_of(b):
        print("   FAIL: cached URLs differ from live"); ok = False
    else:
        print(f"   PASS: {len(urls_of(a))} URLs stable through cache")

    print(f"\n{cost_report()}")
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch a raw Google SERP via Serper, cached.")
    ap.add_argument("query", nargs="?", help="search query")
    ap.add_argument("--gl", default="us"); ap.add_argument("--hl", default="en")
    ap.add_argument("--num", type=int, default=10)
    ap.add_argument("--refresh", action="store_true", help="bypass cache, refetch live")
    ap.add_argument("--urls", action="store_true", help="print only the organic URLs")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()
    if not args.query:
        ap.error("query required (or use --selftest)")

    data = fetch(args.query, gl=args.gl, hl=args.hl, num=args.num, refresh=args.refresh)
    if args.urls:
        for u in urls_of(data, args.num):
            print(u)
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"\n{cost_report()}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

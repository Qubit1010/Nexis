#!/usr/bin/env python3
"""Fetch one page's raw HTML, whole, with the response metadata on-page SEO needs.

Why this exists rather than calling web-scraper's http engine:

web-scraper's `engines/base.result()` truncates BOTH html and markdown at MD_MAX = 60_000
characters, because its downstream consumer is an LLM extraction step with a token budget.
That cap is correct there and fatal here. A WordPress theme with inlined critical CSS can
burn 60KB before `</head>` closes, and footer JSON-LD plus the footer link block - two
things this skill specifically checks - routinely sit past the cut. An on-page audit run
against a silently truncated document reports missing schema and missing links that are
right there in the source.

It also drops what `result()` has no field for and this skill treats as findings in their
own right:
  - the redirect chain (a priority page reached through two hops IS the finding)
  - response headers (x-robots-tag noindex, content-type charset, cache-control)
  - the status code, distinct from "the body looked empty"

So this keeps `r.text` entire and carries the rest alongside. It reuses web-scraper's
HEADERS and its `is_safe_url` SSRF guard verbatim, because those are correct and there is
no reason to have two copies drift.

Escalation: if the body comes back blocked or near-empty, the page is probably rendered
client-side, so it retries through crawl4ai (free, local Playwright) and records which
engine actually produced the bytes. If both come back empty that is not a fetch failure to
paper over, it is a rendering finding to report.

Cache: SHA1 of the normalized URL, in .cache/pages/. Keyed on URL only - no client, no
date, no run id - so re-running the whole audit after a fix costs nothing, exactly like
seo-foundation/scripts/serp.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, urlunparse

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO = SKILL_DIR.parents[2]
sys.path.insert(0, str(REPO / ".claude" / "skills" / "web-scraper" / "scripts"))

from engines.base import BlockedError, is_safe_url  # noqa: E402
from engines.http_engine import HEADERS  # noqa: E402

# Below this many words of visible text, assume the page is rendered client-side.
# A real content page clears it easily; a JS shell returns almost nothing.
THIN_TEXT_WORDS = 120

CACHE_DIR = SKILL_DIR / ".cache" / "pages"

FETCHES = 0
CACHE_HITS = 0
ESCALATIONS = 0


def normalize_url(url: str) -> str:
    """Add a scheme and lowercase the host, but keep the path exactly as given.

    Deliberately does NOT rstrip("/") the way web-scraper's normalize_url does: on this
    skill's checks `/services` and `/services/` can be two indexable URLs, and collapsing
    them would hide a duplicate-content finding behind a cache hit.
    """
    url = (url or "").strip()
    if not url:
        return url
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    p = urlparse(url)
    return urlunparse((p.scheme.lower(), p.netloc.lower(), p.path, p.params, p.query, ""))


def _cache_path(url: str) -> Path:
    return CACHE_DIR / (hashlib.sha1(normalize_url(url).encode("utf-8")).hexdigest() + ".json")


def visible_word_count(html: str) -> int:
    """Words of rendered-ish text, script/style/noscript stripped.

    This is the escalation test rather than web-scraper's `looks_blocked`, which regexes the
    raw HTML for challenge phrases. That regex includes "enable javascript to", and any page
    carrying a <noscript> fallback - Wikipedia, most WordPress themes - matches it while
    being perfectly complete. On the first run of this file that false positive spent a
    5-second Playwright render on a 370KB page that had already fetched fine. Counting real
    text instead asks the question we actually care about: is there content here or not.
    """
    if not html:
        return 0
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript", "template"]):
            tag.decompose()
        return len(soup.get_text(" ", strip=True).split())
    except Exception:  # noqa: BLE001 - a parse failure should not stop a fetch
        return len(html.split())


def _http_fetch(url: str, *, timeout: int = 30) -> dict:
    """requests.get keeping the whole body plus everything result() would have dropped."""
    import requests

    r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
    return {
        "url": url,
        "final_url": r.url,
        "status": r.status_code,
        "html": r.text,
        "headers": {k.lower(): v for k, v in r.headers.items()},
        "redirect_chain": [{"status": h.status_code, "url": h.url} for h in r.history],
        "engine": "http",
        "encoding": r.encoding,
    }


def _crawl4ai_fetch(url: str) -> dict:
    """Playwright render for client-side pages. Free, local, no key."""
    sys.path.insert(0, str(REPO / ".claude" / "skills" / "web-scraper" / "scripts"))
    from engines import crawl4ai_engine

    res = crawl4ai_engine.fetch(url)
    return {
        "url": url,
        "final_url": res.get("url") or url,
        "status": 200,
        "html": res.get("html") or "",
        "headers": {},
        "redirect_chain": [],
        "engine": "crawl4ai",
        "encoding": None,
        "note": "rendered; headers and redirect chain unavailable through this engine",
    }


def fetch(url: str, *, refresh: bool = False, cache: bool = True, timeout: int = 30) -> dict:
    """Fetch one page. Returns the raw record with `_meta` attached."""
    global FETCHES, CACHE_HITS, ESCALATIONS

    url = normalize_url(url)
    if not is_safe_url(url):
        raise ValueError(f"refusing to fetch a private/loopback host: {url}")

    path = _cache_path(url)
    if cache and not refresh and path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            CACHE_HITS += 1
            data.setdefault("_meta", {})["cached"] = True
            return data
        except (json.JSONDecodeError, OSError):
            pass  # corrupt entry: refetch rather than crash or make anyone clean it up

    try:
        data = _http_fetch(url, timeout=timeout)
    except BlockedError as exc:
        data = {"url": url, "final_url": url, "status": 403, "html": "", "headers": {},
                "redirect_chain": [], "engine": "http", "encoding": None, "note": str(exc)}
    except Exception as exc:  # noqa: BLE001 - a dead host is a finding, not a traceback
        data = {"url": url, "final_url": url, "status": 0, "html": "", "headers": {},
                "redirect_chain": [], "engine": "http", "encoding": None, "note": f"{type(exc).__name__}: {exc}"}
    FETCHES += 1

    # Little or no visible text on a 200 means the content is rendered client-side.
    words = visible_word_count(data.get("html") or "")
    blocked_status = data.get("status") in (0, 403, 429, 503)
    if words < THIN_TEXT_WORDS or blocked_status:
        why = f"status {data.get('status')}" if blocked_status else f"only {words} words of text"
        print(f"[fetch] {url}: {why} via http, escalating to crawl4ai", file=sys.stderr)
        try:
            rendered = _crawl4ai_fetch(url)
            if visible_word_count(rendered.get("html") or "") > words:
                rendered["escalated_from"] = "http"
                rendered["http_status"] = data.get("status")
                data = rendered
                words = visible_word_count(data.get("html") or "")
                ESCALATIONS += 1
            else:
                data["note"] = (f"{data.get('note', '')} | crawl4ai rendered no more text; "
                                "the page may genuinely be empty").strip(" |")
        except Exception as exc:  # noqa: BLE001
            data["note"] = f"{data.get('note', '')} | crawl4ai escalation failed: {exc}".strip(" |")

    data["_meta"] = {
        "cached": False,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "html_chars": len(data.get("html") or ""),
        "visible_words": words,
        "truncated": False,  # this fetcher never truncates; stated so downstream can rely on it
    }

    if cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        try:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        except OSError as exc:
            print(f"[fetch] cache write failed (continuing): {exc}", file=sys.stderr)

    return data


def fetch_many(urls: list[str], *, refresh: bool = False, delay: float = 0.4) -> dict[str, dict]:
    out: dict[str, dict] = {}
    total = len(urls)
    for i, u in enumerate(urls, 1):
        before = FETCHES
        try:
            out[normalize_url(u)] = fetch(u, refresh=refresh)
        except ValueError as exc:
            print(f"[fetch] skipped {u}: {exc}", file=sys.stderr)
            continue
        if i % 10 == 0 or i == total:
            print(f"[fetch] {i}/{total} live={FETCHES} cached={CACHE_HITS}", file=sys.stderr)
        if FETCHES > before:
            time.sleep(delay)  # only pause after a real request; cache hits are free
    return out


def robots_signals(data: dict) -> dict:
    """The response-level indexability signals, which no HTML parse can see."""
    h = data.get("headers") or {}
    return {
        "status": data.get("status"),
        "x_robots_tag": h.get("x-robots-tag"),
        "content_type": h.get("content-type"),
        "redirect_hops": len(data.get("redirect_chain") or []),
        "final_url": data.get("final_url"),
        "engine": data.get("engine"),
    }


def cost_report() -> str:
    return (f"fetch_page: {FETCHES} live fetch(es), {CACHE_HITS} cache hit(s), "
            f"{ESCALATIONS} escalation(s) to crawl4ai. No paid API used.")


def _selftest() -> int:
    """Live. Proves the three things this module exists to guarantee."""
    ok = True
    target = "https://en.wikipedia.org/wiki/Search_engine_optimization"

    print("1. fetch a live content page, keep the whole body")
    try:
        a = fetch(target, refresh=True)
        if a["status"] == 200 and a["html"]:
            print(f"   PASS: status 200, {len(a['html'])} chars, "
                  f"{a['_meta']['visible_words']} words, engine={a['engine']}")
        else:
            print(f"   FAIL: status={a['status']} chars={len(a.get('html') or '')}")
            ok = False
    except Exception as exc:  # noqa: BLE001
        print(f"   FAIL: {type(exc).__name__}: {exc}")
        return 1

    print("2. no truncation at web-scraper's 60,000-char cap")
    n = len(a.get("html") or "")
    if n > 60_000:
        print(f"   PASS: {n} chars retained, well past the 60,000 cap that made this file necessary")
    else:
        print(f"   FAIL (weak): {n} chars; expected a page large enough to exercise the cap")
        ok = False

    print("3. no needless escalation on a page that fetched fine")
    if a["engine"] == "http" and ESCALATIONS == 0:
        print("   PASS: served by plain http, no Playwright render spent")
    else:
        print(f"   FAIL: engine={a['engine']} escalations={ESCALATIONS}. The escalation test "
              "is false-positiving again - it must count visible text, not regex the raw HTML.")
        ok = False

    print("4. second fetch is served from cache, costs nothing")
    before = FETCHES
    b = fetch(target)
    if FETCHES == before and b["_meta"]["cached"]:
        print("   PASS: cache hit, no new request")
    else:
        print(f"   FAIL: refetched (FETCHES {before} -> {FETCHES})")
        ok = False

    print("5. SSRF guard rejects a loopback host")
    try:
        fetch("http://localhost/admin")
        print("   FAIL: localhost was not rejected")
        ok = False
    except ValueError:
        print("   PASS: rejected")

    print("\n" + cost_report())
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch a page's raw HTML, whole, with response metadata.")
    ap.add_argument("url", nargs="?", help="page URL")
    ap.add_argument("--refresh", action="store_true", help="bypass the cache")
    ap.add_argument("--headers", action="store_true", help="print only the response-level signals")
    ap.add_argument("--html", action="store_true", help="print the raw HTML to stdout")
    ap.add_argument("--out", help="write the full record to this JSON file")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()
    if not args.url:
        ap.error("url required (or use --selftest)")

    data = fetch(args.url, refresh=args.refresh)

    if args.out:
        Path(args.out).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{args.url}: {data['status']}, {len(data['html'])} chars via {data['engine']} -> {args.out}")
    elif args.headers:
        print(json.dumps(robots_signals(data), indent=2))
    elif args.html:
        sys.stdout.write(data["html"])
    else:
        print(json.dumps({**robots_signals(data), "html_chars": len(data["html"]),
                          "cached": data["_meta"]["cached"]}, indent=2))

    print(cost_report(), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Crawl a site once and record everything the eleven Tier 3 checks need.

The thesis of this skill is crawl once, check eleven times. Every check in technical.py
reads this graph rather than making its own requests, so a full technical audit costs one
pass over the site instead of six.

Why this does NOT call seo-onpage's fetch_page.fetch(), which is otherwise the right
fetcher and is used by the rest of this skill:

  fetch_page escalates to a Playwright render whenever a page returns thin text. That is
  correct for a single-page on-page audit and wrong here, for two reasons.

  Cost: a 300-URL crawl spending five seconds of Playwright on every JS-heavy page takes
  half an hour and produces nothing extra.

  Correctness, which is the real one: comparing raw HTML against rendered HTML IS the
  JavaScript SEO check (course/26). A crawler that silently substitutes rendered HTML
  would report "no rendering problem" on precisely the sites that have one, and the
  finding would be invisible because the evidence was destroyed at fetch time. So this
  crawls raw, always. render_diff.py does the rendering deliberately, separately, and on a
  sample.

Politeness, because this is the first script in the SEO family that hits a site we do not
own at volume. It obeys the target's own robots.txt including crawl-delay, runs
single-threaded with a floor of 0.5s between live requests, caps at 300 URLs by default,
and refuses to start a crawl of more than CONFIRM_ABOVE pages without --yes. Cache hits
are free and are not delayed.

Cache: one JSON per origin in .cache/crawls/, keyed on sha1(origin) only - no client, no
date - so re-running an audit after a fix is free and resumable. Use --refresh to recrawl.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import sys
import time
import urllib.robotparser
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO = SKILL_DIR.parents[2]
sys.path.insert(0, str(REPO / ".claude" / "skills" / "web-scraper" / "scripts"))

from engines.base import is_safe_url  # noqa: E402
from engines.http_engine import HEADERS  # noqa: E402

CACHE_DIR = SKILL_DIR / ".cache" / "crawls"

# Bump whenever a field the checks read is added or changes meaning. A cached graph from an
# older version is recrawled rather than served, because a check reading a field that did
# not exist yet reports `unknown` on a site that is actually fine - a silent wrong answer.
GRAPH_VERSION = 2

DEFAULT_MAX_PAGES = 300
MIN_DELAY = 0.5
CONFIRM_ABOVE = 50          # above this many pages, --yes is required
SITEMAP_MAX_BYTES = 50 * 1024 * 1024   # course/22, [s188, s167]
SITEMAP_MAX_URLS = 50_000              # course/22, [s188, s167]

# Non-HTML we never want to enqueue as pages.
_SKIP_EXT = re.compile(
    r"\.(jpg|jpeg|png|gif|webp|avif|svg|ico|css|js|mjs|json|xml|pdf|zip|gz|mp4|webm|mp3|"
    r"woff2?|ttf|eot|dmg|exe|csv|xlsx?|docx?)(\?|$)", re.I)

REQUESTS = 0
CACHE_HITS = 0


# --------------------------------------------------------------------------- urls

def normalize_url(url: str) -> str:
    """Scheme added, host lowercased, fragment dropped, path left exactly as given.

    The path is deliberately not rstripped of "/", matching seo-onpage/fetch_page.py:
    /services and /services/ can be two separately indexable URLs, and collapsing them
    here would hide a duplicate-content finding (course/23) behind a dedup.
    """
    url = (url or "").strip()
    if not url:
        return url
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    p = urlparse(url)
    return urlunparse((p.scheme.lower(), p.netloc.lower(), p.path, p.params, p.query, ""))


def origin_of(url: str) -> str:
    p = urlparse(normalize_url(url))
    return f"{p.scheme}://{p.netloc}"


def _registrable(host: str) -> str:
    """Host minus a leading www. Enough to decide internal vs external without tldextract."""
    return (host or "").lower().removeprefix("www.")


def same_site(a: str, b: str) -> bool:
    return _registrable(urlparse(a).netloc) == _registrable(urlparse(b).netloc)


def _cache_path(origin: str) -> Path:
    return CACHE_DIR / (hashlib.sha1(origin.encode("utf-8")).hexdigest() + ".json")


# --------------------------------------------------------------------------- http

def _get(url: str, *, timeout: int = 25, allow_redirects: bool = True):
    """One raw GET. No rendering, ever - see the module docstring."""
    global REQUESTS
    import requests

    REQUESTS += 1
    return requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=allow_redirects)


def fetch_raw(url: str, *, timeout: int = 25, _retry: bool = True) -> dict:
    """Raw fetch with the response metadata the checks need. Never raises on a dead host.

    Retries ONCE on a 5xx or a transport error, after a short pause. A server error is the
    single most consequential thing this crawler can report - it fails `status.no_5xx`,
    drops the URL from the generated sitemap, and marks every internal link pointing at it
    as broken - so a one-shot fetch makes a momentary blip look like a site defect.

    This is not hypothetical. On the first live audit a Wix page returned one 502 and the
    report claimed a 5xx plus 37 broken internal links; three manual retries all returned
    200. The retry is deliberately single and only for 5xx: a 4xx is an answer, not a
    failure, and retrying it would just double the load for no information.
    """
    try:
        r = _get(url, timeout=timeout)
        if _retry and 500 <= r.status_code < 600:
            time.sleep(2)
            return fetch_raw(url, timeout=timeout, _retry=False)
        body = r.content or b""
        return {
            "url": url,
            "final_url": r.url,
            "status": r.status_code,
            "html": r.text,
            "bytes": len(body),
            "headers": {k.lower(): v for k, v in r.headers.items()},
            "redirect_chain": [{"status": h.status_code, "url": h.url} for h in r.history],
            "error": None,
        }
    except Exception as exc:  # noqa: BLE001 - an unreachable host is a finding, not a traceback
        if _retry:
            time.sleep(2)
            return fetch_raw(url, timeout=timeout, _retry=False)
        return {"url": url, "final_url": url, "status": 0, "html": "", "bytes": 0,
                "headers": {}, "redirect_chain": [], "error": f"{type(exc).__name__}: {exc}"}


# --------------------------------------------------------------------------- robots

AI_BOTS = {
    # course/21 + seo-scoreboard. Block trainers, allow retrievers that send referrals.
    "GPTBot": "block", "ClaudeBot": "block", "CCBot": "block", "Google-Extended": "block",
    "OAI-SearchBot": "allow", "ChatGPT-User": "allow", "Claude-SearchBot": "allow",
    "PerplexityBot": "allow",
}


def _robots_groups(text: str) -> list[tuple[list[str], list[tuple[str, str]]]]:
    """robots.txt as [(user-agents, [(directive, value), ...])], the way the spec reads it.

    Consecutive `User-agent:` lines share one rule block. A flat line scan instead of this
    grouping is why the first live run of this crawler reported `disallow_all` on a Wix
    site whose only `Disallow: /` belonged to PetalBot - which would have shipped "your
    site blocks all crawlers" as the headline finding of a clean audit.
    """
    groups: list[tuple[list[str], list[tuple[str, str]]]] = []
    agents: list[str] = []
    rules: list[tuple[str, str]] = []
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        field, _, value = line.partition(":")
        field, value = field.strip().lower(), value.strip()
        if field == "user-agent":
            if rules:                      # rules ended the previous group; start a new one
                groups.append((agents, rules))
                agents, rules = [], []
            agents.append(value)
        elif agents:
            rules.append((field, value))
    if agents:
        groups.append((agents, rules))
    return groups


def _rules_for(groups, agent: str) -> list[tuple[str, str]]:
    """The rules that actually bind `agent`: its own group if it has one, else the wildcard."""
    wild: list[tuple[str, str]] = []
    for agents, rules in groups:
        lowered = [a.lower() for a in agents]
        if agent.lower() in lowered:
            return rules
        if "*" in lowered:
            wild = rules
    return wild


def fetch_robots(origin: str) -> dict:
    """robots.txt with the two rules that break sites already evaluated (course/21)."""
    url = origin.rstrip("/") + "/robots.txt"
    r = fetch_raw(url)
    text = r["html"] if r["status"] == 200 else ""

    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(url)
    try:
        rp.parse(text.splitlines())
    except Exception:  # noqa: BLE001 - a malformed file is itself the finding
        pass

    groups = _robots_groups(text)
    star = _rules_for(groups, "*")
    disallows = [v for k, v in star if k == "disallow" and v]
    sitemaps = [v for agents, rules in groups for k, v in rules if k == "sitemap"] or \
               [ln.split(":", 1)[1].strip() for ln in text.splitlines()
                if ln.strip().lower().startswith("sitemap:")]
    sitemaps = list(dict.fromkeys(s for s in sitemaps if s))

    blocked_assets = [d for d in disallows
                      if re.search(r"\.(css|js)|/wp-includes|/wp-content/themes|/assets|/static", d, re.I)]

    declared = {}
    for bot in AI_BOTS:
        own = next((rules for agents, rules in groups
                    if bot.lower() in [a.lower() for a in agents]), None)
        if own is not None:
            declared[bot] = "block" if any(k == "disallow" and v == "/" for k, v in own) else "allow"

    return {
        "url": url,
        "status": r["status"],
        "text": text,
        # course/21: a 5xx stops Googlebot crawling the whole site. A 404 is fine.
        "returns_200": r["status"] == 200,
        "is_5xx": 500 <= (r["status"] or 0) < 600,
        # Asked of the grouped parser, not of a flat line scan - see _robots_groups.
        "disallow_all": bool(text) and not rp.can_fetch("Googlebot", origin.rstrip("/") + "/"),
        "disallows": disallows,
        "sitemaps": sitemaps,
        "blocks_css_or_js": blocked_assets,
        "has_sitemap_directive": bool(sitemaps),
        "ai_policy_declared": declared,
        "mentions_deprecated_anthropic_ai": any(
            a.lower() == "anthropic-ai" for agents, _ in groups for a in agents),
        "crawl_delay": rp.crawl_delay("*"),
        "_parser": rp,
    }


# --------------------------------------------------------------------------- sitemaps

def _strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1]


def parse_sitemap(url: str, *, _depth: int = 0, _seen: set[str] | None = None) -> list[dict]:
    """Return one record per sitemap file, following index files one level (course/22)."""
    import xml.etree.ElementTree as ET

    _seen = _seen if _seen is not None else set()
    if url in _seen or _depth > 2:
        return []
    _seen.add(url)

    r = fetch_raw(url)
    # lastmod_dates keeps the distinct dates, not just a count, because "every URL stamped
    # with today" is a named bad pattern (course/22) and a count cannot see it.
    rec = {"url": url, "status": r["status"], "bytes": r["bytes"], "is_index": False,
           "urls": [], "children": [], "error": r["error"], "lastmods": 0,
           "lastmod_dates": []}
    if r["status"] != 200:
        rec["error"] = rec["error"] or f"status {r['status']}"
        return [rec]

    raw = r["html"]
    if url.endswith(".gz"):
        try:
            raw = gzip.decompress(r["html"].encode("latin-1", "ignore")).decode("utf-8", "ignore")
        except Exception:  # noqa: BLE001
            pass

    try:
        root = ET.fromstring(raw.encode("utf-8", "ignore"))
    except ET.ParseError as exc:
        rec["error"] = f"XML parse error: {exc}"
        return [rec]

    tag = _strip_ns(root.tag)
    out = [rec]
    if tag == "sitemapindex":
        rec["is_index"] = True
        for sm in root:
            loc = next((c.text.strip() for c in sm if _strip_ns(c.tag) == "loc" and c.text), None)
            if loc:
                rec["children"].append(loc)
        for child in rec["children"]:
            out += parse_sitemap(child, _depth=_depth + 1, _seen=_seen)
    elif tag == "urlset":
        for u in root:
            loc = next((c.text.strip() for c in u if _strip_ns(c.tag) == "loc" and c.text), None)
            if loc:
                rec["urls"].append(normalize_url(loc))
            lm = next((c.text.strip() for c in u
                       if _strip_ns(c.tag) == "lastmod" and c.text), None)
            if lm:
                rec["lastmods"] += 1
                rec["lastmod_dates"].append(lm[:10])
        rec["lastmod_dates"] = sorted(set(rec["lastmod_dates"]))
    else:
        rec["error"] = f"unexpected root element <{tag}>"
    return out


def discover_sitemaps(origin: str, robots: dict) -> list[str]:
    """robots.txt Sitemap: directives first, then the two conventional locations."""
    found = list(dict.fromkeys(robots.get("sitemaps") or []))
    for guess in ("/sitemap.xml", "/sitemap_index.xml"):
        cand = origin.rstrip("/") + guess
        if cand not in found:
            r = fetch_raw(cand)
            if r["status"] == 200 and "<" in (r["html"] or "")[:2000]:
                found.append(cand)
    return found


# --------------------------------------------------------------------------- origin probes

def probe_origin(origin: str) -> dict:
    """Five requests for two facts no page-level crawl can answer.

    Host and protocol variants (course/23 step 1): http, https, www and non-www should all
    resolve to one version. Four unresolved homepages is the most common duplication on the
    web and it is invisible from inside a crawl that only ever requested one of them.

    The 404 probe (course/24 step 7): request a URL that cannot exist. A site returning 200
    for it has a soft-404 template, which wastes crawl budget and clutters the index. This
    is asked once per origin here rather than guessed per page in technical.py.
    """
    p = urlparse(origin)
    host = p.netloc
    alt = host[4:] if host.startswith("www.") else "www." + host

    variants = {}
    for scheme in ("https", "http"):
        for h in dict.fromkeys((host, alt)):
            u = f"{scheme}://{h}/"
            r = fetch_raw(u, timeout=15)
            variants[u] = {"status": r["status"], "final_url": normalize_url(r["final_url"]),
                           "hops": len(r["redirect_chain"]), "error": r["error"]}

    probe = origin.rstrip("/") + "/nexis-404-probe-" + hashlib.sha1(origin.encode()).hexdigest()[:10]
    r = fetch_raw(probe, timeout=15)
    return {
        "variants": variants,
        "resolves_to": sorted({v["final_url"] for v in variants.values()
                               if v["status"] == 200 and not v["error"]}),
        "missing_url_probe": {"url": probe, "status": r["status"],
                              "words": len((r["html"] or "").split()), "error": r["error"]},
    }


# --------------------------------------------------------------------------- page parse

_ROBOTS_DIRECTIVES = ("noindex", "nofollow", "none", "noarchive", "nosnippet", "noimageindex")


def parse_page(url: str, r: dict) -> dict:
    """Everything the eleven checks read off one page. Raw HTML in, one graph node out."""
    from bs4 import BeautifulSoup

    html = r.get("html") or ""
    headers = r.get("headers") or {}
    rec = {
        "url": url,
        "final_url": r.get("final_url") or url,
        "status": r.get("status"),
        "bytes": r.get("bytes", 0),
        "html_chars": len(html),
        "content_type": (headers.get("content-type") or "").split(";")[0].strip() or None,
        "x_robots_tag": headers.get("x-robots-tag"),
        "redirect_chain": r.get("redirect_chain") or [],
        "error": r.get("error"),
        "title": None, "h1": [], "meta_robots": None, "canonical": None,
        # canonical_raw survives absolutisation so the "use absolute URLs" rule stays
        # checkable; canonical_count catches the plugin conflict that makes Google ignore
        # every canonical on the page (both course/23).
        "canonical_raw": None, "canonical_count": 0,
        "hreflang": [], "jsonld": [], "microdata_types": [], "images": [],
        "outlinks": [], "internal_outlinks": [], "word_count": 0,
        "has_viewport": False, "lang": None,
    }
    if not html or "html" not in (rec["content_type"] or "html"):
        return rec

    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception as exc:  # noqa: BLE001
        rec["error"] = f"parse failed: {exc}"
        return rec

    # JSON-LD must come out BEFORE scripts are stripped. soup.body is the same tree as
    # soup, so decomposing first would report "no schema" on pages that carry it - the
    # exact bug seo-onpage/onpage.py documents having fixed.
    for tag in soup.find_all("script", attrs={"type": re.compile(r"ld\+json", re.I)}):
        blob = (tag.string or tag.get_text() or "").strip()
        if not blob:
            continue
        try:
            rec["jsonld"].append(json.loads(blob))
        except json.JSONDecodeError as exc:
            rec["jsonld"].append({"__parse_error__": str(exc), "__raw_head__": blob[:200]})

    rec["microdata_types"] = sorted({t.get("itemtype") for t in soup.find_all(attrs={"itemtype": True})
                                     if t.get("itemtype")})

    html_tag = soup.find("html")
    if html_tag:
        rec["lang"] = html_tag.get("lang")

    if soup.title and soup.title.string:
        rec["title"] = soup.title.string.strip()
    rec["h1"] = [h.get_text(" ", strip=True) for h in soup.find_all("h1")]

    mr = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
    if mr and mr.get("content"):
        rec["meta_robots"] = mr["content"].strip()
    grb = soup.find("meta", attrs={"name": re.compile(r"^googlebot$", re.I)})
    if grb and grb.get("content"):
        rec["meta_robots"] = ((rec["meta_robots"] or "") + "," + grb["content"].strip()).strip(",")

    cans = soup.find_all("link", attrs={"rel": lambda v: v and "canonical" in [x.lower() for x in
                                                                               (v if isinstance(v, list) else [v])]})
    cans = [c for c in cans if c.get("href")]
    rec["canonical_count"] = len(cans)
    if cans:
        rec["canonical_raw"] = cans[0]["href"].strip()
        rec["canonical"] = normalize_url(urljoin(url, rec["canonical_raw"]))

    for ln in soup.find_all("link", attrs={"hreflang": True}):
        if ln.get("href"):
            rec["hreflang"].append({"lang": (ln.get("hreflang") or "").strip(),
                                    "href": normalize_url(urljoin(url, ln["href"].strip()))})

    rec["has_viewport"] = bool(soup.find("meta", attrs={"name": re.compile(r"^viewport$", re.I)}))

    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        rec["images"].append({
            "src": urljoin(url, src) if src else None,
            "alt": img.get("alt"),
            "width": img.get("width"), "height": img.get("height"),
            "loading": (img.get("loading") or "").lower() or None,
            "fetchpriority": (img.get("fetchpriority") or "").lower() or None,
        })

    seen_links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        absu = normalize_url(urljoin(url, href))
        if absu in seen_links:
            continue
        seen_links.add(absu)
        entry = {"url": absu, "anchor": a.get_text(" ", strip=True)[:120],
                 "rel": " ".join(a.get("rel") or []) or None}
        rec["outlinks"].append(entry)
        if same_site(url, absu) and not _SKIP_EXT.search(absu):
            rec["internal_outlinks"].append(absu)

    for tag in soup(["script", "style", "noscript", "template"]):
        tag.decompose()
    rec["word_count"] = len(soup.get_text(" ", strip=True).split())
    return rec


def indexable(rec: dict) -> tuple[bool, str]:
    """Can this URL be indexed as itself? Returns (verdict, the reason it is not)."""
    if rec.get("status") != 200:
        return False, f"status {rec.get('status')}"
    directives = f"{rec.get('meta_robots') or ''},{rec.get('x_robots_tag') or ''}".lower()
    if "noindex" in directives or re.search(r"\bnone\b", directives):
        return False, "noindex"
    can = rec.get("canonical")
    if can and normalize_url(can) != normalize_url(rec["url"]):
        return False, f"canonical points elsewhere ({can})"
    return True, ""


# --------------------------------------------------------------------------- crawl

def crawl(seed: str, *, max_pages: int = DEFAULT_MAX_PAGES, delay: float = MIN_DELAY,
          respect_robots: bool = True, refresh: bool = False, cache: bool = True) -> dict:
    """Sitemap-first, BFS fallback. One graph out."""
    global CACHE_HITS
    seed = normalize_url(seed)
    origin = origin_of(seed)
    path = _cache_path(origin)

    if cache and not refresh and path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("graph_version") == GRAPH_VERSION:
                CACHE_HITS += 1
                data.setdefault("_meta", {})["cached"] = True
                return data
            print(f"[crawl] cached graph is v{data.get('graph_version', 1)}, need "
                  f"v{GRAPH_VERSION} - recrawling", file=sys.stderr)
        except (json.JSONDecodeError, OSError):
            pass

    if not is_safe_url(seed):
        raise ValueError(f"refusing to crawl a private/loopback host: {seed}")

    robots = fetch_robots(origin)
    rp = robots.pop("_parser", None)
    crawl_delay = robots.get("crawl_delay")
    effective_delay = max(delay, MIN_DELAY, float(crawl_delay or 0))

    sitemap_urls = discover_sitemaps(origin, robots)
    sitemap_files = []
    submitted: list[str] = []
    for sm in sitemap_urls:
        for rec in parse_sitemap(sm):
            sitemap_files.append(rec)
            submitted += rec["urls"]
    submitted = list(dict.fromkeys(submitted))

    # A sitemap URL that robots.txt disallows is a course/22 contradiction: the file says
    # "index this", the other file says "never fetch it". Recorded here because rp is in
    # hand and is not serialisable.
    disallowed_submitted = [u for u in submitted
                            if rp is not None and robots["returns_200"] and not rp.can_fetch("*", u)]

    probe = probe_origin(origin)

    # Sitemap first, seed always included, BFS fills the rest.
    queue: list[tuple[str, int, str]] = [(seed, 0, "seed")]
    queued = {seed}
    for u in submitted:
        if u not in queued and same_site(seed, u):
            queue.append((u, 1, "sitemap"))
            queued.add(u)

    pages: dict[str, dict] = {}
    skipped_by_robots: list[str] = []
    print(f"[crawl] {origin}: {len(submitted)} sitemap URL(s), cap {max_pages}, "
          f"delay {effective_delay}s", file=sys.stderr)

    while queue and len(pages) < max_pages:
        url, depth, via = queue.pop(0)
        if respect_robots and rp is not None and robots["returns_200"] and not rp.can_fetch("*", url):
            skipped_by_robots.append(url)
            continue

        r = fetch_raw(url)
        rec = parse_page(url, r)
        rec["depth"] = depth
        rec["discovered_via"] = via
        rec["in_sitemap"] = url in set(submitted)
        ok, why = indexable(rec)
        rec["indexable"] = ok
        rec["not_indexable_because"] = why
        pages[url] = rec

        if len(pages) % 10 == 0 or len(pages) == max_pages:
            print(f"[crawl] {len(pages)}/{max_pages} fetched", file=sys.stderr)

        # BFS: only follow links from indexable HTML, and never past the cap.
        if rec["status"] == 200 and len(pages) + len(queue) < max_pages * 3:
            for link in rec["internal_outlinks"]:
                if link not in queued:
                    queued.add(link)
                    queue.append((link, depth + 1, "link"))
        time.sleep(effective_delay)

    # Depth is BFS order, which is the true click depth from the seed only for pages
    # reached by links. Sitemap-seeded pages get their real depth backfilled here.
    _backfill_depth(seed, pages)

    crawled = set(pages)
    graph = {
        "graph_version": GRAPH_VERSION,
        "origin": origin,
        "seed": seed,
        "crawled_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "robots": robots,
        "origin_probe": probe,
        "sitemap_files": sitemap_files,
        "sitemap_urls_submitted": submitted,
        "sitemap_urls_disallowed": disallowed_submitted,
        "pages": pages,
        "skipped_by_robots": skipped_by_robots,
        "stats": {
            "pages_crawled": len(pages),
            "cap": max_pages,
            "hit_cap": len(pages) >= max_pages,
            "queue_remaining": len(queue),
            "indexable": sum(1 for p in pages.values() if p.get("indexable")),
            "in_sitemap_not_crawled": len([u for u in submitted if u not in crawled]),
            "crawled_not_in_sitemap": len([u for u in crawled if u not in set(submitted)]),
            "requests": REQUESTS,
        },
        "_meta": {"cached": False, "delay": effective_delay,
                  "respected_robots": respect_robots},
    }

    if cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        try:
            path.write_text(json.dumps(graph, ensure_ascii=False, indent=1), encoding="utf-8")
        except OSError as exc:
            print(f"[crawl] cache write failed (continuing): {exc}", file=sys.stderr)
    return graph


def _backfill_depth(seed: str, pages: dict[str, dict]) -> None:
    """True click depth from the seed, over links actually found (course/25)."""
    for rec in pages.values():
        rec["depth"] = None
    if seed not in pages:
        return
    pages[seed]["depth"] = 0
    frontier = [seed]
    d = 0
    while frontier:
        d += 1
        nxt = []
        for u in frontier:
            for link in pages[u].get("internal_outlinks") or []:
                tgt = pages.get(link)
                if tgt is not None and tgt.get("depth") is None:
                    tgt["depth"] = d
                    nxt.append(link)
        frontier = nxt


def cost_report() -> str:
    return (f"crawl: {REQUESTS} HTTP request(s), {CACHE_HITS} cached crawl(s) reused. "
            "No paid API used.")


# --------------------------------------------------------------------------- selftest

_FIXTURE = """<!doctype html><html lang="en"><head>
<title>Fixture</title>
<meta name="robots" content="noindex,follow">
<meta name="viewport" content="width=device-width">
<link rel="canonical" href="https://example.com/other">
<link rel="alternate" hreflang="en-gb" href="/en-gb/">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"Article"}</script>
<style>.a{color:red}</style></head><body>
<h1>One</h1><h1>Two</h1>
<p>Some visible words here for the counter to find.</p>
<img src="/hero.jpg" alt="hero" loading="lazy" width="800" height="600">
<a href="/about">About</a><a href="https://external.test/x">Out</a><a href="#frag">Frag</a>
<script>var x = 1;</script></body></html>"""


def _selftest() -> int:
    """Fixture-based. No network, no site crawled."""
    ok = True

    print("1. parse_page pulls JSON-LD out before scripts are stripped")
    rec = parse_page("https://example.com/p", {"html": _FIXTURE, "status": 200,
                                               "headers": {"content-type": "text/html"},
                                               "final_url": "https://example.com/p",
                                               "redirect_chain": [], "bytes": len(_FIXTURE)})
    if len(rec["jsonld"]) == 1 and rec["jsonld"][0].get("@type") == "Article":
        print("   PASS: 1 JSON-LD block recovered")
    else:
        print(f"   FAIL: got {rec['jsonld']}. Scripts are being decomposed before extraction.")
        ok = False

    print("2. head signals parsed")
    checks = {
        "title": rec["title"] == "Fixture",
        "two h1": len(rec["h1"]) == 2,
        "meta robots": rec["meta_robots"] == "noindex,follow",
        "canonical absolutised": rec["canonical"] == "https://example.com/other",
        "hreflang absolutised": rec["hreflang"] == [{"lang": "en-gb", "href": "https://example.com/en-gb/"}],
        "viewport": rec["has_viewport"] is True,
        "lang": rec["lang"] == "en",
    }
    bad = [k for k, v in checks.items() if not v]
    print("   PASS: all head signals" if not bad else f"   FAIL: {bad}")
    ok &= not bad

    print("3. internal vs external links split, fragments and assets dropped")
    if rec["internal_outlinks"] == ["https://example.com/about"] and len(rec["outlinks"]) == 2:
        print("   PASS: 1 internal, 2 total, fragment dropped")
    else:
        print(f"   FAIL: internal={rec['internal_outlinks']} outlinks={len(rec['outlinks'])}")
        ok = False

    print("4. lazy-loaded image recorded (the LCP fault aruntastic names)")
    img = rec["images"][0]
    if img["loading"] == "lazy" and img["width"] == "800" and img["alt"] == "hero":
        print("   PASS: loading/width/alt captured")
    else:
        print(f"   FAIL: {img}")
        ok = False

    print("5. indexable() reports the reason, not just a boolean")
    good, why = indexable(rec)
    if not good and why == "noindex":
        print("   PASS: noindex detected and named")
    else:
        print(f"   FAIL: ({good}, {why!r})")
        ok = False
    can_only = dict(rec, meta_robots=None, x_robots_tag=None)
    good2, why2 = indexable(can_only)
    if not good2 and "canonical points elsewhere" in why2:
        print("   PASS: cross-canonical also caught, separately from noindex")
    else:
        print(f"   FAIL: ({good2}, {why2!r})")
        ok = False

    print("6. normalize_url keeps the trailing slash distinction")
    if normalize_url("Example.com/a/") != normalize_url("example.com/a"):
        print("   PASS: /a and /a/ stay distinct, so duplicate content stays visible")
    else:
        print("   FAIL: trailing slash collapsed; a course/23 finding would be hidden")
        ok = False

    print("7. _backfill_depth computes real click depth, not BFS discovery order")
    pages = {
        "https://e.test/": {"internal_outlinks": ["https://e.test/a"]},
        "https://e.test/a": {"internal_outlinks": ["https://e.test/b"]},
        "https://e.test/b": {"internal_outlinks": []},
        "https://e.test/orphan": {"internal_outlinks": []},
    }
    _backfill_depth("https://e.test/", pages)
    depths = {k.rsplit("/", 1)[-1] or "home": v["depth"] for k, v in pages.items()}
    if depths == {"home": 0, "a": 1, "b": 2, "orphan": None}:
        print("   PASS: depths 0/1/2 and the orphan is None, not 0")
    else:
        print(f"   FAIL: {depths}")
        ok = False

    print("8. robots.txt groups by user-agent (the PetalBot false positive)")
    # The real robots.txt that broke the flat scan: `Disallow: /` belongs to PetalBot only,
    # and the two AdsBot agents are stacked above one shared rule block.
    wix = """User-agent: *
Allow: /
Disallow: *?lightbox=

# Optimization for Google Ads Bot
User-agent: AdsBot-Google-Mobile
User-agent: AdsBot-Google
Disallow: /_partials*

# Block PetalBot
User-agent: PetalBot
Disallow: /

Sitemap: https://example.com/sitemap.xml"""
    groups = _robots_groups(wix)
    star = _rules_for(groups, "*")
    petal = _rules_for(groups, "PetalBot")
    adsbot = _rules_for(groups, "AdsBot-Google")
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(wix.splitlines())
    cases = {
        "wildcard has no Disallow: /": ("disallow", "/") not in star,
        "PetalBot does": ("disallow", "/") in petal,
        "stacked user-agents share one block": ("disallow", "/_partials*") in adsbot,
        "Googlebot may fetch the root": rp.can_fetch("Googlebot", "https://example.com/"),
        "PetalBot may not": not rp.can_fetch("PetalBot", "https://example.com/"),
    }
    bad = [k for k, v in cases.items() if not v]
    if not bad:
        print("   PASS: a per-agent block no longer reads as a site-wide block")
    else:
        print(f"   FAIL: {bad}")
        ok = False

    print("9. a transient 5xx is retried once before it becomes a finding")
    calls = {"n": 0}
    real_get = globals()["_get"]

    class _Resp:
        def __init__(self, code):
            self.status_code, self.url, self.content = code, "https://e.test/p", b"<html></html>"
            self.text, self.headers, self.history = "<html></html>", {}, []

    def _flaky(url, **kw):
        calls["n"] += 1
        return _Resp(502 if calls["n"] == 1 else 200)

    globals()["_get"] = _flaky
    globals()["time"].sleep = lambda *_: None      # no real pause in a test
    try:
        got = fetch_raw("https://e.test/p")
    finally:
        globals()["_get"] = real_get
    if got["status"] == 200 and calls["n"] == 2:
        print("   PASS: 502 then 200 reports 200, so one blip is not 37 broken links")
    else:
        print(f"   FAIL: status={got['status']} after {calls['n']} call(s)")
        ok = False

    calls["n"] = 0

    def _always_502(url, **kw):
        calls["n"] += 1
        return _Resp(502)

    globals()["_get"] = _always_502
    try:
        got = fetch_raw("https://e.test/p")
    finally:
        globals()["_get"] = real_get
    if got["status"] == 502 and calls["n"] == 2:
        print("   PASS: a persistent 502 still reports 502, after exactly one retry")
    else:
        print(f"   FAIL: status={got['status']} after {calls['n']} call(s)")
        ok = False

    print("\n" + cost_report())
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# --------------------------------------------------------------------------- cli

def main() -> int:
    ap = argparse.ArgumentParser(description="Crawl a site once into the shared technical graph.")
    ap.add_argument("url", nargs="?", help="seed URL or domain")
    ap.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES)
    ap.add_argument("--delay", type=float, default=MIN_DELAY,
                    help=f"seconds between live requests (floor {MIN_DELAY}, robots crawl-delay wins)")
    ap.add_argument("--ignore-robots", action="store_true",
                    help="crawl paths the target disallows (records it in the graph)")
    ap.add_argument("--refresh", action="store_true", help="recrawl, ignoring the cached graph")
    ap.add_argument("--yes", action="store_true",
                    help=f"confirm a crawl of more than {CONFIRM_ABOVE} pages")
    ap.add_argument("--out", help="write the graph to this JSON file")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()
    if not args.url:
        ap.error("url required (or use --selftest)")

    cached = _cache_path(origin_of(args.url)).exists() and not args.refresh
    if args.max_pages > CONFIRM_ABOVE and not args.yes and not cached:
        print(f"This will make up to {args.max_pages} requests to {origin_of(args.url)}, a site "
              f"we do not own.\nRe-run with --yes to confirm, or lower --max-pages.", file=sys.stderr)
        return 2

    g = crawl(args.url, max_pages=args.max_pages, delay=args.delay,
              respect_robots=not args.ignore_robots, refresh=args.refresh)

    if args.out:
        Path(args.out).write_text(json.dumps(g, ensure_ascii=False, indent=1), encoding="utf-8")
        print(args.out)
    else:
        print(json.dumps({"origin": g["origin"], "robots_status": g["robots"]["status"],
                          "sitemaps": len(g["sitemap_files"]), **g["stats"]}, indent=2))
    print(cost_report(), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

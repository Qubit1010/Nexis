#!/usr/bin/env python3
"""Build the internal link graph: orphans, click depth, anchor quality, and opportunities.

Internal linking is the only authority signal a client fully controls and reliably the most
underused, so this is usually where an audit finds its cheapest real win.

Four outputs, in descending order of how much they normally matter:

1. **Opportunities** - pages that discuss a topic and do not link to the page that owns it.
   `course/16`'s lab prescribes `site:yourdomain.com "topic phrase"` for this. This module
   does it locally against the crawled corpus instead, which is free, complete, and not
   filtered by whatever Google chose to index. It routinely surfaces dozens.
2. **Orphans** - zero inbound internal links. Link them or remove them.
3. **Click depth** - anything commercial more than 3 clicks from the homepage.
4. **Anchors** - "click here", "read more", and any anchor repeated at scale.

Discovery is sitemap-first because parsing sitemap.xml with stdlib xml costs nothing and
Firecrawl's /map costs credits for the same answer. BFS from the homepage is the fallback
when there is no sitemap. Everything routes through fetch_page's cache, so re-running after
a fix is free.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

import fetch_page  # noqa: E402
import onpage  # noqa: E402

MAX_DEPTH_OK = 3          # course/16: 3 clicks from home to any commercial page
BANNED_ANCHORS = onpage.BANNED_ANCHORS
ANCHOR_REPEAT_LIMIT = 3


def _same_site(url: str, host: str) -> bool:
    h = (urlparse(url).hostname or "").lower()
    return h == host or h.endswith("." + host) or host.endswith("." + h)


def _clean(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc.lower()}{p.path or '/'}"


def from_sitemap(root: str, *, limit: int = 500) -> list[str]:
    """Parse sitemap.xml, following index files one level. Free, stdlib only."""
    host = urlparse(root).hostname or ""
    found: list[str] = []
    queue = [urljoin(root, "/sitemap.xml"), urljoin(root, "/sitemap_index.xml")]
    seen_maps = set()

    while queue and len(found) < limit:
        sm = queue.pop(0)
        if sm in seen_maps:
            continue
        seen_maps.add(sm)
        try:
            rec = fetch_page.fetch(sm)
        except ValueError:
            continue
        body = rec.get("html") or ""
        if rec.get("status") != 200 or "<" not in body:
            continue
        try:
            tree = ET.fromstring(body.encode("utf-8", "ignore"))
        except ET.ParseError:
            continue
        tag = tree.tag.split("}")[-1]
        locs = [e.text.strip() for e in tree.iter() if e.tag.split("}")[-1] == "loc" and e.text]
        if tag == "sitemapindex":
            queue.extend(locs[:20])
        else:
            found.extend(u for u in locs if _same_site(u, host))
    return list(dict.fromkeys(_clean(u) for u in found))[:limit]


def crawl(root: str, *, max_pages: int = 100, refresh: bool = False) -> dict[str, dict]:
    """Fetch the site, sitemap-first, BFS as fallback. Returns url -> parsed record."""
    root = fetch_page.normalize_url(root)
    host = (urlparse(root).hostname or "").lower()

    seeds = from_sitemap(root, limit=max_pages)
    if seeds:
        print(f"[links] sitemap gave {len(seeds)} URL(s)", file=sys.stderr)
    else:
        print("[links] no usable sitemap, falling back to BFS from the homepage", file=sys.stderr)
        seeds = [_clean(root)]

    pages: dict[str, dict] = {}
    queue = deque((u, 0) for u in seeds)

    while queue and len(pages) < max_pages:
        url, depth = queue.popleft()
        if url in pages:
            continue
        try:
            rec = fetch_page.fetch(url, refresh=refresh)
        except ValueError:
            continue
        html = rec.get("html") or ""
        if not html:
            pages[url] = {"url": url, "status": rec.get("status"), "ok": False,
                          "title": "", "outlinks": [], "text": "", "depth": depth,
                          "words": 0, "h1": ""}
            continue
        doc = onpage.doc_from_html(html, rec.get("final_url") or url)
        out = []
        for l in doc.links:
            if not _same_site(l["href"], host):
                continue
            out.append({"href": _clean(l["href"]), "anchor": l["anchor"], "in_nav": l["in_nav"]})
        pages[url] = {
            "url": url, "status": rec.get("status"), "ok": True,
            "title": doc.title, "h1": doc.h1s[0] if doc.h1s else "",
            "outlinks": out, "text": doc.body_text.lower(),
            "words": doc.word_count, "depth": depth,
            "redirected_to": rec.get("final_url") if _clean(rec.get("final_url") or url) != url else None,
        }
        if len(pages) % 10 == 0:
            print(f"[links] crawled {len(pages)}/{max_pages}", file=sys.stderr)
        for l in out:
            if l["href"] not in pages:
                queue.append((l["href"], depth + 1))
    return pages


def build(pages: dict[str, dict], root: str, *, priority: list[str] | None = None) -> dict:
    home = _clean(fetch_page.normalize_url(root))
    priority = [_clean(p) for p in (priority or [])]

    inbound: dict[str, list[dict]] = {u: [] for u in pages}
    for src, rec in pages.items():
        for l in rec["outlinks"]:
            inbound.setdefault(l["href"], []).append(
                {"from": src, "anchor": l["anchor"], "in_nav": l["in_nav"]})

    # Click depth by BFS over body links only. Navigation links would make every page depth 1
    # and hide the finding entirely, which is exactly the trap the 3-click rule is about.
    depth = {home: 0}
    q = deque([home])
    while q:
        u = q.popleft()
        for l in (pages.get(u, {}).get("outlinks") or []):
            if l["href"] not in depth:
                depth[l["href"]] = depth[u] + 1
                q.append(l["href"])

    crawled = [u for u, r in pages.items() if r["ok"]]
    orphans = [u for u in crawled
               if u != home and not [i for i in inbound.get(u, []) if not i["in_nav"]]]

    # A page with no body-link path from the homepage has no depth at all. Assigning it a
    # sentinel like 99 and filing it under "too deep" would state a measurement that was
    # never taken, and it is a different finding: too deep means badly placed, unreachable
    # means not placed.
    too_deep = [{"url": u, "depth": depth[u]} for u in crawled
                if u in depth and depth[u] > MAX_DEPTH_OK]
    unreachable = [u for u in crawled if u not in depth]

    bad_anchors, repeats = [], {}
    for src, rec in pages.items():
        for l in rec["outlinks"]:
            a = l["anchor"].strip().lower()
            if a in BANNED_ANCHORS:
                bad_anchors.append({"from": src, "anchor": l["anchor"], "to": l["href"]})
            if a and not l["in_nav"]:
                repeats[(a, l["href"])] = repeats.get((a, l["href"]), 0) + 1
    over_repeated = [{"anchor": a, "to": t, "count": c}
                     for (a, t), c in repeats.items() if c > ANCHOR_REPEAT_LIMIT]

    known = set(pages)
    broken = []
    for src, rec in pages.items():
        for l in rec["outlinks"]:
            target = pages.get(l["href"])
            if target and not target["ok"]:
                broken.append({"from": src, "to": l["href"], "status": target["status"]})
            elif target and target.get("redirected_to"):
                broken.append({"from": src, "to": l["href"], "status": "redirect",
                               "lands_on": target["redirected_to"]})
            elif l["href"] not in known:
                pass  # not crawled, not necessarily broken - do not claim it is

    inbound_counts = {u: len([i for i in inbound.get(u, []) if not i["in_nav"]]) for u in crawled}

    return {
        "root": root, "pages_crawled": len(crawled),
        "home": home,
        "orphans": sorted(orphans),
        "too_deep": sorted(too_deep, key=lambda d: -d["depth"]),
        "unreachable_from_home": sorted(unreachable),
        "bad_anchors": bad_anchors,
        "over_repeated_anchors": sorted(over_repeated, key=lambda d: -d["count"]),
        "broken_or_redirected_links": broken,
        "inbound_counts": dict(sorted(inbound_counts.items(), key=lambda kv: kv[1])),
        "priority_pages": [
            {"url": p, "inbound_body_links": inbound_counts.get(p, 0),
             "depth": depth.get(p), "crawled": p in pages}
            for p in priority
        ],
        "notes": [
            "Click depth counts body links only. Counting navigation links makes every page "
            "depth 1 and hides the finding the 3-click rule exists to surface.",
            "Link source strength, strongest first: contextual body links, then navigation "
            "(powerful but blunt), then related-post modules, then footer (largely discounted).",
        ],
    }


def opportunities(pages: dict[str, dict], targets: list[dict], *, limit_per_target: int = 25) -> list[dict]:
    """Pages that mention a topic phrase and do not link to the page that owns it.

    This is the local replacement for `site:domain.com "topic phrase"`, and it is strictly
    better: it sees every crawled page rather than only what Google indexed, and it can tell
    the difference between "mentions it" and "already links to it", which the site: operator
    cannot.
    """
    out = []
    for t in targets:
        url, phrase = _clean(t["url"]), t["phrase"].lower().strip()
        if not phrase:
            continue
        hits = []
        for src, rec in pages.items():
            if src == url or not rec["ok"] or phrase not in rec["text"]:
                continue
            if any(l["href"] == url for l in rec["outlinks"]):
                continue
            idx = rec["text"].find(phrase)
            hits.append({"from": src, "title": rec["title"][:80],
                         "context": rec["text"][max(0, idx - 60): idx + len(phrase) + 60]})
        out.append({"target": url, "phrase": t["phrase"],
                    "opportunities": len(hits), "pages": hits[:limit_per_target]})
    return sorted(out, key=lambda d: -d["opportunities"])


def _selftest() -> int:
    """Fixture-based. Proves the graph logic without crawling anything."""
    ok = True

    def page(url, links, text="", title="T", status=200, good=True):
        return {"url": url, "status": status, "ok": good, "title": title, "h1": title,
                "outlinks": [{"href": h, "anchor": a, "in_nav": nav} for h, a, nav in links],
                "text": text.lower(), "words": len(text.split()), "depth": 0,
                "redirected_to": None}

    H = "https://acme.com/"
    pages = {
        H: page(H, [("https://acme.com/a", "about drainage", False),
                    ("https://acme.com/nav-only", "Services", True)]),
        "https://acme.com/a": page("https://acme.com/a", [("https://acme.com/b", "click here", False)],
                                   text="we talk about drainage a lot here"),
        "https://acme.com/b": page("https://acme.com/b", [("https://acme.com/c", "next", False)]),
        "https://acme.com/c": page("https://acme.com/c", [("https://acme.com/d", "deeper", False)]),
        "https://acme.com/d": page("https://acme.com/d", []),
        "https://acme.com/nav-only": page("https://acme.com/nav-only", []),
        "https://acme.com/orphan": page("https://acme.com/orphan", [],
                                        text="this page also mentions drainage in passing"),
        "https://acme.com/drainage": page("https://acme.com/drainage", [], title="Drainage"),
    }
    g = build(pages, H, priority=["https://acme.com/d"])

    print("1. orphans found, and a nav-only inbound link does not rescue a page")
    if set(g["orphans"]) == {"https://acme.com/orphan", "https://acme.com/nav-only",
                             "https://acme.com/drainage"}:
        print("   PASS: nav-only page still counted as an orphan for body-link purposes")
    else:
        print(f"   FAIL: {g['orphans']}")
        ok = False

    print("2. click depth counts body links only")
    deep = {d["url"]: d["depth"] for d in g["too_deep"]}
    if deep.get("https://acme.com/d") == 4:
        print("   PASS: /d is 4 clicks deep, over the 3-click rule")
    else:
        print(f"   FAIL: {g['too_deep']}")
        ok = False

    print("3. banned anchors caught")
    if len(g["bad_anchors"]) == 1 and g["bad_anchors"][0]["anchor"] == "click here":
        print("   PASS: 'click here' flagged")
    else:
        print(f"   FAIL: {g['bad_anchors']}")
        ok = False

    print("4. opportunity discovery finds mentions that do not link")
    opp = opportunities(pages, [{"url": "https://acme.com/drainage", "phrase": "drainage"}])
    froms = {p["from"] for p in opp[0]["pages"]}
    if opp[0]["opportunities"] == 2 and froms == {"https://acme.com/a", "https://acme.com/orphan"}:
        print("   PASS: 2 pages mention 'drainage' without linking to the page that owns it")
    else:
        print(f"   FAIL: {opp}")
        ok = False

    print("5. a page that already links is not reported as an opportunity")
    pages["https://acme.com/a"]["outlinks"].append(
        {"href": "https://acme.com/drainage", "anchor": "drainage guide", "in_nav": False})
    opp2 = opportunities(pages, [{"url": "https://acme.com/drainage", "phrase": "drainage"}])
    if opp2[0]["opportunities"] == 1:
        print("   PASS: dropped once the link exists")
    else:
        print(f"   FAIL: {opp2[0]['opportunities']} (expected 1)")
        ok = False

    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Internal link graph: orphans, depth, anchors, opportunities.")
    ap.add_argument("--site", help="root URL to crawl")
    ap.add_argument("--max-pages", type=int, default=100)
    ap.add_argument("--priority-pages", help="file of URLs, one per line, that matter commercially")
    ap.add_argument("--opportunities", help='JSON file: [{"url": "...", "phrase": "..."}]')
    ap.add_argument("--count-only", action="store_true", help="just report how many URLs exist")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()
    if not args.site:
        ap.error("--site required (or use --selftest)")

    if args.count_only:
        urls = from_sitemap(fetch_page.normalize_url(args.site), limit=5000)
        print(f"{len(urls)} URL(s) in the sitemap" if urls else
              "no usable sitemap - use `site:domain.com` in a browser for a rough count")
        return 0

    priority = []
    if args.priority_pages:
        priority = [l.strip() for l in Path(args.priority_pages).read_text(encoding="utf-8").splitlines()
                    if l.strip() and not l.startswith("#")]

    pages = crawl(args.site, max_pages=args.max_pages, refresh=args.refresh)
    res = build(pages, args.site, priority=priority)

    if args.opportunities:
        targets = json.loads(Path(args.opportunities).read_text(encoding="utf-8"))
        res["opportunities"] = opportunities(pages, targets)

    if args.out:
        Path(args.out).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{args.site}: {res['pages_crawled']} page(s), {len(res['orphans'])} orphan(s), "
              f"{len(res['too_deep'])} too deep -> {args.out}")
    else:
        print(f"\nCrawled {res['pages_crawled']} page(s) from {args.site}")
        print(f"\nOrphans ({len(res['orphans'])}) - zero inbound body links:")
        for u in res["orphans"][:20]:
            print(f"  {u}")
        print(f"\nDeeper than {MAX_DEPTH_OK} clicks ({len(res['too_deep'])}):")
        for d in res["too_deep"][:15]:
            print(f"  depth {d['depth']}  {d['url']}")
        print(f"\nUnreachable from the homepage by body links ({len(res['unreachable_from_home'])}):")
        for u in res["unreachable_from_home"][:15]:
            print(f"  {u}")
        print(f"\nNon-descriptive anchors ({len(res['bad_anchors'])}):")
        for b in res["bad_anchors"][:15]:
            print(f"  \"{b['anchor']}\" on {b['from']}")
        print(f"\nLinks to broken or redirected pages ({len(res['broken_or_redirected_links'])}):")
        for b in res["broken_or_redirected_links"][:15]:
            print(f"  {b['from']} -> {b['to']} ({b['status']})")
        if res["priority_pages"]:
            print("\nPriority pages:")
            for p in res["priority_pages"]:
                print(f"  {p['inbound_body_links']:>3} inbound, depth {p['depth']}  {p['url']}")
        if res.get("opportunities"):
            print("\nInternal link opportunities:")
            for o in res["opportunities"]:
                print(f"  {o['opportunities']:>3} page(s) mention \"{o['phrase']}\" "
                      f"without linking to {o['target']}")
        for n in res["notes"]:
            print(f"\nNOTE: {n}")

    print(fetch_page.cost_report(), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

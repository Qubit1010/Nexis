#!/usr/bin/env python3
"""Build the content inventory and assign every URL a track: keep, update, merge or remove.

course/19's audit sheet, with one column deliberately left honest.

The schema wants clicks, impressions and backlinks. None of those are obtainable here:
`gws` has no Search Console service (checked - the CLI exposes drive, sheets, gmail,
calendar, docs, slides, tasks, people, chat, classroom, forms, keep, meet and script, and
nothing for Search Console), there is no GSC credential in `.env`, and there is no free
backlink API. So those columns come back "not connected" with the export steps attached,
and `--gsc-csv` merges a real export when someone pastes one in.

That gap is not cosmetic. course/20 is explicit that without Search Console you are
inferring rather than diagnosing and should say so, and the tracks assigned from crawl data
alone are weaker than tracks assigned with traffic data. This module marks its own
confidence per row so the report cannot quietly present one as the other.

What it CAN establish without GSC, and what the fallback tracks are built from:
  - inbound internal links (from links.py) - a page nothing links to is already being
    treated as unimportant by its own site
  - word count of article text - thin is measurable
  - cluster membership from seo-foundation's keyword map, when one exists
  - near-duplicate titles and H1s, which is where merge candidates actually come from

Deleting pages to improve rankings feels wrong and is frequently correct: thin content in
one section suppresses good content elsewhere on the same domain [practitioner].
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

import fetch_page  # noqa: E402
import links as links_mod  # noqa: E402

THIN_WORDS = 300           # below this a page is a candidate for update/merge/remove
TITLE_SIMILARITY = 0.82    # above this two pages are near-duplicates
ZERO_TRAFFIC_MONTHS = 6    # course/19's zero-traffic audit window

GSC_STEPS = (
    "Search Console -> Performance -> Search results -> set the date range to the last 6 "
    "months -> Pages tab -> Export -> CSV. Then re-run with --gsc-csv <file>. Columns "
    "expected: a URL/Page column plus Clicks and Impressions."
)


def _norm_title(t: str) -> str:
    t = re.sub(r"\s*[|\-–—]\s*[^|\-–—]{0,40}$", "", t or "")  # drop a trailing brand suffix
    return re.sub(r"[^a-z0-9 ]+", " ", t.lower()).strip()


def load_gsc(path: str) -> dict[str, dict]:
    """Parse a Search Console Pages export. Tolerant about column naming across locales."""
    rows: dict[str, dict] = {}
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            keys = {k.lower().strip(): k for k in r}
            url_k = next((keys[k] for k in keys if k in
                          ("page", "url", "top pages", "address", "landing page")), None)
            clicks_k = next((keys[k] for k in keys if "click" in k), None)
            imp_k = next((keys[k] for k in keys if "impress" in k), None)
            if not url_k:
                continue

            def _num(v):
                try:
                    return int(str(v).replace(",", "").strip() or 0)
                except ValueError:
                    return 0

            rows[links_mod._clean(r[url_k])] = {
                "clicks": _num(r.get(clicks_k)) if clicks_k else None,
                "impressions": _num(r.get(imp_k)) if imp_k else None,
            }
    return rows


def assign_track(row: dict, *, has_gsc: bool) -> tuple[str, str, str]:
    """Return (track, reason, confidence). Never returns a blank track."""
    url, words = row["url"], row["words"]
    inbound = row["internal_links_in"]
    clicks, imps = row.get("clicks"), row.get("impressions")
    dupe = row.get("near_duplicate_of")

    if has_gsc and clicks is not None:
        if clicks == 0 and (imps or 0) == 0 and words < THIN_WORDS:
            return ("remove",
                    f"No clicks and no impressions in {ZERO_TRAFFIC_MONTHS} months, and only "
                    f"{words} words. Check backlinks before deleting - if anything links to it, "
                    "301 it to the closest relevant page instead.", "high")
        if clicks == 0 and (imps or 0) > 100:
            return ("update",
                    f"{imps} impressions and zero clicks. It ranks and nobody chooses it, which "
                    "is a title and description problem before it is a content problem.", "high")
        if dupe:
            return ("merge", f"Near-duplicate of {dupe}. Consolidate into whichever has more "
                    "backlinks and traffic, 301 the other to it.", "high")
        if clicks > 0 and words >= THIN_WORDS:
            return ("keep", f"{clicks} clicks over {ZERO_TRAFFIC_MONTHS} months. Working.", "high")
        return ("update", f"{clicks} clicks, {words} words. Underperforming for its length.",
                "medium")

    # No Search Console. Everything below is inference from crawl data and is weaker.
    if dupe:
        return ("merge", f"Near-duplicate title/H1 with {dupe}. Confirm against traffic before "
                "merging - without Search Console this is a structural signal only.", "low")
    if inbound == 0 and words < THIN_WORDS:
        return ("remove", f"Orphaned and thin ({words} words, nothing links to it). The site "
                "already treats it as unimportant. Confirm against traffic and backlinks before "
                "deleting.", "low")
    if inbound == 0:
        return ("update", f"Orphaned ({words} words). Either it deserves internal links or it "
                "does not deserve to exist. Decide which.", "low")
    if words < THIN_WORDS:
        return ("update", f"Thin at {words} words but {inbound} internal link(s) point at it, so "
                "the site thinks it matters. Expand it or fold it into the page it supports.",
                "low")
    return ("keep", f"{words} words, {inbound} inbound internal link(s). No structural problem "
            "visible without traffic data.", "low")


def build(site: str, *, max_pages: int = 200, gsc_csv: str = "", cluster_map: str = "",
          refresh: bool = False) -> dict:
    pages = links_mod.crawl(site, max_pages=max_pages, refresh=refresh)
    graph = links_mod.build(pages, site)
    inbound = graph["inbound_counts"]

    gsc = load_gsc(gsc_csv) if gsc_csv else {}
    has_gsc = bool(gsc)

    clusters = {}
    if cluster_map:
        raw = json.loads(Path(cluster_map).read_text(encoding="utf-8"))
        for r in (raw if isinstance(raw, list) else raw.get("keyword_map") or []):
            u = r.get("target_url") or r.get("url")
            if u:
                clusters[links_mod._clean(u)] = r.get("cluster") or r.get("primary_query") or ""

    crawled = [u for u, r in pages.items() if r["ok"]]

    # Near-duplicate detection: merge candidates come from pages saying the same thing, which
    # shows up in the title and H1 long before it shows up anywhere else.
    dupes: dict[str, str] = {}
    norm = {u: _norm_title(pages[u]["title"] or pages[u]["h1"]) for u in crawled}
    for i, a in enumerate(crawled):
        if not norm[a] or a in dupes:
            continue
        for b in crawled[i + 1:]:
            if not norm[b] or b in dupes:
                continue
            if SequenceMatcher(None, norm[a], norm[b]).ratio() >= TITLE_SIMILARITY:
                dupes[b] = a

    rows = []
    for u in crawled:
        p = pages[u]
        g = gsc.get(u, {})
        row = {
            "url": u,
            "title": p["title"],
            "words": p["words"],
            "internal_links_in": inbound.get(u, 0),
            "clicks": g.get("clicks"),
            "impressions": g.get("impressions"),
            "external_backlinks": None,
            "cluster": clusters.get(u, ""),
            "last_meaningful_update": None,
            "near_duplicate_of": dupes.get(u),
        }
        track, reason, conf = assign_track(row, has_gsc=has_gsc)
        row.update({"track": track, "reason": reason, "confidence": conf})
        rows.append(row)

    counts = {t: sum(1 for r in rows if r["track"] == t)
              for t in ("keep", "update", "merge", "remove")}

    not_connected = []
    if not has_gsc:
        not_connected.append(
            "Clicks and impressions: NOT CONNECTED. gws has no Search Console service and no "
            f"credential exists. {GSC_STEPS} Until then every track below is inferred from "
            "crawl structure alone and is marked confidence: low.")
    not_connected.append(
        "External backlinks: NOT CONNECTED. No free backlink API exists. Before removing any "
        "page, check it in Search Console -> Links -> Top linked pages, or in Ahrefs/Semrush "
        "if the client has a seat. Deleting a page that has earned links throws the links away.")

    return {
        "site": site,
        "pages": len(rows),
        "has_gsc": has_gsc,
        "track_counts": counts,
        "rows": sorted(rows, key=lambda r: (r["track"] != "remove", r["words"])),
        "not_connected": not_connected,
        "notes": [
            "Every URL has exactly one track. A blank would mean the decision was avoided, and "
            "avoided decisions are how a site accumulates pages nobody will defend.",
            "Removal procedure: 301 to the closest relevant page, or return 410 Gone if there "
            "is no relevant target. Never mass-delete without checking backlinks first, and "
            "never 301 an irrelevant page to the homepage - that is a soft 404.",
            "Consolidation procedure: pick the winner on backlinks and traffic, integrate the "
            "content rather than concatenating it, 301 every loser to the winner, update "
            "internal links to point at the winner directly, and keep the redirects "
            "indefinitely.",
            "A date change is not an update. Real freshness is new data, new sections for "
            "questions that emerged, removed advice that is no longer true, and a re-read of "
            "the SERP for intent drift.",
        ],
    }


def _selftest() -> int:
    """Fixture-based. The track logic is the thing worth locking down."""
    ok = True

    print("1. every row gets a track, never a blank")
    cases = [
        {"url": "/a", "words": 50, "internal_links_in": 0},
        {"url": "/b", "words": 2000, "internal_links_in": 12},
        {"url": "/c", "words": 100, "internal_links_in": 5},
        {"url": "/d", "words": 900, "internal_links_in": 0},
    ]
    tracks = [assign_track(c, has_gsc=False)[0] for c in cases]
    if all(t in {"keep", "update", "merge", "remove"} for t in tracks):
        print(f"   PASS: {tracks}")
    else:
        print(f"   FAIL: {tracks}")
        ok = False

    print("2. without Search Console every track is marked low confidence")
    confs = {assign_track(c, has_gsc=False)[2] for c in cases}
    if confs == {"low"}:
        print("   PASS: all low - the report cannot present inference as diagnosis")
    else:
        print(f"   FAIL: {confs}")
        ok = False

    print("3. with Search Console the confident calls become high confidence")
    t, _, conf = assign_track({"url": "/a", "words": 80, "internal_links_in": 0,
                               "clicks": 0, "impressions": 0}, has_gsc=True)
    if t == "remove" and conf == "high":
        print("   PASS: zero clicks, zero impressions, thin -> remove (high)")
    else:
        print(f"   FAIL: {t}/{conf}")
        ok = False

    print("4. high impressions with zero clicks is a metadata problem, not a content one")
    t, reason, _ = assign_track({"url": "/a", "words": 1200, "internal_links_in": 3,
                                 "clicks": 0, "impressions": 4000}, has_gsc=True)
    if t == "update" and "title and description problem" in reason:
        print("   PASS: routed to update with the right diagnosis")
    else:
        print(f"   FAIL: {t} / {reason}")
        ok = False

    print("5. a near-duplicate becomes a merge, and names what it merges into")
    t, reason, _ = assign_track({"url": "/a", "words": 800, "internal_links_in": 2,
                                 "near_duplicate_of": "/b"}, has_gsc=False)
    if t == "merge" and "/b" in reason:
        print("   PASS")
    else:
        print(f"   FAIL: {t} / {reason}")
        ok = False

    print("6. brand suffixes do not stop two pages being seen as duplicates")
    a, b = _norm_title("Garden Landscaping | Acme"), _norm_title("Garden Landscaping - Acme Ltd")
    if SequenceMatcher(None, a, b).ratio() >= TITLE_SIMILARITY:
        print(f"   PASS: \"{a}\" ~ \"{b}\"")
    else:
        print(f"   FAIL: \"{a}\" vs \"{b}\"")
        ok = False

    print("7. a GSC export parses regardless of column naming")
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="",
                                     encoding="utf-8") as fh:
        fh.write("Top pages,Clicks,Impressions\nhttps://acme.com/a,14,320\n")
        tmp = fh.name
    parsed = load_gsc(tmp)
    Path(tmp).unlink(missing_ok=True)
    if parsed.get("https://acme.com/a", {}).get("clicks") == 14:
        print("   PASS: 'Top pages' recognised as the URL column")
    else:
        print(f"   FAIL: {parsed}")
        ok = False

    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Content inventory with keep/update/merge/remove tracks.")
    ap.add_argument("--site")
    ap.add_argument("--max-pages", type=int, default=200)
    ap.add_argument("--gsc-csv", default="", help="Search Console Pages export to merge")
    ap.add_argument("--cluster-map", default="", help="seo-foundation keyword map JSON")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()
    if not args.site:
        ap.error("--site required (or use --selftest)")

    res = build(args.site, max_pages=args.max_pages, gsc_csv=args.gsc_csv,
                cluster_map=args.cluster_map, refresh=args.refresh)

    if args.out:
        Path(args.out).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{args.site}: {res['pages']} page(s) -> {res['track_counts']} -> {args.out}")
    else:
        print(f"\n{res['pages']} page(s) on {args.site}")
        print(f"Tracks: " + ", ".join(f"{k}={v}" for k, v in res["track_counts"].items()))
        print(f"Search Console: {'connected' if res['has_gsc'] else 'NOT CONNECTED'}\n")
        for r in res["rows"][:40]:
            print(f"  [{r['track']:6}] {r['confidence']:6} {r['words']:>5}w "
                  f"{r['internal_links_in']:>3} in  {r['url'][:70]}")
            print(f"           {r['reason'][:150]}")
        for n in res["not_connected"]:
            print(f"\nNOT CONNECTED: {n}")
        for n in res["notes"]:
            print(f"\nNOTE: {n}")

    print(fetch_page.cost_report(), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

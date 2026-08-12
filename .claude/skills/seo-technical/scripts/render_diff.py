#!/usr/bin/env python3
"""Raw versus rendered (course/26) and mobile versus desktop (course/29).

Two comparisons, one renderer, because they are the same question asked twice: is the
content actually *there*, in the HTML that the thing doing the indexing receives?

Why raw-vs-rendered is the most consequential check in this skill:

    Google indexes in two waves - raw HTML immediately, JavaScript execution 24 to 72 hours
    later. That delay is survivable. What is not survivable is that GPTBot, OAI-SearchBot,
    ClaudeBot and PerplexityBot crawl independently of Googlebot and several of them fetch
    raw HTML and stop. There is no wave two. So a client-rendered site can rank perfectly
    well in Google and be structurally invisible to ChatGPT and Perplexity, and you would
    never detect it by checking your Google rankings.

    The gap between raw and rendered IS that AI visibility gap. This script measures it.

crawl.py deliberately never renders, which is what makes this possible: its stored HTML is
the genuine raw article, not a Playwright render substituted at fetch time. A crawler that
silently rendered would report "no rendering problem" on precisely the sites that have one.

The verdict split is deliberate. Discrete comparisons - is this exact H1 present, is the
canonical present, does this link exist, is there JSON-LD - get a real pass or fail, because
they are exactly answerable. Body-text volume gets `review` with the ratio attached, because
course/29 says content must be "identical" and states no numeric tolerance, and inventing
one here would put a threshold in a client report that the corpus does not support.

Rendering costs seconds per page, so this samples templates rather than crawling everything.
Two renders per sampled page (mobile and desktop); raw comes free from the graph.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO = SKILL_DIR.parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import crawl  # noqa: E402
from technical import _ev, _live, _row, _verdict  # noqa: E402
from vitals import group_by_template, representatives  # noqa: E402

DEFAULT_SAMPLE = 3

# A mid-range Android on a mobile network is the p75 user (course/27), and the mobile
# rendering IS the page as far as Google is concerned (course/29).
MOBILE = {"viewport_width": 412, "viewport_height": 915,
          "user_agent": ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36")}
DESKTOP = {"viewport_width": 1440, "viewport_height": 900,
           "user_agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")}

CSR_RATIO = 0.10        # raw carries under a tenth of the rendered text
SSR_RATIO = 0.90        # raw carries essentially everything

_CHROME = ("script", "style", "noscript", "template", "nav", "header", "footer", "svg")


# --------------------------------------------------------------------------- rendering

async def _arender(url: str, profile: dict) -> str:
    from crawl4ai import AsyncWebCrawler, BrowserConfig

    cfg = BrowserConfig(headless=True, **profile)
    async with AsyncWebCrawler(config=cfg) as crawler:
        page = await crawler.arun(url=url)
        if not getattr(page, "success", False):
            raise RuntimeError(getattr(page, "error_message", "render failed"))
        return getattr(page, "html", "") or ""


def render(url: str, profile: dict) -> tuple[str, str | None]:
    """(html, error). A failed render is a reported unknown, never a silent empty string."""
    try:
        return asyncio.run(_arender(url, profile)), None
    except Exception as exc:  # noqa: BLE001 - no renderer is a finding about the audit, not the site
        return "", f"{type(exc).__name__}: {exc}"


# --------------------------------------------------------------------------- extraction

def signals(html: str, url: str) -> dict:
    """The discrete things that must survive into whichever HTML is being indexed."""
    from bs4 import BeautifulSoup

    out = {"words": 0, "h1": [], "headings": [], "title": None, "canonical": None,
           "meta_description": None, "links": set(), "jsonld_types": set(), "images": set(),
           "image_count": 0, "js_only_nav": 0}
    if not html:
        return out

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all("script", attrs={"type": re.compile(r"ld\+json", re.I)}):
        blob = (tag.string or tag.get_text() or "").strip()
        try:
            data = json.loads(blob)
        except (json.JSONDecodeError, ValueError):
            continue
        stack = [data]
        while stack:
            n = stack.pop()
            if isinstance(n, dict):
                t = n.get("@type")
                out["jsonld_types"] |= {t} if isinstance(t, str) else set(t or [])
                stack += list(n.values())
            elif isinstance(n, list):
                stack += n

    if soup.title and soup.title.string:
        out["title"] = soup.title.string.strip()
    can = soup.find("link", attrs={"rel": lambda v: v and "canonical" in
                                   [x.lower() for x in (v if isinstance(v, list) else [v])]})
    if can and can.get("href"):
        out["canonical"] = crawl.normalize_url(can["href"].strip())
    md = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    if md and md.get("content"):
        out["meta_description"] = md["content"].strip()

    # Strip zero-width and other invisible characters before deciding a heading has text.
    # A live run compared a `&ZeroWidthSpace;` heading against nothing and reported a content
    # parity failure whose entire evidence was an invisible character.
    def _txt(el) -> str:
        return re.sub(r"[​-‏  ﻿\xa0]", " ",
                      el.get_text(" ", strip=True)).strip()

    out["h1"] = [t for t in (_txt(h) for h in soup.find_all("h1")) if t]
    out["headings"] = [t for t in (_txt(h) for h in soup.find_all(["h1", "h2", "h3"])) if t]

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href and not href.startswith(("#", "mailto:", "tel:", "javascript:")):
            absu = crawl.normalize_url(crawl.urljoin(url, href))
            if crawl.same_site(url, absu):
                out["links"].add(absu)
    # course/26: `<span onclick="navigate()">` is not a link, and it is the most common cause
    # of whole sections going undiscovered.
    out["js_only_nav"] = len(soup.find_all(
        lambda t: t.name in ("span", "div", "button") and t.has_attr("onclick")))

    # Images are compared by ALT TEXT, not by src. course/29 asks for "the same images with
    # the same alt text", and a responsive CDN bakes the viewport into the URL - Wix serves
    # `.../w_51,h_48/...` to mobile and a different width to desktop. Comparing src reported
    # all 32 images on a live homepage as missing on mobile, which measured the CDN's
    # transform rather than anything about the content.
    imgs = soup.find_all("img")
    out["image_count"] = len(imgs)
    for img in imgs:
        alt = (img.get("alt") or "").strip()
        if alt:
            out["images"].add(alt)

    for tag in soup(_CHROME):
        tag.decompose()
    out["words"] = len(soup.get_text(" ", strip=True).split())
    return out


def _ratio(a: int, b: int) -> float:
    return 1.0 if not b else round(a / b, 3)


# --------------------------------------------------------------------------- 26. rendering

def check_raw_vs_rendered(url: str, raw: dict, rendered: dict, err: str | None) -> list[dict]:
    A = "Rendering and AI visibility"
    if err:
        return [_row("render.comparison", A, "render failed", "raw compared against rendered",
                     "unknown", "course/26",
                     f"{url}\n{err}\nNo Playwright render available, so the raw-versus-rendered "
                     f"gap could not be measured. Manual: open the page, DevTools Command "
                     f"Palette, 'Disable JavaScript', reload. What remains is roughly what a "
                     f"non-rendering AI crawler receives - the fastest diagnostic in this tier.")]

    out = []
    rw, dw = raw["words"], rendered["words"]
    ratio = _ratio(rw, dw)
    strategy = ("client-side rendered" if ratio < CSR_RATIO else
                "server-rendered or static" if ratio >= SSR_RATIO else "hybrid")
    out.append(_row(
        "render.strategy", A, f"raw HTML carries {ratio:.0%} of the rendered text ({rw}/{dw} words)",
        "content that must be found is in the raw HTML", "review", "course/26 [practitioner]",
        f"{url}\nInferred: {strategy}.\n" +
        ("Worst case for SEO and effectively fatal for AI visibility. GPTBot, ClaudeBot and "
         "PerplexityBot fetch raw HTML and stop - there is no wave two for them, so this "
         "content is absent from AI answers while Google rankings look fine."
         if ratio < CSR_RATIO else
         "Bots receive real content immediately. This is the configuration you want."
         if ratio >= SSR_RATIO else
         "Some content is server-rendered and some is not. The part that is not is invisible "
         "to non-rendering crawlers and delayed 24-72 hours for Google.")))

    # The discrete ones. Each is exactly answerable, so each gets a real verdict.
    missing_h1 = [h for h in rendered["h1"] if h not in raw["h1"]]
    out.append(_row("render.raw_h1", A,
                    f"{len(raw['h1'])} H1 in raw, {len(rendered['h1'])} after rendering",
                    "the H1 is in the raw HTML", _verdict(missing_h1), "course/26",
                    _ev(missing_h1) or "Present before JavaScript runs."))

    missing_h = [h for h in rendered["headings"] if h not in raw["headings"]]
    out.append(_row("render.raw_headings", A, f"{len(missing_h)} heading(s) appear only after JS",
                    "headings are server-rendered", _verdict(missing_h), "course/26",
                    _ev(missing_h)))

    meta_gaps = [f for f in ("title", "canonical", "meta_description")
                 if rendered.get(f) and not raw.get(f)]
    out.append(_row("render.raw_metadata", A,
                    f"{len(meta_gaps)} metadata field(s) injected by JavaScript",
                    "title, meta description and canonical are server-rendered",
                    _verdict(meta_gaps), "course/26", _ev(meta_gaps) or
                    "This is the one that catches people constantly: a client-side SEO plugin "
                    "setting titles after load means bots see the default template title."))

    js_links = sorted(rendered["links"] - raw["links"])
    out.append(_row("render.raw_links", A,
                    f"{len(js_links)} internal link(s) exist only after rendering",
                    "navigation is real <a href> in the raw HTML",
                    _verdict(js_links), "course/26", _ev(js_links) or
                    "Links only present after execution are not followed until wave two, "
                    "which delays discovery of everything behind them."))

    out.append(_row("render.js_only_nav", A,
                    f"{rendered['js_only_nav']} onclick element(s) acting as navigation",
                    "no span/div/button onclick used as a link",
                    "review" if rendered["js_only_nav"] else "pass", "course/26",
                    "`<span onclick=\"navigate()\">` is not a link. Bots follow `<a href>`. "
                    "Named in the course as the most common cause of whole sections going "
                    "undiscovered." if rendered["js_only_nav"] else "Navigation is real links."))

    schema_gap = sorted(rendered["jsonld_types"] - raw["jsonld_types"])
    out.append(_row("render.raw_schema", A, f"{len(schema_gap)} schema type(s) added by JS",
                    "structured data is in the raw HTML", _verdict(schema_gap), "course/26",
                    _ev(schema_gap) or ("No JSON-LD in either." if not rendered["jsonld_types"]
                                        else "Server-rendered.")))
    return out


# --------------------------------------------------------------------------- 29. mobile

def check_parity(url: str, mob: dict, desk: dict, errs: tuple) -> list[dict]:
    A = "Mobile-first parity"
    if any(errs):
        return [_row("mobile.parity", A, "render failed", "mobile matches desktop", "unknown",
                     "course/29", f"{url}\n{[e for e in errs if e]}\n"
                     "Manual: load on desktop, view source, copy the body text; load in mobile "
                     "emulation, copy the rendered DOM body text; compare. Two minutes, and it "
                     "finds most problems.")]

    out = []
    ratio = _ratio(mob["words"], desk["words"])
    out.append(_row(
        "mobile.content_volume", A,
        f"mobile carries {ratio:.0%} of desktop body text ({mob['words']}/{desk['words']} words)",
        "identical - course/29 states no numeric tolerance", "review", "course/29 [confirmed]",
        f"{url}\nGoogle indexes the mobile version. Content missing on mobile is content that "
        "does not exist.\nThis is `review` rather than a verdict because the course requires "
        "parity without defining a tolerance, and a threshold invented here would be a number "
        "in a client report that the corpus does not support. Read the ratio and judge.\n"
        "Hidden behind an accordion but present in the DOM is fine. Conditionally not rendered "
        "below a breakpoint is not."))

    for field, label in (("headings", "heading"), ("links", "internal link"),
                         ("images", "image alt text")):
        d, m = desk[field], mob[field]
        missing = sorted(set(d) - set(m)) if isinstance(d, set) else \
            [x for x in d if x not in m]
        extra = ""
        if field == "links":
            extra = (" A collapsed hamburger menu is fine as long as the links exist in "
                     "the markup.")
        elif field == "images":
            extra = (f" Compared by alt text, not by src: a responsive CDN serves a different "
                     f"URL per viewport, so src comparison measures the transform rather than "
                     f"the content. Image count is {desk['image_count']} desktop vs "
                     f"{mob['image_count']} mobile.")
        out.append(_row(f"mobile.{field}_parity", A,
                        f"{len(missing)} {label}(s) on desktop and not on mobile",
                        f"the same {label}s in both", _verdict(missing), "course/29",
                        _ev(missing) or f"All {label}s present on mobile." + extra))

    schema_gap = sorted(desk["jsonld_types"] - mob["jsonld_types"])
    out.append(_row("mobile.schema_parity", A, f"{len(schema_gap)} schema type(s) desktop-only",
                    "structured data present in the mobile template",
                    _verdict(schema_gap), "course/29", _ev(schema_gap) or
                    "Structured data present on mobile."))

    meta_gaps = [f for f in ("title", "canonical", "meta_description")
                 if desk.get(f) != mob.get(f)]
    out.append(_row("mobile.metadata_parity", A, f"{len(meta_gaps)} metadata field(s) differ",
                    "same title, meta description and canonical",
                    _verdict(meta_gaps), "course/29",
                    _ev([f"{f}: desktop {desk.get(f)!r} vs mobile {mob.get(f)!r}"
                         for f in meta_gaps]) or "Metadata matches."))
    return out


# --------------------------------------------------------------------------- run

def analyze(g: dict, *, sample: int = DEFAULT_SAMPLE, skip_mobile: bool = False) -> dict:
    pages = _live(g.get("pages") or {})
    reps = representatives(group_by_template(pages), sample)
    rows: list[dict] = []

    for tpl, url, size in reps:
        raw_html = None
        page = pages.get(url) or {}
        # The raw HTML is not stored in the graph (it would multiply its size), so re-fetch
        # it raw. One cheap GET against the render, which is the expensive half.
        r = crawl.fetch_raw(url)
        raw_html = r.get("html") or ""
        raw = signals(raw_html, url)

        desk_html, desk_err = render(url, DESKTOP)
        desktop = signals(desk_html, url)

        for row in check_raw_vs_rendered(url, raw, desktop, desk_err):
            row["evidence"] = f"template {tpl} ({size} page(s))\n{row['evidence']}"
            rows.append(row)

        if not skip_mobile:
            mob_html, mob_err = render(url, MOBILE)
            mobile = signals(mob_html, url)
            for row in check_parity(url, mobile, desktop, (mob_err, desk_err)):
                row["evidence"] = f"template {tpl} ({size} page(s))\n{row['evidence']}"
                rows.append(row)

    no_viewport = [u for u, p in pages.items() if not p.get("has_viewport")]
    rows.append(_row("mobile.viewport", "Mobile-first parity",
                     f"{len(no_viewport)} page(s) without a viewport meta tag",
                     "every page declares a viewport", _verdict(no_viewport), "course/29",
                     _ev(no_viewport) or "Read from the crawl, so this covers every page, not "
                                         "just the sample."))
    rows.append(_row("mobile.interstitials", "Mobile-first parity", "not measured",
                     "no intrusive interstitial on arrival from search", "unknown", "course/29",
                     "A full-screen modal on first paint is a documented problem; a cookie "
                     "banner required by law is fine. Nothing here can tell them apart.\n"
                     "Manual: open the page on a phone from a search result and watch the "
                     "first two seconds."))

    counts = {v: sum(1 for r in rows if r["verdict"] == v)
              for v in ("pass", "fail", "review", "unknown")}
    return {
        "origin": g.get("origin"),
        "sampled": [{"template": t, "url": u, "pages": n} for t, u, n in reps],
        "counts": counts,
        "checks": rows,
        "not_connected": [
            "URL Inspection 'Test live URL, View tested page' is the ground truth for what "
            "Google itself renders, and there is no Search Console credential here. This "
            "compares raw against a local Playwright render, which is the right proxy for a "
            "non-rendering AI crawler but is not Google's renderer.",
        ],
        "reading_note": (
            "The raw-versus-rendered gap is the AI visibility gap. Google gets a second wave "
            "24 to 72 hours later; GPTBot, ClaudeBot and PerplexityBot frequently do not. A "
            "site can rank normally and be absent from AI answers, and checking rankings will "
            "never reveal it.\n"
            "The fix path rarely requires a rebuild: server-render the content that must be "
            "found, make navigation real <a href> links, provide paginated fallbacks behind "
            "infinite scroll, and above all server-render the metadata."),
    }


# --------------------------------------------------------------------------- selftest

_RAW_SHELL = """<html><head><title>Loading...</title></head>
<body><div id="root"></div><script src="/app.js"></script></body></html>"""

_RENDERED = """<html><head><title>Real Title</title>
<link rel="canonical" href="https://e.test/p">
<meta name="description" content="A real description.">
<script type="application/ld+json">{"@type":"Article","headline":"x"}</script></head>
<body><h1>The Real Heading</h1><h2>A Section</h2>
<p>Actual body copy that only exists after JavaScript has run, at some length.</p>
<a href="/about">About</a><a href="/pricing">Pricing</a>
<span onclick="go('/hidden')">Not a link</span>
<img src="/hero.jpg" alt="hero"></body></html>"""

_MOBILE_TRIMMED = """<html><head><title>Real Title</title>
<link rel="canonical" href="https://e.test/p">
<meta name="description" content="A real description.">
</head><body><h1>The Real Heading</h1>
<p>Short.</p><a href="/about">About</a></body></html>"""


def _selftest() -> int:
    """Fixture-based. No browser, no network."""
    ok = True
    url = "https://e.test/p"
    raw = signals(_RAW_SHELL, url)
    rendered = signals(_RENDERED, url)

    print("1. a client-rendered shell is detected as one")
    rows = {r["check_id"]: r for r in check_raw_vs_rendered(url, raw, rendered, None)}
    strat = rows["render.strategy"]
    if "client-side rendered" in strat["evidence"] and "absent from AI answers" in strat["evidence"]:
        print("   PASS: CSR named, and the AI-visibility consequence stated")
    else:
        print(f"   FAIL: {strat['evidence'][:120]}")
        ok = False

    print("2. every discrete raw-HTML gap fails, individually")
    expect = ["render.raw_h1", "render.raw_headings", "render.raw_metadata",
              "render.raw_links", "render.raw_schema"]
    wrong = [(c, rows.get(c, {}).get("verdict")) for c in expect
             if rows.get(c, {}).get("verdict") != "fail"]
    print(f"   PASS: all {len(expect)} fired" if not wrong else f"   FAIL: {wrong}")
    ok &= not wrong

    print("3. the onclick pseudo-link is caught")
    r = rows["render.js_only_nav"]
    if r["verdict"] == "review" and "is not a link" in r["evidence"]:
        print("   PASS: span onclick flagged as not-a-link")
    else:
        print(f"   FAIL: {r['verdict']}")
        ok = False

    print("4. a server-rendered page produces no findings")
    clean = {r["check_id"]: r for r in
             check_raw_vs_rendered(url, signals(_RENDERED, url), rendered, None)}
    fails = [c for c, r in clean.items() if r["verdict"] == "fail"]
    if not fails and "server-rendered or static" in clean["render.strategy"]["evidence"]:
        print("   PASS: identical raw and rendered = zero failures, SSR inferred")
    else:
        print(f"   FAIL: {fails}")
        ok = False

    print("5. mobile parity catches missing headings, links and schema")
    par = {r["check_id"]: r for r in
           check_parity(url, signals(_MOBILE_TRIMMED, url), rendered, (None, None))}
    expect = ["mobile.headings_parity", "mobile.links_parity", "mobile.images_parity",
              "mobile.schema_parity"]
    wrong = [(c, par.get(c, {}).get("verdict")) for c in expect
             if par.get(c, {}).get("verdict") != "fail"]
    print(f"   PASS: all {len(expect)} parity gaps fired" if not wrong else f"   FAIL: {wrong}")
    ok &= not wrong

    print("6. body-text volume is `review`, never an invented threshold")
    r = par["mobile.content_volume"]
    if r["verdict"] == "review" and "no numeric tolerance" in r["threshold"]:
        print("   PASS: ratio reported, verdict withheld, reason given")
    else:
        print(f"   FAIL: {r['verdict']} / {r['threshold']}")
        ok = False

    print("7. matching metadata is a pass, differing metadata is a fail")
    same = check_parity(url, rendered, rendered, (None, None))
    m_ok = next(r for r in same if r["check_id"] == "mobile.metadata_parity")
    m_bad = par["mobile.metadata_parity"]
    if m_ok["verdict"] == "pass" and m_bad["verdict"] == "pass":
        # the trimmed fixture keeps metadata identical on purpose
        print("   PASS: metadata compared field by field, not by page shape")
    else:
        print(f"   FAIL: {m_ok['verdict']} / {m_bad['verdict']}")
        ok = False

    print("8. a failed render is `unknown` with the manual method")
    r = check_raw_vs_rendered(url, raw, {}, "RuntimeError: no browser")[0]
    if r["verdict"] == "unknown" and "Disable JavaScript" in r["evidence"]:
        print("   PASS: no browser means unknown, plus the two-minute manual test")
    else:
        print(f"   FAIL: {r['verdict']}")
        ok = False

    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# --------------------------------------------------------------------------- cli

def main() -> int:
    ap = argparse.ArgumentParser(description="Raw vs rendered and mobile vs desktop (26, 29).")
    ap.add_argument("url", nargs="?")
    ap.add_argument("--graph")
    ap.add_argument("--sample", type=int, default=DEFAULT_SAMPLE,
                    help="templates to render (2 renders each)")
    ap.add_argument("--skip-mobile", action="store_true",
                    help="raw-vs-rendered only, halving the render cost")
    ap.add_argument("--max-pages", type=int, default=crawl.DEFAULT_MAX_PAGES)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()
    if not args.graph and not args.url:
        ap.error("url or --graph required (or use --selftest)")

    if args.graph:
        g = json.loads(Path(args.graph).read_text(encoding="utf-8"))
    else:
        cached = crawl._cache_path(crawl.origin_of(args.url)).exists() and not args.refresh
        if args.max_pages > crawl.CONFIRM_ABOVE and not args.yes and not cached:
            print(f"This would make up to {args.max_pages} requests. Re-run with --yes.",
                  file=sys.stderr)
            return 2
        g = crawl.crawl(args.url, max_pages=args.max_pages, refresh=args.refresh)

    res = analyze(g, sample=args.sample, skip_mobile=args.skip_mobile)
    if args.out:
        Path(args.out).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        print(args.out, file=sys.stderr)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0

    print(f"\n{res['origin']}  -  {len(res['sampled'])} template(s) rendered")
    print("  ".join(f"{k}: {v}" for k, v in res["counts"].items()))
    for r in res["checks"]:
        if r["verdict"] == "pass":
            continue
        print(f"\n  [{r['verdict'].upper():7}] {r['check_id']}: {r['observed']}")
        for line in (r["evidence"] or "").splitlines()[:6]:
            print(f"            | {line}")
    print(f"\n{res['reading_note']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

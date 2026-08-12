#!/usr/bin/env python3
"""Core Web Vitals and page-speed opportunities, sampled by template (course/27, course/28).

Built on seo-onpage's `lighthouse.py` rather than a second PageSpeed client, because that
module already handles the key, the cache, the .env typo and the response shape. This one
adds the three things it does not do, all of which come straight out of course/27:

1. **Template sampling.** "Search Console groups URLs by similar behaviour, so a failure
   usually indicates a template problem rather than a page problem. Fixing one blog post
   fixes nothing." Named as the most useful feature of the report and the most commonly
   missed. So this groups the crawl by URL shape, picks one representative per group, and
   tests those - which is also why a 300-page site costs five API calls instead of 300.

2. **Field data first, with the origin fallback.** Google ranks on CrUX, not Lighthouse, and
   a page can score 100 in the lab and fail the field assessment. When a single URL has too
   little traffic to report, the origin-level CrUX block answers for the property. A lab
   number is never presented as what users experience.

3. **course/28's fix list, in payoff order**, mapped onto the Lighthouse audits that
   actually detect each one - with the TTFB gate first, because over ~800ms no front-end
   work compensates.

The floor framing is enforced, not left to the reader: a metric that passes reports "floor
met, stop" and never becomes a finding. Going from 2.4s to 1.1s is real engineering with no
ranking return, and telling a client already passing to optimize further is telling them to
spend money for nothing. The conversion case studies (Rakuten, Vodafone, Deloitte) are real
and are about revenue - this script labels that as a separate argument rather than blending
it into a ranking claim.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO = SKILL_DIR.parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO / ".claude" / "skills" / "seo-onpage" / "scripts"))

import crawl  # noqa: E402
import lighthouse  # noqa: E402  - seo-onpage's PSI client, reused rather than reimplemented
from technical import _ev, _live, _row  # noqa: E402

# course/27 [confirmed]. p75 of real Chrome visits over a rolling 28-day window, all three
# passing simultaneously.
THRESHOLDS = {
    "LARGEST_CONTENTFUL_PAINT_MS": (2500, 4000, "LCP", "ms", 1),
    "INTERACTION_TO_NEXT_PAINT": (200, 500, "INP", "ms", 1),
    "CUMULATIVE_LAYOUT_SHIFT_SCORE": (0.1, 0.25, "CLS", "", 100),  # CrUX reports CLS x100
}
TTFB_GATE_MS = 800          # course/28: over this, fix it before anything else
INP_DROP_RISK = 500         # course/27 [practitioner]: 2-4 position drops, March 2026 update
DEFAULT_TEMPLATES = 5

# course/28's priority order, mapped to the Lighthouse audit that detects each. The order is
# the payoff order in the course, not Lighthouse's own savings estimate.
OPPORTUNITIES = [
    ("server-response-time", "LCP", "TTFB over ~800ms gates everything after it. Fix caching, "
     "CDN and hosting before any front-end work - nothing compensates."),
    ("largest-contentful-paint-element", "LCP", "Identify the LCP element before optimizing "
     "anything. PSI names it; do not guess."),
    ("uses-optimized-images", "LCP", "Compress the LCP element: under 150KB, WebP or AVIF, "
     "sized to display. This alone fixes many failing pages."),
    ("prioritize-lcp-image", "LCP", "Do not lazy-load the LCP element - it delays the exact "
     "thing being measured. loading=eager, fetchpriority=high, and preload it."),
    ("render-blocking-resources", "LCP", "Inline critical CSS, defer the rest, add defer or "
     "async to scripts."),
    ("redirects", "LCP", "Each redirect hop adds 100-500ms before the page starts loading."),
    ("font-display", "LCP/CLS", "font-display: swap prevents invisible text; matching fallback "
     "metrics prevents the swap shift."),
    ("third-party-summary", "INP", "Chat widgets, analytics, heat maps and tag managers are "
     "somebody else's JavaScript on your main thread. For each, ask who reads the data."),
    ("total-blocking-time", "INP", "Any task over 50ms blocks the main thread. Split heavy work "
     "with scheduler.yield() or setTimeout."),
    ("unused-javascript", "INP", "The most effective and least popular fix. Every kilobyte is "
     "parsed, compiled and executed."),
    ("unsized-images", "CLS", "Width and height on every image and video prevents an entire "
     "category of CLS failure."),
    ("layout-shifts", "CLS", "Reserve space for ads, embeds and iframes; never insert content "
     "above existing content; animate transform, not layout properties."),
]

_ID_SEGMENT = re.compile(r"^(\d+|[0-9a-f]{8,}|.*-\d{4,}|p\d+)$", re.I)


# --------------------------------------------------------------------------- templates

def template_of(url: str) -> str:
    """The URL's shape, which is the unit a Core Web Vitals failure actually lives in.

    /blog/how-to-x and /blog/why-y are one template and one fix. Collapsing the leaf segment
    is a heuristic, not a Search Console grouping, and it is labelled as one wherever it is
    reported - but it is the right unit, and testing every page instead would cost 300 API
    calls to learn the same five answers.
    """
    p = urlparse(url)
    segs = [s for s in p.path.split("/") if s]
    if not segs:
        return "/ (homepage)"
    if len(segs) == 1:
        return f"/{segs[0]}" if not _ID_SEGMENT.match(segs[0]) else "/*"
    return "/" + "/".join(segs[:-1]) + "/*"


def group_by_template(pages: dict) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for u, p in pages.items():
        if p.get("status") == 200 and p.get("indexable"):
            groups[template_of(u)].append(u)
    return dict(groups)


def representatives(groups: dict[str, list[str]], limit: int) -> list[tuple[str, str, int]]:
    """(template, representative URL, group size), biggest groups first.

    Biggest first because a template covering 80 URLs is 80 fixes for the price of one, and
    a cap has to spend its calls somewhere.
    """
    out = []
    for tpl, urls in groups.items():
        out.append((tpl, sorted(urls, key=lambda u: (len(u), u))[0], len(urls)))
    out.sort(key=lambda t: (-t[2], t[0]))
    return out[:limit]


# --------------------------------------------------------------------------- field data

def read_field(block: dict | None) -> dict:
    """CrUX metrics normalised to real units with a verdict per metric."""
    out = {}
    for key, (good, poor, name, unit, divisor) in THRESHOLDS.items():
        m = (block or {}).get(key)
        if not m or m.get("percentile") is None:
            out[name] = {"value": None, "verdict": "unknown", "good": good, "unit": unit}
            continue
        val = m["percentile"] / divisor
        out[name] = {
            "value": round(val, 3), "good": good, "poor": poor, "unit": unit,
            "category": m.get("category"),
            "verdict": "pass" if val <= good else "fail",
        }
    return out


def _fmt(name: str, m: dict) -> str:
    if m["value"] is None:
        return f"{name} not reported"
    return f"{name} {m['value']}{m['unit']} (good <= {m['good']}{m['unit']})"


# --------------------------------------------------------------------------- checks

def check_template(tpl: str, url: str, size: int, res: dict) -> list[dict]:
    A = "Core Web Vitals"
    out: list[dict] = []
    scope = f"{tpl} ({size} page(s)), sampled at {url}"

    if res.get("error"):
        return [_row(f"cwv.{tpl}", A, "PageSpeed Insights failed", "field data for the template",
                     "unknown", "course/27", f"{scope}\n{res['error']}")]

    url_field = read_field(res.get("core_web_vitals_field"))
    origin_field = read_field(res.get("core_web_vitals_field_origin"))
    have_url = any(m["value"] is not None for m in url_field.values())
    have_origin = any(m["value"] is not None for m in origin_field.values())
    field = url_field if have_url else origin_field
    source = ("this URL's real users" if have_url else
              "origin-level CrUX (this URL has too little traffic to report on its own)"
              if have_origin else None)

    if source is None:
        lab = res.get("core_web_vitals_lab") or {}
        lab_lcp = (lab.get("largest-contentful-paint") or {}).get("display")
        out.append(_row(
            f"cwv.{tpl}", A, "no field data at URL or origin level",
            "LCP <= 2.5s, INP <= 200ms, CLS <= 0.1 at p75", "unknown", "course/27 [confirmed]",
            f"{scope}\nThis origin has too little real Chrome traffic to appear in CrUX, so "
            f"there is no field data and therefore no assessment. Google ranks on field data "
            f"only.\nLab (a single throttled simulation, NOT what users experience): "
            f"LCP {lab_lcp}.\nUse the lab numbers to iterate; they cannot tell you whether "
            f"the template passes."))
        return out + check_opportunities(tpl, url, res)

    failing = [n for n, m in field.items() if m["verdict"] == "fail"]
    unknown = [n for n, m in field.items() if m["verdict"] == "unknown"]
    detail = "\n".join(_fmt(n, m) for n, m in field.items())

    if failing:
        verdict = "fail"
        note = (f"All three must pass simultaneously. Failing: {', '.join(failing)}.\n"
                "This is a template, so one fix resolves every page in the group.")
    elif unknown:
        verdict = "review"
        note = (f"Not reported: {', '.join(unknown)}. The rest are within the floor. A metric "
                "with too few samples is not a passing metric.")
    else:
        verdict = "pass"
        note = ("Floor met on all three. Stop here - Core Web Vitals are a floor, not a lever, "
                "and optimizing past good is engineering effort with no ranking return.")

    out.append(_row(f"cwv.{tpl}", A, ", ".join(_fmt(n, m) for n, m in field.items()),
                    "LCP <= 2.5s, INP <= 200ms, CLS <= 0.1, all at p75 over 28 days",
                    verdict, "course/27 [confirmed]",
                    f"{scope}\nSource: {source}\n{detail}\n{note}"))

    inp = field.get("INP", {})
    if inp.get("value") is not None and inp["value"] > INP_DROP_RISK:
        out.append(_row(f"cwv.{tpl}.inp_risk", A, f"INP {inp['value']}ms",
                        f"under {INP_DROP_RISK}ms", "fail", "course/27 [practitioner]",
                        f"{scope}\nSites with INP above {INP_DROP_RISK}ms saw 2 to 4 position "
                        "drops in the March 2026 core update. INP measures the worst "
                        "interaction latency across the whole visit, which is why sites that "
                        "comfortably passed FID now fail."))

    if verdict == "fail":
        out += check_opportunities(tpl, url, res)
    return out


def check_opportunities(tpl: str, url: str, res: dict) -> list[dict]:
    """course/28's ordered fix list, filtered to what Lighthouse actually found here."""
    A = "Page speed engineering"
    audits = res.get("perf_audits") or {}
    out: list[dict] = []
    hits = []
    for aid, metric, advice in OPPORTUNITIES:
        a = audits.get(aid)
        if not a:
            continue
        score = a.get("score")
        if score is not None and score >= 0.9:
            continue
        hits.append(f"[{metric}] {a.get('title') or aid}: {a.get('displayValue') or ''}\n"
                    f"        {advice}")

    ttfb = audits.get("server-response-time") or {}
    ttfb_ms = ttfb.get("numericValue")
    if ttfb_ms is not None:
        out.append(_row(f"speed.{tpl}.ttfb", A, f"TTFB {round(ttfb_ms)}ms",
                        f"under {TTFB_GATE_MS}ms",
                        "fail" if ttfb_ms > TTFB_GATE_MS else "pass", "course/28",
                        f"Sampled at {url}\n" +
                        ("Over the gate. Fix caching, CDN and hosting first - no front-end work "
                         "compensates for a slow server." if ttfb_ms > TTFB_GATE_MS else
                         "Under the gate, so the bottleneck is front-end, not the server.")))

    lcp_el = res.get("lcp_element")
    if lcp_el:
        out.append(_row(f"speed.{tpl}.lcp_element", A, "identified",
                        "know the element before optimizing it", "review", "course/28",
                        f"Sampled at {url}\nLCP element: {lcp_el}\n"
                        "Usually the hero image. Compress to under 150KB in WebP or AVIF, size "
                        "it to display, set loading=eager and fetchpriority=high, and preload "
                        "it. That sequence fixes most failing LCP."))

    out.append(_row(f"speed.{tpl}.opportunities", A, f"{len(hits)} opportunity(ies)",
                    "in payoff order, not Lighthouse's savings order",
                    "review" if hits else "pass", "course/28",
                    _ev(hits, 8) if hits else
                    "Lighthouse found nothing on this template's ordered fix list."))
    return out


def analyze(g: dict, *, limit: int = DEFAULT_TEMPLATES, strategy: str = "mobile",
            refresh: bool = False) -> dict:
    pages = _live(g.get("pages") or {})
    groups = group_by_template(pages)
    reps = representatives(groups, limit)
    rows: list[dict] = []

    for tpl, url, size in reps:
        res = lighthouse.run(url, strategy=strategy, refresh=refresh)
        # seo-onpage's cache predates origin-level CrUX. One retry rather than silently
        # reporting "no field data" from a parse that never looked for it.
        if not res.get("error") and "core_web_vitals_field_origin" not in res:
            res = lighthouse.run(url, strategy=strategy, refresh=True)
        rows += check_template(tpl, url, size, res)

    counts = {v: sum(1 for r in rows if r["verdict"] == v)
              for v in ("pass", "fail", "review", "unknown")}
    return {
        "origin": g.get("origin"),
        "strategy": strategy,
        "templates_found": len(groups),
        "templates_tested": len(reps),
        "coverage": f"{sum(s for _, _, s in reps)} of {len(pages)} indexable page(s)",
        "counts": counts,
        "checks": rows,
        "not_connected": [
            "Search Console Core Web Vitals report: the authoritative field-data view, grouped "
            "by Google's own URL clustering. No credential exists here, so templates below are "
            "grouped by URL shape instead - a heuristic, not Google's grouping.",
        ],
        "reading_note": (
            "Judge on field data only. A template scoring 100 in the lab can fail the field "
            "assessment, because real users are on slower devices than the simulation assumes. "
            "Mobile is what drives ranking, so mobile is the default strategy here.\n"
            "Core Web Vitals are a tiebreaker between comparable pages, not a lever for weak "
            "content. Pass the floor and stop.\n"
            "CrUX is a rolling 28-day window, so a fix takes weeks to appear. Deploying an "
            "improvement and checking the next morning proves nothing.\n"
            "The conversion case studies (Rakuten +33% conversions, Vodafone +15% sales, "
            "Deloitte 8.4% per 100ms) measure revenue, not ranking. They are a strong business "
            "argument for speed and a weak ranking argument - say which one you are making."),
    }


# --------------------------------------------------------------------------- selftest

def _selftest() -> int:
    """Fixture-based. No PSI calls, so it costs nothing and runs offline."""
    ok = True

    print("1. template grouping collapses the leaf, not the whole path")
    cases = {
        "https://e.test/": "/ (homepage)",
        "https://e.test/about": "/about",
        "https://e.test/blog/how-to-x": "/blog/*",
        "https://e.test/blog/why-y": "/blog/*",
        "https://e.test/shop/shoes/red-runner": "/shop/shoes/*",
        "https://e.test/12345": "/*",
    }
    bad = {u: (template_of(u), want) for u, want in cases.items() if template_of(u) != want}
    print("   PASS: two blog posts share one template" if not bad else f"   FAIL: {bad}")
    ok &= not bad

    print("2. representatives picks the biggest group first and one URL each")
    groups = {"/blog/*": [f"https://e.test/blog/{i}" for i in range(80)],
              "/about": ["https://e.test/about"],
              "/services/*": ["https://e.test/services/a", "https://e.test/services/b"]}
    reps = representatives(groups, 2)
    if [r[0] for r in reps] == ["/blog/*", "/services/*"] and reps[0][2] == 80:
        print("   PASS: 80-page template tested first, /about dropped by the cap")
    else:
        print(f"   FAIL: {reps}")
        ok = False

    print("3. CLS is divided by 100, the others are not")
    field = read_field({"LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 3100, "category": "AVERAGE"},
                        "INTERACTION_TO_NEXT_PAINT": {"percentile": 180, "category": "FAST"},
                        "CUMULATIVE_LAYOUT_SHIFT_SCORE": {"percentile": 5, "category": "FAST"}})
    if field["CLS"]["value"] == 0.05 and field["LCP"]["value"] == 3100 and \
            field["INP"]["value"] == 180:
        print("   PASS: CLS 5 -> 0.05, LCP and INP left in ms")
    else:
        print(f"   FAIL: {[(k, v['value']) for k, v in field.items()]}")
        ok = False

    print("4. one failing metric fails the template; all three passing says stop")
    rows = check_template("/blog/*", "https://e.test/blog/x", 80, {
        "core_web_vitals_field": {"LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 3100},
                                  "INTERACTION_TO_NEXT_PAINT": {"percentile": 180},
                                  "CUMULATIVE_LAYOUT_SHIFT_SCORE": {"percentile": 5}},
        "core_web_vitals_field_origin": None, "perf_audits": {}})
    fail_row = rows[0]
    good = check_template("/ok", "https://e.test/ok", 1, {
        "core_web_vitals_field": {"LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 2000},
                                  "INTERACTION_TO_NEXT_PAINT": {"percentile": 100},
                                  "CUMULATIVE_LAYOUT_SHIFT_SCORE": {"percentile": 5}},
        "core_web_vitals_field_origin": None, "perf_audits": {}})[0]
    if fail_row["verdict"] == "fail" and "LCP" in fail_row["evidence"] and \
            good["verdict"] == "pass" and "Stop here" in good["evidence"]:
        print("   PASS: LCP 3100ms fails, and a passing template is told to stop")
    else:
        print(f"   FAIL: {fail_row['verdict']} / {good['verdict']}")
        ok = False

    print("5. no field data is `unknown`, never a lab verdict dressed as field data")
    rows = check_template("/x", "https://e.test/x", 1, {
        "core_web_vitals_field": None, "core_web_vitals_field_origin": None,
        "core_web_vitals_lab": {"largest-contentful-paint": {"display": "1.2 s"}}, "perf_audits": {}})
    r = rows[0]
    if r["verdict"] == "unknown" and "NOT what users experience" in r["evidence"]:
        print("   PASS: lab number shown, explicitly not treated as an assessment")
    else:
        print(f"   FAIL: {r['verdict']}")
        ok = False

    print("6. origin CrUX is used when the URL has none")
    r = check_template("/x", "https://e.test/x", 1, {
        "core_web_vitals_field": None,
        "core_web_vitals_field_origin": {"LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 2000},
                                         "INTERACTION_TO_NEXT_PAINT": {"percentile": 100},
                                         "CUMULATIVE_LAYOUT_SHIFT_SCORE": {"percentile": 8}},
        "perf_audits": {}})[0]
    if r["verdict"] == "pass" and "origin-level CrUX" in r["evidence"]:
        print("   PASS: fell back to origin data and said so")
    else:
        print(f"   FAIL: {r['verdict']} - {r['evidence'][:80]}")
        ok = False

    print("7. TTFB over the gate is its own finding, ahead of front-end work")
    rows = check_opportunities("/x", "https://e.test/x",
                               {"perf_audits": {"server-response-time":
                                            {"numericValue": 1400, "score": 0.2,
                                             "title": "Reduce initial server response time"}}})
    ttfb = next((r for r in rows if r["check_id"].endswith("ttfb")), None)
    if ttfb and ttfb["verdict"] == "fail" and "no front-end work compensates" in ttfb["evidence"]:
        print("   PASS: 1400ms TTFB fails and says fix it first")
    else:
        print(f"   FAIL: {ttfb}")
        ok = False

    print("8. INP above 500ms gets the core-update warning")
    rows = check_template("/x", "https://e.test/x", 1, {
        "core_web_vitals_field": {"LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 2000},
                                  "INTERACTION_TO_NEXT_PAINT": {"percentile": 700},
                                  "CUMULATIVE_LAYOUT_SHIFT_SCORE": {"percentile": 5}},
        "core_web_vitals_field_origin": None, "perf_audits": {}})
    risk = next((r for r in rows if r["check_id"].endswith("inp_risk")), None)
    if risk and "2 to 4 position drops" in risk["evidence"]:
        print("   PASS: the March 2026 finding is attached")
    else:
        print("   FAIL: no INP risk row")
        ok = False

    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# --------------------------------------------------------------------------- cli

def main() -> int:
    ap = argparse.ArgumentParser(description="Core Web Vitals by template (course/27-28).")
    ap.add_argument("url", nargs="?")
    ap.add_argument("--graph", help="a graph JSON written by crawl.py --out")
    ap.add_argument("--templates", type=int, default=DEFAULT_TEMPLATES,
                    help="how many templates to sample (one PSI call each)")
    ap.add_argument("--strategy", choices=["mobile", "desktop"], default="mobile")
    ap.add_argument("--max-pages", type=int, default=crawl.DEFAULT_MAX_PAGES)
    ap.add_argument("--refresh", action="store_true", help="bypass both caches")
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

    res = analyze(g, limit=args.templates, strategy=args.strategy, refresh=args.refresh)
    if args.out:
        Path(args.out).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        print(args.out, file=sys.stderr)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0

    print(f"\n{res['origin']}  -  {res['templates_tested']} of {res['templates_found']} "
          f"template(s) tested on {res['strategy']}, covering {res['coverage']}")
    print("  ".join(f"{k}: {v}" for k, v in res["counts"].items()))
    for r in res["checks"]:
        print(f"\n  [{r['verdict'].upper():7}] {r['check_id']}: {r['observed']}")
        for line in (r["evidence"] or "").splitlines()[:8]:
            print(f"            | {line}")
    print(f"\n{res['reading_note']}")
    print(f"\n{lighthouse.cost_report()}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

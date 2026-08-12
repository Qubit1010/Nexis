#!/usr/bin/env python3
"""PageSpeed Insights, asking for the SEO and accessibility categories, not just performance.

This is the highest-leverage free measurement available to this skill and nothing in the
repo was using it. `website-audit-system/scripts/pagespeed.py` requests
`category=performance` only, so the Lighthouse **seo** category - about 14 audits Google
runs for you at no cost - has been sitting unclaimed. Several of them (crawlable anchors,
is-crawlable, hreflang, viewport, font size, structured-data validity) are things this
skill would otherwise have to approximate badly from HTML.

Two framings this module enforces rather than leaving to the reader:

1. **Core Web Vitals are a floor, not a lever.** Failing hurts; exceeding buys nothing.
   Going from 2.4s to 1.1s LCP is engineering effort with no ranking return. So a passing
   metric is reported as `floor met - stop here`, and only a failing one becomes a finding.
2. **Lab data is not field data.** Lighthouse simulates one load on one throttled
   connection. Where PSI returns real CrUX field data it is reported separately and
   preferred, because that is what actually counts.

Key handling: `.env` line 25 is `PAGESPEED_API_KE`, missing the trailing Y. This module
reads both spellings so it works either way. It does not patch `.env` - that is Aleem's
call - but it says which name it found so the typo surfaces instead of silently costing
`website-audit-system` its quota.
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

from _env import get_key  # noqa: E402
from _http import HttpError, get_json, quote  # noqa: E402

ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
CACHE_DIR = SKILL_DIR / ".cache" / "lighthouse"
CATEGORIES = ("seo", "accessibility", "performance")

# The Core Web Vitals floors. These are the only [confirmed] numbers in this whole skill.
FLOORS = {"largest-contentful-paint": 2500, "cumulative-layout-shift": 0.1,
          "total-blocking-time": 200}

CALLS = 0
CACHE_HITS = 0


def _key() -> tuple[str | None, str]:
    """Return (key, which_name). Tolerates the .env typo without hiding it."""
    for name in ("PAGESPEED_API_KEY", "PAGESPEED_API_KE"):
        val = get_key(name, required=False)
        if val:
            return val, name
    return None, "none - running on Google's anonymous quota"


def _cache_path(url: str, strategy: str) -> Path:
    raw = f"{url}|{strategy}|{','.join(CATEGORIES)}"
    return CACHE_DIR / (hashlib.sha1(raw.encode("utf-8")).hexdigest() + ".json")


def run(url: str, *, strategy: str = "mobile", refresh: bool = False) -> dict:
    global CALLS, CACHE_HITS

    path = _cache_path(url, strategy)
    if not refresh and path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            CACHE_HITS += 1
            data.setdefault("_meta", {})["cached"] = True
            return data
        except (json.JSONDecodeError, OSError):
            pass

    key, key_name = _key()
    qs = f"url={quote(url)}&strategy={strategy}" + "".join(f"&category={c}" for c in CATEGORIES)
    if key:
        qs += f"&key={key}"

    print(f"[lighthouse] {url} ({strategy}), categories={','.join(CATEGORIES)}, key={key_name}",
          file=sys.stderr)
    try:
        raw = get_json(f"{ENDPOINT}?{qs}", timeout=90)
    except HttpError as exc:
        msg = str(exc)
        hint = ""
        if "429" in msg or "quota" in msg.lower():
            hint = (" Anonymous quota is small. If PAGESPEED_API_KE is the only key present, "
                    "the trailing Y is missing in .env - tell Aleem rather than editing it.")
        return {"url": url, "strategy": strategy, "error": msg + hint,
                "_meta": {"cached": False, "key_name": key_name}}
    CALLS += 1

    parsed = _parse(raw, url, strategy)
    parsed["_meta"] = {"cached": False, "key_name": key_name,
                       "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(json.dumps(parsed, ensure_ascii=False, indent=1), encoding="utf-8")
    except OSError:
        pass
    return parsed


def _parse(raw: dict, url: str, strategy: str) -> dict:
    lh = raw.get("lighthouseResult") or {}
    cats = lh.get("categories") or {}
    audits = lh.get("audits") or {}

    scores = {c: round((cats.get(c, {}).get("score") or 0) * 100)
              for c in CATEGORIES if c in cats}

    # Lighthouse marks an audit failed when score < 1 and it is not informational.
    seo_refs = (cats.get("seo") or {}).get("auditRefs") or []
    seo_audits = []
    for ref in seo_refs:
        a = audits.get(ref.get("id")) or {}
        if a.get("scoreDisplayMode") in ("notApplicable", "manual", "informative"):
            continue
        seo_audits.append({
            "id": ref.get("id"),
            "title": a.get("title"),
            "passed": (a.get("score") or 0) >= 1,
            "detail": (a.get("description") or "")[:200],
        })

    # Performance audits, kept in the same compact shape as the seo list. seo-technical's
    # vitals.py maps these onto course/28's ordered fix list; nothing here decides an order.
    perf_audits = {}
    for ref in (cats.get("performance") or {}).get("auditRefs") or []:
        a = audits.get(ref.get("id")) or {}
        if not a:
            continue
        perf_audits[ref["id"]] = {"title": a.get("title"), "score": a.get("score"),
                                  "displayValue": a.get("displayValue"),
                                  "numericValue": a.get("numericValue")}

    a11y_failed = []
    for ref in (cats.get("accessibility") or {}).get("auditRefs") or []:
        a = audits.get(ref.get("id")) or {}
        if a.get("scoreDisplayMode") in ("notApplicable", "manual", "informative"):
            continue
        if (a.get("score") or 0) < 1:
            a11y_failed.append({"id": ref.get("id"), "title": a.get("title")})

    vitals = {}
    for aid, floor in FLOORS.items():
        a = audits.get(aid) or {}
        val = a.get("numericValue")
        if val is None:
            vitals[aid] = {"value": None, "verdict": "unknown", "display": None}
            continue
        met = val <= floor
        vitals[aid] = {
            "value": round(val, 3), "floor": floor, "display": a.get("displayValue"),
            "verdict": "floor met - stop here" if met else "below the floor - this is a finding",
        }

    lcp_el = ((audits.get("largest-contentful-paint-element") or {})
              .get("details", {}).get("items") or [{}])
    lcp_node = ""
    if lcp_el and isinstance(lcp_el[0], dict):
        items = lcp_el[0].get("items") or [{}]
        if items and isinstance(items[0], dict):
            lcp_node = (items[0].get("node") or {}).get("snippet", "")[:200]

    def _field(block: dict) -> dict | None:
        m = (block or {}).get("metrics") or {}
        return {k: {"percentile": v.get("percentile"), "category": v.get("category")}
                for k, v in m.items()} or None

    field_data = _field(raw.get("loadingExperience"))
    # Origin-level CrUX: the whole property's field data, aggregated. It is the fallback
    # when a single URL has too little real traffic to report, which is the common case on
    # small sites - and reporting "no field data" while this block sits unread in the same
    # response is how a real user measurement gets replaced by a lab simulation.
    origin_field = _field(raw.get("originLoadingExperience"))

    return {
        "url": url, "strategy": strategy, "scores": scores,
        "seo_audits": seo_audits,
        "seo_failed": [a for a in seo_audits if not a["passed"]],
        "accessibility_failed": a11y_failed,
        "perf_audits": perf_audits,
        "core_web_vitals_lab": vitals,
        "core_web_vitals_field": field_data,
        "core_web_vitals_field_origin": origin_field,
        "lcp_element": lcp_node,
        "notes": [
            "Core Web Vitals are a FLOOR. A metric that meets it needs no further work - "
            "optimizing past good is spending engineering effort for no ranking return.",
            "Lab data simulates one throttled load. Where field (CrUX) data is present it "
            "reflects real users and should be preferred." if field_data else
            "No field data: this origin has too little real-user traffic in CrUX, so only lab "
            "numbers are available. Say so rather than presenting lab data as what users see.",
        ],
    }


def cost_report() -> str:
    return f"lighthouse: {CALLS} live call(s), {CACHE_HITS} cache hit(s). Free API."


def _selftest() -> int:
    """Live. The point is proving the seo category actually comes back populated."""
    ok = True
    key, key_name = _key()

    print("1. resolve an API key, tolerating the .env typo")
    print(f"   {'PASS' if key else 'PASS (weak)'}: using {key_name}")
    if key_name == "PAGESPEED_API_KE":
        print("   NOTE: .env line 25 is missing the trailing Y. This module reads both names, "
              "but website-audit-system/scripts/pagespeed.py reads only the correct one and has "
              "therefore been running on the anonymous quota. Worth telling Aleem.")

    print("2. run against a live URL and get the SEO category back")
    res = run("https://example.com/", strategy="mobile", refresh=True)
    if res.get("error"):
        print(f"   FAIL: {res['error']}")
        return 1
    if "seo" in res["scores"] and res["seo_audits"]:
        print(f"   PASS: seo score {res['scores']['seo']}, {len(res['seo_audits'])} SEO audits returned")
    else:
        print(f"   FAIL: no SEO category in the response. scores={res['scores']}")
        ok = False

    print("3. the SEO audits are the ones this skill would otherwise approximate")
    ids = {a["id"] for a in res["seo_audits"]}
    wanted = {"document-title", "meta-description", "link-text", "is-crawlable",
              "crawlable-anchors", "viewport"}
    found = wanted & ids
    if len(found) >= 4:
        print(f"   PASS: {len(found)}/{len(wanted)} expected audits present: {sorted(found)}")
    else:
        print(f"   FAIL: only found {sorted(found)} of {sorted(wanted)}")
        ok = False

    print("4. a passing vital reads as a floor met, not an invitation to optimize")
    lcp = res["core_web_vitals_lab"].get("largest-contentful-paint", {})
    if lcp.get("verdict", "").startswith(("floor met", "below the floor")):
        print(f"   PASS: LCP {lcp.get('display')} -> {lcp['verdict']}")
    else:
        print(f"   FAIL: {lcp}")
        ok = False

    print("5. second call is cached")
    before = CALLS
    run("https://example.com/", strategy="mobile")
    if CALLS == before:
        print("   PASS: cache hit, no new call")
    else:
        print("   FAIL: refetched")
        ok = False

    print("\n" + cost_report())
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="PageSpeed Insights: SEO + accessibility + performance.")
    ap.add_argument("url", nargs="?")
    ap.add_argument("--strategy", default="mobile", choices=["mobile", "desktop"])
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()
    if not args.url:
        ap.error("url required (or use --selftest)")

    res = run(args.url, strategy=args.strategy, refresh=args.refresh)

    if args.out:
        Path(args.out).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        if res.get("error"):
            print(f"{args.url}: ERROR {res['error']} -> {args.out}")
        else:
            print(f"{args.url}: seo={res['scores'].get('seo')} "
                  f"{len(res['seo_failed'])} SEO audit(s) failed -> {args.out}")
    elif res.get("error"):
        print(f"ERROR: {res['error']}")
        return 1
    else:
        print(f"\nScores: " + ", ".join(f"{k}={v}" for k, v in res["scores"].items()))
        print("\nCore Web Vitals (lab):")
        for k, v in res["core_web_vitals_lab"].items():
            print(f"  {k:32} {str(v.get('display')):10} {v['verdict']}")
        if res["lcp_element"]:
            print(f"  LCP element: {res['lcp_element']}")
        print(f"\nSEO audits failed ({len(res['seo_failed'])}):")
        for a in res["seo_failed"]:
            print(f"  [FAIL] {a['id']:28} {a['title']}")
        if not res["seo_failed"]:
            print("  none - Google's own SEO checks all pass")
        print(f"\nAccessibility audits failed ({len(res['accessibility_failed'])}):")
        for a in res["accessibility_failed"][:10]:
            print(f"  [FAIL] {a['id']:28} {a['title']}")
        for n in res["notes"]:
            print(f"\nNOTE: {n}")

    print(cost_report(), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

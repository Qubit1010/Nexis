#!/usr/bin/env python3
"""Build the 6-tab technical Google Sheet, refusing to write an internally inconsistent one.

Mirrors seo-onpage/scripts/push_sheet.py and seo-foundation's before it: same
TABS-dict-as-source-of-truth, same header-to-key coercion, same validate/--force contract,
same one-batch-per-tab then a single formatting flush. A client holding all three sheets
should not have to learn three conventions. All Google access goes through
leads-to-crm/scripts/sheets.py; nothing here reimplements it.

The six blocking invariants. Each one exists because the sheet would otherwise contradict
the course it is built from, and a deliverable that argues with itself is worse than none:

  1. TIER ORDER. A `this week` finding from a lower tier while a higher-tier failure sits in
     `this month` or lower. course/21 is explicit that the order is not negotiable and that
     a failure at a lower layer invalidates the work above it - fixing schema on a site
     whose pages are not indexed is polishing something invisible. This is the invariant
     that matters most in this skill and it is the one an automated tool always gets wrong,
     because schema and performance findings are the easy ones to generate.

  2. A CORE WEB VITALS VERDICT FROM LAB DATA. Google ranks on field data (CrUX) only, and a
     page can score 100 in Lighthouse and fail the field assessment. A row whose source is
     lab must carry `unknown`, never pass or fail.

  3. A REDIRECT FIX THAT CREATES A CHAIN. An action pointing at a URL that itself redirects
     just moves the chain. course/24: flatten to one hop, then repoint internal links.

  4. A SITEMAP ROW KEPT WITH A DISQUALIFYING STATE. Marking a non-200, noindexed or
     cross-canonicalized URL `keep in sitemap` contradicts course/22's contents rule, and
     junk in the sitemap trains Google to distrust the whole file.

  5. AN EVIDENCE-FREE FINDING. A claim with nothing to point at is an opinion wearing a
     finding's clothes, and the client has no way to check it.

  6. MORE THAN FIVE `this week` FINDINGS. The deliverable is a prioritized diagnosis. An
     audit naming forty problems is the standard output of an automated tool, and it is why
     tool exports do not sell.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO = SKILL_DIR.parents[2]
sys.path.insert(0, str(REPO / ".claude" / "skills" / "leads-to-crm" / "scripts"))

import sheets  # noqa: E402

TABS: dict[str, list[str]] = {
    "Technical Audit": [
        "Tier", "Area", "Check", "Observed", "Threshold", "Verdict", "Source", "Evidence",
    ],
    "Findings": [
        "Priority", "Tier", "Area", "Finding", "Evidence", "Fix", "Expected Effect",
        "Effort", "Owner",
    ],
    "Indexation": [
        "URL", "Status", "In Sitemap", "Indexable", "Blocked Reason", "Declared Canonical",
        "Google-Selected Canonical", "Action",
    ],
    "Redirects": [
        "From URL", "To URL", "Hops", "Status Chain", "Type", "Internal Links Pointing Here",
        "Action",
    ],
    "Architecture": [
        "URL", "Click Depth", "Internal Links In", "Template", "In Sitewide Nav",
        "Has Breadcrumbs", "Action",
    ],
    "Core Web Vitals": [
        "Template", "Sample URL", "Pages", "Data Source", "LCP", "INP", "CLS", "Verdict",
        "Primary Fix",
    ],
}

PAYLOAD_KEYS = {
    "Technical Audit": "audit", "Findings": "findings", "Indexation": "indexation",
    "Redirects": "redirects", "Architecture": "architecture", "Core Web Vitals": "vitals",
}

VALID_VERDICT = {"pass", "fail", "review", "unknown"}
VALID_PRIORITY = {"this week", "this month", "structural", "backlog"}

# course/21's pyramid. Lower number = must be fixed first; a failure here invalidates
# everything above it.
TIERS = {
    "crawlability": 1, "robots": 1, "indexation": 2, "sitemaps": 2,
    "canonicals": 3, "duplicates": 3, "redirects": 4, "status codes": 4,
    "architecture": 5, "rendering": 6, "javascript": 6, "mobile": 6,
    "performance": 7, "core web vitals": 7, "speed": 7,
    "schema": 8, "structured data": 8, "hreflang": 9, "international": 9,
}
PRIORITY_RANK = {"this week": 0, "this month": 1, "structural": 2, "backlog": 3}


def tier_of(text: str) -> int | None:
    """The pyramid level a finding belongs to, read from its Tier or Area text."""
    low = (text or "").strip().lower()
    if low.isdigit():
        return int(low)
    for name, n in TIERS.items():
        if name in low:
            return n
    return None


# Windows' command line dies around 8191 characters and gws takes the payload as one arg.
# Budget conservatively: the range params and the exe path also consume it.
CLI_BUDGET = 6000


def _write_rows(sid: str, tab: str, values: list[list], ncols: int) -> bool:
    """Write a tab in slices sized by serialized length, not by row count.

    sheets.update_rows() batches at a fixed 25 rows, which is right for lead rows and wrong
    here: one Technical Audit row can carry 2000 characters of evidence, so 25 of them is
    50KB and gws dies with WinError 206 - the filename or extension is too long. That is
    exactly how this first failed on a real 112-row audit.
    """
    last = sheets.col_letter(ncols - 1)
    row, i = 1, 0
    while i < len(values):
        chunk, size = [], 0
        while i < len(values):
            cost = len(json.dumps(values[i], ensure_ascii=False))
            if chunk and size + cost > CLI_BUDGET:
                break
            chunk.append(values[i])
            size += cost
            i += 1
        a1 = f"{tab}!A{row}:{last}{row + len(chunk) - 1}"
        if not sheets.update_range(sid, a1, chunk):
            return False
        row += len(chunk)
    return True


def _row(record: dict, headers: list[str]) -> list:
    out = []
    for h in headers:
        key = h.lower().replace(" ", "_").replace("?", "").replace("(", "").replace(")", "")
        val = record.get(key, record.get(h, ""))
        if isinstance(val, list):
            val = ", ".join(str(v) for v in val)
        elif isinstance(val, bool):
            val = "Yes" if val else "No"
        elif val is None:
            val = ""
        out.append(val)
    return out


def validate(payload: dict) -> list[str]:
    """Human-readable problems that each prescribe the fix. Empty list means clean."""
    problems: list[str] = []
    findings = payload.get("findings") or []

    # --- 5. evidence, and enum sanity
    for r in findings:
        if not (r.get("evidence") or "").strip():
            problems.append(
                f"Findings: \"{str(r.get('finding'))[:60]}\" has no evidence. Every claim points "
                "at a measurement, a report or a live URL, otherwise it is an opinion and the "
                "client has no way to check it.")
        p = (r.get("priority") or "").strip().lower()
        if p and p not in VALID_PRIORITY:
            problems.append(f"Findings: priority '{p}' is not one of {sorted(VALID_PRIORITY)}.")

    for r in payload.get("audit") or []:
        v = (r.get("verdict") or "").strip().lower()
        if v and v not in VALID_VERDICT:
            problems.append(f"Technical Audit: verdict '{v}' is not one of {sorted(VALID_VERDICT)}.")

    # --- 1. tier order
    ranked = []
    for r in findings:
        t = tier_of(r.get("tier") or "") or tier_of(r.get("area") or "")
        p = PRIORITY_RANK.get((r.get("priority") or "").strip().lower())
        if t is not None and p is not None:
            ranked.append((t, p, r))
    for tier_hi, prio_hi, hi in ranked:
        for tier_lo, prio_lo, lo in ranked:
            if tier_lo > tier_hi and prio_lo < prio_hi:
                problems.append(
                    f"Findings: \"{str(lo.get('finding'))[:50]}\" (tier {tier_lo}) is prioritized "
                    f"'{lo.get('priority')}' while \"{str(hi.get('finding'))[:50]}\" (tier "
                    f"{tier_hi}) is only '{hi.get('priority')}'. The Tier 3 order is not "
                    "negotiable: a failure at a lower layer invalidates the work above it. "
                    "Fixing schema or speed on a site whose pages are not crawled or indexed is "
                    "polishing something invisible. Reorder, or merge the two.")
                break

    # --- 6. three findings beat forty
    top = [f for f in findings if (f.get("priority") or "").strip().lower() == "this week"]
    if len(top) > 5:
        problems.append(
            f"Findings: {len(top)} findings are marked 'this week'. The deliverable is a "
            "prioritized diagnosis, not a list - an audit that names forty problems is the "
            "standard output of an automated tool and is why tool exports do not sell. Rank "
            "them and move the rest to 'this month' or 'backlog'.")

    # --- 2. no field data, no verdict
    for r in payload.get("vitals") or []:
        src = (r.get("data_source") or "").strip().lower()
        v = (r.get("verdict") or "").strip().lower()
        if v and v not in VALID_VERDICT:
            problems.append(f"Core Web Vitals: verdict '{v}' is not one of {sorted(VALID_VERDICT)}.")
        if v in {"pass", "fail"} and ("lab" in src or "lighthouse" in src or not src):
            problems.append(
                f"Core Web Vitals: {r.get('template') or r.get('sample_url')} carries verdict "
                f"'{v}' with data source '{r.get('data_source') or '(blank)'}'. Google ranks on "
                "field data (CrUX) only, and a page can score 100 in Lighthouse and still fail "
                "the field assessment. A lab-sourced row is 'unknown'. Name the field source or "
                "change the verdict.")

    # --- 3. a fix that just moves the chain
    redirects = payload.get("redirects") or []
    sources = {(r.get("from_url") or "").strip(): r for r in redirects if r.get("from_url")}
    for r in redirects:
        target = (r.get("to_url") or "").strip()
        if target and target in sources and target != (r.get("from_url") or "").strip():
            problems.append(
                f"Redirects: {r.get('from_url')} is pointed at {target}, which is itself a "
                "redirect source on this tab. That is a chain, not a fix - each hop adds "
                "100-500ms and leaks signal, and Googlebot may abandon chains beyond five hops. "
                "Point it at the final destination, then repoint internal links there too.")

    # --- 4. junk kept in the sitemap
    for r in payload.get("indexation") or []:
        action = (r.get("action") or "").strip().lower()
        in_sitemap = str(r.get("in_sitemap") or "").strip().lower() in {"yes", "true", "1"}
        status = str(r.get("status") or "").strip()
        indexable = str(r.get("indexable") or "").strip().lower()
        reasons = []
        if status and not status.startswith("200"):
            reasons.append(f"status {status}")
        if indexable in {"no", "false"}:
            reasons.append(r.get("blocked_reason") or "not indexable")
        can = (r.get("declared_canonical") or "").strip()
        url = (r.get("url") or "").strip()
        if can and url and can != url:
            reasons.append(f"canonicalized to {can}")
        if reasons and (in_sitemap and "remove from sitemap" not in action):
            problems.append(
                f"Indexation: {url} is in the sitemap with {', '.join(reasons)}, and the action "
                f"is '{r.get('action') or '(blank)'}'. A sitemap must contain only 200-status, "
                "canonical, indexable URLs - junk in it trains Google to distrust the whole "
                "file. Either fix the URL or set the action to remove it from the sitemap.")

    return problems


def build(payload: dict, title: str) -> str:
    tab_names = [t for t in TABS if payload.get(PAYLOAD_KEYS[t])]
    if not tab_names:
        raise SystemExit("payload has no rows for any tab")

    sid, _default, gid = sheets.create_spreadsheet(title)
    first = tab_names[0]
    sheets.batch_update(sid, [{"updateSheetProperties": {
        "properties": {"sheetId": gid, "title": first}, "fields": "title"}}])

    gids = {first: gid}
    for tab in tab_names[1:]:
        sheets.batch_update(sid, [{"addSheet": {"properties": {"title": tab}}}])
        gids[tab] = sheets.get_gid(sid, tab)

    fmt: list[dict] = []
    for tab in tab_names:
        headers = TABS[tab]
        records = payload.get(PAYLOAD_KEYS[tab]) or []
        values = [headers] + [_row(r, headers) for r in records]
        if not _write_rows(sid, tab, values, len(headers)):
            raise SystemExit(f"failed writing tab {tab}")
        print(f"  [sheet] {tab}: {len(records)} row(s)", file=sys.stderr)
        g = gids[tab]
        fmt.append({"repeatCell": {
            "range": {"sheetId": g, "startRowIndex": 0, "endRowIndex": 1},
            "cell": {"userEnteredFormat": {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}}},
            "fields": "userEnteredFormat(textFormat,backgroundColor)"}})
        fmt.append({"updateSheetProperties": {
            "properties": {"sheetId": g,
                           "gridProperties": {"frozenRowCount": 1, "frozenColumnCount": 1}},
            "fields": "gridProperties(frozenRowCount,frozenColumnCount)"}})
    sheets.batch_update(sid, fmt)

    return f"https://docs.google.com/spreadsheets/d/{sid}/edit"


# --------------------------------------------------------------------------- payload

def from_results(*results: dict) -> dict:
    """Turn any mix of technical/schema/vitals/render_diff results into a sheet payload.

    Findings are deliberately NOT generated here. Ranking three findings out of sixty rows
    is the judgment the skill exists to supply, and a script that auto-promoted every `fail`
    would produce exactly the forty-item export invariant 6 blocks.
    """
    audit, vitals = [], []
    for res in results:
        for r in res.get("checks") or []:
            area = r.get("area", "")
            if area == "Core Web Vitals" and r["check_id"].startswith("cwv."):
                ev = r.get("evidence", "")
                src = "field" if "real users" in ev or "origin-level CrUX" in ev else "lab"
                vitals.append({
                    "template": r["check_id"].removeprefix("cwv."),
                    "sample_url": next((ln.split("sampled at ")[-1] for ln in ev.splitlines()
                                        if "sampled at " in ln), ""),
                    "data_source": src, "verdict": r["verdict"],
                    "lcp": _metric(r["observed"], "LCP"), "inp": _metric(r["observed"], "INP"),
                    "cls": _metric(r["observed"], "CLS"),
                    "primary_fix": "" if r["verdict"] == "pass" else "see Findings",
                })
                continue
            audit.append({
                "tier": tier_of(area) or "", "area": area, "check": r["check_id"],
                "observed": r["observed"], "threshold": r["threshold"],
                "verdict": r["verdict"], "source": r["source"],
                "evidence": (r.get("evidence") or "")[:2000],
            })
    return {"audit": audit, "vitals": vitals, "findings": [], "indexation": [],
            "redirects": [], "architecture": []}


def _metric(observed: str, name: str) -> str:
    for part in (observed or "").split(","):
        if part.strip().startswith(name):
            return part.strip()
    return ""


# --------------------------------------------------------------------------- selftest

def _selftest() -> int:
    """Pure logic. No network, no Sheet, no gws token needed."""
    ok = True

    def check(name, payload, expect):
        nonlocal ok
        probs = validate(payload)
        hit = any(expect in p for p in probs)
        print(f"   {'PASS' if hit else 'FAIL'}: {name}")
        if not hit:
            print(f"          got: {probs}")
            ok = False

    print("1. a clean payload validates")
    clean = {
        "findings": [{"priority": "this week", "tier": "indexation",
                      "finding": "38 sitemap URLs share one lastmod",
                      "evidence": "pages-sitemap.xml, every <lastmod> is 2026-08-03"}],
        "vitals": [{"template": "/blog/*", "data_source": "field (CrUX)", "verdict": "pass"}],
        "redirects": [{"from_url": "/old", "to_url": "/new"}],
        "indexation": [{"url": "/a", "status": "200", "in_sitemap": "Yes", "indexable": "Yes",
                        "declared_canonical": "/a", "action": "keep"}],
    }
    probs = validate(clean)
    print("   PASS: no problems" if not probs else f"   FAIL: {probs}")
    ok &= not probs

    print("2. INVARIANT 1 - a schema fix ranked above an indexation failure is blocked")
    check("tier order inverted",
          {"findings": [
              {"priority": "this week", "tier": "schema", "finding": "Add Organization schema",
               "evidence": "no JSON-LD on the homepage"},
              {"priority": "this month", "tier": "indexation", "finding": "Sitemap lists 404s",
               "evidence": "3 of 38 URLs return 404"}]},
          "not negotiable")

    print("3. INVARIANT 2 - a Core Web Vitals verdict from lab data is blocked")
    check("lab-sourced CWV verdict",
          {"vitals": [{"template": "/blog/*", "data_source": "Lighthouse lab", "verdict": "pass"}]},
          "Google ranks on field data")
    check("CWV verdict with no source named",
          {"vitals": [{"template": "/x", "data_source": "", "verdict": "fail"}]},
          "field data (CrUX) only")

    print("4. INVARIANT 3 - a redirect fix that just moves the chain is blocked")
    check("chained redirect fix",
          {"redirects": [{"from_url": "/a", "to_url": "/b"},
                         {"from_url": "/b", "to_url": "/c"}]},
          "That is a chain, not a fix")

    print("5. INVARIANT 4 - junk kept in the sitemap is blocked")
    check("404 kept in sitemap",
          {"indexation": [{"url": "/gone", "status": "404", "in_sitemap": "Yes",
                           "action": "keep"}]},
          "trains Google to distrust")
    check("noindexed URL kept in sitemap",
          {"indexation": [{"url": "/b", "status": "200", "in_sitemap": "Yes", "indexable": "No",
                           "blocked_reason": "noindex", "action": "monitor"}]},
          "only 200-status, canonical, indexable URLs")

    print("6. INVARIANT 5 - an evidence-free finding is blocked")
    check("no evidence",
          {"findings": [{"priority": "this week", "finding": "Technical SEO needs work",
                         "evidence": ""}]}, "has no evidence")

    print("7. INVARIANT 6 - more than five 'this week' findings is blocked")
    check("padding",
          {"findings": [{"priority": "this week", "tier": "robots", "finding": f"f{i}",
                         "evidence": "e"} for i in range(7)]},
          "prioritized diagnosis, not a list")

    print("8. tier_of reads the pyramid from either column")
    cases = {"robots": 1, "Sitemaps and indexation": 2, "Canonicals and duplicates": 3,
             "Redirects and status codes": 4, "Site architecture": 5,
             "Rendering and AI visibility": 6, "Core Web Vitals": 7, "Structured data": 8,
             "International and hreflang": 9, "7": 7, "nonsense": None}
    bad = {k: (tier_of(k), v) for k, v in cases.items() if tier_of(k) != v}
    print("   PASS: every area maps to its tier" if not bad else f"   FAIL: {bad}")
    ok &= not bad

    print("9. header-to-key coercion maps every column")
    r = _row({"from_url": "/a", "internal_links_pointing_here": 4, "hops": None}, TABS["Redirects"])
    if r[0] == "/a" and 4 in r and "" in r:
        print("   PASS: keys, ints and None all coerced")
    else:
        print(f"   FAIL: {r}")
        ok = False

    print("10. from_results routes CWV rows to their own tab with a data source")
    payload = from_results({"checks": [
        {"check_id": "cwv./blog/*", "area": "Core Web Vitals", "observed": "LCP 1203ms, INP 89ms",
         "threshold": "t", "verdict": "pass", "source": "course/27",
         "evidence": "sampled at https://e.test/b\nSource: this URL's real users"},
        {"check_id": "robots.disallow_all", "area": "Crawlability and robots", "observed": "ok",
         "threshold": "t", "verdict": "pass", "source": "course/21", "evidence": ""}]})
    v = payload["vitals"][0]
    if len(payload["audit"]) == 1 and v["data_source"] == "field" and v["lcp"] == "LCP 1203ms" \
            and payload["audit"][0]["tier"] == 1 and not validate(payload):
        print("   PASS: split by tab, field source detected, tier assigned, validates clean")
    else:
        print(f"   FAIL: {payload['vitals']} / {payload['audit']}")
        ok = False

    print("11. tab writes chunk by serialized size, not by row count")
    sent = []
    real = sheets.update_range
    sheets.update_range = lambda sid, a1, chunk: (sent.append((a1, chunk)), True)[1]
    try:
        # 112 rows carrying 2000 chars of evidence each - the shape that hit WinError 206.
        big = [["h1", "h2"]] + [[f"r{i}", "E" * 2000] for i in range(112)]
        _write_rows("sid", "Technical Audit", big, 2)
    finally:
        sheets.update_range = real
    oversized = [a1 for a1, c in sent
                 if len(json.dumps(c, ensure_ascii=False)) > CLI_BUDGET + 2100]
    rows_written = sum(len(c) for _, c in sent)
    contiguous = sent[0][0].startswith("Technical Audit!A1:") and rows_written == len(big)
    if not oversized and contiguous and len(sent) > 1:
        print(f"   PASS: 113 rows split into {len(sent)} writes, none over budget, no gaps")
    else:
        print(f"   FAIL: {len(sent)} write(s), oversized={oversized}, rows={rows_written}")
        ok = False

    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the 6-tab technical audit Google Sheet.")
    ap.add_argument("--payload", help="JSON file with the tab data")
    ap.add_argument("--from-results", nargs="+",
                    help="result JSONs from technical/schema/vitals/render_diff --out")
    ap.add_argument("--title")
    ap.add_argument("--validate-only", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()
    if not args.payload and not args.from_results:
        ap.error("--payload or --from-results required (or use --selftest)")

    if args.from_results:
        payload = from_results(*[json.loads(Path(p).read_text(encoding="utf-8"))
                                 for p in args.from_results])
        print("Findings, Indexation, Redirects and Architecture are intentionally empty - they "
              "carry the judgment, not the raw rows. Fill them before shipping.", file=sys.stderr)
    else:
        payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))

    if not args.title and not args.validate_only:
        ap.error("--title required when writing")

    problems = validate(payload)
    if problems:
        print(f"{len(problems)} validation problem(s):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
    else:
        print("Validation clean.", file=sys.stderr)

    if args.validate_only:
        return 1 if problems else 0
    if problems and not args.force:
        print("\nRefusing to write. An internally inconsistent sheet is worse than no sheet - "
              "fix the problems above, or pass --force if you have a reason.", file=sys.stderr)
        return 1

    print(build(payload, args.title))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

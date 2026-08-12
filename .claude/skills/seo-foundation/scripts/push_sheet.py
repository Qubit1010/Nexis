"""Write the SEO foundation to a multi-tab Google Sheet - the working artifact.

Six tabs, because the keyword map is the deliverable but it is unreadable without the
evidence behind it. Someone should be able to open the map, question a row, and find the
SERP read that produced it two tabs over.

The one invariant this file enforces: **every cluster maps to exactly one URL, and no URL
appears twice.** `course/08` calls a map that breaks it "a wish list, not a map", because a
URL serving three clusters is cannibalization wearing a plan's clothes. `validate()` checks
it before anything is written, and a violation is reported as the finding it is rather than
being silently tidied away.

Sheets plumbing is reused wholesale from leads-to-crm's `sheets.py` (gws CLI, retry and
timeout already handled), and the create-and-format pattern from lead-generator's
`scrape_directory.push_to_sheet`. Nothing here reimplements Google API access.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / ".claude" / "skills" / "leads-to-crm" / "scripts"))
import sheets  # noqa: E402

TABS: dict[str, list[str]] = {
    "Keyword Master": [
        "Query", "Source", "Intent", "Relevance", "Intent Value", "Priority",
        "Click Availability", "Winnability", "Cluster", "Volume (manual)", "Notes"],
    "Clusters": [
        "Cluster Name", "Primary Query", "Secondary Queries", "Intent", "Size", "Avg Priority"],
    # The exact 8-column schema from course/08. Do not reorder or rename - other tabs and
    # the report cross-reference these headers by name.
    "Keyword Map": [
        "Cluster Name", "Primary Query", "Secondary Queries", "Intent", "Target URL",
        "Status", "Priority", "Click Availability"],
    "SERP Analysis": [
        "Query", "Top Domains", "Domain Diversity", "UGC on P1", "Platform Slots",
        "Sitelinked", "Dominant Content Type", "Freshness", "PAA Count", "AI Overview",
        "Winnability", "Winnability Reasons"],
    "Competitors": [
        "Domain", "Appearances", "Best Position", "Queries Owned", "Business Competitor?", "Type"],
    "Cannibalization": [
        "Target URL", "Competing Clusters", "Primary Queries", "Recommended Action", "Note"],
}

VALID_STATUS = {"exists and fine", "exists and needs work", "needs creating", "merge into another"}


def validate(payload: dict) -> list[str]:
    """Structural problems worth blocking on. Returns human-readable messages."""
    problems: list[str] = []
    rows = payload.get("keyword_map") or []

    by_url: dict[str, list[str]] = defaultdict(list)
    for r in rows:
        url = (r.get("target_url") or "").strip()
        if url and (r.get("status") or "").strip().lower() != "merge into another":
            by_url[url].append(r.get("cluster_name") or r.get("primary_query") or "?")

    for url, clusters in by_url.items():
        if len(clusters) > 1:
            problems.append(
                f"Target URL {url} is claimed by {len(clusters)} clusters ({', '.join(clusters)}). "
                f"That is cannibalization - resolve it (consolidate / differentiate / prune) and "
                f"mark the losing rows 'merge into another', or record it on the Cannibalization tab.")

    for r in rows:
        st = (r.get("status") or "").strip().lower()
        if st and st not in VALID_STATUS:
            problems.append(f"Cluster '{r.get('cluster_name')}' has status {st!r}; "
                            f"expected one of: {', '.join(sorted(VALID_STATUS))}.")
        if not (r.get("primary_query") or "").strip():
            problems.append(f"Cluster '{r.get('cluster_name')}' has no primary query.")
    return problems


def _row(record: dict, headers: list[str]) -> list[str]:
    out = []
    for h in headers:
        key = h.lower().replace(" ", "_").replace("?", "").replace("(", "").replace(")", "")
        v = record.get(key, record.get(h, ""))
        if isinstance(v, list):
            v = ", ".join(str(x) for x in v)
        elif isinstance(v, bool):
            v = "Yes" if v else "No"
        elif v is None:
            v = ""
        out.append(str(v))
    return out


def _payload_key(tab: str) -> str:
    return {"Keyword Master": "keywords", "Clusters": "clusters", "Keyword Map": "keyword_map",
            "SERP Analysis": "serp_analysis", "Competitors": "competitors",
            "Cannibalization": "cannibalization"}[tab]


def build(payload: dict, title: str) -> str:
    """Create the spreadsheet and fill every tab. Returns the URL."""
    first_tab_name = next(iter(TABS))
    sid, default_tab, gid = sheets.create_spreadsheet(title)

    # Rename the auto-created first sheet rather than leaving an empty "Sheet1" behind.
    sheets.batch_update(sid, [{"updateSheetProperties": {
        "properties": {"sheetId": gid, "title": first_tab_name}, "fields": "title"}}])
    gids = {first_tab_name: gid}

    for tab in list(TABS)[1:]:
        sheets.batch_update(sid, [{"addSheet": {"properties": {"title": tab}}}])
        gids[tab] = sheets.get_gid(sid, tab)

    fmt_requests = []
    for tab, headers in TABS.items():
        records = payload.get(_payload_key(tab)) or []
        values = [headers] + [_row(r, headers) for r in records]
        sheets.update_range(sid, f"{tab}!A1", values)
        print(f"  [sheet] {tab}: {len(records)} row(s)", file=sys.stderr)

        g = gids.get(tab)
        if g is None:
            continue
        fmt_requests += [
            {"repeatCell": {
                "range": {"sheetId": g, "startRowIndex": 0, "endRowIndex": 1},
                "cell": {"userEnteredFormat": {
                    "textFormat": {"bold": True},
                    "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}}},
                "fields": "userEnteredFormat(textFormat,backgroundColor)"}},
            {"updateSheetProperties": {
                "properties": {"sheetId": g,
                               "gridProperties": {"frozenRowCount": 1, "frozenColumnCount": 1}},
                "fields": "gridProperties(frozenRowCount,frozenColumnCount)"}},
        ]
    if fmt_requests:
        sheets.batch_update(sid, fmt_requests)
    return f"https://docs.google.com/spreadsheets/d/{sid}/edit"


def _selftest() -> int:
    """Validation logic only - no network, no Sheet created."""
    ok = True
    print("1. clean map passes...")
    clean = {"keyword_map": [
        {"cluster_name": "crm comparison", "primary_query": "best crm", "target_url": "/blog/best-crm",
         "status": "needs creating"},
        {"cluster_name": "crm pricing", "primary_query": "crm pricing", "target_url": "/pricing",
         "status": "exists and fine"}]}
    p = validate(clean)
    print("   PASS: no problems" if not p else f"   FAIL: {p}"); ok &= not p

    print("2. duplicate URL is caught as cannibalization...")
    dupe = {"keyword_map": [
        {"cluster_name": "crm comparison", "primary_query": "best crm", "target_url": "/blog/crm",
         "status": "needs creating"},
        {"cluster_name": "crm reviews", "primary_query": "crm reviews", "target_url": "/blog/crm",
         "status": "exists and fine"}]}
    p = validate(dupe)
    if p and "cannibalization" in p[0].lower():
        print(f"   PASS: {p[0][:88]}...")
    else:
        print(f"   FAIL: duplicate URL not caught (got {p})"); ok = False

    print("3. rows marked 'merge into another' are exempt...")
    merged = {"keyword_map": [
        {"cluster_name": "a", "primary_query": "q1", "target_url": "/x", "status": "exists and fine"},
        {"cluster_name": "b", "primary_query": "q2", "target_url": "/x", "status": "merge into another"}]}
    p = validate(merged)
    print("   PASS: merge rows do not count as duplicates" if not p else f"   FAIL: {p}"); ok &= not p

    print("4. bad status is caught...")
    bad = {"keyword_map": [{"cluster_name": "a", "primary_query": "q", "target_url": "/x",
                            "status": "todo"}]}
    p = validate(bad)
    if p and "expected one of" in p[0]:
        print("   PASS: invalid status rejected")
    else:
        print(f"   FAIL: bad status not caught (got {p})"); ok = False

    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Push the SEO foundation to a multi-tab Google Sheet.")
    ap.add_argument("--payload", help="JSON file with keys: keywords, clusters, keyword_map, "
                                      "serp_analysis, competitors, cannibalization")
    ap.add_argument("--title", help="spreadsheet title, e.g. 'SEO Foundation - Acme'")
    ap.add_argument("--validate-only", action="store_true")
    ap.add_argument("--force", action="store_true", help="write even if validation fails")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()
    if not args.payload:
        ap.error("--payload required (or use --selftest)")
    # --title is only needed to create a spreadsheet. Validation is a pre-flight check and
    # should run before anyone has decided what to call the thing.
    if not args.title and not args.validate_only:
        ap.error("--title required when writing (omit it only with --validate-only)")

    payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
    problems = validate(payload)
    if problems:
        print(f"{len(problems)} validation problem(s):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        if not args.force and not args.validate_only:
            print("\nRefusing to write. Fix these, or pass --force if the duplicates are "
                  "intentional and recorded on the Cannibalization tab.", file=sys.stderr)
            return 1
    else:
        print("Validation clean: every cluster owns exactly one URL.", file=sys.stderr)

    if args.validate_only:
        return 1 if problems else 0

    url = build(payload, args.title)
    print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

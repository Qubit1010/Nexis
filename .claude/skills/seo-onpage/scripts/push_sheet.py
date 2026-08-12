#!/usr/bin/env python3
"""Build the 6-tab on-page Google Sheet, refusing to write an internally inconsistent one.

Mirrors seo-foundation/scripts/push_sheet.py deliberately: same TABS-dict-as-source-of-truth
shape, same header-to-key coercion, same validate/--force contract, same one-batch-per-tab
then a single accumulated formatting flush. A client who has both sheets should not have to
learn two conventions.

All Google access goes through leads-to-crm/scripts/sheets.py, which already handles the
gws invocation, the retry, and the Windows command-line length limit. Nothing here
reimplements Google API access.

The validation is the part worth reading. A sheet that says a page is fine on one tab and
broken on another is worse than no sheet, so the write is blocked on:

  - a Metadata row proposing a title or description that breaks the very threshold this
    skill exists to enforce (an audit that ships a 78-character replacement title has
    failed at its own job)
  - a Content Inventory row with a blank track, because a blank means the decision was
    avoided and avoided decisions are why the site has 300 thin pages
  - a merge target that is itself marked for removal
  - a Findings row with no evidence, which is an opinion wearing a finding's clothes
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

TITLE_MIN, TITLE_MAX = 50, 60
META_MIN, META_MAX = 105, 155

TABS: dict[str, list[str]] = {
    "Page Audit": [
        "URL", "Area", "Check", "Observed", "Threshold", "Verdict", "Source", "Evidence",
    ],
    "Findings": [
        "Priority", "Area", "Finding", "Evidence", "Fix", "Expected Effect", "Effort", "Owner",
    ],
    "Metadata": [
        "URL", "Primary Query", "Current Title", "Proposed Title", "Title Chars",
        "Current Meta", "Proposed Meta", "Meta Chars", "Current H1", "Proposed H1", "Notes",
    ],
    "Content Inventory": [
        "URL", "Clicks 6mo", "Impressions 6mo", "Internal Links In", "External Backlinks",
        "Cluster", "Last Meaningful Update", "Track", "Reason",
    ],
    "Internal Links": [
        "Type", "From URL", "To URL", "Anchor", "Detail", "Action",
    ],
    "Media": [
        "Page URL", "Image", "Bytes", "Format", "Natural Size", "Has Alt",
        "Explicit Size", "Measured WebP Saving", "Action",
    ],
}

VALID_TRACK = {"keep", "update", "merge", "remove"}
VALID_VERDICT = {"pass", "fail", "review", "unknown"}
VALID_PRIORITY = {"this week", "this month", "structural", "backlog"}
VALID_LINK_TYPE = {"orphan", "opportunity", "bad anchor", "too deep", "broken", "redirect",
                   "unreachable"}

PAYLOAD_KEYS = {
    "Page Audit": "page_audit", "Findings": "findings", "Metadata": "metadata",
    "Content Inventory": "inventory", "Internal Links": "internal_links", "Media": "media",
}


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

    for r in payload.get("metadata") or []:
        url = r.get("url", "(no url)")
        pt = (r.get("proposed_title") or "").strip()
        if pt and not (TITLE_MIN <= len(pt) <= TITLE_MAX):
            problems.append(
                f"Metadata: the proposed title for {url} is {len(pt)} characters, outside "
                f"{TITLE_MIN}-{TITLE_MAX}. Shipping a replacement that breaks the threshold this "
                "audit is enforcing undermines the whole deliverable. Rewrite it before writing.")
        pm = (r.get("proposed_meta") or "").strip()
        if pm and not (META_MIN <= len(pm) <= META_MAX):
            problems.append(
                f"Metadata: the proposed meta description for {url} is {len(pm)} characters, "
                f"outside {META_MIN}-{META_MAX}. Rewrite it before writing.")

    inv = payload.get("inventory") or []
    tracks = {}
    for r in inv:
        url = r.get("url", "(no url)")
        t = (r.get("track") or "").strip().lower()
        if not t:
            problems.append(
                f"Content Inventory: {url} has no track. Every URL gets exactly one of "
                f"{sorted(VALID_TRACK)} - a blank means the decision was avoided, and avoided "
                "decisions are how a site accumulates 300 pages nobody will defend.")
        elif t not in VALID_TRACK:
            problems.append(f"Content Inventory: {url} has track '{t}', expected one of "
                            f"{sorted(VALID_TRACK)}.")
        tracks[url] = t
        if t == "merge" and not (r.get("reason") or "").strip():
            problems.append(f"Content Inventory: {url} is marked merge with no reason. Name the "
                            "page it merges into, or the instruction is unexecutable.")

    for r in inv:
        t = (r.get("track") or "").strip().lower()
        target = (r.get("merge_into") or "").strip()
        if t == "merge" and target and tracks.get(target) == "remove":
            problems.append(
                f"Content Inventory: {r.get('url')} merges into {target}, which is itself marked "
                "remove. Pick the winner first - consolidation means 301 the losers to the "
                "strongest page, never to a page that is about to disappear.")

    for r in payload.get("findings") or []:
        if not (r.get("evidence") or "").strip():
            problems.append(
                f"Findings: \"{str(r.get('finding'))[:60]}\" has no evidence. Every claim points "
                "at a measurement, a report or a SERP, otherwise it is an opinion and the client "
                "has no way to check it.")
        p = (r.get("priority") or "").strip().lower()
        if p and p not in VALID_PRIORITY:
            problems.append(f"Findings: priority '{p}' is not one of {sorted(VALID_PRIORITY)}.")

    for r in payload.get("page_audit") or []:
        v = (r.get("verdict") or "").strip().lower()
        if v and v not in VALID_VERDICT:
            problems.append(f"Page Audit: verdict '{v}' is not one of {sorted(VALID_VERDICT)}.")

    for r in payload.get("internal_links") or []:
        t = (r.get("type") or "").strip().lower()
        if t and t not in VALID_LINK_TYPE:
            problems.append(f"Internal Links: type '{t}' is not one of {sorted(VALID_LINK_TYPE)}.")

    findings = payload.get("findings") or []
    top = [f for f in findings if (f.get("priority") or "").strip().lower() == "this week"]
    if len(top) > 5:
        problems.append(
            f"Findings: {len(top)} findings are marked 'this week'. The deliverable is a "
            "prioritized diagnosis, not a list - an audit that names forty problems is the "
            "standard output of an automated tool and is why tool exports do not sell. Rank "
            "them and move the rest to 'this month' or 'backlog'.")

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
        sheets.update_range(sid, f"{tab}!A1", values)
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


def _selftest() -> int:
    """Pure logic. No network, no Sheet, no gws token needed."""
    ok = True

    def check(name, payload, expect_substring):
        nonlocal ok
        probs = validate(payload)
        hit = any(expect_substring in p for p in probs)
        print(f"   {'PASS' if hit else 'FAIL'}: {name}")
        if not hit:
            print(f"          got: {probs}")
            ok = False

    print("1. a clean payload validates")
    clean = {
        "metadata": [{"url": "/a", "proposed_title": "Garden Landscaping for Small Urban Yards Explained",
                      "proposed_meta": "Garden landscaping for small urban yards. Design, planting and drainage, with real costs and timelines from 40 projects."}],
        "inventory": [{"url": "/a", "track": "keep"}],
        "findings": [{"priority": "this week", "finding": "Titles are filing labels",
                      "evidence": "6 of 8 priority pages open with the brand name"}],
    }
    probs = validate(clean)
    if not probs:
        print("   PASS: no problems")
    else:
        print(f"   FAIL: {probs}")
        ok = False

    print("2. a proposed title that breaks the threshold is blocked")
    check("over-long proposed title",
          {"metadata": [{"url": "/a", "proposed_title": "x" * 78}]}, "outside 50-60")

    print("3. a proposed meta that breaks the threshold is blocked")
    check("over-long proposed meta",
          {"metadata": [{"url": "/a", "proposed_meta": "y" * 200}]}, "outside 105-155")

    print("4. a blank track is blocked")
    check("blank track", {"inventory": [{"url": "/a", "track": ""}]}, "has no track")

    print("5. merging into a page that is being removed is blocked")
    check("merge into a removed page",
          {"inventory": [{"url": "/a", "track": "merge", "reason": "thin", "merge_into": "/b"},
                         {"url": "/b", "track": "remove"}]},
          "which is itself marked remove")

    print("6. a finding without evidence is blocked")
    check("evidence-free finding",
          {"findings": [{"priority": "this week", "finding": "SEO could be better", "evidence": ""}]},
          "has no evidence")

    print("7. more than five 'this week' findings is blocked as padding")
    check("too many top-priority findings",
          {"findings": [{"priority": "this week", "finding": f"f{i}", "evidence": "e"}
                        for i in range(7)]},
          "is a prioritized diagnosis, not a list")

    print("8. header-to-key coercion maps every column")
    r = _row({"page_url": "/a", "measured_webp_saving": "341 KB", "has_alt": True,
              "bytes": None}, TABS["Media"])
    if r[0] == "/a" and "341 KB" in r and "Yes" in r and "" in r:
        print("   PASS: keys, bools and None all coerced")
    else:
        print(f"   FAIL: {r}")
        ok = False

    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the 6-tab on-page audit Google Sheet.")
    ap.add_argument("--payload", help="JSON file with the tab data")
    ap.add_argument("--title", help="spreadsheet title")
    ap.add_argument("--validate-only", action="store_true")
    ap.add_argument("--force", action="store_true", help="write despite validation problems")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()
    if not args.payload:
        ap.error("--payload required (or use --selftest)")
    if not args.title and not args.validate_only:
        ap.error("--title required when writing")

    payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
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

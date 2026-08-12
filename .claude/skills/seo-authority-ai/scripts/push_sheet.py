"""Write the 6-tab Authority and AI Visibility sheet, or refuse to.

Same contract as the sibling writers: TABS is the source of truth, headers coerce to payload
keys, --validate-only needs no title, --force overrides, --selftest is pure logic with no
network and no gws token.

The seven invariants exist because a sheet that contradicts itself is worse than no sheet.
Invariants 1 and 2 are the ones this skill leans on hardest: they make a citation rate
inseparable from its sample size, structurally, so the number cannot be screenshotted out of
context. Everything else about the multi-run protocol is prose that a hurried person can skip.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO = SKILL_DIR.parents[2]
sys.path.insert(0, str(REPO / ".claude" / "skills" / "leads-to-crm" / "scripts"))

MIN_RUNS = 3
CLI_BUDGET = 6000          # gws dies near the Windows 8191-char command limit
EVIDENCE_MAX = 2000
MAX_THIS_WEEK = 5

VALID_VERDICT = {"pass", "fail", "review", "unknown"}
VALID_PRIORITY = {"this week", "this month", "structural", "backlog"}
NOT_CONNECTED_SOURCES = ("search console", "gsc", "ga4", "google analytics", "bing webmaster",
                         "backlink", "ahrefs", "semrush", "moz", "knowledge graph api")

TABS: dict[str, tuple[str, list[str]]] = {
    "Authority Audit": ("audit", [
        "Tier", "Area", "Check", "Observed", "Threshold", "Verdict", "Source", "Evidence"]),
    "Findings": ("findings", [
        "Priority", "Tier", "Area", "Finding", "Evidence", "Fix", "Expected Effect", "Effort", "Owner"]),
    "AI Visibility": ("ai_visibility", [
        "Prompt", "Intent", "Engine", "Runs", "Cited (n)", "Citation Rate", "Stability",
        "Brand Named Without Link", "Competitors Cited", "Cited URLs", "Ranks Top 10",
        "Sampled", "Cost USD"]),
    "Entity": ("entity", [
        "Signal", "Identifier", "Value", "Source", "Status", "Action"]),
    "Mentions and Platforms": ("mentions", [
        "Type", "Platform or URL", "Where", "Snippet", "Linked", "Description Used", "Action"]),
    "Local": ("local", [
        "Signal", "Observed", "Threshold", "Surface", "Verdict", "Action"]),
}


def _key(header: str) -> str:
    return (header.lower().replace(" ", "_").replace("?", "")
            .replace("(", "").replace(")", ""))


def _cell(v) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "Yes" if v else "No"
    if isinstance(v, (list, tuple)):
        return ", ".join(str(x) for x in v)
    return str(v)


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# ------------------------------------------------------------------ invariants

def validate(payload: dict) -> list[str]:
    """Every message names the fix, not just the rule. A validator that says 'invalid' and
    stops is a second problem."""
    problems: list[str] = []

    # 1. no citation rate from fewer than MIN_RUNS
    for r in payload.get("ai_visibility", []):
        runs = _num(r.get("runs"))
        rate = r.get("citation_rate")
        if rate in (None, "") :
            continue
        if runs is None or runs < MIN_RUNS:
            problems.append(
                f"AI Visibility: '{str(r.get('prompt'))[:44]}' on {r.get('engine')} reports a "
                f"citation rate from {r.get('runs')!r} run(s). Minimum is {MIN_RUNS}.\n"
                "    arXiv 2604.07585 decomposed 12,933 LLM brand answers: within-prompt "
                "resampling is 34.8% of total variance; brand identity is 1.5%. Measured here "
                "2026-08-08, two ChatGPT runs of one prompt seconds apart returned different "
                "winners and 0.00 Jaccard overlap on cited domains.\n"
                f"    FIX: re-run with --runs {MIN_RUNS}, or clear Citation Rate and set "
                "Stability to 'single-sample, not a measurement'.")

    # 2. no rate rendered without its run count
    for r in payload.get("ai_visibility", []):
        if r.get("citation_rate") not in (None, "") and not str(r.get("runs") or "").strip():
            problems.append(
                f"AI Visibility: '{str(r.get('prompt'))[:44]}' has a Citation Rate with an empty "
                "Runs cell. A rate without its sample size becomes a wrong screenshot the moment "
                "it leaves this sheet.\n    FIX: populate Runs.")

    # 3. tier order
    findings = payload.get("findings", [])
    week = [f for f in findings if str(f.get("priority", "")).lower() == "this week"]
    for i, f in enumerate(week):
        ft = _num(f.get("tier"))
        for later in week[i + 1:]:
            lt = _num(later.get("tier"))
            if ft is not None and lt is not None and lt < ft:
                problems.append(
                    f"Findings: tier {int(ft)} '{str(f.get('finding'))[:40]}' is ranked above tier "
                    f"{int(lt)} '{str(later.get('finding'))[:40]}'.\n"
                    "    A failure at a lower tier invalidates the work above it - rewriting pages "
                    "for extraction on a site whose robots.txt blocks the retrieval bots is "
                    "polishing something no engine may fetch.\n    FIX: reorder so lower tiers "
                    "come first.")
                break

    # 4. no link-quality claim without a named source
    for m in payload.get("mentions", []):
        if str(m.get("type", "")).lower() != "link-prospect":
            continue
        blob = " ".join(_cell(v) for v in m.values()).lower()
        if any(t in blob for t in (" dr ", "dr:", "domain rating", "domain authority", " da ",
                                   "toxicity", "toxic score", "traffic estimate")):
            if not str(m.get("source") or "").strip():
                problems.append(
                    f"Mentions: link-prospect '{str(m.get('platform_or_url'))[:44]}' carries a "
                    "DR/DA/traffic/toxicity figure with no named source.\n"
                    "    No free backlink index exists, so an unattributed number here was "
                    "invented.\n    FIX: name the tool it came from, or remove the number and "
                    "call this a prospect list rather than a qualified one.")

    # 5. no pass/fail on a not-connected source
    for r in payload.get("audit", []):
        src = str(r.get("source", "")).lower()
        obs = str(r.get("observed", "")).lower()
        if r.get("verdict") in ("pass", "fail") and (
                any(t in src for t in NOT_CONNECTED_SOURCES) or "not connected" in obs):
            problems.append(
                f"Authority Audit: '{r.get('check')}' has verdict {r.get('verdict')} while its "
                "source is not connected.\n    FIX: set the verdict to 'unknown' and put the "
                "export steps in Evidence. A guess dressed as a measurement is the one thing an "
                "audit cannot afford.")

    # 6. no evidence-free finding
    for f in findings:
        if not str(f.get("evidence") or "").strip():
            problems.append(
                f"Findings: '{str(f.get('finding'))[:50]}' has no evidence.\n"
                "    FIX: attach the measurement, or drop the finding. A claim with nothing to "
                "point at is an opinion the client cannot check.")

    # 7. no more than five 'this week' findings
    if len(week) > MAX_THIS_WEEK:
        problems.append(
            f"Findings: {len(week)} 'this week' items; the maximum is {MAX_THIS_WEEK}.\n"
            "    Three beat forty. An audit naming everything is the standard output of an "
            "automated tool and it is why tool exports do not sell.\n"
            "    FIX: demote all but the top five.")

    # vocabulary
    for r in payload.get("audit", []):
        if r.get("verdict") not in VALID_VERDICT:
            problems.append(f"Authority Audit: verdict {r.get('verdict')!r} is not one of "
                            f"{sorted(VALID_VERDICT)}.")
    for f in findings:
        p = str(f.get("priority", "")).lower()
        if p and p not in VALID_PRIORITY:
            problems.append(f"Findings: priority {f.get('priority')!r} is not one of "
                            f"{sorted(VALID_PRIORITY)}.")
    return problems


def warnings_for(payload: dict) -> list[str]:
    w = []
    if any(str(r.get("check_id", "")).startswith("local.") and r.get("observed") == "applicable"
           for r in payload.get("audit", [])) and not payload.get("local"):
        w.append("local.applicable passed but the Local tab is empty.")
    if not payload.get("ai_visibility"):
        w.append("No AI Visibility rows. The report's section 4 must read 'not sampled', which is "
                 "a different finding from 'not cited'.")
    return w


# ------------------------------------------------------------------ from results

def from_results(*results: dict) -> dict:
    """Route script output into tabs. Findings is deliberately left empty: auto-promoting every
    fail produces exactly the forty-item export invariant 7 blocks."""
    payload: dict = {k: [] for _, (k, _) in TABS.items()}
    for res in results:
        if not res:
            continue
        for c in res.get("checks", []):
            payload["audit"].append({
                "tier": c.get("tier"), "area": c.get("area"), "check": c.get("check_id"),
                "observed": c.get("observed"), "threshold": c.get("threshold"),
                "verdict": c.get("verdict"), "source": c.get("source"),
                "evidence": str(c.get("evidence") or "")[:EVIDENCE_MAX],
                "check_id": c.get("check_id"),
            })
            if str(c.get("check_id", "")).startswith("entity."):
                payload["entity"].append({
                    "signal": c.get("check_id"), "identifier": "",
                    "value": _cell(c.get("observed")), "source": c.get("source"),
                    "status": {"pass": "present", "fail": "missing", "review": "inconsistent",
                               "unknown": "unknown"}.get(c.get("verdict"), "unknown"),
                    "action": str(c.get("evidence") or "")[:400]})
            if str(c.get("check_id", "")).startswith("local."):
                payload["local"].append({
                    "signal": c.get("check_id"), "observed": _cell(c.get("observed")),
                    "threshold": c.get("threshold"), "surface": "map pack",
                    "verdict": c.get("verdict"),
                    "action": str(c.get("evidence") or "")[:400]})
        for m in res.get("mentions", []):
            payload["mentions"].append({
                "type": "linked-mention" if m.get("linked") else "unlinked-mention",
                "platform_or_url": m.get("url"), "where": m.get("host"),
                "snippet": m.get("snippet"), "linked": m.get("linked"),
                "description_used": "", "action": "" if m.get("linked") else "reclaim: ask for a link"})
        for name, url in (res.get("platforms") or {}).items():
            payload["mentions"].append({
                "type": "platform-presence", "platform_or_url": name, "where": url,
                "snippet": "", "linked": True, "description_used": "", "action": ""})
        for s in res.get("summary", []):
            stab = (f"cited:{s.get('stability_cited')} named:{s.get('stability_named')} "
                    f"first:{s.get('stability_first')}")
            payload["ai_visibility"].append({
                "prompt": s.get("prompt"), "intent": "", "engine": s.get("engine"),
                "runs": s.get("runs_ok"), "cited_n": s.get("cited_runs"),
                "citation_rate": s.get("citation_rate"), "stability": stab,
                "brand_named_without_link": max((s.get("named_runs") or 0) - (s.get("cited_runs") or 0), 0),
                "competitors_cited": s.get("competitors_cited"),
                "cited_urls": s.get("cited_urls"), "ranks_top_10": "",
                "sampled": res.get("generated_at", ""),
                "cost_usd": (res.get("cost") or {}).get("estimated_usd", "")})
    return payload


# ------------------------------------------------------------------ writing

def _rows_for(tab: str, payload: dict) -> list[list[str]]:
    key, headers = TABS[tab]
    out = []
    for item in payload.get(key, []):
        out.append([_cell(item.get(_key(h), "")) for h in headers])
    return out


def _write_rows(sheets, sid: str, tab: str, headers: list[str], rows: list[list[str]]) -> None:
    """Chunk by serialized length, not row count: 25 rows x 2000 chars of evidence is 50KB and
    gws dies with WinError 206. seo-technical learned this on a real 112-row audit."""
    sheets.update_range(sid, f"'{tab}'!A1", [headers])
    if not rows:
        return
    start, buf, blen = 2, [], 0
    for r in rows:
        rl = len(json.dumps(r, ensure_ascii=False))
        if buf and blen + rl > CLI_BUDGET:
            sheets.update_range(sid, f"'{tab}'!A{start}", buf)
            start += len(buf)
            buf, blen = [], 0
        buf.append(r)
        blen += rl
    if buf:
        sheets.update_range(sid, f"'{tab}'!A{start}", buf)


def push(payload: dict, title: str) -> str:
    import sheets
    sid, first_tab, _ = sheets.create_spreadsheet(title)
    names = list(TABS)
    reqs = [{"updateSheetProperties": {"properties": {"sheetId": 0, "title": names[0]},
                                       "fields": "title"}}]
    reqs += [{"addSheet": {"properties": {"title": n}}} for n in names[1:]]
    sheets.batch_update(sid, reqs)

    fmt = []
    for tab in names:
        key, headers = TABS[tab]
        _write_rows(sheets, sid, tab, headers, _rows_for(tab, payload))
        gid = sheets.get_gid(sid, tab)
        fmt += [
            {"repeatCell": {
                "range": {"sheetId": gid, "startRowIndex": 0, "endRowIndex": 1},
                "cell": {"userEnteredFormat": {
                    "textFormat": {"bold": True},
                    "backgroundColor": {"red": 0.91, "green": 0.91, "blue": 0.91}}},
                "fields": "userEnteredFormat(textFormat,backgroundColor)"}},
            {"updateSheetProperties": {
                "properties": {"sheetId": gid,
                               "gridProperties": {"frozenRowCount": 1, "frozenColumnCount": 1}},
                "fields": "gridProperties(frozenRowCount,frozenColumnCount)"}},
        ]
    sheets.batch_update(sid, fmt)
    return f"https://docs.google.com/spreadsheets/d/{sid}/edit"


# ------------------------------------------------------------------ selftest

def _selftest() -> None:
    print("push_sheet selftest")

    ok = {"audit": [{"tier": 1, "area": "Retrievability", "check": "ai.llms_txt",
                     "observed": "absent", "threshold": "-", "verdict": "pass",
                     "source": "course/40", "evidence": "correctly absent"}],
          "findings": [{"priority": "this week", "tier": 1, "area": "Retrievability",
                        "finding": "OAI-SearchBot disallowed", "evidence": "robots.txt line 4",
                        "fix": "remove the disallow", "expected_effect": "eligible for citation",
                        "effort": "5 min", "owner": "dev"}],
          "ai_visibility": [{"prompt": "p", "engine": "chatgpt", "runs": 3, "cited_n": 2,
                             "citation_rate": 0.667, "stability": "cited:unstable"}],
          "entity": [], "mentions": [], "local": []}
    assert validate(ok) == [], validate(ok)
    print("  ok  a clean payload validates")

    # 1
    bad = json.loads(json.dumps(ok))
    bad["ai_visibility"][0]["runs"] = 1
    p = validate(bad)
    assert p and "34.8%" in p[0] and "1.5%" in p[0], p
    print("  ok  inv1: rate from 1 run blocked, message carries the variance split")

    # 2
    bad = json.loads(json.dumps(ok))
    bad["ai_visibility"][0]["runs"] = ""
    assert any("empty Runs" in x for x in validate(bad))
    print("  ok  inv2: rate without a run count blocked")

    # 3
    bad = json.loads(json.dumps(ok))
    bad["findings"] = [
        {"priority": "this week", "tier": 4, "area": "Extractability", "finding": "add quotes",
         "evidence": "0 quotes"},
        {"priority": "this week", "tier": 1, "area": "Retrievability", "finding": "bot blocked",
         "evidence": "robots.txt"}]
    assert any("ranked above tier" in x for x in validate(bad)), validate(bad)
    print("  ok  inv3: tier-4 fix above a tier-1 failure blocked")

    # 4
    bad = json.loads(json.dumps(ok))
    bad["mentions"] = [{"type": "link-prospect", "platform_or_url": "x.com",
                        "where": "DR 62 domain rating", "source": ""}]
    assert any("invented" in x for x in validate(bad)), validate(bad)
    bad["mentions"][0]["source"] = "Ahrefs, 2026-08-09"
    assert not any("invented" in x for x in validate(bad))
    print("  ok  inv4: unattributed DR blocked, named source passes")

    # 5
    bad = json.loads(json.dumps(ok))
    bad["audit"] = [{"tier": 8, "area": "Measurement", "check": "measure.gsc_connected",
                     "observed": "not connected", "threshold": "-", "verdict": "pass",
                     "source": "Search Console", "evidence": "e"}]
    assert any("not connected" in x for x in validate(bad))
    print("  ok  inv5: pass on a not-connected source blocked")

    # 6
    bad = json.loads(json.dumps(ok))
    bad["findings"][0]["evidence"] = ""
    assert any("no evidence" in x for x in validate(bad))
    print("  ok  inv6: evidence-free finding blocked")

    # 7
    bad = json.loads(json.dumps(ok))
    bad["findings"] = [dict(bad["findings"][0], tier=1, finding=f"f{i}") for i in range(6)]
    assert any("maximum is 5" in x for x in validate(bad))
    print("  ok  inv7: six 'this week' findings blocked")

    # forced single-sample must drop the rate
    forced = json.loads(json.dumps(ok))
    forced["ai_visibility"][0].update(runs=1, citation_rate=None,
                                      stability="single-sample, not a measurement")
    assert validate(forced) == [], validate(forced)
    print("  ok  single sample with no rate + honest stability label validates")

    # from_results leaves Findings empty and routes rows
    res = {"checks": [{"check_id": "entity.wikidata_qid", "area": "Entity", "tier": 2,
                       "observed": "Q1", "threshold": "-", "verdict": "pass",
                       "source": "course/40", "evidence": "e"}], "generated_at": "now"}
    pl = from_results(res)
    assert pl["findings"] == [] and len(pl["audit"]) == 1 and len(pl["entity"]) == 1
    print("  ok  from_results routes rows and leaves Findings empty")

    # header -> key coercion matches the sheet
    assert _key("Cited (n)") == "cited_n" and _key("Brand Named Without Link") == "brand_named_without_link"
    for tab, (_, headers) in TABS.items():
        assert len(set(headers)) == len(headers), tab
    print("  ok  header coercion and unique columns")
    print("ALL PASS")


def main() -> None:
    ap = argparse.ArgumentParser(description="Write the Authority and AI Visibility sheet.")
    ap.add_argument("--payload")
    ap.add_argument("--from-results", nargs="*", default=[])
    ap.add_argument("--title")
    ap.add_argument("--validate-only", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        _selftest()
        return

    if a.payload:
        payload = json.loads(Path(a.payload).read_text(encoding="utf-8"))
    elif a.from_results:
        payload = from_results(*[json.loads(Path(p).read_text(encoding="utf-8"))
                                 for p in a.from_results])
    else:
        raise SystemExit("need --payload or --from-results")

    problems = validate(payload)
    for w in warnings_for(payload):
        print(f"WARNING: {w}", file=sys.stderr)
    if problems:
        print(f"{len(problems)} blocking problem(s):\n", file=sys.stderr)
        for p in problems:
            print(f"  - {p}\n", file=sys.stderr)
        if not a.force:
            raise SystemExit("refusing to write. fix the above, or pass --force if you have a reason.")
        print("--force: writing anyway.", file=sys.stderr)
    else:
        print("validation: clean", file=sys.stderr)

    if a.out:
        Path(a.out).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"wrote {a.out}", file=sys.stderr)
    if a.validate_only:
        return
    if not a.title:
        raise SystemExit("--title required to write")
    print(push(payload, a.title))


if __name__ == "__main__":
    main()

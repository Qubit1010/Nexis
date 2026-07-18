"""Weekly Business Review engine.

Reads every available source, rolls up one ISO week, prints a text summary, and writes
a JSON snapshot the dashboard reads. Each source degrades gracefully -- a failing or
unconfigured source is marked unavailable, never crashes the run.

    python wbr.py                 # current week
    python wbr.py --week 2026-07-13
    python wbr.py --no-write      # summary only, don't write the snapshot
"""
import argparse
import datetime as dt
import json
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
import weekutil
from sources import content, outreach, productivity, upwork, website


def _safe(fn, *a):
    try:
        return fn(*a)
    except Exception as e:
        traceback.print_exc()
        return {"available": False, "reason": f"error: {e}"}


def build(anchor):
    monday, sunday, week_key, label = weekutil.week_bounds(anchor)
    return {
        "week_key": week_key,
        "label": label,
        "start": monday.isoformat(),
        "end": sunday.isoformat(),
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "upwork": _safe(upwork.collect, monday, sunday),
        "outreach": _safe(outreach.collect, monday, sunday),
        "content": _safe(content.collect, monday, sunday),
        "productivity": _safe(productivity.collect, monday, sunday),
        "website": _safe(website.collect, monday, sunday),
    }


def _delta(cur, prev):
    if prev is None:
        return ""
    d = cur - prev
    return f" ({'+' if d >= 0 else ''}{d} vs last wk)"


def summary(r, prev=None):
    L = [f"\n=== Weekly Business Review — {r['label']}  ({r['start']} to {r['end']}) ==="]

    u = r["upwork"]
    if u.get("available"):
        pu = (prev or {}).get("upwork", {}) if prev else {}
        L.append("\nUPWORK")
        L.append(f"  Proposals: {u['proposals']}{_delta(u['proposals'], pu.get('proposals'))}"
                 f"   Connects: {u['connects']}   Spend: ${u['dollars']:.2f}   Boosted: {u['boosted']}")
        L.append(f"  Viewed: {u['viewed']} ({u['view_rate']}%)   "
                 f"Interviews: {u['interviews']} ({u['interview_rate']}%)   "
                 f"Hired: {u['hired']} ({u['hire_rate']}%)")
    else:
        L.append(f"\nUPWORK — unavailable: {u.get('reason')}")

    o = r["outreach"]
    if o.get("available"):
        t = o["totals"]
        L.append(f"\nOUTREACH  (sent {t['sent']}, added {t['added']})")
        for ch, v in o["channels"].items():
            if v.get("available"):
                extra = ""
                if v.get("by_type"):
                    extra = f"   [Founder {v['by_type']['Founder']} / Company {v['by_type']['Company']}]"
                L.append(f"  {ch.title():<10} sent {v['sent']:<4} added {v['added']}{extra}")
            else:
                L.append(f"  {ch.title():<10} unavailable: {v.get('reason')}")

    c = r["content"]
    if c.get("available"):
        L.append(f"\nCONTENT  ({c['totals']['posts']} posts via Buffer)")
        for plat, pv in c["platforms"].items():
            m = pv["metrics"]
            head = "  ".join(f"{k} {v:g}" for k, v in list(m.items())[:5])
            L.append(f"  {plat.title():<10} posts {pv['posts']:<3} {head}")
    else:
        L.append(f"\nCONTENT — unavailable: {c.get('reason')}")

    p = r["productivity"]
    if p.get("available"):
        L.append(f"\nPRODUCTIVITY  ({p['completed']} tasks completed)")
    else:
        L.append(f"\nPRODUCTIVITY — {p.get('reason')}")

    w = r["website"]
    L.append(f"\nWEBSITE — phase 2: {w.get('reason')}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="Weekly Business Review engine")
    ap.add_argument("--week", help="any date (YYYY-MM-DD) in the target week; default today")
    ap.add_argument("--no-write", action="store_true", help="print summary only, don't write snapshot")
    ap.add_argument("--json-only", action="store_true", help="print the rollup JSON, nothing else")
    args = ap.parse_args()

    anchor = args.week or dt.date.today().isoformat()
    r = build(anchor)

    if args.json_only:
        print(json.dumps(r, indent=2))
        return

    prev = None
    prev_path = config.SNAPSHOT_DIR / f"{weekutil.prev_week_key(r['week_key'])}.json"
    if prev_path.exists():
        prev = json.loads(prev_path.read_text(encoding="utf-8"))
    print(summary(r, prev))

    if not args.no_write:
        config.SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        out = config.SNAPSHOT_DIR / f"{r['week_key']}.json"
        out.write_text(json.dumps(r, indent=2), encoding="utf-8")
        print(f"\nsnapshot -> {out}")


if __name__ == "__main__":
    main()

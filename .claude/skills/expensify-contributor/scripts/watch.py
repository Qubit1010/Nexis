"""Find issues inside the work window, and detect when that window closes.

The whole strategy rests on one observation: an Expensify bounty issue is visible, with MelvinBot's
proposal already on it, for a median of about two days before the `Help Wanted` label makes it legal
to post a proposal. The moment the label lands, several contributors fire pre-written multi-kilobyte
proposals within one or two seconds. You cannot win that race by starting when the label appears.
You win it by having already done the work.

So this script answers two questions:
  --scan    which issues are in the window right now, and how much time is probably left
  --armed   have any issues I am tracking just opened for proposals

Usage:
  python watch.py --scan
  python watch.py --check 99215
  python watch.py --track 99215
  python watch.py --armed
  python watch.py --selftest
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import gh  # noqa: E402

STATE_DIR = Path(os.environ.get("EXPENSIFY_STATE_DIR", Path(__file__).parent.parent / "data"))
STATE_FILE = STATE_DIR / "pipeline.json"

# Measured 2026-08-23 across six issues: 4.3h minimum, ~44h median, 193h maximum.
# Used only to estimate urgency, never to justify waiting.
MEDIAN_WINDOW_HOURS = 44
FLOOR_WINDOW_HOURS = 4

PROPOSAL_RE = re.compile(r"^#{1,3} ?Proposal", re.IGNORECASE)


def _now():
    return datetime.now(timezone.utc)


def _parse(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _hours_since(ts):
    return (_now() - _parse(ts)).total_seconds() / 3600


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"tracked": {}}


def save_state(state):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def melvin_proposals(number):
    """Every MelvinBot proposal on the issue, oldest first.

    Melvin posts more than once when the reviewer asks it to try again, so the count matters as much
    as the content: a second or third attempt means the first was not accepted, which is a reviewer
    telling you out loud that the AI has not solved this one.
    """
    out = []
    for c in gh.comments(number):
        if c.get("user", {}).get("login") == "MelvinBot" and "Proposal" in (c.get("body") or ""):
            out.append((c.get("created_at"), c.get("body")))
    return out


def melvin_proposal(number):
    """The latest MelvinBot proposal, which is the one under review. (None, None) if it has not posted."""
    props = melvin_proposals(number)
    return props[-1] if props else (None, None)


def count_proposals(number):
    """Live *human* proposals, excluding withdrawn ones and excluding MelvinBot.

    Melvin is deliberately not counted as a rival. It proposes on effectively every issue, so
    including it would add a constant to every count while implying competition that is not there.
    Worse, an issue where Melvin has posted twice and no human has posted at all would read as "2
    rivals, crowded" when it is in fact wide open. Melvin is scored on its own signal instead.
    """
    n = 0
    for c in gh.comments(number):
        body = (c.get("body") or "").strip()
        if c.get("user", {}).get("login") == "MelvinBot":
            continue
        if PROPOSAL_RE.match(body) and "Duplicated proposal withdrawn" not in body:
            n += 1
    return n


def window_state(number):
    """Classify one issue against the work window."""
    iss = gh.issue(number)
    labels = gh.labels_of(iss)
    hw_at = gh.help_wanted_at(number)
    mel_at, mel_body = melvin_proposal(number)
    created = iss["created_at"]

    if hw_at:
        phase = "OPEN_FOR_PROPOSALS" if iss["state"] == "open" else "CLOSED"
        age_h = _hours_since(hw_at)
    elif "External" in labels or mel_at:
        phase = "WORK_WINDOW"
        age_h = _hours_since(created)
    else:
        phase = "NOT_IN_PIPELINE"
        age_h = _hours_since(created)

    remaining = round(MEDIAN_WINDOW_HOURS - age_h, 1) if phase == "WORK_WINDOW" else None

    return {
        "number": number,
        "title": iss["title"],
        "url": iss["html_url"],
        "phase": phase,
        "state": iss["state"],
        "labels": sorted(labels),
        "created_at": created,
        "help_wanted_at": hw_at,
        "melvin_proposal_at": mel_at,
        "melvin_proposal_chars": len(mel_body) if mel_body else 0,
        "hours_in_phase": round(age_h, 1),
        "estimated_hours_remaining": remaining,
        "proposal_count": count_proposals(number),
        "assignees": [a["login"] for a in iss.get("assignees", [])],
    }


def scan(limit=20):
    """Issues currently in the work window: External, no Help Wanted yet."""
    items = gh.search_issues(
        'repo:Expensify/App is:open is:issue label:External -label:"Help Wanted" sort:created-desc',
        per_page=limit,
    )
    rows = []
    for it in items:
        try:
            st = window_state(it["number"])
        except gh.GhError:
            raise
        except Exception as exc:  # one malformed issue should not kill the whole scan
            rows.append({"number": it["number"], "phase": "ERROR", "error": str(exc)})
            continue
        if st["phase"] == "WORK_WINDOW":
            rows.append(st)
    return rows


def print_scan(rows):
    if not rows:
        print("No issues currently in the work window.")
        print("That is a real answer, not a failure: Expensify produces only about 4 bounty issues a week.")
        return
    print("%d issue(s) in the work window (pre-Help-Wanted)\n" % len(rows))
    for r in sorted(rows, key=lambda x: x.get("hours_in_phase", 0), reverse=True):
        if r["phase"] == "ERROR":
            print("  #%s  ERROR: %s" % (r["number"], r["error"]))
            continue
        rem = r["estimated_hours_remaining"]
        urgency = "OVERDUE, could open any moment" if rem is not None and rem < 0 else "~%sh left (est.)" % rem
        print("  #%s  %s" % (r["number"], r["title"][:66]))
        print("       in window %sh | %s | rivals so far: %s" % (r["hours_in_phase"], urgency, r["proposal_count"]))
        print("       melvin: %s chars | %s" % (r["melvin_proposal_chars"], r["url"]))
        print("")
    print("The shortest window measured was %dh. These estimates are not promises." % FLOOR_WINDOW_HOURS)


def cmd_armed():
    """Report tracked issues whose window has closed. This is the fire signal."""
    state = load_state()
    tracked = state.get("tracked", {})
    if not tracked:
        print("Nothing tracked. Use --track <issue> once triage picks a target.")
        return 0
    fired = []
    for num in list(tracked):
        st = window_state(int(num))
        tracked[num]["last_checked"] = _now().isoformat()
        tracked[num]["phase"] = st["phase"]
        if st["phase"] == "OPEN_FOR_PROPOSALS":
            fired.append(st)
    save_state(state)
    if not fired:
        print("No tracked issue has opened yet. Still in the window:")
        for num, meta in tracked.items():
            print("  #%s  %s  (tracked %s)" % (num, meta.get("phase"), (meta.get("tracked_at") or "?")[:16]))
        return 0
    print("OPEN FOR PROPOSALS, post now:\n")
    for st in fired:
        print("  #%s  %s" % (st["number"], st["title"][:70]))
        print("       labelled %s (%sh ago)" % (st["help_wanted_at"], st["hours_in_phase"]))
        print("       rivals already posted: %s" % st["proposal_count"])
        print("       %s\n" % st["url"])
    if any(s["hours_in_phase"] > 6 for s in fired):
        print("Note: over six hours have passed on at least one of these. Rivals fire within seconds,")
        print("so a late post rarely wins on timing alone. It is still worth posting if your root cause")
        print("is genuinely different from everything already on the thread.")
    return 1


def _fmt_check(st):
    lines = [
        "#%s  %s" % (st["number"], st["title"]),
        "  phase           %s" % st["phase"],
        "  hours in phase  %s" % st["hours_in_phase"],
        "  help wanted at  %s" % (st["help_wanted_at"] or "not yet"),
        "  melvin proposal %s (%s chars)" % (st["melvin_proposal_at"] or "none", st["melvin_proposal_chars"]),
        "  rival proposals %s" % st["proposal_count"],
        "  assignees       %s" % (", ".join(st["assignees"]) or "none"),
        "  %s" % st["url"],
    ]
    if st["phase"] == "WORK_WINDOW":
        lines.append("  estimated hours remaining: %s (median-based; observed floor is 4h)" % st["estimated_hours_remaining"])
    return "\n".join(lines)


def selftest():
    """Check the window classifier against issues whose history is fixed and known."""
    failures = []

    # 98426 is settled history: labelled 2026-08-20T14:40:43Z, winner posted two seconds later.
    st = window_state(98426)
    if st["help_wanted_at"] != "2026-08-20T14:40:43Z":
        failures.append("98426 help_wanted_at was %s, expected 2026-08-20T14:40:43Z" % st["help_wanted_at"])
    if st["phase"] not in ("OPEN_FOR_PROPOSALS", "CLOSED"):
        failures.append("98426 phase was %s, expected OPEN_FOR_PROPOSALS or CLOSED" % st["phase"])
    if st["melvin_proposal_at"] is None:
        failures.append("98426 should have a MelvinBot proposal")
    if st["proposal_count"] < 10:
        failures.append("98426 counted %s live proposals, expected at least 10" % st["proposal_count"])

    # 98791 drew fourteen proposals and still had an unresolved reproduction question.
    st2 = window_state(98791)
    if st2["proposal_count"] < 8:
        failures.append("98791 counted %s live proposals, expected at least 8" % st2["proposal_count"])

    # The scanner must run cleanly and return only work-window issues.
    rows = scan(limit=8)
    for r in rows:
        if r.get("phase") not in ("WORK_WINDOW", "ERROR"):
            failures.append("scan returned #%s in phase %s, expected WORK_WINDOW" % (r["number"], r.get("phase")))

    if failures:
        print("SELFTEST FAILED")
        for f in failures:
            print("  - %s" % f)
        return 1
    print("SELFTEST PASSED")
    print("  window classifier verified against #98426 and #98791")
    print("  scan returned %d live work-window issue(s)" % len(rows))
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--scan", action="store_true", help="list issues currently in the work window")
    p.add_argument("--check", type=int, metavar="N", help="classify one issue")
    p.add_argument("--track", type=int, metavar="N", help="add an issue to the watchlist")
    p.add_argument("--untrack", type=int, metavar="N", help="remove an issue from the watchlist")
    p.add_argument("--armed", action="store_true", help="check whether any tracked issue has opened")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--json", action="store_true", help="machine-readable output")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()

    try:
        if a.selftest:
            return selftest()
        if a.check:
            st = window_state(a.check)
            print(json.dumps(st, indent=2) if a.json else _fmt_check(st))
            return 0
        if a.track:
            state = load_state()
            st = window_state(a.track)
            state.setdefault("tracked", {})[str(a.track)] = {
                "tracked_at": _now().isoformat(),
                "title": st["title"],
                "phase": st["phase"],
            }
            save_state(state)
            print("Tracking #%s (%s). Run --armed to check for the fire signal." % (a.track, st["phase"]))
            return 0
        if a.untrack:
            state = load_state()
            state.get("tracked", {}).pop(str(a.untrack), None)
            save_state(state)
            print("Untracked #%s." % a.untrack)
            return 0
        if a.armed:
            return cmd_armed()
        rows = scan(a.limit)
        if a.json:
            print(json.dumps(rows, indent=2))
        else:
            print_scan(rows)
        return 0
    except gh.GhError as exc:
        print("GitHub access failed: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

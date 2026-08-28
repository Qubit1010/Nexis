"""Score how winnable an Expensify bounty issue actually is.

Why score at all: there are only about four new bounty issues a week, and each draws eight to
seventeen proposals from contributors who have automated their posting. Working every issue is a
guaranteed loss because you would be perpetually late on all of them. Working one or two well-chosen
issues is the only shape of effort that has ever won this game for a newcomer.

The rubric is two hard gates plus six scored signals, deliberately the same shape as the Upwork job
triage rubric so there is one mental model for "is this worth bidding on" rather than two.

What the scores actually mean: these are proxies, not truth. The script can see that MelvinBot cited
no file and line, which usually means a shallow root cause; it cannot see whether the root cause is
correct. Treat a high score as "worth an hour of investigation", not "worth two days of work". The
decision to commit stays with the human after reading the issue.

Usage:
  python triage.py --scan
  python triage.py --issue 99215
  python triage.py --issue 99215 --json
  python triage.py --selftest
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import gh  # noqa: E402
import watch  # noqa: E402

# Thresholds calibrated against the live work-window distribution on 2026-08-23, where eleven issues
# scored between 2.4 and 5.4 under an earlier, badly weighted rubric. Treat these as ranking
# boundaries rather than laws of nature, and re-check them whenever _research/measurements.json is
# re-measured. The deeper point: with only about four issues a week and capacity for one or two, the
# job is to pick the best available issue, not to wait for one that clears an absolute bar.
PURSUE_THRESHOLD = 6.0
BORDERLINE_THRESHOLD = 4.0

# Areas where the fast-proposal crowd is thinner, measured by eye across the sampled issues: these
# need native debugging, a paid integration sandbox, or profiling work that does not fit a
# pre-written template.
LOW_CROWDING_PATTERNS = re.compile(
    r"sentry|crash|fabric|hybridapp|native|memory leak|performance|\bINP\b|profiling|"
    r"netsuite|quickbooks|\bxero\b|\bsage\b|accounting|reconcil|"
    r"deep ?link|websocket|onyx|migration|race condition",
    re.IGNORECASE,
)

# Signals that nobody has managed to reproduce the bug yet. This is the single best opportunity in
# the whole process: on issue 98791, fourteen proposals had landed and the reviewer was still asking
# for a reproduction three days later.
REPRO_TROUBLE = re.compile(
    r"can (?:anyone|you|someone) reproduce|unable to reproduce|cannot reproduce|can't reproduce|"
    r"couldn't reproduce|could not reproduce|not able to reproduce|no longer reproduc|"
    r"needs? reproduction|how (?:did|do) you reproduce",
    re.IGNORECASE,
)

PLATFORM_ONLY = re.compile(r"^\s*(?:\[\$\d+\]\s*)?(ios|android|mac ?os|desktop)\b[\s\-:]", re.IGNORECASE)
WEB_FRIENDLY = re.compile(r"\b(web|mweb|chrome|safari|firefox|browser)\b", re.IGNORECASE)

# A permalink pinned to a blob path with a line anchor is the tell that a proposal actually traced
# the code rather than describing the symptom back to you.
PERMALINK_WITH_LINES = re.compile(r"github\.com/Expensify/App/blob/[0-9a-f]{7,40}/\S+#L\d+")

# Hedging in MelvinBot's own proposal. Found live on issue 99208, where Melvin cited pinned lines
# (which the permalink check reads as a confident trace) while stating in the same paragraph that it
# "could not reproduce" the bug and was guessing at an edge case. Citing a line proves it read some
# code; it does not prove it found the cause. When Melvin says it is unsure, it is telling you the
# reviewer will need a human, which is a far stronger opening than the permalink check can see.
MELVIN_HEDGING = re.compile(
    r"could ?n[o']t reproduce|can ?n[o']t reproduce|unable to reproduce|not able to reproduce|"
    r"did not reproduce|most likely|i suspect|my best guess|appears to be|speculative|"
    r"without being able to|cannot confirm|could not verify|unable to verify|"
    r"i was unable|needs? (?:further )?investigation|hard to say",
    re.IGNORECASE)


def _c_plus_asking_for_repro(comments):
    """Did anyone on the thread say they could not reproduce it? Returns the quote if so."""
    for c in comments:
        body = c.get("body") or ""
        m = REPRO_TROUBLE.search(body)
        if m:
            author = c.get("user", {}).get("login", "?")
            start = max(0, m.start() - 60)
            return "%s: ...%s..." % (author, body[start:m.end() + 80].replace("\n", " ").strip())
    return None


def score_issue(number):
    st = watch.window_state(number)
    comments = gh.comments(number)
    labels = set(st["labels"])
    title = st["title"]
    _, melvin_body = watch.melvin_proposal(number)

    gates = []
    if st["phase"] == "WORK_WINDOW":
        gates.append(("in the work window", True, "pre-Help-Wanted, %sh in" % st["hours_in_phase"]))
    elif st["phase"] == "OPEN_FOR_PROPOSALS" and st["hours_in_phase"] <= 1:
        gates.append(("in the work window", True, "just opened %sh ago, still worth a fast entry" % st["hours_in_phase"]))
    else:
        gates.append(("in the work window", False,
                      "phase is %s (%sh). The preparation advantage is gone." % (st["phase"], st["hours_in_phase"])))

    blocking = {"Internal", "HOLD", "Not a priority", "Reviewing"} & labels
    contributor_assigned = [a for a in st["assignees"]]
    if blocking:
        gates.append(("open to external contributors", False, "carries blocking label(s): %s" % ", ".join(sorted(blocking))))
    else:
        gates.append(("open to external contributors", True,
                      "assignees are %s (reviewers, not the hired contributor)" % (", ".join(contributor_assigned) or "none")))

    passed_gates = all(g[1] for g in gates)

    signals = []

    # 1. Reproduction trouble is the strongest single opening in this whole process, so it carries
    #    the most weight. On issue 98791 fourteen proposals had landed and the reviewer was still
    #    asking for a reproduction three days later. Supplying one makes you the most useful person
    #    on the thread regardless of how fast anyone else posted.
    repro_quote = _c_plus_asking_for_repro(comments)
    if "Needs Reproduction" in labels:
        signals.append(("reproduction is contested", 3.0, 3.0, "carries the Needs Reproduction label"))
    elif repro_quote:
        signals.append(("reproduction is contested", 3.0, 3.0, "someone on the thread cannot reproduce it: %s" % repro_quote[:160]))
    else:
        signals.append(("reproduction is contested", 0.0, 3.0, "nobody has raised a reproduction problem"))

    # 2. Is MelvinBot beatable? Its proposal is reviewed first, so a shallow one is your opening.
    #    A pinned file-and-line citation is the tell that it genuinely traced the code.
    melvin_all = watch.melvin_proposals(number)
    hedge = MELVIN_HEDGING.search(melvin_body) if melvin_body else None
    retries = len(melvin_all)
    if not melvin_body:
        signals.append(("Melvin's root cause", 2.0, 2.0, "no AI proposal to beat yet, unusual and good"))
    elif hedge:
        signals.append(("Melvin's root cause", 2.0, 2.0,
                        "Melvin hedges its own latest proposal (\"%s\"), so the reviewer will need a "
                        "human regardless of what it cited" % hedge.group(0)))
    elif retries > 1:
        signals.append(("Melvin's root cause", 1.7, 2.0,
                        "Melvin has posted %d proposals, so the reviewer rejected at least one and "
                        "asked it to try again" % retries))
    elif PERMALINK_WITH_LINES.search(melvin_body):
        signals.append(("Melvin's root cause", 0.3, 2.0, "cites pinned file and line, a real trace and hard to beat head-on"))
    elif len(melvin_body) < 2500:
        signals.append(("Melvin's root cause", 2.0, 2.0, "short (%d chars) and cites no line, likely shallow" % len(melvin_body)))
    else:
        signals.append(("Melvin's root cause", 1.5, 2.0, "long but cites no pinned line, worth checking for a wrong assumption"))

    # 3. Crowding. The fast-proposal crowd concentrates on plain frontend state bugs.
    haystack = "%s %s" % (title, " ".join(sorted(labels)))
    if LOW_CROWDING_PATTERNS.search(haystack):
        hit = LOW_CROWDING_PATTERNS.search(haystack).group(0)
        signals.append(("area crowding", 2.0, 2.0, "matches a lower-competition area (%s)" % hit))
    else:
        signals.append(("area crowding", 0.8, 2.0, "looks like a mainstream frontend bug, the most contested kind"))

    # 4. Rivals already on the board. Every proposal already posted dilutes whatever opening exists.
    n = st["proposal_count"]
    if n == 0:
        rival_pts, rival_note = 2.0, "no rival proposals yet"
    elif n <= 3:
        rival_pts, rival_note = 1.5, "%d rival proposal(s), still early" % n
    elif n <= 8:
        rival_pts, rival_note = 0.7, "%d rival proposals, crowded" % n
    else:
        rival_pts, rival_note = 0.0, "%d rival proposals, saturated" % n
    signals.append(("rival proposals", rival_pts, 2.0, rival_note))

    # 5. Can it be reproduced without a Mac? This is an Aleem-specific constraint until Mac access
    #    is arranged, and it is a hard practical limit rather than a preference.
    m = PLATFORM_ONLY.match(title)
    if m and m.group(1).lower().replace(" ", "") in ("ios", "macos", "desktop"):
        signals.append(("platform reach", 0.0, 1.0, "titled as %s-only, needs a Mac to reproduce and test" % m.group(1)))
    elif WEB_FRIENDLY.search(title):
        signals.append(("platform reach", 1.0, 1.0, "web or mWeb, reproducible on the current setup"))
    else:
        signals.append(("platform reach", 0.7, 1.0, "platform not stated in the title, check the issue body before committing"))

    total = round(sum(s[1] for s in signals), 2)
    possible = round(sum(s[2] for s in signals), 2)

    # Time left is deliberately NOT scored. It answers "when must I work on this", which is a
    # scheduling question, not "is this worth working on". An earlier version subtracted points from
    # issues that had sat in the window a long time, which is exactly backwards: a long-sitting issue
    # is about to open, so it is more urgent, not less valuable. The median is also a weak predictor
    # given the observed range of 4 to 193 hours, so it is reported as a flag and never as a score.
    rem = st["estimated_hours_remaining"]
    if rem is None:
        urgency = {"level": "CLOSED", "note": "the window has already closed"}
    elif rem < 0:
        urgency = {"level": "IMMINENT",
                   "note": "past the %dh median by %.1fh, could open at any moment" % (watch.MEDIAN_WINDOW_HOURS, -rem)}
    elif rem < 12:
        urgency = {"level": "SOON", "note": "roughly %.1fh left on the median, work today" % rem}
    else:
        urgency = {"level": "COMFORTABLE", "note": "roughly %.1fh left on the median" % rem}

    if not passed_gates:
        verdict, reason = "SKIP", "failed a hard gate"
    elif total >= PURSUE_THRESHOLD:
        verdict, reason = "PURSUE", "scored %.1f of %.1f" % (total, possible)
    elif total >= BORDERLINE_THRESHOLD:
        verdict, reason = "BORDERLINE", "scored %.1f of %.1f, read the issue before deciding" % (total, possible)
    else:
        verdict, reason = "SKIP", "scored %.1f of %.1f" % (total, possible)

    return {
        "urgency": urgency,
        "number": number,
        "title": title,
        "url": st["url"],
        "phase": st["phase"],
        "verdict": verdict,
        "reason": reason,
        "score": total,
        "possible": possible,
        "gates": [{"gate": g[0], "passed": g[1], "note": g[2]} for g in gates],
        "signals": [{"signal": s[0], "points": s[1], "max": s[2], "note": s[3]} for s in signals],
        "rival_proposals": st["proposal_count"],
        "hours_in_phase": st["hours_in_phase"],
    }


def fmt(r):
    out = ["#%s  %s" % (r["number"], r["title"][:70]),
           "  %s  (%s)" % (r["verdict"], r["reason"]),
           "  urgency: %s, %s" % (r["urgency"]["level"], r["urgency"]["note"]),
           "  %s" % r["url"],
           "",
           "  Hard gates:"]
    for g in r["gates"]:
        out.append("    [%s] %s: %s" % ("pass" if g["passed"] else "FAIL", g["gate"], g["note"]))
    out.append("")
    out.append("  Signals (%.1f / %.1f):" % (r["score"], r["possible"]))
    for s in r["signals"]:
        out.append("    %.1f/%.1f  %-26s %s" % (s["points"], s["max"], s["signal"], s["note"]))
    out.append("")
    out.append("  These are proxies. The script can see that Melvin cited no line; it cannot see")
    out.append("  whether Melvin is right. A high score means the issue is worth an hour of")
    out.append("  investigation, not that two days of work is already justified.")
    return "\n".join(out)


def selftest():
    """Verify the rubric discriminates on issues whose outcomes are already known."""
    failures = []

    # 98791: fourteen proposals, and the reviewer was still asking for a reproduction days later.
    # The reproduction signal must fire here, because this is exactly the opening the skill targets.
    r = score_issue(98791)
    repro = next(s for s in r["signals"] if s["signal"] == "reproduction is contested")
    if repro["points"] < 2.5:
        failures.append("98791 should register contested reproduction, scored %.1f (%s)" % (repro["points"], repro["note"]))
    crowd = next(s for s in r["signals"] if s["signal"] == "area crowding")
    if crowd["points"] < 2.0:
        failures.append("98791 is a HybridApp Fabric crash and should score as a low-crowding area, got %.1f" % crowd["points"])

    # 98426: the winning proposal was a pinned-permalink trace, so Melvin's own proposal there should
    # not be scored as trivially beatable if it also cites lines. Either way the window is closed,
    # so the gate must fail and the verdict must be SKIP. A rubric that still says PURSUE on a
    # closed window would send you into a race that ended days ago.
    r2 = score_issue(98426)
    gate = next(g for g in r2["gates"] if g["gate"] == "in the work window")
    if gate["passed"]:
        failures.append("98426's window closed long ago, the gate should fail")
    if r2["verdict"] != "SKIP":
        failures.append("98426 should be SKIP, got %s" % r2["verdict"])

    # The scorer must run over the live scan without raising.
    rows = watch.scan(limit=5)
    for row in rows[:2]:
        scored = score_issue(row["number"])
        if scored["verdict"] not in ("PURSUE", "BORDERLINE", "SKIP"):
            failures.append("unexpected verdict %s on #%s" % (scored["verdict"], row["number"]))

    if failures:
        print("SELFTEST FAILED")
        for f in failures:
            print("  - %s" % f)
        return 1
    print("SELFTEST PASSED")
    print("  reproduction signal fires on #98791 (the archetypal opening)")
    print("  closed-window gate correctly rejects #98426")
    print("  scored %d live issue(s) without error" % min(2, len(rows)))
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--issue", type=int, help="score one issue")
    p.add_argument("--scan", action="store_true", help="score every issue currently in the work window")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--json", action="store_true")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()

    try:
        if a.selftest:
            return selftest()
        if a.issue:
            r = score_issue(a.issue)
            print(json.dumps(r, indent=2) if a.json else fmt(r))
            return 0
        if a.scan:
            rows = watch.scan(a.limit)
            scored = [score_issue(r["number"]) for r in rows]
            scored.sort(key=lambda x: x["score"], reverse=True)
            if a.json:
                print(json.dumps(scored, indent=2))
                return 0
            if not scored:
                print("Nothing in the work window to score right now.")
                return 0
            print("Ranked %d issue(s) in the work window:\n" % len(scored))
            for r in scored:
                print("  %-11s %.1f/%.1f  %-11s #%s  %s" % (
                    r["verdict"], r["score"], r["possible"], r["urgency"]["level"], r["number"], r["title"][:48]))
            print("")
            print("Pursue at %.1f or above; %.1f to %.1f is worth reading before deciding." % (
                PURSUE_THRESHOLD, BORDERLINE_THRESHOLD, PURSUE_THRESHOLD))
            print("With roughly four issues a week and capacity for one or two, the job is to take the")
            print("best available issue that clears the borderline, not to hold out for a perfect one.")
            print("Run --issue N for the breakdown.")
            return 0
        p.print_help()
        return 0
    except gh.GhError as exc:
        print("GitHub access failed: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

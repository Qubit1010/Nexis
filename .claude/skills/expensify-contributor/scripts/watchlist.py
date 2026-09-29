"""A standing review list of new Expensify bounty issues, refreshed twice a day.

Why this exists: by the time `Help Wanted` goes up, most issues are already decided. Measured on
2026-09-29, all 25 open Help Wanted issues were either approved, stalled on backend work, closing as
not reproducible, or carrying 8 to 23 proposals. The only winnable window is the day or two before
the label, so the job is to see every new issue early, drop the dead ones fast, and keep watching
the rest until one opens.

Each refresh pulls every External issue created in the last N hours, re-checks everything already on
the list, grades each one, and records what changed since the previous refresh (new proposals, the
label landing, a reviewer approving someone, a reviewer comment, a close). The grade is a set of
named reasons, never a bare score, so every verdict can be checked by reading the issue.

Usage:
  python watchlist.py --refresh              # discover last 24h + re-check tracked, write report
  python watchlist.py --refresh --hours 48
  python watchlist.py --show                 # print the last report without calling GitHub
  python watchlist.py --note 102503 "traced to SearchUIUtils, repro'd on staging"
  python watchlist.py --pin 102528           # keep watching even if the rules say drop
  python watchlist.py --drop 102490 "needs a paid NetSuite sandbox"
  python watchlist.py --selftest

State lives in data/watchlist.json and the report in data/watchlist.md, both gitignored.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import gh  # noqa: E402
from triage import MELVIN_HEDGING, PERMALINK_WITH_LINES  # noqa: E402

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "watchlist.json"
REPORT_FILE = DATA / "watchlist.md"
DRAFTS = DATA / "drafts"
PKT = timezone(timedelta(hours=5))

# Dropped issues stay visible this long so a wrong drop can be caught and pinned back.
KEEP_DROPPED_DAYS = 7
# Live human proposals after Help Wanted at which an issue is treated as saturated.
CROWDED = 8

AUTOMATION = {"melvin-bot", "github-actions", "applause-bot", "OSBotify", "MelvinBot"}
PROPOSAL_RE = re.compile(r"^\s*#{1,3} ?Proposal", re.IGNORECASE)
APPROVED_RE = re.compile(r"🎀\s*👀\s*🎀")
HIRED_RE = re.compile(r"(?i)an offer has been sent|you have been hired|📣 .{0,60}🎉")
# The regression rule: a bug inside a merged PR's 7-day window goes back to that PR's author.
REGRESSION_RE = re.compile(
    r"(?i)author of that PR is assigned|since (?:he|she|they) authored|regression period is still running")
NOT_A_BUG_RE = re.compile(
    r"(?i)expected behaviou?r|not a bug|working as (?:intended|expected)|can close (?:this|the issue)|close (?:this|it) as")
REPRO_WANTED_RE = re.compile(
    r"(?i)can(?:'t| ?not) reproduce|unable to reproduce|couldn'?t reproduce|can (?:anyone|someone|you) reproduce|"
    r"please (?:attach|share) (?:a )?repro")
CONFIDENCE_RE = re.compile(r"(?i)confidence:\**\s*(low|medium|high)")
BOUNTY_RE = re.compile(r"\[\$(\d+)\]")
# Melvin sometimes posts an "Issue Analysis" instead of a proposal, concluding the fix is not in App.
# Seen on 102520 (TriNet): those issues tend to go to an internal engineer rather than to Help Wanted.
MELVIN_BACKEND_RE = re.compile(r"(?i)backend|internal engineer|outside the App repo|no (?:recommended )?fix in App")
# The same conclusion inside a real proposal. Seen on 102503: "No App code change is needed ... that is a
# new backend feature, not an App fix." Narrower than the analysis pattern, since proposals mention the
# backend in passing all the time.
MELVIN_NO_APP_FIX_RE = re.compile(
    r"(?i)no App (?:code )?change is needed|new backend feature|needs changes outside the App repo|"
    r"escalate to an internal engineer")
# The skill forbids testing against Concierge: it reaches real people.
CONCIERGE_RE = re.compile(r"(?i)\bconcierge\b")
# Melvin's hedge is worth nothing when it only says it could not reproduce inside its sandbox and the
# trace itself is precise. Seen on 102443: seven pinned lines and a correct one-line cause, hedged only
# because a Smart Limit card needs backend setup. Below this many pins a hedge still counts as an opening.
PRECISE_TRACE_PINS = 5
# Reproducing these needs a live third-party account the tester has and Aleem does not.
INTEGRATION_RE = re.compile(r"(?i)\b(trinet|zenefits|gusto|netsuite|quickbooks|qbo|qbd|xero|sage intacct|intacct|"
                            r"certinia|bill\.com)\b")
CHECKED_RE = re.compile(r"^\s*-\s*\[[xX]\]\s*(.+?)\s*$", re.MULTILINE)


def _now():
    return datetime.now(timezone.utc)


def _parse(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _pkt(ts):
    return _parse(ts).astimezone(PKT).strftime("%b %d %H:%M")


def _login(c):
    return (c.get("user") or {}).get("login") or "?"


def _is_automation(login):
    return login in AUTOMATION or login.endswith("[bot]")


def _unquote(body):
    return "\n".join(ln for ln in (body or "").splitlines() if not ln.lstrip().startswith(">"))


# ---------------------------------------------------------------------------------------------
# Reading GitHub
# ---------------------------------------------------------------------------------------------

def _as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def fetch(number):
    """Issue, every comment and every timeline event, in three paginated calls."""
    iss = gh.issue(number)
    comments = _as_list(gh.api("repos/%s/issues/%d/comments?per_page=100" % (gh.REPO, number), jq=".[]", paginate=True))
    events = _as_list(gh.api("repos/%s/issues/%d/timeline?per_page=100" % (gh.REPO, number), jq=".[]", paginate=True))
    return iss, [c for c in comments if isinstance(c, dict)], [e for e in events if isinstance(e, dict)]


def discover(hours):
    since = (_now() - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    items = gh.search_issues("repo:%s is:issue is:open label:External created:>=%s sort:created-desc" % (gh.REPO, since),
                             per_page=100)
    return [it["number"] for it in items]


# ---------------------------------------------------------------------------------------------
# Grading
# ---------------------------------------------------------------------------------------------

def platforms(body):
    """Which platforms the reporter ticked, reduced to what Aleem can actually test on Windows."""
    ticked = [t.lower() for t in CHECKED_RE.findall(body or "")]
    ticked = [t for t in ticked if any(p in t for p in ("android", "ios", "windows", "macos", "mweb"))]
    if not ticked:
        return "unknown", []
    # iOS mWeb is Safari on an iPhone, which a Windows browser does not reproduce, so it is not "web".
    web = any(t.startswith(("windows", "macos: chrome", "android: mweb")) for t in ticked)
    android_app = any(t.startswith("android: app") for t in ticked)
    ios_only = all(t.startswith("ios") or "safari" in t for t in ticked)
    if web:
        reach = "web"
    elif android_app:
        reach = "android-app"
    elif ios_only:
        reach = "ios-only"
    else:
        reach = "unknown"
    return reach, ticked


def snapshot(iss, comments, events):
    """Everything the grade and the change log need, as plain data."""
    labels = sorted(l["name"] for l in iss.get("labels", []))
    assignees = [a["login"] for a in iss.get("assignees", [])]
    hw_at = None
    for ev in events:
        if ev.get("event") == "labeled" and (ev.get("label") or {}).get("name") == "Help Wanted":
            hw_at = ev.get("created_at")
    body = iss.get("body") or ""

    melvin = [c for c in comments if _login(c) == "MelvinBot" and PROPOSAL_RE.search(c.get("body") or "")]
    analyses = [c.get("body") or "" for c in comments
                if _login(c) == "MelvinBot" and "Issue Analysis" in (c.get("body") or "")]
    latest = melvin[-1].get("body") if melvin else ""
    conf = CONFIDENCE_RE.search(latest or "")

    humans, early, approved, hired, regression, not_a_bug, repro_wanted = 0, 0, False, False, False, [], []
    reviewer_comments, reviewer_to_melvin = [], 0
    for c in comments:
        login, text = _login(c), c.get("body") or ""
        plain = _unquote(text)
        if APPROVED_RE.search(text):
            approved = True
        if HIRED_RE.search(text):
            hired = True
        if REGRESSION_RE.search(text):
            regression = True
        if login == "MelvinBot" or _is_automation(login):
            continue
        if PROPOSAL_RE.search(text) and "Duplicated proposal withdrawn" not in text:
            if hw_at and c["created_at"] >= hw_at:
                humans += 1
            else:
                early += 1
        if login in assignees:
            reviewer_comments.append({"id": c["id"], "at": c["created_at"], "by": login,
                                      "text": re.sub(r"\s+", " ", plain)[:220]})
            if "@MelvinBot" in text:
                reviewer_to_melvin += 1
            if NOT_A_BUG_RE.search(plain):
                not_a_bug.append(login)
        if REPRO_WANTED_RE.search(plain) and login in assignees:
            repro_wanted.append(login)
    if REGRESSION_RE.search(body):
        regression = True

    reach, ticked = platforms(body)
    m = BOUNTY_RE.search(iss["title"])
    return {
        "number": iss["number"],
        "title": BOUNTY_RE.sub("", iss["title"]).strip(),
        "url": iss["html_url"],
        "bounty": int(m.group(1)) if m else None,
        "state": iss["state"],
        "labels": labels,
        "assignees": assignees,
        "created_at": iss["created_at"],
        "help_wanted_at": hw_at,
        "reach": reach,
        "hybridapp": bool(re.search(r"(?i)hybrid ?app", body + latest)) and reach != "web",
        "melvin_attempts": len(melvin),
        "melvin_confidence": conf.group(1).lower() if conf else None,
        "melvin_hedges": bool(MELVIN_HEDGING.search(_unquote(latest))) if latest else False,
        "melvin_pinned": len(PERMALINK_WITH_LINES.findall(latest or "")),
        "melvin_says_backend": (bool(analyses) and not melvin and bool(MELVIN_BACKEND_RE.search(analyses[-1])))
                               or bool(MELVIN_NO_APP_FIX_RE.search(latest or "")),
        "concierge": bool(CONCIERGE_RE.search(iss["title"])),
        "integration": (INTEGRATION_RE.search(iss["title"]) or INTEGRATION_RE.search(body[:3000]) or [None])[0],
        "rivals_after_hw": humans,
        "early_posters": early,
        "approved": approved,
        "hired": hired,
        "regression": regression,
        "not_a_bug_by": sorted(set(not_a_bug)),
        "repro_wanted_by": sorted(set(repro_wanted)),
        "reviewer_to_melvin": reviewer_to_melvin,
        "reviewer_comments": reviewer_comments[-5:],
        "comment_count": len(comments),
    }


def grade(s, manual=None):
    """Return (tier, reasons). Tiers: OPEN_NOW, WATCH, LONGSHOT, DROPPED. Every reason is checkable."""
    manual = manual or {}
    dead = []
    if s["state"] != "open":
        dead.append("closed")
    if "Reviewing" in s["labels"]:
        dead.append("a PR is already open (Reviewing)")
    if s["approved"]:
        dead.append("C+ already approved a proposal")
    if s["hired"]:
        dead.append("a contributor was hired")
    if s["regression"]:
        dead.append("regression, goes back to the PR author")
    if {"Internal", "HOLD", "Not a priority"} & set(s["labels"]):
        dead.append("blocking label: %s" % ", ".join(sorted({"Internal", "HOLD", "Not a priority"} & set(s["labels"]))))
    if manual.get("dropped"):
        dead.append("dropped by you: %s" % manual["dropped"])
    if dead and not manual.get("pinned"):
        return "DROPPED", dead

    plus, minus = [], []
    if s.get("melvin_says_backend"):
        minus.append("Melvin says the fix is backend, likely goes internal")
    elif s["melvin_attempts"] == 0:
        plus.append("no Melvin proposal yet")
    elif s["melvin_confidence"] in ("low", "medium"):
        plus.append("Melvin rates itself %s confidence" % s["melvin_confidence"])
    elif s["melvin_hedges"] and s["melvin_pinned"] >= PRECISE_TRACE_PINS:
        minus.append("Melvin traced it with %d pinned lines (only caveat: no repro in its sandbox)" % s["melvin_pinned"])
    elif s["melvin_hedges"]:
        plus.append("Melvin hedges its own proposal")
    elif s["melvin_attempts"] > 1:
        plus.append("Melvin on attempt %d, earlier ones not accepted" % s["melvin_attempts"])
    elif s["melvin_pinned"] >= 3:
        minus.append("Melvin traced it with %d pinned lines, hard to beat" % s["melvin_pinned"])
    if s["repro_wanted_by"]:
        plus.append("reviewer can't reproduce, a repro wins attention")
    if s["reach"] == "web":
        plus.append("testable in a browser")
    elif s["reach"] == "ios-only":
        minus.append("iOS only, needs a Mac")
    elif s["reach"] == "android-app":
        minus.append("Android app only, needs an emulator build")
    if s.get("integration"):
        minus.append("needs a %s account to reproduce" % s["integration"])
    if s["hybridapp"]:
        minus.append("HybridApp, needs the private Mobile-Expensify repo to test")
    if s.get("concierge"):
        minus.append("Concierge, which the skill forbids testing against")
    if s["reviewer_to_melvin"]:
        minus.append("reviewer is iterating with Melvin (%dx)" % s["reviewer_to_melvin"])
    if s["not_a_bug_by"]:
        minus.append("reviewer suggests not a bug / may close")
    if s["help_wanted_at"]:
        if s["rivals_after_hw"] >= CROWDED:
            minus.append("%d proposals since Help Wanted, saturated" % s["rivals_after_hw"])
        elif s["rivals_after_hw"] <= 3:
            plus.append("only %d proposal(s) since Help Wanted" % s["rivals_after_hw"])
    if manual.get("pinned"):
        plus.append("pinned by you")

    hard_no = any(m.startswith(("iOS only", "HybridApp", "reviewer suggests", "Melvin says the fix is backend", "Concierge")) or "saturated" in m for m in minus)
    if hard_no and not manual.get("pinned"):
        tier = "LONGSHOT"
    elif s["help_wanted_at"]:
        tier = "OPEN_NOW"
    elif len(plus) > len(minus):
        tier = "WATCH"
    else:
        tier = "LONGSHOT"
    return tier, plus + ["(-) " + m for m in minus]


# ---------------------------------------------------------------------------------------------
# Change log
# ---------------------------------------------------------------------------------------------

def changes(old, new, old_tier, new_tier):
    if old is None:
        return ["new issue"]
    out = []
    if new["help_wanted_at"] and not old.get("help_wanted_at"):
        out.append("**Help Wanted added %s PKT, proposals are now legal**" % _pkt(new["help_wanted_at"]))
    d = new["rivals_after_hw"] - old.get("rivals_after_hw", 0)
    if d > 0:
        out.append("+%d proposal(s) since Help Wanted (now %d)" % (d, new["rivals_after_hw"]))
    d = new["early_posters"] - old.get("early_posters", 0)
    if d > 0:
        out.append("+%d early proposal(s), ignored under the rules (now %d)" % (d, new["early_posters"]))
    if new["melvin_attempts"] > old.get("melvin_attempts", 0):
        out.append("Melvin posted proposal #%d" % new["melvin_attempts"])
    seen = {c["id"] for c in old.get("reviewer_comments", [])}
    for c in new["reviewer_comments"]:
        if c["id"] not in seen:
            out.append("reviewer @%s: \"%s\"" % (c["by"], c["text"][:160]))
    for key, msg in (("approved", "C+ approved a proposal"), ("hired", "contributor hired"),
                     ("regression", "flagged as a regression")):
        if new[key] and not old.get(key):
            out.append(msg)
    if new["state"] != old.get("state"):
        out.append("state: %s -> %s" % (old.get("state"), new["state"]))
    if old_tier and new_tier != old_tier:
        out.append("tier: %s -> %s" % (old_tier, new_tier))
    return out


# ---------------------------------------------------------------------------------------------
# State and report
# ---------------------------------------------------------------------------------------------

def load():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"issues": {}, "last_refresh": None, "log": []}


def save(state):
    DATA.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def refresh(state, hours):
    numbers = set(discover(hours))
    for n, rec in state["issues"].items():
        if rec["tier"] != "DROPPED" or rec.get("manual", {}).get("pinned"):
            numbers.add(int(n))
    stamp = _now().isoformat()
    run_changes, failed = [], []
    for n in sorted(numbers, reverse=True):
        rec = state["issues"].get(str(n), {})
        try:
            snap = snapshot(*fetch(n))
        except gh.GhError as exc:
            failed.append((n, str(exc).splitlines()[0][:120]))
            continue
        tier, reasons = grade(snap, rec.get("manual"))
        diff = changes(rec.get("snap"), snap, rec.get("tier"), tier)
        if diff:
            run_changes.append((n, snap["title"], diff))
        rec.update({"snap": snap, "tier": tier, "reasons": reasons, "checked_at": stamp})
        if tier == "DROPPED" and not rec.get("dropped_at"):
            rec["dropped_at"] = stamp
        if tier != "DROPPED":
            rec.pop("dropped_at", None)
        state["issues"][str(n)] = rec
    cutoff = _now() - timedelta(days=KEEP_DROPPED_DAYS)
    state["issues"] = {k: v for k, v in state["issues"].items()
                       if not (v["tier"] == "DROPPED" and v.get("dropped_at") and _parse(v["dropped_at"]) < cutoff)}
    state["previous_refresh"], state["last_refresh"] = state.get("last_refresh"), stamp
    state["last_changes"], state["last_failed"] = run_changes, failed
    return state


def _row(n, rec):
    s = rec["snap"]
    draft = " · **draft ready**" if (DRAFTS / ("%s.md" % n)).exists() else ""
    note = (" · note: %s" % rec["manual"]["note"]) if rec.get("manual", {}).get("note") else ""
    rivals = ("%d since HW" % s["rivals_after_hw"]) if s["help_wanted_at"] else ("%d early" % s["early_posters"])
    age = (_now() - _parse(s["created_at"])).total_seconds() / 3600
    return "| [#%s](%s) | %s | %s | %s | %s | %.0fh | %s%s%s |" % (
        n, s["url"], s["title"][:70].replace("|", "/"), ("$%d" % s["bounty"]) if s["bounty"] else "-",
        rivals, s["reach"], age, "; ".join(rec["reasons"]), draft, note)


def report(state):
    last = state.get("last_refresh")
    out = ["# Expensify watchlist", "",
           "Last refresh: %s PKT%s" % (_pkt(last) if last else "never",
                                        (" (previous %s PKT)" % _pkt(state["previous_refresh"])) if state.get("previous_refresh") else ""),
           ""]
    if state.get("last_failed"):
        out.append("**Could not fetch %d issue(s), showing last known state:** %s" % (
            len(state["last_failed"]), ", ".join("#%s" % n for n, _ in state["last_failed"])))
        out.append("")
    out += ["## What changed since last check", ""]
    if state.get("last_changes"):
        for n, title, diff in state["last_changes"]:
            out.append("- **#%s** %s" % (n, title[:70]))
            out += ["  - %s" % d for d in diff]
    else:
        out.append("Nothing changed.")
    out.append("")

    header = ["| Issue | Title | Bounty | Rivals | Reach | Age | Why |", "|---|---|---|---|---|---|---|"]
    sections = (("OPEN_NOW", "Open now: Help Wanted is up, post if you have a draft"),
                ("WATCH", "Watch: prep the draft before the label lands"),
                ("LONGSHOT", "Long shots: tracked, but something stands in the way"),
                ("DROPPED", "Dropped in the last %d days (check these are right)" % KEEP_DROPPED_DAYS))
    for tier, heading in sections:
        rows = sorted(((n, r) for n, r in state["issues"].items() if r["tier"] == tier),
                      key=lambda x: -int(x[0]))
        out += ["## %s (%d)" % (heading, len(rows)), ""]
        out += (header + [_row(n, r) for n, r in rows]) if rows else ["None."]
        out.append("")
    out += ["Rivals: `since HW` are proposals that count. `early` were posted before Help Wanted and are",
            "ignored under CONTRIBUTING.md, but they show who is working the issue.",
            "The tiers are rules over what the thread says, not judgment. Read the issue before committing."]
    return "\n".join(out)


def _manual(state, number):
    rec = state["issues"].setdefault(str(number), {"tier": "WATCH", "reasons": [], "snap": None})
    return rec.setdefault("manual", {})


# ---------------------------------------------------------------------------------------------
# Self-test: grading rules against hand-built snapshots, offline.
# ---------------------------------------------------------------------------------------------

def _fixture(**kw):
    base = {"number": 1, "title": "t", "url": "u", "bounty": 175, "state": "open", "labels": ["External", "Bug"],
            "assignees": ["cplus"], "created_at": "2026-09-29T00:00:00Z", "help_wanted_at": None, "reach": "web",
            "hybridapp": False, "melvin_attempts": 1, "melvin_confidence": None, "melvin_hedges": False,
            "melvin_pinned": 0, "rivals_after_hw": 0, "early_posters": 0, "approved": False, "hired": False,
            "regression": False, "not_a_bug_by": [], "repro_wanted_by": [], "reviewer_to_melvin": 0,
            "reviewer_comments": [], "comment_count": 3}
    base.update(kw)
    return base


def selftest():
    cases = [
        ("approved Melvin is dead", _fixture(approved=True), "DROPPED"),
        ("regression to PR author is dead", _fixture(regression=True), "DROPPED"),
        ("Reviewing label is dead", _fixture(labels=["External", "Reviewing"]), "DROPPED"),
        ("closed is dead", _fixture(state="closed"), "DROPPED"),
        ("unsure Melvin on a web bug is worth watching", _fixture(melvin_confidence="medium"), "WATCH"),
        ("iOS-only is a long shot", _fixture(reach="ios-only", melvin_confidence="low"), "LONGSHOT"),
        ("HybridApp is a long shot", _fixture(reach="android-app", hybridapp=True, melvin_confidence="low"), "LONGSHOT"),
        ("well-traced Melvin, web, is a long shot", _fixture(melvin_pinned=6), "LONGSHOT"),
        ("Help Wanted with few rivals is open now", _fixture(help_wanted_at="2026-09-29T10:00:00Z", rivals_after_hw=2), "OPEN_NOW"),
        ("Help Wanted but saturated is a long shot", _fixture(help_wanted_at="2026-09-29T10:00:00Z", rivals_after_hw=12), "LONGSHOT"),
        ("Melvin says backend is a long shot", _fixture(melvin_attempts=0, melvin_says_backend=True), "LONGSHOT"),
        ("integration bug is not a plain watch", _fixture(integration="TriNet"), "LONGSHOT"),
        ("Concierge is a long shot", _fixture(concierge=True, melvin_confidence="low"), "LONGSHOT"),
        ("hedge on a precise trace is not an opening", _fixture(melvin_hedges=True, melvin_pinned=7), "LONGSHOT"),
        ("hedge on a thin trace is an opening", _fixture(melvin_hedges=True, melvin_pinned=1), "WATCH"),
        ("reviewer says expected behaviour is a long shot", _fixture(not_a_bug_by=["cplus"], melvin_confidence="low"), "LONGSHOT"),
    ]
    failures = []
    for name, snap, want in cases:
        got, reasons = grade(snap)
        if got != want:
            failures.append("%s: want %s, got %s (%s)" % (name, want, got, "; ".join(reasons)))
    if grade(_fixture(approved=True), {"pinned": True})[0] == "DROPPED":
        failures.append("a pinned issue was dropped anyway")

    body = "- [x] Android: App\n- [ ] Android: mWeb Chrome\n- [x] iOS: App\n- [ ] Windows: Chrome"
    if platforms(body)[0] != "android-app":
        failures.append("native-only issue read as %s" % platforms(body)[0])
    if platforms("- [x] Windows: Chrome\n- [x] iOS: App")[0] != "web":
        failures.append("web-ticked issue not read as web")
    if platforms("- [x] iOS: App\n- [x] iOS: mWeb Safari")[0] != "ios-only":
        failures.append("iOS-only issue not read as ios-only")
    if INTEGRATION_RE.search("the usage message is truncated") or not INTEGRATION_RE.search("Trinet - Can't connect"):
        failures.append("integration pattern lost its word boundaries")
    if not APPROVED_RE.search("🎀 👀 🎀 C+ reviewed"):
        failures.append("spaced approval emoji not matched")

    old = _fixture(reviewer_comments=[{"id": 1, "by": "cplus", "at": "x", "text": "a"}])
    new = _fixture(help_wanted_at="2026-09-29T10:00:00Z", rivals_after_hw=3,
                   reviewer_comments=[{"id": 1, "by": "cplus", "at": "x", "text": "a"},
                                      {"id": 2, "by": "cplus", "at": "y", "text": "can anyone reproduce?"}])
    diff = " | ".join(changes(old, new, "WATCH", "OPEN_NOW"))
    for want in ("Help Wanted added", "+3 proposal", "reviewer @cplus", "tier: WATCH -> OPEN_NOW"):
        if want not in diff:
            failures.append("change log missed '%s': %s" % (want, diff))

    if failures:
        print("SELFTEST FAILED")
        for f in failures:
            print("  - " + f)
        return 1
    print("selftest passed (%d grading cases, platform parsing, change log)" % len(cases))
    return 0


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--refresh", action="store_true")
    p.add_argument("--hours", type=int, default=24)
    p.add_argument("--show", action="store_true")
    p.add_argument("--note", nargs=2, metavar=("ISSUE", "TEXT"))
    p.add_argument("--pin", type=int)
    p.add_argument("--unpin", type=int)
    p.add_argument("--drop", nargs=2, metavar=("ISSUE", "REASON"))
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()

    if a.selftest:
        return selftest()
    state = load()
    if a.note:
        _manual(state, int(a.note[0]))["note"] = a.note[1]
    if a.pin:
        m = _manual(state, a.pin)
        m["pinned"] = True
        m.pop("dropped", None)
    if a.unpin:
        _manual(state, a.unpin).pop("pinned", None)
    if a.drop:
        m = _manual(state, int(a.drop[0]))
        m["dropped"] = a.drop[1]
        m.pop("pinned", None)
        rec = state["issues"][a.drop[0]]
        rec["tier"], rec["dropped_at"] = "DROPPED", _now().isoformat()
    if a.refresh:
        try:
            state = refresh(state, a.hours)
        except gh.GhError as exc:
            print("Discovery failed, nothing was changed: %s" % exc)
            return 1
    if a.refresh or a.note or a.pin or a.unpin or a.drop:
        save(state)
    if a.refresh or a.show:
        # Manual-only records created by --pin/--note before a refresh have no snapshot yet.
        text = report({**state, "issues": {k: v for k, v in state["issues"].items() if v.get("snap")}})
        REPORT_FILE.write_text(text, encoding="utf-8")
        print(text)
    elif not (a.note or a.pin or a.unpin or a.drop):
        p.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())

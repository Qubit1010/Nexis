"""Post a prepared proposal, after checking the things that get proposals thrown out.

This exists because the expensive failures in this process are not bad ideas, they are avoidable
procedural mistakes made in a hurry. The window opens, you have sixty seconds of advantage, and that
is exactly the moment you are least likely to notice that the draft still contains a code diff or
that you already have a proposal on the thread. So the checks run here rather than in your head.

Each refusal maps to a documented Expensify rule:

  no Help Wanted label   Proposals posted before the label are ignored and not reviewed.
  code diff present      PROPOSAL_TEMPLATE.md says "DO NOT POST CODE DIFFS" outright, and reviewers
                         are told to course-correct anyone posting large multi-line diffs.
  you already proposed   CONTRIBUTING.md allows one proposal per person per issue. A second one is a
                         rule violation; the correct move is editing the first and posting a short
                         "[Updated](link)" comment.
  missing sections       Reviewers are instructed not to approve proposals that skip required
                         questions, so an incomplete proposal is dead on arrival regardless of merit.

Nothing here posts on its own. --confirm is required, and the point of that is not ceremony: under
Expensify's AI etiquette rules you are personally accountable for anything posted under your name,
and you cannot be accountable for text you have not read.

Usage:
  python post.py --issue 99208 --draft draft.md            # dry run, checks only
  python post.py --issue 99208 --draft draft.md --confirm  # actually post
  python post.py --selftest
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import gh  # noqa: E402
import proposals as props_mod  # noqa: E402

DIFF_FENCE = re.compile(r"```\s*(diff|patch)\b", re.IGNORECASE)
FENCE_BLOCK = re.compile(r"```.*?```", re.DOTALL)
MAX_FENCE_LINES = 15

# Detecting a pasted diff without flagging every markdown bullet list takes a little care. A naive
# "line starts with + or -" rule fires on ordinary prose, since "- point one" is how everyone writes
# a list. The distinguishing feature is the plus: markdown bullets are overwhelmingly "-" or "*",
# while a diff needs added lines. So added lines are counted on their own, and mixed +/- runs are
# only treated as a diff when both signs appear together.
ADDED_LINE = re.compile(r"(?m)^\+(?!\+)[ \t]*\S.*$")
REMOVED_LINE = re.compile(r"(?m)^-(?!-)[ \t]*\S.*$")
MAX_ADDED_LINES = 4

REQUIRED = [
    ("proposal heading", re.compile(r"^#{1,3} ?Proposal", re.IGNORECASE | re.MULTILINE)),
    ("root cause section", re.compile(r"root cause", re.IGNORECASE)),
    ("solution section", re.compile(r"what changes|changes .{0,20}(should|we) make|solution", re.IGNORECASE)),
]


def check_draft(text):
    """Return a list of (severity, message). severity is 'block' or 'warn'."""
    problems = []

    if DIFF_FENCE.search(text):
        problems.append(("block",
                         "The draft contains a ```diff or ```patch block. PROPOSAL_TEMPLATE.md bans code "
                         "diffs outright. Describe the change and cite the lines with permalinks instead."))

    for fence in FENCE_BLOCK.findall(text):
        n = fence.count("\n")
        if n > MAX_FENCE_LINES:
            problems.append(("block",
                             "A fenced code block runs %d lines. Reviewers treat a large multi-line block as "
                             "a PR in disguise and are told to push back on it. Cite the existing code with a "
                             "permalink and describe the change in prose." % n))
            break

    added = ADDED_LINE.findall(text)
    removed = REMOVED_LINE.findall(text)
    if len(added) >= MAX_ADDED_LINES:
        problems.append(("block",
                         "Found %d lines starting with '+', which reads as a pasted diff even without a fence. "
                         "Reviewers ask for prose and permalinks, not patches." % len(added)))
    elif added and len(removed) >= 4:
        problems.append(("block",
                         "Found %d added and %d removed lines together, which is a diff in all but name. "
                         "Describe the change instead and cite the current code with a permalink."
                         % (len(added), len(removed))))

    for name, rx in REQUIRED:
        if not rx.search(text):
            problems.append(("block", "Missing the %s. Reviewers are instructed not to approve proposals "
                                      "that skip a required question." % name))

    words = len(re.findall(r"\S+", text))
    if words < 120:
        problems.append(("warn",
                         "Only %d words. Every proposal that won in the sampled issues carried a traced root "
                         "cause across real files; a short one rarely clears the bar." % words))
    if not re.search(r"/blob/[0-9a-f]{7,40}/\S+#L\d+", text):
        problems.append(("warn",
                         "No SHA-pinned permalink found. The proposal that won issue 98426 cited four of them. "
                         "A root cause with no line references reads as a description of the symptom."))
    if re.search(r"/blob/main/", text):
        problems.append(("warn",
                         "A permalink points at /blob/main/. That link rots the next time the file changes. "
                         "Use repo.py --permalink, which pins the SHA."))
    return problems


def preflight(issue_number, text, me=None):
    """Everything that must be true before posting. Returns (ok, blocking, warnings)."""
    blocking, warnings = [], []

    for sev, msg in check_draft(text):
        (blocking if sev == "block" else warnings).append(msg)

    hw = gh.help_wanted_at(issue_number)
    if not hw:
        blocking.append(
            "Issue #%d does not have the Help Wanted label yet. Proposals posted before the label are "
            "ignored and not reviewed. Keep preparing and run watch.py --armed to catch the moment it "
            "opens." % issue_number)

    iss = gh.issue(issue_number)
    if iss.get("state") != "open":
        blocking.append("Issue #%d is closed." % issue_number)

    me = me or _whoami()
    if me:
        mine = [p for p in props_mod.fetch(issue_number) if p["author"] == me and not p["withdrawn"]]
        if mine:
            blocking.append(
                "You already have a live proposal on this issue (%s). CONTRIBUTING.md allows one per "
                "person. To revise, edit that comment and post a short comment reading "
                "'## Proposal\\n[Updated](link-to-your-edited-comment)'." % mine[0]["url"])

    return (not blocking), blocking, warnings


def _whoami():
    try:
        out = gh.api("user", jq=".login")
        return out if isinstance(out, str) else None
    except gh.GhError:
        return None


def post(issue_number, text):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
        fh.write(text)
        tmp = fh.name
    try:
        proc = subprocess.run(
            ["gh", "issue", "comment", str(issue_number), "--repo", gh.REPO, "--body-file", tmp],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        if proc.returncode != 0:
            raise gh.GhError("posting failed:\n%s" % (proc.stderr or "").strip())
        return (proc.stdout or "").strip()
    finally:
        Path(tmp).unlink(missing_ok=True)


def selftest():
    failures = []

    good = """## Proposal
### What is the root cause of that problem?
The rate row is rendered non-interactive because `isRateInteractive` requires a truthy rate, see
https://github.com/Expensify/App/blob/79bca1613e3ed0494304d7e9b78eecad9df422a3/src/x.tsx#L95-L97
and the value is derived upstream in a hook that returns undefined for moved transactions, so the
field can never be opened by the user once the error state is reached on the confirmation screen.
### What changes do you think we should make in order to solve the problem?
Drop the redundant truthiness check so the row stays interactive while the error is displayed,
which lets the user open the picker and choose a valid workspace rate.
"""
    probs = check_draft(good)
    blockers = [m for s, m in probs if s == "block"]
    if blockers:
        failures.append("a well-formed draft was blocked: %s" % blockers[0])

    cases = [
        ("```diff\n- const a = 1\n+ const a = 2\n```", "diff fence"),
        ("\n".join("+ line %d" % i for i in range(8)), "pasted diff lines"),
        ("\n".join("+const x = %d;" % i for i in range(5)), "unspaced diff lines"),
        ("## Proposal\n### root cause\nthing\n### what changes\n" + "```js\n" + "x\n" * 40 + "```", "oversized code block"),
    ]
    for body, why in cases:
        text = good + "\n" + body
        if not [m for s, m in check_draft(text) if s == "block"]:
            failures.append("draft containing a %s was not blocked" % why)

    # The false positive that matters: an ordinary markdown bullet list must survive. Proposals are
    # full of them, and a checker that blocks normal prose would be turned off within a week, which
    # would take the genuine diff guard down with it.
    bulleted = good + "\n\nAlternatives considered:\n" + "\n".join(
        "- option %d, rejected because it moves the check to the wrong layer" % i for i in range(9))
    if [m for s, m in check_draft(bulleted) if s == "block"]:
        failures.append("an ordinary markdown bullet list was blocked as a diff")

    for missing, why in [
        ("### What is the root cause of that problem?", "root cause"),
        ("## Proposal", "proposal heading"),
    ]:
        stripped = good.replace(missing, "")
        if not [m for s, m in check_draft(stripped) if s == "block"]:
            failures.append("draft missing its %s was not blocked" % why)

    # A /blob/main/ link rots, so it should warn even though it is otherwise well formed.
    rotting = good.replace("blob/79bca1613e3ed0494304d7e9b78eecad9df422a3", "blob/main")
    if not [m for s, m in check_draft(rotting) if s == "warn" and "/blob/main/" in m]:
        failures.append("a /blob/main/ permalink did not raise a warning")

    # Posting to an issue with no Help Wanted label must be blocked. 99215 was in the work window at
    # time of writing; if it has since been labelled, this check reports as skipped rather than fake-passing.
    try:
        if gh.help_wanted_at(99215) is None:
            ok, blocking, _ = preflight(99215, good)
            if ok or not any("Help Wanted" in b for b in blocking):
                failures.append("preflight allowed a post to an issue with no Help Wanted label")
        else:
            print("  note: #99215 has since been labelled, so the label guard was not exercised live")
    except gh.GhError as exc:
        print("  note: could not reach GitHub to exercise the label guard (%s)" % exc)

    if failures:
        print("SELFTEST FAILED")
        for f in failures:
            print("  - %s" % f)
        return 1
    print("SELFTEST PASSED")
    print("  a well-formed proposal passes")
    print("  diff fences, pasted diff lines and oversized code blocks are all blocked")
    print("  missing required sections are blocked")
    print("  rotting /blob/main/ links warn")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--issue", type=int)
    p.add_argument("--draft", metavar="FILE")
    p.add_argument("--confirm", action="store_true", help="actually post; without this it is a dry run")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()

    if a.selftest:
        return selftest()
    if not (a.issue and a.draft):
        p.print_help()
        return 0

    text = Path(a.draft).read_text(encoding="utf-8")
    try:
        ok, blocking, warnings = preflight(a.issue, text)
    except gh.GhError as exc:
        print("GitHub access failed: %s" % exc, file=sys.stderr)
        return 2

    for w in warnings:
        print("WARNING: %s\n" % w)
    for b in blocking:
        print("BLOCKED: %s\n" % b)

    if not ok:
        print("Not posting. Fix the blocking items above and run again.")
        return 1

    if not a.confirm:
        print("Dry run passed. Nothing was posted.")
        print("")
        print("Before adding --confirm, read the draft one more time and check you could explain every")
        print("claim in it to a reviewer without help. Expensify's AI etiquette guide makes you")
        print("personally accountable for what goes up under your name, and a root cause you cannot")
        print("defend in the follow-up conversation costs more than the proposal was worth.")
        return 0

    url = post(a.issue, text)
    print("Posted: %s" % url)
    print("")
    print("Now stop commenting. CONTRIBUTING.md asks you to wait for reviewer feedback rather than")
    print("adding follow-ups, and to revise by editing this comment rather than posting another.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

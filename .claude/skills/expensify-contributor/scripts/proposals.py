"""Read every proposal already on an issue, and screen a draft against them.

Two jobs.

First, show what has already been claimed. Expensify requires that a new proposal be meaningfully
different from existing ones, and you cannot be different from something you have not read. This
also tells you what MelvinBot asserted, which matters because Melvin is reviewed first.

Second, screen a draft for duplicate risk. ProposalPolice runs an OpenAI conversation holding every
proposal posted on the issue, and automatically withdraws any new proposal scoring 90 percent
similarity or above against a still-live one. Losing a proposal that way wastes the entire work
window, so it is worth checking before posting.

An honest limit, and it is the most important thing on this page: the screen here is lexical. It
compares words. ProposalPolice compares meaning. A high lexical score is a reliable danger sign, but
a low one proves nothing at all, because two proposals can share almost no vocabulary and still
describe the identical root cause and fix. So this script reports two distinct outcomes, never one:
DANGER means it found overlap, and INCONCLUSIVE means it found none and cannot tell you more. There
is deliberately no PASS. Judging semantic difference is the reader's job, and the script says so
rather than implying a safety it cannot deliver.

Usage:
  python proposals.py --issue 99208
  python proposals.py --issue 99208 --screen draft.md
  python proposals.py --selftest
"""

import argparse
import difflib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import gh  # noqa: E402

PROPOSAL_RE = re.compile(r"^#{1,3} ?Proposal", re.IGNORECASE)
WITHDRAWN = "Duplicated proposal withdrawn"
LEXICAL_DANGER = 0.60
WORD_RE = re.compile(r"[a-z][a-z0-9_]{2,}")

# Vocabulary every proposal on a given issue shares by construction: the template headings, and the
# words of the bug itself. Left in, these inflate every comparison and make genuinely different
# proposals look alike, which would train you to ignore the warning.
STOPWORDS = set("""
proposal root cause problem solution issue what changes think should make order solve that this
these those alternative alternatives explored optional please state restate trying which when
the and for with from have has been will would could there their they them then than
code line lines file files function component render props state value values return
app expensify user users page screen click tap button field
""".split())


def _norm_tokens(text):
    body = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)          # fenced code
    body = re.sub(r"https?://\S+", " ", body)                          # permalinks
    body = re.sub(r"<!--.*?-->", " ", body, flags=re.DOTALL)          # html comments
    toks = WORD_RE.findall(body.lower())
    return [t for t in toks if t not in STOPWORDS]


def _jaccard(a, b):
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _sequence_ratio(a, b):
    return difflib.SequenceMatcher(None, " ".join(a), " ".join(b)).ratio()


def _extract_root_cause(body):
    """Pull the root-cause section out of a proposal, whichever template variant it used."""
    m = re.search(
        r"###?\s*What is the root cause of that problem\?\s*(.+?)(?=\n###?\s|\Z)",
        body, re.DOTALL | re.IGNORECASE)
    if not m:
        m = re.search(r"###?\s*.*root cause.*?\n(.+?)(?=\n###?\s|\Z)", body, re.DOTALL | re.IGNORECASE)
    if not m:
        return None
    txt = re.sub(r"\s+", " ", m.group(1)).strip()
    return txt


def fetch(number):
    """Every proposal on the issue, MelvinBot's first since it is reviewed first.

    Withdrawn proposals need their own detection rather than the heading match. When ProposalPolice
    withdraws one it rewrites the comment body wholesale, so the text no longer opens with the
    template heading and a heading-only filter silently drops it. That matters: the withdrawn ones
    are the most instructive comments on the thread, because they show exactly which root causes
    were close enough to each other to trip the 90 percent threshold.
    """
    out = []
    for c in gh.comments(number):
        body = (c.get("body") or "").strip()
        withdrawn = WITHDRAWN in body
        if not PROPOSAL_RE.match(body) and not withdrawn:
            continue
        author = c.get("user", {}).get("login", "?")
        out.append({
            "author": author,
            "is_melvin": author == "MelvinBot",
            "created_at": c.get("created_at"),
            "url": c.get("html_url"),
            "chars": len(body),
            "withdrawn": withdrawn,
            "root_cause": _extract_root_cause(body),
            "cites_pinned_lines": bool(re.search(r"/blob/[0-9a-f]{7,40}/\S+#L\d+", body)),
            "body": body,
        })
    out.sort(key=lambda p: (not p["is_melvin"], p["created_at"] or ""))
    return out


def print_landscape(number):
    props = fetch(number)
    live = [p for p in props if not p["withdrawn"]]
    dead = [p for p in props if p["withdrawn"]]
    print("Issue #%d: %d live proposal(s), %d already withdrawn as duplicates\n" % (number, len(live), len(dead)))
    if not live:
        print("Nothing posted yet. Unusual, and worth moving on.")
        return props
    for p in live:
        tag = "MELVIN (reviewed first)" if p["is_melvin"] else p["author"]
        pins = "pinned lines" if p["cites_pinned_lines"] else "no pinned lines"
        print("  %s  %s  %d chars, %s" % ((p["created_at"] or "")[:16], tag, p["chars"], pins))
        rc = p["root_cause"]
        print("     root cause: %s" % (rc[:230] + "..." if rc and len(rc) > 230 else rc or "(no parseable root-cause section)"))
        print("     %s\n" % p["url"])
    if dead:
        print("Withdrawn as duplicates: %s" % ", ".join(p["author"] for p in dead))
        print("That is ProposalPolice at work. It is the fate of any proposal scoring 90 percent")
        print("similarity or above against a live one.\n")
    return props


def screen(number, draft_text):
    props = [p for p in fetch(number) if not p["withdrawn"]]
    if not props:
        print("No live proposals to compare against, so there is nothing to duplicate yet.")
        return 0
    dtoks = _norm_tokens(draft_text)
    if len(dtoks) < 30:
        print("The draft is too short to screen meaningfully (%d content words after filtering)." % len(dtoks))
        return 2

    rows = []
    for p in props:
        ptoks = _norm_tokens(p["body"])
        rows.append((p, _jaccard(dtoks, ptoks), _sequence_ratio(dtoks, ptoks)))
    rows.sort(key=lambda r: max(r[1], r[2]), reverse=True)

    print("Lexical overlap against %d live proposal(s), highest first:\n" % len(props))
    for p, jac, seq in rows:
        who = "MelvinBot" if p["is_melvin"] else p["author"]
        flag = "  <-- DANGER" if max(jac, seq) >= LEXICAL_DANGER else ""
        print("  vocabulary %.0f%%  sequence %.0f%%  %s%s" % (jac * 100, seq * 100, who, flag))
    print("")

    worst = max(max(j, s) for _, j, s in rows)
    if worst >= LEXICAL_DANGER:
        top = rows[0][0]
        print("DANGER: this draft shares %.0f%% of its wording with %s's proposal." % (
            worst * 100, "MelvinBot" if top["is_melvin"] else top["author"]))
        print("Rewording will not fix this. ProposalPolice compares meaning, so the draft needs a")
        print("genuinely different root cause or a materially different approach, or it needs to not")
        print("be posted at all. Read that proposal at %s" % top["url"])
        return 1

    print("INCONCLUSIVE: no significant word overlap found (highest was %.0f%%)." % (worst * 100))
    print("")
    print("This does NOT mean the draft is safe to post. The check above compares vocabulary, while")
    print("ProposalPolice compares meaning at a 90 percent threshold. Two proposals can share almost")
    print("no words and still name the same root cause and the same fix.")
    print("")
    print("So the real check is still yours. Read the root causes printed by --issue and answer one")
    print("question honestly: does this draft name a different cause, or does it name the same cause")
    print("in different words? Only the first is a proposal worth posting.")
    return 0


def selftest():
    failures = []

    # 98791 drew a first wave of proposals, several of which ProposalPolice withdrew as duplicates.
    props = fetch(98791)
    if len(props) < 8:
        failures.append("98791 returned %d proposals, expected at least 8" % len(props))
    if not any(p["withdrawn"] for p in props):
        failures.append("98791 should include at least one proposal withdrawn as a duplicate")
    if not any(p["is_melvin"] for p in props):
        failures.append("98791 should include a MelvinBot proposal")
    if props and not props[0]["is_melvin"]:
        failures.append("MelvinBot should sort first, since it is reviewed first")

    # Root-cause extraction must work on the proposal that actually won 98426.
    winners = [p for p in fetch(98426) if p["author"] == "abbasifaizan70"]
    if not winners:
        failures.append("could not find the winning proposal on 98426")
    else:
        w = winners[0]
        if not w["root_cause"]:
            failures.append("failed to parse a root cause out of the winning 98426 proposal")
        if not w["cites_pinned_lines"]:
            failures.append("the winning 98426 proposal cites pinned permalinks, detector missed it")

    # The screen must flag a near-copy, which is the case it exists to catch.
    if winners:
        rc = screen_value(98426, winners[0]["body"])
        if rc != 1:
            failures.append("screening a verbatim copy of a live proposal returned %s, expected 1 (DANGER)" % rc)

    if failures:
        print("SELFTEST FAILED")
        for f in failures:
            print("  - %s" % f)
        return 1
    print("SELFTEST PASSED")
    print("  parsed %d proposals on #98791 including withdrawn ones" % len(props))
    print("  root-cause and permalink detection verified on the winning #98426 proposal")
    print("  duplicate screen correctly flags a verbatim copy as DANGER")
    return 0


def screen_value(number, draft_text):
    """screen() without the printing, for the selftest."""
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        return screen(number, draft_text)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--issue", type=int, help="issue number")
    p.add_argument("--screen", metavar="FILE", help="path to a draft proposal to screen for duplicate risk")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()

    try:
        if a.selftest:
            return selftest()
        if not a.issue:
            p.print_help()
            return 0
        if a.screen:
            text = Path(a.screen).read_text(encoding="utf-8")
            print_landscape(a.issue)
            print("-" * 72)
            return screen(a.issue, text)
        print_landscape(a.issue)
        return 0
    except gh.GhError as exc:
        print("GitHub access failed: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

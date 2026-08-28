# Choosing what to work on, and the weekly routine

The scoring logic lives in `scripts/triage.py`. This file covers the two things a script cannot
decide: how to read a score, and how to run the week.

## The weekly rhythm

About four bounty issues appear a week, and the one-job-at-a-time rule caps a new contributor at one
active job anyway. So the shape of the week is narrow and deep, not broad.

**Monday and Thursday, ten minutes.** Run `python scripts/triage.py --scan`. It lists everything in
the work window, ranked, with an urgency flag. Two scans a week catches the median two-day window;
during an active pursuit, check daily, because the shortest window measured was four hours.

**Pick one.** Take the highest-scoring issue that clears BORDERLINE. Not the highest-scoring issue
outright, and not all of them. With four candidates a week and one slot, the job is to choose the
best available, not to hold out for a perfect one that may never appear.

**Spend the window investigating.** Reproduce it, trace the cause, build the evidence. This is the
work, and it is the part the competition cannot automate.

**Arm and wait.** Draft the proposal, screen it, and hold. Run `watch.py --armed` to catch the label.

**Post, then stop.** One proposal. Wait for the reviewer rather than adding follow-up comments.

## Reading a score

The rubric is five signals worth ten points, with two hard gates in front. Pursue at 6.0, read the
issue and decide for yourself between 4.0 and 6.0, skip below.

Those boundaries were calibrated against the live distribution rather than derived from anything, so
treat them as a ranking aid. What the number is genuinely good at is ordering ten issues quickly.
What it cannot do is tell you whether the bug is interesting or whether the root cause is findable
in the time available. Read the issue before committing two days.

The most important thing the score cannot see: **it checks whether MelvinBot cited a file and line,
not whether MelvinBot is right.** A confident, well-cited, wrong proposal scores as hard to beat when
it is actually the best opportunity on the board. Only reading it tells you which.

## What the signals mean

**Reproduction is contested, 3.0 points.** The strongest opening available, weighted highest for
that reason. Fires on the `Needs Reproduction` label or on anyone saying they cannot reproduce it.
Automated proposal-firing cannot reproduce a bug; it can only pattern-match issue text. When the
blocker is evidence rather than analysis, the incumbents' speed advantage is worth nothing.

**Melvin's root cause, 2.0 points.** Scores high when MelvinBot posted nothing, or posted something
short with no pinned line. Scores near zero when it cited real lines. Melvin is reviewed first, so a
solid Melvin proposal means the issue is close to decided before you start.

**Area crowding, 2.0 points.** Crash and Sentry issues, native and HybridApp, performance and INP,
and the accounting integrations all draw fewer proposals, because a prepared template does not
handle them and they often need a sandbox or a device. Mainstream frontend state bugs are the most
contested thing on the board.

**Rival proposals, 2.0 points.** Every proposal already posted dilutes whatever opening exists, and
raises the odds that yours reads as a near-duplicate of one of them.

**Platform reach, 1.0 point.** An iOS or macOS-only bug cannot currently be reproduced or tested
without a Mac. See `environment-setup.md` for how and when to solve that. Until then it is a hard
practical limit, not a preference.

## Urgency is not winnability

Time remaining is reported separately and never scored. An earlier version of the rubric subtracted
points from issues that had sat in the window a long time, which is exactly backwards: a
long-sitting issue is about to open, so it is more urgent and no less valuable. The two questions
are "is this worth working on" and "when must I work on it", and mixing them produces a number that
answers neither.

`IMMINENT` means the window is past the median and could close at any moment. That is a reason to
start now, or to skip because you cannot start now. It is not evidence about the issue.

## When everything scores badly

Some weeks nothing clears the bar. That is a real answer, and the correct response is to skip the
week rather than force a pursuit.

The rule that makes this easy: a new contributor may not submit proposals for a new job until their
first pull request is merged. Burning the one slot on a saturated mainstream frontend bug with
fourteen rivals is worse than waiting for a crash issue nobody can reproduce. The slot is the scarce
resource, not the time.

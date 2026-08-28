# How the Expensify bounty process actually works

Measured 2026-08-23 against the live repository. Every number here is reproducible with the queries
in `_research/queries.md`, and the raw data is in `_research/measurements.json`. Re-measure before
trusting any of it after about a quarter: MelvinBot and ProposalPolice are both recent additions
that reshaped the competition, and there is no reason to think the process has stopped moving.

## The one-paragraph version

Expensify pays $250 through Upwork for fixing a bug. You do not apply by writing code. You post a
**proposal** on the GitHub issue explaining the root cause and the fix; a Contributor+ reviewer picks
one; only then are you hired and allowed to open a pull request. The competition is for the proposal,
not the code, and it is decided in the first minutes after a specific label appears.

## The lifecycle of one issue

```
bug reported (often by Applause QA)
   -> labelled External, assigned a Contributor+ reviewer
   -> melvin-bot posts "Job added to Upwork"
   -> MelvinBot (the AI agent) posts the first proposal        [5 to 16 min after creation]
   ===== THE WORK WINDOW: median ~2 days, observed 4h to 8d =====
   -> Help Wanted label applied                                 <-- proposals become legal here
   -> 4 to 8 pre-written proposals fire within 1 to 2 seconds
   -> more trickle in over the following days (8 to 17 total)
   -> C+ reviews Melvin's proposal first, then others first-come-first-serve
   -> C+ posts a ribbon emoji sequence to recommend one to the internal engineer
   -> internal engineer approves, contributor is hired on Upwork and assigned
   -> PR, review by C+ and internal engineer, merge, deploy
   -> payment no sooner than 7 days after production deploy
```

## The five facts that determine strategy

**1. The funnel is small.** About four new `Help Wanted` issues a week, 15 in the last 30 days, 53
open at any time. This is not a firehose you can work through. It is a handful of contested
opportunities.

**2. MelvinBot proposes on effectively every issue.** Twenty of twenty sampled. It posts 5 to 16
minutes after the issue is created, long before proposals are open, and reviewers are told to review
it first because Expensify is paying to run it. On these issues the reviewer, not the contributor,
usually owns the resulting pull request. Read `HOW_TO_WORK_WITH_MELVINBOT.md` in the repo for the
full division of labour.

**3. The work window is where the work happens.** The issue is fully visible, with Melvin's proposal
on it, for a median of about two days before proposals are legal. Everyone serious uses that time.
The shortest window measured was 4.3 hours, so treat the median as a planning aid, never a promise.

**4. The submission is a race that is already automated.** On issue 98426 the label went on at
`14:40:43` and four proposals of 5,900 to 7,500 characters landed at `14:40:45`. Nobody writes 7KB
in two seconds. Several contributors poll for the label and fire a prepared body within a second or
two. You are not going to out-engineer that on timing, and you do not need to: the winner is chosen
among the early arrivals on quality.

**5. Duplicates are auto-withdrawn at 90 percent similarity.** `ProposalPolice` runs an OpenAI
conversation holding every proposal on the issue and rewrites any new one scoring at or above 90
percent similarity into a withdrawal. On issue 98791, four of the first wave died this way. This is
the single cheapest way to waste a two-day investigation.

## The selection rule, stated by Expensify

Inside an HTML comment in `PROPOSAL_TEMPLATE.md`, addressed to reviewers and invisible on the
rendered page:

> Choose the first proposal that has a reasonable answer to all the required questions.

> Do not approve any proposals that lack a satisfying explanation to the first two prompts. It is
> CRITICALLY important that we understand the root cause at a minimum even if the solution doesn't
> directly address it.

Root cause outranks solution, and the bar is completeness rather than brilliance. See
`winning-proposal-anatomy.md` for what clearing that bar looks like in practice.

## Where a newcomer can actually win

Three openings, in order of strength. `scripts/triage.py` scores all three.

### Reproduction that nobody else has managed

The strongest and most reliably available. Issue 98791 drew fourteen proposals inside sixty seconds,
and three days later the assigned reviewer was still commenting "Can anyone reproduce the crash?".
A contributor who posted real reproduction steps became the most useful person on the thread.

Automated proposal-firing cannot reproduce a bug. It can only pattern-match the issue text. On any
issue carrying `Needs Reproduction`, or where someone has said they cannot reproduce it, the entire
speed advantage of the incumbents evaporates, because the thing that is scarce is evidence.

### A Melvin proposal built on a wrong assumption

Melvin is reviewed first, so if it is right and specific, the issue is close to decided. But it is
frequently shallow, and the `Help Wanted` label going up is itself often a sign the reviewer was not
satisfied with it. If you can show its root cause is wrong, with evidence rather than assertion, you
become the obvious fallback and the reviewer needs you.

`triage.py` uses the presence of a SHA-pinned line citation in Melvin's proposal as a rough proxy
for whether it really traced the code. That proxy sees whether Melvin cited a line, not whether the
line is the right one, so verify by reading.

### Areas the fast crowd avoids

The proposal snipers concentrate on mainstream frontend state bugs, which is what a prepared
template handles well. Crash and Sentry issues, native and HybridApp problems, performance and INP
work, accounting integrations such as NetSuite, QuickBooks, Xero and Sage, and anything needing a
paid sandbox all draw fewer and weaker proposals.

## The rules that will disqualify you

These are absolute and documented. `what-not-to-do.md` has the full list with sources. The four that
cost the most:

- **No pull request before a proposal is accepted and you are hired.** This applies on MelvinBot
  issues too.
- **No proposals before the `Help Wanted` label.** They are ignored and not reviewed.
- **One proposal per issue.** To revise, edit the original and post a short comment linking to it.
  A second proposal is a rule violation.
- **One job at a time until your first PR merges.** New contributors may not submit proposals for
  new jobs until the first one is merged. This caps throughput no matter how good the workflow is,
  and it means the first win matters far more than the tenth.

## What this costs and returns

$250 per issue, less Upwork fees. Payment lands no sooner than seven days after the fix reaches
production, and a regression inside the 168-hour window after deploy applies a 50 percent penalty to
both you and the reviewer who approved you.

Set expectations honestly: with eight to seventeen competitors per issue, several of them
professional contributors with automated posting, a realistic first win is four to eight weeks of
consistent weekly effort. The compounding return is a merged pull request in a repository with five
thousand stars belonging to a public company, which is worth considerably more as a credential than
the bounty is as income.

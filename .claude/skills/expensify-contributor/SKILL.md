---
name: expensify-contributor
description: "Required reading before answering anything about the Expensify/App open-source bounty programme, where contributors post proposals on GitHub issues and are hired and paid about $250 through Upwork. Holds the measured mechanics of that competition (the pre-Help-Wanted work window, MelvinBot, ProposalPolice, Contributor+ selection) plus scripts that find and score issues, generate SHA-pinned permalinks, and screen a draft against the 90 percent duplicate auto-withdrawal. Use it rather than general knowledge for picking an issue, diagnosing why proposals lose, or checking a draft before posting. Triggers on a bare Expensify/App issue URL. Not for Expensify the expense product, and not for debugging any other codebase."
---
# Winning Expensify bounties

Expensify pays about $250 through Upwork for fixing a bug in `Expensify/App`. You do not apply by
writing code. You post a **proposal** on the GitHub issue explaining the root cause and the fix, a
Contributor+ reviewer picks one, and only then are you hired and allowed to open a pull request.

## The one thing that determines everything

An issue is fully visible, with an AI-written proposal already on it, for a **median of about two
days** before the `Help Wanted` label makes proposals legal. When that label lands, four to eight
contributors fire pre-written multi-kilobyte proposals **within one to two seconds**, because they
have automated the posting.

On issue 98426 the label went on at `14:40:43` and four proposals of 5,900 to 7,500 characters
landed at `14:40:45`. Nobody writes 7KB in two seconds.

So the work happens in the window, not after the label. A proposal started when the label appears is
already six hours late, and a 19,370-character proposal posted six hours late on that same issue
lost to a 7,275-character one posted at two seconds.

Being early gets you considered. Quality decides it among the early arrivals.

## Where a newcomer actually wins

Not by racing the automation. Three openings, strongest first:

1. **Reproduction nobody else has managed.** On issue 98791, fourteen proposals landed inside sixty
   seconds and three days later the reviewer was still asking "Can anyone reproduce the crash?".
   Automated firing cannot reproduce a bug, only pattern-match issue text. When the scarce thing is
   evidence, the incumbents' speed advantage is worth nothing.
2. **A MelvinBot proposal built on a wrong assumption.** Melvin is reviewed first, so if it is right
   and specific the issue is close to decided. It is often shallow, and the `Help Wanted` label going
   up is frequently a sign the reviewer was not satisfied with it.
3. **Areas the fast crowd avoids.** Crash and Sentry, native and HybridApp, performance and INP, and
   the accounting integrations. A prepared template does not handle these.

## Reference map

Read the one you need; do not load them all.

| File | Read it when |
|---|---|
| `references/how-expensify-works.md` | Orienting, or the user asks how the process works |
| `references/winning-proposal-anatomy.md` | **Before writing any proposal.** The 98426 winner dissected |
| `references/target-selection.md` | Choosing an issue, or interpreting a triage score |
| `references/what-not-to-do.md` | **Before posting anything.** Every disqualifying rule, with sources |
| `references/environment-setup.md` | First run, or the Mac and Node questions come up |
| `_research/measurements.json` | Checking a number, or re-measuring after a quarter |

Everything in the numbers above is measured, with reproducible queries in `_research/queries.md`.
Expensify changes this process often, so re-measure rather than trusting a stale figure.

## The workflow

### Phase 1: find what is in the window

```bash
python scripts/watch.py --scan      # issues in the work window, with time estimates
python scripts/triage.py --scan     # the same set, scored and ranked
```

Twice a week is enough for the two-day median. During an active pursuit, daily, because the shortest
window measured was four hours.

### Phase 2: pick one

Take the highest-scoring issue that clears BORDERLINE, then read it yourself before committing.

The score is a ranking aid built from proxies. Its most important blind spot: it can see that
MelvinBot cited no file and line, which usually means a shallow root cause, but it cannot see
whether Melvin is *right*. A confident, well-cited, wrong Melvin proposal scores as hard to beat
when it is actually the best opportunity on the board.

Pick one, at most two a week. A new contributor cannot propose on a second job until their first
pull request merges, so the slot is scarcer than the time.

```bash
python scripts/triage.py --issue 99208   # full breakdown
python scripts/watch.py --track 99208    # watch for the label
```

### Phase 3: reproduce it

Reproduce against staging with a `+`-suffixed test account. Capture exact numbered steps with the
platform and build, and a video where the bug is visual.

Never test against Concierge or in Expensify-owned public rooms. Both reach real people.

If you cannot reproduce it, that is worth posting on its own on a contested issue. It is what the
reviewer on 98791 was asking for, unsuccessfully, for three days.

### Phase 4: trace the root cause

This is the work, and it is what the proposal is judged on.

```bash
python scripts/repo.py --ensure                                    # clone or update
python scripts/repo.py --permalink src/path/File.tsx 95 97         # SHA-pinned, verified
python scripts/repo.py --blame src/path/File.tsx 95                # the PR that introduced it
```

Trace the causal chain across files rather than naming the one file where the symptom appears. The
98426 winner ran `RateField` to `MenuItem` to `useDistanceRequestState` to `DistanceRequestUtils` to
`useParticipantSubmission`, five files, each cited with a line range pinned to a commit SHA.

Pin the SHA. A `/blob/main/` link points somewhere else the next time the file changes, and
reviewers read these days later. `repo.py --permalink` pins it and verifies the lines exist, because
a confident link to the wrong code damages the proposal more than no link would.

### Phase 5: check what is already claimed

```bash
python scripts/proposals.py --issue 99208
```

Prints every proposal including MelvinBot's and any ProposalPolice already withdrew, with each root
cause extracted, so you can see what has been taken.

Expensify requires a new proposal be **meaningfully different**, and ProposalPolice automatically
withdraws anything scoring **90 percent similarity or above** against a live proposal. It judges
meaning, not wording, so rewording something you just read produces a duplicate that took longer to
write. A different root cause is different. A different phrasing of the same root cause is not.

### Phase 6: write it

**Read `references/winning-proposal-anatomy.md` first.** The six moves that won 98426:

1. Restate the problem naming the **blocked user action**, not the visual symptom.
2. Trace the chain across files, every step a pinned permalink.
3. Collapse the chain into one causal sentence. Five citations are evidence, not an explanation.
4. Name the **conceptual** confusion, not just the mechanical fault. The winner wrote that the
   component "conflates 'we have a resolvable value to display' with 'the user should be allowed to
   edit'". That sentence is what separated it from three identical-second rivals.
5. State what should **not** change and why. Bounding the change is a competence signal.
6. Sweep the regression surface: other call sites, offline, the common case, adjacent flows.
   Regressions carry a 50 percent penalty for the reviewer as well as you, so a proposal that has
   already answered "what else could this break" asks them to take much less risk.

Write it in the user's own voice, plain and brief. The template asks for plain English and warns
against walls of text. Around 6,000 to 8,000 characters is where a properly traced proposal lands.

No code diffs. A single line showing a changed condition is fine and the winner used one. A
multi-line patch is a pull request in the wrong place and breaks a documented rule.

### Phase 7: screen and arm

```bash
python scripts/proposals.py --issue 99208 --screen draft.md
python scripts/post.py --issue 99208 --draft draft.md    # dry run, checks only
```

The duplicate screen reports DANGER or INCONCLUSIVE and deliberately never reports a pass. It
compares vocabulary; ProposalPolice compares meaning. A clean lexical result proves nothing, so the
real differentiation judgment stays with you.

Then wait for the label:

```bash
python scripts/watch.py --armed
```

### Phase 8: post, then stop

```bash
python scripts/post.py --issue 99208 --draft draft.md --confirm
```

Nothing posts without `--confirm`, and that is not ceremony. Expensify's `AI_ETIQUETTE.md` makes you
personally accountable for anything posted under your name, and requires that you can explain it
without AI's help. Once a proposal is accepted you are in a technical conversation with an engineer
about a root cause you claimed. Read the draft and confirm you could defend every sentence.

Afterwards: post one proposal and stop commenting. To revise, **edit the original** and post a short
comment reading `## Proposal` then `[Updated](link)`. A second proposal is a rule violation.

If the reviewer engages, answer their actual question. If they ask for a reproduction, that is the
highest-value thing you can supply.

## Rules that disqualify

Full list with sources in `references/what-not-to-do.md`. The four that cost most:

- **No pull request before you are hired.** Applies on MelvinBot issues too.
- **No proposals before the `Help Wanted` label.** They are ignored and not reviewed.
- **One proposal per issue.** Edit to revise.
- **One job at a time until your first PR merges.**

## Honest expectations

Set these explicitly rather than letting the user discover them.

Eight to seventeen proposals per issue, several from professional contributors with automated
posting. About four new issues a week. A realistic first win is **four to eight weeks** of consistent
effort, and many weeks will correctly end with no pursuit at all because nothing cleared the bar.

Payment is about $250 less Upwork fees, arriving no sooner than seven days after the fix reaches
production, with a 50 percent penalty for any regression inside the following week.

As income this is marginal. The compounding return is a merged pull request in a five-thousand-star
repository belonging to a public company, plus direct experience of a production agentic engineering
pipeline (MelvinBot proposing, AI reviewers on PRs, ProposalPolice moderating). Say so plainly if
the user is weighing this against billable work, rather than implying the bounty is the payoff.

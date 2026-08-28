# What a winning proposal actually looks like

This is built from one worked example: the proposal that won issue 98426 on 2026-08-20. It is worth
studying closely rather than skimming, because it is the clearest evidence available of what the
reviewers actually reward, and it contradicts several things people assume.

Read it in full before writing anything:
https://github.com/Expensify/App/issues/98426#issuecomment-5357437847

## The situation it won in

The `Help Wanted` label went on at `14:40:43`. Four proposals landed at `14:40:45`, each between
5,900 and 7,500 characters. Seventeen proposals were posted in total. The reviewer picked
`abbasifaizan70` the next day with a one-line comment: "I think we can just drop the redundant
`!!rate` check here so @abbasifaizan70's proposal LGTM."

Two things follow from that, and they pull in opposite directions.

Being early is necessary. A proposal from `neerajbachani` on the same issue ran 19,370 characters,
nearly three times the winner, and was posted six hours later. It lost. Length did not compensate
for timing.

Being early is not sufficient. Three other proposals landed in the identical second and lost.
Among the simultaneous entries, the reviewer chose on quality. So the race gets you into
consideration, and the content wins it.

## The reviewer's actual decision rule

From an HTML comment inside `PROPOSAL_TEMPLATE.md`, which does not render on GitHub and which most
contributors therefore never read:

> Choose the first proposal that has a reasonable answer to all the required questions.

And, addressed to reviewers about what to reject:

> Do not approve any proposals that lack a satisfying explanation to the first two prompts. It is
> CRITICALLY important that we understand the root cause at a minimum even if the solution doesn't
> directly address it.

The bar is "reasonable and complete", not "best". Root cause outranks solution, explicitly. A
proposal with a correct fix and a hand-waved cause is rejected; a proposal with a well-established
cause and an imperfect fix can still be accepted.

## The structure that won

Six moves, in order.

### 1. Restate the problem so it names the blocked action

The winner did not describe the visual symptom. It named what the user cannot do:

> the Rate field itself is **not tappable/editable** in this state, so the user has no way to open
> the rate picker and select a valid workspace rate, they are completely blocked from submitting

A reviewer reading that knows immediately whether you understood the bug. "The rate shows an error"
is a symptom. "The user is blocked from submitting and here is the exact affordance that is
missing" is a problem statement.

### 2. Trace the causal chain across files, pinning every step

Four files, each cited with a permalink pinned to a full commit SHA and a line range:

```
https://github.com/Expensify/App/blob/79bca1613e3ed0494304d7e9b78eecad9df422a3/src/components/MoneyRequestConfirmationList/sections/RateField.tsx#L95-L97
```

The chain ran `RateField` (the gate) to `MenuItem` (why the gate disables the press handler) to
`useDistanceRequestState` (where the value comes from) to `DistanceRequestUtils.getRate` (why it
resolves to undefined) to `useParticipantSubmission` (why the stale ID survives the move).

Pin the SHA rather than `main`. A `/blob/main/` link points somewhere else the next time that file
changes, and reviewers read these days later. `scripts/repo.py --permalink` pins the SHA and
verifies the lines exist before handing you the URL.

### 3. Synthesize the chain into a single causal sentence

After the trace, the winner wrote a "Put together:" paragraph collapsing five files into one
sequence of events. This matters because a list of five citations is evidence, not an explanation.
The reviewer needs the one sentence that connects them.

### 4. Name the conceptual confusion, not just the mechanical fault

This is the sentence that most separates the winner from the other three simultaneous proposals:

> `RateField` conflates "we currently have a resolvable rate value to display" with "the user should
> be allowed to edit the rate", and disables editing in precisely the case, an unresolved or invalid
> rate, where editing is what the user needs to do.

The mechanical cause is "`isRateInteractive` requires `!!rate`". The conceptual cause is "this code
confuses two different questions". Reviewers are engineers deciding whether you understand their
codebase, and the second sentence demonstrates that in a way the first cannot.

### 5. State what should NOT change, and why

> The detection and auto-matching logic in `DistanceRequestController` and `getRate` is correct and
> shouldn't change, it's doing its job by flagging that the current rate doesn't belong to the
> destination policy. The bug is purely that `RateField` uses the wrong condition to gate editability.

Bounding the change is a competence signal. It tells the reviewer you considered the surrounding
code and are not proposing to rewrite working logic to make a symptom disappear.

### 6. Pre-answer the regression questions, systematically

The winner closed with a bulleted sweep: what happens to the display when the rate is unresolved,
why the common valid-rate case is unaffected, what happens to split and read-only flows, what
happens to navigation, what happens offline, and whether any other call site consumes the changed
value ("`isRateInteractive` is only consumed within this component, so there are no other call
sites to update").

Expensify applies a 50 percent payment penalty per regression, to the reviewer as well as to the
contributor. A proposal that has already answered "what else could this break" is asking the
reviewer to take much less risk than one that has not. This section is probably why it won.

## About code in proposals

The template says, in capitals, "DO NOT POST CODE DIFFS", and reviewers are told to push back on
anyone "posting large multi-line diffs (this is basically a PR)".

The winner still included one line inside a fence:

```ts
const isRateInteractive = !isReadOnly && iouType !== CONST.IOU.TYPE.SPLIT;
```

That is the distinction. A single line showing the changed condition is a precise way to say what
you mean. A multi-line patch is a pull request posted in the wrong place, and posting one before
being hired breaks a documented rule. `scripts/post.py` blocks diff fences, four or more added
lines, and fenced blocks over fifteen lines, while leaving a one-line change alone.

## Length

The winner was roughly 7,300 characters. The three that lost in the same second ran 5,900 to 7,500.
The 19,370-character entry lost. The template asks you to "be brief and avoid jargon" and warns
against "walls of text".

Treat length as a consequence rather than a target. Five files traced properly and a regression
sweep lands somewhere around 6,000 to 8,000 characters on a typical bug. If a draft is much shorter,
the trace is probably missing. If it is much longer, it is probably explaining things the reviewer
already knows about their own codebase.

## The template

Use the current headings from `contributingGuides/PROPOSAL_TEMPLATE.md`:

```markdown
## Proposal

### What is the root cause of that problem?

### What changes do you think we should make in order to solve the problem?

### What alternative solutions did you explore? (Optional)
```

Some winning proposals, including this one, also open with "Please re-state the problem that we are
trying to solve in this issue", an older template variant that is still widely used and still
accepted. Including it is safe and gives you somewhere to state the blocked action.

The alternatives section is genuinely optional. The winner skipped it. Do not pad it to look
thorough; a weak alternatives section reads worse than none.

## The shape of a losing proposal

Drawn from the entries that lost on 98426 and 98791:

- Describes the symptom back to the reader and calls it a root cause.
- Cites no file and line, or cites `/blob/main/` links that no longer point at the right code.
- Names one file when the cause spans several, which usually means the real cause is upstream of
  where they looked.
- Proposes a fix at the symptom site, for example suppressing an error message, rather than at the
  cause.
- Says nothing about what else the change could affect.
- Arrives hours after the label with no compensating insight.
- Reads as a reworded version of a proposal already on the thread, which is not merely weak but
  gets automatically withdrawn at 90 percent similarity.

# What gets a proposal thrown out

Every rule here is documented by Expensify, with the source named. These are not style preferences.
Several carry warnings that accumulate toward removal from the contributor programme, and one of
them halves the payment.

`scripts/post.py` enforces the mechanical ones automatically. The judgment ones are on you.

## Disqualifying

**Opening a pull request before a proposal is accepted and you are hired.**
`CONTRIBUTING.md` and `HOW_TO_WORK_WITH_MELVINBOT.md`. This holds on MelvinBot issues too, where the
reviewer usually owns the PR rather than the contributor. An unhired PR is the clearest possible
signal that you did not read the process, and it is the most common newcomer mistake.

**Posting a proposal before the `Help Wanted` label.**
`CONTRIBUTING.md` step 4: proposals submitted beforehand "will be ignored and not reviewed". The
issue is visible and discussable for days before that, which is what makes this tempting. Prepare
during the window, post after the label.

**Posting more than one proposal on an issue.**
`CONTRIBUTING.md` step 7. To revise, edit your original comment, then post a short comment reading
`## Proposal` followed by `[Updated](link-to-your-edited-comment)`. A second full proposal is a rule
violation, and ProposalPolice grades edits as well as new comments.

**Submitting proposals while another assigned issue is waiting on you.**
`CONTRIBUTING.md` step 5, which classes it as a violation of Code of Conduct Rule 1 and says
repeated warnings can lead to removal from the programme.

**Taking a second job before your first pull request merges.**
`CONTRIBUTING.md`, payment section. New contributors work one job at a time. This is a throughput
cap no workflow can route around, and it is why the choice of which issue to pursue matters more
than how many you pursue.

**Testing against Concierge, or in Expensify-owned public rooms.**
`CONTRIBUTING.md`, test accounts section. Concierge routes to the real customer support team, and
rooms like `#exfy-roadmap` contain real customers and investors. Create your own test accounts with
a `+` suffix, and use the designated test public room.

## Auto-moderated

**A proposal 90 percent similar to a live one is withdrawn automatically.**
`DUPLICATE_SIMILARITY_THRESHOLD` in `.github/actions/javascript/proposalPoliceComment/proposalPoliceComment.ts`.
ProposalPolice keeps an OpenAI conversation holding every proposal on the issue and rewrites the
offending comment into a withdrawal. Four proposals died this way on issue 98791.

The trap is that this is judged on meaning, not wording. Rewording a proposal you have just read
does not make it different; it makes it a duplicate that took longer to write. `scripts/proposals.py`
prints every existing root cause so you can see what is already claimed, and screens a draft for
word overlap. Read its output carefully: a clean lexical screen is explicitly reported as
inconclusive, because vocabulary overlap is a floor and not a proof.

**Comments that do not follow the template get classified and flagged.** The same bot checks whether
a comment is a proposal at all and whether it uses the required structure.

## Content rules

**No code diffs.** `PROPOSAL_TEMPLATE.md` says it in capitals, and reviewers are instructed to
course-correct anyone "posting large multi-line diffs (this is basically a PR)". A single line
showing a changed condition is fine and the winning proposal on 98426 used one. A patch is not.

**No skipped sections.** Reviewers are told not to approve proposals lacking a satisfying root cause
"even if the solution doesn't directly address it". An incomplete proposal is rejected regardless of
how good the fix is.

**No walls of text.** The template asks for plain English and brevity. The 19,370-character proposal
on issue 98426 lost to a 7,275-character one.

**No claiming another issue is related before a root cause is established.** Listed explicitly among
the behaviours reviewers are told to correct.

## Consequences that arrive later

**Regressions halve the payment.** If your merged fix causes a regression within 168 hours of
production deploy, a 50 percent penalty applies to you *and* to the Contributor+ who approved you.
That second half matters more than it first appears: it is why reviewers reward proposals that have
already worked through what else the change could affect, and why the regression sweep described in
`winning-proposal-anatomy.md` is worth the space it takes.

**Five days of silence can terminate the contract.** `CONTRIBUTING.md` step 13. Daily weekday
updates are expected once assigned; say so in advance if you will be unavailable.

**Payment is not immediate.** No sooner than seven days after production deploy, and the post-merge
checklist has items only you can complete before it is released.

## On using AI

`AI_ETIQUETTE.md` is short and worth reading in full. The operative standard:

> Before posting anything AI helped produce, you should be able to explain it without AI's help and
> feel confident putting your name behind it.

It explicitly prohibits submitting AI-generated code you have not tested or do not fully understand,
and posting undistilled AI output. It also says "blame AI for mistakes" is not available: the mistake
is yours regardless of the source.

This is why nothing in this skill posts automatically. Using AI to search the codebase, trace a
causal chain and draft an explanation is squarely within what the guide encourages. Posting text you
have not read is not, and the practical risk is not abstract: once a proposal is accepted you are in
a technical conversation with an engineer about a root cause you claimed, and a claim you cannot
defend costs more than the proposal was worth.

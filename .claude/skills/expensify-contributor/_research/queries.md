# Reproducible queries behind every number in this skill

Everything in `measurements.json` came from one of the commands below, run on 2026-08-23 with an
authenticated `gh` CLI. Re-run them to re-measure. If a number in the skill's references disagrees
with a fresh run, the fresh run wins and the reference should be updated.

Why this matters: Expensify changes this process often. MelvinBot and ProposalPolice are both recent
additions that reshaped the competition. A stale benchmark here would quietly send you into a race
you have already lost.

## Funnel size

```bash
# Open bounty issues right now
gh api "search/issues?q=repo:Expensify/App+is:open+is:issue+label:%22Help+Wanted%22&per_page=1" --jq '.total_count'

# New ones in the last 7 / 30 days (edit the dates)
gh api "search/issues?q=repo:Expensify/App+is:open+is:issue+label:%22Help+Wanted%22+created:%3E=2026-08-16&per_page=1" --jq '.total_count'
```

## The work window (issue creation to Help Wanted label)

```bash
N=98426
gh api "repos/Expensify/App/issues/$N" --jq '.created_at'
gh api "repos/Expensify/App/issues/$N/timeline?per_page=100" \
  --jq '.[] | select(.event=="labeled" and .label.name=="Help Wanted") | .created_at'
```

## MelvinBot presence and latency

```bash
gh api "repos/Expensify/App/issues/$N/comments?per_page=100" \
  --jq '[.[] | select(.user.login=="MelvinBot") | .created_at] | first'
```

## Competition: how many proposals, and when they fired

```bash
gh api "repos/Expensify/App/issues/$N/comments?per_page=100" \
  --jq '.[] | select(.body | test("(?i)^#+ ?Proposal")) | "\(.created_at)\t\(.user.login)\tlen:\(.body|length)"'
```

Run this on 98426 to see the four simultaneous 6-7KB proposals at `14:40:45`, two seconds after the
label. That single output is the most useful thing in this whole audit trail.

## Who won, and why

```bash
gh api "repos/Expensify/App/issues/$N/comments?per_page=100" \
  --jq '.[] | select(.body | test("(?i)LGTM|C\u002b reviewed|\ud83c\udf80")) | "\(.created_at)\t\(.user.login)\t\(.body[0:300])"'
```

The `🎀👀🎀` emoji string is the C+ signal that a proposal is being recommended to the internal
engineer. Searching for it is the fastest way to find the accepted proposal on any closed issue.

## The duplicate threshold

Not an API call, a source read. The constant lives here and is worth re-checking, because it is the
one number that can silently invalidate a proposal you spent two days on:

```bash
curl -sL "https://raw.githubusercontent.com/Expensify/App/main/.github/actions/javascript/proposalPoliceComment/proposalPoliceComment.ts" \
  | grep -n -A2 "DUPLICATE_SIMILARITY_THRESHOLD"
```

## The selection rule

Also a source read. It is inside an HTML comment, so it does not render on GitHub and most
contributors never see it:

```bash
curl -sL "https://raw.githubusercontent.com/Expensify/App/main/contributingGuides/PROPOSAL_TEMPLATE.md"
```

## Live pipeline right now

The issues currently inside the work window, which is the only set worth working on:

```bash
gh api "search/issues?q=repo:Expensify/App+is:open+is:issue+label:External+-label:%22Help+Wanted%22+sort:created-desc&per_page=20" \
  --jq '.items[] | "\(.number)\t\(.created_at[0:16])\t\(.title[0:60])"'
```

`scripts/watch.py --scan` wraps this and adds the MelvinBot check and window-age arithmetic.

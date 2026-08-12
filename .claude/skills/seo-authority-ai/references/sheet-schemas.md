# Sheet schemas

Six tabs. `push_sheet.py`'s `TABS` dict is the source of truth; this file explains what each
column is for and why the seven invariants exist.

Column headers coerce to payload keys by lowercasing, replacing spaces with underscores and
stripping `?`, `(` and `)`, so `Cited (n)` reads `cited_n`. Same convention as `seo-foundation`,
`seo-onpage` and `seo-technical`.

---

## 1. Authority Audit

`Tier | Area | Check | Observed | Threshold | Verdict | Source | Evidence`

Every check row from every script, unfiltered. The working tab, not the deliverable - it exists so
anyone can trace a finding back to the measurement that produced it and the course section that
set the threshold.

`Verdict` is `pass` / `fail` / `review` / `unknown`. `review` and `unknown` are first-class: a
judgment call and a missing credential are both real answers, and collapsing either into `pass` is
how an audit hands a client a confidently wrong document.

`Tier` is the derived 1-8 order from `checks.md`. It drives the sort and invariant 3.

## 2. Findings

`Priority | Tier | Area | Finding | Evidence | Fix | Expected Effect | Effort | Owner`

The deliverable. Populated **by hand** - `--from-results` leaves it empty on purpose, because
auto-promoting every `fail` produces exactly the forty-item export invariant 7 blocks.

## 3. AI Visibility

`Prompt | Intent | Engine | Runs | Cited (n) | Citation Rate | Stability | Brand Named Without Link | Competitors Cited | Cited URLs | Ranks Top 10 | Sampled | Cost USD`

The tab this skill exists for.

**`Runs` sits immediately beside `Cited (n)` and `Citation Rate`** so the rate cannot be read
without its sample size. That adjacency is doing real work: it is what stops a screenshot of this
tab from becoming a decontextualised percentage in a deck.

`Stability` carries **three** values, not one - `cited:`, `named:` and `first:` - because they
diverge sharply within a single prompt. Measured: the brand set was identical across runs while
first-mention flipped and citations shared nothing.

`Brand Named Without Link` is named runs minus cited runs. It is the gap between being recommended
and getting the click, and it is a specific fixable finding rather than a flat failure.

`Ranks Top 10` is the overlap-collapse column. Organic-to-citation overlap fell from 92% to ~38%,
and to 14-17% in AI Mode, so "ranks well and is not cited" is now a normal state and worth seeing
on one row.

## 4. Entity

`Signal | Identifier | Value | Source | Status | Action`

`Status` is one of present / missing / inconsistent / unknown. Holds the Wikidata Q-number, the
KGMID and its confidence score, the entity home URL, each `sameAs` URL with its HTTP status, the
canonical description, and founder-name variants.

## 5. Mentions and Platforms

`Type | Platform or URL | Where | Snippet | Linked | Description Used | Action`

`Type` is platform-presence / unlinked-mention / linked-mention / link-prospect.

`Description Used` per row is what turns the consistency finding from an assertion into something
checkable: the variants sit next to each other and the client can see them.

## 6. Local

`Signal | Observed | Threshold | Surface | Verdict | Action`

Written only when `local.applicable` passes. `Surface` is map pack / local organic / AI
recommendation, so course/35's three-surface separation is structural rather than prose. They are
different systems and a business can win one while losing another.

**No Roadmap tab.** The 90-day plan is the report's closing section. A sheet of dates is a project
plan nobody maintains.

---

## The seven blocking invariants

A sheet that contradicts itself is worse than no sheet. `push_sheet.py` refuses to write unless
these hold, and `--force` exists for the case where you have a reason. Every message names the
fix, not just the rule.

**1. No citation rate from fewer than 3 runs.** The invariant this skill leans on hardest.
Measured 2026-08-08: two ChatGPT runs of one prompt seconds apart named different winners and
shared zero cited domains. arXiv 2604.07585 puts within-prompt resampling at 34.8% of total
variance against 1.5% for brand identity. A forced row must carry
`Stability = single-sample, not a measurement` **in place of** a rate, not alongside it.

**2. No citation rate rendered without its run count.** Same premise, different failure mode: this
is how a correct measurement becomes a wrong screenshot the moment it leaves the sheet.

**3. Tier order.** No `this week` finding at a higher tier number while a lower-tier failure sits
below it. The specific inversion this catches: "add expert quotes to the top 5 pages" (tier 4)
ranked above "OAI-SearchBot is disallowed" (tier 1), which is paying to polish pages no engine may
fetch. Note that when local applies it is promoted to tier 2, so its findings carry 2, not 7.

**4. No link-quality claim without a named source.** Any link-prospect row carrying a DR, DA,
traffic estimate or toxicity score blocks unless `Source` names the tool. There is no free
backlink index, so an unattributed number here was invented. This enforces `seo-foundation`'s
existing kill list mechanically rather than by good intentions.

**5. No `pass` or `fail` on a not-connected source.** Any row whose source names Search Console,
GA4, Bing Webmaster Tools, a backlink index, or the Knowledge Graph API while it is disabled must
be `unknown`. Same class as `seo-technical`'s field-data invariant, generalised to every absent
credential.

**6. No evidence-free finding.** A claim with nothing to point at is an opinion, and the client
cannot check it.

**7. No more than five `this week` findings.** Three beat forty.

### Two non-blocking warnings

- `local.applicable` passed but the Local tab is empty.
- `aivis.py` never ran, in which case the report's section 4 must read **not sampled** rather than
  implying zero. Those are different findings.

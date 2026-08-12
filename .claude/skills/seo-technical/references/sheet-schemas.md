# Sheet schemas

Six tabs. `push_sheet.py`'s `TABS` dict is the source of truth; this file explains what each
column is for and why the six invariants exist.

Column headers coerce to payload keys by lowercasing and replacing spaces with underscores,
so `Internal Links Pointing Here` reads `internal_links_pointing_here`. Same convention as
`seo-onpage` and `seo-foundation`.

---

## 1. Technical Audit

`Tier | Area | Check | Observed | Threshold | Verdict | Source | Evidence`

Every check row from every script, unfiltered. This is the working tab, not the deliverable -
it exists so a developer can trace any finding back to the measurement that produced it and
the course section that set the threshold.

`Verdict` is one of `pass` / `fail` / `review` / `unknown`. `review` and `unknown` are
first-class: a judgment call and a missing data source are both real answers, and collapsing
them into `pass` is how an audit hands a client a confidently wrong document.

`Tier` is the course/21 pyramid level, 1 to 9. It drives the sort and invariant 1.

---

## 2. Findings

`Priority | Tier | Area | Finding | Evidence | Fix | Expected Effect | Effort | Owner`

The deliverable. Populated by hand, deliberately - `--from-results` leaves it empty, because
auto-promoting every `fail` produces exactly the forty-item export that invariant 6 blocks.

---

## 3. Indexation

`URL | Status | In Sitemap | Indexable | Blocked Reason | Declared Canonical | Google-Selected Canonical | Action`

`Google-Selected Canonical` is filled by hand from URL Inspection. It stays blank rather than
guessed, and a blank column with a known reason is more useful than a populated one that is
inferred.

---

## 4. Redirects

`From URL | To URL | Hops | Status Chain | Type | Internal Links Pointing Here | Action`

`Internal Links Pointing Here` is the column that turns a redirect list into a work list: a
redirect with fifteen internal links pointing at it is fifteen routine internal hops that
should be repointed at the destination.

---

## 5. Architecture

`URL | Click Depth | Internal Links In | Template | In Sitewide Nav | Has Breadcrumbs | Action`

`Click Depth` is shortest link path, not folder depth, and it is blank for orphans rather
than 0 - an unreachable page is not a homepage.

`Template` matches `vitals.py`'s grouping so the two tabs join.

---

## 6. Core Web Vitals

`Template | Sample URL | Pages | Data Source | LCP | INP | CLS | Verdict | Primary Fix`

`Data Source` must name field or CrUX for a `pass`/`fail` verdict. `Pages` is the size of the
template group, which is what makes a fix worth its effort: one change resolving eighty URLs
is a different proposition from one resolving one.

---

## The six blocking invariants

A sheet that contradicts itself is worse than no sheet. `push_sheet.py` refuses to write
unless these hold, and `--force` exists for the case where you have a reason.

**1. Tier order.** No `this week` finding from a lower tier while a higher-tier failure sits
lower in the priority list. course/21 is explicit that the order is not negotiable. This is
the invariant that matters most and the one an automated tool always violates, because
schema and speed findings are the easy ones to generate.

**2. No Core Web Vitals verdict from lab data.** Google ranks on field data only, and a page
can score 100 in Lighthouse and fail the field assessment. A lab-sourced row is `unknown`.

**3. No redirect fix that creates a chain.** An action pointing at a URL that is itself a
redirect source on the same tab moves the chain rather than flattening it.

**4. No junk kept in the sitemap.** A non-200, noindexed or cross-canonicalized URL marked
`keep` contradicts course/22's contents rule. Junk in the sitemap trains Google to distrust
the whole file.

**5. No evidence-free finding.** A claim with nothing to point at is an opinion, and the
client cannot check it.

**6. No more than five `this week` findings.** Three beat forty. An audit naming forty
problems is the standard output of an automated tool and it is why tool exports do not sell.

Each problem message names the fix, not just the rule. A validator that says "invalid" and
stops is a second problem.

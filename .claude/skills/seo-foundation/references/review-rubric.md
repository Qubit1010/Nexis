# Review mode - scoring an existing keyword strategy

Use when a client already has a keyword list, a content plan, or an agency deliverable, and
the question is whether it is any good.

Review scores what exists. It does not quietly rebuild it. If the answer is that there is
not enough there to audit, say so and offer build mode - see the handoff rule at the end.

---

## The scorecard

Seven rows. Each is **Strong / Workable / Weak / Missing**.

| # | Dimension | Strong looks like |
|---|---|---|
| 1 | **Grounded in the customer** | Keywords use the customer's vocabulary. You can tell which business this is from the list alone. |
| 2 | **Intent classified** | Every keyword carries an intent, and the intents match what the SERPs actually return. |
| 3 | **Difficulty read honestly** | Difficulty comes from reading SERPs, or from a tool score explicitly labelled as an estimate. Not absent, not presented as fact. |
| 4 | **Prioritised by business value** | Sorted by relevance and intent. Not by volume. Not alphabetically. |
| 5 | **Clustered** | Keywords grouped into topics, one intent per group, groups formed from evidence rather than by eye. |
| 6 | **Mapped to pages** | Every cluster names one target URL, with a status. No URL serves two clusters. |
| 7 | **Measurable** | A baseline exists, or is at least specified: GSC connected, GA4 retention set, target queries named. |

### Scoring notes

- **Row 4 is the one that fails most often.** A volume-sorted list is the default output of
  every keyword tool, so it is what most agency deliverables are. Say it plainly.
- **Row 6 is the one nobody has.** Most "keyword strategies" are a list with no mapping at
  all. Missing here is normal and is usually the single highest-value fix.
- **Row 3 Weak** covers the common case of an untouched Ahrefs KD column. The problem is
  not that the number is there, it is that nothing was read off the SERP to check it.
- **Row 1 Missing** is the deepest problem even though it looks the softest. A list that
  would fit any competitor in the category was not built from this client's customers.

---

## Output structure

```
# SEO Foundation Review - <Client>

## Verdict
   the 7-row scorecard, then one paragraph: is this usable as-is, fixable, or does it
   need rebuilding

## What's working
   name it specifically. Most deliverables get something right, and leading with it
   makes the criticism land instead of bounce.

## The critical gaps, ranked
   ordered by what it costs the client, not by scorecard order

## Row by row
   Current -> Problem -> Fix, for every row scoring Weak or Missing

## Rewritten pieces
   fix the highest-value ones concretely. If priority sorting is wrong, re-sort their
   top 20 and show both orderings side by side - the difference makes the argument
   better than the explanation does.

## What to do next
   3-5 actions in order, with the first one small enough to do this week
```

---

## Reading order

1. **Look for a target URL column first.** Its absence tells you most of what you need
   before reading a single keyword.
2. **Check the sort.** Descending volume is the tell for a tool-generated list.
3. **Sample 5 keywords across the range and SERP-check them.** `serp_features.py` on five
   queries costs five credits and turns "this looks generic" into evidence. Do this before
   writing anything - a review with no live SERP data is an opinion.
4. **Check intent labels against those SERPs.** Mislabelled intent is common and it
   invalidates the mapping downstream.
5. **Look for duplicate target URLs.** If they mapped at all, check the invariant.
6. **Then score.**

---

## Handoff rule

**If 5 or more rows are Missing, or rows 1 and 6 are Missing and the rest are Weak, there
is not enough here to audit.** Say so directly, score it honestly anyway so the client can
see why, and offer build mode.

The failure to avoid is a review that quietly turns into a rebuild without anyone agreeing
to it - the client asked "is this good", and the answer is "no, and here is what it would
take", not four hours of unrequested work.

## Pushback

If the client defends a Weak score, quote their own row and the criterion. If they are
right, change it. If they are not, hold it. The most common defence is "our agency said
volume is what matters" - the answer is the 30x tool variance [s290] and an offer to show
their own list re-sorted by relevance.

Citations `[sN]` resolve via `seo-advisor/_research/sources.json`.

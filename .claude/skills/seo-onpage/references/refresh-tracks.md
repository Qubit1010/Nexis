# Refresh, Consolidate, Prune

`course/19`. Every URL gets exactly one track. No blanks.

Deleting pages to improve rankings feels wrong and is frequently correct: thin content in
one section suppresses good content elsewhere on the same domain `[practitioner]`. A site
with 400 pages where 300 are thin is usually outperformed by the same site with 100 good
ones. After a core update the playbook is subtractive first.

```bash
python scripts/inventory.py --site https://acme.com --gsc-csv export.csv \
  --cluster-map map.json --out inventory.json
```

---

## The four tracks

| Track | When | What it means concretely |
|---|---|---|
| **keep** | Working, no structural problem | Leave it. Revisit on the refresh cycle. |
| **update** | Ranks but underperforms, or is thin but supported | A real update, defined below |
| **merge** | Duplicates another page's job | Consolidate and 301 into the winner |
| **remove** | No traffic, no links, no purpose | 301 to the closest relevant page, or 410 |

A blank track means the decision was avoided. Avoided decisions are how a site accumulates
300 pages nobody will defend, so `push_sheet.py` blocks the write on any blank.

---

## The Search Console problem

The audit sheet wants clicks, impressions and backlinks. **None are available here.** `gws`
has no Search Console service and there is no credential; no free backlink API exists.

`inventory.py` therefore marks every track with a confidence:

- **high** - assigned with real GSC data merged via `--gsc-csv`
- **low** - inferred from crawl structure alone (inbound links, word count, duplicate
  titles, cluster membership)

A `low` track is a hypothesis. Say so in the report. `course/20` is explicit that without
Search Console you are inferring rather than diagnosing and should say so, and this is the
place that matters most - the recommendation is to delete someone's pages.

**Getting the data:** Search Console -> Performance -> Search results -> last 6 months ->
Pages tab -> Export -> CSV. Then `--gsc-csv <file>`. Fifteen minutes of the client's time
turns the weakest half of this audit into the strongest.

---

## Detection, when GSC is connected

- **Decay:** last 3 months vs the previous 3, sorted by click difference **ascending**.
- **The position 5-15 report:** pages ranking just off the top. Position 8 to position 4 is
  roughly **400% more clicks** `[practitioner]`, and these are the cheapest wins on the site.
- **Zero-traffic audit:** no clicks and no impressions in 6 months. **Cross-check backlinks
  before removing anything.**
- **Intent drift:** re-search the top 10 queries. If what ranks has changed shape, the page
  is answering a question nobody is asking any more.

Without GSC, the usable signals are: orphaned and thin, near-duplicate titles or H1s, and
cluster membership from `seo-foundation`'s map.

---

## What counts as an update

**Real:** new data, new sections for questions that have emerged since, removing advice that
is no longer true, re-reading the SERP for intent drift, adding the evidence modifiers from
`course/14` (a statistic, a named source, something first-hand).

**Not:** changing the date. Swapping a few words. Adding a filler paragraph. Fake freshness
is a recognized pattern and it does not work.

Cadence: a **13-week** cycle on priority pages `[practitioner]`. AI-cited content is
reported to be about **25.7% fresher** than the average `[s294, s128]` `[practitioner]`.

---

## Consolidation procedure

Order matters here; getting it wrong loses the equity you were trying to concentrate.

1. **Pick the winner** - most backlinks, most traffic, best URL.
2. **Integrate, do not concatenate.** Merging two 800-word posts into a 1,600-word post that
   says everything twice makes both worse.
3. **301 every loser to the winner.** Never to the homepage - an irrelevant redirect is
   treated as a soft 404 and the equity evaporates.
4. **Update internal links** to point at the winner directly, not through the redirect.
5. **Keep the redirects indefinitely.**

## Removal procedure

- 301 to the closest relevant page. If there genuinely is not one, **410 Gone** drops it
  from the index faster than a 404 `[practitioner]`.
- **Never mass-delete without checking backlinks.** A page with no traffic and three
  editorial links is an asset with a distribution problem, not a liability.
- Remove in batches, not all at once, so the effect is attributable.

---

## The inventory schema

`course/19`'s eight columns, plus the two this skill adds.

| Column | Source here |
|---|---|
| URL | crawl |
| Clicks, last 6 months | Search Console, or `not connected` |
| Impressions, last 6 months | Search Console, or `not connected` |
| Internal links pointing at it | `links.py` |
| External backlinks | `not connected` - no free API |
| Cluster it belongs to | `seo-foundation`'s Keyword Map |
| Last meaningful update | client records, or `not connected` |
| **Track** | assigned, never blank |
| Reason | added here - a track with no reason is unexecutable |
| Confidence | added here - high with GSC, low without |

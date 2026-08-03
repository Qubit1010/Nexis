# On-Page & Content - Section 19: Refresh, Consolidate, Prune

*Deleting pages to improve rankings feels wrong and is frequently correct.*

**Bottom line:** Publishing is the start of a page's life. AI-cited content runs about 25.7%
fresher than uncited content, and thin pages in one part of a site can suppress good content
elsewhere on the same domain. Every page you own is on one of four tracks: keep, update,
merge, or remove.

---

## The four tracks

Every URL on your site is one of these. Decide deliberately rather than by neglect.

**Keep.** Performing well, still accurate, still matches intent. Leave it and re-check on
schedule.

**Update.** The topic still matters, the page has decayed. Most of your content lives here.

**Merge.** Two or more pages serving the same intent. Consolidate into the strongest and 301
the rest. This is the cannibalization fix from Section 8.

**Remove.** No traffic, no links, no strategic purpose, and no realistic path to any. Redirect
to the nearest relevant page, or return 410 if there is nowhere sensible to send people.

## Why pruning works

From Section 3: evidence points to **domain-level quality weighting**, where thin or
low-value content in one section can suppress genuinely good content elsewhere on the same
domain. `[practitioner]`

That is why the standard post-core-update playbook is subtractive first: consolidate, remove,
then add. A site with 400 pages where 300 are thin is usually outperformed by the same site
with 100 good ones.

The emotional obstacle is real. Those pages took work. Sunk cost is not a ranking factor.

## The refresh cycle

**13 weeks on priority pages** is the working recommendation, with AI-cited content measured
at roughly **25.7% fresher** than uncited content. `[practitioner]`

That does not mean rewriting everything quarterly. It means reviewing priority pages
quarterly and updating what has decayed.

**What counts as a real update:**

- New data replacing outdated numbers
- New sections covering questions that emerged since publication
- Removing advice that is no longer true
- Re-checking the SERP, because intent may have moved (Section 4)
- Adding evidence, from the Section 14 modifiers

**What does not count:** changing the date, swapping a few words, adding a paragraph of
filler. Google is measuring whether the content changed meaningfully, not whether the
timestamp did. Fake freshness is a recognized pattern and it does not work.

## Finding what needs work

**Decay detection in Search Console.** Performance, compare last 3 months to the previous 3
months, sort by click difference ascending. The biggest losers are your update queue.

**The position 5 to 15 report.** From Section 10, the highest-return view in Search Console.
These pages already rank and already earn impressions. Moving position 8 to 4 is roughly 400%
more clicks.

**Zero-traffic audit.** Pages with no clicks and no impressions in 6 months. Cross-check
against internal links and backlinks before removing anything: a page with no traffic but real
backlinks should be merged, not deleted, so the links survive.

**Intent drift.** Re-search your top 10 queries. If the SERP now returns a different content
type than when you wrote the page, the page is mismatched and needs restructuring, not
refreshing.

## How to consolidate properly

1. **Pick the winner.** Usually the page with the most backlinks, traffic, or the best URL.
2. **Merge the content.** Take what is genuinely valuable from the losers into the winner.
   Do not just concatenate, integrate.
3. **301 every loser to the winner.** Not to the homepage. A redirect to an irrelevant page
   is treated as a soft 404.
4. **Update internal links** to point directly at the winner rather than through a redirect.
5. **Keep the redirects in place.** Indefinitely. Removing them later breaks external links.

## How to remove properly

- **301 to the closest relevant page** if one exists.
- **410 Gone** if nothing is relevant. It signals permanent removal and drops the URL from the
  index faster than a 404. `[practitioner]`
- **Never mass-delete without checking backlinks.** A page with external links has value even
  with no traffic. Redirect it.
- **Do the removal in batches** and watch what happens, rather than deleting 200 pages in one
  afternoon.

## The audit that drives it

Build one row per URL:

| Column | Source |
|---|---|
| URL | crawl |
| Clicks, last 6 months | Search Console |
| Impressions, last 6 months | Search Console |
| Internal links pointing at it | crawl |
| External backlinks | Ahrefs, Semrush, or Search Console Links |
| Cluster it belongs to | your Section 8 map |
| Last meaningful update | your records |
| **Track** | keep / update / merge / remove |

The Track column is the deliverable. Everything else exists to decide it.

> **Why this matters:** most sites accumulate content and never subtract. That is how a site
> ends up with 300 pages, 40 of which produce everything and 260 of which are quietly
> suppressing them. The subtraction is the work almost nobody does, and it is often the
> single highest-return action available on an established site.

## Do this now

1. **Build the audit sheet** with the columns above. Even a rough version on 50 URLs is
   useful.
2. **Run decay detection:** Search Console, last 3 months versus previous 3 months, sorted by
   click loss.
3. **Run the zero-traffic query:** no clicks and no impressions in 6 months.
4. **Cross-check zero-traffic pages against backlinks** before marking anything remove.
5. **Assign a track to every URL.** Keep, update, merge, or remove. No blanks.
6. **Execute one merge properly:** pick the winner, integrate the content, 301 the loser,
   update internal links.
7. **Remove or redirect five genuinely dead pages.**
8. **Update your single highest-value decayed page**, with real changes not a date bump.
9. **Put a quarterly reminder in your calendar** to re-run this.

## Capstone step

Every URL on your capstone site now has an assigned track, one merge is complete, dead pages
are removed or redirected, and your highest-value decayed page is genuinely updated. The site
is now smaller and stronger, which is the point.

## Key takeaways

- Every URL is on one of four tracks: keep, update, merge, remove. Decide deliberately, because
  neglect defaults everything to keep.
- Thin content in one part of a site can suppress good content elsewhere on the domain. That is
  why the post-core-update playbook is subtractive first.
- A real update replaces data, adds sections, and removes what is no longer true. Changing the
  date is not an update and does not work.
- Never delete a page with backlinks. Redirect it, so the links survive.

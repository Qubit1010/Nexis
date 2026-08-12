# Competitor discovery - search competitors are not business competitors

The single most useful correction this phase makes: **the sites beating a client in search
are frequently not the companies the client thinks of as rivals.**

A local accountancy firm names three other local firms. Page one for their money terms is
owned by a national comparison site, a bank's content hub, and a software vendor's blog.
None of those three are business competitors. All three are taking the traffic.

Both halves of that gap are findings, and section 2 of the report is where they go.

---

## The procedure

Three to five seed searches, so a domain has to **recur** to count. A domain appearing on
one seed is weak evidence.

```bash
python scripts/collect.py competitors \
  --seeds "seed one,seed two,seed three" \
  --business-competitors "rival1.com,rival2.com" \
  --out competitors.json
```

The script counts domains across the organic results, drops aggregators and platforms,
ranks what remains by appearances, and reconciles against the business list.

### What gets excluded, and why

Aggregators, marketplaces, UGC platforms and big publishers occupy slots on commercial
queries everywhere. They are not competitors you displace with a better page, and leaving
them in produces a "competitor list" of Reddit, YouTube and Forbes that tells you nothing.

`EXCLUDE_FROM_COMPETITORS` in `collect.py` holds the list (major platforms, UGC domains,
review aggregators, big-publisher tech and finance titles, and directory sites). They still
appear in `excluded_aggregators` so nothing is hidden - and that list is itself worth
reading, because **a page one full of aggregators is a signal**: the category has no strong
independent publishers, which usually means it is winnable.

**When to override it.** If a client competes *with* an aggregator - a directory business,
a review site, a marketplace - the exclusion list is wrong for them. Edit the seeds or read
`runners_up` and the excluded list directly, and say in the report that the default
exclusions were bypassed.

### Reading the output

| Field | What it tells you |
|---|---|
| `search_competitors` | the top domains by appearances, with best position |
| `recurring` | appeared on more than one seed. Non-recurring is weak evidence. |
| `also_a_business_competitor` | matched against the supplied list |
| `runners_up` | the next five. Check these when the top five look wrong. |
| `excluded_aggregators` | what was dropped, so the exclusion is auditable |
| `reconciliation.search_only_not_on_the_business_list` | **beating them in search without competing commercially** |
| `reconciliation.business_only_absent_from_page_one` | **commercial rivals invisible in search** |

---

## What each side of the delta means

**Search-only competitors.** Usually publishers, software vendors with content programmes,
or national players ranking in a local market. They are winning attention at the moment the
customer is deciding. They are also frequently beatable, because a comparison article
written by a vendor with no local knowledge is thin against one written by an operator.

**Business-only competitors (absent from page one).** The client's real rivals are not
doing SEO. This is the strongest possible argument for the engagement and it should be said
plainly in the report: the category is open, and being first costs less now than it will
after one of them starts.

Be careful with the inverse read. Rivals absent from page one may be winning through
referral, paid, or relationships. It means the search channel is open, not that they are
losing.

---

## What this does not do

**No backlink or authority data.** There is no free API for it - Ahrefs Webmaster Tools
covers owned domains only. `sitelinked_results` in the SERP read is the closest observable
proxy for "big recognisable brand", and it is a proxy, not a metric. Say so rather than
implying a Domain Rating was checked.

**No competitor keyword export.** Getting the full list of what a competitor ranks for
requires a paid tool. What this does instead is crawl their site for the topics they cover
(Phase 3, layer 4), which finds the content gap without the keyword volumes.

**Note for the report.** When the client asks "what do our competitors rank for", the
honest answer is that this method finds *who* ranks and *what topics they cover*, not their
full keyword footprint. If they want the latter, that is a paid tool and a real cost - route
the pricing conversation to `seo-advisor`.

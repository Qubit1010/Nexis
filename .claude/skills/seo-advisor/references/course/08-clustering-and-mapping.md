# Foundations - Section 8: Clustering and Mapping

*Two hundred keywords is not a plan. One page per intent, every page owning its cluster, is.*

**Bottom line:** Clustering turns a keyword list into a site structure. The rule is one
search intent, one page, one cluster, and clusters are formed by shared SERP results rather
than by similar wording. Do this properly and you also find the cannibalization already
costing you rankings on pages you published years ago.

---

## Why clustering, and not a page per keyword

The old model was one page per keyword. It does not work now and has not for years, for
three reasons.

**Google ranks pages for hundreds of queries, not one.** A page that ranks well typically
ranks for a large tail of related phrasings. Building a separate page for each variant splits
what should be one strong page into several weak ones.

**Search engines understand topics, not strings.** The 2024 API leak surfaced
`siteFocusScore`, which corroborates that topic concentration is measured directly. Depth on
a topic is a signal in itself. `[practitioner]`

**AI retrieval rewards coverage.** Sites with **5 or more interconnected pages on a topic**
are reported **3.2x more likely to be cited** by AI platforms, and sites with 80%+ topical
coverage retain **85.4% of AI visibility** through query fan-out variation. Fragmentation is
now penalized twice, once by Google and once by the answer engines. `[practitioner]`

## The clustering rule

> **Cluster by shared SERP outcome, not by shared wording.**

Take two queries. Search both. Compare the top ten.

- **Substantially the same results?** Same intent. One page. They belong in one cluster,
  regardless of how differently they are worded.
- **Different results?** Different intent. Two pages, even if the phrases look nearly
  identical.

This is the only reliable test, because it uses Google's own judgement rather than your
intuition about language. `[practitioner]`

Worked example. "seo audit" and "seo site audit" almost certainly return the same results:
one cluster, one page. "seo audit" and "seo audit tool" probably do not, because the second
is looking for software: two pages, two intents. The words are closer in the second pair and
the intents are further apart.

**The practical shortcut** for a 200-row list: sort by your Section 4 intent classification
first, then within each intent group by topic, then SERP-check only the pairs you are unsure
about. You do not need to check all 200 manually.

## Anatomy of a cluster

Each cluster has one **primary query**, the clearest expression of the intent, and a set of
**secondary queries** that are the same intent phrased differently, including the long
conversational and fan-out variants from Section 6.

One page owns the cluster. It targets the primary query in the title and the secondaries
naturally throughout the content. You are not sprinkling keywords, you are making sure the
page genuinely covers the ground those phrasings represent.

## Pillars and clusters

Clusters group into topics, and topics get a structure:

- A **pillar page**, comprehensive, typically **2,500 to 4,000 words**, covering the whole
  topic broadly.
- **8 to 15 cluster pages**, each going deep on one sub-intent.
- **Bidirectional internal links**: pillar links down to every cluster page, every cluster
  page links back up to the pillar.

Bidirectional linking is reported to raise AI citation probability **2.7x**, and clustered
content to generate **30 to 43% more traffic** than standalone posts. Both are single-vendor
practitioner findings, so treat the multipliers as directional, but the structural logic is
sound and corroborated by `siteFocusScore`. `[practitioner]`

Do not build a pillar for every topic. Build one for the topic you most need to own, get the
cluster genuinely covered, then move on. One complete cluster beats four half-built ones.

## Cannibalization

This is the payoff for doing the mapping honestly on an existing site.

**Cannibalization** is two or more of your pages targeting the same intent. It feels like
extra coverage and functions as self-competition: your internal links split between them,
Google is unsure which to rank, and both underperform the single page you should have had.

How to find it:

1. **Search Console, Performance, filter by a query.** Look at Pages. If several of your URLs
   pick up impressions for the same query, that is cannibalization.
2. **`site:yourdomain.com <topic>` in Google.** If four of your pages come back covering the
   same ground, same conclusion.
3. **Watch for position instability.** A query where your ranking URL keeps changing is Google
   flip-flopping between candidates.

How to fix it, in order of preference:

- **Consolidate.** Merge the pages into the strongest one and **301 the others to it.** Best
  outcome: combined signals, one strong page.
- **Differentiate.** If they genuinely serve different intents, rewrite so each clearly does,
  and fix internal links and titles to match.
- **Prune.** If a page adds nothing, remove it and redirect. Recall from Section 3 that
  removing thin content is part of the standard post-core-update playbook.

Consolidation is almost always right when the intents match, and almost always resisted
because deleting pages feels like losing something.

## The keyword map

The output of this section. One row per cluster:

| Column | Contents |
|---|---|
| **Cluster name** | plain-language topic |
| **Primary query** | the main target |
| **Secondary queries** | every variant in this cluster |
| **Intent** | one of the six, from Section 4 |
| **Target URL** | the one page that owns it, existing or planned |
| **Status** | exists and fine, exists and needs work, needs creating, or merge into another |
| **Priority** | from your Section 7 relevance x intent score |
| **Click availability** | from Section 5 |

**Every cluster maps to exactly one URL, and no URL appears twice.** If a URL shows up on
two rows, you have found cannibalization, and one of those rows needs merging.

That constraint is the entire point. A keyword map that lets one URL serve three clusters is
a wish list, not a map.

> **Why this matters:** this is the artifact everything else hangs off. Content briefs come
> from it, internal linking comes from it, and the audit in Section 20 checks against it.
> Most sites have no keyword map, which is why their content plans are a list of article
> ideas rather than a structure.

## Do this now

1. **Group your scored sheet by intent**, using your Section 4 classifications.
2. **Within each intent group, cluster by topic.** Fast pass, by eye.
3. **SERP-check every pair you are unsure about.** Same results means one cluster. Aim to
   check 15 to 25 pairs, not all of them.
4. **Name each cluster** and pick its primary query.
5. **Map each cluster to exactly one URL.** Existing page where one fits, planned URL where
   none does.
6. **Look for duplicate URLs across rows.** Any repeat is cannibalization. Mark those rows
   "merge".
7. **Verify against Search Console.** Filter by your top 5 primary queries and check whether
   multiple pages are picking up impressions for each.
8. **Pick your first pillar.** One topic, the one you most need to own. Sketch the pillar plus
   8 to 15 cluster pages, marking which already exist.
9. **Sort by priority.** The top 10 rows are your work queue for Tier 2.

## Capstone step

You have a finished keyword map: every cluster mapped to exactly one URL, cannibalization
identified and marked for merging, one pillar planned, and a prioritized work queue. This is
the deliverable that made Tier 1 worth doing, and Tier 2 executes against it page by page.

## Key takeaways

- Cluster by shared SERP results, not by similar wording. If two queries return the same top
  ten, they are one page regardless of phrasing.
- One cluster, one URL, and no URL on two rows. A map that breaks that constraint is a wish
  list.
- Pillar plus 8 to 15 cluster pages with bidirectional links. Depth on one topic beats
  shallow coverage of four, and both Google and AI retrieval reward the concentration.
- Cannibalization feels like extra coverage and functions as self-competition. Consolidating
  and redirecting is usually right and usually resisted.

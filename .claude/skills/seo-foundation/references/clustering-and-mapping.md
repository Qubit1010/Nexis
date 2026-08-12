# Clustering and mapping

Two hundred keywords is not a plan. One page per intent, each owning its cluster, is.

The old model of one page per keyword stopped working years ago. Google ranks a page for
hundreds of queries, so building a separate page per variant splits what should be one
strong page into several weak ones. Search engines understand topics rather than strings.
And AI retrieval rewards concentration: sites with **5+ interconnected pages on a topic**
are reported **3.2x more likely to be cited** by AI platforms, and 80%+ topical coverage
retains **85.4%** of AI visibility through query fan-out `[practitioner]` [s288, s110].
Fragmentation is now penalised twice.

---

## The clustering rule

> **Cluster by shared SERP outcome, not by shared wording.**

Take two queries. Search both. Compare the top ten.

- **Substantially the same results?** Same intent. One page, however differently worded.
- **Different results?** Different intent. Two pages, even if the phrases look nearly identical.

This is the only reliable test because it uses Google's own judgement rather than our
intuition about language.

**Worked example.** "seo audit" and "seo site audit" return the same page one: one cluster.
"seo audit" and "seo audit tool" do not, because the second wants software: two clusters.
The words are closer in the second pair and the intents are further apart.

## How the script implements it

```bash
python scripts/cluster.py --file queries.txt --out clusters.json --threshold 3
```

**Threshold: 3 shared URLs in the top 10.** Lower it and unrelated queries merge; raise it
and genuine clusters fragment. Whole URLs are compared, not domains - two different pages
on the same big publisher indicate a big publisher, not shared intent.

**Complete linkage.** A query joins a cluster only if it clears the threshold against
*every* member already in it. Single-linkage would chain (A matches B, B matches C, so A
and C merge despite sharing nothing), and anchoring only to a pivot has the same hole - two
members can each overlap the pivot and share nothing with each other.

This errs toward splitting on purpose. A wrong split leaves a small cluster you merge in
seconds. A wrong merge gives one page two intents, which stays invisible until the page
fails to rank for either.

**The course prescribes SERP-checking 15-25 uncertain pairs** because it assumes manual
work. Every SERP is already cached from Phase 4, so all pairs are compared at zero extra
cost. That is a strict improvement on the taught method, not a shortcut around it.

### What to read in the output

- **`borderline_pairs`** - pairs within one URL of the threshold. These are the judgment
  calls and the only ones worth your time. Read them.
- **`singleton_count`** - a cluster of one is either a genuinely distinct intent or an
  under-collected topic. A few are normal. Mostly singletons means the threshold is too
  strict for this niche (try 2) or the candidates are too scattered.
- **`queries_dropped_no_serp`** - returned nothing. Usually a typo or a query nobody makes.

**You name every cluster** and confirm its primary query. The script picks the most
connected member, which is usually the clearest expression of the intent and occasionally
is not.

---

## Anatomy of a cluster

One **primary query** (the clearest expression of the intent) and a set of **secondary
queries** (the same intent phrased differently, including the long conversational and
fan-out variants).

One page owns the cluster. It targets the primary query in the title and covers the
secondaries naturally. You are not sprinkling keywords, you are making sure the page
genuinely covers the ground those phrasings represent.

## Pillars

- A **pillar page**, comprehensive, **2,500-4,000 words** `[practitioner]` [s288, s128]
- **8-15 cluster pages**, each deep on one sub-intent
- **Bidirectional internal links** - pillar down to each, each back up to the pillar

Bidirectional linking is reported at **2.7x** AI citation probability, and clustered
content at **+30-43%** traffic over standalone posts. Both single-vendor practitioner
findings, so treat the multipliers as directional; the structural logic holds regardless.

**Do not build a pillar for every topic.** Pick the one they most need to own, cover the
cluster genuinely, then move on. One complete cluster beats four half-built ones.

---

## The keyword map

One row per cluster. Eight columns, exactly:

| Column | Contents |
|---|---|
| **Cluster name** | plain-language topic |
| **Primary query** | the main target |
| **Secondary queries** | every variant in this cluster |
| **Intent** | one of the six |
| **Target URL** | the one page that owns it, existing or planned |
| **Status** | `exists and fine` / `exists and needs work` / `needs creating` / `merge into another` |
| **Priority** | Relevance x Intent value, from Phase 5 |
| **Click availability** | from Phase 4, or `unknown` below the top 20 |

> **Every cluster maps to exactly one URL, and no URL appears twice.**

That constraint is the entire point. A map that lets one URL serve three clusters is a wish
list, not a map. `push_sheet.py` enforces it and refuses to write until it holds.

This is the artifact everything else hangs off: content briefs come from it, internal
linking comes from it, and every later audit checks against it. Most sites have no keyword
map, which is why their content plans are lists of article ideas rather than a structure.

---

## Cannibalization

Cannibalization is two or more pages targeting the same intent. It feels like extra
coverage and functions as self-competition: internal links split, Google is unsure which to
rank, and both underperform the single page that should have existed.

**How the map finds it:** a URL appearing on two rows *is* the finding. No separate audit
needed.

**Confirm it independently:**
1. Search Console, Performance, filter by the query, check Pages. Several URLs picking up
   impressions for one query confirms it.
2. `site:clientdomain.com <topic>` in Google.
3. Position instability - a query whose ranking URL keeps changing is Google flip-flopping.

**Fix, in order of preference:**

| Action | When | Outcome |
|---|---|---|
| **Consolidate** | intents genuinely match | merge into the strongest page, 301 the others. Combined signals, one strong page. |
| **Differentiate** | they serve genuinely different intents | rewrite so each clearly does, fix titles and internal links to match |
| **Prune** | the page adds nothing | remove and redirect |

Consolidation is almost always right when intents match, and almost always resisted because
deleting pages feels like losing something. Say so plainly when recommending it.

Citations `[sN]` resolve via `seo-advisor/_research/sources.json`.

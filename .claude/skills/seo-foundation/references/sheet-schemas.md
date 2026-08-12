# Sheet schemas and the payload shape

Six tabs. The keyword map is the deliverable, but it is unreadable without the evidence
behind it - someone should be able to question a row in the map and find the SERP read that
produced it two tabs over.

```bash
python scripts/push_sheet.py --payload payload.json --validate-only
python scripts/push_sheet.py --payload payload.json --title "SEO Foundation - <Client>"
```

`--validate-only` first, always. It catches the duplicate-URL problem before a Sheet exists.

---

## The payload

One JSON file, six keys. Field names are the column headers lowercased with spaces as
underscores - `push_sheet.py` maps them automatically, and missing fields become empty
cells rather than errors.

```jsonc
{
  "keywords": [{
    "query": "best crm for small business",
    "source": "autocomplete",          // autocomplete | paa | related | persona | community | competitor | fan-out | gsc
    "intent": "Commercial investigation",
    "relevance": 5, "intent_value": 4, "priority": 20,
    "click_availability": "unknown",   // healthy | reduced | effectively zero | unknown
    "winnability": 4.5,
    "cluster": "crm comparison",
    "volume_manual": "",               // stays empty unless a human pastes real figures
    "notes": "UGC at position 1"
  }],
  "clusters": [{
    "cluster_name": "crm comparison", "primary_query": "best crm for small business",
    "secondary_queries": ["top crm small business", "crm software comparison"],
    "intent": "Commercial investigation", "size": 3, "avg_priority": 18.7
  }],
  "keyword_map": [{
    "cluster_name": "crm comparison", "primary_query": "best crm for small business",
    "secondary_queries": ["top crm small business"],
    "intent": "Commercial investigation",
    "target_url": "/guides/best-crm-small-business",
    "status": "needs creating",        // see the enum below - validated
    "priority": 20, "click_availability": "reduced"
  }],
  "serp_analysis": [{
    "query": "best crm for small business",
    "top_domains": ["reddit.com", "pcmag.com"], "domain_diversity": 1.0,
    "ugc_on_p1": true, "platform_slots": 0, "sitelinked": 0,
    "dominant_content_type": "listicle/comparison (6/8)",
    "freshness": "4/8 dated, median 463d old", "paa_count": 4,
    "ai_overview": "unknown - check manually",
    "winnability": 4.5, "winnability_reasons": ["UGC at position 1"]
  }],
  "competitors": [{
    "domain": "onepagecrm.com", "appearances": 2, "best_position": 8,
    "queries_owned": ["crm for small business"],
    "business_competitor": false, "type": "search-only"
  }],
  "cannibalization": [{
    "target_url": "/blog/crm-guide",
    "competing_clusters": ["crm comparison", "crm basics"],
    "primary_queries": ["best crm", "what is a crm"],
    "recommended_action": "Consolidate",   // Consolidate | Differentiate | Prune
    "note": "Same intent. Merge into the stronger page and 301 the other."
  }]
}
```

`serp_features.py` and `cluster.py` output most of these fields already - reshape rather
than retype.

---

## The tabs

### 1. Keyword Master
Every candidate that survived to scoring, the full working list.
`Query | Source | Intent | Relevance | Intent Value | Priority | Click Availability | Winnability | Cluster | Volume (manual) | Notes`

Sort descending by Priority. **Volume (manual) stays empty** - it exists so a human can
paste real figures in, not so anything can estimate one.

### 2. Clusters
`Cluster Name | Primary Query | Secondary Queries | Intent | Size | Avg Priority`

### 3. Keyword Map — the deliverable
`Cluster Name | Primary Query | Secondary Queries | Intent | Target URL | Status | Priority | Click Availability`

The 8-column schema, exactly. Do not reorder or rename - the report and the other tabs
cross-reference these headers by name.

**`Status` must be one of:** `exists and fine`, `exists and needs work`, `needs creating`,
`merge into another`. Validated; anything else blocks the write.

**The invariant:** every cluster maps to exactly one URL and no URL appears twice. Rows
marked `merge into another` are exempt, since they are the losing side of a resolved
cannibalization and are meant to share a URL.

### 4. SERP Analysis
The evidence behind every winnability score.
`Query | Top Domains | Domain Diversity | UGC on P1 | Platform Slots | Sitelinked | Dominant Content Type | Freshness | PAA Count | AI Overview | Winnability | Winnability Reasons`

`AI Overview` will read `unknown` for most rows. Fill it manually for the top 20.

### 5. Competitors
`Domain | Appearances | Best Position | Queries Owned | Business Competitor? | Type`

`Type`: `search-only`, `both`, or `business-only`. The search-only rows are the ones the
client will not expect.

### 6. Cannibalization
`Target URL | Competing Clusters | Primary Queries | Recommended Action | Note`

Empty is a good result. Say so in the report rather than omitting the tab - "we checked and
found none" is a finding.

---

## What validation blocks

| Problem | Why it blocks |
|---|---|
| One URL claimed by 2+ clusters | That is cannibalization. Resolve it or record it, do not ship it silently. |
| `Status` outside the enum | Downstream tooling and the report read this field by value. |
| A cluster with no primary query | A cluster without a primary target is not a cluster. |

`--force` exists for the case where duplicates are intentional and already documented on
the Cannibalization tab. Reach for it rarely, and say in the report why.

# What Not To Do - retired tactics and claims we refuse to repeat

Two lists. **Tier 1** is tactics that are dead, devalued, or actively punished. **Tier 2**
is claims that circulate as fact and are not, including several from the uncited
`marketing-skills` bundle sitting in this same repo.

---

## Tier 1 - Tactics that are dead or punished

### Link building

| Tactic | Why it fails now | Tier |
|---|---|---|
| **Private blog networks (PBNs)** | Pattern detection catches shared hosting and content footprints within weeks. Outcome is domain-level suppression or deindexing | `[P]` [s320, s322, s316, s173] |
| **Reciprocal link exchanges** | SpamBrain graph clustering identifies the pattern. Reported **15-40% ranking drops** | `[P]` [s170, s213, s193] |
| **Mass guest posting** | **98% of guest-post marketplace sites** are DR < 40 with < 10k traffic. Google devalues "write for us" placements | `[P]` [s320, s316, s216] |
| **Bulk directory submissions** | Zero value, plus it introduces NAP inconsistency that actively hurts local | `[P]` [s320, s173, s213] |
| **Buying links by DR alone** | A DR 70 unrelated link is worth less than a DR 35 topically relevant one. Zero-traffic sites pass zero value | `[P]` [s217, s323, s131] |

### On-page

- **Keyword density targets.** No evidence, never a documented factor [s283, s166].
- **Word count targets.** Long content correlates with ranking only because it tends to be
  more complete. Writing to a number produces padding [s283, s166].
- **Meta keywords tag.** Confirmed dead for over a decade [s283].
- **Optimizing past "good" on Core Web Vitals.** These are a **floor**. Failing hurts,
  exceeding buys nothing. Going from 2.4s to 1.1s LCP is engineering effort with no ranking
  return [s296, s293, s295].
- **Multiple H1s "for keywords".** One H1 [s296, s294].
- **Exact-match anchor text at scale.** Reads as manipulation.

### Technical

- **`Disallow` plus `noindex` on the same URL.** The single most common self-inflicted
  indexation bug. Disallowed means Google never reads the `noindex`, so the URL can stay
  indexed with no content. Pick one [s188, s209].
- **Blocking CSS or JS in robots.txt.** Google needs both to render [s298].
- **Putting 404s or noindex URLs in the sitemap.** Trains Google to distrust the whole
  sitemap [s297, s299].
- **Leaving redirect chains in place.** 2+ hops costs **100-500ms** and leaks signal;
  Googlebot may abandon past **5 hops** [s297, s302].
- **Worrying about crawl budget on a small site.** Only a real constraint above roughly
  **10,000-50,000 pages** [s136, s298].
- **Client-side rendering for content that must be found.** Wave two is **24-72 hours**
  later, and AI crawlers frequently skip JavaScript entirely [s299, s297, s181, s291].

### AI search

- **Selling llms.txt as an SEO deliverable.** No major engine honors it. Google explicitly
  ignores it and has compared it to the keywords meta tag. **~10% adoption** [s116, s118,
  s267, s263].
- **Blocking all AI bots to "protect content".** This removes you from AI answers while
  barely protecting anything, since robots.txt is voluntary. Block **training** bots
  (GPTBot, ClaudeBot), allow **retrieval** bots (OAI-SearchBot, Claude-SearchBot,
  PerplexityBot) [s111, s264].
- **Using `anthropic-ai` in a 2026 robots.txt.** Deprecated legacy agent; it produces broken
  instructions [s111, s116].
- **Adding schema and expecting AI citations.** Two causal studies found no uplift from
  schema alone [s190, s212]. See Tier 2.
- **Assuming a #1 ranking means AI citation.** The overlap fell from **92% to ~38%**
  [s233, s220, s110].

### Commercial

- **Guaranteeing rankings.** Nobody controls Google's ranking. It is the clearest signal of
  a bad vendor.
- **Hourly billing for ongoing execution.** Penalizes efficiency and makes cost
  unpredictable for the client. Hourly is for consulting and training only [s112, s237].
- **Quoting below the difficulty floor.** KD 30-45 needs **$2,000-$3,500/mo minimum**.
  Taking the work under that sells activity you cannot convert into results [s260].
- **Promising results inside 3 months.** Months 1-3 are foundation with minimal movement by
  design. Setting that expectation wrong loses the client in month 4 [s107, s119].

---

## Tier 2 - Claims that are not facts

### Confirmed NOT ranking factors

Google has explicitly stated these are not ranking factors, yet all still circulate:

- **Bounce rate** as measured in Google Analytics [s283, s166]
- **Domain age** [s283, s166]
- **Social signals** (likes, shares) [s283, s166]
- **XML sitemaps** as a ranking input, as opposed to a discovery aid [s283]
- **Meta keywords** [s283]
- **Word count** [s283, s166]
- **Structured data**, per John Mueller [s149, s212, s178]

### Numbers to stop quoting as fact

| Claim | The problem |
|---|---|
| "Content quality is **23% of the algorithm**" | A **First Page Sage** modeled estimate, not a disclosed weight [s283] |
| "Schema gets you **3.2x** more AI citations" | Vendor (xseek.io). **Ahrefs studied 1,885 pages and found no major uplift**; SearchAtlas found no correlation [s212, s190] |
| "**100+ photos = 520% more calls**" on GBP | Vendor research citing Google, not a Google publication. The defensible version is that photo volume correlates with engagement [s132, s172] |
| "Google tightened LCP to **2.0s**" | Single source against the 2.5s documented everywhere else. Unverified [q5 pass] |
| "**Google rewrites 61% of titles**" | Zyppy says 61%, Backlinko says 76%. Two vendor studies, different samples. Quote the range or neither [s166, s295] |
| "AI drives **20% of search-related traffic**" | Graphite vendor study. General studies put AI referrals **under 1%** of total referrals. Different denominators [s180, s251] |
| "**3 billion entities pruned** from the Knowledge Graph" | Single vendor study (OutpaceSEO) [s274] |
| "**25% of search moves to chatbots**" | A Gartner **projection**, not a measurement [s252] |

### The correlation-versus-causation list

These are real measurements, but they are **correlational**. Present them as correlation:

- Brand mentions correlating **0.664** with AI Overview citation vs **0.218** for backlinks
  [s270]. Correlation, single study.
- Screaming Frog's finding that position 1 results are **10% more likely** to pass Core Web
  Vitals than position 9 [s168, s242]. Correlational, and consistent with better-resourced
  sites simply being both faster and more authoritative.
- Bidirectional internal linking raising AI citation **2.7x** [s288]. Single vendor.
- Rakuten's **33% more conversions** and Vodafone's **15% more sales** after speed work
  [s305, s308]. These measure **conversion**, not ranking. They are strong business
  arguments and weak ranking arguments.

### On the uncited material in this repo

`marketing-skills/{ai-seo, seo-audit, schema, site-architecture, programmatic-seo,
directory-submissions}` is roughly 150 KB of vendored third-party content with **no
`_research/`, no citations, and no source-tier flags**. Its checklists are useful as
checklists. Its numbers ("~45% of searches show AI Overviews", "6.5x more likely to be
cited", the Princeton per-method boost table) are bare assertions in that context.

**Rule:** use those files for structure, never for a number. Re-ground any figure against
`research-synthesis.md` or the live notebook before repeating it to Aleem or a client. Where
our corpus and theirs disagree, ours has citations and theirs does not.

---

## The honesty standard, stated once

If there is no evidence for something, say so. "The corpus does not cover client churn
rates" is a better answer than a plausible-sounding invented number. SEO has more confident
wrong answers in circulation than almost any technical field, and the entire value of this
skill is not adding to them.

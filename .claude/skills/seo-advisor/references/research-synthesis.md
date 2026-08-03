# SEO 2026 - Research Synthesis (MASTER)

**Research basis:** 320 unique sources gathered through 14 deep passes of the in-repo
`research` skill (Exa + Tavily + Serper + Jina fused, content-extracted, deduped from 399
raw), then imported into six NotebookLM notebooks and synthesized one question per topic.
Each question was asked against both its topic notebook and the mixed `A_core` notebook,
and the two answers reconciled here.

**Citations:** `[sN]` resolves to the global source index N in `_research/sources.json`
(`sources[N-1]` gives title, url, tier, and which notebook holds it). Raw per-question
answers are in `_research/q*.json`; `_research/render_answer.py <key>` reprints any answer
with citations already resolved to `[sN]`. Run `build_corpus.py verify` after editing to
confirm every marker still resolves.

**Source tier, and why it dominates this document:** the corpus is **18 confirmed-tier
against 302 practitioner-tier**. Confirmed means Google or Bing documentation, web.dev, or
peer-reviewed work. Practitioner means a vendor blog, a tool company's correlation study,
or a consultant's case study. SEO's public information space is overwhelmingly written by
people selling SEO tools and services, so **every load-bearing number below carries its
tier**, and vendor studies are attributed to the vendor by name. Where sources conflict,
the conflict is shown rather than averaged away.

**Correlation is not causation.** Several widely-cited "ranking factor weights" come from
correlation studies with no causal design. They are reported here as what they are.

**Date:** 2026-08-02

> Velocity warning: thresholds, AI-surface behavior, and tool capabilities in this field
> change quarterly. Anything version-, threshold-, or platform-specific should be
> re-checked through `notebook-live-query.md` before being quoted to a client.

---

## Q1 - How search engines work, ranking systems, and core updates

**Bottom line:** Search still runs on crawl, index, rank, but in 2026 an AI answer layer
sits on top of it and takes a large share of the clicks. Google publicly confirms only a
handful of ranking factors; most of what the industry calls a "ranking factor" is a
third-party proxy or an outright myth.

**The three stages, with the thresholds that actually bite**

- **Crawling.** Googlebot fetches up to **2MB per URL** (64MB for PDFs); anything past
  that byte limit is simply not seen [s282] [practitioner]. Crawling happens in two waves:
  raw HTML first, then the Web Rendering Service executes JavaScript **24 to 72 hours
  later** [s299, s297] [practitioner].
- **AI crawlers are separate bots.** GPTBot, OAI-SearchBot, ClaudeBot and PerplexityBot
  crawl independently and **frequently skip JavaScript execution entirely**, so
  JS-dependent navigation is invisible to them [s181, s291] [practitioner]. This is the
  single most under-appreciated technical fact in the corpus.
- **Indexing.** The index exceeds **100 million gigabytes** [s145, s238]. Being crawled is
  not being indexed; pages below a quality threshold sit in "crawled - currently not
  indexed" [s145].
- **Ranking.** Google runs **15+ documented ranking systems**, not one algorithm [s283]:
  RankBrain (novel queries), BERT (language context), MUM (multimodal), PageRank (links),
  Passage Ranking (sections within long pages), the Helpful Content system (folded into
  core in 2024), Freshness, and Reviews [s283, s204, s238, s184, s296].

**The AI layer, in numbers**

| Metric | Value | Tier |
|---|---|---|
| AI Overviews present in search results (Q1 2026) | **~47%** | [practitioner] [s291] |
| Average CTR, #1 organic result | **27.6%** (Backlinko) | [practitioner] [s145, s288] |
| CTR drop when an AI Overview is present | **up to 58%** | [practitioner] [s145, s288] |
| Google searches ending without a click | **~60%** | [practitioner] [s288, s292] |

**Core updates.** Broad core updates are reassessments, not penalties: they re-rank
content relative to the rest of the web rather than punishing a site [s219, s184]
[confirmed, per Google's core-updates documentation]. The May 2026 core update rolled out
over **12 days** of volatility [s219]. Recovery guidance: do not judge until at least a
week after rollout completes [s219]; audit for **domain-level quality weighting**, where
thin content in one site section suppresses good content elsewhere [s294]; then
consolidate overlapping pages, remove thin content, and add named authors and first-hand
experience [s294, s292, s128] [practitioner].

**Confirmed ranking factors (only seven).** Backlinks, content quality/E-E-A-T, HTTPS,
page speed / Core Web Vitals, mobile-friendliness, freshness, and page experience [s283].

**Explicitly not ranking factors**, per Google's own statements: **bounce rate** as
measured in Google Analytics, **domain age**, **social signals** (likes and shares),
**XML sitemaps** as a ranking input, and **meta keywords** [s283, s166]. There is also no
evidence for **word count** as a direct factor; long content correlates with ranking only
because it tends to be more complete [s283, s166].

> **Honesty flag:** the frequently-quoted "content quality is 23% of the algorithm" figure
> comes from a **First Page Sage** vendor study [s283]. It is a modeled estimate, not a
> disclosed weight. Do not present it to a client as Google's number.

Full detail: `references/how-search-works.md`

---

## Q2 - Keyword research and search intent

**Bottom line:** Keyword research moved from volume-first to demand-and-intent-first,
because a majority of searches now end without a click and AI engines expand one prompt
into many sub-queries you were never targeting.

**Metric reliability, which is worse than most people assume**

- Volume estimates for the same keyword can differ by **30x** between tools such as Moz
  and Semrush (Link-Assistant study) [s290] [practitioner].
- About **15% of daily searches are entirely new** and carry zero historical data in any
  platform [s290] [practitioner]. Volume-only prioritization is structurally blind to them.
- Keyword Difficulty is **relative to your domain**, not absolute. KD 40 can be winnable
  for an authority site and impossible for a new one [s285, s288].
- Practical starting threshold for a new site: **KD under 20, volume 100 to 1,000**
  [s288] [practitioner].

**Search intent, now six categories not four**

Informational, Navigational, Commercial Investigation, Transactional, **Local**, and a new
**Generative AI intent** where the user asks a model to perform a task rather than find a
page ("create X", "calculate Y") [s284, s165, s247]. That last category is reported at
**37.5% of queries on platforms like ChatGPT** [s247] [practitioner, single source].
Mismatching intent is reported to cut content effectiveness by **35 to 40%** [s287]
[practitioner].

**Clustering.** The working rule is **one search intent = one page = one keyword cluster**
[s247]. Cluster by **shared SERP outcome, not by wording**: if the same competitors rank
for two phrases, those phrases belong together [s287, s289]. Structure as a pillar page
(2,500 to 4,000 words) supporting **8 to 15 cluster pages** with bidirectional links
[s288, s128] [practitioner].

**Query fan-out is the genuinely new mechanic.** AI engines expand a single prompt into
**2 to 10 synthetic sub-queries** before retrieving [s286]. This creates a retrieval gap:
you can rank #1 for the literal query and still be absent from the AI answer because you
matched none of the sub-queries the engine actually ran [s286]. The practical tactic is
**inverse prompting**, asking the engine directly what sub-queries it would run, then
covering them [s286].

**Prioritization formula** in circulation: `Priority = (Business Relevance x Conversion
Intent) / Competitive Feasibility` [s284, s288, s127] [practitioner]. High-intent,
mid-to-low-volume terms are reported to convert **5 to 10x** better than broad
informational ones [s127] [practitioner].

Full detail: `references/keyword-research-playbook.md`

---

## Q3 - On-page SEO at the site level

**Bottom line:** Title tags and genuine topical depth still carry on-page. Keyword density
and word count are dead. Several performance factors are a floor, not a lever: failing
them hurts, exceeding them does nothing.

**The floor-versus-lever distinction** is the most useful idea in this section. Core Web
Vitals, mobile-friendliness and HTTPS act as a **ranking floor**. Falling below suppresses
rankings; exceeding the threshold buys no further advantage [s296, s293, s295]
[practitioner]. Optimizing past "good" is wasted effort.

**Title tags** remain the highest-leverage single element, with a measured **3.7 position**
difference between optimized and unoptimized [s166, s187] [practitioner]. Keep to **50 to
60 characters or ~600 pixels** and front-load the primary term in the first 40 characters
[s296, s207, s128].

> **Source conflict, shown not averaged:** Zyppy measures Google rewriting **61%** of
> titles; Backlinko measures **76%** [s166, s295]. Both are vendor studies with different
> samples. The actionable part both agree on: alignment between title, H1 and first
> paragraph is the best defense against a rewrite [s296, s166].

**Meta descriptions** are not a ranking factor but drive CTR, which feeds engagement
systems [s181, s296, s283, s207]. Target **105 to 155 characters**, critical information in
the first 120 to survive mobile truncation [s207].

**Headings.** Exactly one H1 [s296, s294]. Phrasing H2s and H3s as **direct user
questions** improves the odds of citation in AI Overviews and featured snippets [s181,
s294] [practitioner].

**Topical authority.** The **2024 Google API leak** surfaced a `siteFocusScore` attribute,
which is the strongest available evidence that topic concentration is measured [s283].
Clustered content is reported to generate **30 to 43% more traffic** than standalone posts
[s288] [practitioner].

**Internal linking.** Bidirectional pillar-to-cluster linking is reported to raise AI
citation probability **2.7x** [s288] [practitioner, single vendor]. Working threshold: **8
to 15 internal links per 2,000 words** [s128]. **BreadcrumbList schema** is called the most
under-implemented signal, because it makes hierarchy machine-readable independently of
prose [s291].

**Freshness.** Ahrefs found AI-cited content is **25.7% fresher** than non-cited content,
supporting a **13-week update cycle** on priority pages [s294, s128] [practitioner].

**Images.** Descriptive alt text on every non-decorative image [s296, s166, s295]; hero
images **under 150KB**, WebP or AVIF [s295, s292].

Full detail: `references/onpage-playbook.md`

---

## Q4 - Technical SEO

**Bottom line:** Technical SEO is a five-layer pyramid where a failure at the bottom
invalidates everything above it. Fix in order: crawlability, architecture, performance,
structured data, then AI-search readiness [s299].

**Layer 1 - Crawlability and indexation.** The most common source of silent traffic loss
[s299, s241]. Crawl budget only becomes a real constraint above roughly **10,000 to
50,000 pages** [s136, s298]; below that, worrying about it is misdirected effort.

- `robots.txt` **must return 200 OK**. A 5xx there causes Googlebot to stop crawling the
  entire site [s299, s188].
- **Never block CSS or JS** [s298]. Google needs them to render.
- Sitemaps: **under 50MB and 50,000 URLs** per file [s188, s167], containing **only
  200-status, canonical, indexable URLs**. Including 404s or noindex URLs trains Google to
  distrust the sitemap [s297, s299].
- **The classic fatal mistake:** combining `Disallow` in robots.txt with a `noindex` tag on
  the page. Disallowed means Google never reads the page, never sees the `noindex`, and the
  URL can stay indexed with no content [s188, s209]. Pick one.
- **IndexNow** gives push-based instant indexing on Bing, Yandex and Naver [s303, s167].

**Layer 2 - Canonicals and duplicates.** Self-referencing canonical on every indexable
page [s299, s297]; 301 the HTTP/HTTPS, www/non-www and trailing-slash variants to one
master [s299, s303, s136]; and make **internal links point at canonical URLs directly**, or
you send contradictory signals [s301, s300].

**Layer 3 - Architecture.** The **3-click rule**: every commercial page reachable within
three clicks of the homepage [s299, s209]. Pages **5+ clicks deep** are crawled less and
receive less link equity [s299, s209]. URLs under **60 characters**, lowercase, hyphens not
underscores [s299, s303].

**Layer 4 - Redirects and status codes.** 301 passes equity, 302 is for genuinely temporary
changes [s303, s299]. **Redirect chains of 2+ add 100 to 500ms of latency** and leak
signal; Googlebot may abandon chains beyond **5 hops** [s297, s302]. Use **410 Gone** for
permanently removed content to drop it from the index faster than a 404 [s303, s299].

**Layer 5 - JavaScript rendering.** The two-wave model means HTML is indexed first and
JavaScript rendered **24 to 72 hours later** [s299, s297]. Combined with the Q1 finding
that AI crawlers often skip JS entirely [s181, s291], server-side rendering is effectively
mandatory for any content that must be found.

Full detail: `references/technical-seo-playbook.md`

---

## Q5 - Core Web Vitals and page speed

**Bottom line:** The thresholds are settled and documented. The ranking effect is real but
small, a tiebreaker between comparable pages rather than a lever that rescues weak content.
Measure on field data, not Lighthouse.

**Thresholds**, evaluated at the **75th percentile of real Chrome visits over a rolling
28-day window**, with all three required to pass simultaneously [s148, s305, s168, s210,
s242, s308, s307, s129] [confirmed, web.dev]:

| Metric | Measures | Good | Needs improvement | Poor |
|---|---|---|---|---|
| **LCP** Largest Contentful Paint | Loading | **<= 2.5s** | 2.5 to 4.0s | > 4.0s |
| **INP** Interaction to Next Paint | Responsiveness | **<= 200ms** | 200 to 500ms | > 500ms |
| **CLS** Cumulative Layout Shift | Visual stability | **<= 0.1** | 0.1 to 0.25 | > 0.25 |

**INP replaced FID** in March 2024 and measures the worst interaction latency across the
whole session, not just the first [s299, s230, s148, s305, s129, s168].

**Ranking impact, honestly.** Sources broadly agree Core Web Vitals act as a **tiebreaker**
[s307, s168, s148, s230, s305, s158, s129, s242, s136]. They will not lift thin content
over an authoritative page, but they can decide between two comparable ones. Supporting
evidence, all vendor or case-study tier:

- **Screaming Frog** (20,000 URLs): position 1 results are **10% more likely to pass** CWV
  than position 9 [s168, s242] [practitioner, correlational].
- **Rakuten**: **33% more conversions, 53% more revenue** per visitor after optimizing
  [s305] [practitioner, single case].
- **Vodafone**: a 31% LCP improvement produced **15% more sales** [s308] [practitioner].
- **Deloitte/Google**: each 100ms of mobile speed improvement lifted retail conversion
  **8.4%** [s168, s308] [practitioner].

Note these measure **conversion**, not ranking. They are strong arguments for speed as a
business investment and weak arguments for speed as a ranking lever.

**Field versus lab, the trap that wastes the most time.** Google uses **field data only**
for ranking [s158, s230, s305, s129, s306, s168, s242, s308, s307, s229, s310]. Field data
(CrUX) comes from real Chrome users over 28 days. Lab data (Lighthouse, WebPageTest) is a
simulation, useful for debugging and nothing else. **A page can score 100 in Lighthouse and
still fail the field assessment**, because real users are on slower devices and worse
networks [s307, s305, s242, s229, s230, s210].

> **Source conflict:** one source claims Google tightened "good" LCP to **2.0s** in 2026
> [q5 pass, practitioner], against the 2.5s documented everywhere else. Treat 2.5s as
> current and 2.0s as an unverified single-source claim.

Full detail: `references/technical-seo-playbook.md`

---

## Q6 - Structured data and schema

**Bottom line:** JSON-LD in the head, roughly 14 types that still earn rich results, a long
list of recent deprecations, and a genuine evidence war over whether schema helps AI
citation. Google's own position is that structured data is **not a direct ranking factor**.

**What still earns rich results.** Schema.org has 800+ classes; Google renders rich results
for roughly **30**, with **14 primary types** actively rewarded: Article, Breadcrumb,
Product (incl. MerchantListing, ProductVariants), Recipe, Event, LocalBusiness, JobPosting,
Video, Organization, Speakable, Return Policy, Shipping Policy, Loyalty Program (added
2025), and Carousel [s312, s313, s212, s167].

**Deprecations, which are the expensive thing to miss**

- **FAQ rich results: sunset entirely on 7 May 2026**, including the former health and
  government exceptions [s175, s312, s135].
- **HowTo**: effectively dead on desktop since 2023, near-zero payoff now [s312, s313, s190].
- **June 2025 sweep**: Book Actions, old-format Course Info, ClaimReview (now restricted to
  verified fact-checkers), Estimated Salary, Learning Video, Special Announcement, Vehicle
  Listing [s312, s212].
- **Sitelinks Searchbox**: sunset late 2024 [s312, s135].

Important nuance: **FAQPage and HowTo markup still carry value for non-Google engines**
(ChatGPT, Perplexity, Bing Copilot) even though Google no longer renders them [s135, s190,
s175, s313]. Removing the markup because Google dropped the rich result is a mistake.

**Implementation.** JSON-LD is Google's recommended format [s299, s313, s150, s149, s212].
Place it in `<head>` for AI-citation reliability [s135]. All URLs absolute; dates and
durations in strict **ISO 8601** (`2026-04-18`, `PT30M`) [s313, s311]. Validate with
**validator.schema.org** for vocabulary conformance and **Google's Rich Results Test** for
Google eligibility; treat Search Console's Enhancements report as ground truth at scale
[s149, s299, s175, s313, s190, s178, s241].

> **The clearest evidence conflict in the whole corpus.** Vendor claims: SE Ranking and
> DigitalApplied report **71% of ChatGPT-cited pages** and **65% of Google AI Mode pages**
> carry structured data [s130, s150, s190]; xseek.io claims **3.2x** more citations [s212];
> Writesonic and Stackmatix claim **2.5x to 3:1** [s150, s212]. Against that: **Ahrefs
> studied 1,885 pages and found no major uplift in AI citations from schema alone**
> [s190], and **SearchAtlas found no direct correlation** between schema coverage and
> citation rate [s212]. **Google's John Mueller has confirmed structured data is not a
> direct ranking factor** [s149, s212, s178].
>
> Resolution: the vendor numbers are correlational and self-interested; the two causal
> studies are negative. Schema is connective tissue that amplifies **existing** authority,
> not a shortcut for weak content [s190, s130, s169]. Implement it for eligibility and
> entity clarity, not as a ranking play.

**Where schema genuinely earns its keep in 2026** is entity disambiguation: stable `@id`
identifiers linking Organization, Person and Article nodes into one graph [s150, s136],
`sameAs` pointing at Wikidata, LinkedIn or Crunchbase [s150, s175, s190, s135], and an
accurate `dateModified` as a recency signal for Perplexity and AI Overviews [s175, s190,
s135].

Full detail: `references/technical-seo-playbook.md`

---

## Q7 - Off-page SEO, backlinks, and digital PR

**Bottom line:** Links are still top-three, but **SpamBrain 3.0** shifted enforcement from
individual links to whole citation networks, and **unlinked brand mentions now correlate
about 3x more strongly with AI citation than backlinks do**. The dividing line is editorial
intent: did a real human editor choose to link.

**What still works**

| Tactic | Evidence | Tier |
|---|---|---|
| Digital PR + original research | Rated most effective: **34%** (Reporter Outreach survey) to **48.6%** (Editorial.link) | [practitioner] [s196, s216, s217] |
| Linkable assets (tools, calculators) | Earn passive links indefinitely | [practitioner] [s318, s171] |
| Journalist outreach (Connectively, Qwoted, Featured.com) | **1 to 2 quality links/month** at 2-3 responses/day | [practitioner] [s318, s213, s217, s320] |
| Broken link building | **5 to 15%** conversion | [practitioner] [s320, s317, s323, s171] |
| Unlinked mention reclamation | **30 to 50%+** conversion, the highest of any tactic | [practitioner] [s317, s193, s171] |

**What gets you hurt**

- **PBNs**: pattern detection catches shared hosting and content footprints within weeks;
  outcome is domain-level suppression or deindexing [s320, s322, s316, s173].
- **Link exchanges**: SpamBrain graph clustering identifies reciprocal networks; reported
  **15 to 40% ranking drops** [s170, s213, s193, s173].
- **Mass guest posting**: **98% of sites on guest-post marketplaces are low quality**
  (DR < 40 and < 10k monthly traffic) [s216] [practitioner].
- **Bulk directory submissions**: zero value plus NAP inconsistency risk [s320, s173, s213].

**Judging a link.** DR and DA are **proxies, not gospel** [s320, s323]. Working thresholds:
topical relevance first, meaning the linking domain's entity cluster overlaps yours
[s322]; **at least 1,000 monthly organic visits**, since zero-traffic sites pass zero value
[s170, s131]; **DR 30+** baseline and **DR 50+** for high-impact placements, with **91% of
SEOs** now setting a DR floor [s170, s196]; and drop anything with a Semrush **Toxic Score
above 45** regardless of DR [s322]. A DR 35 niche-relevant link beats a DR 70 unrelated one
[s217, s323].

**Cost.** Average earned digital PR link runs about **$750** [s196, s216] [practitioner].

**Brand mentions, the headline finding.** Branded web mentions correlate at **r = 0.664**
with AI Overview citation, against **r = 0.218** for backlinks [s196, s317, s270]
[practitioner, correlational]. Brands present on **four or more third-party platforms** are
**2.8x more likely** to be cited by ChatGPT [s179]. Caveat worth carrying: link building
still gets you into the candidate pool the AI synthesizes from, so mentions supplement
links rather than replace them [s270, s220].

Full detail: `references/offpage-authority-playbook.md`

---

## Q8 - Local SEO and Google Business Profile

**Bottom line:** Local is now judged across three surfaces (map pack, local organic, and AI
recommendations). GBP signals and reviews together account for roughly half the weighting,
and the primary category is the single strongest lever.

**Reported local pack weighting** [s191, s172] [practitioner, modeled estimates not
disclosed weights]:

| Signal group | Weight |
|---|---|
| Google Business Profile (categories, completeness, freshness) | **32%** |
| Reviews (volume, velocity, sentiment) | **20%** |
| On-page (NAP, local keywords, authority) | **15%** |
| Behavioral (CTR, click-to-call, direction requests) | **9%** |
| Links (local backlinks, brand authority) | **8%** |
| Citations (directory consistency) | **6%** |

**GBP tactics.** The **primary category is the strongest individual signal**; pick the most
specific match ("Personal Injury Attorney", not "Lawyer") [s191, s243, s132]. Post **1 to 3
Google Posts weekly**, which now surface in AI Overview citations [s243]. Seed **8 to 12
Q&A entries** covering pricing and service areas to feed answer engines [s243, s132].
**46% of all Google searches carry local intent** [s243, s132].

**Reviews.** Target **2 to 4 new reviews per week** [s137]; a sustained **5 to 15 per month
over six months** is reported to move a business 5 to 10 map pack positions [s243].
GrowthPro AI reports businesses with **50+ reviews in 12 months are 3x more likely** to
appear in AI recommendations, and a **4.5+ star rating** doubles citation frequency [s157]
[practitioner, single vendor]. Respond within **24 to 48 hours** [s243, s153].

> **Honesty flag on a number that gets quoted a lot:** the claim that profiles with **100+
> photos get 520% more calls** [s132, s172] traces to vendor research citing Google, not to
> a Google publication. Treat as directional. The more defensible version is that photo
> volume correlates with engagement; the 10 to 25 photo minimum [s243] is the safer
> recommendation.

**Citations.** Fix Tier 1 first (Google, Bing Places, Apple Maps, Yelp, Facebook), then
aggregators (Data Axle, Localeze), then industry directories [s172, s173]. Minor NAP
discrepancies ("St." vs "Street") can suppress rankings [s172]. Tooling: BrightLocal,
Whitespark, Yext [s124, s172, s137].

**Local landing pages** need genuinely unique hyperlocal content, not a city-name swap
[s137, s172, s214, s215]. LocalBusiness + Service + FAQPage schema [s243, s123, s317,
s172]; pages with FAQ schema reported **4x more likely** to be cited in AI Overviews
[s157] [practitioner]. Mobile load **under 2 seconds** [s317, s215].

Full detail: `references/local-seo-playbook.md`

---

## Q9 - AI search, AEO and GEO

**Bottom line:** The overlap between ranking on Google and being cited by AI has collapsed.
Optimizing for AI is now a distinct discipline built on entity authority, topical coverage,
and brand mentions rather than page-level ranking.

**The collapse, in one row.** Correlation between the organic top 10 and AI Overview
citations was **92% in mid-2025** and fell to roughly **38% by early 2026**, with some AI
Mode analyses as low as **14 to 17%** [s233, s220, s110] [practitioner]. Ranking #1 no
longer implies being cited.

**How selection works.** Google filters **200 to 500 candidate documents down to 5 to 15
cited sources** [s110]. Query fan-out expands one prompt into **5 to 11 sub-queries** on
average, and for complex tasks Google can fire **hundreds of parallel searches** [s271,
s110]. The most actionable finding in this section: sites with **80%+ topical coverage of
their domain retain 85.4% of AI visibility** despite fan-out instability, which makes
comprehensive clusters more durable than keyword-targeted pages [s110] [practitioner].

**Platforms cite very differently**

| Platform | Retrieval behavior |
|---|---|
| **ChatGPT** | Bing-indexed content plus Wikipedia (**47.9% of referrals**); about **90% of citations come from pages ranked 21+** on Google [s233, s198, s222] |
| **Perplexity** | Real-time search, community-heavy: **Reddit is nearly half** its top citations vs under 10% for ChatGPT. Strongest recency bias, content over **90 days** loses priority [s233, s198, s179] |
| **Gemini** | **~43%** from Google properties, **21% Reddit**; deep Workspace integration [s198, s233] |
| **Claude** | Reasoning-first, **200,000+ token** context, favors long-form definitive guides and academic-style signals [s220, s268] |

**llms.txt: the honest answer.** It is a **proposed Markdown map, not a standard and not an
access control** [s111, s116]. **Google explicitly ignores it** and has compared it to the
long-discredited keywords meta tag, stating there is "no measured reason" for citation
gains [s116, s179, s263, s142, s113]. Adoption sits around **10% of domains** [s262, s267].
Its genuine niche is developer documentation and sites serving AI coding assistants like
Cursor or Claude Code, where it reduces context noise [s264, s113, s267]. Vendors sell
llms.txt generators; Google says it does nothing. Do not sell it to a client as an SEO
deliverable.

**AI crawler control, the distinction that matters most.** Training and search crawlers are
**different bots**: OpenAI uses **GPTBot** (training) and **OAI-SearchBot** (search);
Anthropic uses **ClaudeBot** (training) and **Claude-SearchBot** (search) [s111]. Blocking
indiscriminately removes you from AI answers while trying to opt out of training.
**robots.txt is voluntary and not a technical lock**; hard enforcement needs WAF or
server-level IP rules, which are evaluated *before* robots.txt is read [s116, s111].
Cloudflare AI Crawl Control and Kinsta Bot Protection expose one-click toggles [s111,
s113]. Context for the tradeoff: Anthropic's crawl-to-referral ratio peaked at
**70,900:1** against Googlebot's **5:1** [s111], meaning AI crawlers take far more than
they send back.

**Entity SEO.** In **June 2025 Google removed over 3 billion entities (6.26%)** from the
Knowledge Graph in a quality purge; it now holds **1.6 trillion facts on 54 billion
entities** [s274]. Use `sameAs` in Organization schema pointing at **Wikidata Q-numbers**,
Crunchbase and LinkedIn [s272, s268, s182]. Wikidata is the most direct path to a Knowledge
Panel for brands without a Wikipedia page, and recognition speed runs Wikidata (fastest),
schema disambiguation, Knowledge Panel, Wikipedia (slowest) [s268, s182].

**The one piece of peer-reviewed evidence in this section.** The **Princeton GEO study**
measured content modifiers that raise citation probability: **expert quotes +41%**,
**statistics +30%**, **inline citations +30%** [s220, s179]. This is the strongest evidence
available for any AI-visibility tactic, and it is about content structure, not markup.

Full detail: `references/ai-search-playbook.md`

---

## Q10 - Measurement, analytics, and reporting

**Bottom line:** Measurement is a triangle of Search Console (visibility), GA4 (behavior),
and CRM (business outcome). The goal is decision-grade data, not precision, because privacy
and AI referrers have permanently broken exact attribution.

**Search Console, the non-negotiable baseline** [s156, s138]

- Track the **28-day rolling average** to smooth volatility [s252].
- Highest-leverage report use: high-impression low-CTR queries. Moving position 8 (~1% CTR)
  to position 4 (~5% CTR) can lift clicks **400%** with no new content [s252] [practitioner].
- **Generative AI Performance report**, launched mid-2026, tracks performance inside AI
  Mode and AI Overviews [s141, s139] [confirmed, Google Search Central].
- Index coverage: healthy sites hold indexed-to-submitted above **85%** [s252].
  "Crawled - currently not indexed" means quality; "Discovered - currently not indexed"
  means crawl budget [s252].
- Use **mobile** Core Web Vitals scores; sites with INP > 500ms saw **2 to 4 position
  drops** in the March 2026 core update [s252] [practitioner].

**GA4, and the misattribution problem.** GA4's default channel grouping misclassifies
**30 to 50% of search traffic** as Direct or Unassigned [s254] [practitioner]. Fixes:
link GSC to GA4 manually (Admin > Product Links) for keyword-level data [s251, s254], and
**extend data retention to 14 months** (default is 2) or year-over-year comparison is
impossible [s251, s254]. To find dark organic, audit Direct traffic landing on deep pages
(4+ URL segments); those are almost always misclassified organic [s254].

**AI traffic measurement.** As of July 2026 GA4 has a native **AI Assistant channel** for
ChatGPT, Gemini and Claude, but it **excludes AI Overviews**, which still report as Organic
Search [s253]. Server log analysis is the ground truth, because AI platforms often use
`rel="noreferrer"` which strips the referrer entirely: **GA4 undercounts AI referrals by 8
to 31%** versus logs [s253] [practitioner].

Regex for a custom GA4 AI channel group [s253]:
`.*(chatgpt.com|openai.com|perplexity.ai|claude.ai|gemini.google.com|copilot.microsoft.com|you.com|grok.x.ai).*`

**Benchmarks**

| Metric | Value | Tier |
|---|---|---|
| AI chatbots as share of total referrals | **under 1%** in general studies | [practitioner] [s251, s180] |
| Projected search volume moving to chatbots by late 2026 | **25%** (Gartner) | [practitioner, projection] [s252] |
| Strong brand AI mention rate | **15%** | [practitioner] [s252] |
| Category leader AI share of voice | **35 to 50%** | [practitioner] [s252] |
| Mature SEO program return | **3 to 5x cost** | [practitioner] [s252] |
| Median SEO ROI across industries | **748%** | [practitioner] [s259] |
| Organic CPA vs paid search CPA | **40 to 70% of paid** | [practitioner] [s252] |

> **Conflict:** general studies put AI referrals under 1% of traffic [s251], while a
> Graphite vendor study claims ChatGPT already drives **20% of global search-related
> traffic** [s180, s253]. These are measuring different denominators and the 20% figure is
> vendor-sourced. Use "under 1% of referrals today, rising fast" as the defensible line.

**Monthly client report** should carry: organic clicks, conversion rate, top-10 keyword
count, an explicit **action log** of pages edited and links earned, AI mention rate and
competitor citation share, and CRM-tied organic CPA [s252, s261, s108].

Full detail: `references/measurement-playbook.md`

---

## Q11 - The 2026 SEO tool stack

**Bottom line:** One all-in-one platform plus Screaming Frog plus Search Console covers
almost everything. Free tiers are genuinely sufficient only for small sites. AI visibility
tracking is a new, separate line item.

| Tool | Best at | 2026 cost | Free option |
|---|---|---|---|
| **Semrush** | Multi-channel (SEO + PPC + social), 140+ technical checks, white-label reporting | **$129.95 to $139.95+**/mo Pro [s174, s256] | 10 searches/day [s140] |
| **Ahrefs** | Backlinks and competitive research; 36-trillion link index refreshed every 15 to 30 min | **$108 to $129+**/mo Lite [s140] | Webmaster Tools, owned domains only [s256] |
| **Moz Pro** | Domain Authority, beginner-friendly | **$31 to $99+**/mo [s180, s174] | MozBar extension [s256] |
| **Screaming Frog** | Deep technical crawling, JS rendering, redirect chains | **Free to 500 URLs**, then **$259/yr** [s138, s256] | Yes, genuinely usable |
| **Peec AI** | Multi-LLM citation tracking, 7+ platforms | **$95/mo** [s156] | No |
| **Dageno AI** | AI share of voice and sentiment, 10+ platforms | Free plan available [s180] | Yes |

**Is free enough?** For a site under 500 URLs, Search Console plus free Screaming Frog
genuinely covers technical and performance work [s256]. It does **not** cover competitor
intelligence, backlink discovery, or scaled rank tracking [s156, s174, s256]. Ahrefs is the
pick for link work (its Traffic Potential metric estimates whole-SERP traffic rather than
single-keyword volume) [s155, s140]; Semrush is the pick for agencies needing PPC data and
white-label reports [s180, s155].

> **Vendor claim, flagged:** Ahrefs' internal data claims its crawler finds **35% more
> referring domains than Semrush and 68% more than Moz** [s176]. That is a vendor
> measuring itself against competitors. Directional only.

Full detail: `references/seo-tool-stack.md`

---

## Q12 - AI crawler control and llms.txt

**Bottom line:** Training bots and search bots are different bots. Block training, allow
retrieval. llms.txt is not honored by any major engine. robots.txt is a request, not a
lock.

**The split, and why it is the whole ballgame** [s111, s113]:

| | Training crawlers | Search / retrieval crawlers |
|---|---|---|
| Purpose | Build model weights | Index for real-time answers and citations |
| Referral value | Effectively zero | Sends high-intent traffic via citations |
| Share of AI bot load | **~82%** | **~15%** |
| Conversion of referred traffic | n/a | **4 to 5x higher** than traditional search [s233, s194] |

**The control matrix** [s111, s264, s113, s116]:

| User-agent | Owner | Action | Why |
|---|---|---|---|
| **GPTBot** | OpenAI | **Block** | Training only, no referral value |
| **OAI-SearchBot** | OpenAI | **Allow** | Powers ChatGPT search citations |
| **ChatGPT-User** | OpenAI | **Allow** | User-triggered fetch; robots.txt often does not apply anyway |
| **ClaudeBot** | Anthropic | **Block** | Training; peaked at **70,900 pages crawled per referred visitor** |
| **Claude-SearchBot** | Anthropic | **Allow** | Retrieval and citation |
| **PerplexityBot** | Perplexity | **Allow** | Retrieval, sends referrals |
| **Google-Extended** | Google | Judgment call | Gemini training opt-out; does **not** affect Search ranking |
| **anthropic-ai** | Anthropic | **Deprecated** | Legacy agent, citing it in 2026 configs gives broken instructions |

For comparison, Googlebot's crawl-to-referral ratio is about **5:1** [s111]. The asymmetry
is the argument for blocking training bots.

**Enforcement.** `robots.txt` is **voluntary and not a technical lock** [s116]. Real
enforcement needs WAF or server-level IP rules, which are evaluated **before** robots.txt is
read [s111]. Cloudflare AI Crawl Control and Kinsta Bot Protection give one-click toggles
[s111, s113].

**llms.txt.** A proposed Markdown site map for LLMs at `/llms.txt` [s116, s265]. **No major
search engine or AI vendor honors it for ranking or access control.** Google explicitly
ignores it; OpenAI points to robots.txt instead [s116, s267]. Adoption is **~10% of
domains** across a 300,000-site sample [s118, s267]. Its one real use is developer
documentation consumed by coding assistants like Claude Code and Cursor [s118, s267].
**Do not sell it as an SEO deliverable.**

Full detail: `references/ai-search-playbook.md`

---

## Q13 - Entity SEO and query fan-out

**Bottom line:** Optimize for being a recognized *thing*, not a matched *string*. Entity
identity is established through Wikidata, `sameAs`, and consistent co-occurrence in
editorial contexts, and it is what survives query fan-out.

**How LLMs form entity understanding.** Two phases: **pre-training** on Wikipedia, Wikidata
and Common Crawl, then **inference-time retrieval** reconciling fresh pages against the
internal entity model [s273]. Wikipedia is highest-authority because it combines stable
identifiers, an editorial notability gate, and a cross-reference graph [s268, s273].
Wikidata is more achievable and nearly as valuable: its **Q-number** identifiers back both
Wikipedia infoboxes and Google's Knowledge Graph [s273, s274].

**Query fan-out, with sharper numbers than Q9.** A prompt expands into **10 to 20 synthetic
sub-queries**, hundreds for deep-research modes [s121, s110, s271]. AI search queries
average **70 to 80 words**, a **17 to 26x complexity increase** over 3 to 4 word searches
[s110]. Practical consequences:

- Content should be structured as **self-contained answer units of roughly 134 to 167
  words** for RAG extraction [s110] [practitioner].
- Open informational sections with an entity definition in the **first 40 to 60 words**
  [s220, s273, s269].
- Use **BLUF** (bottom line up front) structure throughout [s269].
- **80%+ topical coverage retains 85.4% of AI visibility** through fan-out variation
  [s110]. A single strong page on a broad topic loses to deep coverage [s268].

**Establishing entity identity.** Create an **"Entity Home"** (usually the About page) with
a stable `@id` URI so facts do not become data islands [s274, s143]. Point `sameAs` at
Wikidata, Crunchbase and LinkedIn [s268, s273, s269]. Validate with the **Google Knowledge
Graph Search API** to monitor your KGMID and confidence score [s272, s274].

**Brand mentions beat backlinks for AI.** Semrush 2025: branded mentions correlate **0.664**
with AI Overview citation against **0.218** for backlinks [s270]. Mechanism: LLMs train on
co-occurrence, so consistent brand-plus-category mentions in credible editorial contexts
bind the brand vector to the topic regardless of hyperlinks [s269].

> **Three honesty flags on this section.** (1) The **3-billion-entity Knowledge Graph prune
> and the 15.27% "Thing" reduction come from a single vendor study by OutpaceSEO** [s274].
> (2) Princeton and Searchbloom report schema boosting visibility **30 to 40%**, but
> **Google's May 2026 AI search guide states structured data is not required to appear in
> AI Overviews** [s220, s268, s179]. (3) The correlation figures above are correlational,
> not causal.

Full detail: `references/ai-search-playbook.md`

---

## Q14 - Pricing and selling SEO

**Bottom line:** Retainers dominate at 78.2% of engagements. Small business is $1,500 to
$5,000/mo, results take 6 to 12 months, and any guarantee of rankings is a red flag. The US
SEO services market is roughly **$82 billion** [s107].

**Retainer ranges by client size** [s260, s261, s119, s277, s275, s107, s163]:

| Segment | Monthly | What it buys |
|---|---|---|
| **Local entry** | **$500 to $1,500** | GBP management, local citations, 1-2 content pieces |
| **Standard SMB** | **$1,500 to $5,000** | Technical health, 3-5 content pieces, semantic SEO, basic outreach |
| **Growth / mid-market** | **$5,000 to $15,000** | 8-15+ content pieces, advanced link building, dedicated strategist |
| **Enterprise** | **$15,000 to $75,000+** | Account team, complex architecture, AI visibility infrastructure |

B2B tech specifics: Series A budgets **$15k to $30k/mo**, pre-IPO **$60k to $150k+/mo**
[s144].

**Project pricing** [s107, s163, s275]:

- Technical SEO audit: **$2,000 to $15,000**, median **$7,500** for 50 to 500 page sites
- Site migration support: **$5,000 to $30,000+**
- Content strategy and cluster map: **$4,000 to $12,000**

**Models and when each fits** [s237, s144, s109, s275, s126, s163, s112, s279, s119]:

1. **Retainer** (78.2% of professionals) for compounding growth.
2. **Hourly, $75 to $300/hr**, for consulting and training only. **Red flag:** hourly for
   ongoing execution, since it penalizes efficiency and makes cost unpredictable.
3. **Project** for launches and migrations with a defined end.
4. **Performance-based**, rare; most agencies avoid 100% performance as unsustainable.
5. **Hybrid retainer plus milestone**, the 2026 trend for incentive alignment.

**Scoping by difficulty** [s260]: KD 0-15 supports **$500 to $1,000/mo**; KD 30-45 needs a
**$2,000 to $3,500/mo minimum**. Quoting below the competitive floor guarantees failure.

**Timeline, the thing to be honest about upfront** [s107, s119, s275]:

| Phase | Months | What actually happens |
|---|---|---|
| Foundation | 1-3 | Technical fixes, schema, strategy. **Minimal traffic movement** |
| Early traction | 4-6 | Long-tail rankings, indexing gains |
| Measurable impact | 6-12 | Meaningful traffic and lead growth |
| Competitive markets | 12-18+ | Full ROI |

Cross-reference: this corroborates `marketing-advisor`'s independently-gathered
**$3,200/mo average AI SEO retainer**, which sits squarely in the Standard SMB band. Two
separate corpora agreeing raises confidence in the range.

> **Not in sources:** despite a pass aimed directly at it, the corpus did not produce solid
> evidence on **client churn rates, standard contract lengths, or a documented rationale
> for why ranking guarantees are a red flag** (beyond the self-evident point that nobody
> controls Google's ranking). Treat those as unresearched rather than settled.

Full detail: `references/seo-as-a-service.md`

---

## Live Query Additions

> Findings from live notebook queries that were not in the original Q1-Q14 synthesis get
> appended here, newest last, using the format in `notebook-live-query.md`. Step 2 of the
> live-query decision flow reads this section first, so a question answered once is never
> re-queried. Run `build_corpus.py verify` after adding any `[sN]` markers.

*(none yet)*

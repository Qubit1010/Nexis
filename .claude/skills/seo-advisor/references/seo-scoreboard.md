# SEO Scoreboard 2026 - the numbers, then the tactic

Default-load reference. Every row leads with the number and carries its tier. `[C]` =
confirmed (Google/Bing docs, web.dev, peer-reviewed). `[P]` = practitioner (vendor blog,
correlation study, case study). `[sN]` resolves via `_research/sources.json`. Full evidence
and the source conflicts are in `research-synthesis.md`.

**Read the tier before you quote the number.** This corpus is 18 confirmed against 302
practitioner sources. Most SEO "facts" are vendors measuring themselves.

---

## Thresholds that are hard requirements

| Metric | Threshold | Tier |
|---|---|---|
| **LCP** (Largest Contentful Paint) | **<= 2.5s** at p75, 28-day CrUX window | `[C]` [s148, s305] |
| **INP** (Interaction to Next Paint) | **<= 200ms** (replaced FID, March 2024) | `[C]` [s299, s230] |
| **CLS** (Cumulative Layout Shift) | **<= 0.1** | `[C]` [s168, s210] |
| Googlebot fetch limit per URL | **2MB** (64MB for PDFs); anything past is unseen | `[P]` [s282] |
| XML sitemap limits | **50MB and 50,000 URLs** per file | `[C]` [s188, s167] |
| robots.txt status | **must return 200**; a 5xx stops crawling sitewide | `[C]` [s299, s188] |
| Redirect chains | 2+ hops adds **100-500ms**; Googlebot may drop past **5 hops** | `[P]` [s297, s302] |
| Click depth | **3 clicks** to any commercial page; 5+ crawled less | `[P]` [s299, s209] |
| URL length | under **60 characters**, lowercase, hyphens | `[P]` [s299, s303] |
| Title tag | **50-60 chars / ~600px**, keyword in first 40 | `[P]` [s296, s207] |
| Meta description | **105-155 chars**, key info in first 120 | `[P]` [s207] |
| Hero image weight | under **150KB**, WebP or AVIF | `[P]` [s295, s292] |
| Mobile load for local | under **2 seconds** | `[P]` [s317, s215] |
| Index coverage health | indexed-to-submitted above **85%** | `[P]` [s252] |

## The AI search layer

| Metric | Value | Tier |
|---|---|---|
| AI Overviews present in results (Q1 2026) | **~47%** | `[P]` [s291] |
| Searches ending without a click | **~60%** | `[P]` [s288, s292] |
| CTR drop when an AI Overview is present | **up to 58%** | `[P]` [s145, s288] |
| Organic top-10 to AI Overview citation overlap | **92% mid-2025 -> ~38% early 2026** (14-17% for AI Mode) | `[P]` [s233, s220, s110] |
| Candidate documents narrowed to citations | **200-500 -> 5-15** | `[P]` [s110] |
| Query fan-out, sub-queries per prompt | **5-11** typical, **10-20** per deeper analysis, hundreds for deep research | `[P]` [s271, s121, s110] |
| AI query length vs traditional | **70-80 words** vs 3-4, a **17-26x** complexity increase | `[P]` [s110] |
| Topical coverage that survives fan-out | **80%+ coverage retains 85.4% of AI visibility** | `[P]` [s110] |
| Ideal extractable answer-unit length | **134-167 words**, self-contained | `[P]` [s110] |
| Entity definition placement | first **40-60 words** of a section | `[P]` [s220, s273] |
| AI referrals as share of total traffic | **under 1%** today | `[P]` [s251, s180] |
| Projected search volume moving to chatbots by late 2026 | **25%** (Gartner projection) | `[P]` [s252] |

### Princeton GEO study - the only causal evidence in the corpus

| Content modifier | Citation lift | Tier |
|---|---|---|
| Adding **expert quotes** | **+41%** | `[P]` peer-reviewed method [s220, s179] |
| Adding **statistics** | **+30%** | `[P]` [s220, s179] |
| Adding **inline citations** | **+30%** | `[P]` [s220, s179] |

This is content structure, not markup. It is the strongest evidence available for any
AI-visibility tactic.

### Platform citation behavior

| Platform | Where it draws from | Tier |
|---|---|---|
| **ChatGPT** | Bing index + Wikipedia (**47.9% of referrals**); **~90% of citations from pages ranked 21+** on Google | `[P]` [s233, s198, s222] |
| **Perplexity** | Real-time search; **Reddit ~half** of top citations; content over **90 days** loses priority | `[P]` [s233, s179] |
| **Gemini** | **~43%** Google properties, **21%** Reddit | `[P]` [s198] |
| **Claude** | Long-form definitive guides, **200k+ token** context, academic signals | `[P]` [s220, s268] |

### AI crawler control

| Bot | Action | Why |
|---|---|---|
| **GPTBot** | Block | Training only, no referral value |
| **OAI-SearchBot** | Allow | Powers ChatGPT citations |
| **ChatGPT-User** | Allow | User-triggered fetch |
| **ClaudeBot** | Block | Training; **70,900 pages crawled per referred visitor** at peak |
| **Claude-SearchBot** | Allow | Retrieval and citation |
| **PerplexityBot** | Allow | Sends referrals |
| **anthropic-ai** | Deprecated | Legacy, do not use in 2026 configs |

`[P]` [s111, s264, s113]. Googlebot's ratio for comparison: **5:1**. Training bots are
**~82%** of AI bot load and return effectively nothing. robots.txt is **voluntary**; real
enforcement is WAF or IP rules, evaluated before robots.txt is read [s116, s111].

**llms.txt: ~10% adoption, honored by nobody.** Google explicitly ignores it and compares
it to the keywords meta tag [s116, s118, s267]. Do not bill for it.

## Off-page

| Metric | Value | Tier |
|---|---|---|
| Brand mentions vs backlinks, correlation with AI Overview citation | **r = 0.664** vs **r = 0.218** | `[P]` correlational [s270, s317] |
| Brands on **4+ third-party platforms** | **2.8x more likely** cited by ChatGPT | `[P]` [s179] |
| Minimum organic traffic for a link prospect | **1,000 monthly visits**; zero-traffic sites pass zero value | `[P]` [s170, s131] |
| DR floor | **DR 30+** baseline, **DR 50+** high-impact; **91% of SEOs** set a floor | `[P]` [s170, s196] |
| Semrush Toxic Score cutoff | drop above **45** regardless of DR | `[P]` [s322] |
| Average cost of an earned digital PR link | **~$750** | `[P]` [s196, s216] |
| Broken link building conversion | **5-15%** | `[P]` [s320, s317] |
| Unlinked mention reclamation conversion | **30-50%+**, highest of any tactic | `[P]` [s317, s193] |
| Journalist outreach yield | **1-2 quality links/month** at 2-3 responses/day | `[P]` [s320] |
| Guest post marketplace quality | **98%** are DR < 40 and < 10k traffic | `[P]` [s216] |
| Link exchange penalty | reported **15-40% ranking drops** | `[P]` [s170, s213] |

## Local

| Signal group | Weight | Tier |
|---|---|---|
| Google Business Profile | **32%** | `[P]` modeled [s191, s172] |
| Reviews | **20%** | `[P]` [s172] |
| On-page | **15%** | `[P]` [s172] |
| Behavioral | **9%** | `[P]` [s172] |
| Links | **8%** | `[P]` [s172] |
| Citations | **6%** | `[P]` [s172] |

Review velocity target **2-4/week** [s137]; **5-15/month sustained 6 months** reported to
move 5-10 map positions [s243]. **50+ reviews in 12 months = 3x** more likely in AI
recommendations; **4.5+ stars = 2x** citation rate [s157] `[P]` single vendor. Respond in
**24-48 hours** [s243]. **46% of Google searches have local intent** [s243, s132]. Primary
category is the strongest single signal [s191, s243].

## Content and on-page

| Metric | Value | Tier |
|---|---|---|
| Title tag optimization impact | **3.7 position** difference | `[P]` [s166, s187] |
| Google title rewrite rate | **61%** (Zyppy) vs **76%** (Backlinko) - conflicting | `[P]` [s166, s295] |
| Pillar page length | **2,500-4,000 words** supporting **8-15 cluster pages** | `[P]` [s288, s128] |
| Clustered vs standalone content traffic | **+30-43%** | `[P]` [s288] |
| Bidirectional internal linking | **2.7x** AI citation probability | `[P]` single vendor [s288] |
| Internal links per 2,000 words | **8-15** | `[P]` [s128] |
| AI-cited content freshness | **25.7% fresher**; **13-week** update cycle | `[P]` Ahrefs [s294, s128] |
| Sites with 5+ interconnected pages on a topic | **3.2x more likely** cited by AI | `[P]` [s288] |

## Keyword research

| Metric | Value | Tier |
|---|---|---|
| Volume estimate variance between tools | **up to 30x** (Moz vs Semrush) | `[P]` [s290] |
| Daily searches that are entirely new | **~15%**, zero historical data anywhere | `[P]` [s290] |
| New-site keyword target | **KD under 20**, volume **100-1,000** | `[P]` [s288] |
| Intent mismatch cost | **35-40%** effectiveness loss | `[P]` [s287] |
| Generative AI intent share on ChatGPT | **37.5%** of queries | `[P]` single source [s247] |
| High-intent vs broad informational conversion | **5-10x** | `[P]` [s127] |

## Measurement

| Metric | Value | Tier |
|---|---|---|
| GA4 misclassification of search traffic | **30-50%** as Direct/Unassigned | `[P]` [s254] |
| GA4 undercount of AI referrals vs server logs | **8-31%** | `[P]` [s253] |
| GA4 data retention default | **2 months**, must be raised to **14** | `[C]` [s251, s254] |
| CTR gain, position 8 to position 4 | **~1% to ~5%**, roughly **400% more clicks** | `[P]` [s252] |
| Mature SEO program return | **3-5x cost** | `[P]` [s252] |
| Median SEO ROI | **748%** | `[P]` [s259] |
| Organic CPA vs paid CPA | **40-70%** of paid | `[P]` [s252] |
| Strong brand AI mention rate | **15%**; category leaders **35-50%** SOV | `[P]` [s252] |

## Pricing and delivery

| Segment | Monthly | Tier |
|---|---|---|
| Local entry | **$500-$1,500** | `[P]` [s260, s261] |
| Standard SMB | **$1,500-$5,000** | `[P]` [s119, s277] |
| Growth / mid-market | **$5,000-$15,000** | `[P]` [s275, s107] |
| Enterprise | **$15,000-$75,000+** | `[P]` [s275] |
| Technical audit (one-off) | **$2,000-$15,000**, median **$7,500** | `[P]` [s107, s163] |
| Migration support | **$5,000-$30,000+** | `[P]` [s275, s107] |
| Hourly | **$75-$300**, consulting only | `[P]` [s275, s126] |
| Retainer adoption | **78.2%** of professionals | `[P]` [s112, s259] |

**Scoping floor by difficulty:** KD 0-15 supports $500-$1,000/mo; **KD 30-45 needs $2,000-$3,500/mo minimum** [s260].

**Timeline:** months 1-3 foundation with minimal movement, 4-6 early traction, 6-12
measurable impact, 12-18+ for full ROI in competitive markets [s107, s119, s275].

---

## Confirmed ranking factors (only seven)

Backlinks, content quality / E-E-A-T, HTTPS, page speed / Core Web Vitals,
mobile-friendliness, freshness, page experience [s283].

## Confirmed NOT ranking factors

**Bounce rate** (as measured in GA), **domain age**, **social signals**, **XML sitemaps**
as a ranking input, **meta keywords**, and **word count** [s283, s166]. Structured data is
**not a direct ranking factor** either, per John Mueller [s149, s212, s178].

## The floor-versus-lever rule

Core Web Vitals, mobile-friendliness and HTTPS are a **ranking floor**. Failing them
suppresses you; exceeding them buys nothing further [s296, s293, s295]. Stop optimizing
past "good" and go do content or links.

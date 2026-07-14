# Research Techniques — Cited Synthesis (2026)

Master research doc for the `research` skill. Built research-first from **108 unique 2026 sources**
gathered via Exa full-text passes across six questions (Q1-Q6). Every load-bearing claim traces to
a source. Inline `[n]` resolves to `_research/sources.json` → `sources[n-1]` (index == citation
number). Raw per-question source text lives in `_research/exa/q*.json`.

**Honesty rule:** every technique and number here traces to a 2026 source in the corpus. Where a
figure was not found or is provider-quoted (pricing especially), it is flagged. Do not invent or
extrapolate. Pricing and vendor facts in this category go stale fast — treat them as "verify before
quoting to a client."

---

## Q1 — How to research any topic (methodology, triangulation, credibility)

A modern research pass is a **workflow, not a single search**: define the question, search
broadly, evaluate and filter sources, then synthesize with citations [1][2][6]. The reusable loop
is: (1) frame a precise, answerable question and sub-questions; (2) cast a wide net; (3) evaluate
each source; (4) triangulate across independent sources; (5) synthesize, citing as you go [1][6].
For high-stakes/scientific questions, the systematic-review discipline applies: a documented,
reproducible process — protocol, comprehensive search, screening, extraction, synthesis — so the
result is defensible rather than cherry-picked [13][15][16][18].

**Evaluating a source — go beyond CRAAP.** The classic CRAAP test (Currency, Relevance, Authority,
Accuracy, Purpose) is a checklist starting point, but 2026 library guidance argues it is not enough
on its own and should be paired with critical thinking and metacognition [7]. The stronger, evidence
-backed move is **lateral reading**: instead of scrutinizing a page's own content ("vertical
reading"), open new tabs and check what *other* independent sources say about the source. Wineburg &
McGrew's study found professional fact-checkers evaluate credibility faster and more accurately by
reading laterally, whereas students and even academics who read vertically are more often fooled
[8][12]. Practical 4-step moves: (1) who is behind the information, (2) what is the evidence, (3)
what do other sources say, before trusting a claim [9][11].

**Triangulation** — confirming a claim across multiple independent sources — is the core defense
against a single wrong or biased source [1][10]. In this skill it is operationalized by the
fusion layer: a URL/claim returned by several engines outranks one returned by one.

Sources: [1] Rhino Scholar question-to-citation workflow · [2] Research Process steps · [6] desci.com defensible lit review · [7] Expanded CRAAP (CRLN) · [8] Lateral & critical reading (Rowan) · [9][11] Evaluating online sources 4-step (CRLN/Butler) · [10] NMH evaluating sources · [12] Wineburg/McGrew lateral reading · [13][15][16][18] systematic review process guides.

---

## Q2 — Query formulation and Google-dork keyword crafting

**Keyword base-formatting.** Effective queries start from concepts, not sentences: identify the core
concepts, list synonyms/variants, then combine with operators [25][26][29]. Broaden with `OR` and
truncation/synonyms; narrow with added terms, phrases, and exclusions [25][30][32].

**Operators that still work in 2026** (verified across googleguide, Google's own help, and current
cheat-sheets [19][21][31][32][34][36]):
- `"exact phrase"` — force an exact match / word order [21][32][34].
- `site:` — restrict to one domain or TLD (`site:linkedin.com/in`, `site:.gov`) [21][31][36]. The
  single most useful dork for targeted discovery.
- `-term` — exclude a word [21][32].
- `OR` (or `|`) — either term; `( )` group logic [21][34].
- `intitle:` / `allintitle:` — term(s) in the page title [21][36].
- `inurl:` / `allinurl:` — term(s) in the URL [21][36].
- `filetype:` (a.k.a. `ext:`) — restrict to a file type (`filetype:pdf`, `filetype:xlsx`) [21][31][36].
- `intext:` / `allintext:` — term(s) in body text [21][36].
- `related:` — sites similar to a domain [21][32]. `cache:` is **deprecated/removed** [31].
- `AROUND(n)` — two terms within n words of each other (proximity) [31][34].
- `*` — wildcard placeholder within a phrase [34][36].
- Combine freely: `site:linkedin.com/in ("founder" OR "CEO") "acme corp"` [39][41].

Google's own "Refine web searches" help page is the authoritative operator reference; the
Semrush/Kinsta/SearchEngineLand cheat-sheets aggregate the working set [20][21][31][32]. A large
share of listed "dork" operators still behave; a few (`+`, `~`, `cache:`) have been retired [31].

Sources: [19] Google Guide operators · [20] Semrush cheat sheet · [21] Kinsta 40 operators 2026 · [22] gwern all-operators PDF · [25][26][29][30] search-strategy formulation guides · [31] SearchEngineLand 19 operators (+ retired) · [32] Google refine-search help · [34] Cited 50 examples · [36] techpp 35+ commands.

---

## Q3 — Finding people (founders, decision-makers, contact)

**LinkedIn X-ray search** is the workhorse: LinkedIn hides most profiles from its own logged-out
search, but Google has them indexed, so search Google with `site:linkedin.com/in` plus name/title/
company to surface profiles for free [37][41][42]. Examples:
- `site:linkedin.com/in "acme corp" (founder OR "co-founder" OR CEO)` — leadership of a company [39][41].
- `site:linkedin.com/in "VP marketing" "fintech" "London"` — role + industry + geo [40][66].
OSINT guidance adds pairing X-ray with the company's People page, employee-count cross-checks, and
mapping networks rather than trusting a single hit [38][39][40].

**Finding the email.** The reliable 2026 pattern is: (1) determine the company's email format (most
use `first.last@`, `first@`, or `flast@`), then (2) generate permutations, then (3) verify before
sending [43][44][45][46]. Format discovery: find one known employee email (press page, WHOIS, GitHub
commits, a signature) to reveal the pattern [44][47][48]. **Email permutators** generate every
plausible combination from first/last/domain [49][50][51][54], and there are open-source permutators
[52][53]. Always run the candidates through a verifier (SMTP/MX validation) to avoid bounces —
guessing without verification burns sender reputation [43][45][49]. Paid enrichment (Hunter,
Apollo-style) short-circuits this but the free path above works [46][48].

Sources: [37][41][42] LinkedIn X-ray guides · [38][39][40] LinkedIn OSINT/SOCMINT · [43][44][45][46][47][48] find CEO/decision-maker email methods · [49][50][51][54] email permutators/verifiers · [52][53] open-source permutators.

---

## Q4 — Finding and profiling companies

**Company OSINT** starts with the owned surface (site, About/Team, careers, blog) and radiates to
third-party signals [55]. High-signal, low-cost moves:
- **Tech stack detection** — `BuiltWith` and `Wappalyzer` (site + browser extension) reveal the
  CMS, analytics, frameworks, hosting, and martech a site runs [67][68][69][72]; newer lookups
  (`WhatStack`, `WhatBuilt`) do the same [70][71]. This is "technographics" — using tech signals to
  qualify and segment prospects [58]. For agencies this exposes what a prospect is built on (e.g.
  WordPress vs Webflow) and where you can help.
- **Hiring signals** — open roles reveal priorities, budget, and pain (a company hiring 3 React devs
  is investing in frontend; hiring a "RevOps" lead signals scaling pains) [56][59][60].
- **Funding / firmographics** — Crunchbase is the standard for funding, headcount, founders, and
  investors; Crunchbase Pro adds advanced/saved search [61][62][63][65]. Pair LinkedIn + Crunchbase
  to build B2B lead lists [64].
- **Dorks** — `site:company.com (careers OR jobs)`, `"company name" (funding OR raised OR "series
  a")`, `site:linkedin.com/company "company name"` [39][66].

Sources: [55] Company OSINT · [56][59][60] tech-stack + hiring-signal scraping · [57] public tech-stack signals · [58] technographics guide · [61][62][63][65] Crunchbase · [64] LinkedIn+Crunchbase B2B · [66] LinkedIn Xray · [67] BuiltWith · [68][69][72] Wappalyzer · [70][71] WhatStack/WhatBuilt.

---

## Q5 — Extracting from Google/SERPs, and when to use which primitive

There are **three distinct API families**, and picking the wrong one is the most common way builders
overpay [73][77][78]:
1. **SERP APIs** (Serper, SerpApi) — return the raw Google results page as JSON (organic, knowledge
   graph, places, "people also ask"). Cheap, fresh, exact-Google. But you do the snippet-cleaning and
   ranking yourself — no page content, no synthesized answer [73][78][79][94]. Best for freshness,
   dorking, people/company lookups, and knowledge-graph facts.
2. **AI / retrieval search APIs** (Exa, Tavily, Brave) — return a small, ranked, deduplicated list of
   titles + URLs + clean snippets, LLM-shaped so an agent can quote them directly [73][77][94].
3. **Content-scraping / extraction APIs** (Firecrawl, Jina Reader) — you hand a *known URL*, they
   return the full page as clean markdown/JSON [78][92]. Best once you already know where to look.

**Serper vs SerpApi:** both wrap Google; Serper markets itself as the fastest/cheapest, SerpApi as the
broader/more-structured. Independent 2026 benchmarks compare them head-to-head [79][80][81][82][84].
For this skill, Serper is the configured SERP backend (`SERPER_API_KEY`).

**Exa neural vs keyword vs auto:** Exa's index supports `keyword` (classic term match), `neural`
(embedding/semantic — "find docs that *mean* this", including its `findSimilar`), and `auto` (Exa
picks) [85][88]. Neural/semantic search finds conceptually-related pages that keyword search misses,
at the cost of exact-term precision [86][89][90]. Use `neural` for exploratory/topical discovery,
`keyword` for exact names/quotes, `auto` when unsure [85][87].

Sources: [73] Web-search API types · [74] choosing a search API · [75] APIs compared · [76] best SERP API · [77] SERP vs AI search · [78] SERP vs content-scraping · [79] Serper · [80][81] SerpApi · [82][84] SerpApi vs Serper benchmark · [85][88] Exa neural/keyword/auto · [86][87][89] Exa docs/evals · [90] semantic vs keyword.

---

## Q6 — Choosing/optimizing the service, and verifying the answer

**The two-layer mental model** (the single most useful framing): search (query → ranked passages:
Tavily, Exa) is a *different layer* from extraction (URL → clean page: Firecrawl, Jina Reader).
Most production research needs both — search to find the 3 pages that matter, extract to read them —
and picking one vendor for both jobs is where money leaks [92].

**The Full / Fast / Index primitive** framework [95]:
- **Full** — send a query, get a synthesized *cited answer* (vendor runs retrieval + writing).
  Perplexity Sonar, deep-research tiers. In this skill: OpenAI synthesis and Exa `answer`/agentic
  `research`. Use when you want a finished answer.
- **Fast** — query → low-latency, LLM-ready ranked snippets, you synthesize. Tavily, Exa Fast. This
  is the skill's medium default.
- **Index** — raw index access (semantic + keyword) you rank/filter yourself; Exa most purely, plus
  independent keyword indexes like Brave. Use when you need control [95].

**Cost (list prices, 2026 — VERIFY before quoting; this category re-prices constantly** — Exa raised
$250M, Tavily was acquired by Nebius in 2026 [95]): per ~1k searches, Serper ~$1 (drops to ~$0.30 at
scale), Firecrawl ~$0.85, Brave ~$5, Perplexity ~$5, Exa ~$7, Tavily ~$8 [93]. Agents fan out
**80-240 web searches per task**, and routing per query-class instead of defaulting to one premium
engine can cut cost **up to ~8.2×** [93]. Practical routing: Serper for cheap web/news links and
dorks; Exa for semantic/academic/page-content retrieval; Tavily for RAG-shaped "give me an answer-
ready blob"; Jina Reader when the extraction budget is zero [92][93][94][95]. Scorecards rate Exa and
Tavily at the top for agent web search, near-tied [91][96] — treat single-benchmark rankings as
indicative, not gospel (small per-class n) [93][96].

**Verifying the answer / reducing hallucination** (research-backed):
- **Grounding = the answer must be consistent with the cited sources only.** Verify by checking each
  claim against its cited source; discrepancies get refined or dropped [97][99].
- **Chain-of-Verification (CoVe)** — draft, generate fact-check questions, answer them independently,
  then produce the verified response — measurably reduces hallucination [101].
- **Post-hoc citation-enhanced generation (CEG)** — retrieve supporting docs for each generated
  statement and regenerate anything unsupported; a training-free plug-in that beats prior methods on
  hallucination benchmarks [100]. Faithful citation-attribution frameworks (CiteGuard) approach human
  accuracy on citation matching [98]. Note the real risk: **50+ citation hallucinations were found in
  300 ICLR 2026 submissions** — LLMs invent plausible citations [98], which is exactly why this skill
  never lets the model cite anything outside the gathered `sources.json`.
- **Relevance optimization** — a semantic re-ranker as a final step reliably lifts result quality on
  top-k [103]; standard relevance metrics are precision/recall, MAP, MRR, nDCG, precision@k [104].
  In this skill, cross-source agreement (fusion) is the cheap re-ranking signal.

Sources: [91] Exa/Tavily/Serper/Brave scorecard · [92] two-layer search-vs-extraction · [93] data-backed costs + routing 8.2× · [94] Tavily/Exa/Serper output shapes · [95] Full/Fast/Index + market moves · [96] 8-API agentic benchmark · [97] CaLM grounding · [98] CiteGuard + ICLR citation-hallucination finding · [99] AGREE grounding · [100] CEG post-hoc · [101] Chain-of-Verification · [102] Acurai RAGTruth · [103] semantic reranking · [104] relevance metrics.

---

## Live Query Additions

_Append cited findings here when a live NotebookLM/Exa query fills a gap the sections above miss.
Format: `### [YYYY-MM-DD] (Q# - Topic) <question>` then bullets, then a `Source:` line._

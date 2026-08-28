# Blog Writing + SEO/AEO/GEO/AIO — Research Synthesis (2026)

**Research basis:** Built research-first via the `research` skill's deep multi-engine passes (Exa neural + Serper/Google + Jina; Tavily was quota-capped that day). 83 unique 2026 sources indexed in `_research/sources.json`; the five raw passes are `_research/q1..q5.json` and the concatenated synthesized reports are `_research/reports.md`.

**Citation scheme:** Inline `[sN]` = the global source index in `_research/sources.json` (so `s34` = source #34, the Google generative-AI guide). Resolve any `[sN]` to a real URL there.

**Honesty rule (non-negotiable):** Every load-bearing number traces to a source here or is explicitly flagged. Two flags are used throughout:
- **[peer-reviewed]** — from a 2026 academic study in the corpus.
- **[practitioner]** — an industry heuristic (2026 SEO guides, or the installed `ai-seo` skill / the Princeton GEO KDD-2024 study it cites). Useful and widely used, but NOT independently confirmed by the academic pass. Where the academic pass actively *could not* confirm a popular claim, it says so.

**Companion skill:** the installed `marketing-skills:ai-seo` skill is the exhaustive AEO/GEO methodology reference (robots.txt for AI bots, `llms.txt`, OKF, schema types, the Princeton GEO per-method table, content-type citation shares). This synthesis validates and dates the load-bearing parts and flags what is practitioner-only. When a blog needs the deep AEO/GEO checklist, cross-reference `ai-seo`; when it needs the cited 2026 evidence, use this file.

**Date:** 2026-07-21.

---

## Q1 — Blog SEO fundamentals that still move rankings (2026)

**Headline:** In 2026 blog SEO is people-first, experience-backed, topically-authoritative content on a clean on-page structure that both search engines and AI answer engines can parse [s1][s3][s5][s16]. The mechanics below are evergreen and confirmed across Google's own docs and multiple 2026 guides.

- **People-first, helpful content is the foundation.** Google's guidance: create helpful, reliable content that shows who made it and why, not content built to rank [s1]. This is the lens for planning and auditing everything else [s5][s16].
- **E-E-A-T (Experience, Expertise, Authoritativeness, Trust)** is the practical quality bar for competitive topics — demonstrate first-hand experience and clear authorship [s1][s8][s12][s20]. The sources frame E-E-A-T as *what good content looks like*, not a dial you turn; they do not quantify its ranking weight [s12][s20]. **[practitioner]** for any specific "score."
- **Keyword strategy = intent + topical clusters, not isolated terms.** Map content to search intent and semantic coverage of a topic, not single keywords [s5][s16][s1]. This also feeds AI answer engines (Q2/Q3).
- **Title tags & meta descriptions:** unique, descriptive, accurately summarizing the page [s3][s9]. Exact character limits are **not** in Google's docs; the durable industry convention is title ~50-60 chars / meta description ~150-160 chars **[practitioner]** [s9].
- **Heading hierarchy:** one clear H1, logical H2/H3 that communicate structure and map to sub-questions [s3][s7][s9]. This is also the single biggest lever for AI extractability (Q3).
- **Internal linking:** connect related posts into topical clusters/pillars with descriptive anchor text [s0][s3][s7].
- **Structured data:** implement `Article`/`BlogPosting` schema so engines understand the page and it's eligible for enhanced results [s3][s19]. See `ai-seo` for the full schema-type table. Schema's effect on *AI citation* specifically is an open question (Q5, [s76]).
- **Freshness / updating:** periodically update, consolidate overlapping posts, prune the unhelpful ones — ongoing maintenance is a 2026 quality signal, and a visible "last updated" date matters [s0][s4][s7].
- **On-page fundamentals still count:** clean descriptive URLs/slugs, meaningful headings, descriptive anchors, image `alt` text [s3][s7][s21].

**Gaps flagged by the sources:** exact title/meta lengths, optimal update cadence, and the measurable ranking impact of E-E-A-T are not quantified in these materials — treat those as qualitative or practitioner conventions [s3][s7][s1][s12].

---

## Q2 — AEO / GEO: getting a blog cited by AI answer engines (2026)

**Headline:** Being *cited* by ChatGPT/Perplexity/Claude/Gemini is a different game from ranking #1. The strongest 2026 academic signals: (1) query-intent alignment predicts AI citation better than Google rank; (2) explicit, modular on-page structure raises citation likelihood; (3) AI citations are *not* confined to top-ranked pages. Effect sizes are mostly directional; one benchmark reports up to a 40% visibility lift from GEO methods.

- **Query intent > Google rank** as a predictor of AI citation [s27] **[peer-reviewed]**; intent and rank act *jointly*, with intent often the stronger signal [s30] **[peer-reviewed]**. Practical read: tailor the page to the dominant intent(s) behind the target query.
- **Structure shapes whether you're cited, not just whether you influence the answer.** Page-level structural features (clearly labeled, modular sections) measurably raise citation likelihood over unstructured prose with the same content [s26] **[peer-reviewed]**. There's a named failure mode — "citation failures," where a source influences the answer but isn't cited — with diagnostic/repair methods [s28] **[peer-reviewed]**.
- **The "SEO floor":** AI-cited pages are drawn from across Google's rank distribution, not just the top results — GEO is not reducible to classic SEO [s29] **[peer-reviewed]**. A page ranking on page 2-3 can still be the cited source.
- **Effect size:** GEO-bench-style controlled evaluations report proposed GEO methods can boost generative visibility **up to ~40%** across diverse queries [s31] **[peer-reviewed]**. Field referral analytics must be corrected for platform growth before crediting optimization [s25].
- **Treat GEO as complementary to SEO:** keep baseline search visibility, but prioritize intent coverage + extractable structure [s29][s30].

**Honesty flags (important — these popular claims were NOT confirmed by the 2026 academic pass):**
- The **Princeton GEO per-method boosts** ("cite sources +40%, add statistics +37%, add quotations +30%, authoritative tone +25%, keyword stuffing -10%") come from the **Princeton/Georgia Tech GEO paper (KDD 2024)** as carried in the `ai-seo` skill. This deep pass did **not** independently surface that ranking [s24 is the closest — a 2026 GEO survey]. Use the numbers as **[practitioner]**, attribute them to the Princeton GEO study, and treat the *direction* (cite sources, add stats/quotes, don't keyword-stuff) as safe; the *exact percentages* as indicative.
- The **"40-60 word extractable answer block"** length is a **[practitioner]** heuristic (from `ai-seo` / industry snippet-optimization lore). None of the academic sources specify an optimal answer-block word count [s24][s26][s27]. The *principle* — lead each section with a short, self-contained, quotable answer — is well supported [s26]; the exact 40-60 window is convention, not evidence.
- Whether **adding statistics/quotations** causally increases AI citation independent of structure is **not** established in these sources [s26][s28]. It's a reasonable, low-risk practice (and matches the Princeton claim), but label it honestly.

**Actionable core (what the evidence does support):** answer the dominant intent; open each H2 with a short, self-contained, extractable answer; use explicit labeled structure (definitions, steps, comparisons, FAQ); cite real sources and include specific data; don't assume top-rank is required.

---

## Q3 — Google AI Overviews & AI Mode (AIO) (2026)

**Headline:** Google's official stance is that there are no "AIO hacks" — generative features run on core Search quality, so helpful people-first content + clean structure is the path in [s34][s42][s48]. Practitioner playbooks converge on answer-first writing, semantic HTML, and topical clusters that cover query fan-out.

- **Google's official guidance** exists and is explicit: optimize for people and core Search; no special markup/files are required for AI Overviews or AI Mode; demonstrate E-E-A-T [s34][s42][s45][s48]. Aleyda Solís and SEL both flag it as the authoritative reference [s39][s48].
- **Zero-click reality:** ~68-69% of searches now end without a click, per 2026 analyses — being *in* the AI answer matters even if you "rank" [s35][s36]. Treat the exact figure as directional (sources vary 68% vs 69%).
- **Answer-first, scannable structure wins:** concise summary high on the page, clear H2/H3 mapped to sub-questions, lists, tables for comparisons, FAQs that anticipate follow-ups [s37][s38][s44]. Semantic HTML helps AI parse and quote the right segment [s34][s37].
- **Query fan-out + topical clusters:** Google's AI expands one query into many concurrent related queries. Cover the parent topic plus its fan-out (alternatives, troubleshooting, decision criteria, adjacent entities) and interlink the cluster, so you're retrievable across the whole conversational chain [s46][s37][s38].
- **Formats that surface in AI Overviews (practitioner-observed):** practical guides, comparisons, pros/cons, step-by-step walkthroughs [s36][s37][s38]. **[practitioner]** — consistent across guides, not a controlled study.
- **AI bot access:** to be cited, don't block the AI crawlers (GPTBot, ChatGPT-User, PerplexityBot, ClaudeBot/anthropic-ai, Google-Extended) in `robots.txt`; block training-only crawlers (CCBot) only if you must [s43]. Full config in `ai-seo`.
- **Measurement:** Google Search Console now exposes an "AI Mode" option under Search Appearance to see impressions/clicks from AI experiences [s40][s41]; third-party tools (Otterly, Peec, ZipTie) track cross-platform citation [s40].

---

## Q4 — Writing long-form that reads human, not AI-generated (2026)

**Headline:** The reliable way to sound human (and avoid false AI-detection flags) is authentic voice + specific detail + varied sentence rhythm + a phrase audit — not "humanizer" tools. Detectors have real false-positive rates, so writing with genuine voice beats gaming a classifier [s54][s55][s62].

- **AI tells to purge — recurring words / stock phrases.** Pangram Labs maintains a large list of AI-favored words and phrases; audit the draft and replace hotspots with precise, topic-specific language [s51][s66]. Practitioner "robot-style" checklists help you self-spot [s53]. Common offenders: "game-changer," "leverage," "dive into," "unlock," "seamlessly," "in today's fast-paced world," "it's not just X, it's Y," "it's important to note that."
- **Cadence / burstiness.** Uniform, polished, same-length sentences across a whole piece are the #1 tell. Deliberately vary sentence length — mix long (12-18 words) with short (4-7) — and read aloud to catch monotone stretches [s55][s67].
- **Draft in layers**, not one polished pass: (1) idea dump, (2) organize + add evidence/examples, (3) a final pass purely to vary rhythm and tighten voice. The one-pass uniformity is what detectors and readers flag [s55].
- **First-person voice + concrete specificity.** Write from real process, constraints, and decisions; swap generic claims for specific numbers/examples. Generic prose is exactly what gets flagged [s52][s55][s73].
- **Replace template transitions** ("Furthermore," "In conclusion," "Moreover") with your own connective tissue [s55].
- **Don't chase detector-gaming / paraphrase gimmicks.** Fully human text is sometimes flagged as AI [s56][s62]; the durable answer is originality + voice + cadence + specificity, not a "humanizer" [s54][s55]. Exact false-positive rates aren't quantified in these sources [s55][s62]. **[practitioner]** for any specific detector percentage.
- **E-E-A-T-driven humanization:** first-hand experience and a real point of view are both a ranking signal (Q1) and the strongest human tell [s73].

**This maps directly onto Aleem's existing voice framework** — see `agency/personal-brand-voice.md` (the "Unswappable" formula, the So-What test, the specificity rules, the ASCII-only / no-em-dash mechanics). The research above is the evidence base under it; `references/human-tone-rules.md` distills both into the pre-publish checklist.

---

## Q5 — Do specific blog formats rank / get cited more? (2026)

**Headline (honest null result):** The 2026 academic pass found **no direct, controlled evidence** that any named blog format (comparison, definitive guide, original research, how-to, listicle, opinion) consistently ranks higher or is cited more. What the studies support is that *structure, query intent, rank, and possibly schema* drive AI citation — format is a proxy for those, not an independent lever [s26][s27][s30][s76].

- No study head-to-head compares format types for Google rank or AI-citation rate [s76][s77][s78][s79][s80]. Anyone claiming "listicles get cited X% more" is extrapolating.
- **Schema markup as a citation predictor** was studied on 730 ChatGPT-with-browsing citations, but the abstract doesn't report effect direction/magnitude — it's an open question, not a proven lever [s76] **[peer-reviewed, inconclusive]**.
- **Hybrid human-AI authorship** shows readability/SEO benefits over pure-AI in one comparison, supporting a "human writes + edits, AI assists" workflow rather than pure generation [s79] **[peer-reviewed]**.
- **No empirically-supported "ideal word count"** for ranking or citation appears in these sources [s78][s79]. Length should follow topic depth and intent, not a magic number.

**Practitioner fallback (labeled):** the `ai-seo` skill carries industry citation-share figures (comparison articles ~33%, definitive guides ~15%, original research ~12%, listicles ~10%, how-to ~8%, opinion ~10%). Use these as **[practitioner]** directional priors for *what to prioritize when the topic allows a choice* — comparison and definitive-guide angles are reasonable defaults — but never present them as measured fact, because this pass could not confirm them.

**Net guidance:** pick the format that best serves the query's intent and lets you lead with extractable answers and real experience. That satisfies both the peer-reviewed structure/intent findings and the practitioner format priors.

---

## Reconciliation with the `ai-seo` skill (who owns what)

| Claim | Status here | Source of truth |
|---|---|---|
| People-first / E-E-A-T / on-page / schema / freshness | Confirmed 2026 | This synthesis Q1 [s1][s3] + `ai-seo` |
| Answer-first structure, semantic HTML, query fan-out, AI-bot robots.txt, GSC AI Mode | Confirmed 2026 | Q3 [s34][s46] + `ai-seo` |
| Structure & query-intent drive AI citation; GEO ≠ SEO; ~40% GEO lift | Peer-reviewed 2026 | Q2 [s26][s27][s29][s31] |
| Princeton GEO per-method boosts (+40/+37/+30…) | Practitioner (KDD-2024) | `ai-seo` — attribute, don't invent |
| 40-60 word answer block | Practitioner heuristic | `ai-seo` / industry — principle sound, exact window is convention |
| Format citation shares (comparison 33% …) | Practitioner, unconfirmed | `ai-seo` — directional prior only |
| Human-tone / anti-AI-tell craft | Confirmed 2026 | Q4 [s51][s55][s73] + `voice-principles.md` |

---

## Live Query Additions

> When the loaded references + this synthesis don't answer a specific question, run a fresh `research` deep pass per `references/notebook-live-query.md`, present the cited answer, then append it here (newest at bottom) so it's reusable. Format: `### [YYYY-MM-DD] (Q# - topic) question` + bullets + a `Source:` line.

_(none yet)_

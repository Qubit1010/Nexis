# Content scoreboard — what actually moves outcomes

Load this in **advise** mode. **Number first, then the tactic.** Ranked by strength of
evidence, not by how often the tactic gets recommended - the two orderings are close to
inverted in this field.

Evidence in `research-synthesis.md`. `[C]` confirmed, `[P]` practitioner, `[P*]` first-party
platform documentation, `[K]` craft (never evidence).

---

## Tier 1 — Strong evidence, act on it

| Finding | Evidence | What to do |
|---|---|---|
| Engagement with instructional video drops sharply after **~6 minutes**, across **6.9 million viewing sessions** | `[C]` | Chunk teaching content into sub-six-minute units. Attribute it as educational research, because it is |
| **Segmenting** reduces cognitive load and improves retention | `[C]` [s41][s183] | Break any long-form video or lesson into explicit segments with their own payoffs |
| Showing the presenter's **face** improves retention and directs visual attention | `[C]` [s190][s24] | Put a person on screen. Screencast plus face beats slides-only |
| **Graphics beat text for long-term retention**, and improve reading comprehension by meta-analysis | `[C]` [s34][s239][s29] | Use visuals to carry the thing you need remembered, not to decorate |
| **Visual encoding choice is measurable** - some encodings are read more accurately than others | `[C]` [s240][s235][s238] | Pick the encoding for the judgment the reader has to make. Position beats angle beats area |
| **Emotion and arousal predict sharing; information suppresses it.** Information-focused video ads shared significantly *less*, except in risky contexts | `[C]` | Lead with the emotional frame. Put the specification lower down |
| Apparent virality differences **mostly disappear once you match on cascade size** | `[C]` [s14][s16] | Before accepting "their content spreads better", compare like-sized cascades |
| Seeding **hubs and bridges** beat the alternatives in two field experiments plus a live campaign | `[C]` [s11][s15][s110] | Seed high-degree and high-betweenness people. Do not seed the fringe on the strength of a blog post |
| Attention decays as **novelty** decays, following a universal form | `[C]` [s20][s126] | Plan for decay. Evergreen and trending need different cadences because their curves differ |
| Observational attribution produces **large errors against experimental ground truth** across ~2,000 Meta campaigns | `[C]` [s28] | Never present attribution as causal. Use holdouts or geo tests when the spend justifies it |
| **Source credibility** has meta-analytic support and two measured dimensions: competence and trustworthiness | `[C]` [s85][s92][s93] | Build authority from demonstrated competence, not publishing volume |

---

## Tier 2 — Real but conditional

| Finding | Evidence | The condition |
|---|---|---|
| Owned social media positively affects sales | `[C]` [s6][s18] | The average effect is **modest** and much smaller than the engagement effect. Direction, never a multiple |
| Firm-generated content moves purchasing and cross-buying | `[C]` [s72] | Single-firm customer panel, not a general estimate |
| Social presence drives purchase intention in live commerce | `[C]` [s51][s56][s42] | Survey and PLS-SEM designs dominate; the review itself calls for experiments `[C]` [s17] |
| Non-sponsored UGC beats sponsored, mediated by authenticity | mixed | The clearest statement is an MSc thesis. The peer-reviewed layer supports UGC raising purchase intention `[C]` and credibility being central `[C]` [s22][s39] |
| Disclosure affects response to sponsored content | `[C]` [s84][s79] | Effects run through credibility, so disclosure done well is not automatically a cost |
| Paid advertising can generate **earned** impressions | `[C]` [s111] | One of the few parts of the owned/earned/paid framework with actual support |
| Interactivity and vividness correlate with engagement | `[C]` | Findings are mixed across platforms and metrics. Correlational |

---

## Tier 3 — Where it backfires or misleads

| Trap | Evidence | What happens |
|---|---|---|
| **Completion rate as a quality signal** | `[C]` [s31] | Shorter videos win mechanically. You will optimise toward triviality |
| **Comparing views across platforms** | `[C]` [s1], `[P*]` [s426] | The counting rules differ. The ratio is not a number |
| **Comparing engagement rates between accounts or vendor tables** | `[C]` [s1] | No single formula exists; denominators vary. Two tables can both be right and disagree |
| **Open rate as a 2021-onward metric** | `[P]` | Apple MPP registers opens nobody performed. Cross-period and cross-list comparisons are invalid |
| **Information-dense video ads built for sharing** | `[C]` | Information significantly reduced sharing outside risky contexts |
| **Publishing more to fix underperformance** | `[C]` [s99][s108] | Frequency has carryover and diminishing returns. More is not monotonically better |
| **Treating population consumption data as performance data** | `[C]` | "33% get news on TikTok" says nothing about whether TikTok works for this client |

---

## Tier 4 — Weaker than sold

| Sold as | Actually |
|---|---|
| An optimal posting frequency exists | **The formal work says it depends** on carryover and response curvature; pulsing, flighting and continuity can each be optimal `[C]` |
| "Thought leadership" is a discipline with best practices | No confirmed literature under that name. The real construct is **source credibility**, which has 60 years of measurement `[C]` [s93][s85] |
| Repurposing multiplies reach | The multiplier is folklore. Derivative quality is bounded by the source asset |
| Refreshing content restores its traffic | The novelty model implies it should, and **no study here tests the tactic** |
| Podcast market sizes and format preferences | Almost entirely vendor-published `[P]`. Only listening *motivations* are peer-reviewed `[C]` [s36] |
| Webinars have best practices | No literature under that name. What exists is live-commerce and synchronous-instruction research. Treat webinar advice as `[K]` |
| Memes as a brand tactic | Almost no direct evidence. Covered obliquely through diffusion. `[K]` |
| AI content is detectable / undetectable | Both overstated. Detection works but degrades under editing, domain shift and model updates, and humans are not reliably better than machines `[C]` [s25][s158][s162] |

---

## The meta-lesson

**Almost every number in this field is a measurement definition problem before it is a
performance question.** Engagement has no canonical formula, views count different events on
different platforms, completion is duration-biased, opens have been broken since 2021, and
attribution is not incrementality.

Before answering "is this performing", establish what the number counts. Most of the time that
conversation is more valuable to the client than the benchmark they asked for - and it is the
one thing no vendor dashboard will tell them.

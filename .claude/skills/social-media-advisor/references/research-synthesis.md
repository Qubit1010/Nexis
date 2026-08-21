# Research synthesis — social media platforms and accounts, 2026

The master cited document. **329 sources: 119 confirmed / 77 craft / 133 practitioner, of which
60 are first-party platform documentation.** 17 deep passes via the in-repo `research` skill
(Exa + Tavily + Serper + Jina fused), built 2026-08-21.

`[sN]` resolves in `_research/sources.json` **on the `index` field, not list position.** The
index sequence has deliberate gaps where nine junk sources were purged; existing citations are
unaffected, which is the point of not renumbering.

## The tier contract

| Tag | Tier | May be used for | May NOT be used for |
|---|---|---|---|
| `[C]` | confirmed | Supporting a factual claim about algorithmic feeds **as a class** | A claim about how a **named** platform ranks |
| `[P*]` | first-party platform doc | What a platform **says, requires or defines**, quoted **with a retrieval date** | Evidence that anything **works** |
| `[P]` | practitioner | A labelled, attributed number | Being stated as measured fact |
| `[K]` | craft | Technique and worked examples | Any factual claim. Factcheck mode does not read this tier |

**The governing asymmetry of this corpus:** no confirmed source can tell you how a named
platform ranks. That is not a gap to be filled by a better search; the rankers are proprietary
and undocumented. Confirmed evidence covers the *class* of system. First-party documentation
covers what a platform *says*. Nothing covers both.

---

## Q1 — Algorithmic curation and feed ranking

**Ranked feeds reallocate exposure rather than reflecting the network, and this is audited.**
Crowdsourced audits of Twitter/X's recommender show it systematically shapes what a user sees
versus what their network posted `[C]` [s18][s38]. Algorithmic curation measurably changes media
exposure in timelines, including reducing link exposure `[C]` [s37]. Exposure-bias evaluation
methods `[C]` [s40], neutral-bot probes `[C]` [s43], political amplification auditing `[C]`
[s44], personalisation impact on exposure `[C]` [s42], and audit-methodology evaluation `[C]`
[s41] round this out. Reddit's r/popular has its own empirical audit, finding recent comment
activity extends how long a post stays in the trending feed `[C]` [s11][s16][s25].

**Engagement-optimised ranking is linked to amplification of divisive content** `[C]` [s45].

**The filter-bubble question is genuinely unresolved and must be preserved as such.** A
systematic review of 30 peer-reviewed studies (2015-2025) reports conflicting results: some find
personalisation narrows exposure, others find cross-cutting exposure persists `[C]` [s23]. A
landmark Facebook study found individual choice operated alongside ranking `[C]` [s39].

**Not in sources:** effect magnitudes. The audits establish direction and mechanism; the
accessible material does not publish hazard ratios or marginal effects. "The effect is
established, the magnitude is not published" is the correct answer.

---

## Q2 — Exposure allocation and organic reach

**Attention concentrates through cumulative advantage**, independent of platform intent.
Preferential attachment yields heavy-tailed distributions where few accounts hold most attention
`[C]` [s34], demonstrated empirically in large user-generated networks. **The same interaction
inequality persists across platforms** with different business models `[C]` [s56], which is the
finding that breaks the "the platform throttles you to sell ads" single-cause story. Creator
earnings show matching concentration `[C]` [s26][s30]. Platforms do control visibility
affordances and monetisation levers `[C]` [s24], so commercial pressure is real alongside the
structural effect.

**Virality is untied to audience size:** "the ability to create viral content and capture
widespread attention is untied to the size of the information provider" `[C]` [s55]. **Outcomes
are substantially luck-driven** under popularity-biased visibility allocation `[C]` [s53].
Cascade dynamics `[C]` [s57] and multimodal analysis of what travels `[C]` [s27] add mechanism.

**Creators cannot see their own audience.** Combining survey with large-scale log data shows
perceived audience is systematically mismatched against actual audience `[C]` [s52]. Client
intuitions about who sees their content are not evidence.

---

## Q3 — Engagement mechanics

**Engagement has no standardised measure.** A systematic review finds wide heterogeneity, no
dominant behavioural index, and studies that aggregate likes, comments and shares into a single
figure rather than analysing them separately `[C]` [s1]. Validated higher-order measurement
models exist `[C]` [s7][s66][s69] but do not resolve the field onto one formula.

**The largest evidence base here is a meta-analysis of customer engagement behaviour**: 196
effect sizes, 184 publications, n=146,380, resolving into an organic relationship-oriented
pathway alongside a second `[C]` [s72]. Further meta-analytic and empirical work `[C]`
[s65][s67][s70][s73][s74][s75].

**Liking and commenting have different drivers** `[C]` [s68]. This supports separate analysis
and does **not** support any weighting ratio.

**Engagement diverges from value:** "there is potentially a large gap between engagement signals
and a desired notion of value that is worth optimizing for" `[C]` [s71].

**A meta-analysis of brands' owned social media on engagement and sales exists and finds the
literature divergent** `[C]` [s3], it was conducted to explain why results differ, not to
establish a rate. **Never promise a client an engagement-to-sales conversion.**

**Not in sources:** any confirmed weighting of saves or sends against likes; reciprocity and
dyadic interaction effects, which the review flags as underexplored `[C]` [s1].

---

## Q4 — Audience growth dynamics

Follow behaviour has measurable longitudinal predictors `[C]` [s77]; ties form transitively
through existing connections `[C]` [s80]; online communities have documented emergence dynamics
`[C]` [s79] and size-and-time effects on formation `[C]` [s81]; user migration between platforms
is measurable `[C]` [s78]; audiences **duplicate across platforms** rather than being independent
`[C]` [s2]; follower types differ in engagement `[C]` [s31].

The **interest-graph over social-graph** framing is practitioner `[P]`, though directionally
consistent with confirmed audit findings `[C]` [s18][s37].

**Not in sources:** any confirmed posting-frequency-to-growth relationship with an effect size,
any follower threshold, any growth-rate benchmark.

---

## Q5 — Self-presentation and personal branding

**Real literature, almost entirely qualitative.** Microcelebrity and self-branding as social
practice `[C]` [s14][s17], a systematic review of personal branding as a field `[C]` [s19],
leaders' personal branding on professional platforms `[C]` [s22], solo entrepreneurs'
self-presentation `[C]` [s94], CEO communication style and parasocial interaction `[C]`
[s91][s93], impression management on enterprise platforms `[C]` [s92]. Perceived authenticity
recurs as the central cultivated mechanism `[C]` [s14][s4].

**Not in sources, and this is the honest headline:** effect sizes. These sources describe
practices, motivations and perceptions. **None establishes that personal branding produces a
business outcome at a given magnitude.** Anyone quoting a number for founder-led content is not
quoting this literature.

---

## Q6 — Influencer marketing and UGC

**The strongest actionable evidence in the corpus.** Two meta-analyses find significant positive
effects on attitudes, intentions and behaviours, with cross-study moderators `[C]` [s9][s6],
plus field-level reviews `[C]` [s12][s21] and micro-influencer synthesis `[C]` [s20].

**Mechanisms are source credibility and parasocial relationship** `[C]` [s9][s4][s21], not reach.
Influencers shape imitation intentions through social-influence pathways `[C]` [s13].

**Follower count is non-monotonic**: mid-tier outperforms the largest `[C]` [s5], and influencer
size operates as a moderator `[C]` [s9][s20].

**Disclosure has a measurable cost that a strong parasocial relationship attenuates:**
sponsorship disclosure lowers perceived credibility and brand attitude, reducing purchase
intention, mitigated by relationship strength `[C]` [s10][s15]. **This is an argument for
choosing better influencers, never for concealing a paid relationship.**

**Not in sources:** exact coefficients. The meta-analyses report effect sizes; the accessible
excerpts do not reproduce them. Do not invent numbers.

---

## Q7 — Folklore provenance

See `what-not-to-do.md`, which is the working output of this pass.

Headline: **timing has a real literature that the vendor tables misrepresent.** Choosing posting
time is a causal-inference problem distinct from prediction, properly estimated by randomised
test `[C]` [s117][s119], and the research recommends times **per user** because reaction
probability "differs for each user" `[C]` [s118][s120]. Scheduling is modelled seriously `[C]`
[s116]. Hashtags function for discovery and recommendation `[C]` [s32][s29]. Shadow banning is
formally modelled as an opinion-shaping mechanism `[C]` [s33], evidence it *can* be done, not
that platforms do it to marketing accounts. Provenance-tracing method `[P]` [s225].

**Not in sources:** any earliest traceable origin for the link-penalty claim, engagement-pod
effectiveness, or follower thresholds.

---

## Q8-Q13 and Q15-Q17 — Per-platform craft and documentation

Distilled into `platform-specs/`. Not restated here. The load-bearing dated findings:

- **YouTube redefines a "view" on 24 August 2026** to first-frame across all formats; the prior
  definition becomes "engaged view" `[P*]` [s198]. **Breaks every historical YouTube view
  benchmark.**
- **LinkedIn, 12 March 2026:** LLM-based generative recommenders; explicit action to "make
  engagement pods ineffective and curb comment automation"; reduction of "recycled and
  click-driven posts" `[P*]` [s284]. Dwell time is a documented ranking input `[P*]` [s288];
  the ranker was rebuilt on LLMs `[P*]` [s282]; creator-side optimisation runs alongside
  viewer relevance `[P*]` [s320][s318].
- **Instagram, April 2024, fully launched:** stated correction of ranking bias toward large
  accounts and aggregators, with a new input favouring smaller creators `[P*]` [s314][s315].
  Recommendation eligibility is a separate, checkable gate `[P*]` [s311].
- **Facebook, March 2026:** "rewarding creators who post original content… while deprioritizing
  unoriginal content" `[P*]` [s193]. Feed is a documented mix of connected and recommended
  content `[P*]` [s192].
- **TikTok:** For You is per-user and explicitly uses negative signals such as skips `[P*]`
  [s290][s310].

**The cross-platform synthesis worth stating on its own:** Instagram (2024), Facebook (March
2026) and LinkedIn (March 2026) independently announced rewarding originality and
deprioritising recycled or generic content `[P*]` [s314][s193][s284]. Three first-party
statements, one direction. A repurpose-everything strategy now runs against three rankers.

---

## Q14 — Listening and community management

**Craft tier only, and the pass was rebuilt.** The original query led with "social listening" and
returned the Social Security Administration, two dictionaries and a bar; ten of twelve sources
were junk, and those nine indices were purged. The rewritten pass around "brand mention
monitoring" and "community manager" returned a usable tool-and-workflow set `[K]`
[s329][s332][s333][s334][s335][s336][s337][s190][s128].

**Not in sources, all asked for and none returned usable:** cross-platform competitive
monitoring specifics, large-scale comment and DM triage mechanics, moderation and escalation
playbooks, public criticism response examples, employee advocacy programme design, and **how
share of voice is calculated and where it misleads.**

---

## Known gaps

1. **Effect magnitudes**, across most of the evidence half. Direction is well established.
2. **Personal branding performance.** Qualitative literature only.
3. **Reddit** (5 sources, zero first-party), **Threads** (1), **Bluesky** (0).
4. **X current ranking.** Strong audit literature, one useless first-party doc; internals are
   historical. Cross-cite `awesome-claude-skills/twitter-algorithm-optimizer`.
5. **TikTok 2026 changes and tactical thresholds.** Thinnest of the deep five.
6. **Share of voice methodology.** Asked for; not returned.
7. **Pinterest organic.** Six of eight first-party docs are ads and partnerships.

---

## Live Query Additions

*(Append live findings here with source, retrieval date, and a `[Ln]` tag. Do not fold them into
`[sN]` numbering, that would break `gather.py verify`. See `notebook-live-query.md`.)*

None yet.

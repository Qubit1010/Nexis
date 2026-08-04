# Strategic Foundation — Research Synthesis (2026)

The cited evidence base for this skill. Every load-bearing claim in the other reference
files resolves back to a section here, and every `[sN]` resolves to
`_research/sources.json` at `sources[N-1]` (title, url, tier, which passes retrieved it).

**Corpus:** 275 sources from 380 deduped, gathered through 17 deep passes of the in-repo
`research` skill (Exa + Tavily + Serper + Jina fused, content-extracted), junk-filtered,
per-domain capped. **79 confirmed-tier against 196 practitioner-tier.**

**Tiering.** `[confirmed]` means peer-reviewed research or primary statistical data.
`[practitioner]` means a consultancy, vendor, or operator making a case, usually for a
methodology they sell. Business strategy is a field where the practitioner layer is loud
and the empirical layer is quiet, and the whole value of this skill is refusing to
flatten the two. **When a claim is practitioner-tier, say so in the answer.**

**The most important thing about this corpus:** on several of the questions a client
will actually ask, the honest answer is that the evidence is weak, contested, or absent,
while the consulting industry answers them with total confidence. Those are flagged
below and collected in `what-not-to-do.md`. Do not resolve them in the client's favour
just because it makes a better deliverable.

---

## Q1 — Mission, vision and values

**Bottom line:** there is no established link between having a mission statement and
financial performance, after twenty-plus years of looking. Vision has better evidence
than mission, and both are far weaker than the consulting literature implies. Write them
because they make decisions easier to delegate, not because they raise revenue.

**What the evidence supports**
- A meta-analysis of twenty years of research concludes the effect of a mission statement
  on organizational performance **remains unclear** [s58] [confirmed]. This is the single
  most important finding in this section and it is the opposite of how the deliverable is
  usually sold.
- A review across objective and subjective effectiveness criteria finds mission-statement
  effectiveness **subject to substantial skepticism**, and distinguishes proximal effects
  (on employees) from distal ones (on financial outcomes), with the distal case weakest
  [s57] [confirmed].
- Organizational **vision** does show an empirical association with employee work
  performance, in a 2021 hospital study [s2] [confirmed]. Note the setting: one sector,
  employee-level outcome, not firm financials.
- Mission statements in practice tend to be **subjective, vague, broad, and inward-looking,
  and rarely give employees usable focus** [s59] [confirmed]. This is a finding, not a
  complaint about bad writing.
- Corporate purpose is routinely **confused with its operationalization** through mission
  statements, which is why purpose work so often produces nothing [s61] [confirmed].
- Mission statement *quality* and content, rather than mere presence, is where any
  financial relationship would have to live [s60] [confirmed].

**What is contested or unsupported**
- "A strong mission drives performance." Not established [s58] [s57].
- Practitioner sources converge on writing guidance (clear, concise, behaviourally
  grounded, aligned to strategy) [s81] [s85] [s118] [s121] [s125] [practitioner], but none
  of them present causal evidence, and the research reports say so explicitly.
- Values only matter when operationalized into hiring, recognition and day-to-day
  decisions. Consistent practitioner consensus [s85] [s118] [s121] [practitioner], not an
  empirical finding.

**Gaps:** no evidence here on small businesses specifically, and none on whether the
*process* of writing these statements has value independent of the artifact.

---

## Q2 — Market research and market sizing

**Bottom line:** the methodology is practitioner-standard and uncontroversial, but the
one thing the empirical literature is clear about is that founders' own numbers are
systematically too high. Size the market bottom-up, then discount the founder's input,
because the research says the bias is real and directional.

**What the evidence supports**
- Founders **overshoot realized revenues by 22% on average** when forecasting to their own
  VCs, a mixed-methods study with a replication on a second dataset [s64] [confirmed].
  This is the most concrete, most usable number in the entire corpus.
- Nascent entrepreneurs show **substantial overoptimism** in their expectations, tested
  against realized outcomes [s63] [s69] [confirmed].
- Entrepreneurs' own survival expectations **can barely distinguish survivors from exits**,
  across US and Finnish samples, and roughly a quarter will not give an estimate at all
  [s67] [confirmed].
- Investors in equity crowdfunding **cannot filter the optimistic bias** out of founder
  forecasts, though the forecasts do carry some signal on survival [s62] [confirmed].
- Overconfidence changes form across early startup stages rather than simply decreasing
  [s65] [confirmed].
- Expert judgmental forecasting of new product commercial success, tested on 559 ideas,
  is poorly calibrated [s66] [confirmed].

**Method (practitioner consensus, no empirical ranking between approaches)**
- TAM, SAM, SOM are nested scopes: total demand, the share you can serve, the share you can
  realistically win near term [s71] [s83] [s102] [practitioner].
- Top-down starts from a published total and narrows by explicit filters. Fast, and prone
  to overestimation when the filters are loose [s102] [s71] [practitioner].
- Bottom-up multiplies target accounts by realistic annual revenue per customer, which ties
  the number to actual pricing and go-to-market [s104] [practitioner].
- **Triangulate.** Build both independently, reconcile, then pressure-test the assumptions
  with real buyers. The figure that survives both is the defensible one [s94] [s74] [s79]
  [practitioner].
- Investors judge the clarity of who the customer is and how you reach them, not the size
  of the number [s74] [s79] [practitioner].

**Gaps:** this corpus has no sector benchmark tables and no named secondary-data sources.
The forecast-bias literature is about revenue and survival, not specifically about TAM
inflation, so applying the 22% figure to a market-size estimate is an extrapolation and
must be labelled as one.

---

## Q3 — Target customer

**Bottom line:** demographic and firmographic descriptions are the weakest basis for
segmentation and the most commonly delivered. Segment on behaviour and value, and check
that the segments are stable enough to act on.

**What the evidence supports**
- Demographic and geographic segmentation bases are criticized in the literature
  specifically for **failing to predict behaviour**, which is the only thing a segment is
  for [s10] [confirmed]. Extending segmentation across all four bases is the corrective.
- **Segment stability** over time is a precondition for a segmentation being managerially
  useful for targeting and positioning, and it has to be evaluated rather than assumed
  [s11] [confirmed].
- Segment-level customer profitability models are sufficient for most resource-allocation
  decisions; the common belief that you need individual-level models is a misperception
  [s12] [confirmed]. Practical: a client does not need per-customer LTV to act.
- Aggregation criteria for forming segments have been tested empirically, and
  profit-maximizing aggregation outperforms other groupings [s13] [confirmed].
- Dynamic, two-stage segmentation improves targeting by also deciding what differential
  offer each segment gets, not just who to target [s14] [confirmed].

**What is contested or unsupported**
- Buyer personas as a **segmentation** instrument have no support here. The evidence points
  at behavioural and value-based bases instead [s10]. **See Q9**, which was added later and
  resolves this: personas do have measured value as an *alignment* artifact [s255], just not
  as a way to choose or predict a segment. The fictional-character styling specifically is
  what the persona literature criticizes itself for [s257].
- Jobs-to-be-done appears in this corpus only through practitioner sources. Treat the
  framework as a useful interviewing discipline, not an evidenced predictor.

**Gaps:** no B2B-specific segmentation evidence, and nothing on how small a business can be
before formal segmentation stops paying for itself.

---

## Q4 — Competitive position and industry structure

**Bottom line:** industry structure matters, but firm-specific choices matter roughly
one and a half times more. Do not let a client conclude that a bad industry dooms them or
that a good one saves them.

**What the evidence supports**
- The variance decomposition: year effects **2%**, industry effects **19%**,
  corporate-parent effects **4%**, business-specific effects **32%** of the aggregate
  variance in profitability among US public corporations [s50] [confirmed]. This is the
  number to quote when a client asks whether their industry is the problem.
- Rumelt's original decomposition found industry and corporate effects **surprisingly
  small** relative to business-specific ones, which is what set off the whole replication
  literature [s52] [s54] [confirmed].
- A meta-analysis reconciling the competing estimates confirms industry, corporate and
  business effects together explain most performance differences, while the split between
  them depends heavily on which effect-size measure is used [s51] [confirmed]. Quote the
  19/32 split as indicative, not exact.
- Using value-based performance measures instead of accounting ratios changes the answer
  again [s53] [confirmed], and industry and firm effects are not independent of each other
  [s56] [confirmed].
- Five Forces is Porter's own framework for reading industry structure and its profit
  potential, and industry structure is explicitly **dynamic**, not a one-time snapshot
  [s1] [confirmed, primary source].
- The five forces do show an empirical relationship with competitive advantage and
  organizational performance, moderated by management accounting practice [s55] [confirmed].
- Structure-conduct-performance is the underlying economic paradigm: structure shapes
  conduct, conduct determines performance [s5] [confirmed].

**How to use this:** run Five Forces to understand the constraint, then spend the client's
attention on the 32%, which is what they control.

**Gaps:** the variance-decomposition literature is large-firm and public-company data. Its
transfer to a small private services business is an assumption, and should be stated as one.

---

## Q5 — Positioning and the unique value proposition

**Bottom line:** this is the most genuinely contested section in the corpus. Meta-analytic
evidence supports differentiation improving financial performance, and a serious empirical
tradition argues perceived brand differentiation matters far less than everyone assumes.
Present both. Do not sell "differentiate or die" as settled science.

**The case for differentiation**
- A **meta-analysis** finds differentiation strategy relates to financial and non-financial
  performance [s15] [confirmed].
- Differentiation leads to **more sustainable** financial performance than cost leadership,
  where sustainability is the persistence of performance over time [s16] [confirmed].
- The resource-based view has a meta-analytic integration of the strategic
  resources-to-actions-to-performance pathway, though it notes RBV is relatively silent on
  what managers should actually *do* with resources [s18] [confirmed].
- Empirical evidence from Chinese firms links differentiation strategy, built on
  uniqueness and customer loyalty, to firm growth [s6] [confirmed].
- Differentiation level moderates the satisfaction-to-loyalty path, so it changes how
  customers process value, not just whether they pay more [s22] [confirmed].

**The case against, which is not fringe**
- Romaniuk, Sharp and Ehrenberg **directly challenge the central importance of
  differentiation to brand strategy**, on empirical grounds [s20] [confirmed]. This is the
  Ehrenberg-Bass position and it is a real, cited body of work.
- Optimal-distinctiveness research reports **mixed findings** on the
  distinctiveness-to-performance relationship, which is why the field keeps investigating
  moderators [s19] [confirmed]. Distinctiveness operates at multiple levels at once, within
  and between organizations [s17] [confirmed].
- Game-theoretic analysis shows unique resources do **not** automatically convert into
  profit once competitors' responses are modelled [s21] [confirmed].

**How to hold both:** differentiation that shows up in the *offer and the economics* has
support. Differentiation that lives only in brand messaging is exactly what [s20]
challenges. Push clients toward the former.

**Gaps:** April Dunford's positioning framework and the value proposition canvas appear
only as practitioner material here. Use them as process, and do not attach evidence claims
to them.

---

## Q6 — Business model and revenue model

**Bottom line:** business model innovation has the strongest and most replicated
performance evidence in this corpus, but it is not linear, not universally good, and it
matters most early. Novelty for its own sake is not supported.

**What the evidence supports**
- A **meta-analysis of 147 primary studies across 27 countries** finds the positive
  business-model-innovation to firm-performance relationship **robust** across different
  conceptualizations and measures, while benefits vary by institutional context [s28]
  [confirmed]. This is the strongest single result in the corpus.
- The effect is **life-cycle dependent**: business model innovation contributes strongly to
  performance in earlier phases and matters less later, tested on 250 organizations [s3]
  [confirmed]. Directly relevant to early-stage clients.
- The breadth of business model reconfiguration has an **inverted U-shape** with
  performance. Some reconfiguration helps, too much hurts [s27] [confirmed].
- **Refining and upscaling an existing model pays off**, and a more dynamic environment does
  not automatically call for more innovation [s25] [confirmed]. Most clients should improve
  the model they have.
- Novel business model design is **not sufficient** for high performance. It depends on the
  configuration of value drivers, competitive strategy and environment [s31] [confirmed].
  This contradicts the common framing of novelty as inherently good.
- Decomposed by element, value creation, value proposition and value capture behave
  differently over time, from 2,300+ events across 35,000 press releases [s26] [confirmed].
- Evidence in manufacturing SMEs is real but the wider empirical literature is **scarce,
  dispersed and sometimes conflicting** [s4] [confirmed], and design themes matter
  alongside innovation itself [s23] [confirmed].
- Business model fit with internal and environmental contingencies drives performance, from
  309 Finnish firms [s30] [confirmed]. Market power also shapes whether firms innovate their
  model at all [s29] [confirmed]. Established firms follow distinguishable "drifting" versus
  "leaping" learning paths [s24] [confirmed].

**Gaps:** the revenue-model taxonomy itself (subscription vs transactional vs retainer vs
marketplace) and pricing-model selection are practitioner-only in this corpus. There are no
margin benchmarks by model here. Do not invent them.

---

## Q7 — Financial forecast

**Bottom line:** use primary survival data, not the folklore failure rate, and treat any
client-supplied projection as biased high by a known and measured amount.

**What the evidence supports**
- **Roughly 78 to 80% of new US business establishments survive their first year**, from BLS
  primary data across two decades [s8] [confirmed]. This is the number to anchor on.
- Founder revenue forecasts **overshoot realized revenue by about 22%** [s64] [confirmed],
  and founder optimism is substantial and measurable [s63] [s69] [s67] [confirmed]. Carry
  this straight into any forecast built on client-supplied numbers.
- **Short-term revenue volatility is a strong predictor of venture exit**, tracking the bank
  accounts of 6,578 new ventures over 10 years, even after controls [s32] [confirmed].
  Volatility, not just level, is a risk signal worth putting in a forecast.
- First-year financial statements have real but limited power to predict startup survival,
  since conventional bankruptcy ratios work poorly on young firms [s33] [confirmed].
- Causes of failure **differ by firm age and life-cycle stage**, from a dataset of bankrupt
  SMEs [s35] [confirmed]. A three-year-old firm and a three-month-old firm fail for
  different reasons, so diagnose accordingly.
- New venture sales behave close to a random walk while survival is driven by the stock of
  available resources, so predictability improves only partially with age [s37] [confirmed].
- Business mortality by age over 1977-2016 US Census establishment data [s38] [confirmed],
  and Cox proportional-hazard modelling of startup longevity showing factors interact rather
  than act independently [s39] [confirmed].
- Pandemic-era administrative data on the universe of US startups distinguishes employer from
  nonemployer startup dynamics [s34] [confirmed].

**What is contested or unsupported**
- **"90% of startups fail."** This corpus contains the claim [s7] [s36], but it traces to
  practitioner sources (Startup Genome and similar) rather than primary data, and it sits
  against BLS establishment survival of ~80% at one year [s8] [confirmed]. The two are
  measuring different things over different horizons. Never quote 90% as fact.
- CAC, LTV and the LTV-to-CAC ratio: **no benchmark values in this corpus.** The concepts are
  practitioner-standard, the numbers are not evidenced here. Do not state a target ratio as
  research-backed.
- Gross margin benchmarks by business model: not present. Same rule.

**Gaps:** no runway or burn-rate benchmarks, no funding-amount guidance, and nothing on
services-business economics specifically.

---

## Q8 — Diagnosing an existing strategy (review mode)

**Bottom line:** formal strategic planning has a positive, meta-analytically supported
relationship with performance, including in small firms. The famous "70 to 90% of
strategies fail at execution" statistic is not established and should not be repeated.

**What the evidence supports**
- **Formal strategic planning improves financial performance in small firms specifically**,
  by meta-analysis [s45] [confirmed]. This is the most directly applicable result in the
  corpus for Aleem's client base, and it is the justification for the deliverable existing.
- A meta-analysis finds strategic planning has positive consequences for organizational
  performance, against the criticism that it is overly rational and inhibits strategic
  thinking [s40] [confirmed].
- A meta-analysis across **183 independent study samples**, 84 examined for the first time,
  on the corporate-planning to performance relationship, correcting for measurement error
  [s43] [confirmed].
- An earlier meta-analytic review notes that after two decades results were genuinely mixed,
  with some studies finding no relationship or small negative effects, and attributes much of
  the confusion to small samples [s44] [confirmed]. Report the direction, not a precise effect
  size.
- Formal planning guidance that holds up: set objectives explicitly, generate strategies,
  evaluate them, monitor results, and obtain commitment [s46] [confirmed].
- Strategy **alignment** is the missing bridge between formulation and implementation, from a
  review of 36 articles spanning 1980 to 2023 [s47] [confirmed]. Implementation levers have
  been systematically reviewed [s42] [confirmed], as have the obstacles [s48] [confirmed].
- Key success factors differ between strategy *formulation* and *implementation* [s9]
  [confirmed]. A strategy can be well made and badly run, and the review must separate these.

**What is contested or unsupported**
- **"50 to 90% of strategic initiatives fail."** A dedicated review concludes these claims
  are **controversial** and that the literature does not support a specific figure [s41]
  [confirmed]. A second paper revisits the 30-year-old "less than 10% of organizations
  execute their strategy" claim and questions whether it was ever valid [s49] [confirmed].
  Do not use any of these numbers in a client deliverable.
- Rumelt's good-strategy/bad-strategy kernel (diagnosis, guiding policy, coherent action) is
  a practitioner framework. It is a genuinely useful review structure and `review-rubric.md`
  uses it, but it must be labelled as a framework, not an evidenced model. Note that
  Rumelt's *empirical* contribution to this corpus is the variance decomposition in Q4
  [s52] [s54], which is a separate body of work.

**Gaps:** no strategy-audit scorecard validated in the literature. The rubric in
`review-rubric.md` is assembled from these findings and is explicitly ours, not a
published instrument.

---

## Q9 — Buyer personas: what they are actually good for

**Bottom line:** personas have real empirical support, but for a narrower job than they are
sold for. They make a team faster at understanding and identifying users. They do **not**
predict who will buy. Build one to align content and writing, never to choose a market
segment. This resolves the apparent conflict with Q3.

**What the evidence supports**
- A **34-participant controlled experiment** comparing a persona system against an analytics
  system **on identical user data** found personas afford **faster task completion** for a
  user-identification task [s255] [confirmed]. The same paper notes there is a **lack of
  rigorous empirical research** evaluating personas against other methods, so this is a real
  but thin evidence base.
- The persona literature itself records that personas "have come under substantial criticism"
  for being **flat, assumption-based data structures** [s257] [s256] [confirmed]. The
  criticism is internal to the field, not an outside attack.
- **Data-driven construction is the corrective.** Personas built from real behavioural and
  social data, rather than from assumptions, are the direction the research moves in
  [s252] [s256] [s257] [confirmed].
- **Transparency about construction changes how personas are received.** Because data-driven
  persona creation is an opaque algorithmic process, users question the profile; adding
  explanations of how the information was derived measurably improves perception
  [s253] [confirmed]. Practical: show your sources inside the persona.
- Social data can build personas at a fraction of the cost of traditional market research
  [s252] [confirmed], and digital ethnography gives a six-step construction framework
  [s254] [confirmed].

**How this reconciles with Q3**
Q3 finds demographic and geographic bases fail to **predict behaviour** [s10] [confirmed].
That is a finding about **segmentation for targeting and resource allocation**. Q9 is about
a **communication and alignment artifact**. Both are true:

| Use a persona for | Do NOT use a persona for |
|---|---|
| Aligning writers and marketers on who they are addressing [s255] | Choosing which segment to serve |
| Capturing the audience's actual vocabulary and questions [s260] | Predicting purchase behaviour [s10] |
| Making an abstract segment concrete enough to write for | Sizing a market or allocating budget [s12] |

**Gaps:** no evidence that persona use improves content performance, conversion, or search
outcomes specifically. The [s255] result is task efficiency in a user-identification setting.
Do not claim a persona lifts traffic or revenue.

---

## Q10 — Audience language, questions and search intent

**Bottom line:** the gap between how a business describes its product and how a customer
describes their problem is a documented research problem, not a copywriting opinion. Closing
it is the single most defensible reason to build a persona for content and search.

**What the evidence supports**
- **The vocabulary gap is real and named.** Customers express needs "in layman's terms
  instead of the sufficient domain knowledge to identify the product specifications", which
  is why bridging customer language to specification language requires deliberate method
  [s260] [confirmed]. This is the empirical statement of the problem the persona's language
  section solves.
- **User-generated content is the established source for closing it.** Mining UGC bridges
  the semantic gap between customer needs and design specifications [s260] [confirmed], and
  NLP analysis of online customer reviews is a mature method for extracting what customers
  actually say [s251] [confirmed].
- **Query intent classification is a hard, active problem** even for well-resourced
  e-commerce search engines, with a substantial share of queries falling into "unknown"
  intent [s259] [confirmed] and requiring multi-granularity matching to resolve
  [s258] [confirmed]. Implication: do not assume you can infer intent from a keyword string
  alone. Get the phrasing from real sources.

**Practitioner method, from the brief Aleem supplied**
The source page ([aruntastic notes on knowing your audience](https://aruntastic.com/resources/library/seo/notes-know-your-audience-competitors/))
[practitioner] prescribes: define the audience before competitors, build a persona with
Demographics / Needs and Goals / Pain Points / Online Behavior / Motivations, and use AI
research against forums and Q&A sites to surface "the authentic language and common phrases
your audience uses to describe their problems". It then flows audience to competitors to
keyword research.

Adopt the **language-mining step and the ordering**, both of which the confirmed evidence
supports [s260] [s251]. Treat the **demographic block as scaffolding**, not as the
load-bearing part, per [s10].

**Handoff, do not restate:** the search mechanics live in `seo-advisor`'s corpus, which
covers keyword research and intent classification (its Q2), AI search and AEO/GEO (its Q9),
and entity SEO with query fan-out expanding one prompt into 5 to 11, and in its Q13 10 to 20,
sub-queries. Cross-cite that skill rather than duplicating its numbers here.

**Gaps:** nothing in this corpus measures whether matching audience vocabulary improves
rankings or AI citation rates. The vocabulary gap is established; the SEO payoff is inferred.
Say so.

---

## How to cite in an answer

- Lead with the finding or number, then the tier, then the implication.
- Always mark practitioner-tier claims as such when they are load-bearing.
- Where Q1, Q5, Q7 and Q8 flag a contested or unsupported claim, surface the conflict rather
  than picking the convenient side.
- If the corpus does not cover it, run the live fallback in `notebook-live-query.md`, present
  the cited answer, then append it below.

---

## Live Query Additions

*Findings added after the locked corpus, via the live fallback. Each entry records the
question, the date, and the sources. New sources must be appended to `sources.json` through
`gather.py extract` so their `[sN]` indices stay stable.*

(none yet)

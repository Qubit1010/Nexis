# What Not To Do — the kill list

Claims and habits this skill refuses. Run every deliverable through this before sending.
Most entries exist because the consulting default is confidently wrong, not because it is
merely unhelpful.

---

## Tier 1 — Numbers we refuse to repeat

| Claim | Why it dies | Say instead |
|---|---|---|
| "90% of startups fail" | Traces to practitioner sources, not primary data `[P]` [s7] [s36], and sits against BLS establishment survival of ~78-80% at one year `[C]` [s8]. The two measure different things over different horizons. | "About 78-80% of new US establishments survive year one `[C]` [s8]. Longer-horizon failure numbers vary by definition and source." |
| "70% (or 90%) of strategies fail at execution" | A dedicated review finds these claims **controversial and unsupported** `[C]` [s41]; a second questions whether the 30-year-old version was ever valid `[C]` [s49]. | "Implementation is where strategies commonly break down, but there is no credible figure for how often `[C]` [s41]." |
| "A strong mission statement drives performance" | Meta-analysis over 20+ years: effect on performance **still unclear** `[C]` [s58]; effectiveness subject to substantial skepticism `[C]` [s57]. | "Mission and values earn their place through decision clarity. The financial link is not established `[C]` [s58]." |
| Any LTV:CAC target ratio ("aim for 3:1") | **Not in this corpus at any tier.** The ratio is practitioner convention with no evidence base here. | "Track both, and here is how to compute them for your model. I do not have an evidenced target ratio." |
| Gross margin or CAC benchmarks by industry | Not in this corpus. Inventing one is the single easiest way to make this deliverable worthless. | "I do not have a sourced benchmark for your model. We can research it, or build the forecast from your actuals." |
| A market size with no stated assumptions | Investors judge clarity of customer and route to market, not the number `[P]` [s74]. Unfiltered top-down sizing is the classic error `[P]` [s102]. | Show the bottom-up build, every multiplier, and the sensitivity. |

---

## Tier 2 — Method failures

- **Never accept the client's own revenue projection at face value.** Founders overshoot
  realized revenue by ~22% on average `[C]` [s64], their survival expectations barely
  distinguish survivors from exits `[C]` [s67], and investors cannot filter the bias out
  `[C]` [s62]. Label client-supplied figures as client-reported and discount explicitly.
- **Never size a market top-down only.** Fast and prone to overestimation when filters are
  loose `[P]` [s102]. Build bottom-up, cross-check top-down, reconcile `[P]` [s94].
- **Never assume a market share percentage.** "We'll capture 1% of a $10B market" is the
  canonical bad SOM. Tie SOM to reachable accounts and validated pricing `[P]` [s74] [s79].
- **Never build a persona out of demographics.** Demographic and geographic bases are
  criticized specifically for failing to predict behaviour `[C]` [s10]. Segment on behaviour
  and value.
- **Never present a segmentation without checking it holds.** Stability is a precondition for
  managerial usefulness and must be evaluated `[C]` [s11].
- **Never tell a client their industry determines their fate.** Industry explains ~19% of
  profit variance against ~32% business-specific `[C]` [s50].
- **Never recommend reinventing a working business model by reflex.** Refining and upscaling
  an existing model pays off `[C]` [s25], reconfiguration breadth has an inverted U with
  performance `[C]` [s27], and novelty alone is not sufficient `[C]` [s31].
- **Never treat a values statement as finished at the wording.** Values matter only when
  operationalized into hiring, recognition and decisions `[P]` [s85] [s118] [s121].
- **Never invent a customer quote.** A verbatim quote with no source is the worst line in a
  persona, because it looks like the strongest evidence in it. If there is no data, mark the
  language section `[assumption]` and say the persona is a hypothesis.
- **Never use a persona to choose a segment or size a market.** It is an alignment artifact
  with measured benefit for user understanding `[C]` [s255], not a prediction instrument
  `[C]` [s10]. Segment choice comes from the foundation, not the persona.
- **Never claim a persona will lift traffic, rankings or conversion.** No evidence in this
  corpus supports it. The vocabulary gap is established `[C]` [s260]; the search payoff is
  inferred.
- **Never ship a persona without evidence markers.** Transparency about construction
  measurably changes how a persona is received `[C]` [s253], and an untagged persona hides
  which lines are known and which are guessed.
- **Never invent a customer quote.** A verbatim quote with no source is the worst line in a
  persona, because it looks like the strongest evidence in it. If there is no data, mark the
  language section `[assumption]` and say the persona is a hypothesis.
- **Never use a persona to choose a segment or size a market.** It is an alignment artifact
  with measured benefit for user understanding `[C]` [s255], not a prediction instrument
  `[C]` [s10]. Segment choice comes from the foundation, not the persona.
- **Never claim a persona will lift traffic, rankings or conversion.** No evidence in this
  corpus supports it. The vocabulary gap is established `[C]` [s260]; the search payoff is
  inferred.
- **Never ship a persona without evidence markers.** Transparency about construction
  measurably changes how a persona is received `[C]` [s253], and an untagged persona hides
  which lines are known and which are guessed.

---

## Tier 3 — Framework honesty

These are useful and we use them. They are **not** evidence, and must never be cited as if
they were.

| Framework | Status here |
|---|---|
| Rumelt's kernel (diagnosis / guiding policy / coherent action) | Practitioner. Good review structure, used by `review-rubric.md`. Rumelt's *empirical* contribution to this corpus is the variance decomposition `[C]` [s52] [s54], which is separate work. |
| Business Model Canvas | Practitioner. A layout for the conversation, not a predictor. |
| Jobs-to-be-done | Practitioner in this corpus. A good interviewing discipline. No evidenced predictive claim. |
| Buyer persona (the named-character-with-a-photo format) | Practitioner convention `[P]`. The *artifact* has a measured benefit for user understanding `[C]` [s255]; the fictional-character styling is what the research criticizes `[C]` [s257]. Use a short role label, not a backstory. |
| April Dunford positioning | Practitioner. Process only. |
| Value Proposition Canvas | Practitioner. Process only. |
| SWOT / PESTEL | Practitioner. Checklists, not analysis. Never deliver a SWOT as the competitive section. |
| Porter's Five Forces | The framework itself is primary-source `[C]` [s1] with supporting empirical work `[C]` [s55]. Its **limits** are also evidenced: industry is only part of the story `[C]` [s50]. |

---

## Tier 4 — Deliverable smells

Signals the document has drifted into consulting theatre.

- A mission statement that would fit any company in the industry if you swapped the name.
- A UVP that is a feature list, or that claims "quality, service and value".
- A competitor table where every row is a logo and no row is a *choice they made that we
  are choosing differently*.
- Financial projections with no stated assumptions, or a hockey stick with no mechanism.
- A "target customer" section that describes everyone who could conceivably buy.
- Recommendations that no competitor would disagree with. If the opposite is obviously
  stupid, it is not a strategy `[C]` [s41] framing.
- A market size chosen because it is impressive rather than because it is defensible.
- Any section that would read identically if the client's business were different.

---

## Tier 5 — Tone

- No em dashes in body text. No emojis.
- Do not launder a consultancy's marketing number into a fact by dropping the attribution.
- Do not resolve a genuinely contested question (Q5 differentiation especially) just because
  a clean answer makes a better-looking deliverable.
- If the corpus does not cover it, say so plainly. "I do not have a sourced number for that"
  is a better deliverable than a confident invention, and it is the whole reason this skill
  is worth more than a generic LLM answer.

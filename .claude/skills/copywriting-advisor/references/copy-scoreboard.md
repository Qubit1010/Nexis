# Copy scoreboard — what actually moves outcomes

Load this in advise mode. **Number first, then the tactic.** Ranked by strength of evidence,
not by how often the tactic gets recommended.

`[C]` confirmed, `[P]` practitioner. Evidence in `research-synthesis.md`.

---

## Tier 1 — Strong evidence, act on it

| Finding | Evidence | What to do |
|---|---|---|
| Simpler headlines outperform complex ones across **30,000+ field experiments** with the Washington Post and Upworthy; readers also attended more and processed more deeply | `[C]` [s76] | Cut vocabulary complexity before cutting anything else |
| Needless complexity **lowers** judged intelligence | `[C]` [s136] | The strongest reply to "make it sound more sophisticated" |
| Reviews move sales: valence **Es = .78**, volume **Es = .41**, elasticities larger on **third-party** sites and for high-involvement products | `[C]` [s114] | Get reviews onto third-party platforms, not just the site |
| Repeating the headline verbatim on the button raised clickthrough (field study, n = 956) | `[C]` [s2] | Cheapest untried CTA change in the corpus |
| Attention distribution: **57%** above the fold, **17%** second screenful, **26%** the rest | `[C]` [s259] | Load-bearing message high; keep writing below it |
| Plain-language redrafting measurably improves comprehension | `[C]` [s140] | Applies to terms, pricing, onboarding, anything a customer must understand to buy |
| Scarcity raises purchase intention on average | `[C]` [s13][s123] | Real, but read Tier 3 before using it |
| Suspected-fake reviews cause consumers to discount the reviewer **and** harm brand attitude | `[C]` [s115] | Overly polished testimonials cost more than they earn |

---

## Tier 2 — Real but conditional

| Finding | Condition | Evidence |
|---|---|---|
| Concreteness helps — up to a point, then reverses | Curvilinear; depends on the baseline concreteness of competing headlines | `[C]` [s74] |
| Negativity increases clicks | **News headlines.** Not established for considered B2B purchases | `[C]` [s71][s73] |
| Benefits over features | Depends on construal level and how near/concrete the purchase is | `[C]` [s41][s45][s10] |
| Mirroring customer language | Helps for perceived quality `[C]` [s35][s37]; **backfires** via identity threat when it reads as accommodation | `[C]` [s36] |
| Fluency increases liking, confidence and judged truth | Also makes false statements feel true; a persuasion tool with an ethics edge | `[C]` [s131][s8][s137] |
| Fewer words in paid search | Field experiment, 280,877 observations | `[C]` [s28] |
| Email subject-line personalisation (recipient's first name) lifts opens ~20% | Randomized field experiments across millions of emails, plus a published replication testing whether it still holds | `[C]` [s441][s426][s427] |
| Humour rescues high-fear appeals | Reduces the defensive response that suppresses persuasion | `[C]` [s57] |
| Information volume | Inverted U — too little fails as surely as too much | `[C]` [s88][s89] |

---

## Tier 3 — Where it backfires

The part usually left out of a pitch.

| Tactic | Failure mode | Evidence |
|---|---|---|
| Supply-driven limited quantities | Reduces perceived retailer sincerity and purchase intention; mitigated by availability guarantees and external attribution | `[C]` [s121] |
| Limited-time offers | Effect **reverses to negative** when consumer flexibility is restricted, via psychological reactance | `[C]` [s125] |
| Pressure nudges (quantity/time scarcity, social persuasion) | Affect **returns** as well as purchases; a purchase lift can be a return lift | `[C]` [s127] |
| Shortening return deadlines | Can **increase** return rates | `[C]` [s128] |
| Fear appeals | Genuinely contested — effective `[C]` [s4][s51] versus evidence arguing against `[C]` [s54][s52] | Both |
| Adopting the customer's language | Identity threat, lower satisfaction and repurchase | `[C]` [s36] |

---

## Tier 4 — Weaker than sold

| Lever | Reality |
|---|---|
| Gain vs loss framing | Goal/message framing lacks consistent evidence `[C]` [s11]; sun-protection meta k = 33 found no difference `[C]` [s111] |
| Message form generally | Across **1,149 studies of 30 variations**, form choice makes little practical difference to persuasiveness `[C]` [s107] |
| Button colour | No confirmed effect; a design experiment found none on trust `[C]` [s81] |
| Copy length as a rule | Controlled direct-mail test: no readability effect on response `[C]` [s24] |
| Source credibility in reviews | Limited effect on diagnosticity; **information quality** dominates `[C]` [s118] |

**The meta-lesson.** Copy levers are individually small. The large moves are the offer, the
proof, and whether the reader can tell what they are being asked to do. When a client wants a
copy pass to fix a conversion problem, check the offer first.

---

## Measurement reality

| Fact | Evidence |
|---|---|
| ~**30%** of tested ideas improve metrics in mature experimentation programs | `[P]` [s307] |
| Tests need users **in the thousands** minimum; large sites use far more | `[P]` [s302] |
| Minimum detectable effect governs feasibility | `[P]` [s305] |
| Optional stopping invalidates results; sequential methods exist for this reason | `[C]` [s271] |
| Twelve documented metric-interpretation pitfalls | `[C]` [s270] |

**Therefore:** most SMB clients cannot run a conclusive copy test. Recommend on the argument,
report directionally, promise no percentage.

---

## Writing for AI answer engines

| Finding | Evidence |
|---|---|
| Exposure is now **citation-based, not rank-based** — uncited sources get effectively no exposure regardless of retrieval rank | `[C]` [s65] |
| Structural features, not only semantic content, affect GEO outcomes | `[C]` [s61] |
| Citation **selection** and citation **absorption** are different measurements; count is breadth, not influence | `[C]` [s64] |
| Whether GEO is distinct from SEO is an open empirical question | `[C]` [s63] |
| Conversational-SEO methods do **not** transfer across application domains | `[P]` [s253] (NeurIPS; see synthesis tiering note) |
| AI-generated content degrades retrieval itself | `[C]` [s66] |
| Princeton GEO is the foundational paper — use for direction, **not** for the circulated per-method percentages | `[C]` [s62] vs `[P]` [s171] |

**Boundary:** `seo-onpage` owns on-page thresholds and `blog-writer` owns article structure.
Cross-reference them; do not restate their numbers here.

---

## Formatting a post: what generalises

Only three things generalise across platforms. Everything else is convention.

| Generalises | Evidence |
|---|---|
| Front-load the point. Attention is front-loaded, not absent - 57% of viewing time above the fold `[C]` [s259]. On a feed the equivalent is the pre-truncation line | `[C]` |
| Write simply. Simpler wording won across 30,000+ field experiments `[C]` [s76]; needless complexity lowers judged intelligence `[C]` [s136] | `[C]` |
| Match the promise to the destination. Ad-to-landing-page alignment is a primary failure point `[K]` [s385][s396] | `[K]` |

**Does not generalise, and has no confirmed source here:** hashtag counts, in-post link
suppression, emoji use, posting times, per-platform "ideal length". Call these conventions
when a client asks, not findings.

Per-platform and per-topic detail lives in
`copy-conversion/references/platform-formatting.md`. Character limits are verified against
platform docs at time of writing, never quoted from memory - Google's own responsive-search-ad
page does not state its counts, which is why the widely repeated 30/90 figures trace to
counter tools `[P]` [s419][s420] rather than to Google.

# Platform scoreboard

**Ranked by strength of evidence, not by how often the tactic gets recommended.** Number or
finding first, then what to do about it.

`[C]` confirmed · `[P]` practitioner · `[P*]` first-party platform doc, dated · `[K]` craft
(never usable for a factual claim). Indices resolve in `_research/sources.json` on the `index`
field.

---

## Tier 1 — Strong evidence, act on it

| Finding | Evidence | What to do |
|---|---|---|
| **Ranked feeds reallocate exposure; they do not reflect the network.** Independent crowdsourced audits show the recommender systematically shapes what a user sees versus what their network posted | `[C]` [s18][s38][s37] | Stop treating reach as a referendum on the post. Distribution is an allocation decision the account does not control |
| **Attention concentrates through cumulative advantage.** Preferential attachment produces heavy-tailed distributions where a few accounts capture most attention, with or without platform intent | `[C]` [s34][s2] | Never diagnose a small account's reach as a content-quality failure by default. Structural is the null hypothesis |
| **The same inequality persists across platforms** with different business models | `[C]` [s56] | Kills the "the platform is throttling us to sell ads" single-cause story. Ad pressure worsens it; it did not create it |
| **Creator earnings show the same rich-get-richer concentration** | `[C]` [s26][s30] | Set expectations on outcome distributions, not averages. The median result is not the mean result |
| **Virality is untied to audience size.** "The ability to create viral content and capture widespread attention is untied to the size of the information provider" | `[C]` [s55] | Directly refutes follower thresholds. Growth strategy and reach strategy are different problems |
| **Follower count relates to engagement non-monotonically.** Mid-tier accounts outperform the largest | `[C]` [s5] | For influencer selection, refuse follower-count sorting. Bigger is measurably not better past a point |
| **Outcomes are substantially luck-driven**, given visibility allocated by popularity bias | `[C]` [s53] | Judge process over single-post outcomes. One post proves nothing in either direction |
| **Engagement has no standardised measure.** A systematic review finds wide heterogeneity and no dominant behavioural index; studies routinely aggregate likes, comments and shares into one figure | `[C]` [s1] | Two "engagement rates" are rarely comparable. Define the formula before reporting one |
| **Engagement signals and value diverge.** "There is potentially a large gap between engagement signals and a desired notion of value that is worth optimizing for" | `[C]` [s71] | The strongest argument in the corpus against optimising engagement as the goal. Name the business outcome first |
| **Engagement behaviour meta-analysed across 196 effect sizes, 184 publications, n=146,380**, resolving into an organic relationship-oriented pathway and a second pathway | `[C]` [s72] | Treat engagement as relationship-driven, not trick-driven. This is the largest single evidence base here |
| **Owned social media effectiveness research is genuinely divergent**, which the meta-analysis exists to explain rather than resolve | `[C]` [s3] | **Never promise a client an engagement-to-sales conversion rate.** The literature does not agree one exists in general |
| **Creators cannot see their own audience.** Perceived audience is systematically mismatched against actual audience, measured by combining survey with large-scale log data | `[C]` [s52] | Clients' intuitions about "who sees this" are unreliable evidence. Insist on the native analytics |

---

## Tier 2 — Real but conditional

| Finding | Evidence | Condition |
|---|---|---|
| **Three major platforms moved to reward originality and deprioritise recycled content within roughly two years.** Instagram April 2024 (aggregators and large-account bias explicitly named), Facebook March 2026 ("deprioritizing unoriginal content"), LinkedIn March 2026 ("less generic content and engagement bait") | `[P*]` [s314][s193][s284] | Stated intent, not measured outcome. But three independent first-party statements in one direction is the strongest cross-platform signal in this corpus. **A repurpose-everything strategy is now working against three rankers at once** |
| **Instagram states it corrected a bias toward large accounts** and added a ranking input favouring smaller creators | `[P*]` [s314] | Instagram only. Do not transfer to LinkedIn, where cold-start remains hard |
| **LinkedIn documents dwell time as a ranking input** | `[P*]` [s288] | The mechanism is first-party. **The multiples are not.** Never quote "13x" |
| **LinkedIn is targeting engagement pods and comment automation** | `[P*]` [s284], Mar 2026 | Intent, not proof of success. Still enough to advise against pods on LinkedIn |
| **Comment recency extends visibility in Reddit's r/popular** | `[C]` [s11][s16][s25] | One feed on one platform. Do not generalise to "comments boost reach" everywhere |
| **Liking and commenting have different drivers** | `[C]` [s68] | Supports analysing them separately. Does **not** support any specific weighting ratio |
| **Engagement-optimised ranking is linked to amplification of divisive content** | `[C]` [s45] | Relevant to brand safety and to why "what performs" is not "what is good" |
| **YouTube publishes real first-party performance diagnostics** | `[P*]` [s196][s199][s201] | Genuinely more actionable than any other platform's docs. Use before theorising |
| **Snapchat ranks Spotlight, Discover and Lenses separately** | `[P*]` [s283][s325][s327] | Three surfaces, three answers. Ask which one |

---

## Tier 3 — Where it backfires or misleads

| Trap | Evidence | What to say instead |
|---|---|---|
| **Comparing views across platforms** | `[C]` [s1] on measurement heterogeneity; `[P*]` [s198] | The counting rules differ, so the ratio is not a number |
| **Comparing YouTube views across 24 August 2026** | `[P*]` [s198] | YouTube redefined a view to first-frame on that date; the old metric is now "engaged view". Every prior benchmark measures a different event |
| **Optimising engagement as the objective** | `[C]` [s71][s45] | Engagement and value diverge, and engagement-optimised ranking amplifies divisiveness. Name the business outcome |
| **Filter-bubble certainty in either direction** | `[C]` [s23] vs [s39][s43] | A systematic review of 30 studies reports conflicting results, and a landmark Facebook study found individual choice mattered alongside ranking. **Preserve the disagreement** |
| **Reading a platform's own explanation as proof a tactic works** | doctrine | `[P*]` establishes what a platform requires or defines, never that anything works |
| **Population statistics as performance claims** | doctrine | "X% of adults use TikTok" is media consumption, not evidence posting there works |
| **One account's data as a platform finding**, including Aleem's | doctrine | n=1, and the invisible-audience problem `[C]` [s52] makes self-reported reads unreliable |
| **Effect sizes this corpus does not contain** | the audits report direction, not magnitude `[C]` [s11][s18] | "The effect is established, the magnitude is not published" is a complete answer |

---

## The one-paragraph version

Distribution is allocated by a ranker, not earned from a network `[C]` [s18][s38]. Attention
concentrates structurally whatever anyone does `[C]` [s34][s56], virality is untied to audience
size `[C]` [s55], and a meaningful share of the outcome is luck `[C]` [s53]. Engagement is not
one thing, is measured inconsistently, and diverges from value `[C]` [s1][s71]. The one
actionable cross-platform trend with first-party backing is that **originality is being rewarded
and recycled content deprioritised on three major platforms at once** `[P*]`
[s314][s193][s284]. Almost everything else sold as a tactic is convention.

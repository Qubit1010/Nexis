# Authority, AI Search & Strategy - Section 32: How Links Actually Work

*Still one of the seven confirmed ranking factors, and no longer the strongest signal you can build.*

**Bottom line:** Backlinks remain a confirmed top-three ranking factor, and enforcement has
moved from punishing individual bad links to detecting whole citation networks. The finding
that changes strategy in 2026: unlinked brand mentions correlate roughly **three times more
strongly** with AI citation than backlinks do. Links get you into the candidate pool.
Mentions decide who gets quoted.

---

## What a link actually transmits

A backlink is one site vouching for another. Google's original insight, and the reason it beat
every directory-based competitor, was that this vote is hard to fake at scale because it costs
the linking site something: editorial credibility.

That cost is the entire mechanism. **The dividing line in 2026 is editorial intent.** Did a
real human editor decide, unprompted, that linking to you served their reader? Every quality
signal downstream is an attempt to measure that one thing. `[practitioner]`

Backlinks are one of the **seven confirmed ranking factors** from Section 3, alongside content
quality and E-E-A-T, HTTPS, page speed, mobile-friendliness, freshness and page experience.
That confirmation matters, because most of what gets sold as a ranking factor is not on this
list. `[confirmed]`

## What changed: SpamBrain 3.0

The important shift is in **how** manipulation is detected.

Older enforcement evaluated links one at a time. Current systems perform **graph clustering**
across whole networks, looking for the statistical footprints that manipulation leaves
behind: shared hosting, shared registration patterns, reciprocal linking rings, content
similarity across supposedly unrelated sites, and unnatural anchor text distributions.
`[practitioner]`

Two consequences follow, and both are strategically significant:

**You can be caught by association.** A link scheme you did not participate in but sit
adjacent to in the graph is now a risk that did not meaningfully exist a few years ago.

**The scale that made link schemes economical is exactly what makes them detectable.** Buying
five links is hard to detect and does almost nothing. Buying five hundred does something and
is trivially detectable. There is no volume at which the tactic is both effective and safe.

## Judging a single link

Domain Rating and Domain Authority are **third-party proxies, not Google metrics**. They are
useful for sorting a list and dangerous as a sole criterion. `[practitioner]`

Working thresholds from the corpus, in priority order:

| Criterion | Threshold | Why |
|---|---|---|
| **Topical relevance** | Linking domain's subject overlaps yours | The strongest single filter. Checked first |
| **Real organic traffic** | **1,000+ monthly organic visits** | A site with zero traffic passes approximately zero value regardless of its DR |
| **Domain Rating** | **DR 30+** baseline, **DR 50+** for high-impact placements | **91% of SEOs** now set a DR floor |
| **Toxicity** | Drop anything above **Semrush Toxic Score 45** | Regardless of how good the DR looks |

`[practitioner]`

**The rule that matters most: a DR 35 niche-relevant link beats a DR 70 unrelated one.** If
you take one thing from this section into your outreach, take that. It reorders most link
prospecting lists immediately. `[practitioner]`

The traffic check is the one people skip and the one that eliminates the most junk. Expired
domains rebuilt as link farms often carry inherited DR with no traffic at all. DR says 62,
organic traffic says 40 visits a month. That is not a real site.

## The headline finding: mentions versus links

This is the most consequential number in the section, and it is correlational, so hold it at
the right confidence.

**Branded web mentions correlate at r = 0.664 with AI Overview citation. Backlinks correlate
at r = 0.218.** Roughly a threefold difference in association strength.
`[practitioner, correlational]`

Supporting: brands present on **four or more third-party platforms are 2.8x more likely** to
be cited by ChatGPT. `[practitioner, single vendor]`

**What this does not mean.** It does not mean links are obsolete, and reading it that way is
the most common overcorrection. Link building still determines whether you enter the candidate
pool the AI synthesizes its answer from. You cannot be mentioned into a corpus you were never
crawled into.

**What it does mean.** An unlinked mention of your brand in a relevant publication, which the
entire link building industry has historically treated as a failure to be converted into a
link, is now independently valuable. Reclaiming it as a link is still worth doing. Treating
the mention itself as worthless is not.

Section 34 builds on this directly.

## Anchor text, briefly

Anchor text still carries relevance signal, and over-optimized anchor distributions are a
classic manipulation footprint. The practical guidance is short:

- **Natural profiles are mostly branded and URL anchors**, with exact-match keyword anchors as
  a minority.
- **You cannot control anchor text on genuinely earned links**, which is itself the point. A
  profile where 40% of anchors are your exact target keyword did not happen naturally, and the
  pattern is exactly what graph analysis looks for.
- Do not ask for specific anchor text in outreach. It converts worse and it looks like what it
  is.

## Do you still need links at all

Yes, with a proportionality caveat.

For competitive commercial queries, link authority is still a real gate and no amount of
on-page work substitutes for it. For long-tail informational queries, well-structured content
on a technically sound site ranks routinely with almost no links. Section 33 is honest about
the cost, which is the reason this ordering matters: links are expensive, and spending on them
before your content and technical foundations are sound is spending in the wrong order.

> **Why this matters:** the link industry has an unusually strong incentive to tell you links
> are everything, and the AI-search industry now has an equally strong incentive to tell you
> links are dead. The evidence supports neither. Links are a confirmed ranking factor whose
> relative weight is falling as brand mentions rise, and the correct response is to build both
> rather than to pick a side.

## Do this now

1. **Open your own link profile** in Ahrefs, Semrush, or the free Search Console Links report.
   Note total referring domains, not total backlinks. Domains are the meaningful unit.
2. **Pick your closest competitor** and pull their referring domains.
3. **Sort their list by DR and scan the top 30.** For each, ask: is this topically relevant to
   them, and does it look like an editorial link or a placement?
4. **Spot-check five of their links for real traffic.** Anything with high DR and negligible
   organic traffic is inherited authority, not a real endorsement.
5. **Find the links they have that you do not.** This is a link gap analysis and every major
   tool has a one-click version of it.
6. **Search your brand name in quotes** and note every mention that does not link to you.
   Section 34 turns this list into work.
7. **Check your own anchor text distribution.** If exact-match keyword anchors exceed roughly a
   fifth of your profile, note it as a risk.
8. **Write down your referring domain count and your competitor's.** That gap, in context, is
   your honest authority position.

## Capstone step

Your capstone site has a baselined link profile: total referring domains, a competitor
comparison, a link gap list of realistic targets, an anchor text distribution check, and a
list of existing unlinked brand mentions ready for Section 34.

## Key takeaways

- Backlinks are a confirmed ranking factor. Editorial intent is the thing every quality signal
  is trying to measure.
- Enforcement is now network-level graph analysis, so there is no volume at which link schemes
  are both effective and undetectable.
- Judge links by topical relevance first, then real organic traffic, then DR. A DR 35 relevant
  link beats a DR 70 unrelated one.
- Brand mentions correlate about 3x more strongly with AI citation than backlinks do, but links
  still get you into the candidate pool. Build both, do not pick a side.

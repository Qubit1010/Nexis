# Foundations - Section 3: How Google Decides

*Core updates, the 2024 leak, and a permanent method for telling a real SEO claim from a vendor's marketing.*

**Bottom line:** Section 2 named the ranking systems. This section covers the two things
that actually determine whether you can trust anything you read about them: how core updates
really work, and how to grade a claim by its evidence. The second skill outlasts every
tactic in this course.

---

## Core updates are not penalties

This is the most misunderstood event in SEO, and getting it wrong leads people to do exactly
the wrong thing.

A broad core update is a **reassessment**. Google improves how it judges usefulness, then
re-scores the web against the new judgement. Nothing was done *to* your site. Other pages
were judged more useful than yours for the same queries. `[confirmed]`

The practical consequences of that framing:

- **There is no reconsideration request.** That process exists for manual spam actions,
  which are a completely different thing. If you were hit by a core update, there is nobody
  to appeal to.
- **There is no "fix" that reverses it directly.** You cannot undo a core update. You can
  only become the more useful result before the next one.
- **Recovery usually lands on a later update**, not immediately after you make changes.

**Rollouts take days, not minutes.** The May 2026 core update rolled out over **12 days** of
visible volatility. Rankings swing wildly mid-rollout, in both directions. Diagnosing during
that window means diagnosing noise. The rule: do not draw conclusions until at least a week
after Google confirms the rollout is complete. `[confirmed]`

## Domain-level quality weighting, the thing that surprises people

When traffic drops after a core update, the instinct is to look at the pages that dropped.
Often the cause is somewhere else entirely.

Evidence points to **domain-level quality weighting**: thin or low-value content in one
section of a site can suppress genuinely good content elsewhere on the same domain. Your
best pages can lose rankings because of a neglected tag archive, an abandoned blog category,
or three hundred auto-generated location pages nobody has looked at since 2023.
`[practitioner]`

That is why the standard post-core-update playbook is subtractive first:

1. **Consolidate** pages that overlap and compete with each other.
2. **Remove or noindex** content that adds nothing. Deleting pages to improve rankings feels
   wrong and is frequently correct.
3. **Then add** what was missing: named authors, credentials, first-hand experience,
   original evidence.

Notice the order. Most people jump straight to step three, publish more, and make the
problem worse.

## E-E-A-T is not a score

Experience, Expertise, Authoritativeness, Trustworthiness. Google confirms this as a quality
concept, and it is the language its human quality raters use. It is **not** a metric in the
algorithm and there is no E-E-A-T number anywhere.

What it means operationally is that the systems try to approximate these things through
signals they can actually measure: who wrote this, is that person identifiable, do they
demonstrate having actually done the thing, is the claim supported, does the wider web treat
this source as credible.

The first E, **Experience**, was added most recently and is the one most sites fail. It asks
whether the author has first-hand experience of the subject. A page about migrating a site
to a new CMS written by somebody who has migrated sites reads differently from one
assembled out of three other articles, and increasingly Google can tell.

## The 2024 API leak

In 2024 a large volume of internal Google Search API documentation leaked publicly. It is
the best evidence we have about what Google actually measures, with two heavy caveats:
attribute names are not weights, and the presence of a field does not prove it is used in
ranking.

The single most useful thing it surfaced is an attribute called **`siteFocusScore`**,
which corroborates something practitioners had inferred for years: **how concentrated a
site is on one topic appears to be measured directly**. That is the strongest available
support for the pillar-and-cluster model you will build in Section 15. `[practitioner]`

## How to grade an SEO claim

Here is the method. Use it on everything, including this course.

**Tier 1 - Documentation.** Google Search Central, web.dev, Bing's docs, Schema.org. This is
what the engine says about itself. It can be incomplete or deliberately vague, but it is not
made up. Example: the Core Web Vitals thresholds in Section 27.

**Tier 2 - Peer-reviewed research.** Rare in SEO, and valuable precisely because it is rare.
It has a stated method you can attack. Example: the Princeton GEO study in Section 37, which
measured that adding expert quotes raised AI citation probability by 41%.

**Tier 3 - Independent large-scale study with a causal design.** Somebody changed one thing
across many pages and measured the result. Example: Ahrefs testing schema markup across 1,885
pages and finding no meaningful uplift in AI citations.

**Tier 4 - Correlation study.** Somebody measured that top-ranking pages tend to have some
property. This is the most common form of SEO "evidence" and the most abused, because
correlation is almost always reported in language that implies causation.

**Tier 5 - Vendor claim about the vendor's own product or method.** Treat as marketing until
independently replicated.

**Tier 6 - Assertion.** Somebody said it confidently in a blog post with no data at all. An
enormous amount of published SEO advice lives here.

### Four questions that sort almost anything

1. **Who measured it, and do they sell the thing being measured?**
2. **Is this correlation or causation?** If nobody changed anything and measured the
   difference, it is correlation.
3. **What is the sample?** "We analyzed 20,000 URLs" and "in our experience" are not the
   same claim.
4. **Does the number have a mechanism?** If you cannot explain *why* it would be true, be
   more suspicious of the number, not less.

### Worked example

You will read that pages with schema markup are cited far more often by AI engines. Several
vendors report numbers around a 3x lift.

Run the method. Who measured it: companies selling schema tools and AI-visibility products,
Tier 5. Correlation or causation: correlation, they observed which cited pages happened to
have schema. Sample: varies, often unstated. Mechanism: plausible, structured data could
help retrieval.

Now the counter-evidence. Ahrefs ran a causal study across 1,885 pages, adding schema and
measuring the change. No meaningful uplift. SearchAtlas found no correlation at all. And
Google's John Mueller has stated directly that structured data is not a ranking factor.

Conclusion: schema is worth implementing for rich-result eligibility and entity clarity, and
it is not a lever for AI citation on its own. That is a genuinely different action than the
vendor claim implies, and you reached it in about ninety seconds.

> **Why this matters:** SEO has more confident wrong answers in circulation than almost any
> technical field, because most of its literature is written by people with something to
> sell. The grading method above is the difference between an SEO who accumulates folklore
> and one who compounds real understanding. It is also the single most useful thing you can
> demonstrate to a client, because it is exactly what their last agency did not do.

## Do this now

1. **Read Google's ranking systems guide** at `developers.google.com/search/docs/appearance/ranking-systems-guide`.
   It is short. Read the whole thing.
2. **Write down three "ranking factors" you believed that are not in it.** Everyone has some.
   Being specific about what you got wrong is how this sticks.
3. **Read Google's core updates page** at `developers.google.com/search/docs/appearance/core-updates`,
   specifically the "what to do if you're affected" section. Note that the advice is about
   content quality and contains no technical checklist. That absence is informative.
4. **Find the date of the most recent core update.** Search Engine Land and Google's Search
   Status Dashboard both track them.
5. **Overlay that date on your capstone site's Search Console performance graph.** Set the
   range to 6 months and look for a step change at the rollout window. Note whether you see
   one.
6. **Grade one SEO claim.** Find any statistic in an SEO blog post, run the four questions,
   and write down which tier it lands in. Do this once deliberately and you will start doing
   it automatically.

## Capstone step

You now know whether your capstone site was affected by the last core update, and you have a
short written list of beliefs you have corrected. Keep that list. Add to it as the course
goes on. It is the most honest measure of learning you will have.

## Key takeaways

- Core updates are reassessments, not penalties. There is no appeal, no direct undo, and
  recovery usually lands on a later update. Do not diagnose until a week after the rollout
  completes.
- Traffic drops are often caused by thin content elsewhere on the domain, not by the pages
  that dropped. The playbook is consolidate, remove, then add.
- E-E-A-T is a quality concept approximated through measurable signals, not a score.
  Experience is the one most sites fail.
- Grade every claim by its evidence tier and ask who measured it, whether it is causal, what
  the sample was, and whether there is a mechanism. This skill outlasts every tactic here.

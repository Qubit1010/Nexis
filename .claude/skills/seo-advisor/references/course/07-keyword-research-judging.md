# Foundations - Section 7: Keyword Research Part 2, Judging

*Two tools can report volumes 30x apart for the same word. Learn what the numbers are made of, then learn to read the SERP instead.*

**Bottom line:** Search volume and keyword difficulty are estimates built on proxies, not
measurements. They are useful for sorting a big list quickly and unreliable for any single
decision. The durable skill is reading difficulty off the live SERP, which is free, more
accurate, and takes about ninety seconds per query.

---

## Where the numbers come from

**Search volume** is mostly extrapolation. Tools blend Google Keyword Planner's bucketed
ranges with clickstream data bought from browser extensions and panels, then model the rest.
Keyword Planner itself reports wide ranges rather than exact figures, and it is built for
advertisers, so it groups near-identical terms together.

The result is exactly what you would expect from modelling: the same keyword can come back
with volumes **30x apart** between platforms such as Moz and Semrush. `[practitioner]`

**Keyword difficulty** is a vendor invention. There is no such metric at Google. Each tool
computes a 0-100 score, mostly from the link profiles of the pages currently ranking. That
means difficulty scores measure **link strength of incumbents** and largely ignore content
quality, intent match, freshness, and whether the ranking pages actually answer the question.

Neither number is fake. Both are directional. Treat them as a way to sort 200 rows into
rough bands, never as the reason to commit to or abandon a specific target.

## What volume genuinely tells you, and what it hides

Volume is useful for relative comparison inside one tool. It is unreliable across tools and
across time.

Three ways it misleads:

**It hides seasonality.** A monthly average of 400 might be 4,000 in November and zero in
June. Check the trend graph, never just the number.

**It hides the click economy.** You already know from Section 5 that a high-volume query with
an AI Overview and a featured snippet may have almost no clicks in it. Volume measures
searches, not available traffic. A 200-volume query with no AI Overview can beat a
2,000-volume query that is fully answered above the fold.

**It reports zero for things that matter.** Long conversational phrasings, brand-new terms,
and AI fan-out sub-queries all show zero. That includes roughly **15% of daily searches that
are entirely new**. A zero-volume row is not evidence of no demand, it is evidence of no
measurement. `[practitioner]`

For a new or small site, the practical target band is **KD under 20 with volume roughly 100
to 1,000**. High enough to matter, low enough to be winnable. `[practitioner]`

## Difficulty is relative to you

This is the part tools cannot express well. A KD of 40 is comfortable for an established
domain with a strong link profile and impossible for a three-month-old site. The same number
means different things to different sites, and no tool knows which one you are.

So the tool's difficulty score answers "how hard is this in general". The question you
actually need answered is "how hard is this **for me**". Only the SERP can tell you that.

## The manual difficulty read

This is the skill worth having. Search the query and read the results as a competitor.

**1. Who is ranking?** All large recognizable brands means hard. A mix of brands and
independent sites means winnable. Small niche sites ranking means genuinely open.

**2. Is anything weak on page one?** Look for off-intent results, thin pages, content dated
three years ago, or a forum thread ranking. **UGC ranking on page one is the strongest
opportunity signal there is.** If a Reddit thread is in the top five, Google could not find
a good page, and a good page would win.

**3. Do the ranking pages actually answer the query?** Sometimes everything ranking is
mediocre and Google is choosing the least bad option. That is an opening.

**4. How much domain diversity is there?** Ten different domains is an open SERP. Three
domains taking eight slots means Google has decided who the authorities are.

**5. How fresh is the top content?** Everything from this quarter means a freshness system is
active and you will need to maintain the page. Everything from 2022 means nobody is
maintaining anything.

**6. What would it take to be clearly better?** Not marginally better. Clearly. If you cannot
articulate what your page would do that page one does not, you do not yet have a reason to
rank.

Run that on ten queries and you will trust it more than any score. Run it on a hundred and
you will not need the scores at all.

## Prioritization: relevance beats everything

The trap at this stage is optimizing for winnability and ending up with a list of easy,
irrelevant terms that never produce a customer.

A formula in circulation, useful as a way of thinking rather than as arithmetic:

> **Priority = (Business Relevance x Conversion Intent) / Competitive Feasibility**
> `[practitioner]`

The load-bearing term is business relevance. A rankable keyword that attracts people who will
never buy is a cost, not an asset. High-intent, mid-to-low-volume terms are reported to
convert **5 to 10x** better than broad informational ones. `[practitioner]`

Practical scoring for your sheet, 1 to 5 on each:

| Column | Question |
|---|---|
| **Relevance** | If this ranked first tomorrow, would it produce enquiries? |
| **Intent value** | Where in the six intents does it sit? Commercial investigation and transactional score highest |
| **Click availability** | From Section 5. Does this SERP have clicks in it? |
| **Winnability** | Your manual SERP read, not the tool score |

Sort by the first two. Use the last two as tiebreakers. Do not sort by volume.

## What to do with the disagreement

When two tools disagree by 30x, you do not need to resolve it. You need to stop depending on
it.

- Use one tool consistently so at least your relative comparisons are internally coherent.
- Cross-check anything you are about to build a serious piece of content for.
- Trust Search Console impressions over any tool's volume for queries you already rank for,
  because that is measured rather than modelled.
- For anything commercially important, run the manual SERP read and let it override.

> **Why this matters:** the most common failure in keyword research is treating a modelled
> estimate as a fact and building a content plan on it. The second most common is picking
> easy keywords nobody valuable is searching. Both are avoided by judging relevance first and
> reading the SERP for difficulty rather than trusting a number that a competing tool would
> report thirty times differently.

## Do this now

1. **Pick 10 queries** from your Section 6 sheet, spread across easy-looking and
   hard-looking.
2. **Before opening any tool, predict difficulty for each** on a 1 to 5 scale using the
   manual read. Write the prediction down first. This is the point of the exercise.
3. **Now check two tools** for volume and difficulty. Free tiers are fine, Keyword Planner
   plus one other works.
4. **Record all three numbers side by side.** Your prediction, tool A, tool B.
5. **Note the largest volume disagreement you find.** Seeing the spread yourself is what
   makes the caution stick.
6. **Score your full sheet** on Relevance and Intent value, 1 to 5 each. Do this fast, by
   instinct. You know your business.
7. **Sort by Relevance x Intent value** and look at the top 30. That is your real shortlist,
   and it will look different from a volume-sorted list.
8. **Run the manual difficulty read on the top 10** of that shortlist and mark any where a
   forum or an obviously weak page is ranking. Those are your first targets.

## Capstone step

Your raw list is now scored and sorted by business value rather than by search volume, with
a manual difficulty read on the top candidates and at least a few identified weak SERPs.
Section 8 turns this into clusters and a keyword map with one page per intent.

## Key takeaways

- Volume is modelled from clickstream and bucketed advertiser data, and can differ **30x**
  between tools. Difficulty is a vendor metric built mainly from incumbent link profiles and
  does not exist at Google.
- Difficulty is relative to your domain, which no tool knows. Read the SERP: who ranks, is
  anything weak, is there domain diversity, and could you be clearly better.
- A forum or UGC result on page one is the strongest opportunity signal available.
- Sort by business relevance and intent value, never by volume. Easy irrelevant keywords are
  a cost, and zero-volume does not mean zero demand.

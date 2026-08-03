# Foundations - Section 10: Setting Up Measurement

*Two free tools, four settings that most people get wrong, and a baseline you cannot create retroactively.*

**Bottom line:** Search Console and GA4 are free and non-negotiable. Both ship with defaults
that will cost you later, and one of them, GA4's two-month data retention, destroys history
you can never recover. Fix the defaults, record a baseline today, and Tier 1 is done.

---

## The measurement triangle

Three sources answer three different questions, and no single one is sufficient.

| Source | Answers | Limitation |
|---|---|---|
| **Search Console** | What happens in Google search: queries, impressions, clicks, position, indexing | Google only. Anonymizes low-volume queries. **16-month cap** |
| **GA4** | What happens after the click: pages, engagement, conversions | Misattributes a lot of organic. Sampling and consent gaps |
| **CRM / business data** | Whether it produced money | Attribution is imperfect and always will be |

The goal is **decision-grade data, not precision.** Privacy changes, consent banners and
AI referrers have permanently broken exact attribution. Anyone promising perfect measurement
is selling something.

## Search Console setup

**1. Verify a Domain property, not a URL-prefix property.** A Domain property covers every
subdomain and both protocols in one place. URL-prefix properties silently miss traffic on
variants you forgot about. Verification is a DNS TXT record.

**2. Submit your XML sitemap.** Usually `/sitemap.xml` or `/sitemap_index.xml`. Section 22
covers what belongs in it. For now, submit and confirm it is read.

**3. Learn four reports and ignore the rest for now.**

- **Performance.** Queries, pages, impressions, clicks, CTR, position. Where you will spend
  most of your time.
- **Pages** (indexing). Which URLs are indexed and why the rest are not. You read this in
  Section 2.
- **Core Web Vitals.** Field data, mobile is what matters. Tier 3.
- **Generative AI Performance.** Launched mid-2026, reports performance inside AI Mode and AI
  Overviews. New, and the only first-party window into AI surfaces you get.

**4. Use the 28-day rolling view** for routine checks. Daily numbers are noise, and the
28-day average smooths it. `[practitioner]`

**5. Know the 16-month cap.** Search Console keeps 16 months and then it is gone. If you care
about longer history, export monthly to a sheet or connect it to Looker Studio. Nobody does
this until they need data from 18 months ago and discover it does not exist.

## GA4 setup, and the settings that matter

**1. Extend data retention to 14 months.** Admin, Data Settings, Data Retention. **The
default is 2 months.** Two months makes year-over-year comparison impossible, and the setting
is not retroactive. Changing it today does not recover what was already discarded. If you do
one thing from this section, do this one. `[confirmed]`

**2. Link Search Console to GA4.** Admin, Product Links, Search Console Links. This brings
query-level data into GA4 and lets you connect a query to what happened after the click.

**3. Understand the misattribution problem.** GA4's default channel grouping misclassifies
roughly **30 to 50% of search traffic** as Direct or Unassigned. Your organic traffic is
almost certainly higher than GA4 reports. `[practitioner]`

The practical detection trick: look at Direct traffic landing on **deep pages, four or more
URL segments**. Nobody types a URL that long. That traffic is almost always misclassified
organic. `[practitioner]`

**4. Set up an AI referral channel group.** As of July 2026 GA4 has a native AI Assistant
channel covering ChatGPT, Gemini and Claude, but **it excludes AI Overviews**, which still
report as Organic Search. For a custom group, this regex covers the main sources:

```
.*(chatgpt.com|openai.com|perplexity.ai|claude.ai|gemini.google.com|copilot.microsoft.com|you.com|grok.x.ai).*
```

Be aware GA4 undercounts AI referrals by **8 to 31%** against server logs, because AI
platforms often use `rel="noreferrer"` which strips the referrer entirely. Server log
analysis is the only ground truth, and that is Section 41. `[practitioner]`

**5. Define conversions.** At minimum: form submissions, calls, and whatever counts as a
lead. Traffic without conversion data cannot be prioritized, because you cannot tell which
pages produce anything.

## Record the baseline

This is the part people skip and later regret. Today, before Tier 2 changes anything, write
down:

| Metric | Source |
|---|---|
| Total clicks and impressions, last 28 days | Search Console Performance |
| Average position and CTR | Search Console Performance |
| Number of indexed pages | Search Console Pages |
| Count in "Crawled - not indexed" and "Discovered - not indexed" | Search Console Pages |
| Core Web Vitals status, mobile | Search Console CWV |
| Organic sessions and conversions, last 28 days | GA4 |
| Position for each of your top 10 target queries | Search Console, filter by query |
| AI mention baseline for your 10 queries | Your Section 1 and Section 5 notes |

Date it. Everything you do from here is measured against this row, and you cannot create it
retroactively.

## What good looks like

Rough orientation rather than targets, since these vary enormously by site and market:

- **Indexed-to-submitted ratio above 85%** is healthy. `[practitioner]`
- **Impressions rising while clicks stay flat** means visibility without relevance, usually
  ranking for the wrong things.
- **A mature SEO program returns 3 to 5x its cost.** Median reported SEO ROI across
  industries is **748%**, which is a practitioner figure with wide variance behind it.
  `[practitioner]`
- **Organic CPA should run 40 to 70% of paid search CPA.** If it is not cheaper than ads,
  something is wrong. `[practitioner]`

## The one report to run weekly

Search Console, Performance, last 28 days, sorted by impressions, filtered to positions 5 to
15.

That view is where the cheapest wins live. Those pages already rank and already earn
impressions. From Section 5: moving position 8 to position 4 is roughly **400% more clicks**
from content you already have. Every week, pick one row and improve it.

> **Why this matters:** the two-month GA4 retention default has quietly destroyed more
> useful history than any algorithm update. And an undated, unrecorded baseline means that in
> six months you will not be able to prove anything worked, which matters for your own
> learning and matters more when a client asks.

## Do this now

1. **Verify a Domain property in Search Console** if you have not already.
2. **Submit your sitemap** and confirm it is read.
3. **Open GA4, Admin, Data Settings, Data Retention, and set it to 14 months.** Do this
   first, it is the only irreversible one.
4. **Link Search Console to GA4** in Admin, Product Links.
5. **Create the AI referral channel group** using the regex above.
6. **Confirm at least one conversion is defined** and firing.
7. **Check Direct traffic landing on deep pages** and note roughly how much misclassified
   organic you appear to have.
8. **Fill in the baseline table** and date it. Save it somewhere you will find in six months.
9. **Run the positions 5 to 15 report** and note the top three opportunities.

## Capstone step

Tier 1 is complete. Your capstone site now has: a baseline audit, verified measurement,
a keyword map with one page per intent, cannibalization identified, one page properly
optimized, and a dated baseline of every number that matters. Tier 2 works through the
content layer against that map.

## Key takeaways

- GA4 defaults to **2 months** of data retention. Set it to 14 immediately, because the
  setting is not retroactive and year-over-year comparison is impossible without it.
- GA4 misclassifies 30 to 50% of search traffic as Direct or Unassigned. Direct traffic on
  deep URLs is the tell.
- Search Console keeps 16 months and then deletes. Export if you want longer history.
- Record a dated baseline before changing anything. It is the only way to prove later that
  any of this worked.

# Technical SEO - Section 27: Core Web Vitals

*Three numbers, measured on real users, that act as a floor rather than a lever.*

**Bottom line:** LCP under 2.5 seconds, INP under 200 milliseconds, CLS under 0.1, all measured
at the 75th percentile of real Chrome visits over a rolling 28-day window. They are a
tiebreaker between comparable pages, not a lever that rescues weak content. A page can score
100 in Lighthouse and still fail.

---

## The three metrics

| Metric | Measures | Good | Needs improvement | Poor |
|---|---|---|---|---|
| **LCP** Largest Contentful Paint | Loading | **<= 2.5s** | 2.5 to 4.0s | > 4.0s |
| **INP** Interaction to Next Paint | Responsiveness | **<= 200ms** | 200 to 500ms | > 500ms |
| **CLS** Cumulative Layout Shift | Visual stability | **<= 0.1** | 0.1 to 0.25 | > 0.25 |

`[confirmed]`

**Assessed at the 75th percentile of real visits over 28 days**, and **all three must pass
simultaneously** for the URL to pass. `[confirmed]`

That p75 detail matters more than people realize. You are not being measured on your average
user. You are being measured on your slower quarter, which means mid-range Android phones on
mobile networks, not your laptop on office wifi.

**INP replaced FID in March 2024.** FID only measured the delay before the first interaction
was processed. INP measures the worst interaction latency across the entire visit, which is a
far harder test and the reason many sites that comfortably passed FID now fail. `[confirmed]`

## Field data versus lab data

The distinction that wastes the most time when people miss it.

**Field data (CrUX).** Real Chrome users, real devices, real networks, aggregated over 28 days.
**This is what Google uses for ranking.** It appears in Search Console's Core Web Vitals report
and in the top section of PageSpeed Insights.

**Lab data (Lighthouse, WebPageTest).** A simulated load in a controlled environment.
Reproducible, which makes it excellent for debugging, and unrepresentative, which makes it
useless as a verdict.

**The trap:** a page can score **100 in Lighthouse and fail the field assessment**, because
real users are on slower devices and worse connections than the simulation assumes.
`[practitioner]`

Always judge on field data. Use lab data to iterate between measurements.

**A consequence people forget:** because CrUX is a 28-day rolling window, a fix takes weeks to
show up. Deploying an improvement and checking the next morning tells you nothing.

## How much do they actually matter

Honestly: less than the amount of content written about them implies.

Sources broadly agree Core Web Vitals act as a **tiebreaker** rather than a primary lever. They
will not lift thin content above an authoritative page. They can decide between two comparable
ones. `[practitioner]`

The supporting evidence, all vendor or case-study tier:

- **Screaming Frog**, 20,000 URLs: position 1 results are **10% more likely to pass** CWV than
  position 9. Correlational, and consistent with better-resourced sites being both faster and
  more authoritative.
- **Rakuten**: **33% more conversions, 53% more revenue** per visitor after optimizing.
- **Vodafone**: a 31% LCP improvement produced **15% more sales**.
- **Deloitte and Google**: each 100ms of mobile speed improvement lifted retail conversion
  **8.4%**.

Notice that the last three measure **conversion, not ranking**. They are strong arguments for
speed as a business investment and weak arguments for speed as a ranking tactic. Being precise
about that difference is what separates an honest recommendation from a vendor pitch.

One ranking-adjacent data point worth having: sites with **INP above 500ms saw 2 to 4 position
drops** in the March 2026 core update. `[practitioner]`

## The floor, restated

From Section 3, and worth repeating here because this is where people waste the most effort:

**Core Web Vitals are a floor, not a lever.** Failing suppresses you. Passing buys you nothing
further. Going from 2.4 seconds to 1.1 seconds is real engineering work with no ranking return.

Get to "good", then go and do content or links. Telling a client already passing to optimize
further is telling them to spend money for nothing.

The exception is conversion. The case studies above are about revenue, and speed improvements
below the threshold can still pay commercially. Just be clear which argument you are making.

## Where to measure

**Search Console, Core Web Vitals report.** Field data, grouped by URL pattern. **Use the
mobile report**, since mobile is what drives ranking. Your first stop.

**PageSpeed Insights.** Both field and lab for a single URL. The field section is "Discover what
your real users are experiencing".

**Chrome DevTools, Lighthouse and the Performance panel.** For debugging specific causes.

**The CrUX dashboard** for longer historical trends.

## Reading the report properly

Search Console groups URLs by similar behaviour, so a failure usually indicates a **template**
problem rather than a page problem. Fixing one blog post fixes nothing. Fixing the blog template
fixes hundreds of URLs at once.

That grouping is the most useful feature of the report and the most commonly missed.

> **Why this matters:** more effort is wasted on Core Web Vitals than on almost anything else in
> SEO, in both directions. Sites failing badly ignore it because it feels like a developer
> problem. Sites already passing keep optimizing because the number can always go up. Knowing it
> is a floor tells you which situation you are in.

## Do this now

1. **Open Search Console, Core Web Vitals, Mobile.** Note how many URLs are good, need
   improvement, and poor.
2. **Identify the URL groups**, not individual URLs. Which template is failing?
3. **Run PageSpeed Insights on one representative URL per failing group.**
4. **Record field data for all three metrics.** Ignore the Lighthouse score for now.
5. **Note the LCP element.** From Section 17 it is usually an image.
6. **Check whether you are failing on mobile only**, which is common, or on both.
7. **Write down which specific metric fails on which template.** That is Section 28's work
   queue.
8. **If everything is already passing, write "CWV is a floor and I am over it" and move on.**
   Do not optimize further for ranking reasons.

## Capstone step

You know your field-data status for all three metrics on mobile, grouped by template rather
than by URL, with the LCP element identified for each failing group. Section 28 fixes them.

## Key takeaways

- LCP 2.5s, INP 200ms, CLS 0.1, at the 75th percentile of real visits over 28 days, all three
  passing simultaneously.
- Google ranks on field data (CrUX) only. A perfect Lighthouse score means nothing if field data
  fails, and fixes take weeks to appear because the window is rolling.
- They are a tiebreaker between comparable pages, not a lever for weak content. Pass the
  threshold and stop optimizing for ranking reasons.
- The conversion case studies are real and are about revenue, not rankings. Be clear which
  argument you are making.

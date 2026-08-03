# Technical SEO - Section 30: Structured Data and Schema

*Not a ranking factor, sunset by Google faster than most people are updating, and still worth implementing for two specific reasons.*

**Bottom line:** Schema markup earns rich results and clarifies entity identity. It is
explicitly **not a ranking factor**, and the vendor claims about it driving AI citations do not
survive the two causal studies that tested them. Implement it for eligibility and entity
clarity, not as a ranking play, and know which types Google has retired.

---

## What it is

Structured data is machine-readable markup describing what a page contains. **JSON-LD is
Google's recommended format**, placed in the `<head>`, because it keeps markup separate from
content and is easiest to maintain. `[confirmed]`

Schema.org has over 800 classes. **Google renders rich results for roughly 30 of them.** Most of
the vocabulary produces nothing visible. `[practitioner]`

## The evidence, stated honestly

This is the clearest evidence conflict in the entire corpus, and it is a good final exercise in
the Section 3 grading method.

**Vendor claims:** SE Ranking and DigitalApplied report **71% of ChatGPT-cited pages** and
**65% of Google AI Mode pages** carry structured data. xseek.io claims **3.2x** more citations.
Writesonic and Stackmatix claim **2.5x to 3:1**. `[practitioner, correlational, self-interested]`

**The counter-evidence:** **Ahrefs studied 1,885 pages** and found **no major uplift in AI
citations from schema alone**. **SearchAtlas found no direct correlation** between schema
coverage and citation rate. Both causal or large-sample. `[practitioner, causal design]`

**Google's position:** John Mueller has confirmed structured data is **not a direct ranking
factor**, and Google's May 2026 AI search guidance states structured data is **not required** to
appear in AI Overviews. `[confirmed]`

**Resolution:** the vendor numbers are correlational and come from companies selling schema
tools. The two studies designed to detect causation found nothing. Schema is connective tissue
that clarifies what already exists, not a shortcut for weak content.

**So implement it for:** rich result eligibility, and entity disambiguation, which genuinely
matters for Section 40. Not for rankings, and not because a vendor promised 3x citations.

## The types that still earn rich results

Google actively rewards roughly 14 primary types: **Article, Breadcrumb, Product** (including
MerchantListing and ProductVariants), **Recipe, Event, LocalBusiness, JobPosting, Video,
Organization, Speakable, Return Policy, Shipping Policy, Loyalty Program** (added 2025), and
**Carousel**. Also active: ProfilePage, DiscussionForum, QAPage, Dataset. `[practitioner]`

**For most business sites, the useful set is small:**

- **Organization** on the homepage, with `sameAs` pointing at your profiles. This is the entity
  anchor for Section 40
- **BreadcrumbList** sitewide. Described as one of the most under-implemented signals available,
  and it makes hierarchy machine-readable independently of your prose
- **Article** or **BlogPosting** on content, with `author` and `dateModified`
- **LocalBusiness** if you have a physical location or service area
- **Person** on author pages, with `sameAs` to their profiles
- **Product**, **FAQ** or **Event** only if genuinely applicable

## The deprecations

Worth knowing precisely, because plenty of sites are still implementing types that do nothing.

| Type | Status |
|---|---|
| **FAQ rich results** | **Sunset entirely 7 May 2026**, including the former health and government exceptions |
| **HowTo** | Effectively dead on desktop since 2023, near-zero payoff |
| **Book Actions, Course Info (old format), ClaimReview, Estimated Salary, Learning Video, Special Announcement, Vehicle Listing** | Phased out in the June 2025 sweep. ClaimReview now restricted to verified fact-checkers |
| **Sitelinks Searchbox** | Sunset late 2024 |

`[practitioner]`

**An important nuance:** **FAQPage and HowTo markup still carry value for non-Google engines**,
including ChatGPT, Perplexity and Bing Copilot, which continue to use them. Ripping the markup
out because Google stopped rendering the rich result is the wrong reaction. Leave it, just do
not expect a Google rich result. `[practitioner]`

## Implementation rules

- **JSON-LD in the `<head>`.** Best practice for AI-citation reliability as well as
  maintainability. `[practitioner]`
- **Absolute URLs**, always.
- **ISO 8601 for dates and durations.** `2026-04-18`, `PT30M`. Getting this wrong is the most
  common validation error.
- **Markup must match visible content.** Marking up a review score not shown on the page is a
  structured data spam violation and carries a manual action risk.
- **Use stable `@id` identifiers** to connect Organization, Person and Article nodes into one
  graph rather than isolated islands. This is the part that actually matters for entity work.
- **Keep `dateModified` accurate.** It is a real recency signal for Perplexity and AI Overviews,
  and faking it is the same fake-freshness problem as Section 19.

## Validation

**Schema Markup Validator** (`validator.schema.org`) for vocabulary conformance.

**Google Rich Results Test** for whether Google will actually render an enhancement. These
answer different questions and you want both.

**Search Console Enhancements reports** are ground truth at scale. Valid markup on one page
means nothing if the template breaks on 400 others.

## What not to do

- **Do not mark up content that is not on the page.**
- **Do not implement FAQ schema expecting a Google rich result.** It is gone.
- **Do not add every schema type you can.** Irrelevant markup adds maintenance and no benefit.
- **Do not treat schema as a ranking tactic.** Google has said it is not, and the causal studies
  agree.
- **Do not let a plugin generate markup you have never validated.** Plugin-generated schema is
  frequently invalid or duplicated.

> **Why this matters:** schema is the area where the gap between vendor marketing and evidence is
> widest in all of SEO. It is genuinely useful for two things, and it is sold as useful for a
> third that two causal studies could not detect. Being precise about that is the difference
> between a credible recommendation and repeating a tool company's brochure.

## Do this now

1. **Check what schema you currently have.** Run your homepage and one content page through the
   Rich Results Test.
2. **Validate it** at `validator.schema.org`. Note every error and warning.
3. **Add or fix Organization schema** on the homepage, with `sameAs` pointing at your LinkedIn,
   Crunchbase and any other real profiles. Section 40 builds on this.
4. **Add BreadcrumbList sitewide** if it is missing. High value, low effort, widely skipped.
5. **Add Article schema** to your content template, with a real `author` and accurate
   `dateModified`.
6. **Check for FAQ schema** you are maintaining for a Google rich result that no longer exists.
   Leave the markup if other engines use it, but stop expecting Google output.
7. **Verify markup matches visible content** on every type you use.
8. **Open Search Console Enhancements** and check for template-wide errors.
9. **Confirm your `@id` values are stable and connect your entities**, rather than each block
   standing alone.

## Capstone step

Your capstone site has valid Organization schema with `sameAs`, sitewide breadcrumbs, Article
schema with real authorship and accurate dates, no markup that contradicts visible content, and
no expectations resting on retired rich result types.

## Key takeaways

- JSON-LD in the head, absolute URLs, ISO 8601 dates, and markup that matches what is visible.
- Structured data is **not a ranking factor**, and the two causal studies that tested schema
  against AI citations found no meaningful uplift. Implement for rich results and entity
  clarity.
- FAQ rich results sunset on 7 May 2026 and HowTo is effectively dead, but both still carry
  value for ChatGPT, Perplexity and Bing Copilot.
- Organization with `sameAs` plus sitewide BreadcrumbList is the highest-value, lowest-effort
  pair for most business sites.

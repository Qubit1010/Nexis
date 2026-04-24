# Website Audit Framework

This is the grading rubric used by `analyze_audit.py`. It defines what to check in each of the 4 dimensions, how to score findings, and how to phrase them so they're sharp and actionable.

---

## The 4 dimensions

| # | Dimension | What we're actually evaluating | Primary data source |
|---|---|---|---|
| 1 | UX & Messaging | Does the site instantly communicate what they do, who it's for, and why you'd care? Visual hierarchy, CTA placement, copy quality, trust signals. | Firecrawl markdown + metadata |
| 2 | SEO Basics | Title tags, meta descriptions, heading hierarchy, image alt text, mobile tags, structured data. Not deep backlink analysis — just the on-page fundamentals. | Firecrawl HTML |
| 3 | Performance | PageSpeed score (mobile + desktop), Core Web Vitals (LCP, CLS, TBT), render-blocking resources. | Google PageSpeed Insights API |
| 4 | Conversion | Value prop clarity, CTA strength, friction, trust signals (testimonials, logos, case studies), contact ease, offer positioning. | Firecrawl markdown |

---

## Severity rubric

Every finding gets a severity. Use it to prioritize the report.

| Severity | Definition | Example |
|---|---|---|
| **critical** | Actively losing leads or revenue right now. Fix within 1 week. | "No phone or contact form visible above the fold on mobile — ~60% of visitors never scroll" |
| **high** | Significant gap affecting conversion or rankings. Fix within 2-4 weeks. | "Title tag is 'Home' — no keywords, no value prop, likely tanks Google CTR by 40%+" |
| **medium** | Noticeable but not blocking. Fix when convenient. | "No customer testimonials on homepage — weakens trust" |
| **low** | Polish issue. Worth noting in a deep audit, skip in quick mode. | "Footer copyright year reads 2021 — signals neglect" |

---

## Dimension 1 — UX & Messaging

### What to check (quick mode)

1. **Value prop clarity** — can a visitor tell what the business does within 5 seconds of landing?
2. **Above-the-fold CTA** — is there one obvious next action?
3. **Headline quality** — is it specific, outcome-focused, or is it generic ("Welcome to X")?
4. **Visual hierarchy** — does the eye flow naturally from headline → subheadline → CTA?
5. **Trust signals** — logos, testimonials, reviews, case studies visible without scrolling far?

### Additional checks (deep mode only)

6. Copy throughout the site — does it speak to the customer, or about the business?
7. Internal navigation clarity — are section labels clear or cute?
8. Consistency of messaging across pages
9. Mobile experience cues (viewport meta, responsive indicators)
10. Accessibility basics (alt text presence, heading order)

### Red flags (always flag if present)
- Headline is a brand name only ("Acme Corp") with no value statement
- Hero CTA is "Learn more" or "Contact us" with no specificity
- Stock photos with no real team/work shown
- Long paragraphs of marketing copy above the fold

---

## Dimension 2 — SEO Basics

### What to check (quick mode)

1. **Title tag** — present, under 60 chars, contains target keyword, not duplicated
2. **Meta description** — present, under 160 chars, specific and actionable
3. **H1 tag** — exactly one, matches user intent
4. **Heading hierarchy** — H2/H3 logical, not skipping levels
5. **Open Graph tags** — og:title, og:description, og:image present for social sharing

### Additional checks (deep mode only)

6. Canonical URL set correctly
7. Image alt attributes present on key images
8. Structured data (JSON-LD) for Organization / LocalBusiness / Service
9. Robots meta not accidentally noindex
10. Sitemap.xml and robots.txt accessible
11. URL structure clean (no query strings for content pages)
12. Internal linking patterns

### Red flags (always flag if present)
- Title tag is "Home" or the domain name
- Missing or empty meta description
- Multiple H1 tags or zero H1
- Images with no alt text on hero/product sections
- noindex set on homepage

---

## Dimension 3 — Performance

### What to check

1. **Mobile PageSpeed score** — under 50 is critical, 50-70 is high, 70-90 is medium, 90+ is fine
2. **Desktop PageSpeed score** — same thresholds, weighted less (mobile matters more for most prospects)
3. **Largest Contentful Paint (LCP)** — should be under 2.5s (good), 2.5-4s (needs work), >4s (poor)
4. **Cumulative Layout Shift (CLS)** — should be under 0.1 (good), 0.1-0.25 (needs work), >0.25 (poor)
5. **Total Blocking Time / Interactive** — contextualize for mobile

### Framing performance findings

Numbers alone don't land. Translate scores into business impact:
- "Mobile PageSpeed at 34/100 — sites under 50 typically lose 50%+ of mobile visitors before the page finishes loading"
- "LCP at 5.2s on mobile — Google confirms pages over 4s see ~30% higher bounce rates"

### If PageSpeed API is unavailable
Mark performance as "not measured in this audit" in the report. Do NOT fabricate scores. Note it explicitly so the prospect knows.

---

## Dimension 4 — Conversion

### What to check (quick mode)

1. **Primary CTA** — is there one dominant action? Is it above the fold? Is the language specific?
2. **Value stack** — does the page articulate outcomes, not just features?
3. **Social proof** — testimonials, logos, case studies, star ratings, numbers
4. **Friction** — long forms, gated resources, required signups to see pricing, unclear pricing
5. **Contact ease** — phone, email, contact form all easy to find

### Additional checks (deep mode only)

6. Offer positioning — is the core service clearly scoped and priced (or at least anchored)?
7. Urgency or scarcity signals (tasteful, not spammy)
8. Risk reversal (guarantees, free trials, consultation offers)
9. Multiple conversion paths for different buyer stages
10. Exit intent / retargeting infrastructure visible (pixels, Calendly embeds, etc.)

### Red flags (always flag if present)
- No visible CTA anywhere above the fold
- Contact form is 8+ fields long for a top-of-funnel request
- No social proof of any kind on the homepage
- Phone number or email hidden behind multiple clicks
- Generic "schedule a call" with no framing of what the call delivers

---

## Finding output schema

Every finding returned by `analyze_audit.py` must include:

```json
{
  "dimension": "UX & Messaging | SEO Basics | Performance | Conversion",
  "severity": "critical | high | medium | low",
  "title": "Short title (under 60 chars) — the problem in plain English",
  "evidence": "Concrete observation from the site. Quote the actual copy or name the specific element. No guessing.",
  "business_impact": "One sentence on what this costs them — leads lost, ranking lost, trust lost. Use ranges, not made-up exact numbers.",
  "fix": "One concrete recommendation. Specific enough that a developer could act on it.",
  "effort": "quick (under 2 hours) | medium (half a day) | significant (multi-day)"
}
```

---

## Writing rules for findings

1. **Be specific, not generic.** "Your homepage is confusing" is useless. "The H1 reads 'Innovative solutions for modern business' — a visitor can't tell if you do consulting, software, or design" is useful.
2. **Quote real evidence.** When you flag bad copy, include the actual copy. When you flag a missing element, name it.
3. **Business impact, not lecture.** Prospects don't care about Lighthouse scores. They care about losing leads.
4. **Ranges, not exact numbers.** "Likely drops conversion 15-30%" beats "reduces conversion by 22.4%."
5. **No jargon.** "LCP" means nothing to a non-technical founder. Translate: "Main content takes over 5 seconds to load."
6. **No emojis. No em dashes.** Use commas or periods. (Google Docs exports break on em dashes — see memory.)
7. **Respect the reader.** The audit goes to a prospect. It should feel sharp, not condescending. Flag problems without insulting their team.

---

## Deep mode scoring

Deep mode produces a 1-10 score per dimension in addition to findings. Scoring rubric:

| Score | Meaning |
|---|---|
| 9-10 | Exceptional. Virtually nothing to fix. |
| 7-8 | Strong. Minor polish opportunities only. |
| 5-6 | Mixed. Solid foundation but real gaps. |
| 3-4 | Weak. Core issues blocking results. |
| 1-2 | Severe. Needs rebuilding in this dimension. |

Most prospect sites land in the 3-6 range across dimensions. That's the whole reason the audit is valuable.

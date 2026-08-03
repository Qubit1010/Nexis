# Technical SEO - Section 31: International SEO and hreflang

*The most error-prone tag in SEO, and the one most sites should not be using at all.*

**Bottom line:** hreflang tells search engines which language and regional version of a page to
show which users. It is genuinely difficult to implement correctly, breaks silently, and is
unnecessary for most sites. This section is as much about deciding you do not need it as about
implementing it.

---

## Do you actually need this?

Answer honestly before reading further.

**You need hreflang if:** you have substantially the same content in multiple languages, or
targeted at multiple countries with meaningful differences such as currency, pricing, shipping,
or legal terms.

**You do not need hreflang if:**

- You have one site in one language, even with international customers
- You have one English site serving the US, UK and Australia with no meaningful differences
- You are considering translating but have not
- Your "international" pages are the same content with a currency symbol swapped

**A single well-executed site usually outperforms three thin translated ones.** Translation is a
content commitment, not a technical toggle. If you cannot maintain the other versions properly,
do not create them.

Most readers of this section should conclude they do not need hreflang, note the reasoning, and
move to Tier 4.

## The URL structure decision

If you do need international targeting, this choice comes first and is expensive to reverse.

| Structure | Example | Pros | Cons |
|---|---|---|---|
| **ccTLD** | `example.de` | Strongest geo signal, clear to users | Separate authority per domain, expensive, most maintenance |
| **Subdirectory** | `example.com/de/` | Inherits domain authority, cheapest, easiest | Weakest geo signal |
| **Subdomain** | `de.example.com` | Middle ground | Authority sharing is ambiguous, more setup |
| **Parameters** | `example.com?lang=de` | None worth having | Avoid entirely |

**Subdirectories are the right default for most businesses.** Authority consolidates on one
domain, and hreflang plus Search Console targeting supplies the geo signal that the URL does
not.

Choose ccTLDs when the market genuinely demands local presence, typically regulated industries
or markets where users distrust foreign domains.

## How hreflang works

Each page declares every language version of itself, **including itself**.

```html
<link rel="alternate" hreflang="en-us" href="https://example.com/page" />
<link rel="alternate" hreflang="en-gb" href="https://example.com/uk/page" />
<link rel="alternate" hreflang="de" href="https://example.com/de/page" />
<link rel="alternate" hreflang="x-default" href="https://example.com/page" />
```

**Format:** language code (ISO 639-1), optionally a hyphen and region code (ISO 3166-1 Alpha 2).
Language alone is valid. **Region alone is not.** `de` is valid, `de-AT` is valid, `AT` is not.

**`x-default`** specifies the fallback for users matching no other version. Always include it.

**Three placement options:** HTML head, HTTP headers for non-HTML files like PDFs, or the XML
sitemap. Sitemap implementation is easiest to maintain at scale and keeps the markup out of your
templates.

## The five errors that break it

**1. Missing return links.** If page A declares B as an alternate, **B must declare A**. hreflang
is bidirectional and a one-way declaration is ignored entirely. This is the most common failure
and it fails silently.

**2. Not self-referencing.** Each page must include itself in its own hreflang set.

**3. Wrong codes.** `en-UK` is invalid; the country code is `GB`. Region without language is
invalid.

**4. Pointing at non-canonical URLs.** hreflang must reference canonical, indexable, 200-status
URLs. Pointing at a redirect or a canonicalized duplicate breaks the cluster.

**5. Conflicting with canonicals.** If the German page canonicalizes to the English page, you
are simultaneously saying "index this separately for German users" and "do not index this,
index the English one". The canonical wins and hreflang is ignored.

Every one of these fails quietly. Nothing alerts you.

## hreflang is not a ranking signal

Worth being clear, because it is often sold as one. hreflang does not improve rankings. It helps
the **correct version** rank for the correct audience, and it prevents your language versions
being treated as duplicates of each other.

The benefit is showing the right page to the right user, which improves engagement and
conversion. It does not make you rank better in general.

## The other pieces

**Translation quality.** Machine translation with no human review reads as low-quality content
and is judged as such. This is a content problem, and it is the most common reason international
sites underperform.

**Localize, do not just translate.** Currency, date formats, phone formats, addresses, payment
methods, legal requirements, and examples that make sense locally.

**Search Console international targeting.** For subdirectories and subdomains you can set a
target country per property. Not available for ccTLDs, which carry the signal inherently.

**Local hosting or a CDN.** Latency affects Core Web Vitals, and your German users measuring
LCP against a US-only server will not pass.

**Local link building.** Authority is somewhat market-specific. Links from German sites help the
German version.

## Testing

- **Search Console international targeting report**, where available, lists hreflang errors
  directly.
- **Screaming Frog** crawls and validates hreflang clusters, including missing return links.
- **Manual spot check:** pick one page, list every hreflang it declares, then visit each of those
  URLs and confirm they declare it back.

That manual check on three pages finds most problems faster than reading documentation.

> **Why this matters:** hreflang has an unusually high ratio of implementations that are broken
> to implementations that work, because every failure mode is silent. And the more common
> mistake is implementing it at all on a site that never needed it, which adds permanent
> maintenance for no benefit.

## Do this now

1. **Answer the question at the top honestly.** Do you have substantially different content for
   different languages or markets? If no, write down that hreflang does not apply and skip to
   step 8.
2. **If yes, choose your URL structure.** Subdirectory unless you have a specific reason.
3. **Map your language and region versions.** Which pages have which alternates.
4. **Implement hreflang**, in the sitemap if you have more than a handful of pages.
5. **Verify self-reference and return links** on three pages manually.
6. **Check codes are valid** and that region never appears without language.
7. **Confirm no conflict with canonicals.**
8. **If you skipped, note the decision and why.** A documented "not applicable" is a legitimate
   audit finding and stops someone implementing it later for no reason.

## Capstone step

Tier 3 is complete. You have either a validated hreflang implementation with confirmed return
links, or a documented decision that international targeting does not apply to your site. Your
capstone site is now crawlable, indexable, canonically clean, correctly redirected, sensibly
structured, renderable, fast enough, mobile-complete, and marked up.

## Key takeaways

- Most sites do not need hreflang. One well-executed site usually beats three thin translated
  ones, and deciding you do not need it is a legitimate outcome.
- Subdirectories are the right default. ccTLDs only when the market genuinely demands local
  presence.
- Every hreflang declaration must be bidirectional and self-referencing, and every failure mode
  is silent. Manually verify return links on a few pages.
- hreflang is not a ranking signal. It shows the right version to the right user and stops your
  translations being read as duplicates.

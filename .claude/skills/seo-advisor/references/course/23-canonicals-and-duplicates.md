# Technical SEO - Section 23: Canonicals and Duplicate Content

*There is no duplicate content penalty. There is signal dilution, which is worse because nobody tells you it is happening.*

**Bottom line:** Duplicate content does not get you penalized. It splits ranking signals across
several URLs so that none of them is as strong as the one page you should have had. The
canonical tag is a hint, not a directive, and Search Console tells you when Google overrules
you.

---

## The penalty myth

There is no duplicate content penalty for ordinary duplication. Google's position is
consistent: duplication is normal on the web, and it deduplicates rather than punishes.
`[confirmed]`

What actually happens is worse in practice because it is silent:

- **Signals split.** Links, engagement and relevance spread across several URLs.
- **Google picks one** to represent the group, and it may not be the one you wanted.
- **Crawl budget is wasted** fetching the same content repeatedly.

Penalties apply to *scraped* or deliberately manipulative duplication, which is a different
thing.

## Where duplication comes from

Most duplication is accidental and technical.

**Protocol and host variants.** `http://` and `https://`, `www` and non-`www`. Four versions of
your homepage if unresolved.

**Trailing slashes.** `/services` and `/services/`.

**Case sensitivity.** `/Services` and `/services` on servers that treat them as distinct.

**URL parameters.** Tracking (`?utm_source=`), sorting (`?sort=price`), filtering, and session
IDs all produce unique URLs for identical content.

**Pagination.** Page 2 of a category often shares most of its template and description with
page 1.

**Faceted navigation.** The largest generator of duplicates on ecommerce sites. Colour x size x
brand x price produces thousands of near-identical URLs.

**Printer-friendly and AMP versions.**

**Syndicated content.** Your article republished elsewhere, or someone else's on your site.

**Boilerplate-heavy pages.** Twenty location pages differing only in the city name are
functionally duplicates, and this one is a *content* problem wearing a technical costume.

## The canonical tag

```html
<link rel="canonical" href="https://example.com/preferred-url" />
```

**It is a hint, not a directive.** Google considers it alongside other signals and can pick a
different canonical. This surprises people who expect it to be binding. `[confirmed]`

**Use a self-referencing canonical on every indexable page.** The page points at itself. This
is the default and it protects against parameter variants appearing.

**Rules that make canonicals work:**

- Use **absolute URLs**, not relative
- Point at a URL that returns **200**, not a redirect and not a 404
- **One canonical per page.** Multiple tags cause Google to ignore all of them
- **Do not canonicalize everything to the homepage.** A common and destructive error that
  tells Google the rest of your site does not exist
- **Canonical and `noindex` together is contradictory.** One says "index this other page
  instead", the other says "index nothing". Pick one
- **Internal links should point at canonical URLs directly**, not at variants that canonicalize
  elsewhere. Contradicting your own canonical with your internal linking weakens it
  `[practitioner]`

## When Google overrules you

Search Console, URL Inspection, shows **"Google-selected canonical"** next to **"User-declared
canonical"**. When they differ, Google disagreed.

Common reasons:

- The canonical target is substantially different content, so the pages are not actually
  duplicates
- Internal links overwhelmingly point at the other URL
- The other URL is in the sitemap and this one is not
- The other version has the backlinks
- Redirect and canonical signals contradict each other

The fix is to make every signal agree: canonical tag, internal links, sitemap inclusion, and
redirects all pointing the same way.

## The right tool for each case

| Situation | Tool |
|---|---|
| Same content, one permanent preferred URL | **301 redirect** |
| Same content, both URLs must remain accessible | **Canonical tag** |
| Near-duplicate you never want indexed | **`noindex`** |
| Infinite parameter combinations | **Canonical plus robots.txt on the crawl trap** |
| Content genuinely serving different intents | **Rewrite so they are different** |
| Same content, different languages or regions | **hreflang**, Section 31 |

**Redirect when you can, canonicalize when you must.** A 301 is a stronger, unambiguous signal.
Canonicals are for when both URLs need to stay reachable.

## Parameters and faceted navigation

The biggest source of duplication at scale.

- **Self-referencing canonical on the clean URL**, and canonical from parameter variants back
  to it.
- **`noindex` on filter combinations** nobody searches for.
- **Robots-disallow genuine crawl traps**, meaning infinite combinations, accepting from
  Section 21 that disallowed URLs cannot be deindexed by a `noindex` they can never read. Clean
  them up first, then block.
- **Keep internal links pointing at clean URLs.** If your own faceted nav links to
  parameterized URLs, you are generating the problem yourself.

## The location-page trap

Worth calling out because agencies do it constantly.

Twenty pages that are identical except for a city name are not twenty pages. Google will index
one or two and ignore the rest, or index none. This is not solved with canonicals, because they
are not duplicates you want consolidated, they are pages you want to be genuinely distinct.

The fix is content: local specifics, real projects in that area, genuine differences. Section
35 covers this properly. If you cannot write a genuinely different page for a location, you
probably should not have one.

> **Why this matters:** duplication is silent. Nothing in Search Console shouts about it, no
> penalty notice arrives, and the pages still exist. They just quietly underperform, and the
> cause is invisible unless you go looking at which canonical Google actually selected.

## Do this now

1. **Test your host and protocol variants.** Load `http://`, `https://`, `www` and non-`www`.
   All should redirect to one canonical version.
2. **Test trailing slash behaviour** on a few URLs.
3. **Run URL Inspection on 5 important pages.** Compare user-declared canonical to
   Google-selected canonical. Note any disagreement.
4. **Check for self-referencing canonicals** on your key templates.
5. **Search for parameter URLs in the index:** `site:yourdomain.com inurl:?`. Note what is
   indexed that should not be.
6. **Verify no page has multiple canonical tags**, which is a common plugin conflict.
7. **Confirm nothing is canonicalized to the homepage** except the homepage.
8. **Check internal links point at canonical URLs**, not at variants.
9. **If you have location or service-area pages, read two side by side.** If they differ only by
   a place name, mark them for the Section 35 rewrite.

## Capstone step

Host, protocol and trailing-slash variants all resolve to one version. Self-referencing
canonicals are in place, no page carries conflicting signals, and you know of any case where
Google has overruled your canonical choice.

## Key takeaways

- There is no duplicate content penalty. There is signal dilution, which is worse because it is
  silent and nothing reports it.
- The canonical tag is a hint. Search Console's "Google-selected canonical" tells you when you
  were overruled, and the fix is making every signal agree.
- Redirect when you can, canonicalize when both URLs must stay reachable, `noindex` when you
  simply never want it indexed.
- Location pages differing only by a city name are a content problem, not a canonical problem.

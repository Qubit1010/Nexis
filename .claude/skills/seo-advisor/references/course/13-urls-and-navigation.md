# On-Page & Content - Section 13: URLs, Slugs, and Navigation

*A minor ranking signal that is expensive to change, which makes getting it right early worth more than it looks.*

**Bottom line:** URL structure is a small direct signal and a large indirect one. It shapes
crawl priority, it is what people see and copy, and it is the one on-page element where
changing your mind later costs real traffic. Set the pattern deliberately, then leave
existing URLs alone.

---

## The rules

**Short.** Under **60 characters** where practical. `[practitioner]`

**Lowercase.** Some servers treat `/Page` and `/page` as different URLs, which creates
duplicates you did not intend.

**Hyphens, never underscores.** Google treats hyphens as word separators and underscores as
joiners. `seo_audit_guide` reads as one token, `seo-audit-guide` reads as three words.

**The main term, once.** `/blog/seo-audit-guide` not `/blog/seo-audit-guide-seo-checklist-seo-tips`.

**No dates for evergreen content.** `/2024/03/seo-guide` tells everyone the piece is old and
makes updating awkward. Dates belong on news, not on guides.

**No parameters where a clean path will do.** `?id=4471` is opaque to readers and creates
canonical work you do not need.

**Flat hierarchy, three levels maximum.** `/services/seo-audit` beats
`/services/marketing/search/audits/technical/seo-audit`. Depth costs crawl priority, which is
Section 25.

## The rule that saves you the most pain

**Do not change existing URLs to optimize them.**

A URL change means a redirect, which means: some signal loss through the redirect, every
internal link to update, every external link now pointing at a redirect, social shares
pointing at the old URL, and a window where things behave oddly.

Weigh that against the gain, which is a minor ranking signal. The maths almost never works.

**When a URL change is justified:**

- The URL is genuinely broken or misleading
- You are restructuring the site anyway, so the redirect cost is already being paid
- The URL contains something you must remove, such as a wrong brand name or a discontinued
  product
- A migration is happening for other reasons

**When it is not justified:** the slug is not quite the keyword you now target, or somebody
wants it tidier.

If you do change one, 301 the old URL, update every internal link to point at the new one
directly rather than through the redirect, and expect a settling period. Section 24 covers
the mechanics.

## Navigation labels

Navigation is where URL thinking meets user thinking, and the two pull in different
directions.

**Use the words your customers use, not your internal vocabulary.** If your team says
"engagements" and customers say "projects", the nav says projects. Your Section 6 first-party
research is the source for this: real phrasing from real buyers.

**Navigation links are strong internal links.** Anything in the main nav gets linked from
every page, which concentrates authority on it. That means the nav is a statement about what
matters on your site. A nav with fifteen items says nothing matters.

**Keep primary nav to about seven items.** More than that and both people and crawl priority
get diluted.

**Breadcrumbs earn their place.** They give readers orientation, they reinforce hierarchy for
crawlers, and with `BreadcrumbList` schema they make the structure machine-readable
independently of your prose. That schema type is described as one of the most
under-implemented signals available, and Section 30 covers it. `[practitioner]`

## Common structural mistakes

**Category pages that are just lists of links** with no content of their own. These are thin
by default and rarely rank. Give a category page a genuine introduction that establishes what
the category covers.

**Every page one click from the homepage.** Sounds good, produces a flat mess with no
hierarchy and a nav nobody can scan.

**Orphan pages.** Published, never linked from anywhere. From Section 2, these are effectively
invisible. Every page needs at least one internal link pointing at it.

**Parallel structures.** `/services/seo` and `/seo-services` both existing is cannibalization
with extra steps.

> **Why this matters:** URLs are the one on-page element with a real switching cost. Titles
> can be rewritten weekly at no risk. A URL changed carelessly costs traffic and creates
> maintenance forever. Decide the pattern once, apply it to new pages, and resist tidying old
> ones.

## Do this now

1. **Write down your URL pattern** as a rule: what a service page looks like, what a blog post
   looks like, what a location page looks like.
2. **Check your existing URLs against it.** List which do not comply.
3. **For each non-compliant URL, decide: leave it.** Unless it is genuinely broken or
   misleading. Write the reason next to any you decide to change.
4. **Check for parallel structures.** Search `site:yourdomain.com` and look for two URLs
   covering the same thing.
5. **Audit your main navigation.** Count the items. Are the labels your customers' words or
   yours? Is anything in there that does not deserve a link from every page?
6. **Find orphan pages.** In Search Console, look for indexed URLs that receive no internal
   links, or crawl the site with Screaming Frog's free tier and check the orphan report.
7. **Add internal links to any orphans worth keeping.** Delete or redirect the rest.

## Capstone step

You have a documented URL pattern for new pages, a deliberate decision to leave existing URLs
alone unless genuinely broken, a navigation audited against customer vocabulary, and orphan
pages either linked or removed.

## Key takeaways

- Short, lowercase, hyphenated, main term once, three levels maximum, no dates on evergreen
  content.
- Do not change existing URLs to optimize them. The signal gain is minor and the redirect and
  maintenance cost is real.
- Navigation labels should use customer vocabulary, and everything in the main nav gets linked
  from every page, so a fifteen-item nav says nothing matters.
- Orphan pages are effectively invisible. Every page worth keeping needs at least one internal
  link pointing at it.

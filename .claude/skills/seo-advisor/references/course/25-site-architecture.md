# Technical SEO - Section 25: Site Architecture and Crawl Depth

*Architecture is where your authority flows. Bury a page and you have decided it does not matter.*

**Bottom line:** Every commercial page should be reachable within three clicks of the homepage.
Pages five or more clicks deep are crawled less often and receive less link equity. Architecture
is not a diagram exercise, it is the mechanism that decides which of your pages can compete.

---

## What architecture actually does

**It distributes authority.** Your homepage typically holds the most, mostly from external
links. Every link from it passes some on. Pages far from the homepage receive very little.

**It signals importance.** Click depth is a statement. A page linked from the homepage is
important; a page six clicks down is not, and Google reads it that way.

**It determines crawl frequency.** Deep pages are crawled less often, so updates take longer to
register.

**It groups topics.** From Section 15, a coherent structure makes topical relationships
explicit rather than leaving them to be inferred.

## The rules

| Rule | Value | Tier |
|---|---|---|
| Clicks from homepage to any commercial page | **3 maximum** | `[practitioner]` |
| Depth at which pages start being neglected | **5+ clicks** | `[practitioner]` |
| Category depth | **3 levels maximum** | `[practitioner]` |

Click depth means the shortest path following links, not URL folder depth. A page at
`/a/b/c/d/e/page` linked from the homepage is one click deep.

## The shape

**Flat enough to reach, structured enough to mean something.**

```
Homepage
├── Services
│   ├── SEO
│   ├── Web Development
│   └── AI Automation
├── Industries
│   ├── SaaS
│   └── Ecommerce
├── Resources (pillar pages)
│   ├── SEO Guide (pillar)
│   │   ├── cluster page
│   │   └── cluster page
│   └── Automation Guide (pillar)
└── About / Contact
```

Everything commercial sits two clicks from home. Cluster pages sit three, which is acceptable
because the pillar concentrates authority and passes it down.

**Do not go completely flat.** Linking every page from the homepage removes hierarchy entirely,
dilutes the nav, and tells Google nothing about relationships.

## The three mechanisms that control depth

**Navigation.** The strongest and bluntest. Everything in the main nav is linked from every
page. From Section 13, keep it to about seven items, because a fifteen-item nav concentrates
nothing.

**Contextual internal links.** From Section 16. This is how you pull an important deep page up
without cluttering the nav.

**Breadcrumbs.** Reinforce hierarchy, help users, and with `BreadcrumbList` schema make the
structure machine-readable independently of prose. Described as one of the most
under-implemented signals available. `[practitioner]`

## Category and hub pages

Category pages that are only a list of links are thin by default and rarely rank.

Give each one:

- A genuine introduction explaining what the category covers and who it is for
- Context around the links rather than a bare grid
- Its own target cluster from your Section 8 map

A category page done properly is a pillar page. Done lazily it is a crawl waypoint that ranks
for nothing.

## Faceted navigation

The largest architectural problem on ecommerce and directory sites, and the biggest generator
of crawl waste.

Colour x size x brand x price x sort order produces thousands or millions of URLs from a few
hundred products. Each looks like a page. Almost none deserves indexing.

Handling it:

- **Index the facet combinations people actually search for.** "Blue running shoes" probably has
  demand. "Blue running shoes size 9 sorted by price ascending" does not.
- **`noindex` the rest**, with a self-referencing canonical or canonical back to the clean
  category.
- **Block genuine infinite traps in robots.txt**, remembering from Section 21 to clean up the
  index first, since a disallowed URL cannot read a `noindex`.
- **Do not internally link to parameterized URLs** from your own navigation. Most facet
  explosions are self-inflicted.

## Pagination

Keep it simple. `rel=next` and `rel=prev` are no longer used by Google.

- Each paginated page carries a **self-referencing canonical**. Do not canonicalize page 2 to
  page 1, they are different content.
- Usually `noindex` beyond page 1 for blog and category listings, unless the deeper pages
  genuinely have search demand.
- **Make sure products or articles on deep pagination are reachable another way**, through
  categories, tags, or the sitemap. Item 400 on page 20 is effectively unreachable otherwise.

## Finding depth problems

**Crawl the site** and sort by crawl depth. Screaming Frog reports it directly. Anything
important at depth 4 or more needs a shorter path.

**Check that path.** Click from the homepage to your most important service page, counting.
Most people are surprised.

**Look for orphans.** From Section 16, zero internal links means effectively invisible.

**Compare depth against value.** If your highest-margin service is at depth 4 and a 2019 blog
post is at depth 1, your architecture disagrees with your business.

> **Why this matters:** architecture decisions are usually made once, early, by whoever built
> the site, for reasons that had nothing to do with search. They then quietly determine which
> pages can compete for the next five years. It is one of the few areas where a couple of hours
> of restructuring can lift a whole section of a site.

## Do this now

1. **Draw your current architecture.** Actually draw it. Homepage, main sections, what sits
   under each.
2. **Click from the homepage to your three most important commercial pages**, counting clicks.
   Write the numbers down.
3. **Crawl the site and sort by depth.** List anything important at depth 4 or more.
4. **For each, decide the mechanism** to pull it up: nav, contextual links, or a hub page.
5. **Audit your category pages.** Any that are just link lists get a real introduction.
6. **Count your main nav items.** Over about seven, cut.
7. **Check breadcrumbs exist** on deep pages, and note whether they have `BreadcrumbList`
   schema. Section 30 implements it.
8. **If you have faceted navigation**, check `site:yourdomain.com inurl:?` and see how many
   parameter URLs are indexed.
9. **Fix the single worst depth problem** you found.

## Capstone step

You have a drawn architecture, measured click depth to your key pages, a plan for anything
buried too deep, category pages that are more than link lists, and one real depth problem
fixed.

## Key takeaways

- Three clicks maximum from the homepage to any commercial page. Five or more and the page is
  crawled less and receives less authority.
- Click depth is shortest link path, not URL folder depth.
- Category pages that are only link lists are thin. Given a real introduction and a target
  cluster, a category page is a pillar page.
- Faceted navigation is the biggest crawl-waste generator, and most facet explosions are caused
  by a site linking to its own parameterized URLs.

# Technical SEO - Section 22: Sitemaps and Indexation

*A sitemap is a claim about what deserves indexing. Fill it with junk and Google stops believing you.*

**Bottom line:** XML sitemaps are a discovery aid, not a ranking factor. Their real value is
diagnostic: a clean sitemap plus the Search Console indexing report tells you exactly which
pages Google refuses to store and why. Healthy sites hold an indexed-to-submitted ratio above
85%.

---

## What a sitemap is for

**It helps discovery**, especially for large sites, new sites with few backlinks, and pages
that are poorly internally linked.

**It is not a ranking factor.** Google has confirmed this. Submitting a sitemap does not
improve rankings and never has. `[confirmed]`

**It is a statement of intent.** You are telling Google "these are my canonical, indexable,
valuable URLs". That statement is only useful if it is true.

**Its best use is diagnostic.** Submit a sitemap of exactly the pages you believe should be
indexed, then compare against what actually is. The gap is your work list.

## The hard limits

| Limit | Value |
|---|---|
| URLs per sitemap file | **50,000** |
| Uncompressed file size | **50MB** |
| Solution beyond that | sitemap index file pointing at multiple sitemaps |

`[confirmed]`

## What belongs in it

**Only URLs that are all of the following:**

- Return **200 OK**
- Are **canonical**, not pointing elsewhere via a canonical tag
- Are **indexable**, no `noindex`
- Are **not disallowed** in robots.txt
- You genuinely **want indexed**

**What must not be in it:** 404s, redirects, noindexed pages, canonicalized duplicates,
parameter variants, paginated pages beyond the first, tag and author archives you do not care
about, thank-you and confirmation pages.

The reason this matters more than it sounds: **including junk trains Google to distrust the
sitemap.** If a meaningful proportion of submitted URLs are dead or noindexed, the whole file
becomes a weaker signal. `[practitioner]`

Most CMS-generated sitemaps include everything by default. Check yours rather than assuming.

## Structure for diagnosis

Split sitemaps by content type rather than shipping one giant file:

```
/sitemap.xml               (index)
  /sitemap-pages.xml
  /sitemap-blog.xml
  /sitemap-services.xml
  /sitemap-images.xml
```

This costs nothing and turns Search Console into a much better report: you can see that 98% of
service pages are indexed but only 60% of blog posts, which localizes the problem immediately.

**`lastmod` is worth setting accurately.** Google uses it as a hint about what to recrawl.
Setting it to today's date on every page every day destroys its value and is a recognized bad
pattern. `[practitioner]`

**`priority` and `changefreq` are ignored.** Do not spend time on them.

## Reading the indexation report

Search Console, Pages. This is the report that matters.

**Healthy: above 85% of submitted URLs indexed.** `[practitioner]`

The exclusion reasons worth knowing:

| Reason | What it means | Fix |
|---|---|---|
| **Crawled - currently not indexed** | Google fetched it and declined. **Quality signal** | Improve or remove the page |
| **Discovered - currently not indexed** | Known but not fetched. **Crawl signal** | Internal links, flatter architecture, crawl budget |
| **Duplicate, Google chose different canonical** | Google overruled your canonical | Section 23 |
| **Alternate page with proper canonical tag** | Working as intended | Nothing, but should not be in the sitemap |
| **Excluded by noindex** | Working as intended | Nothing, but remove from sitemap |
| **Soft 404** | Returns 200 but looks empty or error-like | Return a real 404, or add content |
| **Blocked by robots.txt** | Cannot be crawled | Section 21 |
| **Page with redirect** | Not a final URL | Remove from sitemap |

You met the first two in Section 2. They look adjacent and share no fixes: one is a content
problem, the other is an architecture problem.

## Getting pages indexed faster

**Request indexing** in URL Inspection. It queues the URL. It does not guarantee speed and the
daily quota is small, so use it for genuinely important pages, not in bulk.

**Internal links are the real mechanism.** A new page linked from a page Google crawls often
gets found quickly. An orphan may never be found at all.

**IndexNow** is a push protocol: you notify search engines that a URL changed rather than
waiting. Supported by **Bing, Yandex and Naver**. Google does **not** support it. Worth doing
anyway, because Bing powers ChatGPT search, which makes Bing indexation strategically more
important than its market share implies. `[practitioner]`

Most major CMSs have an IndexNow plugin. It takes ten minutes.

## When pages should not be indexed

Deliberate exclusion is a legitimate tool. `noindex` these:

- Thank-you and confirmation pages
- Internal search results
- Thin tag and category archives nobody searches for
- Staging and development environments, and check this, since leaked staging sites are common
- Paginated pages beyond the first, in most cases
- Filtered and faceted URL variants

Remember from Section 21: use `noindex`, not `Disallow`, or Google cannot read the instruction.

> **Why this matters:** indexation is binary. A page that is not indexed cannot rank, and no
> amount of content or link work changes that. It is also the fastest technical audit you can
> run, because Search Console tells you the answer directly and most people never open the
> report.

## Do this now

1. **Find your sitemap.** Usually `/sitemap.xml` or `/sitemap_index.xml`. Confirm it loads.
2. **Spot-check 10 URLs from it.** Do they all return 200, are they canonical, are any
   noindexed?
3. **Remove anything that should not be there.** Most CMS sitemaps include junk by default.
4. **Split by content type** if you have more than a few hundred URLs.
5. **Submit it in Search Console** and confirm it is read without errors.
6. **Open the Pages report** and calculate your indexed-to-submitted ratio.
7. **Record the counts for "Crawled - not indexed" and "Discovered - not indexed".** Compare
   against the numbers you wrote down in Section 2.
8. **Pick three "Crawled - not indexed" pages and read them honestly.** These are quality
   rejections.
9. **Pick three "Discovered - not indexed" pages and check their internal links.** These are
   usually orphans or buried too deep.
10. **Install IndexNow** if your CMS supports it.

## Capstone step

Your sitemap contains only canonical, indexable, 200-status URLs, split by content type. You
know your indexed-to-submitted ratio and have separated the quality rejections from the
crawl-reach problems, with three examples of each identified for fixing.

## Key takeaways

- Sitemaps aid discovery and are not a ranking factor. Their real value is diagnostic.
- Include only 200-status, canonical, indexable URLs you actually want indexed. Junk in the
  sitemap trains Google to distrust it.
- Above 85% indexed-to-submitted is healthy. Split sitemaps by content type so the report
  localizes the problem for you.
- IndexNow covers Bing, Yandex and Naver but not Google. Do it anyway, because Bing powers
  ChatGPT search.

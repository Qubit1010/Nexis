# Technical SEO - Section 21: Crawl Budget and robots.txt

*One file, four bytes of syntax, and the ability to remove your entire site from Google by accident.*

**Bottom line:** robots.txt controls what bots may request. It is the highest-risk small file
on your site: a 5xx response there causes Googlebot to stop crawling everything. Crawl budget,
meanwhile, is the thing beginners worry about most and matters least until roughly 10,000
pages.

---

## The technical SEO priority pyramid

Tier 3 works in this order, and the order is not negotiable. A failure at a lower layer
invalidates the work above it.

1. **Crawlability and indexation** (Sections 21 to 22). The most common source of silent
   traffic loss.
2. **Canonicals and duplication** (Section 23).
3. **Redirects and status codes** (Section 24).
4. **Architecture** (Section 25).
5. **Rendering** (Section 26).
6. **Performance** (Sections 27 to 28).
7. **Structured data** (Section 30).

Fixing schema on a site whose pages are not indexed is polishing something invisible.

## robots.txt: what it does and does not do

**It requests that compliant bots not crawl certain paths.** That is all.

**It is not access control.** It is voluntary. A bot can ignore it, and many do.

**It does not remove pages from the index.** This is the most consequential
misunderstanding in technical SEO, and it deserves its own section below.

**It must live at the root:** `example.com/robots.txt`. Nowhere else.

## The two rules that break sites

**Rule one: robots.txt must return 200 OK.**

If it returns a 5xx server error, Googlebot interprets that as "I cannot determine what I am
allowed to crawl" and **stops crawling the site entirely** until it resolves. A 404 is fine and
is treated as "crawl everything". A 500 is not. `[confirmed]`

Check it. Then check it again after any server change.

**Rule two: never block CSS or JavaScript.**

Google needs both to render the page as a user sees it. Blocking them means Google evaluates a
broken version of your site. This was standard advice in 2010 and is now actively harmful.
`[practitioner]`

## The disallow plus noindex conflict

The single most common self-inflicted indexation bug, and it is worth understanding precisely.

You want a page out of the index, so you do both: `Disallow` it in robots.txt and add a
`noindex` tag. That feels thorough. It is broken.

**Disallowed means Google never fetches the page. Never fetching means never seeing the
`noindex` tag.** If the URL is linked from anywhere, Google can keep it indexed, showing the
URL with no description, indefinitely. `[confirmed]`

**Pick one:**

- **To remove from the index:** allow crawling, use `noindex`. Google must be able to fetch the
  page to read the instruction.
- **To save crawl budget on pages you do not care about:** `Disallow`, and accept they might
  appear as bare URLs if linked.

For most sites, most of the time, the answer is `noindex` and leave robots.txt alone.

## AI crawler directives

New in the last two years and now a deliberate decision rather than a default.

The critical distinction, covered fully in Section 40: **training crawlers and search crawlers
are different bots.** Blocking indiscriminately opts you out of AI answers while trying to opt
out of training.

A reasonable 2026 default:

```
User-agent: GPTBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
```

Block the training bots, allow the retrieval bots that send referrals. Note that
**`anthropic-ai` is a deprecated legacy agent** and including it in 2026 configurations
produces broken instructions. `[practitioner]`

Remember rule one: robots.txt is voluntary. Real enforcement requires WAF or server-level
rules, which are evaluated before robots.txt is even read. Section 40 covers that.

## Crawl budget: mostly not your problem

Crawl budget is the number of URLs a bot will fetch from your site in a given window. It is
determined by crawl rate limit (how fast your server responds without strain) and crawl demand
(how much Google wants your content).

**It becomes a genuine constraint above roughly 10,000 to 50,000 pages.** `[practitioner]`

Below that, if pages are not being crawled, the cause is almost always architecture, internal
linking, or quality, not budget. Optimizing crawl budget on a 200-page site is a way of feeling
technical while achieving nothing.

**When it does matter**, the things that waste it:

- Faceted navigation generating infinite URL combinations
- Session IDs and tracking parameters creating unique URLs for identical content
- Endless pagination
- Large numbers of low-value auto-generated pages
- Slow server responses reducing the rate limit
- Redirect chains, since each hop costs a fetch

## Reading the signals

In Search Console, **Settings, Crawl stats** shows requests over time, average response time,
and what Googlebot spent its time fetching. Worth knowing it exists even if you rarely need it.

The useful reads:

- **Response time trending up** means your server is throttling the crawl rate.
- **Most requests going to non-HTML resources** means budget is being consumed by images or
  scripts.
- **Large numbers of 404s or redirects in the crawl** means wasted fetches.

> **Why this matters:** this is the layer where problems are invisible from the front end. A
> site can look perfect, load fast, and read well, while a single line in robots.txt keeps a
> third of it out of the index. Nobody notices until traffic that never arrived is finally
> investigated.

## Do this now

1. **Load `yourdomain.com/robots.txt` in a browser.** Confirm it returns content and a 200.
2. **Check for `Disallow: /`.** More sites than you would believe are blocking themselves,
   usually left over from a staging environment.
3. **Confirm CSS and JS are not blocked.**
4. **Look for any URL that is both disallowed and `noindex`.** Fix by picking one.
5. **Add your sitemap reference** if it is missing.
6. **Add the AI crawler block** above, adjusted to your preference. Decide deliberately whether
   you want to be in AI answers.
7. **Test in Search Console's robots.txt report** to confirm Google reads it as you intend.
8. **Open Settings, Crawl stats.** Note total requests, average response time, and any spike in
   404s.
9. **Count your indexable pages.** Under 10,000, write "crawl budget is not my problem" and
   move on to Section 22.

## Capstone step

Your robots.txt returns 200, blocks nothing it should not, contains no disallow-plus-noindex
conflicts, references your sitemap, and states a deliberate AI crawler policy. You know whether
crawl budget is a real constraint for your site or a distraction.

## Key takeaways

- robots.txt returning a 5xx stops Googlebot crawling your entire site. It is the highest-risk
  small file you own.
- Disallow plus noindex is broken: disallowed means Google never reads the noindex, so the URL
  can stay indexed with no content. Pick one.
- Never block CSS or JavaScript. Google needs both to render what a user sees.
- Crawl budget only binds above roughly 10,000 pages. Below that, uncrawled pages are an
  architecture, linking, or quality problem.

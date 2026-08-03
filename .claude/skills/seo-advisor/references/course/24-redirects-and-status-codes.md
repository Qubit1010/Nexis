# Technical SEO - Section 24: Redirects, Status Codes, and Migrations

*The one area where a mistake made in an afternoon can cost a year of traffic.*

**Bottom line:** Redirects preserve the value of URLs you retire. Chains leak signal and add
100 to 500ms of latency, and Googlebot may abandon chains beyond five hops. Migrations are
where sites die, and they die from unmapped URLs rather than from anything exotic.

---

## Status codes that matter

| Code | Meaning | Use it for |
|---|---|---|
| **200** | OK | Everything that should be indexed |
| **301** | Moved permanently | Any permanent URL change. Passes link equity |
| **302** | Found, temporary | Genuinely temporary changes only |
| **304** | Not modified | Caching. Server-level, rarely your concern |
| **404** | Not found | Content that is gone with no replacement |
| **410** | Gone | Content permanently removed, deliberately |
| **5xx** | Server error | Never intentional. Recall from Section 21 what a 5xx on robots.txt does |

**301 versus 302.** Use 301 for anything permanent. A 302 signals "keep the old URL indexed,
this is temporary", so ranking signals stay with the old URL. People use 302 by accident far
more often than deliberately, usually because a plugin or framework defaults to it.

**404 versus 410.** A 404 says "not found", and Google will keep re-checking for a while. A
410 says "deliberately gone", which drops the URL from the index faster. When you have removed
something on purpose and nothing replaces it, 410 is the honest answer. `[practitioner]`

**Soft 404** is a page returning 200 while looking empty or error-like. Google flags these
because they waste crawl budget and clutter the index. An empty search results page or a
"product unavailable" page returning 200 is the usual culprit.

## Chains and loops

**A chain** is A to B to C. Each hop costs.

- **100 to 500ms of added latency** per chain, which feeds directly into the Core Web Vitals
  you will measure in Section 27
- Some signal loss at each hop
- **Googlebot may abandon chains longer than five hops entirely**, meaning the destination
  never gets crawled

`[practitioner]`

**A loop** is A to B to A. The page becomes permanently unreachable. Always a bug, always
urgent.

**The fix for a chain is to flatten it.** Point A directly at C. Then update internal links to
point at C rather than at A, so the redirect is a fallback for external links rather than a
routine internal hop.

Chains accumulate silently over years of small changes. Nobody creates a five-hop chain
deliberately. It is five people each making one reasonable change.

## Redirect rules

**Redirect to the closest equivalent page.** Not the homepage. A redirect to an irrelevant page
is treated as a soft 404, and you lose the signal you were trying to preserve. `[practitioner]`

**Keep redirects in place indefinitely.** External links and bookmarks point at the old URL
forever. Removing a redirect two years later breaks them. Redirects are cheap; keep them.

**Update internal links to final destinations.** Never rely on a redirect for your own
navigation.

**One redirect, not two.** Check after implementing that you created a single hop.

**Do not redirect en masse to the homepage during a migration.** It is the classic way to lose
everything at once.

## Migrations: the checklist

Migrations are where sites lose the most traffic in the shortest time. Nearly always because
URLs were not mapped.

**Before:**

1. **Crawl the existing site completely.** Every URL, with its status code. Screaming Frog free
   tier for up to 500, paid or another tool beyond that.
2. **Export Search Console performance data**, all queries and pages, for the last 16 months.
   You cannot get this back later, and you will want the before picture.
3. **Export your backlink profile.** Which URLs have external links matters enormously for
   mapping priority.
4. **Build a URL map.** Every old URL to exactly one new URL. This is the deliverable. Pages
   with backlinks and traffic get mapped first and checked personally.
5. **Decide what is genuinely being retired**, and choose 410 or a redirect to the nearest
   relevant page for each.
6. **Set up the new site on staging with `noindex`**, and confirm the `noindex` is removed at
   launch. Forgetting this is a common and spectacular failure.

**At launch:**

7. Implement every redirect, one hop each.
8. Remove staging `noindex` and staging robots.txt blocks. **Check this first, before anything
   else.**
9. Update and resubmit the sitemap.
10. Verify the new property in Search Console if the domain changed, and use the Change of
    Address tool.

**After:**

11. **Crawl the new site immediately.** Look for 404s, chains, and loops.
12. **Watch Search Console indexing daily for two weeks.**
13. **Expect a dip.** A temporary drop is normal even on a clean migration. Recovery typically
    takes weeks.
14. **Compare against your exported baseline** at 4 and 8 weeks, by page and by query, not just
    in total.

## The three failures that cause most migration disasters

1. **Staging `noindex` left in production.** The whole site vanishes. Check first, always.
2. **Everything redirected to the homepage.** Signals lost wholesale.
3. **No URL map**, so redirects were improvised and a long tail of pages was simply dropped.

All three are avoidable with an afternoon of preparation.

> **Why this matters:** almost everything in SEO is slow and reversible. This is neither. A bad
> redirect implementation can undo years of work in a day, and the damage often is not visible
> for a week, by which time the cause is harder to trace.

## Do this now

1. **Crawl your site** and export all non-200 status codes.
2. **Find every redirect chain.** Screaming Frog reports these directly. Flatten each to one
   hop.
3. **Find any redirect loops.** Fix immediately.
4. **Find internal links pointing at redirects** and repoint them at final URLs.
5. **Check for 302s that should be 301s.** Look especially at anything your CMS or framework
   generated.
6. **Look for soft 404s** in Search Console's Pages report. Make them return a real 404 or 410,
   or give them content.
7. **Check your 404 page** actually returns a 404 status, not a 200. Test with a made-up URL
   and a header checker.
8. **If a migration is anywhere in your future, build the URL map now**, before anything else
   is decided.

## Capstone step

Your capstone site has no redirect chains or loops, internal links point at final destinations,
temporary redirects that should be permanent are corrected, and your 404 page returns a genuine
404.

## Key takeaways

- 301 for permanent, 302 only for genuinely temporary, 410 for deliberately removed content.
- Chains add 100 to 500ms and leak signal, and Googlebot may abandon them beyond five hops.
  Flatten to one, then repoint internal links.
- Redirect to the closest relevant page. Redirecting to the homepage is treated as a soft 404.
- Migrations fail from unmapped URLs, staging noindex left in production, and blanket homepage
  redirects. Build the URL map before anything else.

# On-Page & Content - Section 16: Internal Linking

*The only authority signal you fully control, and the one most sites leave sitting unused.*

**Bottom line:** Internal links do three things: they distribute authority, they tell search
engines what a page is about through anchor text, and they make the cluster structure from
Section 15 legible. Bidirectional pillar linking is reported to raise AI citation probability
2.7x. Unlike backlinks, none of this requires anyone else's cooperation.

---

## What internal links do

**Distribute authority.** Pages that receive links, internally and externally, accumulate
authority and pass some of it on. Your homepage usually holds the most. Every internal link is
a decision about where that flows.

**Describe the target.** Anchor text is one of the clearest statements you can make about what
a page covers. This is why "click here" is a wasted link.

**Establish relationships.** The pillar-to-cluster structure only exists to a machine if the
links exist.

**Enable discovery.** From Section 2, a page with no internal links is effectively invisible.
Crawlers find pages by following links.

## The working thresholds

| Guideline | Value | Tier |
|---|---|---|
| Internal links per 2,000 words | **8 to 15** | `[practitioner]` |
| Bidirectional pillar-cluster linking | reported **2.7x** AI citation probability | `[practitioner]` |
| Clicks from homepage to any commercial page | **3 maximum** | `[practitioner]` |
| Orphan pages | **zero** | |

Treat 8 to 15 as a sanity range, not a quota. Links should exist because they are useful.

## Anchor text

**Be specific and descriptive.** The anchor should tell you where you are going without the
surrounding sentence.

- Bad: "click here", "read more", "this article", "learn more"
- Better: "how crawl budget works", "the 60-second difficulty read"

**Vary it naturally.** Ten links to the same page with identical exact-match anchors reads as
manipulation. Different pages will naturally describe the target differently, which is fine
and correct.

**Do not over-optimize.** Internal anchors are a signal you fully control, which means
aggressive exact-match anchoring is easy to detect. Write what the link is genuinely about.

**Anchor text builds the semantic map.** Consistent, topically specific anchors are how a
retrieval system understands that a set of pages belongs together. `[practitioner]`

## Where links should come from

**Contextual links inside body content are the strongest.** A link in a sentence, where the
surrounding text explains why the target is relevant, carries more weight than a link in a
sidebar or footer.

**Navigation links are powerful but blunt.** Everything in the main nav is linked from every
page. That is why Section 13 argues for keeping the nav small.

**Footer links are weak.** Sitewide, low context, largely discounted. A footer stuffed with
keyword-anchored links is a recognizable pattern and not a good one.

**Related-posts modules** are fine but automated, so they tend to be topically loose. They do
not replace deliberate contextual linking.

## Building the cluster links

From your Section 15 link map:

1. **Pillar links down to every cluster page.** In context, where the pillar summarizes that
   sub-topic. A block of fifteen links at the bottom is weaker than fifteen links placed where
   each is relevant.
2. **Every cluster page links back up to the pillar.** Usually early, often in the opening
   context.
3. **Cluster pages link sideways** where genuinely relevant. Do not force a complete graph.
4. **Your most important commercial page gets links from the highest-authority pages** you
   have. Look at which of your pages have the most external links or the most traffic, and
   link from those.

## Finding what is missing

**Orphan pages.** Crawl the site with Screaming Frog's free tier, up to 500 URLs, and check
the orphan report. Or cross-reference indexed URLs in Search Console against your crawl. Every
orphan either gets a link or gets removed.

**Under-linked important pages.** For each page in your top 10 priorities, count internal
links pointing at it. If your most commercially important page has two internal links and a
2019 blog post has thirty, your authority is flowing to the wrong place.

**Missed opportunities.** Search `site:yourdomain.com "topic phrase"` to find every page
mentioning a topic. Any of those pages that mentions the topic without linking to your page
about it is a missing link. This is the fastest way to find dozens of real opportunities.

**Broken internal links.** Any 404 from an internal link wastes authority entirely. Screaming
Frog reports these.

**Links through redirects.** From Section 13, an internal link pointing at a URL that 301s
somewhere else leaks a little signal and adds latency. Point internal links at final URLs.

## Common mistakes

- **Linking everything to the homepage.** It already has the most authority. It does not need
  yours.
- **The same link repeated in every paragraph.** Once per page, in the most relevant place.
- **Only linking to new content.** Older pages that already have authority are often the
  better link sources.
- **No links out of high-traffic pages.** If a page gets traffic and links nowhere useful, that
  attention dead-ends.

> **Why this matters:** backlinks require somebody else to decide you are worth linking to.
> Internal links require nothing but a decision. It is the largest lever most sites have never
> pulled, and the entire cluster structure from Section 15 is inert without it.

## Do this now

1. **Crawl your site** with Screaming Frog free tier, or list your URLs manually if the site is
   small.
2. **Find every orphan page.** Link it from somewhere relevant, or remove it.
3. **Count internal links to your top 10 priority pages.** Note any that are under-linked
   relative to their importance.
4. **Run the `site:` search** for your three most important topics. Find pages that mention the
   topic without linking to your page about it. Add those links. Expect to find more than you
   thought.
5. **Build the cluster links** from your Section 15 map: pillar down to every cluster, every
   cluster back up, placed contextually rather than in a block.
6. **Fix every internal link pointing at a redirect or a 404.**
7. **Audit your anchor text.** Replace every "click here" and "read more" with something
   descriptive.
8. **Check the 3-click rule.** Can you reach every commercial page within three clicks of the
   homepage?

## Capstone step

Your cluster is now wired: pillar and cluster pages linked bidirectionally in context, orphans
resolved, priority pages properly linked, anchors descriptive, and no internal links pointing
at redirects or 404s. The structure from Section 15 is now legible to machines.

## Key takeaways

- Internal linking is the only authority signal that needs nobody's permission, and it is the
  largest unused lever on most sites.
- Bidirectional pillar-cluster linking is reported at 2.7x AI citation probability. Roughly 8
  to 15 contextual links per 2,000 words is a sane range.
- Anchor text should describe the destination specifically. "Click here" wastes the clearest
  statement you can make about a page.
- The `site:` search for a topic finds pages that mention it without linking to your page about
  it. That single technique usually surfaces dozens of real opportunities.

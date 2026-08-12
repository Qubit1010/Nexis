# Clusters and Internal Links

Two areas that are really one: a topic cluster is an internal linking structure with a
content plan attached. Sizing comes from `course/15`, linking from `course/16`.

---

## Building a cluster

Input is a cluster from `seo-foundation`'s Keyword Map. This skill does not choose the
topic or do the keyword work - if there is no map, run `seo-foundation` first.

**The shape:**

| Element | Size | Source |
|---|---|---|
| Pillar page | **2,500-4,000 words** | `course/15` `[s288, s128]` |
| Cluster pages | **8-15**, each owning exactly one sub-intent | `course/15` |
| Linking | **Bidirectional** - pillar to every cluster, every cluster back | `course/15` `[s288]` |

Reported at **2.7x** AI citation probability for bidirectional linking `[s288]`
`[practitioner, single vendor]`. Directional. Do not quote the multiple to a client as a
measured fact.

**Procedure:**

1. Pull every keyword in the cluster from the Keyword Map. Do not re-derive it.
2. Identify the pillar - the page that covers the topic broadly. Existing or planned.
3. List the cluster pages, one sub-intent each, marked `exists and fine` / `exists and
   needs work` / `needs creating`.
4. **Completeness test:** list every question a curious reader would still have. Each needs
   a home in the cluster, or the cluster is not complete.
5. Write out the link map explicitly - which page links to which, in both directions.
6. Order by priority with real dates.
7. **Publish or fix the pillar first.**

**The failure mode, and it is the common one:** starting four clusters and finishing none.
Four half-built clusters produce less than one complete one, because incompleteness is the
thing being penalized. Sites with 5+ interconnected pages on a topic are reported 3.2x more
likely to be cited by AI systems `[s110]` `[practitioner]`; four disconnected pages get
none of that.

Topic choice, when there is a choice: genuine first-hand expertise, highest commercial
value, some existing content to build on, and competition that is not entirely large
brands. All four, ideally.

---

## Internal linking

```bash
python scripts/links.py --site https://acme.com --max-pages 100 \
  --priority-pages pages.txt --opportunities targets.json --out links.json
```

`targets.json` is `[{"url": "...", "phrase": "..."}]` - the page that owns a topic, and the
phrase that should trigger a link to it.

**Work the output in this order.** It is ordered by yield, not by how satisfying each is:

1. **Opportunities.** Pages that discuss a topic and do not link to the page that owns it.
   Usually dozens, each a one-line fix, and collectively the largest available gain.
2. **Orphans.** Zero inbound body links. Link them or remove them; there is no third option.
3. **Click depth.** Anything commercial more than **3 clicks** from home `[s299, s209]`.
4. **Anchors.** "click here", "read more", and any anchor repeated at scale.
5. **Broken and redirected targets.** Internal links should point at the final URL directly,
   not through a redirect.

### Why opportunity discovery runs locally

`course/16`'s lab prescribes `site:yourdomain.com "topic phrase"`. `links.py` searches the
crawled corpus instead. That is free, sees every page rather than only what Google chose to
index, and - the part the operator cannot do - distinguishes "mentions the topic" from
"already links to it", so the output is a work list rather than a reading list.

### The density number, and how it gets misused

**8 to 15 internal links per 2,000 words** `[s128]`. `course/16` says explicitly to treat
this as a sanity range, not a quota, and the misuse is predictable: hitting 12 by adding a
related-posts block satisfies the number and none of the intent.

Link source strength, strongest first:

1. **Contextual body links** - by a wide margin
2. **Navigation** - powerful but blunt, and identical on every page
3. **Related-post modules** - weak
4. **Footer** - largely discounted

So a pillar links down to its clusters **in context**, in the prose, not as a block of 15
at the bottom. And the most important commercial page should collect links from the
highest-authority pages on the site, which usually are not the ones currently linking to it.

### Anchors

Specific and descriptive. Never "click here", "read more", "learn more", "this article".

Vary them naturally. Exact-match anchor text repeated at scale reads as manipulation, and
`links.py` flags any anchor used for the same target more than three times.

---

## Where this stops

Cannibalization detection and the keyword-to-URL mapping belong to `seo-foundation` -
this skill consumes that map and reports conflicts it finds, but does not rebuild it.

External links, digital PR and anything about earning links from other domains is off-page
and out of scope.

# Secondary platforms — X, Reddit, Pinterest, Threads, Snapchat

**Read the coverage column before answering anything from this file.** These five were
researched at deliberately lighter depth, and the depth is very uneven between them. Two of
them this corpus effectively cannot answer.

| Platform | Sources | `[P*]` | Can this skill advise? |
|---|---|---|---|
| Pinterest | 9 | 8 | **Yes**, on distribution basics. Docs skew to ads and partnerships |
| Snapchat | 7 | 7 | **Yes**, on ranking. Unusually good first-party ranking docs |
| X / Twitter | 18 | 1 | **On research, yes; on current ranking, no.** Strong audit literature, no useful first-party doc |
| Reddit | 5 | **0** | **Barely.** General principles only |
| Threads | 1 | 0 | **No.** Say so |
| Bluesky | 0 | 0 | **No coverage at all** |

All `[P*]` retrieved **2026-08-21**.

---

## Pinterest

**What it is for:** intent-driven discovery with a long content life. Closer to a visual search
engine than a social feed. Genuinely strong for retail, home, food, weddings, and anything
planned in advance.

**How it ranks `[P*]`:** Pinterest documents Pin performance and distribution directly `[P*]`
[s324], and publishes an account of its AI use `[P*]` [s323]. Note that **6 of its 8 first-party
docs in this corpus are advertising and paid-partnership material** `[P*]`
[s304][s305][s306][s307][s308][s309], not organic ranking. That is a real limit on how
confidently organic questions can be answered.

**Fails when:** the product is not visual, or the purchase is not planned. Also fails when a
client expects social-style engagement; this platform is closer to search.

**Who executes:** `carousel` and `canvas-design` for assets, `content-production` for copy.

---

## Snapchat

**What it is for:** narrow. Young audiences, consumer brands, AR and Lenses. Rarely the right
answer for NexusPoint's ICP or its clients.

**How it ranks `[P*]`:** unusually well documented for a platform this size. Snapchat publishes
separate ranking explanations for **Spotlight** `[P*]` [s283][s302], **Discover** `[P*]` [s325],
and **Lenses** `[P*]` [s327], plus a personalisation overview `[P*]` [s326][s328].

**The useful point:** three separately documented ranking surfaces means "how does Snapchat rank"
has three answers. Ask which surface before answering.

**Fails when:** B2B, older demographics, or any brand without a reason to be where the audience
is. **Usually recommend against it**, and the strength of the docs is not a reason to advise
using the platform.

---

## X / Twitter

**The inverted case: strong research, no usable first-party ranking documentation.** The only
first-party doc retrieved is a media-literacy policy `[P*]` [s293], which says nothing about
ranking.

**What IS strong is the audit literature**, and it is confirmed-tier. Crowdsourced audits of the
recommender `[C]` [s18][s38], algorithmic curation reducing link exposure and reshaping timelines
`[C]` [s37], exposure-bias evaluation `[C]` [s40][s44], and neutral-bot probes `[C]` [s43]. X is
the most-audited platform in this corpus, so **general claims about how ranked feeds reallocate
exposure are best evidenced here**.

**For ranking internals, cross-cite rather than re-derive.**
`awesome-claude-skills/twitter-algorithm-optimizer` documents Real-graph, SimClusters, TwHIN and
Tweepcred from Twitter's own open-sourced algorithm release. It is vendored and unregistered as
a skill, so it will not surface on its own. Point at it explicitly.

**Note the age problem:** the open-sourced release and much of the audit literature predate the
platform's recent changes. Treat internals as historical unless checked live.

**Fails when:** the client needs predictable reach, or brand-safety tolerance is low.

---

## Reddit

**Zero first-party documentation in this corpus.** What exists is one confirmed audit of
algorithmic curation on **r/popular**, finding that recent comment activity helps a post stay
in the trending feed longer, and that the feed selectively allocates visibility rather than
reflecting submissions chronologically `[C]` [s11][s16][s25].

That is a real finding about **one feed** and it is close to everything this corpus knows.

**What to do:** answer only at the level of "ranked feeds reallocate exposure and comment
recency extends visibility" `[C]` [s11]. For subreddit norms, self-promotion rules, moderation
and community tactics, route to `marketing-skills/community-marketing` and be explicit that it
is generic rather than research-backed.

**The standing warning:** Reddit punishes marketing that reads as marketing, harder than any
other platform here, and this corpus cannot tell you where each subreddit's line sits. Do not
improvise it on a client's behalf.

---

## Threads

**One source. This corpus cannot answer questions about Threads.**

Say that plainly. **Do not infer from Instagram**: shared ownership is not shared ranking, and
`content-advisor`'s own social-text spec explicitly disclaims Threads for the same reason.

If a client genuinely needs a Threads answer, run a live pass via `notebook-live-query.md` and
label the result as un-corpus'd.

---

## Bluesky

**No coverage.** Not researched. Say so rather than reasoning from first principles about
decentralised feeds.

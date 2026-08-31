# Social text — threads, LinkedIn posts, X posts

Three formats sharing one mechanic: **the reader sees one truncated line and decides from it.**
Everything else about these formats is downstream of that.

Tiers per `00-index.md`.

**Boundary: how a post is *formatted* for a platform is `copy-conversion`'s**
(`platform-formatting.md`, its `format` mode) - field structure, the pre-truncation line,
character limits, the topic-shape intersection rule. This file covers what the *format* is as a
content asset. **Cross-cite it, do not restate it.**

---

## The evidence that applies to all three

**Emotion and arousal predict sharing; information suppresses it.** Two independent field
studies across video ads, 11 emotions and 60+ characteristics found information-focused content
had a **significantly negative** effect on sharing, except in risky contexts. High-arousal
positive emotions - inspiration, amusement - and surprise increased sharing; sadness decreased
it unless paired with hope `[C]`.

**"Engagement" is not one thing.** A systematic review finds it operationalised heterogeneously
across studies and platforms `[C]` [s1], which is why vendor benchmark tables disagree with each
other and why quoting one at a client is a liability.

**There is no single engagement-rate formula** `[C]` [s1]. Denominators vary - followers, reach,
impressions, views - and different denominators give different answers. Always state which.

**Vividness and interactivity correlate with engagement**, but findings are mixed across
platforms and metrics `[C]`. Correlational, not causal.

**Cascade comparisons need size matching.** Apparent differences in how content spreads
between accounts or platforms often reflect cascade size rather than mechanism, and diminish or
reverse once matched `[C]` [s14][s16]. Relevant every time a client says a competitor's post
"went viral".

---

## LinkedIn posts

**What it is for.** Reaching a professional audience without an intermediary. The highest-trust
text surface most B2B clients have.

**Structure.** First line carries the whole point. Body in one idea, chosen because it
demonstrates something the writer can prove: a repeatable framework built from real work
(Pierre Herubel, Lincoln Murphy), a metric from their own operation (Austin Rief, Brigitta
Ruha), or a specific lesson from a named mistake (Justin Welsh). `[K]` [s378][s358][s328].
Readers scan a post's shape - the first line, then the bullet points - before deciding whether
to invest in reading the rest, rather than reading it linearly top to bottom. `[K]` [s378]. Close
with one action or a genuine question. `[K]` [s354]

**The hook.** The pre-truncation line. It is the only thing most people see, and the truncation
point varies by device and placement - which is why it is verified, not remembered. See
`copy-conversion/references/platform-formatting.md`. Beyond surviving truncation, named creators
build the opening line as a pattern interrupt: a curiosity gap or a vulnerable admission (Dickie
Bush, Nicolas Cole), or a contrarian "what everyone gets wrong" claim (Sam Browne) - never a
scene-setting lead-in. `[K]` [s356][s354]

**Length and pacing.** Set by the idea. "Shorter is better" is an assumption that has been
tested against directly, not a finding.

**2026 optimization.** Everything commonly asserted here - optimal posting times, hashtag
counts, whether body links suppress reach - is **convention with no confirmed source** in this
corpus. See `what-not-to-do.md` Part 4. Report them as conventions if asked, never as findings,
and never quote a reach-penalty percentage.

**Distribution.** The post is the distribution. What matters is what happens in the first hour,
which is a behaviour, not a format decision.

**Fails when** the first line is a windup, or when the post is an article compressed rather than
a post written.

**Who executes it.** `content-production` for clients. `post-creator` and `content-engine` for
Aleem's own.

---

## X posts

**What it is for.** Speed and reach in a fast-decaying feed. The shortest half-life of any
format here - consistent with sharp exogenous bursts decaying fastest `[C]`.

**Structure.** One claim. That is the format.

**The hook.** The post is the hook. There is no below-the-fold.

**2026 optimization.** Thinnest evidence base of the three. `copy-conversion`'s own file calls X
its thinnest coverage with no confirmed source, and this corpus does not improve on that.
Verify conventions live rather than taking them from any file.

**Fails when** it is a LinkedIn post pasted over.

**Who executes it.** `content-production`.

---

## Threads

**What it is for.** An argument too long for one post and too short for an article, in a feed.

**Structure.** Post 1 carries the whole claim **standalone**. Post 2 gives the stake. Middle
posts carry one idea each, paced to a single narrative or collaborative sequence - repurposing
long-form media into one standalone lesson per post (Jay Clouse), or a high-volume run of short,
scannable posts on one theme (Warby Parker). `[K]` [s301][s305]. Final post resolves and closes
on an open-ended question, or a "soft handoff" to a collaborator's audience - both aimed at
generating comment activity in the first hour rather than summarizing. `[K]` [s301][s356]

**The rule that decides whether a thread works:** **no post exists only to set up the next
one.** A thread built as a teaser dies at post 1, because post 1 is the only one most people
see. Every post has to be worth reading on its own while still advancing the argument.

**The hook.** Post 1, and it is doing two jobs: standing alone and earning the second post.

**Length and pacing.** As many posts as the argument has ideas. Padding to hit a number is
visible.

**Disambiguation:** "Threads" in this repo means a **multi-post sequence on X or LinkedIn**.
Meta's *Threads* is a different platform with different specifications. If a client means the
platform, treat it as its own surface and verify specs live - this corpus does not cover it.

**Fails when** post 1 is a hook with no content, when the middle is filler, or when it should
have been an article.

**Who executes it.** `content-production`.

---

## What generalises across all three

1. **The truncated first line is the format.** Everything else is downstream.
2. **Front-load the point.** The one thing that generalises across every platform.
3. **Write simply.** Costs nothing, holds everywhere.
4. **Do not repost one text across platforms.** Repurposing is fine; identical posting is not.
5. **Most per-platform "rules" are conventions.** Hashtags, posting times, link suppression,
   emoji, optimal length. State them as conventions or leave them out.
6. **State the denominator** whenever an engagement number is quoted `[C]` [s1].

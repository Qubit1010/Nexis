# LinkedIn

**Corpus depth: deepest of any platform here, 17 first-party documents**, including LinkedIn's
own engineering write-ups on feed ranking and dwell time. When someone asks how the LinkedIn
algorithm works, this is the one platform where a substantial first-party answer exists.
All `[P*]` retrieved **2026-08-21**.

---

## 1. What it is for

Professional and B2B audiences, and the platform where an **individual** account substantially
outperforms a brand account. For NexusPoint's agency-first ICP it is the primary channel.

Not for: consumer retail, visual-first brands, anyone whose buyer is not at work when deciding.

## 2. How it ranks — `[P*]`

**Two-stage retrieval then ranking.** LinkedIn's engineering blog describes tens of thousands of
candidate posts per member visit, reduced by "a first-pass, candidate generation layer
[applying] an efficient and lightweight ranking algorithm to identify the top candidate
updates", then ranked more expensively `[P*]` [s288]. This is the architecture; everything
below sits inside it.

**Dwell time is a documented ranking input, first-party.** LinkedIn published a dedicated
engineering post on how member time-distribution on the feed was used "to improve the algorithms
that rank content" `[P*]` [s288]. **The mechanism is first-party; the multiples are not.**
`marketing-advisor`'s "13x" figure is practitioner-tier and has no traceable source. Cite the
mechanism, refuse the multiple.

**The ranker was rebuilt on LLMs.** LinkedIn describes "a new advanced ranking system, powered
by LLMs and GPUs, that better understands what a post is actually about and how it relates to a
member's evolving interests and career goals", serving 1.3 billion members `[P*]` [s282].
Practitioner sources call this system "360Brew" `[P]`; LinkedIn's own posts in this corpus do
not use that name, so attribute it as practitioner vocabulary.

**Both sides are optimised.** LinkedIn runs explicit **creator-side** optimisation alongside
viewer-side relevance, describing members as occupying two roles and receiving feedback through
"viral actions by liking and commenting" `[P*]` [s320], plus community-focused feed optimisation
`[P*]` [s318]. Practically: the feed is not purely a viewer-relevance auction, and distribution
to *some* audience is partly a creator-retention objective.

Further first-party detail: `[P*]` [s289][s319] (relevance models), [s292] (knowledge graph),
[s321] (FollowFeed), [s322] (how content appearance is tested), [s299] (LinkedIn's own
algorithm best-practice guide), [s298] (LinkedIn's definition of engagement rate).

## 3. What changed — dated

**12 March 2026, LinkedIn newsroom** `[P*]` [s284]. Four stated changes, quoted:

- **"Smarter content ranking using Generative Recommenders and LLMs"**: more advanced models
  that "better understand what posts are about and how members' interests change over time".
- **"Action against automated comments and inauthentic engagement"**: explicitly "working to
  make engagement pods ineffective and curb comment automation or third party tools that create
  fake conversations". **This is the single most decision-relevant line in the corpus** and it
  is why the pods entry in `what-not-to-do.md` is answered rather than open.
- **"Less generic content and engagement bait"**: "reducing recycled and click-driven posts…
  We want the Feed to be relevant to your interests, not a popularity contest."
- **Interest Picker at sign-up** for new-member personalisation.

Read all four as **stated intent**, not measured outcome.

## 4. Formats that win

**This is where the corpus is weakest and the industry is loudest.** Practitioner sources
converge on document/PDF carousels outperforming, commonly quoting ~6.6% engagement against ~2%
for text `[P]`, on the mechanism that carousels require swipes and so accumulate dwell time.

The mechanism is consistent with LinkedIn's own dwell-time post `[P*]` [s288]. **The numbers are
not first-party and not confirmed.** Note that `marketing-advisor` states these as fact; this
skill does not. Give the direction, attribute the number, never assert it.

## 5. Cadence

**No first-party statement exists on posting frequency.** Every number in circulation is
practitioner convention. The general evidence on frequency and audience growth is weaker and
more conditional than the industry implies (see `growth-playbooks.md`).

Aleem's own committed cadence is **2x/week**, set in `context/current-priorities.md` after
3x/week failed twice. Do not advise him upward without a reason that survives that history.

## 6. Growth mechanics

- **Commenting is the lever that adds reach without adding posts.** This is the documented
  rationale for the `linkedin-commenter` skill and it follows from creator-side optimisation
  `[P*]` [s320]: participation as a viewer is a first-class role, not a side activity.
- **Personal over company page.** Widely held, practitioner-tier for the magnitude.
- **Comment *quality* over volume.** Consistent with the March 2026 anti-automation stance
  `[P*]` [s284]: automated or generic comments are a named target.
- **Reach concentration is structural**, not a personal failing. See `[C]` [s34][s56] in
  `platform-scoreboard.md`.

## 7. Fails when

- The buyer is not a professional decision-maker.
- The account is new with no network. Cold-start is genuinely hard here.
- The strategy depends on volume. LinkedIn stated it is reducing "recycled and click-driven
  posts" `[P*]` [s284].
- The plan is automation-led. Directly targeted, first-party, as of March 2026 `[P*]` [s284].

## 8. Who executes

`post-creator` and `content-engine` (Aleem's own posts), `linkedin-commenter` (the daily
commenting round), `linkedin-infographics` (single-image infographics), `content-production`
(document carousels, text posts for clients), `copy-conversion` (formatting and character
limits), `sales-playbook` (DMs and outreach copy).

**Profile optimisation:** route to `social-media-skills:profile-optimizer`. Strategy here, the
artifact there.

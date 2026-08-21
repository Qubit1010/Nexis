# What not to do — the social media kill list

Factcheck mode reads this file **first**. If the claim is here, answer from here and stop.

**The governing rule:** the honest verdict is almost always *"no traceable primary source"*,
**not** *"proven false"*. Those are different, and the difference is the whole credibility of
this skill. Say which one you mean.

**The second rule, specific to this subject:** the absence of a vendor's evidence is not the
absence of evidence. Several claims below are dismissed by practitioners as unknowable when
peer-reviewed work on them actually exists, and it usually says something more useful than
either the folklore or the dismissal. Check the corpus before saying "nobody knows".

Tags: `[C]` confirmed · `[P]` practitioner · `[P*]` first-party platform doc · `[K]` craft
(never usable for a factual claim). Indices resolve in `_research/sources.json` **on the
`index` field, not list position**.

---

## Part 1 — Claims with no traceable source

### "The best time to post is [day] at [time]"

**The tables have no traceable basis, but the underlying question does have a literature, and
it says something the tables cannot.** This is the single most-asked social media question and
the most confidently answered wrong, in both directions.

What is actually established: choosing posting time is a **causal-inference problem**, formally
distinct from predicting reach conditional on time, and estimating it properly requires a
randomised test on the account in question `[C]` [s117][s119]. The research that recommends
posting times does so **per user**, because the probability of a reaction "differs for each
user and depends on various factors, such as location, daily and weekly behavior patterns"
`[C]` [s118][s120]. Scheduling has been modelled seriously for content platforms `[C]` [s116].

So the finding is not "timing doesn't matter". It is **the optimum is personal, and a universal
table is answering a different question from the one it appears to answer**: an observational
aggregate over somebody else's accounts, presented as a causal recommendation for yours.

**Say:** "Those tables are aggregates of other people's audiences, and the research on timing
is explicit that the answer is per-account and has to be estimated causally, not read off a
chart `[C]` [s117][s118]. Your own audience-activity data in the native analytics is the only
version of that answer that applies to you. Test two windows against each other for a month if
it matters enough to know."

### "Outbound links in the post body get you penalised, so put them in the first comment"

**No traceable primary source, in either direction.** The provenance pass found no earliest
citable source for the claim at all `[P]` [s225]. No platform documents a link penalty; no
controlled test in this corpus establishes one.

It is also **internally contradictory across the sources that assert it**:
`marketing-skills/social/references/platforms.md` recommends the first-comment workaround while
`marketing-advisor/references/linkedin-playbook.md` states the workaround is itself now
penalised. Two confident, opposite, unsourced answers is the signature of folklore.

**Say:** "Nobody can point to where this started and no platform documents it. It may well be
true, and it is cheap to comply with, so treat it as a low-cost convention rather than a
finding, and never quote a percentage for it."

### "Hashtags are dead" / "use exactly N hashtags"

**Both halves are unsourced as stated**, and the specific-number version has no basis at all.
What exists: hashtags demonstrably function as a **discovery and recommendation** mechanism
`[C]` [s32], and practitioner consensus has shifted toward fewer and more relevant tags `[C]`
[s29]. What does not exist is a reach penalty per hashtag, or an optimal count.

**Say:** "Hashtags still do something, mostly categorisation and discovery `[C]` [s32]. What has
no source is the count. Anyone quoting a reach penalty for using four instead of two is
repeating a number nobody can trace."

### "You need N followers before the algorithm takes you seriously"

**No source for any threshold.** The nearest real finding runs the other way: follower count and
reach are decoupled more than the folklore assumes, and **followers do not dictate virality**
for publishers `[C]` [s55]. Influencer engagement is **non-monotonic** in follower count, with
mid-tier accounts outperforming the largest ones `[C]` [s5], which is the opposite of a
threshold story. Outcomes are also substantially luck-driven `[C]` [s53].

**Say:** "There is no threshold in any source. The research points the other way: past a point
more followers buys less engagement, not more `[C]` [s5], and follower count doesn't determine
whether something travels `[C]` [s55]."

### "Engagement pods work" / "reciprocity rings beat the algorithm"

**On LinkedIn this is now answered first-party, and the answer is no.** LinkedIn's newsroom,
dated **12 March 2026**, states it is taking "action against automated comments and inauthentic
engagement", specifically that it is "working to make engagement pods ineffective and curb
comment automation or third party tools that create fake conversations" `[P*]` [s284] (retrieved
2026-08-21).

Read that precisely. It is a **statement of intent and active work**, not a measurement of
success, and `[P*]` never establishes that something works. What it does establish is that pods
are a named target of the ranking team, which makes them a tactic being actively engineered
against on the one platform that has said so.

**No equivalent statement exists for any other platform in this corpus**, and no controlled test
of pod effectiveness exists anywhere in it.

**Say:** "On LinkedIn, don't. Their own newsroom says they are working to make pods ineffective
and to curb comment-automation tools `[P*]` [s284, Mar 2026]. That is intent rather than proof
it worked, but it does mean you would be betting a brand account against a team actively
targeting the tactic. Elsewhere there's no evidence either way, which is not the same as
permission."

---

## Part 2 — Claims that are real but routinely misstated

### "We've been shadowbanned"

**Usually a folk explanation for a real experience, and occasionally the right word.** Three
things are separately true and constantly conflated:

1. **Platforms do restrict distribution** for guideline violations, and acknowledge doing so
   even while disputing the word "shadowban" `[C]` [s29].
2. **Shadow banning is a tractable mechanism**, modelled formally as an optimisation that can
   shape a network's opinion distribution `[C]` [s33]. That paper establishes it *can* be done
   and what it would achieve. **It is not evidence any platform does it to marketing accounts.**
3. **Belief in it is widespread** and measured as a belief, not a mechanism.

**Say:** "Reduced distribution is real and platforms admit restricting rule-breaking content
`[C]` [s29]. What has no evidence is silent suppression of ordinary marketing accounts. Before
reaching for it, rule out the two boring explanations: a platform-wide ranking change, and a
drop in the signals your content used to earn."

### "Engagement rate is X%" / "saves are worth 3x a like"

**There is no single engagement-rate formula**, and that is a documented property of the
literature, not a gap in this corpus. A systematic review finds engagement measured
inconsistently across studies with **no standardised behavioural index** `[C]` [s1], and studies
routinely **aggregate likes, comments and shares into one figure** rather than analysing them
separately `[C]` [s1]. Platform metric definitions differ too, and each platform defines its own
distribution and measurement terms in its own documentation `[P*]` [s191][s192][s203] (quote
with a retrieval date; Meta revises these pages).

Which means the weighted-signal claims ("a comment is worth 5-7 likes", "saves count 3x") have
**no confirmed basis**. There is real work on what drives liking versus commenting as distinct
behaviours `[C]` [s68], and that is the honest version of the claim.

**Say:** "There's no standard formula, so two 'engagement rates' are rarely comparable `[C]`
[s1]. The weighting multiples are practitioner convention. What is supported is that liking and
commenting have different drivers `[C]` [s68], which is a reason to look at them separately,
not a reason to trust a specific ratio."

### "Organic reach is dead because the platform wants your ad money"

**The decline is real; the single-cause story is not.** Unequal exposure arises substantially
from **cumulative advantage / preferential attachment**, a structural property of networks that
produces heavy-tailed distributions with or without platform intent `[C]` [s34]. Creator
earnings show the same rich-get-richer concentration `[C]` [s26][s30], and interaction
inequality persists **across platforms** `[C]` [s56], which a per-platform monetisation policy
would not explain. Platforms do control visibility levers and monetisation incentives `[C]`
[s24], so the commercial pressure is real too. Both things are true.

**Say:** "Reach concentration is real, but it isn't only a pricing decision. Networks
concentrate attention on their own `[C]` [s34], and the same inequality shows up across
platforms with different business models `[C]` [s56]. Ad pressure makes it worse; it didn't
create it."

### "The algorithm shows people whatever keeps them scrolling"

**Directionally supported, and better evidenced than most claims here**: but do not overstate
it into a filter-bubble certainty. Independent audits confirm ranking systematically reallocates
exposure rather than reflecting the follow graph `[C]` [s18][s38][s11], and engagement-optimised
ranking is linked to amplification of divisive content `[C]` [s45]. **But** the filter-bubble
literature is genuinely mixed: a systematic review of 30 peer-reviewed studies reports
conflicting results, with cross-cutting exposure persisting under algorithmic curation in some
work `[C]` [s23], and a landmark Facebook study found individual choice mattered alongside
ranking `[C]` [s39].

**Preserve this disagreement rather than resolving it.**

---

## Part 3 — Method failures

**Never present a `[P*]` platform statement as evidence something works.** A platform describing
its own ranking is authoritative for what it *says it does* and worthless as proof of outcome.
It has a commercial interest and publishes no method. Quote it with a retrieval date.

**Never compare metrics across platforms.** Counting rules differ, a "view" is a different event
on each, and the resulting ratio is not a number.

**Never quote an effect size this corpus does not contain.** The evidence passes repeatedly
returned direction without magnitude, audits establish *that* exposure is reallocated without
publishing *how much* `[C]` [s11][s18]. Saying "the effect is established, the magnitude isn't
published" is a real answer. Inventing a percentage is not.

**Never let a population statistic become a performance claim.** "X% of adults use TikTok" is a
media-consumption fact. It is not evidence that posting on TikTok works.

**Never extrapolate between platforms.** A finding about Twitter's recommender does not transfer
to LinkedIn's. Where the corpus is thin, say it is thin.

**Never treat one account's data as a platform-wide finding**, including Aleem's own.

---

## Part 4 — Where this corpus is genuinely thin

State these out loud rather than extrapolating:

| Platform | Coverage | What to do |
|---|---|---|
| **Reddit** | 5 sources, **zero first-party docs** | Answer only at the level of "how ranked feeds work generally"; route community tactics to `marketing-skills/community-marketing` |
| **Threads** | 1 source | Say so. Do not infer from Instagram: shared ownership is not shared ranking |
| **Bluesky** | 0 sources | No coverage. Say so plainly |
| **X / Twitter** | 18 sources but only 1 first-party | The audit literature here is strong `[C]` [s18][s37][s44]; for ranking internals cross-cite `awesome-claude-skills/twitter-algorithm-optimizer`, built from the open-sourced release |
| Effect sizes generally | Direction without magnitude across most evidence passes | Report direction, refuse the number |

---

## Part 5 — The disagreement with `marketing-advisor`

`marketing-advisor` asserts firm platform numbers: a 60-68% link penalty, a 29% hashtag reach
cost, a 13x dwell-time multiple. `content-advisor` and `copy-conversion` already classify this
class of claim as unsourced convention and forbid quoting it, and **this corpus agrees with
them**: none of those figures has a traceable primary source here.

There is a second, separate problem with that skill's audit trail. Its reference files cite
`_research/sources.json` as the resolver for every `[sN]`, and **that file does not exist** , 
`_research/` holds only raw pass JSON with opaque NotebookLM UUIDs and no URL map. So those
citations currently resolve to nothing. Flagged in both playbooks, not fixed here.

**Do not silently overrule it and do not defer to it.** Name the disagreement, give the reading
from this corpus, and let the recommendation stand on the tier. Cite one skill or the other,
never both, and never present them as agreeing.

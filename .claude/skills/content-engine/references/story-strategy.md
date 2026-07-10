# Instagram Stories Strategy

Aleem posts Carousels, Reels, and Static posts, but Stories was an unexecuted stage of the
Instagram funnel. Per `platform-formats.md`, the funnel is **Reels (awareness) -> Carousels
(saves/trust) -> Stories (direct/BOFU)**. This file is the canonical Stories playbook — cadence,
formats, and promo mix. `platform-formats.md` carries only the short spec and points here.

**Honesty flag:** the marketing-advisor corpus (234 sources) has no dedicated Instagram Stories
benchmark research — Q3 of `research-synthesis.md` is Reels-only. The one real Stories-adjacent
data point is from `sales-playbook`: **Story-Reply automation converts at 40-50%** (vs. 50-60%
for comment-to-DM) [14]. Everything else below is structural best practice (funnel logic,
existing content pillars, sales-playbook DM/ask-timing mechanics), not a cited benchmark. A
dedicated Exa/NotebookLM research pass on Stories benchmarks is a valid future refresh per
`.claude/rules/research-backed-skills.md`, not a prerequisite for running this strategy.

---

## Content pillars -> Story formats

Reuses the exact 4 pillars from `content-pillars.md` — Stories is another platform lens on them,
same pattern Reel/Carousel/Standalone already follow. No new pillars.

1. **AI & Automation** (Conversion) — quick build clips (5-10s native screen recordings of
   something just shipped/automated), "would you rather" tool/approach polls, Q&A sticker ("ask
   me anything about X automation") with 2-3 follow-up answer Stories.
2. **Founder Journey** (Conversion + Awareness) — behind-the-build reactions (deal closed, hard
   day, milestone), countdown sticker for real urgency (client slots/cohort), same-day repost of
   that day's carousel/Reel/static post with a one-line personal reaction.
3. **Tech Insights** (Awareness) — one-line "hot take" text Story on a release/trend with a
   reaction/poll sticker, true-or-false quiz sticker on a trend claim.
4. **Young Builder / Learning in Public** (Awareness) — raw "this broke today / stuck on this"
   clip, "this or that" sticker comparing two tools/approaches.

Every pillar keeps the hard brand rule enforced everywhere else in this skill: **never name the
agency, never reference university/degree/student status.**

---

## Weekly cadence — daily, 1-3 slides/day

Stories decay in 24h and are cheap to produce (mostly phone-native, no editing pass), so a
near-daily light cadence sustains momentum better than infrequent bursts:

| Day | Pillar | Story content |
|-----|--------|----------------|
| Mon | Founder Journey | Week-ahead build/goal (1-2 slides) + repost Monday's feed post if one goes out |
| Tue | AI & Automation | Quick build clip or "would you rather" poll (1-2 slides) |
| Wed | Tech Insights | Hot take / quiz sticker (1 slide) + repost Wednesday's feed post |
| Thu | Young Builder | Learning-in-public / stuck-on-this clip (1-2 slides) |
| Fri | Founder Journey | Week close reflection/win, or countdown sticker if a real urgency angle exists (1-2 slides) |
| Weekend | Optional | Repost weekend content if any goes out, otherwise skip — 5 solid weekdays is enough to start |

**Non-negotiable daily habit regardless of pillar:** same-day reshare of every carousel/Reel/
static post to Stories with a one-line reaction. Near-zero effort, compounds reach on content
already made — never skip this one.

**Interaction requirement:** at least one Story per day should carry an actual interaction
mechanic (poll/quiz/Q&A/this-or-that), not just a passive announcement slide. That interaction is
what feeds people into the DM funnel below.

---

## What to promote

- **Lead magnets first** (e.g. the Claude Practical Playbook poster). Stories are the natural
  "link in bio, download free" channel — more native than a feed post, and repeatable without
  feeling repetitive since Stories don't stack in a grid the way feed posts do.
- **Real urgency/scarcity** — "closing X client slots this month" countdown stickers, same
  Hormozi/Voss framing already used in `sales-playbook`. Only run this when the scarcity is real.
- **Traffic-back-to-feed** — the same-day reshare habit above.
- **Never:** agency name, university/degree/student framing (same hard rule as every pillar).

---

## Funnel mechanics (ties into sales-playbook, no new infra needed)

- Poll/quiz/Q&A/this-or-that stickers are cheap engagement, not the sale — their job is to get
  one interaction that seeds the person into the conversation-memory system `convo.py` already
  tracks (same ask-by-6-exchange advance triggers apply once a DM thread starts).
- Story-Reply automation (40-50% reply rate [14]) is the one cited Stories-specific mechanic —
  flagged as a possible future build (a leads-to-crm-adjacent automation), not built here.
- Any DM that results from a Story interaction routes into the existing sales-playbook Live Reply
  flow already used for LinkedIn/Instagram DMs — no new conversation-handling logic required.

---

## Logging

Log Stories to the same Google Sheet "Content Log" tab via `log_post.py` with `Format: "Story"` —
no schema change needed, the sheet already accepts any Format value.

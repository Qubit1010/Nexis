# Facebook Cold DM Sequence — Source-Backed Playbook

> **Source basis:** Cited from `references/research-synthesis.md` (Q8, July 2026 Exa pass). Real data: Nicherly platform-limit data, Clepher Messenger mechanics, MultipleGroupPoster group-funnel benchmarks, Growth Models spearfishing method, Six Figure AI Outreach agency SOP, SetSmart 2026 Messenger playbook.

## Where Facebook fits in our stack

Facebook is a **precision channel, not a volume channel**. The platform caps cold DMs to non-connections at roughly 10/day (vs Instagram's 100-150 for established accounts), and messages from non-friends land in the Message Requests folder with reduced visibility, which is the documented hidden reason FB cold outreach underperforms expectations (Q8).

Our edge: leads arrive from **group posts** via `facebook-lead-nav` (post author -> profile URL -> "Instant Facebook Leads" sheet -> `leads-to-crm` Touch 1). That means every lead already showed intent in public: they posted about a problem. The documented reply rate for observation-based openers referencing a member's own post is **60-80%**, and 20-40% of those conversations convert to a booked consult (Q8). No other channel starts this warm.

| Constraint | Number | Source |
|---|---|---|
| Cold DMs to non-connections | ~10/day hard ceiling | Nicherly |
| Realistic daily send | 8-12, spaced out | Nicherly (stay under the cap) |
| Well-targeted group-context opener reply rate | 60-80% | MultipleGroupPoster |
| DM conversation -> booked consult | 20-40% | MultipleGroupPoster |
| Agency SOP DM 1 reply target | 30-40% | Six Figure AI Outreach |
| Ban trigger | Identical copy, not volume | Nicherly |

---

## Platform safety rules

1. **Never exceed ~10 cold DMs/day** to people who aren't friends/connections. This is the FB-specific cap; it does not scale with account age like Instagram.
2. **Vary at least the first line of every message.** Identical copy across prospects is the flag trigger, not raw volume (Q8).
3. **Warm up before the DM when possible:** like 2-3 of their recent posts or reply to their group post/comment first. Raises reply rates, lowers spam flags, and makes your name familiar when the Message Request lands (Q8).
4. **Assume the Message Requests folder.** Your first message may sit unseen for days. Keep it short enough to read fully in the request preview, and don't count silence as a "no" on FB until Touch 2 has had time to land.
5. **No mass-DMing a group's member list.** Corrodes community trust and trips automation detection. Sustainable pace: a handful of high-signal DMs per group per week (Q8).

---

## The opener structure (4 lines, sourced)

Every Facebook cold DM follows this shape (Q8, Nicherly):

1. **Line 1:** Something specific from their group post (the pain they described, in their words)
2. **Line 2:** The problem you observed, stated in their language
3. **Line 3:** One sentence on what you do for businesses like theirs
4. **Line 4:** ONE yes/no question. Never a calendar link in the opener.

4-6 sentences total. Pain before service. One question, one ask, zero links.

---

## The 3-touch sequence

Adapted from the documented agency SOP (Q8) to our group-post lead source.

### Touch 1 (Day 1) — Group-context opener

Reference the post that put them in our sheet. This is the whole advantage; never send a generic opener to a lead we sourced from a specific post.

> Hey [Name], saw your post in [Group] about [their exact problem, e.g. "chasing no-show quotes all week"]. That one's common with [their business type] and it's usually fixable. We build AI workflows that handle exactly that for [niche] owners. Are you still dealing with it manually?

> [Name], your question in [Group] about [topic] caught my eye. A lot of the [niche] owners we work with hit the same wall around [the underlying pain]. Curious, did you find a fix or is it still eating your week?

**Rules:** their post first, one qualifying question, no links, no pitch, no calendar. If we replied to their post in the group before DMing, reference that ("following up on my comment").

### Touch 2 (Day 6, if silent) — Value giveaway

The Message Requests folder means silence after Touch 1 is weak signal. Touch 2 delivers value with a micro-ask.

> Hey [Name], following up on your [Group] post about [pain]. We put together a short breakdown of how [similar business type] owners automate that exact thing. Want me to send it over?

**Rules:** the ask is "want it?", not "book a call". A yes here restarts the thread inside their real inbox, which kills the requests-folder problem for every message after.

### Touch 3 (Day 8, if silent) — Audit / call offer, then stop

> [Name], last one from me. Happy to do a free 20-min teardown of how you're handling [pain] right now, I'll point at the first thing I'd automate and you keep the notes either way. Worth it, or should I leave you to it?

**Rules:** anchored deliverable (Ops Teardown), honest "last one", easy out. After Touch 3 with no reply: mark ghosted in the CRM, re-enter in 60-90 days per the Q9 stall-recovery data. Never send a fourth cold touch.

---

## When they reply

Switch immediately to `scripts/live-conversation-playbook.md`: load conversation state (`python scripts/convo.py get facebook <identity>`), run the phases, obey the Advance Triggers (ask by exchange 6, jump on buying signals). The group-funnel data says the consult offer lands naturally at the 4th-6th exchange (Q8), which is exactly where the trigger fires.

Facebook identity for memory: profile URL slug or `id:<number>` from `profile.php?id=N`, same normalization as `leads-to-crm`.

---

## Tone (Facebook-specific)

Group members skew local-business owners and operators, not LinkedIn-polished founders. Plain words, contractions, zero corporate vocabulary, no emojis beyond one at most. Match the register of their own post. The read-aloud test from Q6 applies double here: if it wouldn't sound right said across a counter, rewrite it.

---

## What this file is NOT

This is the COLD sequence for Facebook. Once a prospect replies:
- **Live conversation** -> `scripts/live-conversation-playbook.md` (memory + advance triggers)
- **Discovery call after they agree** -> `scripts/discovery-call-script.md`
- **Objection handling** -> `frameworks/objection-riffs.md`

Kill list before any send: `references/what-not-to-do.md` (including the Tier 6 AI-tells).

# Live Conversation Playbook — When They Reply

> **Source basis:** Stitched from `references/research-synthesis.md` (Q3 IG conversation flow, Q4 discovery structure, Q5 objection responses). Pulls Voss labels (`frameworks/voss-calibrated-questions.md`) and objection riffs (`frameworks/objection-riffs.md`).

## When to use this file

Prospect has replied to a cold DM (LinkedIn or Instagram). The cold sequences (`scripts/linkedin-cold-dm-sequence.md`, `scripts/instagram-cold-dm-sequence.md`) hand off to this file the moment a back-and-forth starts.

The job here: **don't blow the rapport you just earned**. Most reps overpitch the second they see "interesting!" come back. The data says the opposite move wins. But the opposite failure is just as real: labeling and mirroring forever without ever asking. The Advance Triggers below exist to kill that loop.

---

## Conversation state (memory)

Every live thread has a record in the conversation DB (Supabase, table `conversations`, managed by `scripts/convo.py`). Before drafting any reply:

1. **Derive the identity** from the prospect's profile URL or handle (LinkedIn `/in/` slug, Instagram `@handle`, Facebook slug/id).
2. **Load the record:** `python scripts/convo.py get <channel> <identity>`. Treat the stored `stage`, `exchange_count`, and `meeting_status` as ground truth. Do not re-infer the phase from the pasted snippet alone; a short paste looks like an early conversation even when it isn't.
3. **Merge threads:** the pasted thread wins when it is longer (it is the superset). If the stored thread has exchanges the paste is missing, use the stored one as history.
4. **Draft the reply** using the phases + Advance Triggers below.
5. **Write back:** `python scripts/convo.py upsert <channel> <identity> --stage <new_stage> --thread-file <merged_thread> --last-draft "<reply>"` and `--meeting asked` the moment a call ask goes out (then `booked` / `declined` / `ghosted` as the thread resolves).

If the DB is unreachable, say so, draft from the pasted thread, and count exchanges manually. Never silently skip the state check.

---

## Advance Triggers (check before every reply)

An **exchange = one prospect reply.** Count them (the DB tracks it; the transcript's `[Them]:` lines are the same number). Check these in priority order before writing anything. When one fires, it overrides whatever phase you think you are in.

1. **Exchanges >= 6 and no call ask yet:** this reply MUST contain the anchored Ops Teardown ask. Not softened, not deferred. Six replies of engagement IS the pull; waiting longer reads as either fear or farming. (Research-pinned, not a guess: the SetSmart 828K-conversation study puts the booking inflection at ~11 total messages, i.e. 5-6 prospect replies, with near-zero bookings before it and a plateau past ~20 replies. See research-synthesis.md Q7.)
2. **Buying signal in their last 1-2 messages:** jump straight to Phase 6, skip everything between. Buying signals: a price or timeline question, "how does it work", a technical or integration question ("does it work with X?"), a second request for proof, mentioning a partner or team decision, asking about your availability.
3. **Same objection raised twice:** stop handling it in DMs. Send the transition line ("Honestly, easier to show you than type it. 20 min screen-share Tuesday or Thursday?").
4. **Phase 5 loop cap:** loop back to Phase 3 at most ONCE per conversation. A second unresolved objection pass means DMs have hit their ceiling: transition line or disqualify cleanly.

Phase 6 is the default destination, not a reward for a perfect conversation. Every reply must be measurably closer to a booked call than the last one: a deeper disclosure, a quantified cost, a proof drop, or the ask itself. If a drafted reply does none of those, it is a loop; rewrite it.

---

## The 6-Phase Live Conversation Flow

Adapted from the sourced "Partnership Discovery Flow" + Voss tactical empathy framework + Cole Gordon's relief-ladder structure.

| Phase | Goal | Move | Time in DMs |
|---|---|---|---|
| **1. Qualify** | Confirm pain is real, not curiosity | Calibrated open question | 1-2 exchanges |
| **2. Label** | Mirror the pain back, deepen | Voss label + silence | 1-2 exchanges |
| **3. Deepen** | Quantify the cost | Follow-up calibrated questions | 2-3 exchanges |
| **4. Proof** | One specific peer result (only when asked) | Named example, screenshot/Loom if possible | 1 exchange |
| **5. Objection branch** | Handle pushback if any | Pull from `frameworks/objection-riffs.md` | varies |
| **6. Warm Ask → Call** | Anchored call ask | Two specific times + deliverable framing | 1-2 exchanges |

**Critical:** Don't run ahead of the prospect's signals: going Touch 1 → Phase 6 the moment a prospect replies is still the burnt move. But always skip TOWARD Phase 6 when an Advance Trigger fires. Phase 6 is the default destination; every reply must be measurably closer to the booked call.

---

### Phase 1 — Qualify (1-2 exchanges)

Prospect replied to your Touch. They might be curious, mildly interested, or genuinely in pain. Your first response should figure out which.

**Calibrated open question:**

| Their reply | Your response |
|---|---|
| "Interesting, tell me more" | "Quick one before I dive in - is [the specific pain you mentioned in Touch 1] something you're actively trying to solve, or more 'interesting to know about'? Want to make sure I give you something useful, not generic." |
| "What do you actually do?" | "We build AI workflows that take manual ops off founder plates - usually 10+ hrs/week back. But before I pitch anything - what's the part of your week right now that's eating the most time?" |
| "Sounds good, send info" | "Happy to. Quick - is it more 'what does it look like for someone like me' or 'what does it cost'? Want to send the right thing." (Sandler reversing - see `frameworks/objection-riffs.md` #6) |
| "Yeah we have that problem" | "Yeah - it's a pattern. Walk me through how it currently runs? Just curious where the breaks are." |

**Goal of Phase 1:** Get a real answer about whether this is a fire or a curiosity. Don't pitch. Don't even describe the offer.

---

### Phase 2 — Label (1-2 exchanges)

Once they describe the pain, **don't move to solution yet**. Label it back. Voss's rule: tactical empathy first, logic second.

**Pull labels from `frameworks/voss-calibrated-questions.md`:**

| Their pain statement | Your label |
|---|---|
| "We're doing it manually every week" | "Sounds like that's quietly becoming the ceiling on the rest of the business." |
| "We've tried tools but they didn't stick" | "Seems like every attempt to fix it has added more friction, not less." |
| "It's eating my Saturdays" | "It sounds like the business is running you, not the other way around." |
| "I just don't have time to figure it out" | "Seems like you've been carrying this whole thing in your head, and that's becoming its own bottleneck." |
| "We're scaling fast and it's getting worse" | "It looks like you're hitting the part of growth where the manual stuff that used to be tolerable is now structural." |

**After the label: SILENCE.** In DM context, "silence" means: send the label, then don't send anything else. Let them respond first.

What usually happens: they expand the pain. They tell you more than they meant to. That's the floodgate effect Voss describes.

---

### Phase 3 — Deepen (2-3 exchanges)

Now they've expanded. You want to QUANTIFY the cost. Don't ask "how much does it cost you" directly — that's clumsy. Use sourced calibrated questions:

| Goal | Sourced question |
|---|---|
| Cost in hours | "How many hours a week do you reckon goes into [the specific manual thing]?" |
| Cost in $ | "If you had to put a number on what that's costing in lost revenue or wages - what would you guess?" |
| Personal cost | "What position are you in if this doesn't change?" (Voss) |
| Urgency | "What makes this urgent right now?" (Voss) |
| Time horizon | "How will this look in a year if things don't change?" (Voss) |
| Past attempts | "How have you handled these issues in the past?" (Voss) |

**Goal of Phase 3:** Get the prospect to QUANTIFY the cost in their own words. By the time you offer a price (later), they've already named a number 10x bigger than your fee.

---

### Phase 4 — Proof (1 exchange, ONLY if they ask)

Wait until they ASK for proof. Don't volunteer.

When they ask "have you done this for someone like me?" or "what does it look like?":

**The move (sourced from Becc Holland + Justin Welsh):**

> "Yeah - built exactly this for [Peer Name] (similar [stage/niche/stack]). Took [specific number] hrs/week off their plate, live in [N] days. Want me to send a 60-sec Loom of the actual build?"

**Why this works:**
- Same-stage/niche/stack = high Perceived Likelihood (Hormozi)
- Specific numbers = credibility (not "lots of hours" — "12 hrs/week")
- Loom offer = low-friction value drop, no calendar required
- "Want me to send" = they pull, not you push

**Pull peer names from `offer/proof-bank.md`** by industry/pain to match the prospect.

---

### Phase 5 — Objection Branch (varies)

At some point — usually after Phase 3 or 4 — they'll raise an objection. The 10 most common are documented with cited responses in `frameworks/objection-riffs.md`.

**Branch flow:**

```
Prospect raises objection
  → Label it first (Voss): "It seems like [feeling]..."
  → [SILENCE - let them confirm or expand]
  → Pull the cited response from objection-riffs.md
  → [SILENCE again]
  → If resolved → continue to Phase 6
  → If not resolved → loop back to Phase 3 (deepen) ONCE, max, or disqualify cleanly
     (second unresolved pass = transition line or disqualify; see Advance Triggers)
```

**Most common DM-stage objections:**
1. "Too expensive" / "What's the price?" (asked early) — see objection-riffs.md #1 and #10
2. "Not the right time" — #7
3. "We have something already" — #4
4. "Need to think about it" — #2
5. "Send more info" — #6

---

### Phase 6 — Warm Ask → Call (the default destination, 1-2 exchanges)

By now you've labeled, deepened, proven (only if asked), and handled any objection. The prospect should be leaning in. And even if they are not visibly leaning in, an Advance Trigger (6+ exchanges, buying signal, repeated objection) puts you here anyway; make the ask.

**The warm ask (sourced as best-performing in DMs):**

> "Want a 20-min Ops Teardown? I screen-share, look at your stack, tell you the exact first thing I'd automate. You decide if it's worth building. Tuesday 2pm or Thursday 11am works on my end - what about you?"

**Why this works (sourced):**
- "Ops Teardown" = a DELIVERABLE, not a sales call. Prospect gets value just by showing up.
- "Tell you the exact first thing I'd automate" = specific, valuable output promised
- "You decide if it's worth building" = removes pressure (no-oriented frame)
- "Tuesday 2pm or Thursday 11am" = two specific times (assumes yes)

**Variations by signal:**

If they're high-warmth ("yes please send the loom"):
> "Sending. While I'm building it - want to also book a 20-min Ops Teardown? I'll walk you through it live + audit your stack. Two times Thursday: 11am or 2pm?"

If they're medium-warmth ("not sure yet"):
> "Totally fair. No pressure - want me to send the Loom of [Peer]'s build first so you can decide if it's even relevant? Then you tell me if a call makes sense."

If they're price-curious early ("how much?"):
> "Depends on what you'd actually need - which is why I do a free 20-min Ops Teardown. I screen-share your stack, you see exactly what we'd build, then we talk numbers if it makes sense. Tuesday 2pm or Thursday 11am?"

**Never use:**
- "Worth a quick chat?" / "Hop on a call?" / "Open to a call?" — see `references/what-not-to-do.md`

---

## The conversation length rule

**Don't try to close the deal in DMs.** The data says:
- DMs are for QUALIFICATION + WARM ASK
- Deal happens on the call

**Signs you've stretched too long in DMs** (these are now enforced as Advance Triggers, counted via the conversation DB, not eyeballed):
- 6+ exchanges without a call ask → the next reply must contain the ask
- Same objection re-emerging twice → not handling it well, switch to call
- They start asking technical questions ("does it integrate with X?") → MOVE TO CALL, this is buying behavior

**The transition line:**
> "Honestly, easier to show you than type it. 20 min screen-share Tuesday or Thursday?"

---

## Cold-thread re-entry (they went silent mid-conversation)

If they replied a few times then ghosted, don't:
- "Just bumping this..."
- "Following up..."
- "Wanted to check in..."

**Do:**
- Add new value (a Loom, a specific framework, a peer case study) and link it to the LAST thing they said
- Or use the Voss no-oriented exit ramp:

> "[Name] - might've gotten buried. Are you good or has this dropped in priority? Either answer is fine."

This works because "Are you good?" is a no-oriented question. Saying "no" feels safe. They'll either say "no, still interested" (saving the thread) or "yes, all good" (which means it's dead — and now you can move on cleanly).

---

## The Speed-to-Reply rule (Instagram especially)

**Sourced finding:** Reply within **1 minute** of a prospect message = **+391% conversion** vs 30+ min delay.

**On Instagram specifically:** the conversation tempo is fast. A 2-hour delay drops conversion to 3-5%. A 24-hour delay drops it below 2%.

**Aleem's operational rule:** When the IG/LinkedIn notification fires during a live thread, drop everything and reply within 5 min. The deal compounds at the speed of your responsiveness.

---

## Peer / partner routing (the non-client conversation)

Sometimes the DM thread reveals the prospect is actually a **peer** (another AI consultant, agency owner, fellow operator) rather than a client. Don't try to sell — flip the frame.

**Peer move:**

> "Wait - you build this stuff too? Different conversation then. Want to compare notes? Always trying to learn how other operators in this space are running things. Got 20 min next week to nerd out?"

This converts ~half of "wrong-fit prospects" into either:
- Referral partners (they don't need it but their clients do)
- Idea swaps (they teach you something, vice versa)
- Long-game brand connections

Don't burn the relationship by pitching when there's no fit.

---

## What this file is NOT

This is the live DM flow. Once the prospect agrees to a call:
- **The actual call** → `scripts/discovery-call-script.md`

For the objection responses themselves:
- `frameworks/objection-riffs.md`

For the labels and calibrated questions referenced throughout:
- `frameworks/voss-calibrated-questions.md`

For the COLD sequence (before they replied):
- `scripts/linkedin-cold-dm-sequence.md` or `scripts/instagram-cold-dm-sequence.md`

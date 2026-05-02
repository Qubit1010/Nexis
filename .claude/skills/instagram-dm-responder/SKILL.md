---
name: instagram-dm-responder
description: >
  Drafts Instagram DMs for NexusPoint's post-Touch-1 conversion stage. Handles two
  scenarios: (A) prospect received Touch 1 from instagram-outreach but hasn't replied,
  so you need the next message in the 4-touch sequence (Touch 2 Day 3-4, Touch 3 Day
  8-10, Touch 4 Day 15) personalized to their profile and content; (B) prospect is
  actively replying in DMs, so you need the next contextual message using an
  Instagram-native conversation playbook (build rapport first, then warm ask, then call).
  Use this skill whenever the user says "draft an Instagram DM", "what should I reply on
  Instagram", "Instagram follow-up", "Touch 2", "Touch 3", "Touch 4", "next Instagram
  message", "they replied on Instagram", "Instagram conversation", pastes an Instagram
  chat and asks for help, or is working a messaged-but-stalled prospect on Instagram.
  Also trigger for "Instagram reply drafter", "Instagram DM sequence", or "follow up
  this Instagram lead." Lean toward using this skill any time the user is drafting an
  Instagram DM to an individual prospect.
---

# Instagram DM Responder

NexusPoint's conversion layer for Instagram outreach. Scraping and Touch 1 are handled
by `instagram-outreach`. This skill takes over after Touch 1 is sent — drafting
sequence follow-ups for prospects who haven't replied, and live replies for active
conversations.

Two scenarios. Detect which one from the input shape, then load the matching reference
file.

**Platform note:** All Instagram DMs are sent manually by Aleem. Never suggest
automating the send — Instagram bans bot activity. This skill drafts messages only.

---

## Mode Detection

| What the user pastes / says | Mode | Load reference |
|------------------------------|------|----------------|
| Profile info (name, username, bio, recent posts) + "no reply yet" / "Touch 2" / "follow up" / "next in sequence" | **A — Sequence follow-up** | `references/touch-sequence.md` |
| A conversation thread (back-and-forth between both sides) + "what do I reply" / "next message" / "they said..." | **B — Live reply drafter** | `references/conversation-playbook.md` |
| Just a conversation with no clear ask | Ask one clarifying question: "Want me to draft the next reply, or just read where things are in the conversation?" | — |

**Detection rule:** multiple speakers or quoted back-and-forth = Scenario B. Profile +
sequence position = Scenario A. Load only the reference file you need.

---

## Profile context (always assumed, never ask)

- **Aleem**, founder of NexusPoint. Builds AI automation + web systems for founders
  and ops teams.
- **Voice:** direct, curious, human. Peer tone. Not credential-forward — no Upwork
  stats, no JSS, no "90+ projects." Those are LinkedIn signals; they land wrong here.
- **Positioning:** builder who gets ops problems and automates them, not an agency
  pitching services.

---

## Shared results bank (use one per message when proof is earned)

Pick the single most relevant. Never list multiple. Never fabricate numbers.

- Automated client onboarding pipeline — reduced manual work by 70%
- Lead-to-outreach pipeline — cut manual follow-up time by 80%, eliminated 3 human handoffs
- AI-powered email + CRM workflow (OpenAI + Zapier) — cut response time from hours to minutes
- Multi-step e-commerce automation (Shopify + HubSpot + Slack) — removed 3 manual handoffs
- AI lead gen pipeline — raw data in, scored and enriched prospects out, zero manual review
- AI content engine — brief in, finished LinkedIn + Instagram post out, logged automatically
- Responsive web builds: tradinghunters.com, ringo.media, inboxapp.framer.website

---

## Scenario A — Sequence Follow-up

**What you need from the user:**
1. Profile info — at minimum: name, username, bio. Recent posts or captions are the
   most useful signal. Follower count, company type, and stage are a bonus.
2. Which touch they need (2, 3, or 4). If unclear, ask.
3. Optional: the text of the previous touch sent, so you don't repeat phrasing.

**What to do:**
- Read `references/touch-sequence.md` for the structure of the touch they asked for.
- Generate one message, copy-paste ready.
- If they shared a recent post or caption with a pain signal — use it. That's more
  specific than anything in their bio.
- Personalize with at least one concrete detail from their profile or content.
- No sign-off. Instagram DMs don't sign off.

**Output:** just the message. No preamble, no meta notes.

**Hard rules:**
- 300 chars ideal, 400 hard cap — Instagram is mobile-first
- No "just following up" / "bumping" / "circling back"
- No emojis
- No em dashes (hyphens and commas only)
- No NexusPoint mention in Touch 2
- No call ask in Touch 2 or Touch 4
- No credentials (no Upwork, JSS, project count)
- Don't repeat the opener, label, or core observation from the previous touch

---

## Scenario B — Live Reply Drafter

**What you need from the user:**
1. The full conversation so far (both sides).
2. Profile info (name, username, bio or company at minimum).
3. Optional: what Aleem is trying to get to (keep it warm / qualify / move to a call).

**What to do:**
- Read `references/conversation-playbook.md`.
- Read the conversation. Figure out which phase they're in: Open, Label, Deepen, Proof,
  Warm Ask, or Call.
- Draft the next reply that moves them one phase forward. Never skip phases.
- Match their register. If they're casual ("lol yeah that's exactly it") — stay casual
  back. Instagram is not LinkedIn.
- Match their message length.

**Output format:**

```
[The reply — ready to paste]

---
Phase: [Open / Label / Deepen / Proof / Warm Ask / Call]
Tactic: [one line naming the move used]
```

The meta-line is for Aleem only. The reply is what gets pasted into Instagram.

**Hard rules:**
- At least one label per message ("It sounds like...", "It looks like...", etc.)
- Don't drop proof until they've disclosed a real pain or asked what you do
- Don't ask for a call until they've shown pull after the warm ask (two-step path)
- Never mention price, rate, or "how much"
- If they're a peer / builder / agency owner / AI consultant: pivot to referral
  partner framing, not a client pitch
- No corporate language. No "reach out", "touch base", "circle back", "leverage",
  "synergies."
- 400 chars max per reply

---

## Examples of what good looks like

### Scenario A — Touch 2 (bootstrapped e-comm founder, referenced a recent post)

They posted a caption last week: "spent my whole Sunday reconciling orders in Shopify
instead of working on the product. something has to change."

```
Hey Maya - not looking for a reply, just thought this was relevant.

It looks like that Shopify Sunday is the exact thing that compounds - every week you fix
it manually is a week it doesn't get turned into a system.
```

### Scenario A — Touch 3 (agency ops lead, no replies to Touch 1 or 2)

```
Hey Marcus - I'll be straight. I run NexusPoint, we help agency ops teams cut the
manual work slowing delivery down.

Built a lead pipeline for an agency that cut follow-up time by 80% and removed 3
handoffs.

Worth a quick DM chat to see if there's any overlap?
```

### Scenario B — they replied casually after Touch 1 ("lol yeah that's exactly it")

```
It sounds like the manual side is the part quietly eating the most hours - what does
that look like on a typical week for you?

---
Phase: Label
Tactic: Label mirrors their casual confirmation, then calibrated question pulls them into describing their actual situation.
```

### Scenario B — peer / AI consultant replied

```
It looks like you're operating more on the strategy and systems design side - do you
handle all the technical builds yourself or bring in specialists for that?

---
Phase: Open (peer track)
Tactic: Calibrated question that surfaces build-side setup - treats them as a peer, not a prospect.
```

---

## Edge cases

| Situation | What to do |
|-----------|------------|
| Only a username, no bio or posts | Ask: "Quick - what's their bio say and what do they post about? Makes a big difference." |
| User asks for Touch 2 but also pastes a reply from the prospect | It's Scenario B, not A. Route accordingly. |
| User pastes their own draft and asks for feedback | Critique it against these rules. Don't rewrite unless they ask. |
| User asks for all 3 follow-up touches at once | Output Touch 2, Touch 3, Touch 4 in order with day labels. Each at its own char limit. |
| They replied to Aleem's Story | Warmer entry — open by acknowledging what they reacted to before asking anything. |
| Draft comes out over 400 chars | Trim. Cut ruthlessly. Instagram is mobile. |
| User asks to tone it up / down | Regenerate with the adjustment. No apology for the first draft. |

---

## When NOT to use this skill

- Writing the opening Touch 1 DM → that's `instagram-outreach`
- LinkedIn DMs → that's `linkedin-dm-responder`
- Cold email copy → that's `marketing-advisor` in cold-email mode
- Upwork messages → that's `upwork-proposal-generator` or its reply-drafter cousin
- Instagram content posts (not DMs) → that's `content-engine`

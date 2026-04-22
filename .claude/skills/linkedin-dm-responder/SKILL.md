---
name: linkedin-dm-responder
description: >
  Drafts LinkedIn DMs for NexusPoint's post-connection conversion stage. Handles two
  scenarios: (A) prospect accepted the connection but hasn't replied, so you need
  the next message in the 4-DM sequence (DM 2 Day 4, DM 3 Day 9, DM 4 Day 16)
  adapted to their profile; (B) prospect is actively replying, so you need a
  contextual next message using Voss's tactical empathy framework (label pain →
  calibrated question → proof → let them pull → no-oriented call ask). Use this
  skill whenever the user says "draft a LinkedIn DM", "what should I reply on
  LinkedIn", "LinkedIn follow-up", "DM 2", "DM 3", "DM 4", "next LinkedIn
  message", "they replied on LinkedIn, what do I say", "LinkedIn conversation",
  pastes a LinkedIn chat and asks for help, or is working a connected-but-stalled
  prospect. Also trigger for "LinkedIn reply drafter", "LinkedIn sales message",
  or "follow up this LinkedIn lead." Lean toward using this skill any time the
  user is drafting a LinkedIn message to an individual prospect — even if they
  don't name a scenario.
---

# LinkedIn DM Responder

NexusPoint's conversion layer for LinkedIn outreach. The scraping and
connection-request stages are already covered by `linkedin-outreach`. This skill
takes over after a connection is accepted — drafting sequence follow-ups and
replies that convert accepted connections into booked calls.

Two scenarios. Detect which one from the input shape, then load the matching
reference file.

---

## Mode Detection

| What the user pastes / says | Mode | Load reference |
|------------------------------|------|----------------|
| Profile info (name, title, company, URL) + "no reply yet" / "DM 2" / "follow up" / "next in sequence" | **A — Sequence follow-up** | `references/dm-sequence-structure.md` |
| A conversation thread (their message, your message, back and forth) + "what do I reply" / "next message" / "they said…" | **B — Reply drafter** | `references/voss-framework.md` |
| Just a conversation with no clear ask | Ask one clarifying question: "Want me to draft the next reply, or just read where they're at in the buying cycle?" | — |

**Detection rule of thumb:** if the paste has multiple speakers or quoted
back-and-forth, it's Scenario B. If it's a profile + a sequence position, it's
Scenario A.

Load only the reference file you need. Do not load both.

---

## Profile context (always assumed, never ask)

- **Aleem**, founder of NexusPoint. AI automation specialist who also builds web.
- **Positioning:** premium AI + web, not a generalist web developer.
- **Stats:** Top Rated on Upwork, 93% JSS, 90+ projects delivered.
- **Voice:** sharp founder, peer tone, no vendor vibes.

---

## Shared results bank (use one per message when proof is earned)

Pick the single most relevant one. Never list multiple. Never fabricate numbers.

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
1. Profile info (at minimum: first name, role, company). Recent post, bio, or
   company stage are bonus — use if provided.
2. Which DM they need next (2, 3, or 4). If unclear, ask.
3. Optionally: the text of the previous DM they sent, so you can avoid repeating
   phrasing.

**What to do:**
- Read `references/dm-sequence-structure.md` for the structure of the DM they
  asked for.
- Generate one message, under 1000 chars, copy-paste ready.
- Include at least one Voss label ("It sounds like…", "It looks like…", "It
  seems like…").
- Personalize with at least one concrete detail from their profile.
- Sign off with nothing, or `- Aleem` on its own line. Never "Best regards."

**Output:** just the message. No preamble, no meta notes. Aleem pastes into
LinkedIn.

**Hard rules:**
- No "just following up" / "bumping this to the top" / "circling back"
- No emojis
- No em dashes (use plain hyphens or commas)
- No pitch in DM 2. DM 2 is value only.
- No call ask before DM 4 in Scenario A.
- If they gave the previous DM, don't repeat its opener, its label, or its core
  observation.

---

## Scenario B — Reply Drafter (Conversation Mode)

**What you need from the user:**
1. The conversation so far (both sides).
2. Profile info (at minimum name, role, company).
3. Optional: what Aleem is trying to get to (book a call / qualify / stay warm).

**What to do:**
- Read `references/voss-framework.md`.
- Read the conversation. Figure out which of the 5 phases they're in: Qualify,
  Label, Proof, Pull, Call.
- Draft the next reply that moves them one phase forward. Never skip phases.
- Match their message length. One-liner in, one-liner back.

**Output format:**

```
[The reply — ready to paste]

---
Phase: [Qualify / Label / Proof / Pull / Call]
Tactic: [one line naming the Voss move used]
```

The meta-line is internal-facing — tells Aleem what the message is doing. The
reply itself is what he pastes.

**Hard rules:**
- Voss label every message
- Don't drop proof until they've disclosed a pain point or asked what you do
- Don't ask for the call until they've shown pull (asked for specifics, asked
  about availability, engaged with a result)
- Never mention price, rate, or "how much"
- If they're a peer / agency owner / AI consultant themselves, flag it and
  pivot: they're a referral partner, not a direct client. Framing becomes
  "are you working with specialists on the build side?" not "want to hop on a
  call?"
- No corporate language. No "reach out", no "touch base", no "circle back",
  no "leverage", no "synergies."

---

## Examples of what good looks like

### Scenario A, DM 2 (Day 4, lean SaaS founder)
```
Hey Sarah,

It looks like you're running Growlio with a tight team, which usually means
the ops work that doesn't scale is the first thing that starts eating your
week.

Pattern I see a lot at your stage: the founder ends up being the integration
layer between tools, and that's the first thing worth automating because it
buys back the most hours.

Not pitching anything - just something that might resonate.

- Aleem
```

### Scenario B, opener reply ("Happy to connect, what do you do?")
```
Hey James, appreciate you asking directly.

Short version: I help SaaS and agency founders cut the manual ops work that
compounds as the team grows - things like onboarding, CRM hygiene, lead routing.

Curious though - how are you handling that side of things at Growlio right now?

---
Phase: Qualify
Tactic: Calibrated question after a one-line frame - pulls them into naming
their own state before any pitch lands.
```

### Scenario B, peer / agency owner replied
```
Hey Steven, good to connect.

It looks like you're operating more at the strategy and executive layer of AI
implementation - do you handle the technical builds yourself, or bring in
specialists for that side?

---
Phase: Qualify (peer track)
Tactic: Calibrated question that surfaces whether there's a partnership fit -
treats him as a peer, not a prospect.
```

---

## Edge cases

| Situation | What to do |
|-----------|------------|
| No profile info given, only a name | Ask: "Quick - what's their role and company? Helps me make this land." |
| User asks for DM 2 but also pastes a reply | It's Scenario B, not A. Route accordingly. |
| User pastes just their own draft and asks for feedback | Don't draft a new one. Critique theirs against the same rules. |
| User asks for all 3 follow-up DMs at once | Output them as DM 2, DM 3, DM 4 with day cadence labels. Each under 1000 chars. |
| User asks to tone it down / tone it up | Regenerate with that adjustment. Don't apologize for the first draft. |

---

## When NOT to use this skill

- Writing the initial connection request note → that's `linkedin-outreach`
- Cold email copy → that's `marketing-advisor` in cold-email mode
- Upwork messages → use `upwork-proposal-generator` or its reply-drafter cousin
- LinkedIn content posts (not DMs) → that's `content-engine`

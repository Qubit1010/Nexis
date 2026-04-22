# 4-DM Sequence Structure

Loaded in Scenario A (sequence follow-up). This is the day-cadenced sequence
that runs after a LinkedIn connection is accepted when the prospect hasn't
replied yet.

The underlying template lives in
`projects/lead-gen/transformers/linkedin_transformer.py` (function
`generate_linkedin_sequence`). This reference re-expresses that structure as
writing guidance — because when Aleem is mid-conversation with a real
prospect, he needs the *shape* of the next DM, not a template to paste.

---

## The cadence

| DM | Day | Role in the sequence | Core move |
|----|-----|----------------------|-----------|
| DM 1 | Day 0 | **Warm opener** | Thank them for connecting, label their situation, ask one open question |
| DM 2 | Day 4 | **Value drop** | One pattern/observation relevant to their stage — no pitch, no ask |
| DM 3 | Day 9 | **Bridge + soft proof** | Connect a NexusPoint result to their likely pain, offer to share more |
| DM 4 | Day 16 | **Direct no-oriented ask** | Permission-based call ask, framed so saying no is easy |

DMs 2, 3, and 4 are what this skill generates in Scenario A (DM 1 already
went out from the automated pipeline). If Aleem asks for "DM 1," he probably
means a replacement/rewrite — confirm before drafting.

---

## DM 2 — Day 4 — Value drop

**What it does:** proves Aleem read their profile and thinks about their
problem space. Zero pitch. Zero ask. The only goal is to feel useful and
non-salesy enough that the next DM gets read.

**Structure:**
1. **Voss label** — one line about what their situation looks like from the
   outside. Specific to their role, stage, or a post of theirs if available.
2. **Pattern or observation** — one useful thing Aleem has seen at their
   stage or in their industry. Concrete, not generic.
3. **Soft close** — "not pitching anything" / "just something that might
   resonate" / "curious if this lands."

**Hard rules:**
- No case study
- No call ask
- No "I can help with this"
- Under 1000 chars
- Sign off with "- Aleem" on its own line, or nothing

**Example (lean SaaS founder, 4-person team):**
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

**Example (Series A ops lead):**
```
Hey James,

It seems like you're at the stage where the number of tools is growing
faster than the team that has to babysit them.

The thing I see break first at this stage is usually the handoff layer -
the stuff between Salesforce and the rest of the stack where nobody fully
owns the data flow. Quiet problem, expensive over time.

Sharing because it's been the #1 theme in conversations this month.

- Aleem
```

---

## DM 3 — Day 9 — Bridge and soft proof

**What it does:** makes the connection explicit. Bridges from "here's a
pattern" (DM 2) to "here's what we've actually done about it" — with one
concrete result. Still no direct call ask.

**Structure:**
1. **Short re-anchor** — one sentence referencing the space or pain you
   labeled in DM 2, without literally repeating the words.
2. **One result from the results bank** — the single most relevant one. Use
   a number if the result has one (70%, 80%, hours-to-minutes, etc.).
3. **Soft hook** — "happy to share how it was built if that's useful" /
   "can send over a quick walkthrough if it's relevant."

**Hard rules:**
- Exactly one result. Never list multiple.
- Number-forward if possible — specificity lands harder than adjectives.
- Still no call ask. This DM earns the right to DM 4's ask.
- Under 1000 chars

**Example (continuing with Sarah from DM 2):**
```
Hey Sarah, one more thought on the ops side at your stage.

We built a client onboarding pipeline for a similar-sized SaaS team
recently that cut their manual onboarding work by 70% - most of the gain
came from turning tribal knowledge into a system the tool runs, not a
checklist a human runs.

Happy to send a short walkthrough of how it's structured if you're curious
what it looked like under the hood.

- Aleem
```

**Example (James, Salesforce handoff theme):**
```
Hey James, circling on the handoff theme from last week.

We built a lead-to-outreach pipeline for an ops team dealing with exactly
this - cut manual follow-up time by 80% and removed three human handoffs
that were quietly costing them deals.

If it'd help, I can send a quick breakdown of how the handoff layer was
architected. No pitch, just the shape of what worked.

- Aleem
```

---

## DM 4 — Day 16 — Direct no-oriented ask

**What it does:** this is the ask. Permission-framed and no-oriented so the
person feels in control. Also explicitly the last message in the sequence —
this creates honest urgency without fake scarcity.

**Structure:**
1. **Honest frame** — "last note from me on this" / "not going to keep this
   in your inbox" — tells them this isn't a forever drip.
2. **No-oriented call ask** — *Would it be off base...* / *Is it a bad idea...*
   / *Is this the worst timing...*. Specific duration (15-20 min). Specific
   value ("show you what it looks like" / "map it against your flow").
3. **Soft exit** — "if it's not the right time, all good, I'll see you
   around the network" / "if not, no worries at all."

**Hard rules:**
- Must be no-oriented, not yes-oriented
- Offer a specific, short duration (15 or 20 min)
- Include a graceful "no" option — never guilt-framed
- Under 1000 chars

**Example (Sarah, final):**
```
Hey Sarah, last note from me on this one.

It seems like this kind of ops automation could be a genuine lift for a
team at your stage - would it be off base to grab 20 minutes this week so
I can show you what the onboarding pipeline looked like end-to-end and we
can figure out if the same shape would map to Growlio?

If it's not the right timing, all good - I'll leave this alone and just
stay in the network.

- Aleem
```

**Example (James, final):**
```
Hey James, last message from me on this - don't want to camp in your
inbox.

Would it be off base to do a 15-minute call this week so I can walk you
through how the handoff layer was structured and see if there's anything
worth mapping to your stack?

If it's a bad time, no worries - I'll catch you around the feed.

- Aleem
```

---

## Personalization inputs to pull from

When Aleem pastes profile info for Scenario A, these are the levers to
reach for in order of preference:

1. **A recent post of theirs** — most specific signal. If they posted about
   hiring, funding, a launch, a struggle — reference it in DM 2.
2. **Their role + company stage** — "CTO of a 4-person team" and "Head of
   Ops at a Series A" call for different pain labels.
3. **Company size** — lean (≤5) vs. scaling (≥20) vs. mid-market calls for
   different observations. The transformer has these hardcoded; for skill
   output, mirror the same reasoning:
   - **≤5 people:** founder is the integration layer, time-not-money is the
     constraint, ops work eats the week.
   - **≥20 people:** coordination overhead kicks in, tool sprawl starts
     hurting, handoff layers break first.
   - **Mid:** stage-specific — ask Aleem what their real signal is if it
     isn't obvious.
4. **Industry** — SaaS founders have different pain than e-commerce
   founders have different pain than agency owners. Keep the pain
   label industry-appropriate.

If Aleem only gives a name and no other info, ask one clarifying question
before drafting: *"Quick — what's their role, company, and roughly what
stage the business is at? Helps me make this land."*

---

## Common failure modes to avoid

| Mistake | Why it kills the DM |
|---------|---------------------|
| "Just following up" / "bumping this" | Everyone writes this. Instant sales-flavor. |
| "Circling back" / "touching base" | Corporate vocab. Aleem is a sharp founder peer, not a BDR. |
| Repeating exact phrasing from the prior DM | Signals template, not thought. If DM 2 said "integration layer," DM 3 should not. |
| Listing multiple results in one DM | One result lands. Three results feel like a pitch deck. |
| Asking for a call before DM 4 | You haven't earned it yet. DM 2 and 3 build the trust that makes DM 4's ask reasonable. |
| Emojis or em dashes | Breaks the founder-voice tone. Hyphens and commas only. |
| "Best regards," / formal sign-offs | LinkedIn, not email. "- Aleem" or nothing. |
| Long paragraphs | LinkedIn DMs get skimmed on mobile. Keep paragraphs to 2-3 lines max. |

---

## If Aleem asks for all 3 follow-ups at once

Output them in order — DM 2 first, then DM 3, then DM 4 — with the day
label at the top of each. Under 1000 chars each. Make sure the three of
them read like a coherent arc, not three standalone messages: DM 3 should
echo the pain space DM 2 labeled, and DM 4 should reference the value
space DM 3 hinted at. Variety in opening lines across the three — don't
start all three with "Hey [Name],".

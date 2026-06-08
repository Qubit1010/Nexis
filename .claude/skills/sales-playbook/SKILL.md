---
name: sales-playbook
description: Master sales playbook for NexusPoint cold outreach and client conversion. Contains the opener archetypes, frameworks (Voss, Hormozi, Sandler), live conversation playbook with objection branches, full DM-to-call sequences for LinkedIn and Instagram, and the 30-minute Discovery Call (Ops Teardown) script. This is the canonical source — the DM outreach skills (linkedin-outreach, instagram-outreach) and the Sales Playbook Dashboard (projects/sales-playbook-dashboard) reference it. Use this skill when Aleem asks "what should I say to [prospect]", "draft a DM", "how do I respond to this objection", "prep me for a sales call", "write a discovery call script", "how do I close this lead", "convert this prospect", "pitch my AI automation offer", "what's my opener", or anything related to the cold-outreach-to-close pipeline. Also trigger when Aleem pastes a live conversation thread and asks "what now". The lead offer is AI automation as the premium wedge — never lead with web dev.
---

# Sales Playbook

The canonical sales asset for NexusPoint. Built to fix one problem: existing DM scripts sound like cadence (predictable AI-style openers, "worth a quick chat?" asks), so prospects ignore them. This playbook rotates across six opener archetypes, anchors every call ask to a deliverable, and gives Aleem a tight 30-min discovery call frame that converts.

## When to use

- "Draft a DM to [prospect]" → pick archetype from `frameworks/opener-archetypes.md`, follow `scripts/linkedin-cold-dm-sequence.md` or `scripts/instagram-cold-dm-sequence.md`
- "They replied — what now?" → `scripts/live-conversation-playbook.md`
- "They said [objection]" → `frameworks/objection-riffs.md`
- "I have a discovery call with X" → `scripts/discovery-call-script.md` + offer context from `offer/`
- "How do I pitch this prospect?" → `offer/ai-automation-positioning.md`
- "Give me a result I can drop for [industry]" → `offer/proof-bank.md`

## The lead offer (locked)

**AI automation as the premium wedge.** Web is the upsell, not the opener.

One-liner: *"We build AI workflows that take the manual ops work off founders' plates — 10+ hrs/week back, usually inside 14 days."*

Full positioning: `offer/ai-automation-positioning.md`

## The six opener archetypes (rotation discipline)

Never send two prospects the same archetype back-to-back. Rotation is what kills cadence smell.

1. **Permission-Based** — "Random ask — mind if I float a stupid idea?"
2. **Anti-Pitch** — "Probably not a fit but had to ask..."
3. **Observation + Confession** — "Watched your [X]. Quick confession — I'm in your DMs because..."
4. **Loom-First** — "Made you a 90-sec video on [their workflow]"
5. **Pattern from the field** — "Every [niche] founder I've talked to this month is doing [X] manually. Same here?"
6. **Quantified peer result** — "Took 12 hrs/week off [peer] by wiring [stack]. Same problem here?"

Detail + variants: `frameworks/opener-archetypes.md`

## The call ask (locked language)

Never: *"worth a quick chat?"* / *"open to a call?"* / *"15 mins?"*

Always: anchored to a deliverable.
- *"Tuesday 2pm or Thursday 11am — I'll screen-share the actual automation we built for [peer], you tell me if it'd port to your stack."*
- *"Want a 20-min Ops Teardown? I look at your stack, tell you the first thing I'd automate, you decide if it's worth building."*

## The discovery call (30-min Ops Teardown)

Frame: *"I'm going to ask 6 questions about your ops, then either show you what I'd build or tell you it's not a fit."* Not a sales call — a teardown.

Full script: `scripts/discovery-call-script.md`

## Hard bans (the cadence-smell list)

Lifted to its own file because it's referenced everywhere: `references/what-not-to-do.md`

Top offenders:
- "Just following up" / "bumping this" / "circling back"
- "Worth a quick chat?" / "open to a call?"
- "I came across your profile..."
- "Hope this finds you well"
- "Reaching out because..."
- "I'd love to learn more about your business"
- Any em-dash (—) in cold messages, ever
- "It looks like..." as the literal opener (still fine mid-message)

## File map

```
sales-playbook/
├── SKILL.md                                # this file
├── frameworks/
│   ├── opener-archetypes.md                # 6 archetypes, 3 variants each
│   ├── voss-calibrated-questions.md        # Question bank by phase
│   ├── hormozi-value-equation.md           # How to frame every proof
│   └── objection-riffs.md                  # 12 objections × Voss response
├── scripts/
│   ├── linkedin-cold-dm-sequence.md        # 4-touch with archetype rotation
│   ├── instagram-cold-dm-sequence.md       # IG-native voice
│   ├── live-conversation-playbook.md       # 6 phases + objection branches
│   └── discovery-call-script.md            # 30-min Ops Teardown
├── offer/
│   ├── ai-automation-positioning.md        # The AI wedge — one-liner + 3 sub-offers
│   └── proof-bank.md                       # Results by industry/pain
└── references/
    ├── research-synthesis.md               # Cited Q1-Q5 research + Live Query Additions
    ├── what-not-to-do.md                   # Banned phrases + patterns
    └── notebook-live-query.md              # LIVE FALLBACK: ask the sales notebook on a miss
```

## How to use this skill in a request

When Aleem asks for any sales asset:
1. Read the relevant script file in full
2. Pull the right archetype from `opener-archetypes.md`
3. Pull a matching proof from `proof-bank.md` (by industry)
4. Pass through the `what-not-to-do.md` filter before returning the message
5. If a call ask is involved, use the anchored-deliverable phrasing from `discovery-call-script.md`

Don't paraphrase the bans or the call-ask templates — copy them verbatim. They were chosen for specific psychological reasons documented in their files.

## When the playbook doesn't have it (live fallback)

For a sales KNOWLEDGE question (an opener/reply/closing benchmark, an objection nuance, a discovery-call detail, "what does the research say about X") that the framework/script files and `references/research-synthesis.md` don't confidently answer: **query the live sales NotebookLM notebook before guessing.** Follow `references/notebook-live-query.md` — ask the notebook, present the cited answer, then append the finding to `references/research-synthesis.md` under its "Live Query Additions" section so it's reusable next time. Only after a genuine notebook miss do you say the corpus doesn't cover it. (This is for facts/knowledge — generating the actual DM/script still works from the archetypes + scripts above.)

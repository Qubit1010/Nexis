---
name: sales-playbook
description: Master sales playbook for NexusPoint cold outreach and client conversion. Contains the opener archetypes, frameworks (Voss, Hormozi, Sandler), live conversation playbook with objection branches, full DM-to-call sequences for LinkedIn and Instagram, and the 30-minute Discovery Call (Ops Teardown) script. This is the canonical source — the DM outreach skills (linkedin-outreach, instagram-outreach) and the Sales Playbook Dashboard (projects/sales-playbook-dashboard) reference it. Use this skill when Aleem asks "what should I say to [prospect]", "draft a DM", "how do I respond to this objection", "prep me for a sales call", "write a discovery call script", "how do I close this lead", "convert this prospect", "pitch my AI automation offer", "what's my opener", or anything related to the cold-outreach-to-close pipeline. Also trigger when Aleem pastes a live conversation thread and asks "what now". The lead offer is AI automation as the premium wedge — never lead with web dev.
---

# Sales Playbook

The canonical sales asset for NexusPoint. Built to fix one problem: existing DM scripts sound like cadence (predictable AI-style openers, "worth a quick chat?" asks), so prospects ignore them. This playbook rotates across six opener archetypes, anchors every call ask to a deliverable, and gives Aleem a tight 30-min discovery call frame that converts.

## When to use

- "Draft a DM to [prospect]" → pick archetype from `frameworks/opener-archetypes.md`, follow `scripts/linkedin-cold-dm-sequence.md`, `scripts/instagram-cold-dm-sequence.md`, or `scripts/facebook-cold-dm-sequence.md`
- "They replied — what now?" → `scripts/live-conversation-playbook.md` (load conversation memory first, see below)
- "They said [objection]" → **diagnose the distortion** in `frameworks/objection-psychology.md`, then pull the phrase-level response from `frameworks/objection-riffs.md`
- "Prep my head before a call / how do I not sound salesy" → `frameworks/hormozi-selling-principles.md`
- "I have a discovery call with X" → `scripts/discovery-call-script.md` + offer context from `offer/`
- "How do I pitch this prospect?" → **agency prospect** → `offer/agency-to-agency-positioning.md` (primary ICP); **end-business/founder** → `offer/ai-automation-positioning.md`
- "Give me a result I can drop for [industry]" → `offer/proof-bank.md`

## The lead offer (locked)

**AI automation as the premium wedge.** Web is the upsell, not the opener.

**ICP (two tracks):**
- **Primary — agencies (white-label):** marketing / AI / design / branding agencies who need AI-automation + build capacity they can't staff in-house. One-liner: *"We're the white-label AI-automation and build team behind agencies — you keep the client and the brand, we deliver, usually inside 14 days."* Full positioning: `offer/agency-to-agency-positioning.md`.
- **Secondary — founders/SMBs:** *"We build AI workflows that take the manual ops work off founders' plates — 10+ hrs/week back, usually inside 14 days."* Full positioning: `offer/ai-automation-positioning.md`.

Pick the track by who the prospect is; the frameworks (openers, objection psychology, discovery call) are shared.

## The 5 opener archetypes (rotation discipline)

Never send two prospects the same archetype back-to-back. Rotation is what kills cadence smell. `frameworks/opener-archetypes.md` is the canonical list (with cited benchmarks + variants) — these are the five:

1. **Trigger-Aware Zero-Ask** (Justin Welsh) — congratulate a real trigger event, make no ask.
2. **Specific Signal + Named Peers** (Becc Holland) — trigger → the pain it creates → two named peer wins → one concrete ask.
3. **No-Pitch Connection** — reference real profile activity and explicitly promise no pitch.
4. **Laid-Back Anti-Pitch** (Josh Braun) — "Not sure it's a fit, but thought you might be interested..."
5. **Post-Connection Genuine Question** — after a connect, ask one open operational question, no CTA.

Detail + variants: `frameworks/opener-archetypes.md`

## The call ask (locked language)

Never: *"worth a quick chat?"* / *"open to a call?"* / *"15 mins?"*

Always: anchored to a deliverable.
- *"Tuesday 2pm or Thursday 11am — I'll screen-share the actual automation we built for [peer], you tell me if it'd port to your stack."*
- *"Want a 20-min Ops Teardown? I look at your stack, tell you the first thing I'd automate, you decide if it's worth building."*

## Conversation memory (the anti-loop layer)

Every live conversation has a persistent record in Supabase (table `conversations`), managed by `scripts/convo.py` (stdlib Python, reads `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` from the repo `.env`). One-time table setup: paste `scripts/schema.sql` into the Supabase SQL Editor.

The loop for any live reply:

1. `python scripts/convo.py get <channel> <identity_or_url>` before drafting. Stored `stage`, `exchange_count`, and `meeting_status` are ground truth; never re-infer the phase from a short paste.
2. Draft using `scripts/live-conversation-playbook.md`, checking its Advance Triggers first (6+ exchanges without an ask forces the ask; buying signals jump to Phase 6).
3. `python scripts/convo.py upsert <channel> <identity_or_url> --stage <s> --thread-file <merged> --last-draft "<reply>"` after drafting; set `--meeting asked/booked/declined/ghosted` as the thread resolves.

`list` shows the whole pipeline (`python scripts/convo.py list`). The dashboard (projects/sales-playbook-dashboard) reads and writes the same table, so the memory is shared. Self-check: `python scripts/test_convo.py`.

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
│   ├── opener-archetypes.md                # 5 archetypes, variants each (canonical opener list)
│   ├── voss-calibrated-questions.md        # Question bank by phase
│   ├── hormozi-value-equation.md           # How to frame every proof
│   ├── hormozi-selling-principles.md       # NEW — the mindset/posture layer (21 beliefs, re-voiced)
│   ├── objection-psychology.md             # NEW — diagnose the distortion (3 distortions × 5 manifestations)
│   └── objection-riffs.md                  # 10 objections × cited response (phrase-level, tagged to the taxonomy)
├── scripts/
│   ├── linkedin-cold-dm-sequence.md        # 4-touch with archetype rotation
│   ├── instagram-cold-dm-sequence.md       # IG-native voice
│   ├── facebook-cold-dm-sequence.md        # FB group-context outreach (Q8 research)
│   ├── live-conversation-playbook.md       # 6 phases + Advance Triggers + distortion-diagnosis branch
│   ├── discovery-call-script.md            # 30-min Ops Teardown (+ 3 pre-yes beliefs)
│   ├── convo.py                            # conversation memory CLI (Supabase)
│   ├── schema.sql                          # one-time Supabase table setup
│   └── test_convo.py                       # self-check for convo.py
├── offer/
│   ├── agency-to-agency-positioning.md     # NEW — white-label wedge for agencies (PRIMARY ICP)
│   ├── ai-automation-positioning.md        # Founder/SMB wedge (secondary ICP)
│   └── proof-bank.md                       # Results by industry/pain
├── references/
│   ├── research-synthesis.md               # Cited Q1-Q12 research + Live Query Additions
│   ├── what-not-to-do.md                   # Banned phrases + patterns (Tier 1-7, incl. Hormozi-brash)
│   ├── notebook-live-query.md              # LIVE FALLBACK: ask the sales notebook on a miss
│   ├── ask-timing.md                       # "Ask by exchange 6" data justification
│   ├── how-to-use.md                       # Usage modes + daily workflow
│   └── worked-example-{linkedin,instagram,cold-email}.md   # End-to-end teaching walkthroughs
└── _research/                              # Audit trail: sources.json, q*.json, hormozi-4hr-sales-notes.md
```

## How to use this skill in a request

When Aleem asks for any sales asset:
1. Read the relevant script file in full
2. Pick the positioning track by ICP: agency prospect → `offer/agency-to-agency-positioning.md`; founder/SMB → `offer/ai-automation-positioning.md`
3. Pull the right archetype from `opener-archetypes.md`
4. Pull a matching proof from `proof-bank.md` (by industry)
5. **For an objection: diagnose the distortion first** (`frameworks/objection-psychology.md`) — which layer (circumstances/others/self) — then pull the matching overcome from `objection-riffs.md`. Set the posture from `hormozi-selling-principles.md` (back foot, one calm angle, resolve the specific concern).
6. Pass through the `what-not-to-do.md` filter (now Tier 1-7, incl. Hormozi-brash) before returning the message
7. If a call ask is involved, use the anchored-deliverable phrasing from `discovery-call-script.md`

Don't paraphrase the bans or the call-ask templates — copy them verbatim. They were chosen for specific psychological reasons documented in their files.

## When the playbook doesn't have it (live fallback)

For a sales KNOWLEDGE question (an opener/reply/closing benchmark, an objection nuance, a discovery-call detail, "what does the research say about X") that the framework/script files and `references/research-synthesis.md` don't confidently answer: **query the live sales NotebookLM notebook before guessing.** Follow `references/notebook-live-query.md` — ask the notebook, present the cited answer, then append the finding to `references/research-synthesis.md` under its "Live Query Additions" section so it's reusable next time. Only after a genuine notebook miss do you say the corpus doesn't cover it. (This is for facts/knowledge — generating the actual DM/script still works from the archetypes + scripts above.)

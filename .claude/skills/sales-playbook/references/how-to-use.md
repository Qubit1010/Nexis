# How to Use the Sales Playbook

Three modes: automatic (already wired into other skills), on-demand (you ask, the right file gets pulled), and manual reference (you read the files yourself).

---

## 1. Automatic — already wired into existing skills

The `linkedin-outreach` and `instagram-outreach` generators now pull from the playbook on every batch run. No additional action needed. When you run:

- `"scrape linkedin leads"` then `"generate connection messages"` → the new archetype rotation kicks in (Welsh / Holland / Braun / etc.)
- `"scrape instagram leads"` then `"generate instagram DMs"` → IG-native voice + caption-aware archetypes

Output now varies across prospects — no more "Hey [Name], it looks like..." every time.

---

## 2. On-demand — you ask, the skill triggers automatically

Just say what you need. The skill description triggers on intent. Examples:

| What you say | What you get |
|---|---|
| `"draft a LinkedIn DM to [paste prospect bio]"` | Archetype-rotated DM grounded in the playbook |
| `"they replied [paste their message] - what do I say?"` | Next move from `scripts/live-conversation-playbook.md` |
| `"prospect said 'we already have someone' - how do I respond?"` | Cited objection riff (Becc Holland's praise-then-differentiate move) |
| `"prep me for a discovery call with [company]"` | Combines `scripts/discovery-call-script.md` + prospect research |
| `"write my Touch 3 for Sarah at [company]"` | DM 3 with anchored Ops Teardown ask, not "worth a quick chat" |
| `"how do I close this prospect on $5k/month?"` | Hormozi two-yes structure + Frank Kern risk reversal |
| `"what's my opener for [prospect]"` | Picks the right archetype based on signal you provide |

You don't need to type "use the sales-playbook" — intent-match handles it.

---

## 3. Manual reference — when you want to study or print

```
sales-playbook/
├── frameworks/
│   ├── opener-archetypes.md           ← print this, keep on desk
│   ├── voss-calibrated-questions.md   ← the 15 questions to memorize
│   ├── objection-riffs.md             ← reference before every call
│   └── hormozi-value-equation.md      ← how to think about price
├── scripts/
│   ├── linkedin-cold-dm-sequence.md   ← daily LinkedIn workflow
│   ├── instagram-cold-dm-sequence.md  ← daily IG workflow
│   ├── live-conversation-playbook.md  ← when someone replies
│   └── discovery-call-script.md       ← print before every call
├── offer/
│   ├── ai-automation-positioning.md   ← your one-liner + tiers
│   └── proof-bank.md                  ← Steve / Andrey / Mikey
└── references/
    ├── what-not-to-do.md              ← scan before sending anything
    ├── research-synthesis.md          ← source-of-truth for every claim
    └── how-to-use.md                  ← this file
```

---

## The typical daily workflow

**Morning (15 min):**
- `"scrape 30 new linkedin leads in [niche]"` → automated
- `"generate connection messages"` → uses new archetype rotation automatically
- Review the output in the sheet, send the ones that pass the "would a real human send this?" test

**Midday (live replies):**
- When a prospect replies: `"they said [X] - what's next?"` → pulls from live-conversation-playbook
- When they raise an objection: `"how do I handle [objection]?"` → cited riff from objection-riffs

**Before a discovery call:**
- `"prep me for the call with [prospect]"` → combines discovery-call-script frame with prospect research
- The matching peer surfaces from the proof bank (Steve / Andrey / Mikey based on their pain)

**After the call:**
- `"draft the follow-up contract email for [prospect]"` → uses the same-day send-through template from `discovery-call-script.md`

---

## Three highest-leverage actions to make this work harder

1. **Record a 60-sec Loom** of Steve's social posting workflow. Becomes the highest-converting Touch 1 attachment per the research (Archetype 4 — Loom-First). One recording, infinite reuse.

2. **Run a batch of 10 LinkedIn messages dry-run** now to see the archetype variety:
   ```
   "generate linkedin messages --dry-run --limit 10"
   ```
   If the output reads like 10 different humans, ship it. If it still smells like cadence, surface it and the prompts get tuned.

3. **Add Mikey/Andrey direct testimonials** to `offer/proof-bank.md` when you have time. Steve's testimonial is the strongest weapon you have — having three is 3x.

---

## The principle

The playbook is built to disappear into the background. You describe what you need — the right file gets pulled, the right archetype gets picked, the right framework gets applied. The cited research (77 sources synthesized in `references/research-synthesis.md`) backs every claim.

If a script feels wrong, the fix is usually in the source — adjust the prompt in `linkedin-outreach/scripts/generate_messages.py` or `instagram-outreach/scripts/generate_messages.py`, or update the archetype rotation weights. Everything flows from this one skill.

---
name: brand-voice
description: >
  Use to BUILD or AUDIT how a brand sounds and what it says: brand voice, tone of voice,
  messaging framework, messaging house, vocabulary, writing mechanics, and where in scope brand
  naming and taglines. This is the execution skill that produces the artifact, not the advice
  skill.
  Triggers on: brand voice, voice guidelines, tone of voice, tone guidelines, voice and tone,
  define their voice, voice spec, how should they sound, messaging framework, messaging house,
  message hierarchy, core message, messaging pillars, proof points, brand vocabulary, words we
  use, words we never use, writing style for the brand, copy guidelines, editorial guidelines,
  brand naming, name this product, name candidates, tagline, taglines, slogan, strapline,
  audit their voice guide, review this tone of voice doc, their copy sounds inconsistent, every
  page sounds different, our writers all sound different, ghostwriting voice, founder voice,
  my writing voice, make it sound like me.
  Works from whatever exists: the client's live copy, a Google Doc, a PDF or DOCX voice guide,
  pasted text, a website URL, transcripts and voice notes, or a client-projects slug. Consumes
  13-brand-strategy.md for personality and positioning and 08-audience-persona.md for customer
  language rather than re-deriving them.
  Outputs client-projects/<slug>/14-brand-voice.md: voice dimensions as scales with exclusions
  named at both ends rather than adjectives, tone shifts per real context, a messaging
  framework, use and never-use vocabulary, sentence mechanics, and before-and-after rewrites of
  the client's own copy where every change traces to a stated rule. Audit mode instead produces
  a six-row Strong/Workable/Weak/Missing scorecard.
  Numbers cited as [sN] resolve via branding-advisor's corpus. It does not default to
  "be more conversational", because informal brand communication can backfire, and it states
  plainly that a name search is not a trademark clearance.
  Scope is deliberately the verbal identity only. For positioning, personality, promise, story
  or values use brand-strategy. For colour, typography, logo or the guidelines document use
  brand-visual. For actually writing posts or articles in the finished voice use blog-writer,
  content-engine or client-content-creator. For explaining or diagnosing branding use
  branding-advisor. For cold email and sales copy use marketing-advisor or sales-playbook.
argument-hint: [client name, URL, doc, or client-projects slug - optionally "audit" or "founder"]
---

# Brand Voice

Builds or audits how a brand sounds: the voice spec, the messaging, the vocabulary, and where
in scope the name and tagline.

**`branding-advisor` knows things. This skill does things.** If the ask is "explain this to me"
rather than "do this for a client", route there.

---

## Where this sits

```
brand-strategy       ->  brand-voice      ->  brand-visual
  13-brand-strategy       14-brand-voice       15-brand-visual-identity
  who the brand is        how it sounds        what it looks like

                          |
                          v
              blog-writer / content-engine / client-content-creator
              (the skills that write in the voice this defines)
```

It is the verbal identity **and nothing else**. It defines the voice; it does not write the
content.

---

## Operating principles (read once)

- **Operability is the bar.** A freelance writer who has never met the client should produce
  on-brand copy from this document on the first attempt. If they cannot, it failed, however
  well it describes the brand.
- **Scales, not adjectives.** "Friendly but professional" excludes nothing and fits most B2B
  brands. Every dimension names what it rules out at both ends.
- **Never default to conversational.** Informal brand communication can backfire `[C]` [s79].
  A casual register is a decision to be argued, not the safe option.
- **Read their actual copy before writing a word of the spec.** A voice guide written without
  reading the client is prescription dressed as description, and it should be labelled that way
  when it happens.
- **The rewrites are the proof.** Any edit that cannot be traced to a stated rule means the
  guide has a hole.

---

## Boundaries / handoffs (important)

| Hand off to | For |
|---|---|
| `branding-advisor` | Explaining a concept, fact-checking a claim, diagnosis |
| `brand-strategy` | Positioning, personality, promise, story, values |
| `brand-visual` | Colour, typography, logo, guidelines assembly |
| `blog-writer` / `content-engine` / `client-content-creator` | Writing actual content in the finished voice |
| `strategic-foundation` | Audience personas, ICP, customer language research |
| `marketing-advisor` / `sales-playbook` | Cold email, ads, sales copy, DMs |
| `podcast-repurposer` | Per-client voice files for repurposing work |

State the handoff when you make it. Do not silently stop.

---

## Context to load first

Always: `references/method.md` (build) or `references/review-rubric.md` (audit).

Then `references/report-structure.md` when writing, and
`.claude/skills/branding-advisor/references/what-not-to-do.md` before delivering.

**Max 3 reference files per invocation.**

---

## Mode Detection

| Mode | Trigger keywords | Load |
|---|---|---|
| **build** (default) | "write the voice guidelines", "define their tone", no existing guide | `method.md` |
| **audit** | "audit", "review this voice guide", an existing guide supplied | `review-rubric.md` |
| **messaging** | "messaging framework", "messaging house", "core message" | `method.md` Phase 5 |
| **naming** | "name this", "name candidates", "tagline", "slogan" | `method.md` Phase 7 |
| **founder** | "my voice", "sound like me", "ghostwriting", "founder voice" | `method.md` + Subject: founder |

If ambiguous, pick the more specific. Founder is a subject modifier and combines with build or
audit.

---

## Workflow

Full detail in `method.md`. In short:

1. **Resolve the input** into text.
2. **Collect what they already sound like**: transcripts, sent emails, body copy, support
   replies. Read it in one sitting. This phase decides whether the document is descriptive or
   invented.
3. **Read upstream**: `13` for personality and positioning, `08` for customer language.
4. **Ask only what you cannot infer.** Batched, one round, 2-4 max.
5. **Set dimensions as scales with exclusions.**
6. **Tone shifts, messaging, vocabulary, mechanics.**
7. **Prove it** with before-and-after rewrites of their own copy, each traceable to a rule.
8. **Naming and taglines** only if in scope.
9. **Kill list, write the file, summarise, offer `brand-visual`.**

---

## Writing Rules

**Internal:** direct, bullets, lead with the recommendation.

**Client-facing:** operator, not consultancy. **Never mention NexusPoint or Aleem** in the
document.

Both: no emojis, no em dashes in body text.

Note the recursion: this document is itself a piece of writing about writing. If it violates
its own dimensions it will not be taken seriously, and rightly so.

---

## Edge Cases

| Scenario | Action |
|---|---|
| Client has almost no existing copy | Say so. Mark the document prescriptive rather than descriptive. It changes what it is |
| No `13-brand-strategy.md` exists | Offer to run `brand-strategy` first. If declined, derive working traits and label them assumptions |
| Client asks for "friendly but professional" | Push back with the exclusion test. Convert to scales with both ends named |
| Client wants a casual voice for a serious purchase | Raise the backfire finding `[C]` [s79] once, then follow their call and note it |
| A rewrite improves copy in a way no rule explains | The guide is incomplete. Add the rule, redo the rewrite |
| Asked to write a blog post or caption | Route to `blog-writer` or `client-content-creator`. This skill defines the voice, it does not write the content |
| Asked to confirm a name is available | State exactly what was checked. **A search is not a trademark clearance.** Point at the real registry |
| Asked for a tagline's expected recall lift | Only one tagline finding exists in this corpus `[C]` [s97]. No lift figures. Say so |
| The guide exists and nobody follows it | Different failure. Route to adoption: who writes, what they reach for, what the guide fails to answer |
| Founder voice, client wants it "more polished" | Warn that polishing out the tells is what makes ghostwriting detectable. Their call |

---

## Reference Map

```
references/
├── method.md             THE PIPELINE, phases 0-8 + the founder variant. Load first in build
├── review-rubric.md      Audit mode: 6-row scorecard, the five-minute apply test
└── report-structure.md   Deliverable section order for 14-brand-voice.md, each section with
                          its "fails when" test
```

No `_research/` here on purpose. `[sN]` resolves via
`.claude/skills/branding-advisor/_research/sources.json`, 260 sources, 132 confirmed. Run
`branding-advisor/_research/gather.py verify` after any citation edit; it checks this skill's
`references/` too.

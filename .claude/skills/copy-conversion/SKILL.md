---
name: copy-conversion
description: "Use to WRITE or AUDIT copy whose job is to make someone act: landing and sales pages, homepages, email sequences, ads, product descriptions, headlines, hooks, CTAs, microcopy, popups. Execution skill, not the advice one. Consumes the brand voice, strategy and persona files rather than re-deriving them; writes client-projects/<slug>/17-conversion-copy.md. Audit mode returns a Strong/Workable/Weak/Missing scorecard. For why copy works use copywriting-advisor; for non-conversion formats, content-production; for a full article, blog-writer."
argument-hint: [client name, URL, doc, or client-projects slug - optionally "audit"]
---

# Copy Conversion

Writes or audits the copy that has to make someone act.

**`copywriting-advisor` knows things. This skill does things.** If the ask is "explain this
to me" or "is that statistic real" rather than "write this for a client", route there.

---

## Where this sits

```
strategic-foundation  ->  brand-strategy  ->  brand-voice  ->  copy-conversion
  07 / 08                   13                 14              17-conversion-copy
  who the customer is       what it stands     how it          the words that
  and what we sell          for                sounds          ask for the action

                                                    |
                                                    +--> blog-writer
                                                         (articles, not pages)
```

It writes the words. It does not define the voice, and it does not decide the offer.

---

## Operating principles (read once)

- **Take the upstream documents, do not re-derive them.** If `13` and `14` exist, positioning
  and voice are settled. Re-deriving them here forks the client's brand into two slightly
  different versions.
- **Specificity is the lever.** "Save time on reporting" fails. "Cut weekly reporting from
  four hours to fifteen minutes" passes. Almost every weak line in client copy is a specific
  claim someone softened because they could not prove it.
- **One page, one action.** A second call to action of equal weight is a decision to argue
  for, never a default.
- **Frameworks are scaffolds, not evidence.** AIDA, PAS, BAB, 4Ps, 4Us, FAB and
  Story-Problem-Solution-CTA are useful ways to arrange an argument. None of them is a
  measured mechanism, and no source in the corpus tests one against another. Name the frame
  in use; never present it as the reason the copy will work.
- **Never invent proof.** Not a testimonial, not a statistic, not a customer name, not a
  result, not a logo. Placeholders are fine and must be visibly marked as placeholders.
- **Never promise a lift figure.** We do not know it, most reported wins do not replicate,
  and the client will hold us to the number.
- **Use the craft tier for HOW, never for WHETHER.** `[K]` sources in the corpus - teardowns,
  swipe files, microcopy galleries, per-platform ad guides, VeryGoodCopy's micro-lessons -
  are there to inform technique, structure and format conventions. They may never be quoted
  to a client as evidence that something works. If a craft source states a number, it is
  unverified by definition: the craft passes produced "you have 2 seconds", "78% of agencies
  use generative AI" and "microcopy is the 3-5 most-read words", none of which has a primary
  source.

---

## Boundaries / handoffs (important)

| Hand off to | For |
|---|---|
| `copywriting-advisor` | Explaining a concept, fact-checking a claim, diagnosing why copy underperforms |
| `brand-voice` | Defining the voice, tone, messaging framework, naming, taglines |
| `brand-strategy` | Positioning, personality, promise, values |
| `strategic-foundation` | The UVP, the offer, personas, customer research |
| `blog-writer` | Long-form articles and blogs, including client blogs and AEO/GEO |
| `seo-onpage` / `seo-authority-ai` | Page titles and metas as SEO artifacts; AI-search visibility |
| `sales-playbook` | Aleem's own cold email, DMs and outreach, where he is the sender rather than the client |
| `proposal-generator` | Client proposals and offer construction |
| `content-engine` / `post-creator` / `carousel` | Aleem's own social content: idea sourcing, the posting schedule, the repurposing flywheel. **Formatting a post for a platform lives HERE** (`platform-formatting.md`); what to post about lives there |
| `social-media-advisor` | How a platform *ranks and distributes* a post, account and follower growth, engagement strategy, profile optimisation, community management, social listening. **Formatting still lives HERE**: character limits, the "see more" cut, per-platform structure. That skill explains the system the formatted post lands in |
| `client-content-creator` | A broad multi-piece content package rather than conversion assets |

State the handoff when you make it. Do not silently stop.

---

## Context to load first

Always: `references/method.md` (build) or `references/review-rubric.md` (audit).

Then `references/report-structure.md` when writing, and
`.claude/skills/copywriting-advisor/references/what-not-to-do.md` before delivering.

**Max 3 reference files per invocation.**

---

## Mode Detection

| Mode | Trigger keywords | Load |
|---|---|---|
| **build** (default) | "write the copy", "we need a landing page", no existing copy supplied | `method.md` |
| **audit** | "audit", "review this copy", "why isn't this converting", existing copy supplied | `review-rubric.md` |
| **single-asset** | one named asset: "just the headline", "rewrite the CTA" | `method.md` Phases 4-6 only |
| **format** | "how should this look on LinkedIn", "format this for Instagram", a platform or a character limit named | `platform-formatting.md` |
| **founder** | the subject is a person, not a company | `method.md` + the founder variant |

If ambiguous, pick the more specific. Founder is a subject modifier and combines with build
or audit.

---

## Workflow

Full detail in `method.md`. In short:

1. **Resolve the input** into text.
2. **Read upstream**: `14` voice, `13` exclusions, `08` customer language, `07` UVP. **If
   they are missing, say so and offer to build them first**, then proceed either way and
   label the gaps as assumptions.
3. **Read their live copy and inventory the proof they actually have.** This decides what the
   copy is allowed to claim.
4. **Ask only what you cannot infer.** Batched, one round, 2-4 max.
5. **Spec each asset**: one action, reader state, the one belief, the proof, the frame.
6. **Write it complete**, in their voice, then run the anti-AI-tell pass.
7. **Proof pass**: fact / assumption / unprovable. Cut the unprovable.
8. **Write the file, summarise what was cut, offer the next asset.**

---

## Writing Rules

**Internal:** direct, bullets, lead with the recommendation.

**Client-facing:** operator, not consultancy. **Never mention NexusPoint or Aleem** in the
document.

Both: no emojis, no em dashes in body text.

Note the recursion, as `brand-voice` does: this is copy about copy. Vague, unprovable claims
in the deliverable discredit the deliverable.

---

## Edge Cases

| Scenario | Action |
|---|---|
| No `14-brand-voice.md` | Say so, offer `brand-voice` first. If declined, derive a working voice from their live copy and label it an assumption |
| No `07-strategic-foundation.md` | Say so, offer `strategic-foundation`. Without a UVP the copy will invent a differentiator that does not survive a sales call |
| Client has no proof points at all | This is the finding. Say it plainly, write the copy the proof supports, and list what to collect. Do not paper over it with adjectives |
| Asked to write a testimonial | **Refuse.** Offer to draft interview questions that get a real one, or a marked placeholder |
| Asked for a specific statistic to use | Only from the corpus or a live query, cited. Never invented, and never a vendor number presented as measured |
| Asked to guarantee a conversion lift | Decline the number, give the argument for the change, state what would need to be true to measure it |
| Client wants a countdown timer that resets | Flag the legal exposure per `what-not-to-do.md`, offer a real deadline instead. Their call, noted in writing |
| "Make it more conversational" | Not automatically right. `14` decides register, and informal copy can backfire in high-consideration purchases |
| Asked for 50 headline variants | Give a small number of genuinely different angles. Volume is handing the client the work |
| Copy is fine, the offer is the problem | Say so. Route to `strategic-foundation` or `proposal-generator`. Copy cannot fix an offer nobody wants |
| Asked to write a blog or article | Route to `blog-writer` - it owns AEO/GEO and long-form structure |

---

## Reference Map

```
references/
├── method.md             THE PIPELINE, phases 0-7 + the founder variant. Load first in build
├── review-rubric.md      Audit mode: 7-row scorecard, the five-second test, the measurement warning
├── report-structure.md   Deliverable section order for 17-conversion-copy.md, each section with
│                         its "fails when" test, plus the per-asset table
└── platform-formatting.md  Format mode: what each platform does to your text, what each topic
                          shape requires, and the three things that actually generalise
```

No `_research/` here on purpose. `[sN]` resolves via
`.claude/skills/copywriting-advisor/_research/sources.json`. Run
`copywriting-advisor/_research/gather.py verify` after any citation edit; it checks this
skill's `references/` too.

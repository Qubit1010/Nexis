# Method — building conversion copy

The pipeline. Load this first in build mode.

Output: `client-projects/<slug>/17-conversion-copy.md`, structured per `report-structure.md`.

**The bar is that the copy could ship tomorrow.** Not a strategy document about what the copy
should say - the actual words, in the client's voice, with every claim backed by something
real. A deliverable the client has to rewrite before using has failed, however well it
reasons.

---

## Phase 0 — Resolve the input

Same dispatch as the sibling skills. All run **UNSANDBOXED**.

| What they gave | Resolve with |
|---|---|
| Google Doc URL or ID | `python .claude/skills/client-onboarding-workflow/scripts/extract_proposal.py "<url_or_id>"` |
| PDF / DOCX / PPTX | `python .claude/skills/to-markdown/scripts/convert.py "<path>"` then `Read` the `.md` |
| `.md` / `.txt` / pasted text | `Read` it, or use the paste inline |
| Business website URL | `python .claude/skills/web-scraper/scripts/scrape.py --url "<url>" --depth crawl --pages 12 --extract raw` |
| Name only | `python .claude/skills/research/scripts/research.py --query "<name> <industry>" --depth medium --mode entity` then crawl |
| `client-projects/<slug>` | `Read` the numbered files directly, then still crawl the live site (Phase 2) |

---

## Phase 1 — Read upstream and take, do not re-derive

This is the phase that separates this skill from a generic copywriting prompt. These
documents already exist for a reason. Re-deriving positioning here produces a second,
slightly different strategy and quietly forks the client's brand.

| File | Take |
|---|---|
| `14-brand-voice.md` | Voice dimensions and their marked positions, tone shifts per context, the use / never-use vocabulary, sentence mechanics. **These are constraints, not suggestions.** |
| `13-brand-strategy.md` | Positioning, personality traits, the promise, and critically the **"what this rules out"** section - copy that violates it is off-brand even if it converts |
| `08-audience-persona.md` | Verbatim customer language, the questions they actually ask, objections in their own words. This is the raw material for headlines and objection handling |
| `07-strategic-foundation.md` | The UVP and the business model, so the offer in the copy matches the offer that exists |

### When they are missing

**Say so before writing, and offer to build them.** In order of how much damage the gap does:

| Missing | Consequence | Offer |
|---|---|---|
| `14-brand-voice.md` | The copy will sound like the agency, not the client. This is the single most common way client copy gets rejected | Run `brand-voice` first |
| `07-strategic-foundation.md` | No UVP means the copy invents a differentiator, and invented differentiators do not survive a sales call | Run `strategic-foundation` first |
| `13-brand-strategy.md` | No exclusions means nothing stops the copy drifting generic | Run `brand-strategy` first |
| `08-audience-persona.md` | Customer language gets invented rather than mined, which is the difference between copy that resonates and copy that sounds like marketing | Run `strategic-foundation --mode persona` |

If Aleem declines, **proceed** - do not stall the deliverable. Derive working substitutes from
the client's live copy and the market, and record every one in the fact table at the top of
the document as `[assumption]`, not `[verified]`. The client should be able to see exactly
which parts of their copy rest on something they told us and which rest on our inference.

---

## Phase 2 — Read their live copy before writing any

Non-negotiable, and the phase most often skipped under deadline. Crawl the site and read:

1. **The pages you are replacing.** You cannot argue a rewrite is better without knowing what
   the current one was trying to do.
2. **Their own words about themselves** - About page, founder letters, job postings. Job
   postings are unusually honest: they describe the business without a customer reading.
3. **Proof that already exists** - case studies, testimonials, numbers, logos, certifications,
   guarantees. Inventory this now. It determines what the copy is allowed to claim.
4. **What competitors say**, enough to know which claims are table stakes in the category.
   A differentiator every competitor also states is not a differentiator.

Note what is missing as much as what is there. "No proof points anywhere on the site" is a
finding that changes the deliverable, not an inconvenience to write around.

---

## Phase 3 — Ask only what you cannot infer

`AskUserQuestion`, **batched, one round, 2-4 maximum.**

Worth asking, because no artifact contains them:

- What is the single action this page or asset has to produce? If the answer is more than
  one thing, that is the finding.
- What can we claim that is **checkably true** - real numbers, real timeframes, real
  guarantees? And what are we legally or commercially unable to say?
- What has been tried already and did not work?
- Who is the copy competing against in the reader's head - a competitor, a spreadsheet, doing
  nothing?

Not worth asking: "who is your target audience" when `08` exists, or "what's your tone" when
`14` exists. Asking a question the client already answered in a document they paid for reads
as not having read it.

---

## Phase 4 — Spec each asset before writing it

Per `report-structure.md`. For every asset, fix these before drafting a word:

- **One action.** Named, singular. A second CTA is a decision to argue for, not a default.
- **The reader's state on arrival** - what they already know, what they just clicked, what
  they are afraid of. Copy that ignores traffic source writes to nobody.
- **The one thing they must believe** to take the action. Everything in the asset either
  supports that or is cut.
- **The proof carrying it** - a fact, a number, a named customer, a demonstration. If the
  only available proof is an adjective, the asset has a proof problem, not a wording problem.
- **The structural frame** (AIDA, PAS, BAB, FAB, Story-Problem-Solution-CTA). Name it, and
  see the warning in `SKILL.md`: these are scaffolds for arranging an argument, not evidence
  that the arrangement works.

---

## Phase 5 — Write

In the client's voice, from the vocabulary in `14`, using the customer's language from `08`.

Write the whole asset, not fragments. A headline without the subhead and CTA underneath it
cannot be judged, because the reader never encounters it alone.

**Give options only where a real decision exists.** Three headline variants is useful when
they represent genuinely different angles. Ten variants of the same sentence is not a choice,
it is a way of handing the client the work.

Then run the anti-AI-tell pass with
`.claude/skills/blog-writer/references/human-tone-rules.md` - phrase audit, cadence, the
read-aloud check. It is the same problem there and here, so it is not restated in this skill.

---

## Phase 6 — Proof pass (the gate)

Walk every claim in the finished copy and mark it:

| Mark | Meaning | Action |
|---|---|---|
| **Fact** | Traceable to something the client gave us or that is publicly checkable | Keep |
| **Assumption** | Plausible, unverified | Flag inline for the client to confirm or kill before publishing |
| **Unprovable** | Cannot be substantiated at all | **Cut it.** Do not soften it into a weasel phrase - "helping businesses achieve more" is what an unprovable claim becomes when nobody is willing to delete it |

**Never invent a testimonial, a statistic, a customer name, a result, or a logo.** Placeholder
proof is acceptable and must be visibly marked as a placeholder the client has to fill. Fake
proof in a deliverable is the one failure that ends a client relationship rather than
starting a revision round.

For testimonials and endorsements specifically, note the FTC constraints in
`copywriting-advisor/references/what-not-to-do.md`. This is law, not style.

---

## Phase 7 — Deliver

Write `client-projects/<slug>/17-conversion-copy.md` per `report-structure.md`.

Then, in the handoff summary:

1. What was written, and the one action each asset drives.
2. **What was cut and why** - the unprovable claims. This is the most valuable part of the
   summary and the part clients push back on, so it goes in writing.
3. Every `[assumption]` that needs confirming before publishing.
4. What could not be written because a proof point does not exist yet, and what would have to
   be true to write it.
5. What to measure, and honestly - see the measurement warning in `review-rubric.md`. Do not
   promise a lift figure.

---

## Founder / personal-brand variant

When the subject is a person rather than a company (a founder's own landing page, their
newsletter, their offer), the changes are small but real:

- The voice source is the founder's, and it is **descriptive** - captured from how they
  already talk, not designed. `14-brand-voice.md` in founder mode already holds this.
- Proof is personal: their track record, their clients, their numbers. Same rule, no borrowed
  credibility.
- The risk is different. Copy that overclaims for a company embarrasses a brand; copy that
  overclaims for a person is attached to them permanently and is trivially checkable by
  anyone who meets them.

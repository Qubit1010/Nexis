# Method — producing a content asset

The pipeline. Load this first in build mode, alongside the one `format-specs/` file for the
format being produced.

Output: `client-projects/<slug>/content/<format>-<slug>.md`.

**The bar is that it could publish tomorrow.** Not an outline of what the piece should cover,
unless an outline is what was asked for. The actual words, in the client's voice, with every
claim backed by something real.

---

## Phase 0 — Route check

Before anything else. If another skill owns the format, hand off and stop.

The table lives in `SKILL.md`. The two that get confused most:

- **Guides.** On-site pillar article → `blog-writer`. Gated downloadable → here.
- **Case studies.** NexusPoint's own project write-up → `case-study-generator`. A case study
  about *the client's* customer → here.

Writing a blog post here rather than routing it means producing an article with none of
`blog-writer`'s AEO/GEO corpus behind it. That is a worse deliverable, not a faster one.

---

## Phase 1 — Resolve the input

All run **UNSANDBOXED**.

| What they gave | Resolve with |
|---|---|
| Google Doc URL or ID | `python .claude/skills/client-onboarding-workflow/scripts/extract_proposal.py "<url_or_id>"` |
| PDF / DOCX / PPTX | `python .claude/skills/to-markdown/scripts/convert.py "<path>"` then `Read` the `.md` |
| `.md` / `.txt` / pasted text | `Read` it, or use the paste inline |
| A transcript | `Read` it. If the ask is short-form pieces from a podcast, route to `podcast-repurposer` |
| Source URL to build from | `python .claude/skills/web-scraper/scripts/scrape.py --url "<url>" --extract raw` |
| Topic only | `python .claude/skills/research/scripts/research.py --query "<topic>" --depth medium` |
| `client-projects/<slug>` | `Read` the numbered files, then still read their live channels |

---

## Phase 2 — Read upstream and take

| File | Take |
|---|---|
| `18-content-strategy.md` | **Which pillar this serves and what the piece is supposed to do.** A piece with no stated job becomes a summary of a topic |
| `14-brand-voice.md` | Voice dimensions and their marked positions, tone shift for this context, the use / never-use vocabulary. **Constraints, not suggestions** |
| `13-brand-strategy.md` | Positioning, personality, and the "what this rules out" section |
| `08-audience-persona.md` | The audience's own words and the questions they actually ask. Headlines and objections come from here, not from invention |
| `07-strategic-foundation.md` | The UVP, so what the piece promises matches what exists |

### When they are missing

Say so, offer the producing skill, then **proceed** with the gaps recorded as `[assumption]`.

| Missing | Consequence | Offer |
|---|---|---|
| `14-brand-voice.md` | The piece sounds like the agency. The most common reason client work gets rejected | `brand-voice` |
| `18-content-strategy.md` | No stated job for the piece. Ask one question instead, then proceed | `content-strategy` |
| `08-audience-persona.md` | Audience language gets invented | `strategic-foundation --mode persona` |

---

## Phase 3 — Load the format spec

From `content-advisor/references/format-specs/`. One file, the one covering this format.

Take from it: **structure**, **the opening**, **length and pacing**, **2026 optimization**,
**distribution**, and **fails when**. Every one of those carries an evidence tier. Note which
parts of the spec are `[C]` confirmed, which are `[P]` practitioner convention, and which are
`[K]` craft, because that decides how firmly you follow them and how you describe them if the
client pushes back.

**Do not write from a general sense of how the format goes.** That is what this phase replaces.

---

## Phase 4 — Inventory the proof

Before writing a word, list what the client can actually evidence: numbers they have measured,
named customers who agreed to be named, results with a source, certifications, and anything a
regulator would ask them to substantiate.

**This decides what the piece is allowed to claim.** A whitepaper whose central argument rests
on a number the client cannot produce is not a draft, it is a liability.

Where a claim is needed and no proof exists, either cut it or mark it clearly as a placeholder
the client must fill. **Never invent a statistic, a customer quote, a named reference or a
result.** Never soften an unsourced claim into "studies show".

---

## Phase 5 — Ask what you could not infer

Batch **2 to 4 questions**, once. Anything answerable from Phases 1-4 is not a question.

Typically: who exactly this is for and at what awareness level, what the one action after
reading is, what proof they are willing to publish, and any claim their legal or compliance
side will not allow.

---

## Phase 6 — Spec the piece before writing it

Five lines, agreed in your own head before drafting:

1. **The one action** it should produce.
2. **The reader's state** when they arrive, and what they already believe.
3. **The one belief** the piece has to change.
4. **The proof** carrying that belief.
5. **The frame** — the format's structure from Phase 3, chosen deliberately.

If the piece cannot answer these five, it will be a topic summary, which is the default failure
mode of every format in this skill.

---

## Phase 7 — Write it complete

Not an outline. Not a sketch with brackets where the hard parts go. The whole thing, at the
length the format's job requires rather than a word target.

Length is set by what the argument needs. "Shorter is better" is an assumption that has been
tested directly against it, so do not truncate on principle, and do not pad to look
substantial either.

---

## Phase 8 — Proof pass

Go through the draft and mark every claim:

- **fact** — traceable to something real, with the source named
- **assumption** — reasonable, derived, and labelled as such
- **unprovable** — cut it, or replace it with something the client can stand behind

Any platform specification quoted carries the date it was verified.

---

## Phase 9 — Human-tone pass

Run `blog-writer/references/human-tone-rules.md` over the draft. Read it aloud. Anything you
would not say out loud gets rewritten.

This is not cosmetic. Content that reads as machine-written gets rejected regardless of how
correct it is, and in 2026 clients are unusually good at spotting it.

---

## Phase 10 — Deliver

Write to `client-projects/<slug>/content/<format>-<slug>.md`.

Then say, briefly and outside the file: what the piece assumes, what proof the client still
needs to supply, and where it goes next — the distribution row in `18-content-strategy.md`, or
the skill that produces the derivative assets.

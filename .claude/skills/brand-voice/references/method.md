# Method — building a brand voice

The pipeline. Load this first in build mode.

Output: `client-projects/<slug>/14-brand-voice.md`, structured per `report-structure.md`.

**The bar is operability.** A freelance writer who has never met the client should produce
on-brand copy from this document on their first attempt. Every phase serves that test, and
Phase 6 is the test.

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

---

## Phase 1 — Collect the corpus of what they already sound like

**This is the phase that decides whether the document is descriptive or invented**, and it is
the one most often skipped.

Gather everything they have actually written, in this order of value:

1. **Founder transcripts, voice notes, recorded calls.** The most honest signal, because nobody
   performs a brand voice while talking.
2. **Sent emails and proposals.** Written under real pressure to a real person.
3. **Website body copy**, excluding the homepage hero, which is usually the most
   agency-mediated text they own.
4. **Social posts**, if they write them personally.
5. **Support replies**, which show the voice under stress.

Read it all in one sitting and note: sentence length, contractions, hedging, humour, how they
explain something technical, how they disagree, what they apologise for.

**If they have almost no existing copy**, say so now and mark the document prescriptive rather
than descriptive. It changes what it is, and the client should know.

---

## Phase 2 — Read upstream

| File | Take |
|---|---|
| `13-brand-strategy.md` | Personality traits and their behavioural definitions. Voice dimensions must be consistent with them. Positioning, so the core message does not drift |
| `08-audience-persona.md` | How customers describe the problem in their own words. This is the raw material for the vocabulary section |
| `07-strategic-foundation.md` | The UVP, so the core message ladders to it |

If `13` does not exist, you are defining voice with no personality to derive it from. Offer to
run `brand-strategy` first. If the client will not, derive working traits here and label them
an assumption.

---

## Phase 3 — Ask only what you cannot infer

`AskUserQuestion`, **batched, one round, 2-4 maximum.**

Worth asking:

- Which brand's writing do they admire, and which do they find insufferable? The second answer
  is more useful and people answer it more honestly.
- What do they never want to sound like?
- Who writes for them today, and what goes wrong?
- Is there anything they are legally or commercially unable to claim?

Not worth asking: "describe your tone in three words". It produces the adjectives this document
exists to replace.

---

## Phase 4 — Set the dimensions

Per `report-structure.md` §2. **Scales with marked positions and exclusions on both ends**, not
adjectives.

**The evidence that shapes this:**

- **Do not default to conversational.** Informal brand communication can backfire `[C]` [s79].
  This is the single most decision-relevant finding for voice work and it contradicts the
  standard agency default. A casual register must be argued from audience and context, not
  assumed.
- Conversational human voice has measured effects, including on people merely observing an
  exchange rather than participating `[C]` [s81].
- Brand linguistics is an established framework for studying brand language `[C]` [s82], with a
  systematic review of brand language on social media `[C]` [s80].
- Personification and organizational personality affect response `[C]` [s84], moderated by
  culture `[C]` [s78].
- Leaders' corporate messages have identifiable move structures `[C]` [s86], useful for the
  founder variant.

**No corpus evidence supports any specific voice framework.** The slider format is practitioner
convention `[P]`. It earns its place because it forces exclusions, not because it is validated.
Say so if asked.

---

## Phase 5 — Tone, messaging, vocabulary, rhythm

Per `report-structure.md` §3-6.

- **Tone shifts** only for contexts they actually write in. A tone table covering channels they
  do not use is padding.
- **Messaging framework**: core message must be consistent with `13`'s positioning. Proof
  points are facts, not adjectives.
- **Vocabulary**: the never-use list is the valuable half. Mine it from Phase 1 (their own
  filler), Phase 2 (words customers do not use), and the category research in
  `13-brand-strategy.md` Phase 2, words every competitor uses are unavailable as
  differentiators.
- **Rhythm** comes from reading their best existing copy, not from a generic style guide.

---

## Phase 6 — Prove it works

**The phase that separates a usable voice guide from a decorative one.**

Take three to five real passages from their existing copy. Rewrite each to spec. For every
change, name the rule that drove it.

**If a change cannot be traced to a dimension, a vocabulary entry or a rhythm rule, the guide
is incomplete.** You made that edit on instinct, which a freelance writer will not have. Add
the missing rule and redo the rewrite.

Never use invented examples. They prove nothing, because they were written to be easy to fix.

---

## Phase 7 — Naming and taglines, only if in scope

Per `report-structure.md` §8. The evidence:

- **Sound symbolism is real.** Speech sounds systematically shape judgment `[C]` [s100] [s101]
  [s102], and brand spelling affects memory for names heard aloud `[C]` [s103].
- **Pronounceability is the most defensible single criterion.** Hard-to-pronounce names carry
  measured liabilities `[C]` [s99], and name fluency relates to investor recognition and firm
  value `[C]` [s98].
- Figurativeness of names and logos affects memory `[C]` [s96].
- **Taglines have exactly one solid finding in this corpus: a brief pause between the tagline
  and the brand name increases brand name recognition** `[C]` [s97]. Everything else about
  taglines is judgment, and the document should not pretend otherwise.
- Descriptive versus suggestive versus arbitrary, and the trademark trade-off, is practitioner
  `[P]` [s205]. Real as a legal matter, not empirically ranked here.

**Availability checking.** State plainly what was and was not checked. A search is not a
trademark clearance. Point them at a real search before they buy a domain or print signage.
`uspto.gov` and the relevant national registry are the starting points, not Google.

---

## Phase 8 — Kill list, then deliver

Run against `.claude/skills/branding-advisor/references/what-not-to-do.md`. This skill has no
kill list of its own; the hub's covers the refused numbers, method failures and deliverable
smells, and one copy cannot drift.

1. Write `client-projects/<slug>/14-brand-voice.md`.
2. Summarise: the dimensions in one line each, the three highest-value never-use words, and one
   before/after pair.
3. Offer `brand-visual` next. Do not start it unasked.

Doc and PDF are not built by default. Offer via `content-engine/scripts/save_content.py` and
`seo-advisor/scripts/seo_pdf.py`.

---

## Subject: founder

Three changes, and the goal inverts.

**The job is descriptive first.** You are capturing how a specific person already writes so
ghostwritten copy passes as theirs, not installing a new voice. Phase 1 becomes the bulk of the
work and transcripts outrank everything else.

**Add tells.** The verbal habits that make it recognisably them: favourite constructions, how
they qualify a claim, how they disagree, what they find funny, the word they overuse. These are
what a reader notices when they go missing, and they are what a generic "professional but
approachable" guide destroys.

**Add positions held.** What they have publicly said, so ghostwritten copy does not contradict
them.

A founder voice guide that reads like a corporate voice guide has failed. The whole point is
that it sounds like one person rather than a well-run company.

# Method — building a brand strategy

The pipeline. Load this first in build mode.

Output: `client-projects/<slug>/13-brand-strategy.md`, structured per `report-structure.md`.

---

## Phase 0 — Resolve the input

Whatever the client gave, turn it into text. All of these run **UNSANDBOXED**.

| What they gave | Resolve with |
|---|---|
| Google Doc URL or ID | `python .claude/skills/client-onboarding-workflow/scripts/extract_proposal.py "<url_or_id>"` |
| PDF / DOCX / PPTX / XLSX | `python .claude/skills/to-markdown/scripts/convert.py "<path>"` then `Read` the `.md` written beside it |
| `.md` / `.txt` / pasted text | `Read` it, or use the paste inline |
| Business website URL | `python .claude/skills/web-scraper/scripts/scrape.py --url "<url>" --depth crawl --pages 12 --extract raw` |
| Name or one-line brief only | `python .claude/skills/research/scripts/research.py --query "<name> <industry hint>" --depth medium --mode entity` then crawl the site it finds |

If you cannot find the business at all, say so and ask for the URL. **Do not invent a plausible
company.**

---

## Phase 1 — Read what already exists

Check `client-projects/<slug>/` before doing any thinking of your own.

| File | What to take from it | Rule |
|---|---|---|
| `07-strategic-foundation.md` | Market position, UVP, target customer, competitive set | **Take, do not re-derive.** If the brand work suggests a different position, say so explicitly and name what you changed. Never contradict it silently |
| `08-audience-persona.md` | Customer language, the questions they ask, intent | Feeds the vocabulary side of `14-brand-voice.md` more than this document, but read it for how customers describe the problem |
| Existing brand assets | Current logo, colours, copy, any old brand deck | Current state is a fact to record, not a starting position to defend |

If `07` does not exist, you are missing the layer this document sits on. Two options, and you
must pick openly rather than quietly proceeding:

1. Run `strategic-foundation` first. Correct when the client has budget and no settled
   position. This is the honest recommendation more often than not.
2. Proceed and derive a working position here, **labelled as an assumption** in section 0 and
   listed in section 8 for validation.

---

## Phase 2 — See the category

You cannot claim a position without knowing what is already occupied.

```
python .claude/skills/research/scripts/research.py --query "<category> <geo> leading companies brand positioning" --depth deep --save
```

Then look at the top three to five competitors' actual sites. What you are extracting:

- The **claim** each one makes on the homepage, in their words.
- The **vocabulary** the category shares. Words everyone uses are unavailable as
  differentiators and are candidates for the never-use list in `14-brand-voice.md`.
- The **visual convention**: what the category looks like, so `brand-visual` knows what
  conformity and deviation each cost.
- Which positions are **genuinely unoccupied** rather than merely unclaimed on a homepage.

**The five-site test.** Put the client's homepage beside four competitors with the logos
covered. If you cannot tell which is which, the brand has no position, and that is the finding
to lead with. This is the fastest honest diagnosis available and it costs ten minutes.

---

## Phase 3 — Ask only what you cannot infer

`AskUserQuestion`, **batched, one round, 2-4 questions maximum.** Skip anything inferable from
Phases 0-2.

Worth asking, because they are rarely written down anywhere:

- Which customers do they **not** want? (Feeds section 7, and it is the question that most
  often exposes an unmade decision.)
- What do they refuse to do that competitors do?
- Why did the business start? (Feeds the story. Founder stories influence brand authenticity
  through values `[C]` [s91], so this is load-bearing, not colour.)
- What do customers say when they explain the business to someone else?

Not worth asking, because the answer is always the same and always useless: "what are your
values", "what makes you different", "describe your ideal customer in three words".

---

## Phase 4 — Position

Build all five parts from `report-structure.md` §2. Frame of reference first: it determines
everything downstream and is the part most often skipped.

**What the evidence does and does not support**, and you will be asked:

- Positioning effectiveness is a measurable construct `[C]` [s62], with antecedents and
  consequences studied `[C]` [s64] and psychological grounding for positioning options
  `[C]` [s63].
- **There is no causal evidence in the corpus that a clearly positioned brand outperforms an
  ambiguously positioned one.** Practitioners assert it universally and none show data. Do not
  put that claim in the deliverable.
- **Distinctiveness may matter more than differentiation for a small brand.** Perceived
  differentiation may matter less than assumed `[C]` [s1], larger brands hold more associations
  simply by being larger `[C]` [s2], and distinctive assets drive recognition and retrieval
  `[C]` [s7]. See `branding-advisor` Q11 and **preserve the disagreement** rather than picking
  a side in the document.

The practical consequence for an SMB: make sure they are *recognisable* before optimising how
*meaningfully unique* they are. A brand nobody retrieves does not get to compete on its
difference.

---

## Phase 5 — Personality, promise, story, values

Per `report-structure.md` §3-6. The evidence to hold in mind:

- **Personality**: Aaker's five dimensions are a real published scale `[C]` [s69] and structure
  is culture-dependent `[C]` [s73]. Use them as vocabulary. **Archetypes are a creative device
  with no empirical basis** `[P]` [s169], usable, but never labelled as research.
- **Story**: narrative persuasion has meta-analytic support `[C]` [s87] [s88], perspective
  (first vs third person) changes impact `[C]` [s6], and founder stories work through values
  `[C]` [s91]. Write the story true; an invented origin is the highest-risk line in the
  document.
- **Promise and values**: no direct corpus evidence. These earn their place through decision
  clarity, so the test is operational, not literary. A value with no trade-off gets cut.

---

## Phase 6 — Rule things out

Section 7 is where you find out whether Phases 4 and 5 produced decisions or descriptions.

Write it, then re-read sections 2-6 and ask of each line: could a competitor say this? If yes,
it is a description. Fix it or cut it.

---

## Phase 7 — Kill list, then deliver

Run the output against `.claude/skills/branding-advisor/references/what-not-to-do.md`. This
skill deliberately has no kill list of its own: the hub's covers Tier 1 refused numbers, method
failures, framework honesty and the per-section deliverable smells, and keeping one copy stops
the two drifting apart. Then:

1. Write `client-projects/<slug>/13-brand-strategy.md`.
2. Summarise in chat: the position in one sentence, the three things it rules out, and the
   biggest open assumption.
3. Offer next steps: `brand-voice` for how it sounds, `brand-visual` for how it looks. Do not
   start either without being asked.

Google Doc and PDF are **not** built by default. Offer them: the Doc via
`content-engine/scripts/save_content.py`, the PDF via `seo-advisor/scripts/seo_pdf.py`.

---

## Subject: founder

Same pipeline, three changes:

- **Phase 2 becomes voice-landscape research.** The competitors are the other voices the
  audience already follows, not companies. What positions do they hold, and what is left?
- **Phase 3 asks different questions**: what will you say publicly that costs you something,
  what will you not talk about, what do you want to be known for in two years.
- **Phase 6 adds the separation section** (`report-structure.md` §7b): what is shared with the
  company brand, what is deliberately distinct, and what happens to the business if the person
  steps back.

**Evidence honesty for founder work.** This is the weakest area of the corpus: one confirmed
source on CEO visibility `[C]` [s5]. The transferable finding is founder-story authenticity
`[C]` [s91]. Key-person concentration risk is a **reasoned argument, not a research finding**,
and the document must label it that way.

Content pillars, cadence and platform choice are **not** in this document. Route to
`marketing-advisor` and `content-engine`.

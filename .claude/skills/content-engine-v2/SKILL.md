---
name: content-engine-v2
description: "Use to BUILD an alternative, independently-derived content engine for a subject using the installed marketing-skills pack's methodology, or to RUN that v2 engine and write a finished post through its mandatory Seven Sweeps and Expert Panel scoring gate. This is the deliberate A/B counterpart to content-engine (v1): it builds its own product-marketing context from raw source material and never reads the v1 chain, so the two can be compared honestly. Say 'build the v2 engine', 'run v2', 'compare v1 and v2'. For the standard engine use content-engine."
argument-hint: [build v2 <slug> | run v2 <platform> <topic> | repurpose v2]
---

# Content Engine v2 (marketing-skills pack)

Two jobs, same as v1: **BUILD** writes a subject's content engine document. **RUN** writes
content against it. What makes this v2, not a second copy of v1:

1. **Independent sourcing.** BUILD never reads `07-strategic-foundation.md`,
   `08-audience-persona.md`, `13-brand-strategy.md`, `14-brand-voice.md`, `17-conversion-copy.md`,
   `18-content-strategy.md`, or the `agency/personal-brand-voice.md` / `agency/personal-brand-pillars.md`
   equivalents. It derives its own context from raw material via the marketing-skills pack's own
   `product-marketing.md` process. This is the entire point: if v2 read the same derived docs v1
   does, an A/B test would only be testing craft, not the pack's whole approach including how it
   gathers context.
2. **A mandatory quality gate on every RUN.** v1 has none. v2 runs the pack's Seven Sweeps editing
   pass and an Expert Panel Scoring gate before any post is considered finished.

This skill does not decide what to write about, same as v1. Topic selection is out of scope.

---

## Subject resolution — do this first, always

| Subject | Signal | Context doc | Engine artifact |
|---|---|---|---|
| **A client** | a `client-projects/<slug>` is named, a client name, or "for [company]" | `client-projects/<slug>/product-marketing.md` | `client-projects/<slug>/content-engine-v2.md` |
| **Aleem, personal brand** | no slug given, "my", "for me", "my LinkedIn" | `agency/personal-brand-product-marketing.md` | `agency/personal-brand-content-engine-v2.md` |

Both artifacts are deliberately unnumbered and live outside the numbered chain — the same place
v1's own personal-brand engine (`agency/personal-brand-content-engine.md`) already lives — so
neither can ever collide with a numbered slot or with v1's own `19-content-engine.md`.

**Never mention NexusPoint or Aleem inside a client's deliverable.** For Aleem's own
personal-brand content: never name the agency, never mention university or BSAI. Same standing
rules as v1, independent of which engine wrote the piece.

---

## Context to load

Always: `references/subject-context.md` (the context-doc spec and exclusion list),
`references/editing-gate.md` (the quality gate mechanics), `references/conflict-resolution.md`
(how to handle a pack claim that conflicts with Nexis's own corpus).

From the marketing-skills pack, load only what the current step needs:
- `.claude/skills/marketing-skills/product-marketing/SKILL.md` — the context-building process
- `.claude/skills/marketing-skills/copywriting/SKILL.md` + `references/copy-frameworks.md` — headline/CTA formulas, page structure
- `.claude/skills/marketing-skills/copy-editing/SKILL.md` — the full Seven Sweeps + Expert Panel Scoring source (mirrored, condensed, in `references/editing-gate.md`)
- `.claude/skills/marketing-skills/content-strategy/SKILL.md` — pillar identification, Customer Impact/Content-Market Fit/Search Potential/Resources scoring
- `.claude/skills/marketing-skills/social/SKILL.md` + `references/{post-templates,platform-limits}.md` — hook formulas, repurposing system, short-form video structure
- `.claude/skills/marketing-skills/marketing-psychology/SKILL.md` — persuasion mental models

**Platform ground truth still comes from Nexis's own corpora, loaded live, never assumed:**
`social-media-advisor/references/platform-specs/<platform>.md` and
`content-advisor/references/format-specs/`. These are NOT part of the "don't read the derived
chain" rule — they're general platform-fact corpora (hundreds of cited sources each), not
anything synthesized from this specific subject's own 07-18 chain. Skipping them would leave v2
with zero grounded platform mechanics, forcing it onto the pack's own numbers, which are shakier
(see `references/conflict-resolution.md`) — that would confound the test for reasons that have
nothing to do with the methodology actually being compared.

**Load only what the request needs.** A single LinkedIn post does not need the Instagram spec.

---

## BUILD — write the context doc, then the engine document

### Stage A — build or refresh the subject-scoped context doc

1. Resolve the subject.
2. Check whether the context doc already exists at the resolved path. If yes, read it, summarize
   what's captured, ask which sections to refresh — same as the pack's own `product-marketing`
   Step 1.
3. Also check root `.agents/product-marketing.md`. If it's populated, someone ran the vanilla pack
   skill directly with no subject scoping. Do not silently adopt it — ask which subject it was
   actually for.
4. If no subject-scoped doc exists, auto-draft it from **raw material only**. See
   `references/subject-context.md` for the exact source list per subject and the full exclusion
   list. State the exclusion explicitly if asked to shortcut it — reading the derived chain here
   would quietly turn this back into v1.
5. Fill all 12 sections of the pack's template (Product Overview, Target Audience, Personas,
   Problems & Pain Points, Competitive Landscape, Differentiation, Objections & Anti-Personas,
   Switching Dynamics, Customer Language, Brand Voice, Proof Points, Goals) — the exact structure
   is in `.claude/skills/marketing-skills/product-marketing/SKILL.md`.
6. Present the draft for correction before saving. Save with a header noting it was built by
   `content-engine-v2` BUILD, the date, and the subject, so a future reader knows its provenance.

**First-time personal-brand builds are real work, not a rebuild.** v1's engine had 199 already-
analyzed posts to draw on. Building v2's context "genuinely independently" means closer to a
fresh derivation from raw wiki pages, `context/me.md`, and actual post history — set that
expectation before starting, don't rush it to look like a quick pass.

### Stage B — synthesize the engine document

Produces the engine artifact at the path resolved above. Same 7-section shape v1 established, for
comparability, but every section sourced from the pack instead of the numbered chain:

| Section | Sourced from |
|---|---|
| 0. What we know | The subject's `product-marketing.md` itself — a fact table with confidence, and what couldn't be established |
| 1. Hook patterns | `product-marketing.md` §9 Customer Language (verbatim phrases) crossed with `social/SKILL.md`'s Hook Formulas (Curiosity/Story/Value/Contrarian) and `social/references/post-templates.md`. Every pattern must trace to a real phrase in this subject's own §9 — not a generic formula with no anchor |
| 2. Format set | Bounded by `content-strategy/SKILL.md`'s pillar identification and CMF scoring, run against this subject's `product-marketing.md`. Mechanics cited from `platform-specs/<platform>.md` and `format-specs/`, per the "Context to load" carve-out above |
| 3. Copywriting rules | `product-marketing.md` §10 Brand Voice + §9 Customer Language, turned into writing instructions via `copywriting/SKILL.md`'s principles (Clarity > Cleverness, Benefits > Features, headline formulas in `copy-frameworks.md`, the CTA formula) and relevant `marketing-psychology/SKILL.md` mental models, each annotated with why it applies |
| 4. Repurposing map | `social/SKILL.md`'s content-atoms system, matched to the subject's actual cadence from `product-marketing.md` §12 Goals |
| 5. What this engine will not do | `product-marketing.md` §7 Objections & Anti-Personas, stated as explicit refusals |
| 6. Assumptions to validate | Anything inferred rather than confirmed |
| 7. The editing gate | Points to `references/editing-gate.md` and declares the Seven Sweeps + Expert Panel gate as a standing rule for every RUN against this engine |

### The bar

**Genuinely independent, not templated.** The test this skill exists to support only means
something if the context doc traces to raw material this subject actually produced or said —
not a reformat of documents another skill already built. If the output would read the same
whether it was sourced from raw material or from the numbered chain, something went wrong.

Missing raw material is reported by name. A confident context doc built on assumed inputs is
worse than no document — same standard v1 holds for its own upstream files.

---

## RUN — write and gate a finished post

1. **Resolve the subject**, load its `content-engine-v2.md` and the relevant platform specs.
2. **Take the topic from the request.** This skill does not generate topics, same as v1.
3. **Write a complete first draft** against the engine's hook patterns and copywriting rules —
   not an outline.
4. **Run the Seven Sweeps** (Clarity → Voice/Tone → So What → Prove It → Specificity → Heightened
   Emotion → Zero Risk, each looping back through the earlier sweeps, then one final loop through
   all six after Zero Risk). Full mechanics in `references/editing-gate.md`.
5. **Run Expert Panel Scoring.** Assemble the panel for this post type, score each persona 1-10,
   revise the lowest scores first, re-score. Iterate **until every persona scores 7+ and the panel
   average is 8+** — both conditions, not average alone. Cap at 3 rounds; if it hasn't converged by
   then, surface the gap to Aleem rather than looping indefinitely. Full mechanics in
   `references/editing-gate.md`.
6. **Deliver the finished piece with the gate's record attached** — the sweep sign-off and the
   final panel scores, inline. This is what makes the piece auditable for the A/B comparison; a
   post with no visible gate record hasn't actually been through v2's process.
7. **Repurpose on request.** Structural translation, never copy-paste, same rule as v1 — and each
   repurposed variant re-enters the gate (steps 4-5) rather than inheriting the original's pass,
   since a different platform makes different claims and needs different proof, emotion, and
   specificity.
8. **Offer to save and log.** Never save without being asked.

---

## Hand off

| To | For |
|---|---|
| `content-engine` (v1) | Any content request with no v2/alternative cue — the default engine |
| `content-strategy` (Nexis) | A client's numbered-chain pillars, cadence, funnel, distribution |
| `content-advisor` | Whether a content statistic is real, what a format should be |
| `social-media-advisor` | How a platform ranks, why reach dropped, account growth |
| `copywriting-advisor` | Whether a copywriting claim is real |
| `brand-voice` | Building or auditing the Nexis-derived voice itself |
| *(no owning skill)* | Channel mix, offer and pricing, paid ads, email, cross-channel measurement |

---

## Save and log — user-gated only

Google Doc via the shared writer:

```bash
echo '<JSON>' | python tools/gdocs/save_content.py
```

Payload: `{"title": "...", "sections": [{"heading": "...", "level": 1, "body": "..."}]}`

Then log the entry using v1's existing script (reused unmodified — do not fork it), prefixing the
title with `[CE2]` so the shared Content Log sheet stays traceable to which engine wrote which row:

```bash
echo '{"platform":"...","format":"...","goal":"...","title":"[CE2] ...","hook":"...","doc_url":"..."}' | python .claude/skills/content-engine/scripts/log_post.py
```

---

## Edge cases

| Scenario | Action |
|---|---|
| Asked what to post about | This skill does not ideate. Ask for a topic or point at wherever the subject's topic source lives |
| No `content-engine-v2.md` for the subject | Offer BUILD first. RUN without it works but is weaker, and say so |
| Root `.agents/product-marketing.md` exists, unscoped | Ask which subject it's for. Do not silently adopt it |
| Raw material missing for BUILD | Name it, do not invent it. A missing input is not license to guess |
| Client has no raw intake material at all | Report the gap by name — nothing to auto-draft from. Do not fall back to the numbered chain |
| Expert Panel Scoring hasn't converged after 3 rounds | Surface the gap and lowest-scoring critiques to Aleem rather than looping further |
| Asked for a platform benchmark | Give direction, attribute the number, never assert it. See `references/conflict-resolution.md` |
| Save script fails | Output inline with a note to copy manually |
| Request has no v2/alternative-engine cue | Do not trigger. This is v1's territory — see the frontmatter description |

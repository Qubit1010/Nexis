---
name: podcast-repurposer
description: >
  Turns a long podcast transcript into a full short-form content package: 3-5 best segments,
  each with 5 text hooks, 3 A/B captions, and 3-5 long-form LinkedIn/Facebook posts. Built as a
  4-template comparison harness so you can generate the package four different ways (one per
  content methodology) and pick the best method before locking it into production. Client-agnostic
  with a per-client "main voice file" that holds tone, segment criteria, and word limits.

  Use this skill whenever Aleem (or a client like Min / Belle & Perry) wants to:
  - "Turn this podcast into reels / short-form content", "repurpose this episode", "podcast to clips"
  - "Make segments + hooks + captions + posts from this transcript"
  - "Run the 4 templates", "compare the podcast repurposing approaches", "which method is best"
  - Repurpose any long-form audio/video transcript into platform content at higher volume
  - Onboard a new podcast client into the repurposing system (build their main voice file)

  Always trigger when a podcast/long-form transcript needs to become multiple short-form pieces,
  even if the user doesn't say "skill". This is the text layer (segments, hooks, captions, posts);
  actual clip cutting stays in the editor (Riverside/Canva).
argument-hint: "<transcript path> --client <slug> [--template 1|2|3|4|5|all]"
---

# Podcast Repurposer

Turns one long podcast transcript into a structured short-form package. The signature feature:
it can produce that package **four different ways** (four content methodologies), so you can run
them side by side and pick the winning method before porting it into a production (e.g. OpenAI)
pipeline. Each client has a **main voice file** that holds all the per-client rules; updating a
client means editing that file, not the templates.

## How it works

1. **Identify inputs:** the transcript file and the client (`--client <slug>`, e.g.
   `brenda-thompson`). If the client has no voice file yet, see "Onboarding a new client" below.
2. **Read the foundation:**
   - `clients/<slug>.md` — the main voice file (tone, absence signals, ICP, pillars, word
     limits, segment criteria). **All limits and rules come from here, never hardcode them.**
   - `references/output-spec.md` — the exact output structure every template must emit.
3. **Pick template(s):**
   - `--template all` (default for a comparison run) → run all 4, then score with the rubric.
   - `--template N` → run just template N.
4. **Generate:** read the chosen `templates/NN-*.md`, follow its method, emit the output-spec
   structure to `output/<slug>/<episode-slug>/NN-<name>.md`.
5. **Compare (when running all 4):** read `references/comparison-rubric.md`, score each set
   1-5 on the 5 dimensions, cite real examples, and recommend a winner or hybrid plus what to
   port into Min's production system.

## The 4 templates

| # | File | Method |
|---|------|--------|
| 1 | `templates/01-social-media-skills.md` | Reverse-engineer strongest standalone moments; archetype hooks; voice-match; post-formatter rhythm; scorer QA gate. |
| 2 | `templates/02-marketing-skills.md` | Tactic chain — each segment mapped to a pillar + a psychological trigger; every asset has a job. |
| 3 | `templates/03-client-content-creator.md` | Full-funnel; platform-native pieces (IG/LinkedIn/FB written differently); two-angle ideation; brand-alignment notes. |
| 4 | `templates/04-marketing-advisor.md` | 2026 research-backed; select by saveability/sends/completion; hook-rate + word-density targets; dwell-time posts. |
| **5** | **`templates/05-hybrid.md`** | **Recommended production method.** Fuses the four: 04's segment selection (saveability/sends lens) + 01's archetype hooks (reverse-engineer + QA gate) + 03's platform-native captions/posts (IG/LinkedIn/FB genuinely different) + 02's strategic tagging (pillar + trigger + format metadata per segment). Validated across two test episodes. Use this for Min's production port. |

All five emit the **same** output spec — only the method differs. Templates 1-4 are the
comparison harness; Template 05 is the validated production method. Run all 4 to compare
on a new client, then switch to Template 05 once the method is confirmed.

## Output

- One markdown file per template under `output/<slug>/<episode-slug>/`.
- When running all 4: also a `comparison.md` with the scorecard + recommendation.
- `output/` is gitignored (client work).

## Onboarding a new client (building a main voice file)

When a new podcast client comes in, create `clients/<new-slug>.md` modeled on
`clients/brenda-thompson.md`. Capture from their brand/brief: who the content recruits or sells
to (ICP), brand archetype/voice, tone rules, **absence signals** (what their voice is NOT),
content pillars, taglines, the current format being improved, and the `[Red knob]` word limits +
segment criteria (mark which fields the client's creative lead owns). Then run as normal.

## Constraints (always)

- **Text layer only.** This produces segments/hooks/captions/posts. It does not cut video.
- **Voice file is law.** Obey its absence signals (for Brenda: no em dashes, no buzzwords, no
  emojis unless the knob is ON, no generic motivation).
- **Self-contained output.** Every piece must stand alone without the full episode. No "listen
  to the full episode" as the only CTA.
- **Real timestamps** from the transcript, never invented.

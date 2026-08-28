---
name: content-engine
description: >
  Use to BUILD a subject's content engine, or to RUN that engine and write finished content.
  Works for any client with a marketing chain in client-projects/<slug>/, and for Aleem's own
  personal brand. BUILD reads their 07-strategic-foundation, 08-audience-persona,
  13-brand-strategy, 14-brand-voice, 17-conversion-copy, 18-content-strategy and
  09-seo-foundation, then writes client-projects/<slug>/19-content-engine.md: the hook patterns
  drawn from their audience's real language, the format set limited to the platforms their
  strategy actually selected, copywriting rules traced to their voice dimensions, and a
  repurposing map matched to their cadence. Derived per subject, never templated. RUN writes
  actual posts against that engine and repurposes one piece into platform-native variants.
  Triggers on: content engine, build their content engine, create content, write a post,
  write a LinkedIn post, write an Instagram caption, post for [platform], repurpose this,
  turn this into a carousel, make this a reel script, content formats for [client], what hooks
  should they use, how should they open a post, platform formats, full content run, write
  everything for this topic. Does NOT do ideation: it will not tell you what to post about,
  score topics, or build a calendar from a news feed. For a client's pillars, cadence, funnel
  and distribution plan use content-strategy. For whether a content statistic is real use
  content-advisor; for how a platform ranks use social-media-advisor. For a long article use
  blog-writer, for Instagram carousels use carousel, for vertical short frames use
  shorts-creator, for a rendered video use reel-creator, and for whitepapers, newsletters,
  threads or scripts use content-production.
argument-hint: [build <slug> | run <platform> <topic> | repurpose]
---

# Content Engine

Two jobs. **BUILD** writes a subject's content engine document. **RUN** writes content against it.

This skill does not decide what to write about. Ideation was removed 2026-08-28 and archived to
`archives/content-engine-ideation-2026-08-28/`; topic selection belongs to the subject's
`18-content-strategy.md`, or to a future ideation skill.

---

## Subject resolution — do this first, always

| Subject | Signal | Engine spec | Voice source | Pillars |
|---|---|---|---|---|
| **A client** | a `client-projects/<slug>` is named, a client name, or "for [company]" | `client-projects/<slug>/19-content-engine.md` | `client-projects/<slug>/14-brand-voice.md` | `18-content-strategy.md` |
| **Aleem, personal brand** | no slug given, "my", "for me", "my LinkedIn" | `agency/personal-brand-content-engine.md` | `agency/personal-brand-voice.md` | `agency/personal-brand-pillars.md` |

**If a client run finds no `14-brand-voice.md`**, say so and offer to run `brand-voice` first.
Do not invent a voice. The same applies to every upstream file below.

**Aleem's engine is `agency/personal-brand-content-engine.md`**, built 2026-08-28 from 199 logged
posts. It carries one **unresolved decision**: whether personal-brand content may name NexusPoint.
His three strongest posts do; the standing rule says not to. Until he decides, use option (a) from
that file's §7 and write "the agency I run" rather than the name.

**Never mention NexusPoint or Aleem inside a client's deliverable.** It is their document. For
Aleem's own personal-brand content the separate rule applies: never name the agency, never
mention university or BSAI.

---

## Context to load

Always: `references/platform-formats.md` (craft checklist), plus the resolved voice source.

Per platform, load the mechanics rather than assuming them:
- `social-media-advisor/references/platform-specs/<platform>.md` — how it ranks, cadence, growth
- `content-advisor/references/format-specs/` — what the format should be

**Load only what the request needs.** A single LinkedIn post does not need the Instagram spec.

---

## BUILD — write the engine document

Produces `client-projects/<slug>/19-content-engine.md`.

### What it reads, and what each file is for

| Upstream | What BUILD takes from it |
|---|---|
| `08-audience-persona.md` | **The hook patterns.** Their audience's verbatim language and the questions they actually ask. This is the single most important input |
| `17-conversion-copy.md` | Hooks, headlines and CTAs already written and proven for them |
| `14-brand-voice.md` | Copywriting rules. Every rule in the output traces to a voice dimension here |
| `18-content-strategy.md` | Pillars, cadence, funnel, distribution. **The format set is limited to the platforms this file actually selected** |
| `13-brand-strategy.md` | Positioning, and what the brand rules out |
| `07-strategic-foundation.md` | The buyer, the UVP, what content has to sell |
| `09-seo-foundation.md` | The keyword map, where written content should aim |

Take these as given. Do not re-derive a persona or a voice that another skill already produced.

### What the document contains

Follow the shape of `agency/21-blog-engine.md`, the working precedent. Structure:

1. **What we know** — a fact table with sources and confidence, and what could not be established
2. **Hook patterns** — 5-8 patterns, each with a worked example, **each traceable to a real phrase
   in 08 or a proven line in 17**. Not generic hook formulas
3. **Format set** — one section per platform their strategy selected, and no others. Craft from
   `platform-formats.md`, mechanics cited from `platform-specs/`
4. **Copywriting rules** — voice dimensions from 14 turned into writing instructions, with a
   before-and-after on their own copy where possible
5. **Repurposing map** — what becomes what, matched to the cadence in 18
6. **What this engine will not do** — the formats and moves ruled out by 13, stated explicitly
7. **Assumptions to validate** — anything inferred rather than read

### The bar

**Derived, never templated.** If the output would read the same for a different client, it is
wrong. A reader should be able to point at a hook pattern and trace it to a line in that client's
own persona document.

Missing upstream is reported by name, with the producing skill offered. A confident engine
document built on assumed inputs is worse than no document.

---

## RUN — write content against the engine

1. **Resolve the subject** and load its engine spec, voice source and the relevant platform spec.
2. **Take the topic from the request or from `18-content-strategy.md`.** This skill does not
   generate topics.
3. **Write the finished piece.** Not an outline. Follow the engine's hook patterns and
   copywriting rules, and the craft checklist in `platform-formats.md`.
4. **Repurpose on request.** One insight, rebuilt per platform. Structural translation, never
   copy-paste.
5. **Offer to save and log** (below). Never save without being asked.

### Running a row from the Weekly Posting Schedule

`post-creator` owns that flow: it reads the row, researches, writes, builds the image prompts,
saves the Doc and writes the link back. **This skill does not replace it.** What this skill adds
is the gate `post-creator` does not have.

**The gate runs BEFORE post-creator's research step**, because researching a level-2 topic just
produces a well-researched level-2 post. Three questions against
`agency/personal-brand-content-engine.md`:

1. **Ladder check.** Is the row a tool announcement, a news relay, a neutral tutorial or an
   "N ways to" listicle? Those are levels 1-4 and the voice file marks them FORBIDDEN. **38% of
   the 199 logged posts failed this**, so expect to catch real rows here.
2. **First-person check.** Can this row carry a first-person claim with a real number or a named
   moment in the first two lines? If the honest answer is no, the topic is not his to write yet.
3. **Pillar check.** Which of the 4 topical pillars does it serve, and does the current mix need
   it? Founder Journey and Young Builder are at roughly zero across 199 posts.

**If a row fails the gate, say so and propose the rescue rather than writing it.** Most failing
rows are rescuable: a tool announcement becomes level 6+ the moment it carries what happened when
*he* used it, and what he got wrong first. "Here is what OmniVoice does" fails; "I replaced my
voiceover step with OmniVoice and the first three takes were unusable, here is what I had
misconfigured" passes.

**The gate itself lives in `post-creator` step 1b**, because "next post" and "run the post
creator" trigger that skill directly and this one never loads. This section is the rationale;
that file is where it executes. Keep the two in sync.

**Then fill the two columns that have never been filled.** `Pillars` and `Content Mode` are empty
on all 199 rows, which is why the mix has never been measurable. `schedule.py write` takes
`--pillars` and `--content-mode` as of 2026-08-28, so filling them is part of the same write as
the Doc URL. `Pillars` holds the **4 topical pillars**, not the 7 ingredients; the script rejects
an ingredient label there rather than writing it.

Hand off to `post-creator` once the row clears.

### Route to the specialist where one exists

| Asked for | Skill |
|---|---|
| A long article or blog post | `blog-writer` |
| An Instagram carousel image set | `carousel` |
| A single-image LinkedIn infographic | `linkedin-infographics` |
| Vertical short frames | `shorts-creator` |
| A rendered, voiced video | `reel-creator` or `hyperframes-reel` |
| Whitepaper, newsletter, thread, case study, video script, webinar | `content-production` |
| Turning a transcript into short-form | `podcast-repurposer` |

RUN writes posts and captions directly. Anything above goes to its owner.

---

## Hand off

| To | For |
|---|---|
| `content-strategy` | Pillars, calendar, cadence, funnel, distribution. **The plan this engine serves** |
| `content-advisor` | Whether a content statistic is real, what a format should be |
| `social-media-advisor` | How a platform ranks, why reach dropped, account growth |
| `copywriting-advisor` | Whether a copywriting claim is real |
| `copy-conversion` | Copy whose job is to make someone act, and per-platform character limits |
| `brand-voice` | Building or auditing the voice itself |
| `post-creator` | Aleem's scheduled posts driven from the Weekly Posting Schedule sheet |
| `linkedin-commenter` | His daily commenting round |
| `sales-playbook` | 1:1 DMs and outreach, where he is the sender |
| *(no owning skill)* | Channel mix, offer and pricing, paid ads, email and lifecycle, cross-channel measurement. Say so plainly rather than improvising |

---

## Save and log — user-gated only

Google Doc via the shared writer at `tools/gdocs/save_content.py` (moved out of this skill
2026-08-28; it is a general utility used by five skills):

```bash
echo '<JSON>' | python tools/gdocs/save_content.py
```

Payload: `{"title": "...", "sections": [{"heading": "...", "level": 1, "body": "..."}]}`

Then log the entry:

```bash
echo '{"platform":"...","format":"...","goal":"...","title":"...","hook":"...","doc_url":"..."}' | python .claude/skills/content-engine/scripts/log_post.py
```

**This skill does not research.** Source discovery belongs to the `research` skill, and for a
scheduled row it is `post-creator` step 2 that calls it. `scripts/research_notebooklm.py` stays
on disk because `projects/content-engine-dashboard`'s `/api/research` routes still execute it,
but it is not a path this skill offers: it bypasses the `research` skill and goes straight to
NotebookLM with its own depth ladder, which is a second unranked research surface. If a RUN
needs sources, hand the topic to `research` or to `post-creator`.

---

## Edge cases

| Scenario | Action |
|---|---|
| Asked what to post about | This skill does not ideate. Point at `18-content-strategy.md`, or ask for a topic |
| No `19-content-engine.md` for the client | Offer BUILD first. RUN without it works but is weaker, and say so |
| Upstream file missing | Name it, offer the producing skill, do not invent its contents |
| Client has no `18-content-strategy.md` | The format set has nothing to constrain it. Run `content-strategy` first or the engine will guess at platforms |
| Asked for a platform benchmark | Give direction, attribute the number, never assert it. See `platform-formats.md` |
| Save script fails | Output inline with a note to copy manually |
| Personal-brand run, no slug | Resolve from `agency/`. Do not ask for a client folder |

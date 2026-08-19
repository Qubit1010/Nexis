---
name: content-production
description: >
  Use to WRITE or AUDIT an actual piece of content in a format that has no dedicated skill of
  its own: whitepapers, ebooks, gated guides and lead magnets, standalone email newsletters,
  customer case studies, X and LinkedIn threads, single text posts, memes, TikTok and
  short-video scripts, long-form YouTube video scripts, webinar structure and running order,
  and LinkedIn document carousels. This is the execution skill that produces the piece, not
  the advice skill, and it routes rather than duplicates when a specialist skill already owns
  the format.
  Triggers on: write a whitepaper, whitepaper outline, ebook, lead magnet, gated guide,
  downloadable guide, content upgrade, write the newsletter, newsletter issue, email
  newsletter, customer case study, client success story, write a thread, X thread, Twitter
  thread, LinkedIn thread, thread outline, write a LinkedIn post, X post, text post, meme,
  branded meme, TikTok script, short video script, video script, YouTube script, long-form
  video outline, video hook, retention edit, webinar outline, webinar running order, webinar
  script, document carousel, LinkedIn carousel PDF, slide deck content, show notes, podcast
  show notes, episode description.
  Also triggers on: "turn this into a thread", "we need a lead magnet", "write this up as a
  case study", "draft this week's newsletter", "script this video", "what goes in the
  whitepaper", "make this a downloadable", "audit this piece", "why is this post flat".
  Reads 14-brand-voice.md for voice, 13-brand-strategy.md for positioning, 08-audience-persona
  for the audience's own language, and 18-content-strategy.md for which pillar the piece serves
  and what it is supposed to do; when one is missing it says so, offers to run the producing
  skill, then proceeds with the gaps labelled as assumptions. Writes every piece against the
  format spec in content-advisor/references/format-specs/ rather than from memory, and never
  invents a statistic, customer quote or result.
  Outputs to client-projects/<slug>/content/<format>-<slug>.md.
  Routes rather than competes: articles and blog posts go to blog-writer, Instagram carousels
  to carousel, single-image infographics to linkedin-infographics, vertical short frames to
  shorts-creator, rendered video to reel-creator or hyperframes-reel, transcript-to-shortform
  to podcast-repurposer, NexusPoint project write-ups to case-study-generator, and landing or
  sales page copy to copy-conversion. For what a format should look like use content-advisor;
  for the plan the piece belongs to use content-strategy.
argument-hint: [a format and a topic, a client slug, or a piece to audit]
---

# Content Production

The execution spoke for the formats nothing else owns.

**`content-advisor` knows what a format should be. This skill produces one.** And when another
skill already owns the format, this skill hands off rather than writing a second-best version.

---

## Route first, write second

Check this before doing anything else. Writing a blog post here instead of routing it to
`blog-writer` means producing an article without an 83-source AEO/GEO corpus behind it.

| Format | Owner |
|---|---|
| Blog posts, articles, pillar pages, definitive guides (ungated, on-site) | **`blog-writer`** |
| Instagram carousels (4:5 image prompts) | **`carousel`** |
| Single-image LinkedIn infographics | **`linkedin-infographics`** |
| Vertical short frames (9:16 image prompts) | **`shorts-creator`** |
| Rendered, voiced 9:16 video | **`reel-creator`** or **`hyperframes-reel`** |
| A podcast transcript into short-form pieces | **`podcast-repurposer`** |
| A NexusPoint project or tool write-up | **`case-study-generator`** |
| Landing pages, sales pages, ads, email sequences that ask for the sale | **`copy-conversion`** |
| The plan the piece belongs to | **`content-strategy`** |

**Written here, because nothing else owns them:**

whitepapers - ebooks - gated guides and lead magnets - standalone email newsletters - a
client's *customer* case studies - X and LinkedIn threads - single text posts - memes -
TikTok and short-video scripts - long-form YouTube video scripts - webinar structure and
running order - LinkedIn document carousels - podcast show notes

Two boundaries worth stating because they get confused:

- **Guides.** An on-site pillar article is `blog-writer`. A gated downloadable is this skill:
  different structure, different opening, different job.
- **Case studies.** `case-study-generator` writes up NexusPoint's own projects for prospects.
  A case study about *the client's* customer is this skill.

---

## Operating principles (read once)

- **Write against the spec, not from memory.** Every piece is written against its entry in
  `content-advisor/references/format-specs/`. That is where structure, opening, length and
  2026 optimization live, with the evidence tier attached. Writing a newsletter from a general
  sense of how newsletters go is exactly what this skill exists to stop.
- **Inventory the proof before writing a word.** What the client can actually evidence decides
  what the piece is allowed to claim. **Never invent a statistic, a customer quote, a named
  reference or a result.** Placeholders are marked as placeholders.
- **Voice is a constraint, not a suggestion.** `14-brand-voice.md` governs. A piece that reads
  well but sounds like the agency has failed.
- **Length follows the format's job, not a word count.** "Shorter is better" is an assumption
  and has been tested directly against it; do not assert it as settled.
- **Platform specifics are verified and dated, never remembered.** Character limits, aspect
  ratios and truncation points come from `format-specs/` and carry the date they were checked.
  Truncation is not the limit - the limit is what the field accepts, truncation is what the
  reader sees before "more".
- **Anti-AI-tell pass on everything.** Run `blog-writer/references/human-tone-rules.md` over
  the draft before delivering. Content that reads as machine-written is the fastest way for a
  client to reject a deliverable.

---

## Boundaries / handoffs (important)

| Hand off to | For |
|---|---|
| `content-advisor` | What the format should look like, whether a statistic is real, why a piece underperformed |
| `content-strategy` | Which pillar this serves, the calendar it sits in, and the distribution plan behind it |
| `blog-writer` | Articles, on-site guides, and article-level AEO/GEO |
| `copy-conversion` | Copy that asks for the sale, and how a post is formatted for a platform |
| `copywriting-advisor` | Headlines, hooks-as-copy and CTAs as a knowledge question |
| `brand-voice` | Defining the voice, when `14-brand-voice.md` does not exist yet |
| `seo-onpage` | On-page thresholds. **This skill does not restate them** |
| `content-engine` / `post-creator` | NexusPoint's own posts and the weekly schedule |

State the handoff when you make it. Do not silently stop.

---

## Context to load first

`references/method.md`, plus the one `content-advisor/references/format-specs/` file covering
the format being produced. `references/review-rubric.md` in audit mode.

**Max 3 reference files per invocation.**

---

## Mode Detection

| Mode | Trigger keywords | Load |
|---|---|---|
| **build** (default) | "write the X", "draft the X", a format plus a topic | `method.md` + the format spec |
| **audit** | "audit this piece", "why is this flat", an existing piece supplied | `review-rubric.md` + the format spec |
| **route** | The ask belongs to another skill | the routing table above, then hand off |

If ambiguous, prefer build. If the format is owned elsewhere, route before anything else.

---

## Workflow

Follow `references/method.md`. In short:

1. **Route check** — if another skill owns the format, hand off and stop.
2. **Resolve the input** — Doc, file, URL, slug, or a topic inline.
3. **Read upstream and take** — `18-content-strategy.md` for the job the piece does,
   `14-brand-voice.md` for how it sounds, `13`/`08` for positioning and audience language.
   Name what is missing, offer the producing skill, proceed with `[assumption]` labels.
4. **Load the format spec** from `content-advisor/references/format-specs/`.
5. **Inventory the proof** the client actually has. This decides what the piece may claim.
6. **Ask 2-4 non-inferable questions once**, batched.
7. **Write it complete.** Not an outline unless an outline was asked for.
8. **Proof pass** — mark every claim fact / assumption / unprovable.
9. **Human-tone pass** — `blog-writer/references/human-tone-rules.md`.
10. **Deliver** to `client-projects/<slug>/content/<format>-<slug>.md`.

---

## Writing Rules

- **Internal (to Aleem):** direct, bullets, lead with the recommendation.
- **Client-facing:** the client's voice per `14-brand-voice.md`, never the agency's. **Never
  mention NexusPoint, Aleem, or any skill name inside the deliverable.**
- Both: no emojis unless the format spec and the brand voice both call for them, **no em dashes
  in body text** (headings may use them).
- Every claim traces to something real. Unprovable claims get cut or marked, never softened
  into "studies show".
- Platform numbers carry their retrieval date.

---

## Edge Cases

| Scenario | Action |
|---|---|
| Format is owned by another skill | Route. Do not write a second-best version here |
| No `14-brand-voice.md` | Say so, offer `brand-voice`, then derive a working voice from their live copy and label it `[assumption]` |
| No `18-content-strategy.md` | Ask what the piece is for in one question, then proceed. Offer `content-strategy` afterwards |
| Client wants a statistic the corpus refuses | Say it is unsourced, offer a true replacement. If they insist, state the exposure once in writing and note it in the deliverable |
| No proof exists for the central claim | Say the piece cannot carry that claim, and rewrite around what they can evidence |
| Asked for a gated asset with thin substance | Say so. A gated download that disappoints costs more than the email address is worth |
| "Make it go viral" | Refuse the forecast. Cascade size is famously hard to predict; give the argument, not a promise |
| Asked for a character limit | Take it from the format spec with its date, or verify against the platform's own docs. Never from memory |
| A meme for a brand with no cultural licence | Say when a brand should not use one. This is in the spec |
| Piece is for NexusPoint, not a client | Route to `content-engine` or `post-creator` |

---

## Reference Map

```
references/
├── method.md            THE PIPELINE, route check through delivery. Build mode
├── review-rubric.md     Per-format scorecard + the read-aloud gate. Audit mode
└── asset-templates.md   Skeletons for the formats nothing else owns. Never for a
                         format blog-writer, carousel or shorts-creator already writes
```

Format specs live in `content-advisor/references/format-specs/` and are **not** duplicated
here. No `_research/` on purpose. `[sN]` resolves via
`.claude/skills/content-advisor/_research/sources.json`. Run
`python .claude/skills/content-advisor/_research/gather.py verify` after any citation edit.

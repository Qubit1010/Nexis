# Filling image-prompt templates headlessly

The carousel and linkedin-infographics skills are conversational: they interview the user and
gate on approval before emitting Gemini prompts. Inside post-creator you already have everything
they would ask for (description, source, template number from the row), and post-creator has its
own single review checkpoint — so fill their templates directly instead of re-running their
interview loops.

## Inputs for the fill

- **Simplified Source** (NotebookLM's simplified answer, step 3 of SKILL.md) — the content
  that goes on the image. It's already written for scan-reading; the Formal Source is too
  dense for cards/slides.
- **Post Description** (from the row) — the angle; drives the title/headline.
- **Template number(s)** — from `templates.linkedin` / `templates.instagram` in the parsed row.

## LinkedIn infographic (one prompt, one image)

1. Read `.claude/skills/linkedin-infographics/references/LinkedIn-Template-<N>/input-prompt.md`
   — it contains a "SINGLE PROMPT" code block with `<placeholders>`.
2. Skim the same folder's `design-structure.md` only if the placeholder meanings are unclear;
   `example-post.md` shows a fully filled version worth glancing at the first time you use a template.
3. Map the Simplified summary into the placeholders: title (with the accent words picked),
   sections/phases/cards per the template's structure. Respect the template's counts
   (e.g. Template 9 wants 3-4 phases × exactly 3 cards).
4. Emit exactly ONE prompt in one code block. It must keep the template's closing RULES line
   and "One image only." — those keep Gemini from drifting into carousels.

## Instagram carousel (prompt set, one image per slide)

1. Read `.claude/skills/carousel/references/Instagram-Template-<N>/input-prompt.md`
   — it defines CONTEXT (no image) → COVER → BODY (repeat) → CTA blocks.
2. Fill each block from the Simplified summary: one idea/resource per BODY slide.
   Default 6 slides (cover + 4 body + CTA) unless the content clearly wants 8.
   Handle is `@aleem_uh`; pick a natural comment-trigger keyword for the CTA.
3. Emit the blocks in order, each in its own code block, numbered so Aleem can paste them
   into the Gem one at a time.

## Both platforms

- All prompts are 1080x1350 (4:5) — that's baked into the templates; don't change it.
- No emojis, no em dashes in prompt text bodies (brand rule, also in the templates' RULES).
- The prompts go BOTH into the Google Doc (an "Image Prompts" section) and into chat.
- The image generation itself stays manual: Aleem pastes prompts into the matching
  Gemini Gem (`gem.md` in each template folder names it). Never claim images were generated.

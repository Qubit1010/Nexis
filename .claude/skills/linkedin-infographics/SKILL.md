---
name: linkedin-infographics
description: >
  Generate a single-image LinkedIn bento-grid infographic from a post description + source. Maps the
  content into a template's card grid, waits for approval, then outputs ONE Gemini image-generation
  prompt that renders the whole infographic at 1080x1350 (4:5). Use this skill whenever the user says
  "linkedin infographic", "make an infographic", "turn this into an infographic", "bento infographic",
  or "infographic from this post". Also onboards new templates from a reference image. Always includes
  an approval gate between the content map and the prompt output.
---

# LinkedIn Infographics

The LinkedIn counterpart to the `carousel` skill. Carousel makes a multi-slide Instagram set, one
slide image at a time. This skill makes a **single dense infographic** -- the whole bento grid in
ONE image. Same template-driven Gemini-Gem workflow, inverted output format.

## Two phases

- **Phase A -- onboard a template** (when the user drops a NEW reference infographic): extract its
  design into `references/LinkedIn-Template-N/` as a 4-file set. See "Onboarding a new template".
- **Phase B -- generate a post** (the common path): take a description + source, map it into an
  existing template's card grid, gate on approval, then emit the single Gem prompt.

## Templates (preferred path)

Reusable design templates live in `references/<Template>/`. Each has a `design-structure.md` (the
spec), a `gem.md` (a Gemini Gem to build once), an `input-prompt.md` (the per-post fill), and an
`example-post.md` (a worked example).

- **LinkedIn-Template-1** (`references/LinkedIn-Template-1/`) -- bento/masonry round-up infographic.
  Bold black title with a teal vertical accent bar, then a grid of warm-ivory rounded cards. Each
  card has a black category pill (white text; one featured card in teal), real full-color brand
  logos with small grey labels, and a one-line description. Rows mix three-up and two-up, with wider
  cards holding 3 logos. Best for: "N tools by use case", "N ways to X", tool stacks, framework
  breakdowns. Source image in `docs/LinkedIn-Template-1/`.
- **LinkedIn-Template-2** (`references/LinkedIn-Template-2/`) -- tiered horizontal bands infographic.
  Ultra-heavy bold title + subtitle, then three full-width stacked bands graduating from very light
  mint (top/simplest) to sage green (bottom/advanced). Each band has a left metric label, a center
  schematic flowchart, and a right three-point explanation panel (What is / How it works / When to
  use it) with a tier name and level badge. Ends with a full-width tools reference section split into
  three columns. Best for: progression frameworks, level comparisons, "3 approaches to X",
  beginner-to-advanced guides, maturity models. Source image in `docs/LinkedIn-Template-2/`.
- **LinkedIn-Template-4** (`references/LinkedIn-Template-4/`) -- numbered pattern catalogue.
  Ultra-heavy bold title with key words in orange, NexusPoint logo top-right, thin separator, then
  4-6 full-width numbered rows stacked below. Each row has a solid accent-colored number box on the
  left (white "01", "02" ...), a small-caps category label + bold pattern name + 2-3 sentence
  description + 3-4 use-case pill tags in the center, and a schematic flowchart diagram on the
  right. Row accent colors cycle: orange, teal, purple, amber, rose. Warm cream background (#FAF6F0)
  throughout. Best for: "N patterns for X", design pattern references, architecture guides,
  methodology breakdowns, "how X works" explainers. Source image in `docs/LinkedIn-Template-4/`.
- **LinkedIn-Template-11** (`references/LinkedIn-Template-11/`) -- two-column hybrid layout.
  Large bold title with one key phrase in an inline coral pill (#F07560, white text). 3-box
  definition row (full width, "X =" format, thin amber left-border). Left column (~65%): dark navy
  section header + 4-6 numbered rows (orange badge, bold title, description, italic orange tagline,
  sketch illustration). Right column (~35%): dark navy sidebar header + 3-4 best practice cards
  (flat icon, bold title, description). Footer: warm amber-beige quote banner. Best for: "How I use
  X in my workflow", "N ways I use X", practitioner-voice tool breakdowns, tutorials with a
  best-practices sidebar. Source image in `docs/LinkedIn-Template-11/`.
- **LinkedIn-Template-10** (`references/LinkedIn-Template-10/`) -- flat numbered card grid.
  Very large center-aligned display title: big orange numeral (#D96B32) + bold black title words +
  small orange asterisk above. Then 12 equal white cards in a 3-column x 4-row grid (no phases, no
  headers, no bands). Each card has an orange circle badge (top-left, "01"-"12"), a bold 2-4 word
  title, 2-3 sentence body copy (left ~60%), and a hand-drawn outline wireframe sketch illustration
  (right ~40%). Optional real brand logos bottom-right. Warm cream page (#FAF6F0). Best for:
  "N things worth knowing", "N moves worth stealing", feature showcases, tactic catalogues,
  capability rundowns, tool feature explainers. Source image in `docs/LinkedIn-Template-10/`.
- **LinkedIn-Template-9** (`references/LinkedIn-Template-9/`) -- phased roadmap grid.
  Bold title with 1-2 key words in orange and NexusPoint logo top-right, optional full-width hero
  step (Step 00), then 3-4 phase sections each with a colored phase header bar (blue, orange,
  purple, or teal-green) and a 3-column feature card grid. Each card has an accent-colored header
  strip (step number + name), a 1-2 sentence body description, and an action example box at the
  bottom ("PASTE INTO CLAUDE" / "TRY THIS" style). 9-12 total steps. Best for: "N steps to X",
  product/feature roadmaps, phased learning paths, onboarding guides, workflow playbooks, feature
  catalogues grouped by theme. Source image in `docs/LinkedIn-Template-9/`.

When a template fits, recommend it: tell the user to build the Gem once from `gem.md` (attach the
Knowledge image), then use `input-prompt.md` per post so Gemini renders the whole infographic in
that exact look in one image.

## Auto-start on load

When this skill triggers for a post (Phase B), go straight to Step 1. Do not summarise.

## Step 1. Gather inputs

Ask:

> Paste the **post description** (the topic / angle, e.g. "the AI tools I use by use case") and the
> **source** (the list, article, framework, or notes to pull the items from). Both make a tighter
> infographic than either alone. Which template -- or should I pick one?

Wait for the content. If only one template exists and it fits, use it. Otherwise recommend the best
fit and confirm.

## Step 2. Map content to the grid (the core step)

Turn the raw description + source into the template's card structure. For LinkedIn-Template-1:

- Derive a **title**: "N Ways to [outcome]" or "N [things] for [audience]". Keep N accurate.
- Break the content into **categories** (one per card). Aim for **9-12 cards** -- the legibility
  sweet spot at 1080x1350.
- For each card pick: the **category pill** label (1-3 words), the **tools/items** in it (1-3, with
  real brand logos), and a **one-line description** (max ~12 words, plain English).
- Decide the **grid layout**: which cards are WIDE (3 logos) vs NARROW (1 logo), and how rows group.
  Always include a couple of wide cards to balance the masonry. Mark one card as FEATURED (teal pill).

Present the map as a numbered list (title + each card's pill / logos / description / wide-or-narrow),
then tell the user:

> Here is the content map for the infographic. Tell me what to change, or say "generate" when you
> are happy.

Wait for approval. Do not proceed until the user explicitly approves. This gate exists because
regenerating a dense infographic is expensive -- it is cheaper to fix the map than the image.

## Step 3. Output the single prompt

Once approved, fill the template's `input-prompt.md` with the mapped content and output **ONE**
Gemini image-generation prompt in a single code block -- the one that renders the whole infographic.
Do not output multiple prompts; this is one image, not a carousel.

Tell the user:

> Paste this into your `NexusPoint LinkedIn Infographic` Gem (or a new Gemini chat with Create Image
> enabled and Nano Banana selected). It renders the whole infographic as one 1080x1350 image. Fix it
> with "regenerate, same layout, change X".

## Onboarding a new template (Phase A)

When the user supplies a NEW reference infographic (image in `docs/LinkedIn-Template-N/`):

1. Read the image. Extract its design DNA: canvas, title treatment, grid/layout logic, card anatomy,
   palette (hex), type stack, and any baked-in identity (strip source handles to `@{{HANDLE}}`).
2. Create `references/LinkedIn-Template-N/` with the same 4 files as Template-1:
   - `design-structure.md` -- the canonical spec (source of truth).
   - `gem.md` -- the drop-in Gemini Gem, with the **single-image** OUTPUT FORMAT (one complete
     infographic per response, never a deck, never tiled).
   - `input-prompt.md` -- the per-post fill (one single prompt that renders the whole graphic).
   - `example-post.md` -- a filled worked example.
3. Add the new template to the "Templates" list above.
4. Leave the source image in `docs/` (it is the Gem's Knowledge attachment, not copied into the skill).

## Rules

- Always gate on user approval of the content map before outputting the image prompt.
- 1080x1350 px, 4:5 portrait. The whole infographic is ONE image -- never a carousel, deck, or tiled set.
- 9-12 cards max for legibility. If there are more items, cut them, never shrink text to illegible.
- Use real, recognizable brand logos in full color. Do not invent icons for named tools.
- Keep the template palette consistent unless the user supplies brand colors.
- No emojis. No em dashes -- use commas or periods instead.
- Always place the NexusPoint logo (`brand-assets/logos/nexuspoint-logo.png`) small at the top-right,
  above the card grid. Add it as a Knowledge file when building the Gem.
- No handle or footer at the bottom of the infographic.

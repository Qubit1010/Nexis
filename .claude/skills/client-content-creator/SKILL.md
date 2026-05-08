---
name: client-content-creator
description: >
  Generates a full content package for any client based on their business info and branding.
  Given a client's files (brand guide, company overview, audience notes, colors, fonts, etc.),
  produces 5 finished pieces: a 500-700 word SEO blog post, an Instagram caption + hashtags,
  a LinkedIn post, an 8-slide Instagram carousel with visual concepts, and a 6-8 scene video/reel
  concept. Packages everything into a PDF and uploads to Google Drive.

  Use this skill whenever Aleem:
  - Says "create content for [client]", "content package for [client]", "generate content for..."
  - Pastes or links a client's brand guide, business brief, or company overview and wants content
  - Says "client content", "content package", "make content for this client"
  - Has just onboarded a client and needs their first social/blog content suite
  - Receives files from a client (PDF, doc, or inline info) and says "turn this into content"
  - Asks for a "blog + social" or "full content" for any business that isn't NexusPoint

  This skill is for CLIENT brands, not Aleem's personal brand (use content-engine for that).
  Always trigger when content is being created for a third-party business.
argument-hint: "[client name] [optional: topic brief or 'ideate']"
---

# Client Content Creator

Generates a complete, publication-ready content package for any client in Aleem's pipeline.
The workflow: ingest client brief → extract brand voice → ideate/confirm topics → write 5 pieces → package as PDF → upload to Drive.

---

## Step 1: Ingest the Client Brief

Read every file the user provides. Extract and organize:

| Field | Source | If missing |
|-------|--------|------------|
| Business name | Anywhere in files | Ask |
| Core services / products | Company overview, website | Ask |
| Target audience | Brand guide, audience doc | Infer from services, confirm |
| Brand voice keywords | Brand guide, tone section | Infer from industry + examples |
| Color palette | Branding doc | Note as "not provided" — still write content |
| Typography | Branding doc | Note as "not provided" |
| Key differentiators | About page, tagline, values | Infer |
| Location / market | Anywhere | Infer |

If the user pastes inline text instead of files, parse it the same way.

If the business name or core services are completely missing, ask one question before continuing. Do not ask multiple questions — infer everything else.

---

## Step 2: Confirm or Ideate Topics

If the user provides a topic or topic brief, use it directly.

If no topic is given, propose two angles before writing:
- **Blog topic:** The deepest, most SEO-rich angle for the business. Should address a real pain point the target audience searches for. Avoid generic "intro to [service]" angles — find the gap between what they search and what competitors already cover.
- **Social campaign topic:** A different angle from the blog. Something practical, visual, and savable. Must stand alone — not just a summary of the blog.

State both in 1-2 sentences each and say: "Confirm these or redirect, and I'll write all 5 pieces."

If the user says "go ahead" or confirms, proceed. Do not re-ask.

---

## Step 3: Write All 5 Pieces

Write in order. Each piece informs the next — the blog is the richest source, then repurposing flows down.

### Piece 1: Blog Post (500-700 words)

Structure:
1. **Hook** (no preamble — open mid-thought, mid-scene, or with a specific question the audience is already asking)
2. **The problem** (what breaks when this issue is ignored — ground it in consequence, not theory)
3. **The argument** (the business's approach or insight — 2-3 specific points with named examples where possible)
4. **What this looks like in practice** (a session, a product feature, a result — concrete enough to feel real)
5. **One soft CTA** (embedded, not a banner — "If you're curious, [book/try/reach out]")

Sub-headings: 3-4, scannable, keyword-aware. Weave the primary keyword naturally — do not stuff.

End with 2 stock image recommendations: visual concept + searchable Unsplash/Pexels descriptors.

End with an SEO notes block:
```
Primary keyword: [keyword]
Supporting keywords: [list]
Word count: ~[N]
Meta description: "[under 160 chars]"
```

### Piece 2: Instagram Post

Format:
- **Hook line** (1 line — designed to stop the scroll. Must earn the second line.)
- **Body** (3-5 short paragraphs, one idea per paragraph, line breaks between each)
- **CTA** (1 line, soft — "Link in bio" or equivalent)
- **Hashtags** (10-12, mix of high-traffic and mid-tier niche, on a new line)

Word count: 130-180 words (caption only, not hashtags).

Note at the end: "For LinkedIn, swap 'Link in bio' for the direct URL and reduce hashtags to 4-5."

### Piece 3: LinkedIn Post

Adapt from the blog. Same core argument, different framing:
- More professional, more thought-leadership angle
- Open with a bold claim or a data point, not a scene
- 300-600 words
- Short paragraphs, white space, no bullet walls
- End with an extractable principle or a question to the reader — not "follow me for more"

### Piece 4: Instagram Carousel (8 slides)

Format per slide:
```
### Slide N — [Label]
**Heading:** [6-8 words max]
**Sub-text:** [1-3 sentences, under 30 words]
**Visual:** [Specific visual concept with color/lighting direction matching brand palette]
```

Slide structure:
1. Hook (stop-scroll claim — the single boldest thing you can say)
2. Premise / setup
3. Sign / problem / point 1
4. Sign / problem / point 2
5. Sign / problem / point 3
6. Bridge (the shift — "there is a way...")
7. Solution / technique / offer
8. Close + CTA (brand mark, soft offer, save prompt)

End with a carousel caption (adapt from Instagram post) and hashtags.

End with production notes: dimensions, suggested AI/design tools, type sizing, safe margins.

### Piece 5: Video / Reel Concept (30-60 seconds)

Format:

| # | Time | Visual | Text Overlay | Mood / Audio |
|---|------|--------|--------------|--------------|
| 1 | 0:00-0:XX | [shot description, lighting, color direction] | "[overlay text] (font if known)" | [audio/mood note] |
...

6-8 scenes. Total runtime 30-60 seconds.

Specify:
- **Pacing note** (how cuts relate to audio or emotional arc)
- **Aesthetic anchor** (palette, lighting style, color references to brand)
- **Suggested tools** (Runway Gen-3, Kling, CapCut, DaVinci for grading)
- **Music note** (BPM, genre, specific library suggestions if possible)
- **Reel caption** (trimmed from Instagram post, max 150 words + 5 hashtags)

---

## Step 4: Brand Alignment Notes

After all 5 pieces, write a short paragraph (4-6 sentences) explaining how the package reflects the client's brand:
- Which colors appear where and why
- How typography was used (if provided)
- How tone stays consistent across pieces
- What makes the reel or carousel native to the platform

---

## Step 5: Package and Deliver

### Local markdown file

Assemble all pieces into one markdown file at:
```
[project-path-or-cwd]/[client-name]-content-package-[YYYY-MM-DD].md
```

Where `project-path` is the directory where the client's files live (if known), otherwise the current working directory.

Structure:
```
# [Client Name] — Content Package — [Date]
**Prepared by:** Aleem Ul Hassan | NexusPoint

---

## Cover Note
[2-3 sentences: what topics were chosen and why, what the package covers]

---

# 1. Blog Post
...

---

# 2. Social Media Campaign
## 2A. Instagram Post
## 2B. LinkedIn Post

---

# 3. Instagram Carousel

---

# 4. Video / Reel Concept

---

## Brand Alignment Notes
```

### PDF generation

Run this script to convert the markdown to PDF:

```bash
python .claude/skills/client-content-creator/scripts/generate_pdf.py \
  --input "[markdown-file-path]" \
  --output "[same-path-with-.pdf-extension]"
```

If the script fails, note the error and continue with Drive upload of the markdown file instead. Do not block on PDF generation.

### Drive upload

Note: `gws drive files create --upload` ignores the `name` param — the file uploads as "Untitled". Use a two-step approach: upload first, then rename.

```bash
# Step 1: Upload
cd "[directory-containing-the-file]"
gws drive files create --upload "[filename.pdf]"
```

Save the `id` from the response. Then rename and get the link:

```bash
# Step 2: Rename
gws drive files update --params '{"fileId": "[FILE_ID]", "resource": {"name": "[Client Name] - Content Package - [Date]"}}'

# Step 3: Get shareable link
gws drive files get --params '{"fileId": "[FILE_ID]", "fields": "webViewLink"}'
```

If the rename command also fails (gws version-dependent), tell the user: "File uploaded — please rename it manually in Drive to '[Client Name] — Content Package — [Date]'." Then report the link.

Report the Drive link to the user.

---

## Quality Rules (apply to every word written)

These rules are not suggestions — they determine whether the content reads as human-written or AI-generated. Apply them before outputting any piece.

**Voice:** Write in the CLIENT's brand voice. Never inject Aleem's founder perspective, NexusPoint references, or personal anecdotes. Adapt tone to what the client's brand demands (clinical, playful, bold, warm, etc.).

**No AI tells:**
- No em dashes — use commas, periods, or short sentences instead
- No "it's not X, it's Y" constructions
- No "in today's fast-paced world" or similar filler openers
- No "game-changer", "leverage", "unlock", "dive into", "seamlessly"
- No rhythmic AI cadence (three parallel clauses of the same length in a row)
- No "it's important to note that..."

**Hook discipline:** Never open with context, backstory, or a definition. Open with tension, a specific moment, or a bold claim that demands the next line.

**Specificity over vagueness:**
- "many people" → name the exact audience segment
- "recent research" → the actual finding, even if paraphrased
- "some results" → a specific outcome with a number or name
- If specifics aren't in the brief, use a plausible anchor and note it's illustrative

**So What test:** Before outputting any paragraph, ask: "Why does this matter to someone reading it right now?" If the answer isn't in the paragraph, cut or rewrite it.

**Vary cadence:** Mix long sentences (12-18 words) with short ones (4-7 words). Two short sentences followed by a longer one is a strong rhythm. Three paragraphs of the same sentence length in a row is not.

---

## Edge Cases

| Scenario | Action |
|----------|--------|
| No brand voice keywords in brief | Infer from industry and examples in the brief. Note what was inferred. |
| No color palette provided | Write the reel/carousel concepts in terms of lighting and mood (warm, cool, neutral) instead of hex codes. |
| Client is in a regulated industry (health, finance, law) | Avoid any claims that could constitute medical/legal/financial advice. Use "may", "some", "for many clients" framing. |
| User provides a URL instead of files | Read the URL using Firecrawl MCP (if available) or ask user to paste key content. |
| Topic is too broad ("write about wellness") | Ask one clarifying question: "Which angle — [option A] or [option B]?" Give two specific choices based on the business. |
| PDF script fails | Output the markdown and note: "PDF generation failed — upload this markdown to Drive manually or convert via Google Docs." |

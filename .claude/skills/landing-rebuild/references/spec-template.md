# SPEC.md — Template

Fill in every section. Preserve all copy **verbatim** — every word as it appears on the source page. Where the source doesn't provide a value, write `_(not present on source)_` rather than inventing.

---

# {SITE_NAME} Landing — Design Spec

> Extracted from {SOURCE_URL} on {DATE}.
> Source of truth for both `faithful/` and `bold/` rebuilds.

---

## Design Language

### Theme
One sentence describing the overall mood (e.g., "Dark luxury / premium agency", "Bright Swiss-grid SaaS", "Playful retro toy site").

### Color Palette

| Token | Value | Role |
|-------|-------|------|
| `bg` | `<rgb/hex>` | Page background |
| `surface` | `<rgb/hex>` | Cards / raised surfaces |
| `border` | `<rgb/hex>` | 1px borders |
| `text-primary` | `<rgb/hex>` | Body text |
| `text-muted` | `<rgba/hex>` | Secondary text |
| `accent-1` | `<rgb/hex>` | Primary brand accent |
| `accent-2` | `<rgb/hex>` | Secondary accent (if any) |

### Typography

**Primary font:** `<family name>` — source/CDN: <Fontshare or Google Fonts URL>
- Weights used: `<list>`

**Secondary font (if any):** `<family name>` — source/CDN: <URL>
- Used in: <e.g. "CTA section serif italic accent only">

**Scale:**

| Use | Size | Weight | Transform | Letter-spacing |
|-----|------|--------|-----------|----------------|
| Hero headline | <px> | <weight> | <none/UPPERCASE> | <px> |
| Section heading | <px> | <weight> | <none/UPPERCASE> | <px> |
| Card title | <px> | <weight> | <none/UPPERCASE> | <px> |
| Overline / label | <px> | <weight> | UPPERCASE | <px> |
| Body | <px> | <weight> | none | <px> |
| Nav links | <px> | <weight> | <none/UPPERCASE> | <px> |

### Spacing
- Section vertical padding: `<px>` (desktop), `<px>` (mobile)
- Container max-width: `<px>`
- Card gap: `<px>`

### Border Radius
| Use | Value |
|-----|-------|
| Cards | <px> |
| Buttons | <px> |
| Other | <px> |

### Motion notes
Brief description of section-entry animations, hover effects, marquees, etc.

---

## Section Inventory

For each section the page has, in order from top to bottom, fill in this block. Skip sections the page doesn't have.

### 1 — Navbar
**Layout:** <one sentence>

- Logo: `<text/image description>`, color `<token>`, font `<family weight>`
- Nav links: `<list>` — styling notes
- CTA: `<button label>` — styling notes
- Position: <sticky/static>

### 2 — Hero
**Layout:** <one sentence>

- **Imagery:** `<filename or description>`
- **Headline:** `"<verbatim text>"` — typography notes
- **Subheadline:** `"<verbatim text>"` — typography notes
- **CTA(s):** `"<button text>"` — styling
- **Background:** color, gradient, or other treatment

### 3 — <next section> (repeat the block)

For each card/grid section, list ALL items verbatim:

**Card 1 — <title>**
> <body copy verbatim>
> CTA: `<button text>`

**Card 2 — <title>**
> ...

---

## Image Assets

Map of all images that appear on the page, organized by role. Reference these by their local filename in `extraction/public-images/`.

| Asset | Filename | Used in section |
|-------|----------|-----------------|
| Hero portrait | `hero-portrait.png` | Hero |
| Work card 1 | `work-1.png` | Work |
| Avatar 1 | `avatar-1.png` | Testimonials |
| Logo 1 | `logo-1.png` | Trusted By |
| _(etc — match what download_assets.py produced; see asset-manifest.json)_ | | |

---

## Brand Voice

3-5 bullets characterizing the writing voice. Pull adjectives from the actual copy.
- <e.g., "Direct, no-fluff, slightly aggressive confidence">
- <e.g., "Specificity as credibility — uses concrete numbers like '20+ hours/week'">
- <e.g., "Anti-incumbent positioning">

---

## External Links (preserve in rebuild)

| Label | URL |
|-------|-----|
| Contact | <url> |
| LinkedIn | <url> |
| _(etc — only the ones actually used on the page)_ | |

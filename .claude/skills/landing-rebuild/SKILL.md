---
name: landing-rebuild
description: Clone any landing page into a self-hosted Next.js 16 + Tailwind v4 + TypeScript codebase. Produces two side-by-side rebuilds — a faithful 1:1 clone for production use and a bold creative reimagining for design exploration — with full extraction artifacts (markdown copy, design tokens, section screenshots, downloaded assets) saved alongside. Use this skill whenever the user pastes a landing page URL and asks for "rebuild", "clone", "recreate", "convert to Next.js", "self-host", "extract", "make a Next.js version", "give me the code for", "I want to own this site", or anything that implies turning a hosted/no-code site (Framer, Webflow, Wix, Squarespace, custom Next/React) into editable source code. Triggers on phrases like "rebuild [URL]", "clone [URL]", "extract and rebuild [URL]", "recreate this landing page", "convert this Framer site to Next.js", "self-host this site", "make me a Next.js version of [URL]", "I want to take this off Framer", "give me the source for this site". ALWAYS use this skill when a public landing page URL is shared in the context of recreation, copying, replicating, or codebase generation — even when the user doesn't say "skill". Lean toward triggering: if a URL is involved and the user is asking for anything beyond reading or summarizing the page, this skill is probably the right answer.
---

# Landing Rebuild

Take a URL, return a working Next.js codebase. Two flavors per run: faithful clone + bold variant.

The reference implementation that informed this skill lives at `projects/nexuspoint-landing/` — read it if you need a fully-worked example of the output shape.

## When to use vs. NOT use

**Use this skill when:**
- User pastes any landing page / marketing site URL and wants to recreate, clone, copy, self-host, or convert it
- User wants design exploration variants of an existing site
- User wants to migrate off Framer/Webflow/Wix/Squarespace
- User wants a Next.js codebase generated from a reference design

**Do NOT use when:**
- User just wants to read the page contents → use Firecrawl directly via the MCP or WebFetch
- User wants a security/SEO/UX audit → use `website-audit-system` skill
- User wants a single-component conversion (no full page) → use `frontend-design` skill

---

## Phase 1 — Capture intent (use AskUserQuestion)

Required:
- **URL** — if not in the prompt, ask
- **Bold variant aesthetic** — present 6 options. Default highlight: `editorial`. Options come from `references/variants/`:
  - `brutalist` — raw, sharp edges, oversized type, monospace labels, acid accent
  - `editorial` — magazine-style, serif/sans pairing, generous whitespace (Recommended default)
  - `swiss-minimal` — Helvetica feel, strict grid, single accent, lots of negative space
  - `luxury-dark` — deep blacks, gold/champagne accents, refined serif headings
  - `playful` — rounded, colorful, soft shadows, friendly micro-illustrations
  - `retro-futuristic` — gradient meshes, chrome text, 80s-90s computing references

Optional flags (inferred from prompt or asked separately):
- `--extract-only` — stop after Phase 3, no rebuild
- `--faithful-only` / `--bold-only` — skip one variant
- `--multi-page` — also crawl 4 internal pages (see `references/multi-page.md`)

Derive the **site slug** from the URL hostname (e.g., `aleemuh001.framer.ai` → `aleemuh001`). Output directory is `projects/<slug>-landing/`.

---

## Phase 2 — Extract

Run these scripts from the workspace root, in this order. Each writes into `<output-dir>/extraction/`.

```bash
python .claude/skills/landing-rebuild/scripts/extract.py <url> <output-dir>
python .claude/skills/landing-rebuild/scripts/screenshot_sections.py <url> <output-dir>
python .claude/skills/landing-rebuild/scripts/parse_design.py <output-dir>
python .claude/skills/landing-rebuild/scripts/measure_computed.py <url> <output-dir>
python .claude/skills/landing-rebuild/scripts/download_assets.py <output-dir>
```

What each produces:
- `extract.py` → `page.md`, `page.html`, `metadata.json`, `firecrawl-screenshot.png`
- `screenshot_sections.py` → `full-desktop.png`, `full-mobile.png`, `sections/desktop/NN-*.png`, `sections/mobile/NN-*.png` (capped at 14 sections — bounding-box clustering avoids nested duplicates)
- `parse_design.py` → `design-tokens.json` (colors, fonts inc. base64-decoded Framer font tokens, sizes, weights, radii, CSS vars)
- `measure_computed.py` → `computed-tokens.json` (pixel-precise font-size/line-height/padding/etc from `getComputedStyle()` on `h1`/`h2`/`h3`/`p`/`button`/cards)
- `download_assets.py` → `public-images/` (renamed by inferred role) and `asset-manifest.json`

All five scripts read `FIRECRAWL_API_KEY` from `.env` and assume Chromium is installed via Playwright. If a script fails, surface the error to the user — don't silently continue.

---

## Phase 3 — Synthesize SPEC.md

`SPEC.md` is the single source of truth that both rebuilds reference. **Synthesize it in one pass — do not view every section screenshot one by one. That wastes context and turn count.**

Do this:
1. Read `references/spec-template.md` for the structure to fill in
2. Read these inputs:
   - `extraction/page.md` (full markdown copy)
   - `extraction/metadata.json` (meta tags, OG, links)
   - `extraction/design-tokens.json` (colors + fonts + radii)
   - `extraction/computed-tokens.json` (pixel-precise typography)
   - `extraction/full-desktop.png` (whole page layout)
   - 4–6 section screenshots that look distinct from each other (skim `sections/desktop/` and pick representative ones — hero, services, work, testimonials, CTA, footer)
3. Write `extraction/SPEC.md` filling every field in the template
4. **Critical:** preserve copy verbatim — every headline, body paragraph, button label, navigation item should appear word-for-word as it is on the source page
5. Note which fonts you found and which CDN URLs map them — cross-reference `references/font-lookup.md`

---

## Phase 4 — Build faithful/

**Before writing any code, read `references/nextjs-gotchas.md` and `references/faithful-patterns.md`.** These contain non-obvious Next.js 16 + Tailwind v4 rules that tripped up the reference implementation.

Scaffold (run from `projects/<slug>-landing/`):

```bash
npx create-next-app@latest faithful \
  --typescript --tailwind --app --src-dir \
  --import-alias "@/*" --use-npm --no-git --yes
cd faithful
npm install framer-motion
```

`--use-npm` is required: `create-next-app` sometimes defaults to pnpm and fails on Windows when pnpm isn't installed.

Then:
1. Copy `extraction/public-images/` → `faithful/public/images/`
2. Update `faithful/next.config.ts` with `images.remotePatterns` for the source CDN (if you want to keep some remote)
3. Write `faithful/src/lib/content.ts` from the SPEC.md copy (use `assets/content-template.ts` as the starting shape — duplicate it from this skill into the new project)
4. Update `faithful/src/app/globals.css` with the font imports and Tailwind tokens (see `references/faithful-patterns.md` and `references/nextjs-gotchas.md` for the @import-order trap)
5. Update `faithful/src/app/layout.tsx` — replace the default Geist setup, add metadata
6. Write `faithful/src/app/page.tsx` composing the sections
7. Build one component per section in `faithful/src/components/sections/` — Navbar, Hero, then whatever the SPEC's section inventory lists
8. Run `python .claude/skills/landing-rebuild/scripts/verify_build.py faithful/` and fix any errors reported

---

## Phase 5 — Build bold/

```bash
npx create-next-app@latest bold \
  --typescript --tailwind --app --src-dir \
  --import-alias "@/*" --use-npm --no-git --yes
cd bold
npm install framer-motion
```

Then:
1. Read `references/variants/<chosen-variant>.md`
2. Copy `faithful/src/lib/content.ts` → `bold/src/lib/content.ts` — **identical copy, do not change a word**
3. Copy images: `cp -r faithful/public/images bold/public/images`
4. Update globals.css with the variant's font + color tokens
5. Rebuild each section component using the variant's layout language — same component boundaries as faithful (Navbar, Hero, Services, …) so they map 1:1, but a totally different visual execution
6. Run `python .claude/skills/landing-rebuild/scripts/verify_build.py bold/`

---

## Phase 6 — Verify visually & write README

For each app:

```bash
cd <app>
npm run dev -- --port <port> &
sleep 6
python .claude/skills/landing-rebuild/scripts/render_screenshot.py http://localhost:<port> <output-dir>/extraction/verify-<flavor>.png
```

Ports: faithful = 3010, bold = 3011.

After rendering the verify screenshot, **view it alongside `extraction/full-desktop.png`**. Compare:
- Section order matches
- Hero copy reads identically
- Typography scale (headlines feel similar size)
- Spacing feels comparable
- Color palette matches

If you see ≥3 obvious mismatches, patch them and re-render. Do at most **2 refinement passes per app** — the goal is "production-grade close enough", not pixel-perfect.

Finally, write `projects/<slug>-landing/README.md` documenting:
- How to run each app
- Where to edit copy (`src/lib/content.ts`)
- The bold variant's aesthetic direction
- How to re-run extraction if the source page changes

Use the README at `projects/nexuspoint-landing/README.md` as a template.

---

## Mode shortcuts

- **`--extract-only`** — Stop after Phase 3 (SPEC.md written). Tell the user: "Extraction done, SPEC.md ready at `<path>`. Run the skill again without `--extract-only` to generate rebuilds."
- **`--faithful-only`** — Skip Phase 5 entirely. Don't ask about bold variant in Phase 1.
- **`--bold-only`** — Skip Phase 4. You still need a `content.ts` — generate it directly into `bold/src/lib/content.ts` from SPEC.md.
- **`--multi-page`** — Before Phase 2, also read `references/multi-page.md`. Crawl up to 5 internal pages, write each as a separate Next.js route.

---

## Critical gotchas (don't skip — these always trip up the rebuild)

These are documented in detail in `references/nextjs-gotchas.md`. The headline list:

1. **CSS `@import` order:** font imports must come BEFORE `@import "tailwindcss"` in `globals.css`, or Next.js 16's CSS optimizer will silently drop them. Symptom: fonts fall back to system default in production.
2. **`"use client"` for interactivity:** any component with `onClick`, `useState`, `useEffect`, `window.*`, or `localStorage` access needs `"use client";` as the first line. Footer scroll-to-top buttons are a common culprit.
3. **`Image` component with `fill`:** must also have a `sizes` prop, or Next.js logs warnings (not fatal but messy).
4. **`pnpm` not installed on Windows:** always pass `--use-npm` to `create-next-app`.
5. **Project-local AGENTS.md:** the scaffold auto-creates an `AGENTS.md` that says "this is not the Next.js you know" — ignore it, it's a Next.js 16 boilerplate file with outdated instructions.

When `verify_build.py` reports an error, match it to one of these patterns first.

---

## Scripts inventory

All in `scripts/`. Run with `python .claude/skills/landing-rebuild/scripts/<name>.py [args]`.

| Script | Purpose | Args |
|---|---|---|
| `extract.py` | Firecrawl page scrape + screenshot | `<url> <output-dir>` |
| `screenshot_sections.py` | Playwright section + full-page screenshots, bbox clustering | `<url> <output-dir>` |
| `parse_design.py` | CSS regex token extraction + base64 font decode | `<output-dir>` |
| `measure_computed.py` | Playwright `getComputedStyle()` per element | `<url> <output-dir>` |
| `download_assets.py` | Role-aware image downloader from CDN URLs found in HTML | `<output-dir>` |
| `render_screenshot.py` | Single full-page screenshot of a running dev server | `<url> <output-path>` |
| `verify_build.py` | Wraps `npm run build`, surfaces errors structured | `<app-dir>` |

## References inventory

In `references/`. Read on demand:

| File | When to read |
|---|---|
| `spec-template.md` | Phase 3, before writing SPEC.md |
| `font-lookup.md` | Phase 4 + 5, when wiring fonts |
| `nextjs-gotchas.md` | Phase 4 + 5, before any code |
| `faithful-patterns.md` | Phase 4, before code |
| `multi-page.md` | Phase 2 if `--multi-page` is set |
| `variants/<name>.md` | Phase 5, before bold code |

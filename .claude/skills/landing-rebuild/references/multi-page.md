# Multi-Page Mode (`--multi-page` flag)

When the source site has multiple meaningful pages (e.g., Home, Services, About, Work, Contact, Pricing), rebuild each as a separate Next.js route.

## Phase 2 changes (extraction)

Instead of one `extract.py` run, crawl up to 5 internal pages:

1. From `extraction/metadata.json` (already produced by `extract.py` on the home page), collect `links[]` and filter to same-hostname URLs
2. Heuristic page-prioritization order (only crawl what exists):
   - Services / Products
   - About
   - Work / Portfolio / Case Studies
   - Pricing
   - Contact
3. For each, re-run `extract.py <url> <output-dir>/extraction/pages/<page-name>/` to produce a sibling `extraction/pages/services/page.md`, `extraction/pages/about/page.md`, etc.
4. Run `screenshot_sections.py` and `download_assets.py` for each page

## Phase 3 changes (SPEC)

Write a separate SPEC file per page: `SPEC.home.md`, `SPEC.services.md`, `SPEC.about.md`, etc. Each follows `spec-template.md`.

Plus a top-level `SPEC.shared.md` capturing the design tokens (one palette, one type scale, one navbar, one footer — these stay constant across pages).

## Phase 4-5 changes (Next.js routing)

In `src/app/`:

```
app/
├── layout.tsx           # shared <Navbar /> and <Footer />
├── page.tsx             # Home
├── services/page.tsx    # /services
├── about/page.tsx       # /about
├── work/
│   ├── page.tsx         # /work (index)
│   └── [slug]/page.tsx  # /work/<project>
├── pricing/page.tsx
└── contact/page.tsx
```

Components in `src/components/sections/` are organized by where they're used:
- `shared/` — `Navbar.tsx`, `Footer.tsx`, `Ticker.tsx`, used everywhere
- `home/` — sections unique to home (Hero, Services preview)
- `services/` — sections unique to /services
- etc.

`content.ts` exports namespaced per page:

```ts
export const HOME = { hero: {...}, services: [...], ... };
export const SERVICES_PAGE = { hero: {...}, services: [...], ... };
export const ABOUT = { ... };
```

## When NOT to use multi-page mode

If the source site is single-page (everything on one URL with anchor scrolling), don't use `--multi-page`. The default mode handles that case cleanly.

## Constraints

- Cap at 5 pages per run to keep build time + token cost reasonable
- The bold variant copies the same routing structure
- If a page has a CMS pattern (blog list + dynamic slug pages), only stub the route — don't try to crawl all CMS entries. Document this in the README: "Add CMS routes by writing /blog/[slug]/page.tsx and a content data file."

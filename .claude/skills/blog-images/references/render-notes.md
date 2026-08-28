# The SVG contract and the render step

## Why authored SVG rather than a generated image

These images explain concepts, so **the labels are the payload**. Image models routinely garble
text inside diagrams, there is no `GEMINI_API_KEY` on this machine, and `15` §3 specifies exact hex
values a generative model can only approximate.

Authored SVG gives exact palette, legible type, reproducible output, editability and zero API cost.
This is the one place `blog-images` deliberately diverges from `linkedin-infographics`,
`shorts-creator` and `carousel`, all of which stop at a paste-ready Gemini prompt.

## Why a browser and not a rasteriser

Checked 2026-08-22 on this machine: `cairosvg`, `rsvg-convert`, `inkscape` and `magick` are all
absent. Playwright is installed with cached Chromium builds. The browser is the render path that
already exists, and it also gives real web font shaping for free.

## The SVG contract

Every file must:

1. Carry a `viewBox`. `render.py` reads the output size from it and refuses without one.
2. Carry a meaningful `aria-label` on the root `<svg>`. That label becomes the alt text, so write it as a sentence a screen reader user would want, never "diagram".
3. Paint a full-bleed `<rect>` in `#02040A` first. The renderer sets the page background too, but the SVG must stand alone when opened directly.
4. Use only palette hex values. `render.py` audits and refuses otherwise.
5. Contain at least one `#A6DAFF` element. An image with no accent has not decided what it is about.

## Sizes

| Role | viewBox | Rendered at 2x |
|---|---|---|
| Cover | `0 0 1200 630` | 2400x1260 |
| Supporting | `0 0 1200 800` | 2400x1600 |

Cover is 1200x630 because that is the Open Graph standard, so the hero and the social card are one
asset rather than two.

## Running it

```bash
python scripts/render.py path/to/cover.svg              # writes cover.png beside it
python scripts/render.py cover.svg --out out.png --scale 2
python scripts/render.py --selftest                     # 6 checks, no arguments needed
```

`--selftest` is not decorative. It proves the fonts inline, the palette audit catches a retired
colour *and* passes a clean file, the PNG comes out at the right size, the ground is genuinely
`#02040A` rather than white, and **glyph ink is actually present** where the headline sits. That
last one is the check that distinguishes "the font loaded" from "the render silently produced a
blank panel", which look identical in a file size.

## Font inlining is not optional

Both Urbanist faces are inlined as base64 `woff2` data URIs. A network font load has hung a render
in this repo before, and a hung render is indistinguishable from a slow one. `font-display: block`
plus a 300ms settle before the screenshot is what makes the swap deterministic.

Source: `projects/reel-engine/public/fonts/Urbanist-{Regular,Bold}.woff2`, OFL licensed.

## Editing a shipped image

Change the SVG, re-run `render.py`. The PNG is a build artefact and the SVG is the source. Never
edit a PNG.

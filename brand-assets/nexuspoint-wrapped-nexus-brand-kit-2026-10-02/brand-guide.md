# NexusPoint brand guide

**Wrapped Nexus identity · 2 October 2026 · Version 1.0**

NexusPoint connects business strategy, web platforms, and automation into systems that clients can own and run. The identity combines the selected Wrapped Nexus logo with the exact blue and visual language of [Aleem's portfolio](https://www.aleemuh.com/).

This guide distinguishes **extracted** website facts from **recommended** agency specifications. Colours and font declarations were verified from live HTML and CSS on 2 October 2026. Layout, application, and logo usage rules below form the proposed production system. Existing agency strategy and voice documents remain the business foundation.

## 1. Brand foundation

| Element | Direction |
|---|---|
| Essence | Systems you own. |
| Audience | Agency owners and founders whose operations have outgrown their team. |
| What we build | Websites, connected workflows, and AI automation that remove repeating work. |
| Promise | You own what we build, with the source and documentation to run it. |
| Personality | Direct, plain-spoken, precise, and practical. |
| Core message | We build the systems that do your repeating work, and you own them outright. |
| Short descriptor | Websites and automation. |

The name suggests a point of connection. In the symbol, opposing ribbons draw attention toward one shared centre. That centre represents the business outcome the whole system serves.

Write **NexusPoint** with capital N and P and no internal space. Use “we” for the agency and “I” when Aleem speaks personally. Keep the agency identity usable independently of the founder's portfolio, while sharing its visual vocabulary.

### Voice

- Lead with the answer or outcome. Use short, concrete sentences.
- Describe the work in the client's words. Name technical tools when they help the reader decide.
- Explain ownership and handover clearly. Do not imply dependence on a retained login.
- Publish results only when a current, attributable record supports them.
- Avoid hype, manufactured urgency, emojis, and em dashes in body copy.

**Example headline:** “The repeating work gets done. You keep the system.”

**Example supporting copy:** “We connect your website, tools, and workflows so your team spends less time moving the same information around.”

**Example CTA:** “Tell us what your team repeats.”

These are suggested copy examples, not evidence of a measured result. For detailed messaging, use the existing `agency/13-brand-strategy.md` and `agency/14-brand-voice.md`.

## 2. Logo system

### The selected mark

The Wrapped Nexus N uses opposing folded ribbons around a central circle. The N supplies recognition; the folds express connection and movement; the blue point provides a single visual destination.

The production SVGs reconstruct the selected raster artwork as editable vector outlines. The centre is a native SVG circle filled with **#02A1E1**. The original wordmark is preserved as outlined geometry. Its source typeface is not established and must not be described as Inter, Urbanist, or any portfolio display font.

The reference reconstruction uses a 292 × 284 unit symbol bound and a 78.5 unit centre-circle diameter. The path fitting tolerance was 0.65 source pixels. These describe the reconstruction, not a newly invented geometric grid.

### Variants and selection

| Use | Asset |
|---|---|
| Default, matching the portfolio | `logos/nexuspoint-primary-black.svg` |
| Original concept's navy presentation | `logos/nexuspoint-primary-dark.svg` |
| White backgrounds and print | `logos/nexuspoint-primary-light.svg` |
| Placing over an existing dark surface | `logos/nexuspoint-primary-transparent-white.svg` |
| Placing over an existing light surface | `logos/nexuspoint-primary-transparent-navy.svg` |
| Narrow or square layouts | Corresponding `nexuspoint-stacked-*` variants |
| Profile image or compact brand marker | Corresponding `nexuspoint-symbol-*` variants |
| One-colour reproduction | `*-mono-white.svg`, `*-mono-black.svg`, or `*-mono-navy.svg` |
| Browser icon | `logos/nexuspoint-favicon.svg` and `logos/favicons/` |
| Wordmark without the symbol | `logos/nexuspoint-wordmark-white.svg` or `nexuspoint-wordmark-navy.svg` |

The kit provides 28 SVG variants. Use SVG for websites, layout tools, and print. PNG exports in `logos/png/` are convenient for slide tools, social platforms, and applications that cannot accept SVG. White transparent artwork needs a dark background to remain visible. Choose the true-black monochrome variant for a one-ink black reproduction.

### Clear space and size

**Recommended clear space:** use the centre-circle diameter as unit **x**. Keep at least x between the outer visible logo and text, other marks, images, or a layout edge. This is approximately 28% of the symbol height. Existing export padding counts toward this allowance; add layout padding where necessary.

**Production guidance:** use the horizontal lockup at 240 px wide or more, and the detailed standalone symbol at 32 px or more; 48 px or more is preferred. The supplied digital-size render checks support these limits. For print, start at 45 mm wide for the lockup and 10 mm high for the symbol, then inspect the actual output. The print limits are conservative recommendations, not guarantees for every printer or material. The supplied favicon sizes use the full symbol, including the 16 px browser exception; at that size the silhouette and centre remain identifiable but the fold detail is lost.

Keep the supplied proportions and symbol-to-wordmark spacing. Scale the whole asset uniformly. On busy imagery, place the logo on a plain black, white, or navy panel.

### Preserve the mark

- Keep the centre blue on the colour variants. Use a supplied monochrome asset when only one ink is available.
- Retain the circular centre and open ribbon gaps.
- Do not stretch, rotate, rearrange, add an outline, or retype the wordmark.
- Keep decorative glow, grids, and dimensional effects outside the logo artwork.
- Do not put a tagline inside the primary lockup. Place supporting copy separately, beyond its clear space.

The outline master and reconstruction details are in `logos/nexuspoint-outline-master.svg` and `logos/geometry-and-method.json`. The original selected concept is retained in `logos/reference/`.

## 3. Colour palette

### Extracted from the live portfolio

| Colour | HEX | RGB | Agency role |
|---|---|---|---|
| Nexus blue | **#02A1E1** | 2, 161, 225 | Centre point, selected emphasis, primary actions on dark surfaces |
| Hover blue | **#0289BF** | 2, 137, 191 | Interaction state |
| Ink | **#000000** | 0, 0, 0 | Primary digital background |
| Soft ink | **#101010** | 16, 16, 16 | Cards and raised surfaces |
| Ink line | **#1D1E1F** | 29, 30, 31 | Decorative dividers and surface edges |
| Deep band | **#060607** | 6, 6, 7 | Quiet alternate section background |
| White | **#FFFFFF** | 255, 255, 255 | Primary text and light background |

The website's older decorative N uses **#EEF1F4**. Record it as a source detail rather than another primary colour; the new logo uses white.

### Recommended supporting colours

| Colour | HEX | Purpose |
|---|---|---|
| Body grey | **#CCCCCC** | Secondary text on dark backgrounds |
| Muted grey | **#8A8A8A** | Supporting labels on dark backgrounds |
| UI boundary | **#646464** | Functional control boundaries on black or soft ink |
| Accessible link blue | **#0079AA** | Normal text links on white backgrounds |
| Concept navy | **#02040A** | Optional presentation background retained from the selected concept |

These supporting colours are agency recommendations, not newly discovered portfolio tokens. The UI boundary colour is distinct from the low-contrast decorative ink line. Use black, white, and grey for most of a composition. Reserve blue for the centre, one meaningful emphasis, or an action. A suggested balance is 80% dark ground, 15% white or neutral information, and 5% blue; treat it as an art-direction guide rather than a strict calculation.

Use the exact sRGB HEX values for digital work. For print, ask the printer to convert through the chosen paper and press ICC profile and approve a proof. A single generic CMYK conversion cannot preserve this bright blue across all printing conditions.

## 4. Typography

### What the portfolio actually declares

| Family | Extracted role | Declared style |
|---|---|---|
| **Ethnocentric** | H1 and primary hero line | Normal, 400 |
| **Mokoto** | H2 section headings | Normal, 400 |
| **Conthrax** | H3 and H4 display headings | Base heading rule requests 300; available face is declared 400 |
| **Nasalization** | Heading accent words, navigation, footer links | Normal, 400 |
| **Inter** | Body, interface, CTA labels | Normal, 300 / 400 / 500 |
| **Gambetta** | Editorial emphasis and article quotations | Italic, 300 |

Conthrax's CSS face label is separate from its actual named style. Inspection of the local portfolio file identifies Conthrax SemiBold, version 3.000. The CSS declares that face at 400 and requests 300 for H3/H4; this does not indicate a separate 300-weight Conthrax file. The other downloaded font names and versions are recorded in fonts/portfolio-local-use/source-manifest.json.

### Recommended agency hierarchy

Use **Inter** as the working foundation. It keeps proposals, dashboards, case studies, and long copy readable. Once the relevant display-font rights are confirmed, use **Ethnocentric** sparingly for large campaign headlines. **Nasalization** may identify one blue phrase or short navigation label. Preserve the other extracted families as optional reference choices instead of requiring all six on each page.

| Role | Recommended specification |
|---|---|
| Hero | Ethnocentric 400, or Inter 700 fallback; 44 to 104 px fluid size; line-height 1.08; tracking -0.01em |
| Hero blue emphasis | Nasalization 400, or Inter 500 fallback; tracking +0.02em |
| Section heading | Inter 600; 28 to 44 px; line-height 1.15 |
| Card heading | Inter 600; 20 to 24 px; line-height 1.3 |
| Body | Inter 400; 16 px; line-height 1.6 |
| Long-form article | Inter 400; 16 to 18 px; line-height 1.75; comfortable reading width |
| Eyebrow | Inter 500; 13 px; line-height 1.5; tracking +0.115em; uppercase |
| CTA label | Inter 500; 13 px; tracking +0.14em; uppercase for short labels |
| Optional editorial quote | Gambetta 300 italic after direct acquisition, or Inter italic fallback |

The hero, body, eyebrow, and CTA measurements come from the portfolio. The simplified hierarchy, Inter 600 headings, article size range, and fallback policy are agency recommendations. Avoid extended all-capital display copy and decorative fonts in body text.

### Files and licences

**Inter is bundled.** The three exact portfolio WOFF2 files are accompanied by official Inter 4.1 variable desktop/web files and static OTF Regular, Medium, SemiBold, and Bold. They are distributed with their SIL Open Font License 1.1 notices. Use the OTF or variable TTF files in desktop design applications, and WOFF2 for web delivery. [Official Inter source](https://rsms.me/inter/) · [OFL agreement](https://raw.githubusercontent.com/rsms/inter/v4.1/LICENSE.txt).

**Gambetta is a direct-download font.** Fontshare's ITF Free Font License 2.0 permits commercial use and self-hosting but prohibits distributing font files to third parties. Each contractor should acquire their own copy from [Fontshare](https://www.fontshare.com/fonts/gambetta). The licence reference is included in `fonts/Gambetta-ITF-FFL-2.0.txt`. Aleem's downloaded private reference under `sources/private-font-reference/` must stay out of shared handoff archives. [Official licence terms](https://www.fontshare.com/licenses).

**Display families are identified, with acquisition links.** At Aleem's request, five additional exact portfolio WOFF2 files are now copied into fonts/portfolio-local-use/ for local typography previews. They are excluded from the shared ZIP. Existing portfolio agreements were not provided; use those original agreements or acquire the required rights for new production uses and font sharing.

- [Ethnocentric](https://typodermicfonts.com/ethnocentric/), [Conthrax](https://typodermicfonts.com/conthrax/), and [Nasalization](https://typodermicfonts.com/nasalization/): [Typodermic's current licensing routes](https://typodermicfonts.com/license/).
- [Mokoto](https://drizyfont.com/fonts/mokoto-glitch-typeface-font/): Drizy's relevant commercial licence.

This is a handoff constraint for new use, not a finding that the portfolio lacks valid rights. The outlined logo does not require a named wordmark font to be installed.

## 5. Layout, graphics, and motion

### Extracted visual language

- **Spacing base:** 4 px. The responsive breakpoints are 640, 768, 1024, 1280, and 1536 px. The site's largest content container is 1280 px.
- **Corners:** 2 px sharp elements, 10 px cards, and 500 px pill elements.
- **Hero grid:** 76 × 76 px squares, using white at approximately 4.3% opacity.
- **Hero halo:** accent blue at 13% maximum opacity, fading across the upper-right field.
- **Cards:** white at 5% opacity, with a 10% white inset edge.
- **CTA rule:** a 1 px white underline at 22% opacity, rising to 55% on hover.
- **Motion:** `cubic-bezier(.25,1,.5,1)`, a 540 ms reveal, 75 ms reveal staggering, and 300 to 500 ms interaction transitions.
- **Reduced motion:** the portfolio disables decorative effects and reveal animation for `prefers-reduced-motion: reduce`.

### Recommended agency use

Build layouts on a 4 px scale, using 8, 12, 16, 24, 32, 48, 64, and 96 px for common spacing. Start with 24 px mobile page gutters and 48 px desktop gutters. Use a 12-column desktop grid with 24 px column gutters and stack content on mobile. The column grid and gutters are agency recommendations; the 1280 px maximum content width is extracted from the portfolio. Keep body copy to approximately 60 to 75 characters per line.

Use one dominant heading, one blue focal point, and generous negative space. Crop oversized ribbon contours or simple connection paths as occasional background graphics. Keep the authentic mark intact when it identifies the business.

Use grids, technical lines, dark architectural forms, and restrained system diagrams as supporting art. Prefer real product screens, workflow maps, and project evidence over generic robot or circuit imagery. Thin decorative lines can remain subtle; meaningful controls and data need visible contrast.

Make movement converge toward the centre or clarify a connection. Keep the primary logo static. Respect reduced-motion settings and ensure content remains readable when animations are disabled.

## 6. Accessibility and interface rules

The following sRGB contrasts are computed from the verified colours:

| Pair | Ratio | Practical use |
|---|---|---|
| Blue #02A1E1 on black | **7.19:1** | Readable blue text on the dark ground |
| Black on blue #02A1E1 | **7.19:1** | Preferred text for a filled blue CTA |
| White on blue #02A1E1 | **2.92:1** | Fails normal-text AA and the 3:1 large-text threshold |
| Blue #02A1E1 on white | **2.92:1** | Use as a brand accent, not normal body/link text |
| Hover blue #0289BF on white | **3.94:1** | Still below normal-text AA |
| Accessible link blue #0079AA on white | **4.87:1** | Recommended normal-text link colour on white |
| UI boundary #646464 on black | **3.55:1** | Recommended functional control boundaries |
| UI boundary #646464 on soft ink | **3.22:1** | Recommended functional control boundaries |

Use white or body grey for normal dark-mode copy. Use black text on white documents and black text on filled blue buttons. In light layouts, use the recommended #0079AA accessible link blue with an underline, or dark text with an underline. Preserve #02A1E1 in the logo centre; the darker link blue is a functional text colour. Colour alone is not enough to communicate a state.

The live dark-mode focus style is a 2 px blue outline with a 3 px offset. On white, use an ink outline or another verified high-contrast colour instead. Use generous controls, with a recommended 44 px interactive target where layout permits, and keep keyboard focus visible.

The logo is a brand graphic and is exempt from text contrast rules; that exemption does not extend to navigation, buttons, body copy, or charts. Use #1D1E1F only for decorative dividers and edges. Where a boundary is necessary to identify a control, use #646464 or a stronger colour rather than the decorative ink line. [WCAG text contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) · [WCAG non-text contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html).

## 7. Applications

| Surface | Recommended execution |
|---|---|
| Website | Primary black lockup in the header; large restrained hero; blue emphasis; Inter body; ownership and handover made explicit |
| Proposal or document | White pages, light logo, black Inter body; blue section rules; one dark cover; page footer with project and page number |
| Social profile | Symbol centred on black; keep the ribbons and centre inside the platform's circular crop |
| Social post | One clear statement or real result; strong black/white contrast; one blue focus; small logo outside the main reading area |
| Slide deck | Dark opening and closing slides, light detail slides; one message per slide; SVG logos where supported |
| Email signature | Compact light logo on white or text-only NexusPoint; system-font fallback; name, role, and a linked website |
| Case study | Actual screen or workflow, specific problem, implemented system, verified outcome, and client ownership |
| Icon or favicon | Supplied square symbol assets; no wordmark squeezed into a small icon |

Suggested social production sizes are 1080 × 1080 px for square posts and 1080 × 1350 px for portrait posts. Check the destination's current crop and export requirements before publishing. Avoid inventing phone numbers, account handles, client results, or contact details in templates.

For a business card or other print collateral, use a white information side and an optional black logo side. Confirm real contact details before export and proof the blue before ordering.

## 8. Production handoff

The kit contains 28 SVG logo variants with matching PNGs, favicon sizes, an outlined master, the selected raster reference, Inter font files and agreements, saved source evidence, and reconstruction scripts. Use `brand-tokens.css` and `brand-tokens.json` for implementation rather than manually re-entering colours across tools. The application examples are `templates/email-signature.html`, `templates/social-cover.svg`, `templates/proposal-cover.svg`, and `templates/components.html`.

Before releasing a new asset:

1. Choose the correct background variant and preserve the logo's aspect ratio.
2. Apply clear space around visible artwork and inspect the mark at the actual display size.
3. Use exact #02A1E1 for the colour logo's centre.
4. Keep small text readable and verify interactive states on the chosen ground.
5. Embed or outline the correctly licensed fonts when required by the output format.
6. Export SVG for scalable art and sufficiently sized PNG for raster destinations.
7. Share only the permitted fonts. Exclude private Fontshare reference files from external packages.

The logo is reconstructed from the selected concept rather than drawn from a supplied original vector. Render comparison measured 98.34% white-shape overlap for the symbol and 96.54% for the wordmark, with a 95th-percentile boundary difference of 1 source pixel. These checks support fidelity to the selected concept; they do not make the reconstructed artwork identical to the raster. Inspect specialised reproduction, such as embroidery, engraving, and tiny print, with the vendor before ordering. Use monochrome artwork where the process cannot retain the folded details or blue.

## 9. Sources and scope

**Verified visual source:** [Aleem's live portfolio](https://www.aleemuh.com/), with [shared stylesheet](https://www.aleemuh.com/_astro/about.D7EEYB4O.css) and [home stylesheet](https://www.aleemuh.com/_astro/index.DcaP5fwH.css), captured 2 October 2026. The saved evidence and full font/colour declarations are recorded in `sources/extracted-style.json` with source URLs, file hashes, and limitations.

**Selected artwork:** the user's Wrapped Nexus concept, preserved locally and reconstructed in `logos/`. **Business foundation:** existing NexusPoint strategy and voice documents, without carrying forward old revenue statistics or unverified performance claims.

This kit intentionally imports the portfolio palette into the agency identity at Aleem's request. It does not silently rewrite older agency guidelines or change either live website. Applying the kit to those surfaces is a separate implementation step.

Colours and CSS font names in the extraction tables are verified facts. Logo clear space, suggested sizes, simplified type hierarchy, application layouts, supporting greys, and accessible link blue are production recommendations. Display-font rights and specialised print results have not been established by this visual extraction.

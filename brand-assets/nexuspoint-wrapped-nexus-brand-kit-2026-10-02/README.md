# NexusPoint, Wrapped Nexus brand kit

**Version 1.0 · 2 October 2026**

The selected Wrapped Nexus logo now uses the exact live portfolio accent, **#02A1E1** (RGB 2, 161, 225). The kit connects that artwork to the typography, colours and visual language extracted from https://www.aleemuh.com/.

## Start here

1. Open **brand-guide.pdf** for the complete visual guide. The same guide is available as brand-guide.html; brand-guide.md contains the detailed written specification.
2. Use **logos/nexuspoint-primary-black.svg** as the main logo on its portfolio-black background.
3. Use **logos/nexuspoint-primary-transparent-white.svg** over an existing dark surface, or **logos/nexuspoint-primary-transparent-navy.svg** over a light surface.
4. For tools that require images, choose the matching file in **logos/png/**.
5. Install the bundled Inter desktop fonts when working in desktop design tools. The outlined logo itself needs no font installation.

## Included

| Folder or file | Contents |
|---|---|
| brand-guide.pdf / .html / .md | Foundation, logo, colour, typography, layout, motion, applications and production guidance |
| logos/ | 28 native SVG assets: primary, stacked, symbol, monochrome, transparent, wordmark and favicon |
| logos/png/ | Matching high-resolution PNG exports |
| logos/favicons/ | ICO and PNG sizes from 16 to 512 px |
| fonts/ | Inter desktop/web fonts, OFL notices, extracted family roles and acquisition links |
| templates/ | Editable social cover, proposal cover, email signature and responsive interface examples |
| brand-tokens.css / .json | Reusable colours, font roles, spacing, radii, layout and motion tokens |
| contrast-report.json | 18 calculated colour combinations and their text/interface contrast results |
| sources/ | Saved live CSS/HTML, extraction metadata and source/licence evidence |
| previews/ | Image-generator blue-dot preview |
| scripts/ | Rebuild and verification scripts |
| qa/ | Asset, document and application verification evidence |

## Typography and colour facts

The live site declares **Ethnocentric**, **Mokoto**, **Conthrax**, **Nasalization**, **Inter** and **Gambetta**. The guide maps each family to its actual CSS role and weight declaration. The logo wordmark is supplied as outlines; its original typeface has not been established.

Inter is bundled under the SIL Open Font License. At Aleem's request, five additional exact portfolio WOFF2 files are available locally in fonts/portfolio-local-use/. That folder is excluded from shared ZIPs. Official acquisition links remain in fonts/README.md. Fontshare's current Gambetta agreement allows commercial use and self-hosting but excludes external font-file redistribution. Its private reference download is also excluded from the shared ZIP.

The extracted main palette is blue #02A1E1, hover #0289BF, black #000000, raised surface #101010, decorative line #1D1E1F, deep band #060607 and white #FFFFFF. Optional retained logo navy is #02040A. The guide labels proposed supporting colours separately.

For readable interfaces, use black text on the blue button fill. On white, normal blue links use the derived #0079AA. Functional control borders use #646464; decorative #1D1E1F lines carry no essential information.

## Ready-to-use templates

- **templates/social-cover.svg** is editable; social-cover.png is the uploadable 1584 × 396 export.
- **templates/proposal-cover.svg** is editable A4 artwork; proposal-cover.pdf is the corresponding one-page template. Replace the labelled client, project and date fields.
- **templates/email-signature.html** previews the signature. Copy only its marked table and replace the local PNG source with your publicly hosted HTTPS logo URL.
- **templates/components.html** previews the portable type and dark/light component rules. Its sample buttons have no submission or tracking.

## Artwork and source method

The SVGs are faithful contour reconstructions of the selected generated raster, with a native circle using exact #02A1E1. The original concept is preserved in logos/reference/. Slight raster irregularities remain in the fitted outlines. Measured silhouette overlap was 98.34% for the symbol and 96.54% for the wordmark; the 95th-percentile edge difference was one original image pixel.

Use the full horizontal lockup at 240 px wide or more. Use the detailed symbol at 32 px or more, preferably 48 px. Leave at least one centre-dot diameter of clear space. Full rules are in the guide.

This is the new selected brand kit. Existing strategy/voice documents supply its messaging foundation. Live website implementation is outside this handoff.

## Rebuilding

Run scripts/build-handoff-assets.py to rebuild the portable template sources and recompute contrast. Rendering scripts use a local Node/Playwright runtime and Chrome; their executable/runtime paths can be set for the target machine. Logo geometry and build instructions are in logos/README.md and scripts/build-logo-assets.py.

The PDF/HTML guide uses bundled Inter and native SVGs. It does not embed private display-font files.

## Sharing

Share the companion ZIP. It contains the guide, logos, usable font files and notices, tokens, templates and source evidence. The packaging script excludes sources/private-font-reference/, the redundant official Inter source ZIP, and large internal rendering screenshots. A SHA-256 file manifest accompanies the handoff.

# NexusPoint, Soft Fold brand kit

**Approved identity, version 2.0 · 2 October 2026**

Aleem selected **02 Soft Fold** from the open-wrap exploration as the NexusPoint logo to move forward with. This kit supersedes Wrapped Nexus for new branding. The previous kit and original files remain preserved.

## Start here

1. Read **NexusPoint-Soft-Fold-Brand-Guide.pdf** for the 12-page visual guide, or brand-guide.md for detailed implementation rules.
2. Use **logos/nexuspoint-primary-transparent-white.svg** on dark surfaces or **nexuspoint-primary-transparent-navy.svg** on light surfaces.
3. Use matching high-resolution transparent PNGs in **logos/png/** where SVG is unsupported.
4. Find the new Conthrax LinkedIn banner, WhatsApp banners, profile avatar and two-sided card in **applications/**.
5. Use **brand-tokens.css / .json** when building agency interfaces. The primary display family is Conthrax; body and interface copy use Inter.

## Included

| File or folder | Contents |
|---|---|
| NexusPoint-Soft-Fold-Brand-Guide.pdf / .html / .md | Logo, palette, type, spacing, imagery, accessibility and handoff rules |
| logos/ | 28 native SVG variants, including horizontal, stacked, symbol, monochrome and outlined wordmark |
| logos/png/ | High-resolution transparent and background PNGs |
| logos/favicons/ | Nine PNG sizes and a multi-resolution ICO |
| applications/ | Conthrax LinkedIn banner, two WhatsApp layouts, profile avatar, business-card SVG/PNG/PDF and type specimen |
| templates/ | Proposal cover, editable social cover, email signature and responsive interface examples |
| fonts/ | Inter desktop and web files with OFL notices; locally copied portfolio families |
| brand-tokens.css / .json | Colours, chosen type roles, spacing, radii and motion rules |
| contrast-report.json | 18 calculated colour pairs |
| sources/ + scripts/ | Portfolio snapshots, provenance, reference artwork and reproducible asset builders |
| qa/ | Geometry, dimension, QR, layout and package checks |

## Card revision, 2 October 2026

The approved business card is **3C Diagonal Wrap**, locked by Aleem on 2 October 2026. Use applications/Business-Card-Soft-Fold-Front.svg and Back.svg, their PNG exports, Business-Card-Soft-Fold-Print.pdf, and Business-Card-Soft-Fold-Final-Proof.png. Its QR opens https://nexus-point.co/work, with no Portfolio caption. Earlier options remain preserved for reference.

## Folded Edge refinements

Aleem approved **3C Diagonal Wrap** as the final card. The divider has a clear gap above AI SYSTEMS & AUTOMATION. The source artwork and earlier refinements remain in applications/folded-edge-variations/. applications/business-card-selection.json records the approval and makes future application rebuilds use the approved source SVGs.

## Identity and type

The Soft Fold N retains the two inward-facing ribbons and central point, with softer shoulders and an open outer silhouette. The existing NexusPoint wordmark remains unchanged outlined artwork. Conthrax is the chosen display type for headings and banner copy; it does not replace the logo wordmark.

The exact centre colour is **#02A1E1**, RGB 2, 161, 225. Primary backgrounds are black and white. Portfolio navy #02040A remains an optional dark ground. Use black labels on blue buttons, and #0079AA for normal links on white.

The logo SVGs are native contour reconstructions of the chosen PNG, with a native circular point. Symbol white-shape overlap measures 99.39%; the 95th-percentile edge difference is one source pixel. Minor curve-fitting differences remain. Source artwork is preserved in logos/reference/approved-soft-fold-original.png.

## Fonts and sharing

The exact portfolio WOFF2 files for Conthrax, Ethnocentric, Mokoto, Nasalization and Gambetta are copied into **fonts/portfolio-local-use/**. Conthrax's file identifies SemiBold, version 3.000, and is declared at CSS weight 400 on the portfolio. These are webfont copies, not installed or converted desktop fonts.

Keep those local font binaries out of shared archives. Inter is supplied under SIL OFL. Font acquisition links and licence evidence remain in fonts/README.md. Finished application SVGs use lettering outlines, so they contain no private font binary. The guide uses bundled Inter for text and an outlined actual Conthrax specimen.

## Rebuild order

1. Python scripts/build-soft-fold-logo.py
2. Node scripts/build-logo-assets.cjs
3. Python scripts/build-soft-fold-logo.py --verify
4. Python scripts/build-applications.py, then Node scripts/build-application-exports.cjs
5. Python scripts/build-handoff-assets.py, then Node scripts/validate-handoff.cjs
6. Node scripts/build-brand-guide.cjs
7. Optional card alternatives: Python scripts/build-card-variations.py, Node scripts/render-card-variations.cjs, then Python scripts/validate-card-variations.py.
8. Python scripts/validate-production.py, with --qr-python pointing to an OpenCV-enabled interpreter if needed
9. Python scripts/package-brand-kit.py

The current PDF is NexusPoint-Soft-Fold-Brand-Guide.pdf. Any local brand-guide.pdf is a superseded draft and is excluded from the handoff ZIP.

Builders require fontTools, numpy, OpenCV, scikit-image, Pillow, qrcode, pypdf, pypdfium2, sharp, Playwright and Chrome. Local Conthrax files are required only to rebuild its outlines. Existing font licences govern new uses.

The companion ZIP contains the production handoff and SHA-256 manifest. It excludes local display-font binaries, private Fontshare references, duplicate font-source archives and large internal QA images. Websites and social accounts have not been published or changed.

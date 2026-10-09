# LinkedIn banner typography variations

Five versions use actual downloaded portfolio WOFF2 files, rendered in Chrome at **1584 × 396 px**. The supplied Wrapped Nexus logo remains native outlined artwork; its centre is exactly #02A1E1.

- LinkedIn-Banner-Conthrax.png: recommended balance of clear reading and a technical identity.
- LinkedIn-Banner-Ethnocentric.png: closest match to the portfolio's main hero type.
- LinkedIn-Banner-Nasalization.png: softer technical forms and lighter appearance.
- LinkedIn-Banner-Mokoto.png: more graphic headline alternative.
- LinkedIn-Banner-Gambetta.png: editorial Light Italic alternative.

Open font-comparison.html to compare and download individual banners. font-comparison.png is a static comparison sheet. The generated background and its exact prompt are preserved alongside the build script.

The five source fonts are copied under ../nexuspoint-wrapped-nexus-brand-kit-2026-10-02/fonts/portfolio-local-use/. Inter is already in its parent fonts folder. Local files are WOFF2 webfonts, not converted desktop-installable files. Source hashes and actual font name-table metadata are in the fonts folder's source-manifest.json.

The companion PNG-only ZIP contains these five rendered banners and this README. It does not contain font binaries or font-dependent preview source. Portfolio fonts remain local; use the original agreements and official acquisition routes for new production or sharing needs.

Rebuild with Node, Playwright and Chrome:
Set NODE_PATH to the installed node_modules directory, then run node build-font-variations.cjs. The script verifies that all families load, artwork resolves, names fit and banners render at 1584 × 396. It does not install fonts globally.


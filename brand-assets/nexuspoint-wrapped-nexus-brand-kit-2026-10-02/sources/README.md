# Portfolio extraction sources

Verified from the public live portfolio on **2 October 2026, Asia/Karachi**.

`extracted-style.json` records the exact color tokens, typography roles, font URLs, theme scale, surface details, motion settings, evidence rules, licenses and SHA-256 hashes of the saved source snapshots. Values come from HTML/CSS rather than estimating the screenshot.

| Snapshot | Live source |
|---|---|
| `portfolio-live.html` | <https://www.aleemuh.com/> |
| `about.D7EEYB4O.css` | <https://www.aleemuh.com/_astro/about.D7EEYB4O.css> |
| `index.DcaP5fwH.css` | <https://www.aleemuh.com/_astro/index.DcaP5fwH.css> |
| `inter-official.css` | <https://rsms.me/inter/inter.css> |
| `typodermic-license.html` | <https://typodermicfonts.com/license/> |
| `mokoto-official.html` | <https://drizyfont.com/fonts/mokoto-glitch-typeface-font/> |
| `fontshare-licenses.html` | <https://www.fontshare.com/licenses> |

Run `python sources/build_extracted_style.py` from the kit folder to rebuild the extraction JSON from the saved files. It does not contact the website. Python and fontTools are required.

The actual hero overrides its global display-size tokens. Its verified size is `clamp(2.75rem,.5rem + 6.9vw,6.5rem)`, or 44–104px at a 16px root. The screenshot's rotating word is “pipeline”; the fetched page initially displays “revenue”. The blue and typography system are consistent.

The site's Conthrax font file is declared at CSS weight 400. The global H3/H4 rule requests 300 and resolves to the available face. Inspection of the exact file copied locally at Aleem's request identifies Conthrax SemiBold, version 3.000. The generated logo's wordmark font remains unidentified. Five additional source font files are in fonts/portfolio-local-use/, with hashes and metadata; this folder is excluded from shared archives.

## Private references

`private-font-reference/` contains Aleem's direct official Fontshare download, including its supplied ITF FFL 2.0 license dated 17 August 2026. It is a private local reference. **Exclude this directory from external brand handoff archives.** Contractors can obtain their own copy directly from Fontshare.

`Inter-4.1-official.zip` is the complete official OFL release archive. Selected reusable desktop and web files, with their license, are already copied into `fonts/`; external handoffs do not need this duplicate archive.

The extracted CSS references six font families. Only Inter binaries are bundled in the external font handoff. Official acquisition and licensing links for the remaining families are in `fonts/README.md` and `extracted-style.json`.

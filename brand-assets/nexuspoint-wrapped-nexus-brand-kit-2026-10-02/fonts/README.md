# Typography files and acquisition

The portfolio's exact typography was read from its current live CSS on 2 October 2026. The generated Wrapped Nexus logo's wordmark is an image-generated drawing; its original font cannot be conclusively identified from a raster image. Use the supplied outlined logo instead of rebuilding it with a guessed font.

| Portfolio role | Extracted family | CSS declaration | Font handoff |
|---|---|---|---|
| Primary H1 / hero | Ethnocentric | Normal 400 | Official acquisition link below |
| H2 section headings | Mokoto | Normal 400 | Official acquisition link below |
| H3/H4 and display labels | Conthrax | Base rule requests 300; available face declared 400 | Official acquisition link below |
| Blue heading words, navigation, footer | Nasalization | Normal 400 | Official acquisition link below |
| Body, UI and CTA labels | Inter | 300 / 400 / 500 available | Bundled under OFL |
| Editorial italics and blockquotes | Gambetta | 300 italic | Free direct Fontshare download |

## Bundled Inter files

Inter is distributed under **SIL Open Font License 1.1**. Keep its copyright notice and license with the files. No fonts are installed automatically by this kit.

- `inter-300.woff2`, `inter-400.woff2`, `inter-500.woff2`: exact portfolio web files. Source: `https://www.aleemuh.com/fonts/inter-{weight}.woff2`.
- `InterVariable.woff2`, `InterVariable-Italic.woff2`: official 4.1 variable webfonts, from <https://rsms.me/inter/inter.css>.
- `InterVariable.ttf`, `InterVariable-Italic.ttf`: official 4.1 installable variable fonts.
- `Inter-Regular.otf`, `Inter-Medium.otf`, `Inter-SemiBold.otf`, `Inter-Bold.otf`: official 4.1 static desktop files, useful in software that prefers fixed styles.
- `Inter-OFL.txt`: official Inter project license.
- `Inter-v4.1-OFL.txt`: license linked by the official 4.1 release.

Official release: <https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip>. Project: <https://rsms.me/inter/>. License: <https://raw.githubusercontent.com/rsms/inter/v4.1/LICENSE.txt>.

To install the desktop font, open the relevant TTF or OTF file and use Windows' Install command. Choose either the variable family or static styles in your design app. Exact portfolio WOFF2 files are for web use, not ordinary desktop installation.

```css
@font-face {
  font-family: Inter;
  src: url("inter-400.woff2") format("woff2");
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: Inter;
  src: url("inter-500.woff2") format("woff2");
  font-weight: 500;
  font-style: normal;
  font-display: swap;
}
/* Additional official variable family, not a claim about the portfolio setup. */
@font-face {
  font-family: InterVariable;
  src: url("InterVariable.woff2") format("woff2");
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}
```

## Remaining portfolio families

At Aleem's request on 2 October 2026, all five additional exact portfolio WOFF2 files are now copied locally into portfolio-local-use/. That folder is available for local typography previews and is excluded from the external handoff ZIP. Its source-manifest.json records actual inspected font metadata, including Conthrax SemiBold. These local copies do not change the font redistribution policy below.

These families are accurately identified in the guide. Their working binaries are not included in the external handoff, since a site's public font URL does not establish permission to redistribute it.

| Family | Official source | Reuse route |
|---|---|---|
| Ethnocentric | <https://typodermicfonts.com/ethnocentric/> | Use the agreement delivered with the exact style. Current desktop and embedding licenses differ. |
| Conthrax | <https://typodermicfonts.com/conthrax/> | The copied portfolio binary identifies SemiBold, version 3.000. Its CSS declaration at weight 400 is separate from that named style; use the agreement for the intended output. |
| Nasalization | <https://typodermicfonts.com/nasalization/> | Use the agreement delivered with the exact style. Web and document embedding require their appropriate rights. |
| Mokoto | <https://drizyfont.com/fonts/mokoto-glitch-typeface-font/> | Obtain or confirm the project's relevant commercial license for desktop, web, documents or other uses. |
| Gambetta | <https://www.fontshare.com/fonts/gambetta> | Free direct download for commercial and self-hosted use. Each external contractor must obtain their own copy. |

Typodermic's current licensing guide: <https://typodermicfonts.com/license/>. Older valid agreements may have different terms; this kit does not establish or dispute the portfolio's existing license status.

Gambetta's official direct download is <https://api.fontshare.com/v2/fonts/download/gambetta>. The included current **ITF Free Font License 2.0, 17 August 2026**, is copied as `Gambetta-ITF-FFL-2.0.txt`. Its binary redistribution restriction means it should not be passed to external designers in this kit. Aleem's directly obtained private package is preserved in `sources/private-font-reference/`, excluded from shared archives. Fontshare's official license page is <https://www.fontshare.com/licenses>.

For an immediate portable marketing template, use the bundled Inter family and the supplied outlined logo. Matching the full personal-site heading identity is a separate use of the extracted display families with their relevant licenses.

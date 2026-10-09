# Confluence hero QA evidence

The final scene passed responsive and behavioral checks at 375, 390, 768, 1440 and 1920 pixels. Opening headline and both actions fit the viewport, the document has no horizontal overflow, scroll progress reverses correctly, and rendering stops at rest.

No JavaScript, reduced motion, unavailable WebGL and SaveData all retain the static poster, readable copy and usable actions without extra pinned scroll distance. Context loss restores that fallback. Keyboard tests cover menu opening, link access, Escape focus restoration, desktop resizing and both hero actions. Direct links to reviews and contact retain their position after enhancement. Persisted page lifecycle events were simulated to exercise the BFCache pause/resume branch.

The assertions report records 208 of 209 checks passing. Its one failed full-page pixel hash came from animated development chrome, including the Astro toolbar. The focused `reverse-comparison.json` excludes the fixed header and development toolbar and records identical hashes before and after reverse scrolling. This was a capture comparison issue; no scene runtime fix was needed. The temporary test script now uses that isolated comparison.

Axe found zero violations at 390 and 1440 pixels, with 52 rules passing and one incomplete rule requiring human review at each width. Screenshot runs reported no console, page or HTTP errors. Both required brand fonts loaded wherever JavaScript font inspection was available.

Final scene statistics were 67,714 triangles and 10 draw calls. Automated Chromium uses SwiftShader, so these checks establish rendering and behavior rather than real-device frame-rate claims. Physical mobile performance remains unverified.

Artifacts:

- `assertions.json`: complete responsive, lifecycle and fallback assertions.
- `reverse-comparison.json`, `reverse-before.png`, `reverse-after.png`: isolated deterministic rendering comparison.
- `axe/report.json`: accessibility results.
- `normal/`: opening screenshots and four scroll frames at all five widths.
- `no-js/`, `reduced-motion/`, `no-webgl/`: fallback screenshots at 390 and 1440 pixels.
- `production/`: polished screenshots, four scroll frames and browser recordings from the production preview, without development chrome.

# Reel and selected work QA

Status: complete. 232 passed, 0 failed.

Target: http://127.0.0.1:4323/

No software assertion failures so far.

Headless Chromium with SwiftShader verifies deterministic behavior and accessibility. It does not establish real-device frame rate, Core Web Vitals, video decoder efficiency or tactile interaction quality.

Reversal compares exact progress, transforms and inline scene properties, not video pixels. The film is time-driven and cannot be expected to produce identical frames during natural reversed scrolling.

No-JavaScript contexts verify the server-rendered fallback and fragment navigation. Axe is run only in scripting-enabled contexts because its injected runtime does not execute when JavaScript is disabled.

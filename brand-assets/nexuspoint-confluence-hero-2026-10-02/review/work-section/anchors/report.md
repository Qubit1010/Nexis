# Anchor and browser-input QA

Status: complete. 57 passed, 0 failed.

Checks cover deep-link load/reload at 390 and 1440px, including blocked WebGL; native forward/reverse wheel and PageDown/PageUp; video visibility handlers. Anchor placement accommodates the existing 88px fixed-header alignment and section scroll margin.

No software assertion failures so far.

390: live #work: headless Chromium keeps document.hidden=false even after another tab is foregrounded. Native visibility could not be simulated honestly. Checking visibilitychange handler with a controlled hidden getter instead.

1440: live #work: headless Chromium keeps document.hidden=false even after another tab is foregrounded. Native visibility could not be simulated honestly. Checking visibilitychange handler with a controlled hidden getter instead.

These software checks do not establish real-device frame rates or Core Web Vitals.

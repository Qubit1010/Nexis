# Soft Fold hero validation

Validated locally on October 2, 2026. The actual-logo direction supersedes earlier fan artwork and reports.

## Result

- Astro check: 0 errors, 0 warnings, one existing Lighthouse script hint.
- Production build succeeded. Existing build assertions: 56/56. Brand assertions: 29/29. Copy lint: clean.
- Revised production interaction harness: **476/476 passed**, with zero browser console, page or HTTP errors.
- Axe WCAG 2.2 AA and best-practice scan: **zero violations** at opening, 33%, 58% and 86%, at both 390 and 1440 pixels. Each scan passed 52 rules. A permanent accessible H1 fixes the disappearing page heading found during the first phase scan.

## Responsive and motion coverage

375×812, 390×844, 768×1024, 1440×900 and 1920×1080: visible and focusable primary/secondary actions, correct anchor targets, readable chapter headings and no horizontal overflow. Forward and reverse exact progress, rapid native scrolling and responsive resize passed. Reverse captures reproduce the same scene with identical image hashes.

Keyboard opening, Tab navigation, Escape dismissal and focus return passed for mobile navigation during the animated narrative. Both persistent CTAs activate by keyboard from the completed-logo state. Direct #contact and #reviews links retain their destinations after the longer track initializes.

Reduced motion, no JavaScript, no WebGL and data saving retain loaded posters, readable HTML and normal section height without fetching the logo runtime. Runtime reduced-motion changes and context loss dispose the scene and restore static content. Simulated persisted page transitions preserve the scene. GPU drawing rests at all tested widths.

The scene uses 19 logo segments and approximately 10,302 triangles in the opening pose. DPR is capped at 2 on desktop and 1.25 below 1024 pixels. The approved contour data has validated shared boundaries; runtime simplification is bounded at 0.0008 scene units. The complete logo dissolves to unsplit surfaces after arrival.

## Production performance

Lighthouse medians from three runs against the local production preview, with the final geometry and runtime:

| Metric | Mobile simulation | Desktop simulation |
|---|---:|---:|
| LCP | 1,961 ms | 523 ms |
| CLS | 0.000 | 0.000 |
| Performance | 72 | 71 |
| Accessibility | 100 | 100 |
| Best practices | 100 | 100 |
| SEO | 100 | 100 |
| Total blocking time | 1,709 ms | 832 ms |

The requested LCP and CLS targets passed. The largest long task in representative reports was attributed to Lighthouse's injected evaluation script; application scene tasks were still measurable (about 503 ms mobile simulation and 193 ms desktop). Report scores and blocking time are retained without removing tool overhead. These performance runs preceded the final persistent-H1 semantic fix, which changed no geometry, motion or visible composition.

Native Chrome scrolling was inspected locally. **Physical mobile frame rate and field Core Web Vitals remain unverified.** Headless scene captures and simulated Lighthouse runs do not establish sustained FPS on mobile hardware.

## Evidence

[Production interaction assertions](logo-final/production/assertions.json) · [Axe phase scans](logo-final/axe/report.json) · [Mobile performance](logo-final/performance/lighthouse/mobile-summary.json) · [Desktop performance](logo-final/performance/lighthouse/desktop-summary.json) · [Contour validation](logo-segmentation.json)

[Composed desktop/mobile views](logo-composed-views.jpg) · [Four-frame storyboard](logo-storyboard.jpg) · [Individual responsive views and phases](logo-final/production/)

Existing uncommitted work and the rejected renderer were preserved in Nexis archives. No commits or deployment were made. No additional Higgsfield generation was used for this revision. Built client bundles contained no tested Higgsfield credential pattern.

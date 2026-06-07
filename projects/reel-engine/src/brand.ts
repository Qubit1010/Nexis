/**
 * NexusPoint brand tokens for the Reel Engine.
 * Source of truth: brand-assets/brand-guidelines.md (tech-blue gradient identity).
 */

export const COLORS = {
  blueLight: "#208EC7", // bright cyan-leaning blue (gradient start)
  blueDeep: "#1F5B99", // deeper royal blue (gradient end)
  charcoal: "#232323", // primary dark canvas
  charcoalDeep: "#161616", // slightly deeper charcoal for layering
  black: "#0B0B0B",
  white: "#FFFFFF",
  fog: "rgba(255,255,255,0.62)", // muted body text on dark
  hairline: "rgba(255,255,255,0.12)",
  glow: "rgba(32,142,199,0.55)", // blue glow for pills / accents
} as const;

/** Primary tech-blue gradient (top-left -> bottom-right). */
export const BLUE_GRADIENT = `linear-gradient(135deg, ${COLORS.blueLight} 0%, ${COLORS.blueDeep} 100%)`;

/** Vertical charcoal canvas gradient for backgrounds. */
export const CANVAS_GRADIENT = `linear-gradient(180deg, ${COLORS.charcoal} 0%, ${COLORS.charcoalDeep} 100%)`;

export const FONTS = {
  display: "QuicheSans", // bold serif display (headlines, brand anchor)
  body: "Urbanist", // geometric sans (sub-copy, labels, captions)
} as const;

/** Reel format: vertical 9:16 for Instagram / LinkedIn. */
export const VIDEO = {
  width: 1080,
  height: 1920,
  fps: 30,
} as const;

/** Safe-area padding so nothing critical hugs the edges on mobile. */
export const SAFE = {
  x: 96,
  top: 220,
  bottom: 360, // leaves room for captions + IG UI chrome
} as const;

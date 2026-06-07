/**
 * Local brand fonts, inlined as base64 woff2 data URIs (src/fonts-data.ts,
 * regenerate with `node scripts/embed-fonts.mjs`).
 *
 * Inlined (no network) + font-display:swap + no delayRender gate. Gating on a
 * font-load promise (@remotion/fonts loadFont OR document.fonts.load) stalled
 * indefinitely under the video renderer's concurrency here. Because the bytes
 * are inline, the face is parsed immediately and applies within the first task.
 */
import { FONTS } from "./brand";
import { QUICHE_BOLD, URBANIST_REGULAR, URBANIST_BOLD } from "./fonts-data";

const FACES = [
  { family: FONTS.display, src: QUICHE_BOLD, weight: 700 },
  { family: FONTS.body, src: URBANIST_REGULAR, weight: 400 },
  { family: FONTS.body, src: URBANIST_BOLD, weight: 700 },
];

if (typeof document !== "undefined" && !document.querySelector("style[data-brand-fonts]")) {
  const css = FACES.map(
    (f) =>
      `@font-face{font-family:'${f.family}';src:url(${f.src}) format('woff2');font-weight:${f.weight};font-style:normal;font-display:swap;}`,
  ).join("\n");
  const style = document.createElement("style");
  style.setAttribute("data-brand-fonts", "true");
  style.textContent = css;
  document.head.appendChild(style);
}

export const fontsReady = Promise.resolve();

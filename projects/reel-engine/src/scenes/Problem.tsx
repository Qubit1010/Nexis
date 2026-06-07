import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { SAFE, COLORS, FONTS } from "../brand";
import { KineticHeadline } from "../components/KineticHeadline";
import type { Scene } from "../types";

const PAIN = "#ff5b7e"; // a deliberate "pain" coral, used sparingly in the problem beat only

/**
 * Problem scene with selectable treatments so the pain beat doesn't look identical
 * across every reel. Pick per post via scene.problemVariant:
 *   - "chips"    : flickering keyword pills (good for commands / short symptoms)
 *   - "crossout" : a struck-through list of pains (good for "here's what's broken")
 *   - "glitch"   : a glitching headline (good for drift / breakdown / chaos topics)
 * Defaults to "chips". All three read the same data (headline, sub, chips).
 */
export const Problem: React.FC<{ scene: Scene }> = ({ scene }) => {
  const variant = scene.problemVariant ?? "chips";
  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: `${SAFE.top}px ${SAFE.x}px ${SAFE.bottom}px`,
        gap: 70,
      }}
    >
      {variant === "glitch" ? (
        <GlitchView scene={scene} />
      ) : variant === "crossout" ? (
        <CrossoutView scene={scene} />
      ) : (
        <ChipsView scene={scene} />
      )}
    </AbsoluteFill>
  );
};

/* ----------------------------- chips (default) ----------------------------- */
const ChipsView: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const chips = scene.chips ?? [];
  return (
    <>
      <KineticHeadline text={scene.headline ?? ""} fontSize={92} delay={4} align="center" />
      {chips.length > 0 ? (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 22, justifyContent: "center", maxWidth: 820 }}>
          {chips.map((chip, i) => {
            const appear = spring({ frame: frame - 18 - i * 4, fps, config: { damping: 200 } });
            const flicker = 0.45 + 0.55 * Math.abs(Math.sin((frame - i * 7) / fps * 6));
            return (
              <div
                key={i}
                style={{
                  opacity: interpolate(appear, [0, 1], [0, 1]) * flicker,
                  fontFamily: FONTS.body,
                  fontWeight: 700,
                  fontSize: 40,
                  color: COLORS.fog,
                  padding: "16px 34px",
                  borderRadius: 16,
                  border: `1px solid ${COLORS.hairline}`,
                  background: "rgba(255,255,255,0.03)",
                }}
              >
                {chip}
              </div>
            );
          })}
        </div>
      ) : null}
      <Sub scene={scene} />
    </>
  );
};

/* ----------------------------- crossout list ------------------------------- */
const CrossoutView: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const items = scene.chips ?? [];
  return (
    <>
      <KineticHeadline text={scene.headline ?? ""} fontSize={88} delay={4} align="center" />
      <div style={{ display: "flex", flexDirection: "column", gap: 28, width: "100%", maxWidth: 760, marginTop: 8 }}>
        {items.map((item, i) => {
          const appear = spring({ frame: frame - 18 - i * 9, fps, config: { damping: 200 } });
          const op = interpolate(appear, [0, 1], [0, 1]);
          const x = interpolate(appear, [0, 1], [-34, 0]);
          const strike = interpolate(frame - 26 - i * 9, [0, 16], [0, 100], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          return (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 26, opacity: op, transform: `translateX(${x}px)` }}>
              <div
                style={{
                  flexShrink: 0,
                  width: 56,
                  height: 56,
                  borderRadius: 13,
                  background: "rgba(255,91,126,0.14)",
                  border: `1px solid rgba(255,91,126,0.5)`,
                  color: PAIN,
                  fontFamily: FONTS.body,
                  fontWeight: 800,
                  fontSize: 32,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                ✕
              </div>
              <div style={{ position: "relative", display: "inline-block" }}>
                <div
                  style={{
                    fontFamily: FONTS.body,
                    fontWeight: 700,
                    fontSize: 50,
                    color: strike > 55 ? COLORS.fog : COLORS.white,
                    whiteSpace: "nowrap",
                  }}
                >
                  {item}
                </div>
                <div
                  style={{
                    position: "absolute",
                    top: "52%",
                    left: 0,
                    height: 5,
                    width: `${strike}%`,
                    background: "rgba(255,255,255,0.82)",
                    borderRadius: 5,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
      <Sub scene={scene} />
    </>
  );
};

/* -------------------------------- glitch ----------------------------------- */
const GlitchView: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const text = (scene.headline ?? "").replace(/\*/g, "");

  const entry = interpolate(frame, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  // deterministic per-frame jitter (changes every 2 frames)
  const rnd = (s: number) => {
    const x = Math.sin((Math.floor(frame / 2) + 1) * s) * 43758.5453;
    return x - Math.floor(x);
  };
  const burst = Math.sin((frame / 30) * Math.PI * 2) > 0.82; // periodic stronger glitch
  const shift = Math.round((rnd(12.9898) - 0.5) * (burst ? 18 : 5));
  const vy = Math.round((rnd(78.233) - 0.5) * (burst ? 6 : 2));
  const flick = (0.84 + 0.16 * Math.abs(Math.sin(frame * 1.7))) * entry;

  return (
    <>
      <div
        style={{
          position: "relative",
          maxWidth: 880,
          textAlign: "center",
          fontFamily: FONTS.display,
          fontWeight: 700,
          fontSize: 100,
          lineHeight: 1.0,
          letterSpacing: "-0.02em",
          color: COLORS.white,
          opacity: flick,
          transform: `translateX(${shift * 0.3}px)`,
          textShadow: `${shift}px ${vy}px 0 ${COLORS.blueLight}, ${-shift}px ${-vy}px 0 ${PAIN}`,
        }}
      >
        {text}
      </div>
      <Sub scene={scene} />
    </>
  );
};

/* --------------------------------- shared ---------------------------------- */
const Sub: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  if (!scene.sub) return null;
  return (
    <div
      style={{
        opacity: interpolate(frame, [40, 55], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        fontFamily: FONTS.body,
        fontWeight: 700,
        fontSize: 48,
        color: COLORS.blueLight,
        letterSpacing: "-0.01em",
        textAlign: "center",
      }}
    >
      {scene.sub}
    </div>
  );
};

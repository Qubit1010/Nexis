import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { SAFE, COLORS, BLUE_GRADIENT, FONTS } from "../brand";
import { KineticHeadline } from "../components/KineticHeadline";
import type { Scene } from "../types";

/**
 * Punch scene: the one-line payoff/reframe. Selectable treatments via
 * scene.punchVariant so the beat doesn't look identical across every reel:
 *   - "rule"      : thin accent bar above a clean headline (editorial, default)
 *   - "quote"     : oversized quotation mark, reads as a mantra / principle
 *   - "spotlight" : a soft radial glow behind the line (cinematic emphasis)
 */
export const Punch: React.FC<{ scene: Scene }> = ({ scene }) => {
  const variant = scene.punchVariant ?? "rule";
  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: `${SAFE.top}px ${SAFE.x}px ${SAFE.bottom}px`,
        gap: 48,
      }}
    >
      {variant === "quote" ? (
        <QuoteView scene={scene} />
      ) : variant === "spotlight" ? (
        <SpotlightView scene={scene} />
      ) : (
        <RuleView scene={scene} />
      )}
    </AbsoluteFill>
  );
};

/* --------------------------------- rule ------------------------------------ */
const RuleView: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const rule = spring({ frame: frame - 6, fps, config: { damping: 200 } });
  const width = interpolate(rule, [0, 1], [0, 240]);
  return (
    <>
      <div style={{ width, height: 10, borderRadius: 10, backgroundImage: BLUE_GRADIENT, boxShadow: `0 0 30px ${COLORS.glow}` }} />
      <KineticHeadline text={scene.headline ?? ""} fontSize={104} delay={8} align="center" />
    </>
  );
};

/* --------------------------------- quote ----------------------------------- */
const QuoteView: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const q = spring({ frame: frame - 2, fps, config: { damping: 200 } });
  return (
    <>
      <div
        style={{
          fontFamily: FONTS.display,
          fontWeight: 700,
          fontSize: 230,
          lineHeight: 0.8,
          height: 120,
          color: COLORS.blueLight,
          opacity: interpolate(q, [0, 1], [0, 0.32]),
          transform: `translateY(${interpolate(q, [0, 1], [24, 0])}px)`,
          textShadow: `0 0 40px ${COLORS.glow}`,
        }}
      >
        &ldquo;
      </div>
      <KineticHeadline text={scene.headline ?? ""} fontSize={94} delay={8} align="center" />
    </>
  );
};

/* ------------------------------- spotlight --------------------------------- */
const SpotlightView: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const glow = interpolate(frame, [0, 24], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const pulse = 0.82 + 0.18 * Math.sin((frame / 34) * Math.PI * 2);
  return (
    <>
      <div
        style={{
          position: "absolute",
          width: 1000,
          height: 1000,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${COLORS.glow} 0%, transparent 58%)`,
          filter: "blur(50px)",
          opacity: 0.55 * glow * pulse,
          pointerEvents: "none",
        }}
      />
      <KineticHeadline text={scene.headline ?? ""} fontSize={110} delay={6} align="center" />
    </>
  );
};

import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { SAFE, COLORS, FONTS } from "../brand";
import { LogoSting } from "../components/LogoSting";
import { PillButton } from "../components/PillButton";
import type { Scene } from "../types";

/** Outro scene: CTA question + pill button + logo sting + handle. */
export const Outro: React.FC<{ scene: Scene; handle?: string }> = ({ scene, handle }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const ctaEnter = spring({ frame: frame - 2, fps, config: { damping: 200 } });

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: `${SAFE.top}px ${SAFE.x}px ${SAFE.bottom}px`,
        gap: 70,
      }}
    >
      {scene.cta ? (
        <div
          style={{
            opacity: interpolate(ctaEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(ctaEnter, [0, 1], [24, 0])}px)`,
            fontFamily: FONTS.display,
            fontWeight: 700,
            fontSize: 78,
            textAlign: "center",
            color: COLORS.white,
            letterSpacing: "-0.02em",
            lineHeight: 1.05,
            maxWidth: 880,
          }}
        >
          {scene.cta}
        </div>
      ) : null}

      <PillButton label="Follow for more" delay={20} />

      <div style={{ marginTop: 30 }}>
        <LogoSting delay={34} />
      </div>

      {handle ? (
        <div
          style={{
            opacity: interpolate(frame, [60, 75], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            fontFamily: FONTS.body,
            fontWeight: 700,
            fontSize: 40,
            color: COLORS.fog,
            letterSpacing: "0.04em",
          }}
        >
          {handle}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

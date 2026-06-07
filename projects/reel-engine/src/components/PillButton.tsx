import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { COLORS, FONTS, BLUE_GRADIENT } from "../brand";

/**
 * Pill-shaped CTA container (brand motif) with a soft pulsing blue glow.
 */
export const PillButton: React.FC<{ label: string; delay?: number }> = ({
  label,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({
    frame: frame - delay,
    fps,
    config: { damping: 200, stiffness: 110, mass: 0.8 },
  });
  const scale = interpolate(enter, [0, 1], [0.8, 1]);
  const opacity = interpolate(enter, [0, 1], [0, 1]);

  const pulse = interpolate(Math.sin((frame - delay) / fps * 3), [-1, 1], [0.45, 0.9]);

  return (
    <div
      style={{
        transform: `scale(${scale})`,
        opacity,
        display: "inline-flex",
        alignItems: "center",
        gap: 22,
        padding: "32px 60px",
        borderRadius: 999,
        backgroundImage: BLUE_GRADIENT,
        boxShadow: `0 0 ${60 * pulse}px ${COLORS.glow}, 0 18px 50px rgba(0,0,0,0.5)`,
      }}
    >
      <span
        style={{
          fontFamily: FONTS.body,
          fontWeight: 700,
          fontSize: 50,
          color: COLORS.white,
          letterSpacing: "0.01em",
        }}
      >
        {label}
      </span>
      <span
        style={{
          fontFamily: FONTS.body,
          fontWeight: 700,
          fontSize: 50,
          color: COLORS.white,
          transform: "translateY(-2px)",
        }}
      >
        →
      </span>
    </div>
  );
};

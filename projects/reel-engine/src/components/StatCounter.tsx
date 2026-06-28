import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { COLORS, FONTS, BLUE_GRADIENT } from "../brand";
import type { StatItem } from "../types";

/**
 * Big animated count-up stat in a glass card. The centerpiece motif
 * (mirrors the reference "58% fewer tool calls" cards).
 */
export const StatCounter: React.FC<{ stat: StatItem; delay?: number; index?: number }> = ({
  stat,
  delay = 0,
  index = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({
    frame: frame - delay,
    fps,
    config: { damping: 200, stiffness: 90, mass: 0.9 },
  });

  // Count-up: ease the displayed number toward the target over ~24 frames.
  const countProgress = interpolate(frame - delay, [0, 26], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const eased = 1 - Math.pow(1 - countProgress, 3);
  const display = Math.round(stat.value * eased);

  const float = Math.sin((frame - delay) / fps * 1.4 + index) * 5;
  const y = interpolate(enter, [0, 1], [60, 0]) + float * interpolate(enter, [0, 1], [0, 1]);
  const opacity = interpolate(enter, [0, 1], [0, 1]);
  const glow = interpolate(countProgress, [0, 1], [0, 1]);

  // Light sheen sweeps across the card shortly after it lands.
  const sheen = interpolate(frame - delay, [10, 45], [-130, 130], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        transform: `translateY(${y}px)`,
        opacity,
        position: "relative",
        overflow: "hidden",
        display: "flex",
        alignItems: "center",
        gap: 40,
        padding: "40px 52px",
        borderRadius: 36,
        background: "rgba(255,255,255,0.04)",
        border: `1px solid ${COLORS.hairline}`,
        boxShadow: `0 24px 80px rgba(0,0,0,0.45), inset 0 0 0 1px rgba(255,255,255,0.02)`,
        backdropFilter: "blur(8px)",
        width: "100%",
      }}
    >
      {/* sheen */}
      <div
        style={{
          position: "absolute",
          top: 0,
          bottom: 0,
          left: `${sheen}%`,
          width: "45%",
          background: "linear-gradient(105deg, transparent, rgba(255,255,255,0.10), transparent)",
          transform: "skewX(-18deg)",
          pointerEvents: "none",
        }}
      />
      {/* Number */}
      <div
        style={{
          fontFamily: FONTS.display,
          fontWeight: 700,
          fontSize: 168,
          lineHeight: 1,
          letterSpacing: "-0.04em",
          backgroundImage: BLUE_GRADIENT,
          WebkitBackgroundClip: "text",
          backgroundClip: "text",
          color: "transparent",
          textShadow: `0 0 ${30 * glow}px ${COLORS.glow}`,
          minWidth: 360,
          textAlign: "right",
          whiteSpace: "nowrap", // ponytail: never reflow mid-count; keep suffixes short (units go in label)
        }}
      >
        {stat.prefix ?? ""}
        {display}
        {stat.suffix ?? ""}
      </div>

      {/* Accent bar + label */}
      <div style={{ display: "flex", alignItems: "center", gap: 28, flex: 1 }}>
        <div
          style={{
            width: 8,
            height: 96,
            borderRadius: 8,
            backgroundImage: BLUE_GRADIENT,
            boxShadow: `0 0 24px ${COLORS.glow}`,
          }}
        />
        <div
          style={{
            fontFamily: FONTS.body,
            fontWeight: 700,
            fontSize: 46,
            lineHeight: 1.08,
            color: COLORS.white,
            letterSpacing: "-0.01em",
          }}
        >
          {stat.label}
        </div>
      </div>
    </div>
  );
};

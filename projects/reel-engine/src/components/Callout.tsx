import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { COLORS, FONTS } from "../brand";

/**
 * A floating annotation pill (the reference's "60% avg fill" callout). Pops in
 * with a glowing dot + label. Positioned by the parent (absolute or inline).
 */
export const Callout: React.FC<{ text: string; delay?: number }> = ({ text, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: frame - delay, fps, config: { damping: 200, mass: 0.8 } });
  const op = interpolate(enter, [0, 1], [0, 1]);
  const s = interpolate(enter, [0, 1], [0.82, 1]);
  const y = interpolate(enter, [0, 1], [14, 0]);
  const pulse = 0.7 + 0.3 * Math.sin((frame / fps) * 3);

  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 14,
        padding: "14px 24px",
        borderRadius: 999,
        background: "rgba(18,26,42,0.92)",
        border: `1px solid ${COLORS.blueLight}`,
        boxShadow: `0 12px 34px rgba(0,0,0,0.5), 0 0 26px ${COLORS.glow}`,
        opacity: op,
        transform: `translateY(${y}px) scale(${s})`,
        whiteSpace: "nowrap",
      }}
    >
      <div
        style={{
          width: 12,
          height: 12,
          borderRadius: "50%",
          background: COLORS.blueLight,
          boxShadow: `0 0 ${10 + 8 * pulse}px ${COLORS.glow}`,
        }}
      />
      <span style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 30, color: COLORS.white }}>{text}</span>
    </div>
  );
};

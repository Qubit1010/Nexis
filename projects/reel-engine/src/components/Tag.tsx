import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { COLORS, FONTS } from "../brand";

/** Small uppercase kicker pill used above headlines. */
export const Tag: React.FC<{ label: string; delay?: number }> = ({ label, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: frame - delay, fps, config: { damping: 200 } });
  const opacity = interpolate(enter, [0, 1], [0, 1]);
  const y = interpolate(enter, [0, 1], [-18, 0]);

  return (
    <div
      style={{
        opacity,
        transform: `translateY(${y}px)`,
        alignSelf: "center",
        display: "inline-flex",
        alignItems: "center",
        gap: 16,
        padding: "16px 30px",
        borderRadius: 999,
        border: `1px solid ${COLORS.hairline}`,
        background: "rgba(32,142,199,0.10)",
      }}
    >
      <span style={{ width: 12, height: 12, borderRadius: 999, background: COLORS.blueLight, boxShadow: `0 0 16px ${COLORS.glow}` }} />
      <span
        style={{
          fontFamily: FONTS.body,
          fontWeight: 700,
          fontSize: 30,
          letterSpacing: "0.28em",
          textTransform: "uppercase",
          color: COLORS.white,
        }}
      >
        {label}
      </span>
    </div>
  );
};

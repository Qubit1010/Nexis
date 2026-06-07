import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { COLORS } from "../brand";

/**
 * An animated pointer that glides to a target and "clicks" (expanding ring), like
 * the reference's UI walkthrough cursor. Positioned by the parent; (x,y) is the
 * resting target in the parent's local coordinates; it eases in from `from`.
 */
export const Cursor: React.FC<{
  x: number;
  y: number;
  from?: { x: number; y: number };
  delay?: number;
}> = ({ x, y, from, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f0 = from ?? { x: x + 180, y: y - 140 };

  const move = spring({ frame: frame - delay, fps, config: { damping: 20, stiffness: 80, mass: 1 } });
  const cx = interpolate(move, [0, 1], [f0.x, x]);
  const cy = interpolate(move, [0, 1], [f0.y, y]);
  const op = interpolate(frame - delay, [0, 7], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Click ring shortly after arrival.
  const ring = interpolate(frame - delay, [26, 44], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const ringOp = interpolate(frame - delay, [26, 44], [0.7, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <div style={{ position: "absolute", left: cx, top: cy, opacity: op, pointerEvents: "none", zIndex: 5 }}>
      <div
        style={{
          position: "absolute",
          left: 2,
          top: 2,
          width: 64,
          height: 64,
          marginLeft: -32,
          marginTop: -32,
          borderRadius: "50%",
          border: `3px solid ${COLORS.blueLight}`,
          transform: `scale(${ring})`,
          opacity: ringOp,
        }}
      />
      <svg width="44" height="44" viewBox="0 0 24 24" style={{ filter: "drop-shadow(0 4px 8px rgba(0,0,0,0.55))" }}>
        <path
          d="M4 2 L4 19 L8.5 14.8 L11.3 21 L14 19.9 L11.2 13.8 L18 13.8 Z"
          fill="#ffffff"
          stroke={COLORS.blueDeep}
          strokeWidth="1"
          strokeLinejoin="round"
        />
      </svg>
    </div>
  );
};

import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from "remotion";
import { COLORS, FONTS } from "../brand";

/**
 * A giant kinetic-type wipe that sweeps through on a scene's entry (the reference's
 * oversized "Waste" / "Arlo" word moments). Rendered as a brief ADDITIVE overlay
 * over the first ~14 frames so it never shifts scene timing or desyncs captions.
 * The word overflows the frame on purpose (cropped giant type). Style cycles by
 * `variant` (scale-through / side-wipe / blur-dissolve).
 */
export const TypeTransition: React.FC<{ word: string; variant?: number; durationInFrames?: number }> = ({
  word,
  variant = 0,
  durationInFrames = 26,
}) => {
  const frame = useCurrentFrame();
  if (!word || frame >= durationInFrames) return null;

  // Slow, smooth glide: gentle ease-in-out, with the word holding softly mid-wipe.
  const p = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.33, 0, 0.2, 1),
  });
  const opacity = interpolate(p, [0, 0.3, 0.72, 1], [0, 0.4, 0.4, 0]);

  const v = ((variant % 3) + 3) % 3;
  let transform = "";
  let blur = 0;
  if (v === 0) {
    transform = `scale(${interpolate(p, [0, 1], [0.85, 1.9])})`;
  } else if (v === 1) {
    transform = `translateX(${interpolate(p, [0, 1], [-48, 48])}%) scale(1.22)`;
  } else {
    transform = `scale(${interpolate(p, [0, 1], [1.32, 1.0])})`;
    blur = interpolate(p, [0, 1], [0, 22]);
  }

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", pointerEvents: "none", overflow: "hidden" }}>
      <div
        style={{
          fontFamily: FONTS.display,
          fontWeight: 700,
          fontSize: 420,
          lineHeight: 1,
          letterSpacing: "-0.04em",
          textTransform: "uppercase",
          color: COLORS.blueLight,
          opacity,
          transform,
          filter: blur ? `blur(${blur}px)` : "none",
          whiteSpace: "nowrap",
          textShadow: `0 0 60px ${COLORS.glow}`,
        }}
      >
        {word}
      </div>
    </AbsoluteFill>
  );
};

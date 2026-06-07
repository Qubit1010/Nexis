import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";

/**
 * Wraps a panel (a native infographic rebuild) so it flies in as a tilted 3D
 * card and settles flat for readability, then keeps a subtle continuous float.
 * Mirrors the reference's floating-dashboard showcase without leaving the content
 * permanently skewed (text stays crisp once settled).
 */
export const Perspective3D: React.FC<{ children: React.ReactNode; delay?: number; intensity?: number }> = ({
  children,
  delay = 6,
  intensity = 1,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({ frame: frame - delay, fps, config: { damping: 200, mass: 1.1, stiffness: 90 } });
  const rotY = interpolate(enter, [0, 1], [20 * intensity, 0]);
  const rotX = interpolate(enter, [0, 1], [12 * intensity, 0]);
  const tz = interpolate(enter, [0, 1], [-260 * intensity, 0]);

  // Gentle continuous float after settling (subtle, keeps text readable).
  const settle = interpolate(enter, [0, 1], [0, 1]);
  const floatY = Math.sin((frame / fps) * 1.0) * 5 * settle;
  const floatRX = Math.sin((frame / fps) * 0.7) * 0.8 * settle;

  return (
    <div style={{ perspective: 1500, perspectiveOrigin: "50% 42%", width: "100%", display: "flex", justifyContent: "center" }}>
      <div
        style={{
          transformStyle: "preserve-3d",
          transform: `translateZ(${tz}px) rotateX(${rotX + floatRX}deg) rotateY(${rotY}deg) translateY(${floatY}px)`,
          width: "100%",
          display: "flex",
          justifyContent: "center",
        }}
      >
        {children}
      </div>
    </div>
  );
};

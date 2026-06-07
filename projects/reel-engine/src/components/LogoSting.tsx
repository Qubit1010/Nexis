import React from "react";
import { Img, staticFile, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { evolvePath } from "@remotion/paths";
import { COLORS, FONTS } from "../brand";

/**
 * Cinematic outro logo reveal: an accent line draws on, the white NexusPoint
 * lockup wipes in left-to-right with a blooming glow, then the one-line mantra
 * rises. Approximates the reference's line-art logo reveal.
 */
export const LogoSting: React.FC<{ delay?: number }> = ({ delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Logo wipe-in + scale + glow bloom.
  const enter = spring({ frame: frame - delay, fps, config: { damping: 200, stiffness: 90, mass: 1 } });
  const wipe = interpolate(enter, [0, 1], [100, 0]); // clip-path inset from the right
  const scale = interpolate(enter, [0, 1], [0.92, 1]);
  const opacity = interpolate(enter, [0, 1], [0, 1]);
  const glowBloom = interpolate(frame - delay, [6, 26, 46], [0, 26, 12], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Accent underline draws on first.
  const draw = spring({ frame: frame - delay, fps, config: { damping: 200 } });
  const lineD = "M 40 6 L 520 6";
  const evolved = evolvePath(draw, lineD);

  // Mantra rises after.
  const mantra = spring({ frame: frame - delay - 12, fps, config: { damping: 200 } });
  const mantraOpacity = interpolate(mantra, [0, 1], [0, 1]);
  const mantraY = interpolate(mantra, [0, 1], [22, 0]);

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 34, transform: `scale(${scale})`, opacity }}>
      <Img
        src={staticFile("logo/nexuspoint-logo.png")}
        style={{
          width: 560,
          // Pure black source -> white, plus a blooming blue glow, revealed by a wipe.
          filter: `brightness(0) invert(1) drop-shadow(0 0 ${glowBloom}px rgba(32,142,199,0.8))`,
          clipPath: `inset(0 ${wipe}% 0 0)`,
        }}
      />

      <svg viewBox="0 0 560 12" width={560} height={12} style={{ marginTop: -6 }}>
        <path
          d={lineD}
          fill="none"
          stroke={COLORS.blueLight}
          strokeWidth={3}
          strokeLinecap="round"
          strokeDasharray={evolved.strokeDasharray}
          strokeDashoffset={evolved.strokeDashoffset}
          style={{ filter: `drop-shadow(0 0 10px ${COLORS.glow})` }}
        />
      </svg>

      <div
        style={{
          opacity: mantraOpacity,
          transform: `translateY(${mantraY}px)`,
          fontFamily: FONTS.body,
          fontWeight: 700,
          fontSize: 30,
          letterSpacing: "0.2em",
          textTransform: "uppercase",
          color: COLORS.blueLight,
          whiteSpace: "nowrap",
        }}
      >
        Innovate&nbsp;&nbsp;|&nbsp;&nbsp;Create&nbsp;&nbsp;|&nbsp;&nbsp;Elevate
      </div>
    </div>
  );
};

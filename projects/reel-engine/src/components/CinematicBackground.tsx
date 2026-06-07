import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { noise2D } from "@remotion/noise";
import { COLORS, CANVAS_GRADIENT } from "../brand";

/**
 * Cinematic brand canvas: a noise-driven particle dot-field that flows like a 3D
 * wave (rising from the bottom), plus a few drifting wave-lines and soft aurora
 * glow. Edges stay anchored (static stripes + vignette) per brand feedback; all
 * motion lives in the interior.
 *
 * One continuous wave runs the whole reel (motion never resets between scenes).
 * `heroWindows` are global frame ranges (intro/punch) where the field swells to
 * full "hero" intensity; elsewhere it eases back to "calm" so scene text stays
 * readable. Deterministic (noise + frame only), bounded element count for speed.
 */

const W = 1080;
const H = 1920;
const COLS = 18;
const ROWS = 16; // 288 dots

const CYAN = "#5BC8F0";

export const CinematicBackground: React.FC<{ heroWindows?: [number, number][] }> = ({ heroWindows = [] }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  // Smooth hero<->calm intensity from the global frame (ramps at window edges).
  let intensity = 0;
  for (const [a, b] of heroWindows) {
    const up = interpolate(frame, [a - 2, a + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const down = interpolate(frame, [b - 12, b + 2], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    intensity = Math.max(intensity, Math.min(up, down));
  }
  const amp = 34 + 44 * intensity;
  const dotMax = 0.46 + 0.39 * intensity;

  // Particle wave field.
  const dots: { x: number; y: number; r: number; op: number; blue: boolean }[] = [];
  for (let row = 0; row < ROWS; row++) {
    for (let col = 0; col < COLS; col++) {
      const baseX = (col + 0.5) * (W / COLS);
      const baseY = (row + 0.5) * (H / ROWS);
      const n = noise2D("wave", baseX * 0.0016 + t * 0.05, baseY * 0.0016);
      const n2 = noise2D("wave2", baseX * 0.0032 - t * 0.04, baseY * 0.0032);
      const x = baseX + n2 * 16;
      const y = baseY + n * amp + n2 * amp * 0.4;
      const vrt = baseY / H; // brighter toward the bottom (wave rises from below)
      const weight = 0.22 + 0.78 * vrt;
      const tw = 0.5 + 0.5 * noise2D("tw", col * 0.5 + t * 0.6, row * 0.5);
      dots.push({
        x,
        y,
        r: 2.6 + 0.7 * intensity,
        op: dotMax * weight * (0.4 + 0.6 * tw),
        blue: n > 0,
      });
    }
  }

  // Flowing wave-lines.
  const lines = [0, 1, 2].map((i) => {
    const cy = H * (0.6 + i * 0.085);
    const pts: string[] = [];
    for (let s = 0; s <= 36; s++) {
      const x = (s / 36) * W;
      const y =
        cy +
        noise2D("ln" + i, x * 0.0022 + t * 0.08, i) * (50 + 42 * intensity) +
        Math.sin(x * 0.006 + t + i) * (12 + 8 * intensity);
      pts.push(`${x.toFixed(1)},${y.toFixed(1)}`);
    }
    return { d: "M" + pts.join(" L"), op: (0.26 + 0.24 * intensity) - i * 0.06 };
  });

  // Drifting aurora glow blobs (interior depth).
  const blobs = [
    { x: 26, y: 30, r: 560, hue: COLORS.blueLight, sp: 0.4, ph: 0 },
    { x: 76, y: 72, r: 620, hue: COLORS.blueDeep, sp: 0.33, ph: 2.2 },
  ];

  return (
    <AbsoluteFill style={{ background: CANVAS_GRADIENT, overflow: "hidden" }}>
      {/* STATIC diagonal stripe texture — anchored edges */}
      <AbsoluteFill
        style={{
          backgroundImage: `repeating-linear-gradient(135deg, transparent 0px, transparent 94px, rgba(0,0,0,0.5) 94px, rgba(0,0,0,0.5) 95px, transparent 95px, transparent 158px, rgba(32,142,199,0.06) 158px, rgba(32,142,199,0.06) 159px)`,
          opacity: 0.55,
        }}
      />

      {blobs.map((b, i) => {
        const dx = Math.sin(t * b.sp + b.ph) * 60;
        const dy = Math.cos(t * b.sp * 0.8 + b.ph) * 44;
        const op = 0.2 + 0.1 * Math.sin(t * b.sp + b.ph * 1.5);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${b.x}%`,
              top: `${b.y}%`,
              width: b.r,
              height: b.r,
              marginLeft: -b.r / 2,
              marginTop: -b.r / 2,
              borderRadius: "50%",
              background: `radial-gradient(circle, ${b.hue} 0%, transparent 68%)`,
              filter: "blur(70px)",
              transform: `translate(${dx}px, ${dy}px)`,
              opacity: op,
            }}
          />
        );
      })}

      <svg viewBox={`0 0 ${W} ${H}`} width="100%" height="100%" style={{ position: "absolute", inset: 0 }} preserveAspectRatio="xMidYMid slice">
        {lines.map((ln, i) => (
          <path key={`ln${i}`} d={ln.d} fill="none" stroke={COLORS.blueLight} strokeWidth={2} opacity={Math.max(0, ln.op)} />
        ))}
        {dots.map((d, i) => (
          <circle key={`d${i}`} cx={d.x} cy={d.y} r={d.r} fill={d.blue ? COLORS.blueLight : CYAN} opacity={d.op} />
        ))}
      </svg>

      {/* STATIC vignette — anchors + darkens the edges */}
      <AbsoluteFill
        style={{
          background: "radial-gradient(80% 64% at 50% 46%, transparent 36%, rgba(0,0,0,0.62) 100%)",
        }}
      />
    </AbsoluteFill>
  );
};

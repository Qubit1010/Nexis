import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, CANVAS_GRADIENT } from "../brand";

/**
 * The shared NexusPoint canvas. Everything that touches the FRAME EDGES is
 * static (base gradient, diagonal stripe texture, vignette) so the edges never
 * appear to move. All motion lives in the INTERIOR: slow-drifting blurred blue
 * "aurora" blobs and floating ambient particles. Fluid, but anchored.
 */

const BLOBS = [
  { x: 24, y: 26, r: 560, hue: COLORS.blueLight, ax: 60, ay: 40, sp: 0.45, ph: 0 },
  { x: 78, y: 70, r: 620, hue: COLORS.blueDeep, ax: 70, ay: 55, sp: 0.38, ph: 2.1 },
  { x: 60, y: 18, r: 420, hue: COLORS.blueLight, ax: 50, ay: 35, sp: 0.55, ph: 4.2 },
];

// Deterministic ambient particles (no per-frame randomness).
const PARTICLES = Array.from({ length: 22 }, (_, i) => {
  const seed = (n: number) => ((Math.sin((i + 1) * 12.9898 * n) * 43758.5453) % 1 + 1) % 1;
  return {
    x: seed(1) * 100,
    yBase: seed(2) * 100,
    size: 2 + seed(3) * 4,
    speed: 4 + seed(4) * 9, // % of height per second, upward
    drift: (seed(5) - 0.5) * 6,
    twinkle: 2 + seed(6) * 3,
    blue: seed(7) > 0.5,
  };
});

export const BrandBackground: React.FC<{ accent?: boolean }> = ({ accent = true }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  return (
    <AbsoluteFill style={{ background: CANVAS_GRADIENT, overflow: "hidden" }}>
      {/* STATIC diagonal stripe texture — anchored, fills the frame */}
      <AbsoluteFill
        style={{
          backgroundImage: `repeating-linear-gradient(
            135deg,
            transparent 0px,
            transparent 94px,
            rgba(0,0,0,0.55) 94px,
            rgba(0,0,0,0.55) 95px,
            transparent 95px,
            transparent 158px,
            rgba(32,142,199,0.07) 158px,
            rgba(32,142,199,0.07) 159px
          )`,
          opacity: 0.7,
        }}
      />

      {accent ? (
        <>
          {/* INTERIOR aurora — soft blue blobs drifting + breathing */}
          {BLOBS.map((b, i) => {
            const dx = Math.sin(t * b.sp + b.ph) * b.ax;
            const dy = Math.cos(t * b.sp * 0.8 + b.ph) * b.ay;
            const scale = 1 + 0.12 * Math.sin(t * b.sp * 1.3 + b.ph);
            const op = 0.22 + 0.12 * Math.sin(t * b.sp + b.ph * 1.7);
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
                  filter: "blur(60px)",
                  transform: `translate(${dx}px, ${dy}px) scale(${scale})`,
                  opacity: op,
                }}
              />
            );
          })}

          {/* Floating ambient particles in the interior */}
          {PARTICLES.map((p, i) => {
            const y = (((p.yBase - t * p.speed) % 100) + 100) % 100;
            const x = p.x + Math.sin(t * 0.6 + i) * p.drift;
            const tw = 0.25 + 0.55 * Math.abs(Math.sin(t / p.twinkle + i));
            // Fade particles near the very top/bottom edges so they don't pop at borders.
            const edgeFade = Math.min(1, y / 12, (100 - y) / 12);
            return (
              <div
                key={i}
                style={{
                  position: "absolute",
                  left: `${x}%`,
                  top: `${y}%`,
                  width: p.size,
                  height: p.size,
                  borderRadius: "50%",
                  background: p.blue ? COLORS.blueLight : COLORS.white,
                  opacity: tw * 0.5 * edgeFade,
                  boxShadow: p.blue ? `0 0 8px ${COLORS.glow}` : "none",
                }}
              />
            );
          })}
        </>
      ) : null}

      {/* STATIC vignette — anchors and darkens the edges */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(78% 62% at 50% 44%, transparent 38%, rgba(0,0,0,0.6) 100%)",
        }}
      />
    </AbsoluteFill>
  );
};

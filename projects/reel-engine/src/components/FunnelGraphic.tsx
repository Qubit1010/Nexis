import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { COLORS, FONTS } from "../brand";
import type { FunnelStage } from "../types";

/**
 * A native, animated marketing funnel — the motion-graphics rebuild of a funnel
 * infographic. Stages stack and narrow toward the bottom (classic funnel), each
 * springing in with a stagger, numbered like the source art. Kept on-brand: the
 * segments step from bright to deep blue instead of the source's rainbow, so the
 * funnel sits inside the rest of the blue reel instead of fighting it.
 *
 * Driven by data (scene.funnel), so any post whose infographic is a funnel/pyramid/
 * step-flow can reuse this — just pass the stages.
 */

// hex helpers for the per-stage blue ramp
const toRgb = (h: string) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
const toHex = (a: number[]) =>
  "#" + a.map((v) => Math.round(Math.max(0, Math.min(255, v))).toString(16).padStart(2, "0")).join("");
const lerp = (a: number[], b: number[], t: number) => a.map((v, i) => v + (b[i] - v) * t);

const BRIGHT = toRgb("#2BA6D4"); // top of funnel
const DEEP = toRgb("#163F70"); // bottom of funnel
const WHITE = [255, 255, 255];

const stageGradient = (t: number) => {
  const base = lerp(BRIGHT, DEEP, t);
  const top = lerp(base, WHITE, 0.16);
  return `linear-gradient(135deg, ${toHex(top)} 0%, ${toHex(base)} 100%)`;
};

export const FunnelGraphic: React.FC<{ stages: FunnelStage[]; delay?: number }> = ({
  stages,
  delay = 6,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const n = Math.max(1, stages.length);

  return (
    <div
      style={{
        width: "100%",
        maxWidth: 880,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 16,
      }}
    >
      {/* Flow arrows pouring into the funnel (echoes the source art). */}
      <div style={{ display: "flex", gap: 14, marginBottom: 4 }}>
        {[0, 1, 2].map((i) => {
          const a = ((frame - i * 5) % 36) / 36; // 0..1 loop
          const op = 0.25 + 0.55 * Math.sin(a * Math.PI);
          return (
            <div
              key={i}
              style={{
                width: 0,
                height: 0,
                borderLeft: "11px solid transparent",
                borderRight: "11px solid transparent",
                borderTop: `16px solid ${COLORS.blueLight}`,
                opacity: op,
                transform: `translateY(${a * 8}px)`,
              }}
            />
          );
        })}
      </div>

      {stages.map((stage, i) => {
        const t = n === 1 ? 0 : i / (n - 1);
        const width = 100 - t * 28; // 100% -> 72% : a gentle funnel taper (keeps long labels readable)
        const enter = spring({
          frame: frame - delay - i * 7,
          fps,
          config: { damping: 200, stiffness: 110, mass: 0.8 },
        });
        const y = interpolate(enter, [0, 1], [-46, 0]);
        const opacity = interpolate(enter, [0, 1], [0, 1]);
        const sx = interpolate(enter, [0, 1], [0.92, 1]);

        return (
          <div
            key={i}
            style={{
              width: `${width}%`,
              transform: `translateY(${y}px) scaleX(${sx})`,
              opacity,
              display: "flex",
              alignItems: "center",
              gap: 26,
              padding: "26px 34px",
              borderRadius: 22,
              background: stageGradient(t),
              boxShadow: `0 18px 50px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.18)`,
            }}
          >
            {/* number badge — dark pill, like the source art */}
            <div
              style={{
                flexShrink: 0,
                width: 64,
                height: 64,
                borderRadius: 16,
                background: COLORS.charcoalDeep,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontFamily: FONTS.display,
                fontWeight: 700,
                fontSize: 38,
                color: COLORS.white,
              }}
            >
              {i + 1}
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 4, minWidth: 0 }}>
              <div
                style={{
                  fontFamily: FONTS.display,
                  fontWeight: 700,
                  fontSize: 40,
                  lineHeight: 1.04,
                  color: COLORS.white,
                  letterSpacing: "-0.01em",
                  whiteSpace: "nowrap",
                }}
              >
                {stage.name}
              </div>
              {stage.goal ? (
                <div
                  style={{
                    fontFamily: FONTS.body,
                    fontWeight: 600,
                    fontSize: 26,
                    lineHeight: 1.1,
                    color: "rgba(255,255,255,0.86)",
                    whiteSpace: "nowrap",
                  }}
                >
                  {stage.goal}
                </div>
              ) : null}
            </div>
          </div>
        );
      })}
    </div>
  );
};

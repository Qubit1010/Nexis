import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { COLORS, FONTS, BLUE_GRADIENT } from "../brand";
import { Callout } from "./Callout";
import { Cursor } from "./Cursor";
import type { FunnelStage } from "../types";

/**
 * A native, animated roadmap — the motion-graphics rebuild of a phased / step
 * infographic (e.g. "Context -> Fire -> Extend -> Scale"). A vertical spine draws
 * downward while numbered phase nodes pop in sequence, each with a card beside it.
 * On-brand blue. Driven by data (scene.roadmap), so any phased infographic reuses it.
 *
 * Fixed row geometry (ROW_H + ROW_GAP) keeps the spine math deterministic, so keep
 * phase names + goals short enough to sit on one line.
 */

const ROW_H = 150;
const ROW_GAP = 26;
const NODE = 84;
const PITCH = ROW_H + ROW_GAP;

export const RoadmapGraphic: React.FC<{ phases: FunnelStage[]; delay?: number; highlight?: number; callout?: string }> = ({
  phases,
  delay = 8,
  highlight,
  callout,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const n = Math.max(1, phases.length);

  // The spine runs from the first node's center to the last node's center.
  const spineHeight = (n - 1) * PITCH;
  const spineGrow = interpolate(frame - delay, [0, n * 9], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div style={{ position: "relative", width: "100%", maxWidth: 860 }}>
      {/* drawing spine */}
      <div
        style={{
          position: "absolute",
          left: NODE / 2 - 3,
          top: ROW_H / 2,
          width: 6,
          height: spineHeight,
          borderRadius: 6,
          backgroundImage: BLUE_GRADIENT,
          transform: `scaleY(${spineGrow})`,
          transformOrigin: "top",
          boxShadow: `0 0 22px ${COLORS.glow}`,
        }}
      />

      {phases.map((phase, i) => {
        const active = i === highlight;
        const enter = spring({
          frame: frame - delay - i * 9,
          fps,
          config: { damping: 200, stiffness: 120, mass: 0.8 },
        });
        const x = interpolate(enter, [0, 1], [40, 0]);
        const opacity = interpolate(enter, [0, 1], [0, 1]);
        const pop = interpolate(enter, [0, 1], [0.6, 1]);

        return (
          <div
            key={i}
            style={{
              position: "relative",
              height: ROW_H,
              marginBottom: i < n - 1 ? ROW_GAP : 0,
              display: "flex",
              alignItems: "center",
              gap: 30,
            }}
          >
            {/* numbered node */}
            <div
              style={{
                position: "relative",
                zIndex: 1,
                flexShrink: 0,
                width: NODE,
                height: NODE,
                borderRadius: "50%",
                backgroundImage: BLUE_GRADIENT,
                transform: `scale(${pop})`,
                opacity,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontFamily: FONTS.display,
                fontWeight: 700,
                fontSize: 40,
                color: COLORS.white,
                boxShadow: active
                  ? `0 0 46px ${COLORS.blueLight}, inset 0 1px 0 rgba(255,255,255,0.3)`
                  : `0 0 28px ${COLORS.glow}, inset 0 1px 0 rgba(255,255,255,0.25)`,
                border: active ? `3px solid ${COLORS.white}` : `3px solid ${COLORS.charcoalDeep}`,
              }}
            >
              {i + 1}
            </div>

            {/* phase card */}
            <div
              style={{
                flex: 1,
                opacity,
                transform: `translateX(${x}px)`,
                display: "flex",
                flexDirection: "row",
                alignItems: "center",
                gap: 20,
                height: ROW_H,
                padding: "0 38px",
                borderRadius: 24,
                background: active ? "rgba(32,142,199,0.10)" : "rgba(255,255,255,0.04)",
                border: active ? `1px solid ${COLORS.blueLight}` : `1px solid ${COLORS.hairline}`,
                boxShadow: active
                  ? `0 18px 50px rgba(0,0,0,0.4), 0 0 34px ${COLORS.glow}`
                  : "0 18px 50px rgba(0,0,0,0.4)",
                backdropFilter: "blur(8px)",
              }}
            >
              <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", gap: 6, minWidth: 0 }}>
                <div
                  style={{
                    fontFamily: FONTS.display,
                    fontWeight: 700,
                    fontSize: 52,
                    lineHeight: 1.02,
                    color: COLORS.white,
                    letterSpacing: "-0.01em",
                    whiteSpace: "nowrap",
                  }}
                >
                  {phase.name}
                </div>
                {phase.goal ? (
                  <div
                    style={{
                      fontFamily: FONTS.body,
                      fontWeight: 600,
                      fontSize: 30,
                      color: COLORS.fog,
                      whiteSpace: "nowrap",
                    }}
                  >
                    {phase.goal}
                  </div>
                ) : null}
              </div>
              {active && callout ? (
                <div style={{ marginLeft: "auto", paddingLeft: 18 }}>
                  <Callout text={callout} delay={delay + i * 9 + 16} />
                </div>
              ) : null}
            </div>

            {active ? <Cursor x={64} y={46} from={{ x: 320, y: -120 }} delay={delay + i * 9 + 10} /> : null}
          </div>
        );
      })}
    </div>
  );
};

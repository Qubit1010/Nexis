import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { COLORS, FONTS } from "../brand";
import { Callout } from "./Callout";
import { Cursor } from "./Cursor";
import type { FunnelStage } from "../types";

/**
 * A native, animated layer stack — the motion-graphics rebuild of a layered /
 * "stack" infographic (e.g. "Layer 1 ... Layer 5"). Equal-width slabs with a 3D
 * thickness edge stack top-to-bottom, each dropping into place in sequence.
 * On-brand blue ramp. Driven by data (scene.layers); reuse for any stacked diagram.
 */

const toRgb = (h: string) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
const toHex = (a: number[]) =>
  "#" + a.map((v) => Math.round(Math.max(0, Math.min(255, v))).toString(16).padStart(2, "0")).join("");
const lerp = (a: number[], b: number[], t: number) => a.map((v, i) => v + (b[i] - v) * t);

const BRIGHT = toRgb("#2BA6D4");
const DEEP = toRgb("#163F70");
const WHITE = [255, 255, 255];
const SHADOW = [8, 16, 28];

const slabFace = (t: number) => {
  const base = lerp(BRIGHT, DEEP, t);
  const top = lerp(base, WHITE, 0.14);
  return `linear-gradient(135deg, ${toHex(top)} 0%, ${toHex(base)} 100%)`;
};
const slabEdge = (t: number) => toHex(lerp(lerp(BRIGHT, DEEP, t), SHADOW, 0.5));

export const LayersGraphic: React.FC<{ layers: FunnelStage[]; delay?: number; highlight?: number; callout?: string }> = ({
  layers,
  delay = 8,
  highlight,
  callout,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const n = Math.max(1, layers.length);

  return (
    <div style={{ width: "100%", maxWidth: 880, display: "flex", flexDirection: "column", gap: 22 }}>
      {layers.map((layer, i) => {
        const t = n === 1 ? 0 : i / (n - 1);
        const active = i === highlight;
        const enter = spring({
          frame: frame - delay - i * 8,
          fps,
          config: { damping: 200, stiffness: 120, mass: 0.8 },
        });
        const y = interpolate(enter, [0, 1], [-36, 0]);
        const opacity = interpolate(enter, [0, 1], [0, 1]);

        return (
          <div
            key={i}
            style={{
              position: "relative",
              transform: `translateY(${y}px)`,
              opacity,
              display: "flex",
              alignItems: "center",
              gap: 28,
              padding: "26px 36px",
              borderRadius: 20,
              background: slabFace(t),
              // 3D thickness edge + drop shadow so the slabs read as a physical stack;
              // the highlighted slab gets an extra blue ring + glow.
              boxShadow: active
                ? `0 11px 0 ${slabEdge(t)}, 0 26px 46px rgba(0,0,0,0.5), inset 0 0 0 2px ${COLORS.blueLight}, 0 0 38px ${COLORS.glow}`
                : `0 11px 0 ${slabEdge(t)}, 0 26px 46px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.2)`,
            }}
          >
            {/* number badge */}
            <div
              style={{
                flexShrink: 0,
                width: 66,
                height: 66,
                borderRadius: 15,
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
                  fontSize: 46,
                  lineHeight: 1.02,
                  color: COLORS.white,
                  letterSpacing: "-0.01em",
                  whiteSpace: "nowrap",
                }}
              >
                {layer.name}
              </div>
              {layer.goal ? (
                <div
                  style={{
                    fontFamily: FONTS.body,
                    fontWeight: 600,
                    fontSize: 27,
                    color: "rgba(255,255,255,0.86)",
                    whiteSpace: "nowrap",
                  }}
                >
                  {layer.goal}
                </div>
              ) : null}
            </div>

            {/* Annotation on the highlighted slab: callout pill (right) + cursor click */}
            {active && callout ? (
              <div style={{ marginLeft: "auto", paddingLeft: 20 }}>
                <Callout text={callout} delay={delay + i * 8 + 16} />
              </div>
            ) : null}
            {active ? <Cursor x={104} y={28} from={{ x: 340, y: -140 }} delay={delay + i * 8 + 10} /> : null}
          </div>
        );
      })}
    </div>
  );
};

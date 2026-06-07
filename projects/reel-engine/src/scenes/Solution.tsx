import React from "react";
import {
  AbsoluteFill,
  Img,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";
import { SAFE, COLORS, BLUE_GRADIENT } from "../brand";
import { KineticHeadline } from "../components/KineticHeadline";
import { FunnelGraphic } from "../components/FunnelGraphic";
import { RoadmapGraphic } from "../components/RoadmapGraphic";
import { LayersGraphic } from "../components/LayersGraphic";
import { Perspective3D } from "../components/Perspective3D";
import type { Scene } from "../types";

const FRAME_H = 980;
const INFOGRAPHIC_AR = 922 / 1152; // matches public/reels/codegraph/infographic.png

/**
 * Solution scene. Two visual modes:
 *  - "funnel": a native animated funnel rebuilt from the infographic (scene.funnel).
 *  - default ("infographic"): a framed "device screen" that slowly zooms + pans
 *    DOWN the post's infographic. Falls back to a node-graph when none is present.
 */
export const Solution: React.FC<{ scene: Scene; slug: string; hasInfographic: boolean }> = ({
  scene,
  slug,
  hasInfographic,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Native motion modes: rebuild the infographic instead of panning a flat image.
  if (scene.visual === "funnel" && scene.funnel && scene.funnel.length > 0) {
    return (
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          padding: `${SAFE.top - 80}px ${SAFE.x}px ${SAFE.bottom - 140}px`,
          gap: 48,
        }}
      >
        <KineticHeadline text={scene.headline ?? ""} fontSize={78} delay={2} align="center" />
        <Perspective3D delay={6}>
          <FunnelGraphic stages={scene.funnel} delay={12} />
        </Perspective3D>
      </AbsoluteFill>
    );
  }
  if (scene.visual === "roadmap" && scene.roadmap && scene.roadmap.length > 0) {
    return (
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          padding: `${SAFE.top - 80}px ${SAFE.x}px ${SAFE.bottom - 140}px`,
          gap: 48,
        }}
      >
        <KineticHeadline text={scene.headline ?? ""} fontSize={74} delay={2} align="center" />
        <Perspective3D delay={6}>
          <RoadmapGraphic
            phases={scene.roadmap}
            delay={12}
            highlight={scene.cursorTarget}
            callout={scene.callouts?.[0]?.text}
          />
        </Perspective3D>
      </AbsoluteFill>
    );
  }
  if (scene.visual === "layers" && scene.layers && scene.layers.length > 0) {
    return (
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          padding: `${SAFE.top - 80}px ${SAFE.x}px ${SAFE.bottom - 140}px`,
          gap: 48,
        }}
      >
        <KineticHeadline text={scene.headline ?? ""} fontSize={74} delay={2} align="center" />
        <Perspective3D delay={6}>
          <LayersGraphic
            layers={scene.layers}
            delay={12}
            highlight={scene.cursorTarget}
            callout={scene.callouts?.[0]?.text}
          />
        </Perspective3D>
      </AbsoluteFill>
    );
  }

  const frameEnter = spring({ frame: frame - 14, fps, config: { damping: 200, mass: 0.9 } });
  const frameScale = interpolate(frameEnter, [0, 1], [0.88, 1]);
  const frameOpacity = interpolate(frameEnter, [0, 1], [0, 1]);
  const glowPulse = 0.5 + 0.5 * Math.sin(frame / fps * 1.6);

  // Slow zoom + downward pan across the infographic.
  const zoom = interpolate(frame, [14, 330], [1.02, 1.16], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const overflow = (zoom - 1) * FRAME_H;
  const panY = interpolate(frame, [14, 330], [overflow * 0.5, -overflow * 0.5], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: `${SAFE.top - 60}px ${SAFE.x}px ${SAFE.bottom - 120}px`,
        gap: 56,
      }}
    >
      <KineticHeadline text={scene.headline ?? ""} fontSize={82} delay={2} align="center" />

      <div
        style={{
          transform: `scale(${frameScale})`,
          opacity: frameOpacity,
          height: FRAME_H,
          aspectRatio: `${INFOGRAPHIC_AR}`,
          borderRadius: 36,
          overflow: "hidden",
          position: "relative",
          border: `1px solid ${COLORS.hairline}`,
          boxShadow: `0 30px 90px rgba(0,0,0,0.6), 0 0 ${50 + 30 * glowPulse}px ${COLORS.glow}`,
          background: COLORS.charcoalDeep,
        }}
      >
        {/* Top blue accent bar (app-window feel) */}
        <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 7, backgroundImage: BLUE_GRADIENT, zIndex: 2 }} />

        {hasInfographic ? (
          <Img
            src={staticFile(`reels/${slug}/infographic.png`)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              objectPosition: "center top",
              transform: `translateY(${panY}px) scale(${zoom})`,
            }}
          />
        ) : (
          <NodeGraphFallback />
        )}

        {/* Soft inner edge highlight */}
        <AbsoluteFill style={{ boxShadow: "inset 0 0 60px rgba(0,0,0,0.5)", borderRadius: 36, pointerEvents: "none" }} />
      </div>
    </AbsoluteFill>
  );
};

/** Abstract animated knowledge-graph used when no infographic is supplied. */
const NodeGraphFallback: React.FC = () => {
  const frame = useCurrentFrame();
  const nodes = [
    { x: 50, y: 26 },
    { x: 24, y: 50 },
    { x: 76, y: 48 },
    { x: 36, y: 76 },
    { x: 66, y: 78 },
    { x: 50, y: 52 },
  ];
  const edges = [
    [5, 0],
    [5, 1],
    [5, 2],
    [5, 3],
    [5, 4],
    [1, 3],
    [2, 4],
  ];

  return (
    <AbsoluteFill style={{ background: COLORS.charcoalDeep }}>
      <svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet" style={{ width: "100%", height: "100%" }}>
        {edges.map(([a, b], i) => {
          const prog = interpolate((frame - i * 4) % 90, [0, 45, 90], [0.2, 1, 0.2]);
          return (
            <line key={i} x1={nodes[a].x} y1={nodes[a].y} x2={nodes[b].x} y2={nodes[b].y} stroke={COLORS.blueLight} strokeWidth={0.4} opacity={prog} />
          );
        })}
        {nodes.map((n, i) => {
          const pulse = 1 + 0.25 * Math.sin((frame - i * 8) / 8);
          return <circle key={i} cx={n.x} cy={n.y} r={(i === 5 ? 3.4 : 2.2) * pulse} fill={i === 5 ? COLORS.blueLight : COLORS.white} opacity={i === 5 ? 1 : 0.85} />;
        })}
      </svg>
    </AbsoluteFill>
  );
};

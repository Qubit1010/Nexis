import React from "react";
import { AbsoluteFill } from "remotion";
import { SAFE } from "../brand";
import { StatCounter } from "../components/StatCounter";
import { Tag } from "../components/Tag";
import type { Scene } from "../types";

/** Stats scene: small kicker + a stack of staggered count-up cards. */
export const Stats: React.FC<{ scene: Scene }> = ({ scene }) => {
  const stats = scene.stats ?? [];
  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: `${SAFE.top}px ${SAFE.x}px ${SAFE.bottom}px`,
        gap: 40,
      }}
    >
      <Tag label={scene.headline || "The Numbers"} delay={2} />
      <div style={{ display: "flex", flexDirection: "column", gap: 34, width: "100%", marginTop: 18 }}>
        {stats.map((stat, i) => (
          <StatCounter key={i} stat={stat} index={i} delay={14 + i * 14} />
        ))}
      </div>
    </AbsoluteFill>
  );
};

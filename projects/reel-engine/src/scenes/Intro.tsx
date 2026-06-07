import React from "react";
import { AbsoluteFill } from "remotion";
import { SAFE } from "../brand";
import { KineticHeadline } from "../components/KineticHeadline";
import { Tag } from "../components/Tag";
import type { Scene } from "../types";

export const Intro: React.FC<{ scene: Scene }> = ({ scene }) => {
  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: `${SAFE.top}px ${SAFE.x}px ${SAFE.bottom}px`,
        gap: 56,
      }}
    >
      <Tag label={scene.sub || "AI Engineering"} delay={2} />
      <KineticHeadline text={scene.headline ?? ""} fontSize={118} delay={10} align="center" />
    </AbsoluteFill>
  );
};

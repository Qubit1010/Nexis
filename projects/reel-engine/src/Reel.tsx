import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  staticFile,
  useCurrentFrame,
  interpolate,
} from "remotion";
import "./fonts";
import type { ReelContent, Scene, Timeline } from "./types";
import { CinematicBackground } from "./components/CinematicBackground";
import { TypeTransition } from "./components/TypeTransition";
import { Captions } from "./components/Captions";
import { Intro } from "./scenes/Intro";
import { Problem } from "./scenes/Problem";
import { Solution } from "./scenes/Solution";
import { Stats } from "./scenes/Stats";
import { Punch } from "./scenes/Punch";
import { Outro } from "./scenes/Outro";

export type ReelProps = {
  slug: string;
  content: ReelContent;
  timeline: Timeline;
  hasInfographic: boolean;
  audioReady: boolean;
  audioExt: string;
};

/** Single giant word for the entry wipe: explicit override, else the headline's *accent* word. */
const transitionWordFor = (scene: Scene): string | null => {
  if (scene.transitionWord) return scene.transitionWord;
  const m = scene.headline?.match(/\*([^*]+)\*/);
  return m ? m[1].trim().split(" ")[0] : null;
};

/** Intro + punch swell the background to "hero"; scene.bg can force it either way. */
const isHeroScene = (scene: Scene): boolean =>
  scene.bg === "hero" || (scene.bg !== "calm" && (scene.type === "intro" || scene.type === "punch"));

const renderScene = (scene: Scene, slug: string, hasInfographic: boolean, handle?: string) => {
  switch (scene.type) {
    case "intro":
      return <Intro scene={scene} />;
    case "problem":
      return <Problem scene={scene} />;
    case "solution":
      return <Solution scene={scene} slug={slug} hasInfographic={hasInfographic} />;
    case "stats":
      return <Stats scene={scene} />;
    case "punch":
      return <Punch scene={scene} />;
    case "outro":
      return <Outro scene={scene} handle={handle} />;
    default:
      return null;
  }
};

/** Fluid scene transition: content gently rises + scales in, sinks + scales out. */
const SceneWrap: React.FC<{ durationInFrames: number; children: React.ReactNode }> = ({
  durationInFrames,
  children,
}) => {
  const frame = useCurrentFrame();
  const fade = 9;
  const opacity = interpolate(
    frame,
    [0, fade, durationInFrames - fade, durationInFrames],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  const y = interpolate(
    frame,
    [0, fade, durationInFrames - fade, durationInFrames],
    [34, 0, 0, -26],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  const scale = interpolate(
    frame,
    [0, fade, durationInFrames - fade, durationInFrames],
    [1.04, 1, 1, 0.99],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  return (
    <AbsoluteFill style={{ opacity, transform: `translateY(${y}px) scale(${scale})` }}>
      {children}
    </AbsoluteFill>
  );
};

export const Reel: React.FC<ReelProps> = ({ slug, content, timeline, hasInfographic, audioReady, audioExt }) => {
  const sceneById = new Map(content.scenes.map((s) => [s.id, s]));

  // Global frame ranges where the particle field swells to "hero" intensity.
  const heroWindows = timeline.scenes
    .map((e) => ({ s: sceneById.get(e.sceneId), e }))
    .filter(({ s }) => s && isHeroScene(s))
    .map(({ e }) => [e.startFrame, e.endFrame] as [number, number]);

  return (
    <AbsoluteFill style={{ backgroundColor: "#161616" }}>
      {/* One continuous cinematic canvas behind every scene */}
      <CinematicBackground heroWindows={heroWindows} />

      {timeline.scenes.map((entry, i) => {
        const scene = sceneById.get(entry.sceneId);
        if (!scene) return null;
        const durationInFrames = Math.max(1, entry.endFrame - entry.startFrame);
        const word = transitionWordFor(scene);
        return (
          <Sequence
            key={entry.sceneId}
            from={entry.startFrame}
            durationInFrames={durationInFrames}
            name={`${scene.type}:${scene.id}`}
          >
            <SceneWrap durationInFrames={durationInFrames}>
              {renderScene(scene, slug, hasInfographic, content.handle)}
            </SceneWrap>
            {/* Giant kinetic-type wipe over the scene's first frames (sync-safe overlay) */}
            {word ? <TypeTransition word={word} variant={i} /> : null}
          </Sequence>
        );
      })}

      {/* Synced word captions ride on top of everything */}
      <Captions slug={slug} />

      {audioReady ? <Audio src={staticFile(`reels/${slug}/voiceover.${audioExt}`)} /> : null}
    </AbsoluteFill>
  );
};

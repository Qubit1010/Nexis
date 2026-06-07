import React from "react";
import { Composition, staticFile, type CalculateMetadataFunction } from "remotion";
import { Reel, type ReelProps } from "./Reel";
import { VIDEO } from "./brand";
import { buildTimeline } from "./timeline";
import type { ReelContent, Timeline } from "./types";

/** GET-probe a public asset; returns the Response if it exists, else null. */
const probe = async (url: string, signal?: AbortSignal): Promise<Response | null> => {
  try {
    const res = await fetch(url, { signal });
    return res.ok ? res : null;
  } catch {
    return null;
  }
};

const calculateMetadata: CalculateMetadataFunction<ReelProps> = async ({ props, abortSignal }) => {
  const { slug } = props;

  const contentRes = await probe(staticFile(`reels/${slug}/content.json`), abortSignal);
  if (!contentRes) {
    throw new Error(`Missing reels/${slug}/content.json`);
  }
  const content = (await contentRes.json()) as ReelContent;

  const [timelineRes, infographicRes, audioMp3Res, audioWavRes] = await Promise.all([
    probe(staticFile(`reels/${slug}/timeline.json`), abortSignal),
    probe(staticFile(`reels/${slug}/infographic.png`), abortSignal),
    probe(staticFile(`reels/${slug}/voiceover.mp3`), abortSignal),
    probe(staticFile(`reels/${slug}/voiceover.wav`), abortSignal),
  ]);

  // Prefer .wav (works around a compositor ffprobe issue with some mp3 encodings).
  const audioExt = audioWavRes ? "wav" : audioMp3Res ? "mp3" : null;

  const alignedTimeline = timelineRes ? ((await timelineRes.json()) as Timeline) : null;
  const timeline = buildTimeline(content, VIDEO.fps, alignedTimeline);

  return {
    durationInFrames: timeline.durationInFrames,
    fps: VIDEO.fps,
    width: VIDEO.width,
    height: VIDEO.height,
    props: {
      ...props,
      content,
      timeline,
      hasInfographic: Boolean(infographicRes),
      audioReady: Boolean(audioExt),
      audioExt: audioExt ?? "mp3",
    },
    defaultOutName: slug,
  };
};

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Reel"
      component={Reel}
      durationInFrames={1350}
      fps={VIDEO.fps}
      width={VIDEO.width}
      height={VIDEO.height}
      defaultProps={
        {
          slug: "codegraph",
          // Filled in by calculateMetadata; placeholders satisfy the type.
          content: { slug: "codegraph", platform: "instagram", title: "", voiceScript: "", scenes: [] },
          timeline: { fps: VIDEO.fps, durationInFrames: 1350, durationMs: 45000, aligned: false, scenes: [] },
          hasInfographic: false,
          audioReady: false,
          audioExt: "mp3",
        } as ReelProps
      }
      calculateMetadata={calculateMetadata}
    />
  );
};

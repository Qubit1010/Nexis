import type { ReelContent, Timeline, TimelineEntry } from "./types";

export const countWords = (text: string): number =>
  text.trim().split(/\s+/).filter(Boolean).length;

/** Natural TTS pace used for the pre-audio estimate (words per second). */
const WORDS_PER_SECOND = 2.6;
const MIN_SCENE_SECONDS = 2.6;

/**
 * Build the scene timeline. When an aligned timeline (produced by
 * scripts/prepare.mjs from the real voiceover) is available, use it verbatim.
 * Otherwise estimate scene durations from word counts so the composition is
 * fully previewable before the audio exists.
 */
export const buildTimeline = (
  content: ReelContent,
  fps: number,
  aligned: Timeline | null,
): Timeline => {
  if (aligned && aligned.aligned && aligned.scenes.length === content.scenes.length) {
    return aligned;
  }

  let cursor = 0;
  const scenes: TimelineEntry[] = content.scenes.map((scene) => {
    const seconds = Math.max(MIN_SCENE_SECONDS, countWords(scene.voiceText) / WORDS_PER_SECOND);
    const frames = Math.round(seconds * fps);
    const entry: TimelineEntry = {
      sceneId: scene.id,
      startFrame: cursor,
      endFrame: cursor + frames,
    };
    cursor += frames;
    return entry;
  });

  return {
    fps,
    durationInFrames: cursor,
    durationMs: Math.round((cursor / fps) * 1000),
    aligned: false,
    scenes,
  };
};

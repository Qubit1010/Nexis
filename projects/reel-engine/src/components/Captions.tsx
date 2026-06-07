import React, { useState, useEffect, useCallback, useMemo } from "react";
import {
  AbsoluteFill,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  useDelayRender,
} from "remotion";
import { createTikTokStyleCaptions, type Caption, type TikTokPage } from "@remotion/captions";
import { COLORS, FONTS } from "../brand";

const SWITCH_CAPTIONS_EVERY_MS = 900; // fewer words on screen = punchy, reel-style

/**
 * TikTok-style synced captions driven by word-level timestamps in
 * reels/<slug>/captions.json. If the file is absent (audio not transcribed
 * yet) it renders nothing, so the composition still previews cleanly.
 */
export const Captions: React.FC<{ slug: string }> = ({ slug }) => {
  const [captions, setCaptions] = useState<Caption[] | null>(null);
  const { delayRender, continueRender } = useDelayRender();
  const [handle] = useState(() => delayRender(`captions-${slug}`));

  const fetchCaptions = useCallback(async () => {
    try {
      const res = await fetch(staticFile(`reels/${slug}/captions.json`));
      if (!res.ok) throw new Error("no captions");
      setCaptions(await res.json());
    } catch {
      setCaptions([]); // graceful: no captions yet
    } finally {
      continueRender(handle);
    }
  }, [slug, continueRender, handle]);

  useEffect(() => {
    fetchCaptions();
  }, [fetchCaptions]);

  const pages = useMemo(() => {
    if (!captions || captions.length === 0) return [];
    return createTikTokStyleCaptions({
      captions,
      combineTokensWithinMilliseconds: SWITCH_CAPTIONS_EVERY_MS,
    }).pages;
  }, [captions]);

  if (!captions || pages.length === 0) return null;

  return (
    <AbsoluteFill>
      {pages.map((page, index) => (
        <PageSequence key={index} page={page} next={pages[index + 1] ?? null} />
      ))}
    </AbsoluteFill>
  );
};

const PageSequence: React.FC<{ page: TikTokPage; next: TikTokPage | null }> = ({ page, next }) => {
  const { fps } = useVideoConfig();
  const startFrame = (page.startMs / 1000) * fps;
  const endFrame = Math.min(
    next ? (next.startMs / 1000) * fps : Infinity,
    startFrame + (SWITCH_CAPTIONS_EVERY_MS / 1000) * fps,
  );
  const durationInFrames = Math.max(1, Math.round(endFrame - startFrame));

  return (
    <Sequence from={Math.round(startFrame)} durationInFrames={durationInFrames}>
      <CaptionPage page={page} />
    </Sequence>
  );
};

const CaptionPage: React.FC<{ page: TikTokPage }> = ({ page }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const absoluteTimeMs = page.startMs + (frame / fps) * 1000;

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: 300,
        paddingLeft: 70,
        paddingRight: 70,
      }}
    >
      <div
        style={{
          fontFamily: FONTS.body,
          fontWeight: 700,
          fontSize: 62,
          lineHeight: 1.12,
          textAlign: "center",
          whiteSpace: "pre-wrap",
          textShadow: "0 4px 22px rgba(0,0,0,0.85)",
        }}
      >
        {page.tokens.map((token) => {
          const isActive = token.fromMs <= absoluteTimeMs && token.toMs > absoluteTimeMs;
          return (
            <span
              key={`${token.fromMs}-${token.text}`}
              style={{
                color: isActive ? COLORS.blueLight : COLORS.white,
                textShadow: isActive ? `0 0 26px ${COLORS.glow}` : "0 4px 22px rgba(0,0,0,0.85)",
              }}
            >
              {token.text}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

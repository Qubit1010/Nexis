"use client";

import Image from "next/image";
import { ExternalLink } from "lucide-react";
import { SaveToSheetButton } from "./SaveToSheetButton";

interface TopVideo {
  videoId: string;
  title: string;
  channelName: string;
  url: string;
  thumbnailUrl: string | null;
  viewCount: number;
  publishedDate: string | null;
  performanceNote: string | null;
}

interface YouTubeTopVideosProps {
  videos: TopVideo[];
}

function formatViews(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`;
  return String(n);
}

export function YouTubeTopVideos({ videos }: YouTubeTopVideosProps) {
  if (!videos.length) return null;

  return (
    <div>
      <p className="text-[11px] font-semibold text-muted-foreground/60 uppercase tracking-[0.15em] mb-4">
        Top Performing Videos
      </p>
      <div className="space-y-3">
        {videos.map((v, i) => (
          <a
            key={i}
            href={v.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex gap-3 rounded-xl border border-border/50 bg-card/30 p-3 hover:border-rose-500/20 hover:bg-rose-500/[0.02] transition-all duration-200 group"
          >
            {/* Thumbnail */}
            <div className="shrink-0 relative w-[120px] h-[67px] rounded-lg overflow-hidden bg-muted/30">
              {v.thumbnailUrl ? (
                <Image
                  src={v.thumbnailUrl}
                  alt={v.title}
                  fill
                  className="object-cover"
                  sizes="120px"
                  unoptimized
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-muted-foreground/30 text-2xl">
                  ▶
                </div>
              )}
              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors" />
            </div>

            {/* Info */}
            <div className="flex-1 min-w-0 flex flex-col justify-between py-0.5">
              <div>
                <h3 className="text-sm font-medium line-clamp-2 leading-snug group-hover:text-rose-400 transition-colors">
                  {v.title}
                </h3>
                <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                  <span className="text-[11px] text-rose-400/80 font-medium">
                    {v.channelName}
                  </span>
                  {v.viewCount > 0 && (
                    <span className="text-[11px] text-muted-foreground/50">
                      {formatViews(v.viewCount)} views
                    </span>
                  )}
                  {v.publishedDate && (
                    <span className="text-[11px] text-muted-foreground/40">
                      {new Date(v.publishedDate).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                      })}
                    </span>
                  )}
                </div>
              </div>
              {v.performanceNote && (
                <p className="text-[11px] text-muted-foreground/50 leading-relaxed mt-1 line-clamp-1">
                  {v.performanceNote}
                </p>
              )}
            </div>

            <div className="flex flex-col items-center gap-1 shrink-0">
              <SaveToSheetButton
                payload={{
                  type: "video",
                  title: v.title,
                  channelName: v.channelName,
                  url: v.url,
                  viewCount: v.viewCount,
                  likeCount: 0,
                  publishedDate: v.publishedDate,
                  durationSeconds: null,
                }}
              />
              <ExternalLink className="w-3.5 h-3.5 text-muted-foreground/30 group-hover:text-rose-400/60 transition-colors" />
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}

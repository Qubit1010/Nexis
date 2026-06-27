import { db } from "@/lib/db";
import {
  youtubeBriefs,
  youtubeTrendingTopics,
  youtubeTopVideos,
  youtubeChannelStats,
  youtubeContentIdeas,
  youtubeSuggestedTopics,
} from "@/lib/db/schema";
import { eq, asc } from "drizzle-orm";
import { notFound } from "next/navigation";
import { ReadingProgress } from "@/components/reading-progress";
import { CollapsibleSection } from "@/components/collapsible-section";
import { YouTubeBriefHeader } from "@/components/youtube/YouTubeBriefHeader";
import { YouTubeSentimentPulse } from "@/components/youtube/YouTubeSentimentPulse";
import { YouTubeTrendingTopics } from "@/components/youtube/YouTubeTrendingTopics";
import { YouTubeTopVideos } from "@/components/youtube/YouTubeTopVideos";
import { YouTubeContentIdeas } from "@/components/youtube/YouTubeContentIdeas";
import { YouTubeSuggestedTopics } from "@/components/youtube/YouTubeSuggestedTopics";
import { YouTubeChannelGrid } from "@/components/youtube/YouTubeChannelGrid";
import { YouTubeFormatDistribution } from "@/components/youtube/YouTubeFormatDistribution";

export const dynamic = "force-dynamic";

interface YouTubePageProps {
  params: Promise<{ date: string }>;
}

export default async function YouTubePage({ params }: YouTubePageProps) {
  const { date } = await params;

  const brief = db.select().from(youtubeBriefs).where(eq(youtubeBriefs.date, date)).get();
  if (!brief) notFound();

  const topics = db
    .select()
    .from(youtubeTrendingTopics)
    .where(eq(youtubeTrendingTopics.briefId, brief.id))
    .orderBy(asc(youtubeTrendingTopics.sortOrder))
    .all()
    .map((t) => ({ ...t, channels: JSON.parse(t.channels) as string[] }));

  const videos = db
    .select()
    .from(youtubeTopVideos)
    .where(eq(youtubeTopVideos.briefId, brief.id))
    .orderBy(asc(youtubeTopVideos.sortOrder))
    .all();

  const channels = db
    .select()
    .from(youtubeChannelStats)
    .where(eq(youtubeChannelStats.briefId, brief.id))
    .orderBy(asc(youtubeChannelStats.sortOrder))
    .all();

  const ideas = db
    .select()
    .from(youtubeContentIdeas)
    .where(eq(youtubeContentIdeas.briefId, brief.id))
    .orderBy(asc(youtubeContentIdeas.sortOrder))
    .all();

  const suggested = db
    .select()
    .from(youtubeSuggestedTopics)
    .where(eq(youtubeSuggestedTopics.briefId, brief.id))
    .orderBy(asc(youtubeSuggestedTopics.sortOrder))
    .all()
    .map((s) => ({ ...s, referenceVideos: JSON.parse(s.referenceVideos) as string[] }));

  const sentiment = brief.overallSentiment
    ? (JSON.parse(brief.overallSentiment) as {
        overall: string;
        confidence: number;
        reasoning: string;
        signals: Array<{ signal: string; weight: string }>;
      })
    : null;

  const formatDist = brief.formatDistribution
    ? (JSON.parse(brief.formatDistribution) as Record<string, number>)
    : {};

  return (
    <div className="max-w-4xl mx-auto px-8 py-10">
      <ReadingProgress />

      <YouTubeBriefHeader
        date={brief.date}
        createdAt={brief.createdAt}
        videoCount={brief.videoCount ?? 0}
        channelCount={brief.channelCount ?? 0}
        analyzedAt={brief.analyzedAt}
        modelUsed={brief.modelUsed}
      />

      {sentiment && (
        <div className="mt-6">
          <YouTubeSentimentPulse sentiment={sentiment} />
        </div>
      )}

      {topics.length > 0 && (
        <div className="mt-8">
          <YouTubeTrendingTopics topics={topics} />
        </div>
      )}

      {videos.length > 0 && (
        <div className="mt-8">
          <CollapsibleSection id="yt-top-videos" label="Top Performing Videos">
            <YouTubeTopVideos videos={videos} />
          </CollapsibleSection>
        </div>
      )}

      {ideas.length > 0 && (
        <div className="mt-8">
          <CollapsibleSection id="yt-content-ideas" label="Content Opportunities">
            <YouTubeContentIdeas ideas={ideas} />
          </CollapsibleSection>
        </div>
      )}

      {suggested.length > 0 && (
        <div className="mt-8">
          <CollapsibleSection id="yt-suggested" label="Suggested Topics to Create">
            <YouTubeSuggestedTopics topics={suggested} />
          </CollapsibleSection>
        </div>
      )}

      {channels.length > 0 && (
        <div className="mt-8">
          <CollapsibleSection id="yt-channels" label="Channel Breakdown">
            <YouTubeChannelGrid stats={channels} />
          </CollapsibleSection>
        </div>
      )}

      {Object.keys(formatDist).length > 0 && (
        <div className="mt-8">
          <YouTubeFormatDistribution distribution={formatDist} />
        </div>
      )}

      <div className="mt-16 mb-8 text-center">
        <div className="h-px bg-border mb-6" />
        <p className="text-[13px] text-muted-foreground/40">
          YouTube Intelligence · AI channel analysis for content strategy
        </p>
      </div>
    </div>
  );
}

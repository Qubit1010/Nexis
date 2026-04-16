import { CheckCircle2, XCircle, Clock } from "lucide-react";
import type { PullIdeasOutput } from "@/lib/types";

interface SourceStatusProps {
  data: PullIdeasOutput | null;
}

function formatAge(dateStr: string | null): string {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (diffDays === 0) return "today";
  if (diffDays === 1) return "yesterday";
  return `${diffDays}d ago`;
}

interface BadgeProps {
  label: string;
  available: boolean;
  date?: string | null;
  count?: number;
}

function StatusBadge({ label, available, date, count }: BadgeProps) {
  const age = date ? formatAge(date) : null;
  const stale = age && !["today", "yesterday"].includes(age);

  return (
    <div
      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[13px] font-medium border transition-colors ${
        available && !stale
          ? "bg-[rgba(32,142,199,0.08)] border-[rgba(32,142,199,0.18)] text-[#6ab4d8]"
          : available && stale
          ? "bg-[rgba(255,165,0,0.07)] border-[rgba(255,165,0,0.18)] text-[#f5a623]"
          : "bg-[rgba(255,255,255,0.03)] border-[rgba(255,255,255,0.07)] text-[#444]"
      }`}
    >
      {available ? (
        stale ? (
          <Clock className="w-3 h-3 shrink-0" />
        ) : (
          <CheckCircle2 className="w-3 h-3 shrink-0" />
        )
      ) : (
        <XCircle className="w-3 h-3 shrink-0" />
      )}
      <span>{label}</span>
      {available && (
        <span className="opacity-60">
          {count !== undefined ? `${count}` : ""}
          {age ? ` · ${age}` : ""}
        </span>
      )}
    </div>
  );
}

export function SourceStatus({ data }: SourceStatusProps) {
  if (!data) return null;

  const newsCount = data.news_brief.ideas?.length ?? 0;
  const ytCount =
    (data.youtube_brief.content_opportunities?.length ?? 0) +
    (data.youtube_brief.suggested_topics?.length ?? 0);
  const savedCount = data.saved_topics.ideas?.length ?? 0;
  const articlesCount = data.saved_articles?.articles?.length ?? 0;

  return (
    <div className="flex flex-wrap gap-2 items-center">
      <StatusBadge
        label="News"
        available={data.news_brief.available}
        date={data.news_brief.date}
        count={newsCount}
      />
      <StatusBadge
        label="YouTube"
        available={data.youtube_brief.available}
        date={data.youtube_brief.analyzed_at}
        count={ytCount}
      />
      <StatusBadge
        label="Content Opportunities"
        available={data.saved_topics.available}
        count={savedCount}
      />
      <StatusBadge
        label="Saved Articles"
        available={data.saved_articles?.available ?? false}
        count={articlesCount}
      />
    </div>
  );
}

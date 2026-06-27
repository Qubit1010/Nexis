interface ChannelStat {
  channelName: string;
  channelHandle: string | null;
  videosScraped: number;
  totalViews: number;
  avgViews: number;
  mostCommonFormat: string | null;
  postingFrequency: string | null;
}

interface YouTubeChannelGridProps {
  stats: ChannelStat[];
}

function formatViews(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`;
  return String(n);
}

const FREQ_STYLES: Record<string, string> = {
  daily: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  "every-few-days": "text-amber-400 bg-amber-500/10 border-amber-500/20",
  weekly: "text-zinc-400 bg-zinc-500/10 border-zinc-500/20",
};

export function YouTubeChannelGrid({ stats }: YouTubeChannelGridProps) {
  if (!stats.length) return null;

  return (
    <div>
      <p className="text-[11px] font-semibold text-muted-foreground/60 uppercase tracking-[0.15em] mb-4">
        Channel Breakdown
      </p>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {stats.map((ch, i) => {
          const freqStyle =
            FREQ_STYLES[ch.postingFrequency || ""] || FREQ_STYLES.weekly;

          return (
            <div
              key={i}
              className="rounded-xl border border-border/50 bg-card/30 p-3.5 hover:border-rose-500/20 transition-colors"
            >
              <div className="mb-2">
                <p className="text-sm font-semibold leading-snug line-clamp-1">
                  {ch.channelName}
                </p>
                {ch.channelHandle && (
                  <p className="text-[11px] text-muted-foreground/40 mt-0.5">
                    {ch.channelHandle}
                  </p>
                )}
              </div>

              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground/50">Total views</span>
                  <span className="font-medium text-foreground/80">
                    {formatViews(ch.totalViews || 0)}
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground/50">Avg / video</span>
                  <span className="font-medium text-foreground/80">
                    {formatViews(ch.avgViews || 0)}
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground/50">Videos</span>
                  <span className="font-medium text-foreground/80">
                    {ch.videosScraped}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-1.5 mt-3 flex-wrap">
                {ch.mostCommonFormat && (
                  <span className="text-[10px] text-rose-400/80 bg-rose-500/8 border border-rose-500/15 px-2 py-0.5 rounded-full">
                    {ch.mostCommonFormat}
                  </span>
                )}
                {ch.postingFrequency && (
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded-full border ${freqStyle}`}
                  >
                    {ch.postingFrequency}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

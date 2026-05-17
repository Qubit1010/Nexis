"use client";

import { TrendingUp } from "lucide-react";
import { CardActions, mdFilename } from "./card-actions";

export interface ToolTrendItem {
  id: number;
  title: string;
  slug: string;
  summary: string;
  toolNames: string[];
  contentPotential: number | null;
}

interface ToolTrendsProps {
  trends: ToolTrendItem[];
  briefDate: string;
}

export function ToolTrends({ trends, briefDate }: ToolTrendsProps) {
  if (trends.length === 0) return null;

  return (
    <div className="space-y-3">
      {trends.map((trend, i) => (
        <div
          key={trend.id}
          className="rounded-xl border border-border/50 bg-card/40 hover:bg-card/60 transition-colors p-5 animate-fade-in"
          style={{ animationDelay: `${i * 50}ms` }}
        >
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-teal-500/10 flex items-center justify-center shrink-0">
              <TrendingUp className="w-4 h-4 text-teal-500" />
            </div>
            <div className="min-w-0 flex-1 space-y-1.5">
              <div className="flex items-start justify-between gap-2 flex-wrap">
                <div className="flex items-center gap-2 flex-wrap min-w-0">
                  <h3 className="text-base font-semibold tracking-tight">
                    {trend.title}
                  </h3>
                  {trend.contentPotential != null && (
                    <span className="text-[10px] font-semibold text-teal-500 bg-teal-500/10 border border-teal-500/20 px-2 py-0.5 rounded-full">
                      {trend.contentPotential}/10 content
                    </span>
                  )}
                </div>
                <CardActions
                  id={`trend-${trend.id}`}
                  storageKey="tools-brief-used-trends"
                  markdownFilename={mdFilename(trend.title, "trend")}
                  buildMarkdown={() =>
                    [
                      `# ${trend.title}`,
                      "",
                      `**Type:** Trend`,
                      trend.contentPotential != null
                        ? `**Content potential:** ${trend.contentPotential}/10`
                        : "",
                      "",
                      `## Summary`,
                      trend.summary,
                      "",
                      ...(trend.toolNames.length > 0
                        ? [
                            `## Tools`,
                            ...trend.toolNames.map((t) => `- ${t}`),
                            "",
                          ]
                        : []),
                    ]
                      .filter((l) => l !== "")
                      .join("\n") + "\n"
                  }
                  buildSheetPayload={() => ({
                    briefDate,
                    title: trend.title,
                    format: "trend",
                    timeliness: "trending",
                    angle: trend.summary,
                    hook: trend.summary.split(/[.!?]/)[0] + ".",
                    keyPoints: [trend.summary],
                    relatedTrends: trend.toolNames,
                  })}
                />
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {trend.summary}
              </p>
              {trend.toolNames.length > 0 && (
                <div className="flex items-center gap-1.5 flex-wrap pt-1">
                  {trend.toolNames.map((name) => (
                    <span
                      key={name}
                      className="text-[10px] font-medium text-muted-foreground/80 bg-muted/40 px-2 py-0.5 rounded"
                    >
                      {name}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

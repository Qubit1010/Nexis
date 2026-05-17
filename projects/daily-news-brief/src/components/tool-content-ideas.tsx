"use client";

import { Lightbulb } from "lucide-react";
import { CardActions, mdFilename } from "./card-actions";

export interface ToolContentIdeaItem {
  id: number;
  title: string;
  angle: string;
  format: string;
  hook: string;
  keyPoints: string[];
  relatedToolNames: string[];
}

interface ToolContentIdeasProps {
  ideas: ToolContentIdeaItem[];
  briefDate: string;
}

const FORMAT_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  tutorial: { label: "Tutorial", color: "text-cyan-400", bg: "bg-cyan-500/15" },
  carousel: { label: "Carousel", color: "text-violet-400", bg: "bg-violet-500/15" },
  reel: { label: "Reel", color: "text-pink-400", bg: "bg-pink-500/15" },
  thread: { label: "Thread", color: "text-amber-400", bg: "bg-amber-500/15" },
  blog: { label: "Blog", color: "text-emerald-400", bg: "bg-emerald-500/15" },
};

export function ToolContentIdeas({ ideas, briefDate }: ToolContentIdeasProps) {
  if (ideas.length === 0) return null;

  return (
    <div className="space-y-3">
      {ideas.map((idea, i) => {
        const fmt = FORMAT_CONFIG[idea.format] || {
          label: idea.format,
          color: "text-zinc-400",
          bg: "bg-zinc-500/10",
        };

        return (
          <div
            key={idea.id}
            className="rounded-xl border border-border/50 bg-card/40 hover:bg-card/60 transition-colors p-5 animate-fade-in"
            style={{ animationDelay: `${i * 40}ms` }}
          >
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center shrink-0">
                <Lightbulb className="w-4 h-4 text-amber-500" />
              </div>
              <div className="min-w-0 flex-1 space-y-2">
                <div className="flex items-start justify-between gap-2 flex-wrap">
                  <div className="flex items-center gap-2 flex-wrap min-w-0">
                    <h3 className="text-base font-semibold tracking-tight">
                      {idea.title}
                    </h3>
                    <span
                      className={`text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full ${fmt.bg} ${fmt.color}`}
                    >
                      {fmt.label}
                    </span>
                  </div>
                  <CardActions
                    id={`idea-${idea.id}`}
                    storageKey="tools-brief-used-ideas"
                    markdownFilename={mdFilename(idea.title, "idea")}
                    buildMarkdown={() =>
                      [
                        `# ${idea.title}`,
                        "",
                        `**Format:** ${idea.format}`,
                        "",
                        `## Angle`,
                        idea.angle,
                        "",
                        `## Hook`,
                        `> ${idea.hook}`,
                        "",
                        ...(idea.keyPoints.length > 0
                          ? [
                              `## Key Points`,
                              ...idea.keyPoints.map((p) => `- ${p}`),
                              "",
                            ]
                          : []),
                        ...(idea.relatedToolNames.length > 0
                          ? [
                              `## Related Tools`,
                              ...idea.relatedToolNames.map((t) => `- ${t}`),
                              "",
                            ]
                          : []),
                      ].join("\n")
                    }
                    buildSheetPayload={() => ({
                      briefDate,
                      title: idea.title,
                      format: idea.format,
                      timeliness: "evergreen",
                      angle: idea.angle,
                      hook: idea.hook,
                      keyPoints: idea.keyPoints,
                      relatedTrends: idea.relatedToolNames,
                    })}
                  />
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {idea.angle}
                </p>
                <div className="rounded-lg border border-amber-500/20 bg-amber-500/[0.04] px-3 py-2">
                  <p className="text-[10px] font-semibold text-amber-500/80 uppercase tracking-[0.15em] mb-1">
                    Hook
                  </p>
                  <p className="text-sm font-medium italic">&ldquo;{idea.hook}&rdquo;</p>
                </div>
                {idea.keyPoints.length > 0 && (
                  <ul className="space-y-1 pl-1">
                    {idea.keyPoints.map((p, k) => (
                      <li key={k} className="text-sm leading-relaxed flex gap-2">
                        <span className="text-teal-500/60 mt-0.5">·</span>
                        <span>{p}</span>
                      </li>
                    ))}
                  </ul>
                )}
                {idea.relatedToolNames.length > 0 && (
                  <div className="flex items-center gap-1.5 flex-wrap pt-1">
                    <span className="text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider">
                      Tools:
                    </span>
                    {idea.relatedToolNames.map((name) => (
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
        );
      })}
    </div>
  );
}

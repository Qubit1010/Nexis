"use client";

import { ExternalLink } from "lucide-react";
import { CardActions, mdFilename } from "./card-actions";

export interface ToolItem {
  id: number;
  name: string;
  url: string;
  source: string;
  oneLiner: string;
  bestUseCase: string;
  howToSteps: string[];
  audienceHook: string;
  pricingTier: string | null;
  tags: string[];
  upvotes: number | null;
  relevanceScore: number | null;
}

interface ToolCardProps {
  tool: ToolItem;
  domainName: string;
  domainSlug: string;
  briefDate: string;
  index?: number;
}

const PRICING_STYLES: Record<string, string> = {
  free: "bg-emerald-500/15 text-emerald-400 border-emerald-500/25",
  freemium: "bg-cyan-500/15 text-cyan-400 border-cyan-500/25",
  paid: "bg-amber-500/15 text-amber-400 border-amber-500/25",
  unknown: "bg-zinc-500/10 text-zinc-400 border-zinc-500/20",
};

export function ToolCard({
  tool,
  domainName,
  domainSlug,
  briefDate,
  index = 0,
}: ToolCardProps) {
  const pricingClass = PRICING_STYLES[tool.pricingTier || "unknown"] || PRICING_STYLES.unknown;
  const delay = `${Math.min(index * 40, 280)}ms`;

  return (
    <div
      className="group rounded-xl border border-border/50 bg-card/40 hover:bg-card/60 hover:border-border transition-all duration-200 p-5 sm:p-6 animate-fade-in"
      style={{ animationDelay: delay }}
    >
      {/* Header: name + pricing badge */}
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <h3 className="text-lg font-bold tracking-tight">{tool.name}</h3>
            {tool.pricingTier && (
              <span
                className={`text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full border ${pricingClass}`}
              >
                {tool.pricingTier}
              </span>
            )}
            {tool.upvotes != null && tool.upvotes > 0 && (
              <span className="text-[11px] text-muted-foreground/60">
                {tool.upvotes} upvotes
              </span>
            )}
          </div>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {tool.oneLiner}
          </p>
        </div>
        <div className="flex items-center gap-1 shrink-0">
          <CardActions
            id={`tool-${tool.id}`}
            storageKey="tools-brief-used-tools"
            markdownFilename={mdFilename(tool.name, "tool")}
            buildMarkdown={() =>
              [
                `# ${tool.name}`,
                "",
                `**Domain:** ${domainName}`,
                tool.pricingTier ? `**Pricing:** ${tool.pricingTier}` : "",
                tool.url ? `**URL:** ${tool.url}` : "",
                "",
                `## One-liner`,
                tool.oneLiner,
                "",
                `## Best use case`,
                tool.bestUseCase,
                "",
                ...(tool.howToSteps.length > 0
                  ? [
                      `## How to use it`,
                      ...tool.howToSteps.map((s, i) => `${i + 1}. ${s}`),
                      "",
                    ]
                  : []),
                tool.audienceHook ? `## Audience hook\n> ${tool.audienceHook}` : "",
                "",
                ...(tool.tags.length > 0
                  ? [`**Tags:** ${tool.tags.join(", ")}`, ""]
                  : []),
              ]
                .filter((l) => l !== "")
                .join("\n") + "\n"
            }
            buildSheetPayload={() => ({
              briefDate,
              title: tool.name,
              format: "tool",
              timeliness: "evergreen",
              angle: tool.oneLiner,
              hook: tool.audienceHook || tool.bestUseCase,
              keyPoints: [tool.bestUseCase, ...tool.howToSteps],
              relatedTrends: [domainName, ...tool.tags],
            })}
          />
          <a
            href={tool.url}
            target="_blank"
            rel="noopener noreferrer"
            className="w-7 h-7 rounded-md flex items-center justify-center text-muted-foreground/40 hover:text-foreground hover:bg-accent/60 transition-all duration-200"
            title="Visit tool"
          >
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>

      {/* Best use case */}
      <div className="mt-4">
        <p className="text-[10px] font-semibold text-teal-500/80 uppercase tracking-[0.15em] mb-1.5">
          Best Use Case
        </p>
        <p className="text-sm leading-relaxed">{tool.bestUseCase}</p>
      </div>

      {/* How to use */}
      {tool.howToSteps?.length > 0 && (
        <div className="mt-4">
          <p className="text-[10px] font-semibold text-teal-500/80 uppercase tracking-[0.15em] mb-2">
            How To Use It
          </p>
          <ol className="space-y-1.5">
            {tool.howToSteps.map((step, i) => (
              <li key={i} className="text-sm leading-relaxed flex gap-2.5">
                <span className="shrink-0 w-5 h-5 rounded-full bg-teal-500/10 text-teal-500 text-[11px] font-bold flex items-center justify-center mt-0.5">
                  {i + 1}
                </span>
                <span className="min-w-0">{step}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* Audience hook */}
      {tool.audienceHook && (
        <div className="mt-4 rounded-lg border border-amber-500/20 bg-amber-500/[0.04] px-3.5 py-2.5">
          <p className="text-[10px] font-semibold text-amber-500/80 uppercase tracking-[0.15em] mb-1">
            Audience Hook
          </p>
          <p className="text-sm font-medium leading-snug italic">
            &ldquo;{tool.audienceHook}&rdquo;
          </p>
        </div>
      )}

      {/* Tags */}
      <div className="mt-4 flex items-center gap-1.5 flex-wrap">
        {tool.tags?.map((tag) => (
          <span
            key={tag}
            className="text-[10px] font-medium text-muted-foreground/70 bg-muted/40 px-2 py-0.5 rounded"
          >
            {tag}
          </span>
        ))}
        <span className="text-[10px] text-muted-foreground/50">
          via {tool.source}
        </span>
      </div>
    </div>
  );
}

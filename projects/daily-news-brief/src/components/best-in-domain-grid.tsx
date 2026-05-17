"use client";

import { Crown, ExternalLink } from "lucide-react";
import { CardActions, mdFilename } from "./card-actions";

export interface DomainWinner {
  domainName: string;
  domainSlug: string;
  toolName: string;
  toolUrl: string;
  oneLiner: string;
  bestUseCase: string;
  reason: string;
  pricingTier: string | null;
}

interface BestInDomainGridProps {
  winners: DomainWinner[];
  briefDate: string;
}

const DOMAIN_LABELS: Record<string, string> = {
  "content-creation": "Best for Content",
  "outreach-sales": "Best for Outreach",
  "automation-workflows": "Best Agent / Automation",
  "productivity-ops": "Best for Productivity",
};

const PRICING_STYLES: Record<string, string> = {
  free: "bg-emerald-500/15 text-emerald-400 border-emerald-500/25",
  freemium: "bg-cyan-500/15 text-cyan-400 border-cyan-500/25",
  paid: "bg-amber-500/15 text-amber-400 border-amber-500/25",
  unknown: "bg-zinc-500/10 text-zinc-400 border-zinc-500/20",
};

export function BestInDomainGrid({ winners, briefDate }: BestInDomainGridProps) {
  if (winners.length === 0) return null;

  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {winners.map((w, i) => {
        const label = DOMAIN_LABELS[w.domainSlug] || `Best for ${w.domainName}`;
        const pricingClass =
          PRICING_STYLES[w.pricingTier || "unknown"] || PRICING_STYLES.unknown;

        return (
          <div
            key={w.domainSlug}
            className="group relative block rounded-xl border border-teal-500/25 bg-gradient-to-br from-teal-500/[0.06] to-transparent hover:border-teal-500/50 hover:bg-teal-500/[0.08] transition-all duration-200 p-5 animate-fade-in"
            style={{ animationDelay: `${i * 60}ms` }}
          >
            <div className="flex items-start justify-between gap-2 mb-2">
              <a
                href={`#${w.domainSlug}`}
                className="flex items-center gap-2 min-w-0"
              >
                <Crown className="w-3.5 h-3.5 text-teal-400 shrink-0" />
                <span className="text-[10px] font-bold uppercase tracking-[0.15em] text-teal-400/90">
                  {label}
                </span>
              </a>
              <div className="flex items-center gap-2 shrink-0">
                {w.pricingTier && (
                  <span
                    className={`text-[9px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded-full border ${pricingClass}`}
                  >
                    {w.pricingTier}
                  </span>
                )}
                <CardActions
                  id={`winner-${w.domainSlug}`}
                  storageKey="tools-brief-used-winners"
                  markdownFilename={mdFilename(w.toolName, w.domainSlug)}
                  buildMarkdown={() =>
                    [
                      `# ${w.toolName}`,
                      "",
                      `**${label}** — ${w.domainName}`,
                      w.pricingTier ? `**Pricing:** ${w.pricingTier}` : "",
                      "",
                      `## One-liner`,
                      w.oneLiner,
                      "",
                      `## Best use case`,
                      w.bestUseCase,
                      "",
                      `## Why it wins`,
                      w.reason,
                      "",
                      `[Visit tool](${w.toolUrl})`,
                      "",
                    ]
                      .filter((l) => l !== "")
                      .join("\n") + "\n"
                  }
                  buildSheetPayload={() => ({
                    briefDate,
                    title: `${label}: ${w.toolName}`,
                    format: "tool",
                    timeliness: "evergreen",
                    angle: w.oneLiner,
                    hook: w.reason,
                    keyPoints: [w.bestUseCase, `URL: ${w.toolUrl}`],
                    relatedTrends: [w.domainName],
                  })}
                />
              </div>
            </div>
            <a
              href={w.toolUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 mb-1.5"
            >
              <h3 className="text-lg font-bold tracking-tight">{w.toolName}</h3>
              <ExternalLink className="w-3 h-3 text-muted-foreground/40 group-hover:text-muted-foreground transition-colors" />
            </a>
            <p className="text-sm text-muted-foreground leading-snug mb-2">
              {w.oneLiner}
            </p>
            <p className="text-xs leading-relaxed text-foreground/80 italic">
              {w.reason}
            </p>
          </div>
        );
      })}
    </div>
  );
}

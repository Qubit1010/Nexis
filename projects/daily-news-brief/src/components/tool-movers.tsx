import { TrendingUp, Github, Sparkles } from "lucide-react";

export interface Mover {
  name: string;
  url: string;
  signal: string;
  source: "github" | "openrouter";
  blurb?: string;
}

export function ToolMovers({ movers }: { movers: Mover[] }) {
  if (!movers || movers.length === 0) return null;

  return (
    <div className="rounded-xl border border-border/50 bg-card/30 p-5 animate-fade-in">
      <p className="text-[11px] font-semibold text-muted-foreground/60 uppercase tracking-[0.15em] mb-4 inline-flex items-center gap-2">
        <TrendingUp className="w-3.5 h-3.5 text-teal-500" />
        What&apos;s Surging
      </p>
      <div className="grid sm:grid-cols-2 gap-2.5">
        {movers.map((m, i) => (
          <a
            key={`${m.name}-${i}`}
            href={m.url}
            target="_blank"
            rel="noopener noreferrer"
            className="group flex items-start gap-2.5 rounded-lg border border-border/40 bg-background/40 p-3 hover:border-teal-500/40 hover:bg-teal-500/[0.04] transition-all duration-200"
          >
            <div className="w-7 h-7 rounded-md bg-teal-500/10 flex items-center justify-center shrink-0 mt-0.5">
              {m.source === "github" ? (
                <Github className="w-3.5 h-3.5 text-teal-500/80" />
              ) : (
                <Sparkles className="w-3.5 h-3.5 text-teal-500/80" />
              )}
            </div>
            <div className="min-w-0">
              <div className="flex items-baseline gap-2">
                <span className="text-sm font-semibold truncate group-hover:text-teal-500 transition-colors">
                  {m.name}
                </span>
                <span className="text-[11px] text-teal-500/80 shrink-0">{m.signal}</span>
              </div>
              {m.blurb && (
                <p className="text-[12px] text-muted-foreground/70 leading-snug line-clamp-2 mt-0.5">
                  {m.blurb}
                </p>
              )}
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}

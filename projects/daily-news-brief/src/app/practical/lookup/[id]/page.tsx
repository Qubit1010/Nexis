import { db } from "@/lib/db";
import { practicalLookups } from "@/lib/db/schema";
import { eq } from "drizzle-orm";
import { notFound } from "next/navigation";
import { ReadingProgress } from "@/components/reading-progress";
import { Sparkles, ExternalLink, Wrench } from "lucide-react";

export const dynamic = "force-dynamic";

interface PageProps {
  params: Promise<{ id: string }>;
}

interface WhatsNew {
  title: string;
  detail: string;
  url: string;
}
interface HowSolve {
  problem: string;
  approach: string;
  tools: string[];
  steps: string[];
}
interface Source {
  title: string;
  url: string;
  source: string;
}

export default async function LookupPage({ params }: PageProps) {
  const { id } = await params;
  const row = db
    .select()
    .from(practicalLookups)
    .where(eq(practicalLookups.id, Number(id)))
    .get();
  if (!row) notFound();

  const whatsNew = JSON.parse(row.whatsNew) as WhatsNew[];
  const howPeopleSolve = JSON.parse(row.howPeopleSolve) as HowSolve[];
  const sources = JSON.parse(row.sources) as Source[];

  return (
    <div className="max-w-4xl mx-auto px-8 py-10">
      <ReadingProgress />

      <div className="relative rounded-xl bg-gradient-to-r from-[var(--background)] to-[var(--navy-light)] border border-border/50 p-6 sm:p-8 animate-fade-in overflow-hidden">
        <div className="absolute top-0 right-0 w-48 h-48 bg-teal-500/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4 pointer-events-none" />
        <div className="relative space-y-3">
          <p className="text-xs font-semibold text-teal-500 uppercase tracking-[0.15em] inline-flex items-center gap-2">
            <Wrench className="w-3.5 h-3.5" />
            Practical AI Lookup
          </p>
          <h1 className="text-2xl sm:text-4xl font-bold tracking-tight">{row.tool}</h1>
          <div className="flex items-center gap-2.5 flex-wrap">
            <span className="inline-flex items-center gap-1.5 text-xs font-medium text-teal-500 bg-teal-500/10 border border-teal-500/20 px-3 py-1.5 rounded-full">
              last {row.days} days
            </span>
            <span className="text-xs text-muted-foreground/50">
              {new Date(row.createdAt).toLocaleString("en-US", {
                month: "short",
                day: "numeric",
                hour: "numeric",
                minute: "2-digit",
              })}
            </span>
            {row.notebookUrl && (
              <a
                href={row.notebookUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-xs font-medium text-violet-400 bg-violet-500/10 border border-violet-500/20 px-3 py-1.5 rounded-full hover:bg-violet-500/20 transition-colors"
              >
                <Sparkles className="w-3 h-3" />
                Grounded via NotebookLM
                <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>
          <p className="text-sm sm:text-base text-muted-foreground leading-relaxed max-w-2xl pt-1">
            {row.summary}
          </p>
        </div>
      </div>

      {whatsNew.length > 0 && (
        <div className="mt-8">
          <p className="text-[11px] font-semibold text-muted-foreground/60 uppercase tracking-[0.15em] mb-3">
            What&apos;s New
          </p>
          <div className="space-y-2.5">
            {whatsNew.map((w, i) => (
              <a
                key={i}
                href={w.url}
                target="_blank"
                rel="noopener noreferrer"
                className="group block rounded-xl border border-border/40 bg-card/30 p-4 hover:border-teal-500/40 hover:bg-teal-500/[0.03] transition-all duration-200"
              >
                <div className="flex items-start justify-between gap-3">
                  <h3 className="text-sm font-semibold group-hover:text-teal-500 transition-colors">
                    {w.title}
                  </h3>
                  <ExternalLink className="w-3.5 h-3.5 text-muted-foreground/40 shrink-0 mt-0.5" />
                </div>
                <p className="text-[13px] text-muted-foreground/80 leading-relaxed mt-1">
                  {w.detail}
                </p>
              </a>
            ))}
          </div>
        </div>
      )}

      {howPeopleSolve.length > 0 && (
        <div className="mt-8">
          <p className="text-[11px] font-semibold text-muted-foreground/60 uppercase tracking-[0.15em] mb-3 inline-flex items-center gap-2">
            <Sparkles className="w-3.5 h-3.5 text-amber-500" />
            How People Solve Problems With It
          </p>
          <div className="space-y-3">
            {howPeopleSolve.map((h, i) => (
              <div key={i} className="rounded-xl border border-border/50 bg-card/30 p-5">
                <h3 className="text-base font-bold tracking-tight">{h.problem}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed mt-1.5">
                  {h.approach}
                </p>
                {h.tools?.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-3">
                    {h.tools.map((t, j) => (
                      <span
                        key={j}
                        className="text-[11px] font-medium text-teal-500 bg-teal-500/10 border border-teal-500/20 px-2.5 py-1 rounded-full"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                )}
                {h.steps?.length > 0 && (
                  <ol className="mt-3 space-y-1.5">
                    {h.steps.map((s, j) => (
                      <li key={j} className="flex gap-2.5 text-[13px] leading-relaxed">
                        <span className="w-5 h-5 rounded-md bg-amber-500/15 text-amber-500 text-[11px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                          {j + 1}
                        </span>
                        <span className="font-mono text-muted-foreground">{s}</span>
                      </li>
                    ))}
                  </ol>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {sources.length > 0 && (
        <div className="mt-8">
          <p className="text-[11px] font-semibold text-muted-foreground/60 uppercase tracking-[0.15em] mb-3">
            Sources
          </p>
          <div className="flex flex-wrap gap-2">
            {sources.map((s, i) => (
              <a
                key={i}
                href={s.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[12px] text-muted-foreground/70 hover:text-teal-500 border border-border/40 rounded-full px-3 py-1.5 transition-colors"
              >
                {s.title.slice(0, 60)} · {s.source}
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

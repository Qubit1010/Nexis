import { ToolCard, type ToolItem } from "./tool-card";

interface ToolsCategorySectionProps {
  name: string;
  slug: string;
  summary: string;
  tools: ToolItem[];
  briefDate: string;
}

export function ToolsCategorySection({
  name,
  slug,
  summary,
  tools,
  briefDate,
}: ToolsCategorySectionProps) {
  return (
    <section id={slug} className="scroll-mt-8">
      <div className="mb-5">
        <div className="flex items-baseline justify-between gap-3 mb-2">
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight">{name}</h2>
          <span className="text-xs text-muted-foreground/60 shrink-0">
            {tools.length} tool{tools.length === 1 ? "" : "s"}
          </span>
        </div>
        <p className="text-sm text-muted-foreground leading-relaxed">{summary}</p>
      </div>

      {tools.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border/40 px-6 py-10 text-center">
          <p className="text-sm text-muted-foreground/60">
            No new tools in this domain today. Check back tomorrow.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {tools.map((tool, i) => (
            <ToolCard
              key={tool.id}
              tool={tool}
              domainName={name}
              domainSlug={slug}
              briefDate={briefDate}
              index={i}
            />
          ))}
        </div>
      )}
    </section>
  );
}

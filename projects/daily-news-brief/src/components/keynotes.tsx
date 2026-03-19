interface CategoryData {
  name: string;
  slug: string;
  insight: string;
  articleCount: number;
}

interface KeynotesProps {
  categories: CategoryData[];
  date: string;
}

const KEYNOTE_COLORS = [
  { bg: "from-blue-500/15 to-blue-600/5", border: "border-blue-500/25", dot: "bg-blue-400" },
  { bg: "from-cyan-500/15 to-cyan-600/5", border: "border-cyan-500/25", dot: "bg-cyan-400" },
  { bg: "from-violet-500/15 to-violet-600/5", border: "border-violet-500/25", dot: "bg-violet-400" },
  { bg: "from-amber-500/15 to-amber-600/5", border: "border-amber-500/25", dot: "bg-amber-400" },
  { bg: "from-emerald-500/15 to-emerald-600/5", border: "border-emerald-500/25", dot: "bg-emerald-400" },
  { bg: "from-rose-500/15 to-rose-600/5", border: "border-rose-500/25", dot: "bg-rose-400" },
  { bg: "from-orange-500/15 to-orange-600/5", border: "border-orange-500/25", dot: "bg-orange-400" },
];

export function Keynotes({ categories, date }: KeynotesProps) {
  if (categories.length === 0) return null;

  // Pick top 3 categories as keynotes
  const keynotes = categories.slice(0, 3);
  const totalArticles = categories.reduce((s, c) => s + c.articleCount, 0);

  return (
    <div className="animate-slide-up mb-10">
      {/* Keynotes header */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/25 to-primary/10 flex items-center justify-center">
            <span className="text-primary text-lg font-bold">K</span>
          </div>
          <div>
            <h2 className="text-lg font-bold tracking-tight">
              Today's Keynotes
            </h2>
            <p className="text-[13px] text-muted-foreground">
              Top insights across {categories.length} categories &middot; {totalArticles} articles
            </p>
          </div>
        </div>
      </div>

      {/* Keynote cards grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {keynotes.map((cat, i) => {
          const color = KEYNOTE_COLORS[i % KEYNOTE_COLORS.length];
          return (
            <a
              key={cat.slug}
              href={`#${cat.slug}`}
              className={`group relative rounded-xl border ${color.border} bg-gradient-to-br ${color.bg} p-5 transition-all duration-300 hover:scale-[1.02] hover:shadow-lg cursor-pointer animate-slide-up`}
              style={{ animationDelay: `${i * 0.1}s` }}
            >
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <span className={`w-2 h-2 rounded-full ${color.dot}`} />
                  <span className="text-[11px] font-semibold uppercase tracking-[0.1em] text-muted-foreground">
                    {cat.name}
                  </span>
                </div>
                <p className="text-[14px] leading-relaxed text-foreground/85 line-clamp-4">
                  {cat.insight}
                </p>
                <div className="mt-3 flex items-center gap-1.5 text-[12px] text-muted-foreground/60 group-hover:text-primary/60 transition-colors">
                  <span>{cat.articleCount} articles</span>
                  <span className="opacity-0 group-hover:opacity-100 transition-opacity">&#8594;</span>
                </div>
              </div>
            </a>
          );
        })}
      </div>

      {/* Quick stats bar */}
      <div className="mt-5 flex items-center gap-6 px-1">
        {categories.slice(3).map((cat, i) => {
          const color = KEYNOTE_COLORS[(i + 3) % KEYNOTE_COLORS.length];
          return (
            <a
              key={cat.slug}
              href={`#${cat.slug}`}
              className="flex items-center gap-2 text-[13px] text-muted-foreground hover:text-foreground transition-colors duration-200"
            >
              <span className={`w-1.5 h-1.5 rounded-full ${color.dot}`} />
              <span>{cat.name}</span>
              <span className="text-muted-foreground/40">({cat.articleCount})</span>
            </a>
          );
        })}
      </div>
    </div>
  );
}

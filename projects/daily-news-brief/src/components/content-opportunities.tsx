"use client";

import { useState, useEffect, useCallback } from "react";

interface ContentIdea {
  id: number;
  title: string;
  angle: string;
  format: string;
  hook: string;
  keyPoints: string[];
  timeliness: string;
  relatedTrendSlugs: string[];
}

interface ContentOpportunitiesProps {
  ideas: ContentIdea[];
  briefDate: string;
}

const FORMAT_TABS = [
  { key: "all", label: "All" },
  { key: "thread", label: "Thread" },
  { key: "blog", label: "Blog" },
  { key: "newsletter", label: "Newsletter" },
] as const;

const FORMAT_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  thread: { label: "Thread", color: "text-cyan-400", bg: "bg-cyan-500/15" },
  blog: { label: "Blog Post", color: "text-violet-400", bg: "bg-violet-500/15" },
  newsletter: { label: "Newsletter", color: "text-amber-400", bg: "bg-amber-500/15" },
};

const TIMELINESS_CONFIG: Record<
  string,
  { label: string; color: string; bg: string; dotColor: string }
> = {
  breaking: {
    label: "Breaking",
    color: "text-red-400",
    bg: "bg-red-500/15",
    dotColor: "bg-red-400",
  },
  trending: {
    label: "Trending",
    color: "text-amber-400",
    bg: "bg-amber-500/15",
    dotColor: "bg-amber-400",
  },
  evergreen: {
    label: "Evergreen",
    color: "text-teal-400",
    bg: "bg-teal-500/15",
    dotColor: "bg-teal-400",
  },
};

const USED_STORAGE_KEY = "intel-brief-used-ideas";

function loadUsedIds(): Set<number> {
  if (typeof window === "undefined") return new Set();
  try {
    const raw = localStorage.getItem(USED_STORAGE_KEY);
    return raw ? new Set(JSON.parse(raw)) : new Set();
  } catch {
    return new Set();
  }
}

function saveUsedIds(ids: Set<number>) {
  localStorage.setItem(USED_STORAGE_KEY, JSON.stringify([...ids]));
}

function ClipboardIcon() {
  return (
    <svg
      width="13"
      height="13"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </svg>
  );
}

export function ContentOpportunities({ ideas, briefDate }: ContentOpportunitiesProps) {
  const [activeTab, setActiveTab] = useState<string>("all");
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [usedIds, setUsedIds] = useState<Set<number>>(new Set());
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [savingId, setSavingId] = useState<number | null>(null);
  const [savedIds, setSavedIds] = useState<Set<number>>(new Set());

  useEffect(() => {
    setUsedIds(loadUsedIds());
  }, []);

  const toggleUsed = useCallback((id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setUsedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      saveUsedIds(next);
      return next;
    });
  }, []);

  const copyText = useCallback((text: string, field: string, e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 1500);
  }, []);

  const exportMarkdown = useCallback((idea: ContentIdea, e: React.MouseEvent) => {
    e.stopPropagation();
    const md = [
      `# ${idea.title}`,
      "",
      `**Format:** ${idea.format}`,
      `**Timeliness:** ${idea.timeliness}`,
      "",
      `## Angle`,
      idea.angle,
      "",
      `## Hook`,
      `> ${idea.hook}`,
      "",
      `## Key Points`,
      ...idea.keyPoints.map((p) => `- ${p}`),
      "",
    ].join("\n");

    const blob = new Blob([md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${idea.title.toLowerCase().replace(/[^a-z0-9]+/g, "-").slice(0, 50)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }, []);

  const saveToSheet = useCallback(
    async (idea: ContentIdea, e: React.MouseEvent) => {
      e.stopPropagation();
      if (savedIds.has(idea.id)) return;
      setSavingId(idea.id);
      try {
        const res = await fetch("/api/sheets", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            briefDate,
            title: idea.title,
            format: idea.format,
            timeliness: idea.timeliness,
            angle: idea.angle,
            hook: idea.hook,
            keyPoints: idea.keyPoints,
            relatedTrends: idea.relatedTrendSlugs,
          }),
        });
        if (!res.ok) throw new Error("Failed to save");
        setSavedIds((prev) => new Set(prev).add(idea.id));
      } catch (err) {
        console.error("Failed to save to sheet:", err);
        alert("Failed to save to Google Sheet. Check console for details.");
      } finally {
        setSavingId(null);
      }
    },
    [briefDate, savedIds]
  );

  if (ideas.length === 0) return null;

  const filteredIdeas =
    activeTab === "all" ? ideas : ideas.filter((i) => i.format === activeTab);
  const usedCount = ideas.filter((i) => usedIds.has(i.id)).length;

  return (
    <div className="animate-slide-up">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500/25 to-violet-600/10 flex items-center justify-center">
            <span className="text-violet-400 text-lg font-bold">!</span>
          </div>
          <div>
            <h2 className="text-lg font-bold tracking-tight">Content Opportunities</h2>
            <p className="text-[13px] text-muted-foreground">
              Actionable content ideas based on today&apos;s trends
            </p>
          </div>
        </div>
        {usedCount > 0 && (
          <span className="text-[12px] text-emerald-400/70 bg-emerald-400/10 px-2.5 py-1 rounded-full">
            {usedCount}/{ideas.length} used
          </span>
        )}
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 mb-5 p-1 rounded-lg bg-muted/30 w-fit">
        {FORMAT_TABS.map((tab) => {
          const count =
            tab.key === "all"
              ? ideas.length
              : ideas.filter((i) => i.format === tab.key).length;
          if (tab.key !== "all" && count === 0) return null;
          const isActive = activeTab === tab.key;

          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-3 py-1.5 rounded-md text-[12px] font-semibold transition-all duration-200 ${
                isActive
                  ? "bg-card text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {tab.label}
              <span className="ml-1.5 text-[10px] opacity-60">{count}</span>
            </button>
          );
        })}
      </div>

      {/* Cards */}
      <div className="space-y-3">
        {filteredIdeas.map((idea, i) => {
          const format = FORMAT_CONFIG[idea.format] || FORMAT_CONFIG.blog;
          const timeliness =
            TIMELINESS_CONFIG[idea.timeliness] || TIMELINESS_CONFIG.trending;
          const isExpanded = expandedId === idea.id;
          const isUsed = usedIds.has(idea.id);

          return (
            <div
              key={idea.id}
              className={`group rounded-xl border transition-all duration-300 hover:border-amber-500/20 hover:shadow-[0_0_20px_rgba(245,158,11,0.06)] animate-slide-up cursor-pointer ${
                isUsed
                  ? "border-emerald-500/20 bg-emerald-500/[0.03]"
                  : "border-border/60"
              }`}
              style={{ animationDelay: `${i * 0.06}s`, animationFillMode: "both" }}
              onClick={() => setExpandedId(isExpanded ? null : idea.id)}
            >
              <div className="p-5">
                {/* Badges row */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${format.bg} ${format.color}`}
                    >
                      {format.label}
                    </span>
                    <span
                      className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full ${timeliness.bg} ${timeliness.color}`}
                    >
                      <span className={`w-1.5 h-1.5 rounded-full ${timeliness.dotColor}`} />
                      {timeliness.label}
                    </span>
                    {isUsed && (
                      <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400">
                        Used
                      </span>
                    )}
                  </div>
                  {/* Action buttons */}
                  <div className="flex items-center gap-1">
                    <button
                      onClick={(e) => toggleUsed(idea.id, e)}
                      className={`w-7 h-7 rounded-md flex items-center justify-center transition-all duration-200 ${
                        isUsed
                          ? "text-emerald-400 hover:text-emerald-300"
                          : "text-muted-foreground/40 hover:text-foreground hover:bg-accent/60"
                      }`}
                      title={isUsed ? "Mark as unused" : "Mark as used"}
                    >
                      <svg
                        width="14"
                        height="14"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                    </button>
                    <button
                      onClick={(e) => exportMarkdown(idea, e)}
                      className="w-7 h-7 rounded-md flex items-center justify-center text-muted-foreground/40 hover:text-foreground hover:bg-accent/60 transition-all duration-200"
                      title="Export as Markdown"
                    >
                      <svg
                        width="14"
                        height="14"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                        <polyline points="7 10 12 15 17 10" />
                        <line x1="12" y1="15" x2="12" y2="3" />
                      </svg>
                    </button>
                    <button
                      onClick={(e) => saveToSheet(idea, e)}
                      disabled={savingId === idea.id || savedIds.has(idea.id)}
                      className={`w-7 h-7 rounded-md flex items-center justify-center transition-all duration-200 ${
                        savedIds.has(idea.id)
                          ? "text-green-400"
                          : savingId === idea.id
                            ? "text-muted-foreground/40 animate-pulse"
                            : "text-muted-foreground/40 hover:text-foreground hover:bg-accent/60"
                      }`}
                      title={savedIds.has(idea.id) ? "Saved to Google Sheet" : "Save to Google Sheet"}
                    >
                      <svg
                        width="14"
                        height="14"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                        <rect x="7" y="7" width="4" height="4" />
                        <line x1="15" y1="7" x2="19" y2="7" />
                        <line x1="15" y1="11" x2="19" y2="11" />
                        <line x1="7" y1="15" x2="19" y2="15" />
                        <line x1="7" y1="19" x2="19" y2="19" />
                      </svg>
                    </button>
                  </div>
                </div>

                {/* Title */}
                <h3 className="font-semibold text-[15px] leading-snug mb-1.5">
                  {idea.title}
                </h3>

                {/* Angle */}
                <p className="text-[13px] text-muted-foreground leading-relaxed">
                  {idea.angle}
                </p>

                {/* Hook (always visible, copyable) */}
                <div className="mt-3 p-3 rounded-lg bg-muted/20 border border-border/30">
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-[10px] font-semibold text-amber-400/70 uppercase tracking-[0.1em]">
                      Hook
                    </p>
                    <button
                      onClick={(e) => copyText(idea.hook, `hook-${idea.id}`, e)}
                      className="flex items-center gap-1 text-[11px] text-muted-foreground/50 hover:text-amber-400 transition-colors"
                    >
                      <ClipboardIcon />
                      {copiedField === `hook-${idea.id}` ? "Copied!" : "Copy"}
                    </button>
                  </div>
                  <p className="text-[13px] text-foreground/85 italic leading-relaxed">
                    &ldquo;{idea.hook}&rdquo;
                  </p>
                </div>

                {/* Expandable key points */}
                {isExpanded && (
                  <div className="mt-4 pt-4 border-t border-border/30 animate-fade-in">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-[10px] font-semibold text-amber-400/70 uppercase tracking-[0.1em]">
                        Key Points
                      </p>
                      <button
                        onClick={(e) =>
                          copyText(
                            idea.keyPoints.map((p) => `- ${p}`).join("\n"),
                            `points-${idea.id}`,
                            e
                          )
                        }
                        className="flex items-center gap-1 text-[11px] text-muted-foreground/50 hover:text-amber-400 transition-colors"
                      >
                        <ClipboardIcon />
                        {copiedField === `points-${idea.id}` ? "Copied!" : "Copy"}
                      </button>
                    </div>
                    <ul className="space-y-1.5">
                      {idea.keyPoints.map((point, j) => (
                        <li
                          key={j}
                          className="text-[13px] text-muted-foreground flex items-start gap-2"
                        >
                          <span className="text-amber-500/50 mt-0.5 shrink-0">
                            &bull;
                          </span>
                          {point}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Expand hint */}
                <div className="flex items-center gap-1.5 mt-3 text-[11px] text-muted-foreground/40">
                  <svg
                    width="12"
                    height="12"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className={`transition-transform duration-200 ${isExpanded ? "rotate-180" : ""}`}
                  >
                    <polyline points="6 9 12 15 18 9" />
                  </svg>
                  <span>{isExpanded ? "Collapse" : "Expand key points"}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

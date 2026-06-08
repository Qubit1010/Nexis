"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Search, Loader2, Wand2, Link, FileText } from "lucide-react";
import { ResearchPanel } from "@/components/research-panel";
import { ContentOutput } from "@/components/content-output";
import { LogPostModal } from "@/components/log-post-modal";
import type { ContentMode, PillarKey, NLMSource, NotebookLMSourcesOutput, NotebookLMAskOutput } from "@/lib/types";

type Platform = "LinkedIn" | "Instagram" | "Blog";
type FormatMap = Record<Platform, string[]>;
type ResearchPhase = "idle" | "fetching-sources" | "selecting" | "fetching-response" | "response";
type ResearchDepth = "light" | "medium" | "deep";

const PLATFORMS: Platform[] = ["LinkedIn", "Instagram", "Blog"];

const FORMATS: FormatMap = {
  LinkedIn: ["Text Post", "Carousel", "Article", "Newsletter"],
  Instagram: ["Carousel", "Reel", "Short Video", "Caption"],
  Blog: ["Article", "Tutorial", "Opinion"],
};

const CONTENT_MODES: { key: ContentMode; label: string; description: string }[] = [
  { key: "news", label: "News / Analysis", description: "Data-first, low personalization" },
  { key: "opinion", label: "Opinion / POV", description: "Strong personal take" },
  { key: "story", label: "Personal Story", description: "Narrative-driven, identity-heavy" },
  { key: "tutorial", label: "Tutorial / How-to", description: "Practical, step-by-step" },
];

const PILLARS: { key: PillarKey; label: string }[] = [
  { key: "lived_experience", label: "Lived Exp." },
  { key: "strong_pov", label: "Strong POV" },
  { key: "cross_domain", label: "Cross-domain" },
  { key: "taste_judgment", label: "Taste & Judgment" },
  { key: "identity_voice", label: "Identity" },
  { key: "practical_stakes", label: "Practical Stakes" },
  { key: "content_specific", label: "Content Specific" },
];

const MODE_DEFAULTS: Record<ContentMode, PillarKey[]> = {
  news: ["practical_stakes", "content_specific"],
  opinion: ["strong_pov", "taste_judgment"],
  story: ["lived_experience", "identity_voice"],
  tutorial: ["practical_stakes", "cross_domain"],
};

function CreatePageInner() {
  const params = useSearchParams();

  const [platform, setPlatform] = useState<Platform>(
    (params.get("platform") as Platform) || "LinkedIn"
  );
  const [format, setFormat] = useState<string>(
    params.get("format") || FORMATS.LinkedIn[0]
  );
  const [topic, setTopic] = useState(params.get("topic") || "");

  // Context source: "none" | "text" | "link"
  const [contextMode, setContextMode] = useState<"none" | "text" | "link">("none");
  const [pastedText, setPastedText] = useState("");
  const [linkUrl, setLinkUrl] = useState("");
  const [fetchedContext, setFetchedContext] = useState<string | null>(null);
  const [fetchingUrl, setFetchingUrl] = useState(false);
  const [fetchUrlError, setFetchUrlError] = useState<string | null>(null);

  const [contentMode, setContentMode] = useState<ContentMode>("opinion");
  const [selectedPillars, setSelectedPillars] = useState<PillarKey[]>(MODE_DEFAULTS.opinion);

  // NotebookLM research state
  const [researchDepth, setResearchDepth] = useState<ResearchDepth>("medium");
  const [researchPhase, setResearchPhase] = useState<ResearchPhase>("idle");
  const [nlmSources, setNlmSources] = useState<NLMSource[]>([]);
  const [nlmNotebookId, setNlmNotebookId] = useState<string>("");
  const [nlmNotebookUrl, setNlmNotebookUrl] = useState<string>("");
  const [selectedSourceIds, setSelectedSourceIds] = useState<Set<string>>(new Set());
  const [nlmResponse, setNlmResponse] = useState<string>("");
  const [researchError, setResearchError] = useState<string | null>(null);

  const [generatedContent, setGeneratedContent] = useState("");
  const [generating, setGenerating] = useState(false);
  const [generateError, setGenerateError] = useState<string | null>(null);
  const [showLogModal, setShowLogModal] = useState(false);

  useEffect(() => {
    setFormat(FORMATS[platform][0]);
  }, [platform]);

  function handleModeChange(mode: ContentMode) {
    setContentMode(mode);
    setSelectedPillars(MODE_DEFAULTS[mode]);
  }

  function togglePillar(key: PillarKey) {
    setSelectedPillars((prev) =>
      prev.includes(key) ? prev.filter((p) => p !== key) : [...prev, key]
    );
  }

  async function fetchUrl() {
    if (!linkUrl.trim()) return;
    setFetchingUrl(true);
    setFetchUrlError(null);
    setFetchedContext(null);
    try {
      const res = await fetch("/api/fetch-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: linkUrl.trim() }),
      });
      const data = await res.json() as { text?: string; error?: string };
      if (data.error) throw new Error(data.error);
      setFetchedContext(data.text ?? "");
    } catch (err) {
      setFetchUrlError(err instanceof Error ? err.message : String(err));
    } finally {
      setFetchingUrl(false);
    }
  }

  async function runResearch() {
    if (!topic.trim()) return;
    setResearchPhase("fetching-sources");
    setResearchError(null);
    setNlmSources([]);
    setSelectedSourceIds(new Set());
    setNlmResponse("");
    try {
      const res = await fetch("/api/research", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: topic.trim(), depth: researchDepth }),
      });
      const data: NotebookLMSourcesOutput = await res.json();
      if (!data.available) {
        setResearchError(data.error ?? "Research unavailable");
        setResearchPhase("idle");
        return;
      }
      const sources = data.sources ?? [];
      setNlmSources(sources);
      setNlmNotebookId(data.notebook_id ?? "");
      setNlmNotebookUrl(data.notebook_url ?? "");
      // All sources are topic-scoped from a fresh research pass — pre-select all.
      setSelectedSourceIds(new Set(sources.map((s) => s.id)));
      setResearchPhase("selecting");
    } catch (err) {
      setResearchError(err instanceof Error ? err.message : String(err));
      setResearchPhase("idle");
    }
  }

  function toggleSource(id: string) {
    setSelectedSourceIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function selectAll() {
    setSelectedSourceIds(new Set(nlmSources.map((s) => s.id)));
  }

  function deselectAll() {
    setSelectedSourceIds(new Set());
  }

  async function fetchResponse() {
    if (selectedSourceIds.size === 0) return;
    setResearchPhase("fetching-response");
    setResearchError(null);
    try {
      const res = await fetch("/api/research/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: topic.trim(), notebookId: nlmNotebookId, sourceIds: [...selectedSourceIds] }),
      });
      const data: NotebookLMAskOutput = await res.json();
      if (!data.available) {
        setResearchError(data.error ?? "No response from NotebookLM");
        setResearchPhase("selecting");
        return;
      }
      setNlmResponse(data.answer ?? "");
      setResearchPhase("response");
    } catch (err) {
      setResearchError(err instanceof Error ? err.message : String(err));
      setResearchPhase("selecting");
    }
  }

  function useAsContext() {
    setContextMode("text");
    setPastedText(nlmResponse);
  }

  function backToSources() {
    setResearchPhase("selecting");
    setResearchError(null);
  }

  async function generateContent() {
    if (!topic.trim()) return;
    setGenerating(true);
    setGenerateError(null);
    setGeneratedContent("");
    try {
      const context =
        contextMode === "text" ? pastedText.trim() || undefined :
        contextMode === "link" ? fetchedContext ?? undefined :
        undefined;

      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: topic.trim(), platform, format, context, contentMode, selectedPillars }),
      });
      const data = await res.json() as { content?: string; error?: string };
      if (data.error) throw new Error(data.error);
      setGeneratedContent(data.content ?? "");
    } catch (err) {
      setGenerateError(err instanceof Error ? err.message : String(err));
    } finally {
      setGenerating(false);
    }
  }

  const isBusy = researchPhase === "fetching-sources" || researchPhase === "fetching-response";

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-[26px] font-bold text-white leading-tight">Create Content</h1>
        <p className="text-[13px] text-[#666] mt-1">
          Pick a platform, enter a topic, run research, then generate.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left col — controls */}
        <div className="space-y-5">
          {/* Platform selector */}
          <div>
            <p className="text-[12px] font-semibold text-[#555] uppercase tracking-wide mb-2">Platform</p>
            <div className="flex gap-2">
              {PLATFORMS.map((p) => (
                <button
                  key={p}
                  onClick={() => setPlatform(p)}
                  className={`flex-1 py-2.5 rounded-xl text-[13px] font-semibold border transition-all duration-150 ${
                    platform === p
                      ? "gradient-blue text-white border-transparent shadow-[0_0_16px_rgba(32,142,199,0.25)]"
                      : "bg-[#111111] text-[#666] border-[rgba(255,255,255,0.06)] hover:text-white hover:border-[rgba(32,142,199,0.2)]"
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          {/* Format selector */}
          <div>
            <p className="text-[12px] font-semibold text-[#555] uppercase tracking-wide mb-2">Format</p>
            <div className="flex flex-wrap gap-2">
              {FORMATS[platform].map((f) => (
                <button
                  key={f}
                  onClick={() => setFormat(f)}
                  className={`px-4 py-2 rounded-lg text-[12px] font-medium border transition-all duration-150 ${
                    format === f
                      ? "bg-[rgba(32,142,199,0.12)] text-[#208ec7] border-[rgba(32,142,199,0.3)]"
                      : "bg-[#111111] text-[#666] border-[rgba(255,255,255,0.06)] hover:text-white hover:border-[rgba(255,255,255,0.12)]"
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          {/* Topic input */}
          <div>
            <p className="text-[12px] font-semibold text-[#555] uppercase tracking-wide mb-2">Topic</p>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") runResearch(); }}
              placeholder="e.g. AI agent security best practices"
              className="w-full px-4 py-3 rounded-xl bg-[#111111] border border-[rgba(255,255,255,0.08)] text-[13px] text-white placeholder-[#444] focus:outline-none focus:border-[rgba(32,142,199,0.4)] transition-colors"
            />
          </div>

          {/* Content Mode */}
          <div>
            <p className="text-[12px] font-semibold text-[#555] uppercase tracking-wide mb-2">Content Mode</p>
            <div className="grid grid-cols-2 gap-2">
              {CONTENT_MODES.map((mode) => (
                <button
                  key={mode.key}
                  onClick={() => handleModeChange(mode.key)}
                  className={`flex flex-col items-start px-3 py-2.5 rounded-xl text-left border transition-all duration-150 ${
                    contentMode === mode.key
                      ? "bg-[rgba(32,142,199,0.12)] text-[#208ec7] border-[rgba(32,142,199,0.3)]"
                      : "bg-[#111111] text-[#666] border-[rgba(255,255,255,0.06)] hover:text-white hover:border-[rgba(255,255,255,0.12)]"
                  }`}
                >
                  <span className="text-[12px] font-semibold">{mode.label}</span>
                  <span className={`text-[11px] mt-0.5 ${contentMode === mode.key ? "text-[#4a9bc7]" : "text-[#444]"}`}>
                    {mode.description}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Pillars */}
          <div>
            <p className="text-[12px] font-semibold text-[#555] uppercase tracking-wide mb-1">
              Pillars
              <span className="ml-2 text-[#444] font-normal normal-case tracking-normal">pre-filled by mode, editable</span>
            </p>
            <div className="flex flex-wrap gap-2">
              {PILLARS.map((pillar) => {
                const active = selectedPillars.includes(pillar.key);
                return (
                  <button
                    key={pillar.key}
                    onClick={() => togglePillar(pillar.key)}
                    className={`px-3 py-1.5 rounded-lg text-[11px] font-medium border transition-all duration-150 ${
                      active
                        ? "bg-[rgba(32,142,199,0.12)] text-[#208ec7] border-[rgba(32,142,199,0.3)]"
                        : "bg-[#111111] text-[#444] border-[rgba(255,255,255,0.06)] hover:text-[#888] hover:border-[rgba(255,255,255,0.1)]"
                    }`}
                  >
                    {active && <span className="mr-1">✓</span>}{pillar.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Context source */}
          <div>
            <p className="text-[12px] font-semibold text-[#555] uppercase tracking-wide mb-2">Source Material (optional)</p>
            <div className="flex gap-2 mb-3">
              {(["none", "text", "link"] as const).map((mode) => (
                <button
                  key={mode}
                  onClick={() => setContextMode(mode)}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-[12px] font-medium border transition-all duration-150 ${
                    contextMode === mode
                      ? "bg-[rgba(32,142,199,0.12)] text-[#208ec7] border-[rgba(32,142,199,0.3)]"
                      : "bg-[#111111] text-[#666] border-[rgba(255,255,255,0.06)] hover:text-white hover:border-[rgba(255,255,255,0.12)]"
                  }`}
                >
                  {mode === "text" && <FileText className="w-3.5 h-3.5" />}
                  {mode === "link" && <Link className="w-3.5 h-3.5" />}
                  {mode === "none" ? "None" : mode === "text" ? "Paste Text" : "Link"}
                </button>
              ))}
            </div>

            {contextMode === "text" && (
              <textarea
                value={pastedText}
                onChange={(e) => setPastedText(e.target.value)}
                placeholder="Paste an article, notes, or research context... (or use Run Research → Use as Context)"
                rows={5}
                className="w-full px-4 py-3 rounded-xl bg-[#111111] border border-[rgba(255,255,255,0.08)] text-[13px] text-white placeholder-[#444] focus:outline-none focus:border-[rgba(32,142,199,0.4)] transition-colors resize-none"
              />
            )}

            {contextMode === "link" && (
              <div className="space-y-2">
                <div className="flex gap-2">
                  <input
                    type="url"
                    value={linkUrl}
                    onChange={(e) => { setLinkUrl(e.target.value); setFetchedContext(null); setFetchUrlError(null); }}
                    onKeyDown={(e) => { if (e.key === "Enter") fetchUrl(); }}
                    placeholder="https://..."
                    className="flex-1 px-4 py-3 rounded-xl bg-[#111111] border border-[rgba(255,255,255,0.08)] text-[13px] text-white placeholder-[#444] focus:outline-none focus:border-[rgba(32,142,199,0.4)] transition-colors"
                  />
                  <button
                    onClick={fetchUrl}
                    disabled={fetchingUrl || !linkUrl.trim()}
                    className="px-4 py-3 rounded-xl bg-[#111111] border border-[rgba(32,142,199,0.2)] text-[#208ec7] text-[13px] font-semibold hover:bg-[rgba(32,142,199,0.08)] disabled:opacity-40 transition-all duration-150 shrink-0"
                  >
                    {fetchingUrl ? <Loader2 className="w-4 h-4 animate-spin" /> : "Fetch"}
                  </button>
                </div>
                {fetchUrlError && (
                  <p className="text-[12px] text-[#e05c5c]">Error: {fetchUrlError}</p>
                )}
                {fetchedContext && (
                  <div className="rounded-xl border border-[rgba(32,199,100,0.2)] bg-[rgba(32,199,100,0.04)] p-3">
                    <p className="text-[12px] text-[#4caf7d]">Fetched {fetchedContext.length.toLocaleString()} chars. Ready to use in generation.</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Research depth */}
          <div>
            <p className="text-[12px] font-semibold text-[#555] uppercase tracking-wide mb-2">Research Depth</p>
            <div className="flex gap-2">
              {(["light", "medium"] as const).map((d) => {
                const meta = { light: { label: "Light", hint: "8-12 sources" }, medium: { label: "Medium", hint: "20-25 sources" } };
                return (
                  <button
                    key={d}
                    onClick={() => setResearchDepth(d)}
                    className={`flex-1 flex flex-col items-center py-2 rounded-lg text-[12px] font-medium border transition-all duration-150 ${
                      researchDepth === d
                        ? "bg-[rgba(32,142,199,0.12)] text-[#208ec7] border-[rgba(32,142,199,0.3)]"
                        : "bg-[#111111] text-[#666] border-[rgba(255,255,255,0.06)] hover:text-white hover:border-[rgba(255,255,255,0.12)]"
                    }`}
                  >
                    <span>{meta[d].label}</span>
                    <span className={`text-[10px] mt-0.5 ${researchDepth === d ? "text-[#4a9bc7]" : "text-[#444]"}`}>{meta[d].hint}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex gap-3">
            <button
              onClick={runResearch}
              disabled={isBusy || !topic.trim()}
              className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl bg-[#111111] border border-[rgba(32,142,199,0.2)] text-[#208ec7] text-[13px] font-semibold hover:bg-[rgba(32,142,199,0.08)] disabled:opacity-40 transition-all duration-150"
            >
              {researchPhase === "fetching-sources" ? (
                <><Loader2 className="w-4 h-4 animate-spin" />Searching…</>
              ) : (
                <><Search className="w-4 h-4" />Run Research</>
              )}
            </button>
            <button
              onClick={generateContent}
              disabled={generating || !topic.trim()}
              className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl gradient-blue text-white text-[13px] font-semibold hover:opacity-90 disabled:opacity-40 transition-all duration-150 shadow-[0_0_20px_rgba(32,142,199,0.15)]"
            >
              {generating ? (
                <><Loader2 className="w-4 h-4 animate-spin" />Generating…</>
              ) : (
                <><Wand2 className="w-4 h-4" />Generate</>
              )}
            </button>
          </div>

          {researchError && (
            <div className="rounded-xl border border-[rgba(255,100,100,0.2)] bg-[rgba(255,100,100,0.05)] p-3">
              <p className="text-[12px] text-[#e05c5c]">Research: {researchError}</p>
            </div>
          )}
          {generateError && (
            <div className="rounded-xl border border-[rgba(255,100,100,0.2)] bg-[rgba(255,100,100,0.05)] p-3">
              <p className="text-[12px] text-[#e05c5c]">Generate error: {generateError}</p>
            </div>
          )}

          {/* Content output */}
          {topic && (
            <ContentOutput
              platform={platform}
              topic={topic}
              format={format}
              generatedContent={generatedContent}
              generating={generating}
            />
          )}

          {/* Log post button */}
          {generatedContent && !generating && (
            <button
              onClick={() => setShowLogModal(true)}
              className="w-full py-2.5 rounded-xl bg-[#111111] border border-[rgba(32,142,199,0.2)] text-[#208ec7] text-[13px] font-semibold hover:bg-[rgba(32,142,199,0.08)] transition-all duration-150"
            >
              Log this post →
            </button>
          )}
        </div>

        {/* Right col — NotebookLM research panel */}
        <div>
          <ResearchPanel
            phase={researchPhase}
            sources={nlmSources}
            notebookUrl={nlmNotebookUrl}
            selectedSourceIds={selectedSourceIds}
            response={nlmResponse}
            error={researchError}
            onToggleSource={toggleSource}
            onSelectAll={selectAll}
            onDeselectAll={deselectAll}
            onGetResponse={fetchResponse}
            onUseAsContext={useAsContext}
            onBackToSources={backToSources}
          />
        </div>
      </div>

      {showLogModal && (
        <LogPostModal
          platform={platform}
          format={format}
          topic={topic}
          generatedContent={generatedContent}
          onClose={() => setShowLogModal(false)}
        />
      )}
    </div>
  );
}

export default function CreatePage() {
  return (
    <Suspense fallback={null}>
      <CreatePageInner />
    </Suspense>
  );
}

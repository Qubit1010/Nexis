"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Search, Loader2, Wand2, Link, FileText } from "lucide-react";
import { ResearchPanel } from "@/components/research-panel";
import { ContentOutput } from "@/components/content-output";
import { LogPostModal } from "@/components/log-post-modal";
import type { ResearchOutput, ContentMode, PillarKey } from "@/lib/types";

type Platform = "LinkedIn" | "Instagram" | "Blog";
type FormatMap = Record<Platform, string[]>;

const PLATFORMS: Platform[] = ["LinkedIn", "Instagram", "Blog"];

const FORMATS: FormatMap = {
  LinkedIn: ["Text Post", "Article", "Newsletter"],
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

  const [research, setResearch] = useState<ResearchOutput | null>(null);
  const [researching, setResearching] = useState(false);
  const [researchError, setResearchError] = useState<string | null>(null);

  const [generatedContent, setGeneratedContent] = useState("");
  const [generating, setGenerating] = useState(false);
  const [generateError, setGenerateError] = useState<string | null>(null);
  const [showLogModal, setShowLogModal] = useState(false);

  // When platform changes, reset format to first option
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
    setResearching(true);
    setResearchError(null);
    setResearch(null);
    try {
      const res = await fetch("/api/research", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: topic.trim() }),
      });
      const data: ResearchOutput = await res.json();
      setResearch(data);
    } catch (err) {
      setResearchError(err instanceof Error ? err.message : String(err));
    } finally {
      setResearching(false);
    }
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
        body: JSON.stringify({ topic: topic.trim(), platform, format, research, context, contentMode, selectedPillars }),
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
                placeholder="Paste an article, notes, or any source material..."
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

          {/* Action buttons */}
          <div className="flex gap-3">
            <button
              onClick={runResearch}
              disabled={researching || !topic.trim()}
              className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl bg-[#111111] border border-[rgba(32,142,199,0.2)] text-[#208ec7] text-[13px] font-semibold hover:bg-[rgba(32,142,199,0.08)] disabled:opacity-40 transition-all duration-150"
            >
              {researching ? (
                <><Loader2 className="w-4 h-4 animate-spin" />Researching…</>
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
              <p className="text-[12px] text-[#e05c5c]">Research error: {researchError}</p>
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

          {/* Log post button — shown once content is generated */}
          {generatedContent && !generating && (
            <button
              onClick={() => setShowLogModal(true)}
              className="w-full py-2.5 rounded-xl bg-[#111111] border border-[rgba(32,142,199,0.2)] text-[#208ec7] text-[13px] font-semibold hover:bg-[rgba(32,142,199,0.08)] transition-all duration-150"
            >
              Log this post →
            </button>
          )}
        </div>

        {/* Right col — research panel */}
        <div>
          {!research && !researching && (
            <div className="flex flex-col items-center justify-center h-64 rounded-xl border border-dashed border-[rgba(32,142,199,0.15)] text-center p-6">
              <Search className="w-8 h-8 text-[#333] mb-3" />
              <p className="text-[14px] text-[#444] font-medium">No research yet</p>
              <p className="text-[12px] text-[#333] mt-1">
                Run Research first to get keywords, data points, and hashtags. The Generate button works without it too.
              </p>
            </div>
          )}

          {researching && (
            <div className="flex flex-col items-center justify-center h-64 rounded-xl border border-[rgba(32,142,199,0.1)] bg-[#111111] text-center p-6">
              <Loader2 className="w-8 h-8 text-[#208ec7] animate-spin mb-3" />
              <p className="text-[13px] text-[#666]">Searching the web…</p>
              <p className="text-[11px] text-[#444] mt-1">Powered by OpenAI web search</p>
            </div>
          )}

          {research && !researching && <ResearchPanel data={research} />}
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

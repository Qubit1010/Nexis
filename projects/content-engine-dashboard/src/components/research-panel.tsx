"use client";

import { Search, Loader2, ExternalLink, ClipboardCopy, ArrowLeft, BookOpen } from "lucide-react";
import type { NLMSource } from "@/lib/types";

type ResearchPhase = "idle" | "fetching-sources" | "selecting" | "fetching-response" | "response";

interface ResearchPanelProps {
  phase: ResearchPhase;
  sources: NLMSource[];
  notebookUrl: string;
  selectedSourceIds: Set<string>;
  response: string;
  error: string | null;
  onToggleSource: (id: string) => void;
  onSelectAll: () => void;
  onDeselectAll: () => void;
  onGetResponse: () => void;
  onUseAsContext: () => void;
  onBackToSources: () => void;
}

export function ResearchPanel({
  phase,
  sources,
  notebookUrl,
  selectedSourceIds,
  response,
  error,
  onToggleSource,
  onSelectAll,
  onDeselectAll,
  onGetResponse,
  onUseAsContext,
  onBackToSources,
}: ResearchPanelProps) {

  // ---- idle ----
  if (phase === "idle") {
    return (
      <div className="flex flex-col items-center justify-center h-64 rounded-xl border border-dashed border-[rgba(32,142,199,0.15)] text-center p-6">
        <BookOpen className="w-8 h-8 text-[#333] mb-3" />
        <p className="text-[14px] text-[#444] font-medium">NotebookLM Research</p>
        <p className="text-[12px] text-[#333] mt-1 leading-relaxed">
          Enter a topic and click Run Research. Select which sources to include, then get a detailed response to paste as context.
        </p>
      </div>
    );
  }

  // ---- fetching sources ----
  if (phase === "fetching-sources") {
    return (
      <div className="flex flex-col items-center justify-center h-64 rounded-xl border border-[rgba(32,142,199,0.1)] bg-[#111111] text-center p-6">
        <Loader2 className="w-8 h-8 text-[#208ec7] animate-spin mb-3" />
        <p className="text-[13px] text-[#666]">Researching the web on your topic…</p>
        <p className="text-[11px] text-[#444] mt-1">NotebookLM is pulling fresh sources. Deep can take a few minutes.</p>
      </div>
    );
  }

  // ---- source selection ----
  if (phase === "selecting") {
    const allSelected = sources.length > 0 && selectedSourceIds.size === sources.length;
    const noneSelected = selectedSourceIds.size === 0;

    return (
      <div className="space-y-3">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[13px] font-semibold text-white">
              Sources Found
              <span className="ml-2 text-[11px] font-normal text-[#555]">{sources.length} total</span>
            </p>
            <p className="text-[11px] text-[#444] mt-0.5">
              Topic-scoped from a fresh web search.
              {notebookUrl && (
                <>
                  {" "}
                  <a href={notebookUrl} target="_blank" rel="noopener noreferrer" className="text-[#208ec7] hover:text-white transition-colors">
                    View notebook
                  </a>
                </>
              )}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={onSelectAll}
              disabled={allSelected}
              className="text-[11px] text-[#208ec7] hover:text-white disabled:text-[#444] disabled:cursor-default transition-colors"
            >
              All
            </button>
            <span className="text-[#333] text-[11px]">/</span>
            <button
              onClick={onDeselectAll}
              disabled={noneSelected}
              className="text-[11px] text-[#208ec7] hover:text-white disabled:text-[#444] disabled:cursor-default transition-colors"
            >
              None
            </button>
          </div>
        </div>

        {/* Source list */}
        {sources.length === 0 ? (
          <div className="rounded-xl border border-[rgba(255,200,100,0.2)] bg-[rgba(255,200,100,0.04)] p-4">
            <p className="text-[12px] text-[#c9a84c]">No sources found for this topic in the notebook. Try a broader topic, or paste your own context.</p>
          </div>
        ) : (
          <div className="space-y-2 max-h-[420px] overflow-y-auto pr-1">
            {sources.map((source) => {
              const selected = selectedSourceIds.has(source.id);
              return (
                <div
                  key={source.id}
                  onClick={() => onToggleSource(source.id)}
                  className={`flex gap-3 p-3 rounded-xl border cursor-pointer transition-all duration-150 ${
                    selected
                      ? "bg-[rgba(32,142,199,0.08)] border-[rgba(32,142,199,0.25)]"
                      : "bg-[#111111] border-[rgba(255,255,255,0.06)] hover:border-[rgba(255,255,255,0.1)]"
                  }`}
                >
                  {/* Checkbox */}
                  <div className={`mt-0.5 w-4 h-4 rounded border flex items-center justify-center shrink-0 transition-colors ${
                    selected
                      ? "bg-[#208ec7] border-[#208ec7]"
                      : "border-[rgba(255,255,255,0.2)] bg-transparent"
                  }`}>
                    {selected && (
                      <svg className="w-2.5 h-2.5 text-white" viewBox="0 0 10 10" fill="none">
                        <path d="M1.5 5L4 7.5L8.5 2.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <p className={`text-[12px] font-medium leading-snug ${selected ? "text-white" : "text-[#888]"}`}>
                        {source.title || "Untitled source"}
                      </p>
                      {source.url && (
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={(e) => e.stopPropagation()}
                          className="text-[#444] hover:text-[#208ec7] transition-colors shrink-0 mt-0.5"
                        >
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>
                    {source.url && (
                      <p className="text-[11px] text-[#555] mt-1 leading-relaxed truncate">
                        {source.url.replace(/^https?:\/\/(www\.)?/, "")}
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Get response button */}
        <div className="pt-1">
          <button
            onClick={onGetResponse}
            disabled={noneSelected || sources.length === 0}
            className="w-full py-3 rounded-xl gradient-blue text-white text-[13px] font-semibold hover:opacity-90 disabled:opacity-40 transition-all duration-150 shadow-[0_0_20px_rgba(32,142,199,0.12)]"
          >
            Get Response from {selectedSourceIds.size} Source{selectedSourceIds.size !== 1 ? "s" : ""}
          </button>
        </div>
      </div>
    );
  }

  // ---- fetching response ----
  if (phase === "fetching-response") {
    return (
      <div className="flex flex-col items-center justify-center h-64 rounded-xl border border-[rgba(32,142,199,0.1)] bg-[#111111] text-center p-6">
        <Loader2 className="w-8 h-8 text-[#208ec7] animate-spin mb-3" />
        <p className="text-[13px] text-[#666]">Generating response from {selectedSourceIds.size} source{selectedSourceIds.size !== 1 ? "s" : ""}…</p>
        <p className="text-[11px] text-[#444] mt-1">NotebookLM is synthesizing</p>
      </div>
    );
  }

  // ---- response ----
  if (phase === "response") {
    return (
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <p className="text-[13px] font-semibold text-white">Research Response</p>
          <button
            onClick={onBackToSources}
            className="flex items-center gap-1 text-[11px] text-[#555] hover:text-[#208ec7] transition-colors"
          >
            <ArrowLeft className="w-3 h-3" />
            Back to sources
          </button>
        </div>

        <div className="bg-[#111111] border border-[rgba(32,142,199,0.12)] rounded-xl p-4 max-h-[420px] overflow-y-auto">
          <p className="text-[13px] text-[#d0d0d0] leading-relaxed whitespace-pre-wrap">{response}</p>
        </div>

        <div className="flex gap-2 pt-1">
          <button
            onClick={onUseAsContext}
            className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl gradient-blue text-white text-[13px] font-semibold hover:opacity-90 transition-all duration-150 shadow-[0_0_20px_rgba(32,142,199,0.12)]"
          >
            <ClipboardCopy className="w-4 h-4" />
            Use as Context
          </button>
        </div>

        <p className="text-[11px] text-[#444] text-center">
          This fills the Paste Text area. Then click Generate.
        </p>
      </div>
    );
  }

  return null;
}

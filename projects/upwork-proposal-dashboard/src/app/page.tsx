"use client";

import { useState } from "react";
import { Copy, Check, ExternalLink, Loader2, Zap, Save } from "lucide-react";

type JobType = "Web Dev" | "Marketing Automation" | "AI Services";

const JOB_TYPE_STYLES: Record<JobType, string> = {
  "Web Dev": "bg-blue-500/15 text-blue-400 border border-blue-500/25",
  "Marketing Automation": "bg-orange-500/15 text-orange-400 border border-orange-500/25",
  "AI Services": "bg-purple-500/15 text-purple-400 border border-purple-500/25",
};

export default function Home() {
  const [jobPost, setJobPost] = useState("");
  const [proposal, setProposal] = useState("");
  const [jobType, setJobType] = useState<JobType | null>(null);
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [copied, setCopied] = useState(false);
  const [docUrl, setDocUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleGenerate() {
    if (!jobPost.trim()) return;
    setGenerating(true);
    setError(null);
    setProposal("");
    setJobType(null);
    setDocUrl(null);

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jobPost }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Generation failed");
      setProposal(data.proposal);
      setJobType(data.jobType as JobType);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setGenerating(false);
    }
  }

  async function handleCopy() {
    if (!proposal) return;
    await navigator.clipboard.writeText(proposal);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  async function handleSave() {
    if (!proposal || !jobType) return;
    setSaving(true);
    setError(null);
    setDocUrl(null);

    try {
      const res = await fetch("/api/save-to-drive", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ proposal, jobType }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Save failed");
      setDocUrl(data.docUrl);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-[--border] px-6 py-4 flex items-center gap-3">
        <div className="w-7 h-7 rounded-md bg-[#208ec7]/20 flex items-center justify-center">
          <Zap size={14} className="text-[#208ec7]" />
        </div>
        <div>
          <h1 className="text-sm font-semibold text-[--foreground]">Proposal Generator</h1>
          <p className="text-xs text-[--muted-foreground]">NexusPoint — Upwork</p>
        </div>
      </header>

      {/* Main */}
      <div className="flex flex-1 gap-0 overflow-hidden">
        {/* Left Panel */}
        <div className="w-1/2 flex flex-col border-r border-[--border] p-6 gap-4">
          <div>
            <label className="text-xs font-medium text-[--muted-foreground] uppercase tracking-wider mb-2 block">
              Job Post
            </label>
            <textarea
              value={jobPost}
              onChange={(e) => setJobPost(e.target.value)}
              placeholder="Paste job post here..."
              className="w-full h-[calc(100vh-240px)] resize-none rounded-lg bg-[--input] border border-[--border] text-[--foreground] placeholder:text-[--muted-foreground] text-sm p-4 focus:outline-none focus:ring-1 focus:ring-[#208ec7]/50"
            />
          </div>

          <button
            onClick={handleGenerate}
            disabled={generating || !jobPost.trim()}
            className="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium transition-colors"
          >
            {generating ? (
              <>
                <Loader2 size={15} className="animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Zap size={15} />
                Generate Proposal
              </>
            )}
          </button>
        </div>

        {/* Right Panel */}
        <div className="w-1/2 flex flex-col p-6 gap-4">
          {/* Top row: label + badge */}
          <div className="flex items-center justify-between">
            <label className="text-xs font-medium text-[--muted-foreground] uppercase tracking-wider">
              Generated Proposal
            </label>
            {jobType && (
              <span
                className={`text-xs font-medium px-2.5 py-1 rounded-full ${JOB_TYPE_STYLES[jobType] || "bg-[--muted] text-[--muted-foreground]"}`}
              >
                {jobType}
              </span>
            )}
          </div>

          <textarea
            value={proposal}
            onChange={(e) => setProposal(e.target.value)}
            placeholder={generating ? "Generating your proposal..." : "Your proposal will appear here..."}
            className="flex-1 resize-none rounded-lg bg-[--input] border border-[--border] text-[--foreground] placeholder:text-[--muted-foreground] text-sm p-4 focus:outline-none focus:ring-1 focus:ring-[#208ec7]/50 leading-relaxed"
          />

          {/* Error */}
          {error && (
            <div className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
              {error}
            </div>
          )}

          {/* Doc link */}
          {docUrl && (
            <a
              href={docUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-xs text-[#208ec7] hover:text-[#208ec7]/80 transition-colors"
            >
              <ExternalLink size={12} />
              Saved to Google Drive — open doc
            </a>
          )}

          {/* Action buttons */}
          <div className="flex gap-2">
            <button
              onClick={handleCopy}
              disabled={!proposal}
              className="flex items-center gap-2 flex-1 justify-center py-2.5 rounded-lg bg-[--muted] hover:bg-[--card] disabled:opacity-40 disabled:cursor-not-allowed text-[--foreground] text-sm font-medium transition-colors border border-[--border]"
            >
              {copied ? (
                <>
                  <Check size={14} className="text-emerald-400" />
                  Copied
                </>
              ) : (
                <>
                  <Copy size={14} />
                  Copy
                </>
              )}
            </button>

            <button
              onClick={handleSave}
              disabled={saving || !proposal}
              className="flex items-center gap-2 flex-1 justify-center py-2.5 rounded-lg bg-[#208ec7]/15 hover:bg-[#208ec7]/25 disabled:opacity-40 disabled:cursor-not-allowed text-[#208ec7] text-sm font-medium transition-colors border border-[#208ec7]/25"
            >
              {saving ? (
                <>
                  <Loader2 size={14} className="animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save size={14} />
                  Save to Drive
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

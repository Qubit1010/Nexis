"use client";

import { useState, useEffect } from "react";
import { X, Loader2, CheckCircle, ExternalLink } from "lucide-react";

const GOALS = [
  "Thought leadership",
  "Educational",
  "Personal story",
  "Opinion",
  "Tutorial",
  "Promotional",
  "Engagement",
];

interface LogPostModalProps {
  platform: string;
  format: string;
  topic: string;
  generatedContent: string;
  onClose: () => void;
}

export function LogPostModal({
  platform,
  format,
  topic,
  generatedContent,
  onClose,
}: LogPostModalProps) {
  const [title, setTitle] = useState(topic);
  const [goal, setGoal] = useState(GOALS[0]);
  const [hook, setHook] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<{ docUrl: string; row: number } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const firstLine = generatedContent
      .split("\n")
      .map((l) => l.trim())
      .find((l) => l.length > 0);
    setHook(firstLine?.slice(0, 200) ?? "");
  }, [generatedContent]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const res = await fetch("/api/log-post", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          platform,
          format,
          title,
          goal,
          hook,
          content: generatedContent,
        }),
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setResult({ docUrl: data.doc_url, row: data.row });
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(0,0,0,0.7)" }}
    >
      <div className="w-full max-w-lg bg-[#111111] border border-[rgba(32,142,199,0.2)] rounded-2xl shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[rgba(255,255,255,0.06)]">
          <div>
            <h2 className="text-[15px] font-bold text-white">Log this post</h2>
            <p className="text-[11px] text-[#555] mt-0.5">
              Creates a Google Doc and logs to Content Log sheet
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-[rgba(255,255,255,0.06)] text-[#555] hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {result ? (
          <div className="flex flex-col items-center justify-center py-10 px-6 gap-4 text-center">
            <CheckCircle className="w-10 h-10 text-green-400" />
            <div>
              <p className="text-[14px] font-semibold text-white">Logged successfully</p>
              <p className="text-[12px] text-[#555] mt-1">Row {result.row} added to Content Log</p>
            </div>
            {result.docUrl && (
              <a
                href={result.docUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[rgba(32,142,199,0.1)] border border-[rgba(32,142,199,0.2)] text-[13px] text-[#208ec7] hover:bg-[rgba(32,142,199,0.18)] transition-colors"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                Open Google Doc
              </a>
            )}
            <button
              onClick={onClose}
              className="text-[12px] text-[#444] hover:text-[#666] transition-colors"
            >
              Close
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
            {/* Platform + Format chips */}
            <div className="flex gap-2">
              <span className="px-3 py-1 rounded-lg bg-[rgba(32,142,199,0.12)] border border-[rgba(32,142,199,0.25)] text-[11px] font-semibold text-[#208ec7]">
                {platform}
              </span>
              <span className="px-3 py-1 rounded-lg bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.08)] text-[11px] text-[#666]">
                {format}
              </span>
            </div>

            {/* Title */}
            <div>
              <label className="block text-[11px] font-semibold text-[#555] uppercase tracking-wide mb-1.5">
                Title / Topic
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                className="w-full px-3 py-2.5 rounded-xl bg-[#111111] border border-[rgba(255,255,255,0.08)] text-[13px] text-white placeholder-[#444] focus:outline-none focus:border-[rgba(32,142,199,0.4)] transition-colors"
              />
            </div>

            {/* Goal */}
            <div>
              <label className="block text-[11px] font-semibold text-[#555] uppercase tracking-wide mb-1.5">
                Goal
              </label>
              <select
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl bg-[#111111] border border-[rgba(255,255,255,0.08)] text-[13px] text-white focus:outline-none focus:border-[rgba(32,142,199,0.4)] transition-colors"
              >
                {GOALS.map((g) => (
                  <option key={g} value={g} className="bg-[#111111]">
                    {g}
                  </option>
                ))}
              </select>
            </div>

            {/* Hook */}
            <div>
              <label className="block text-[11px] font-semibold text-[#555] uppercase tracking-wide mb-1.5">
                Hook (opening line)
              </label>
              <textarea
                value={hook}
                onChange={(e) => setHook(e.target.value)}
                rows={2}
                className="w-full px-3 py-2.5 rounded-xl bg-[#111111] border border-[rgba(255,255,255,0.08)] text-[13px] text-white placeholder-[#444] resize-none focus:outline-none focus:border-[rgba(32,142,199,0.4)] transition-colors leading-relaxed"
              />
            </div>

            <p className="text-[11px] text-[#444]">
              A Google Doc will be created automatically in your Nexis Content Drive folder.
            </p>

            {error && (
              <div className="rounded-xl border border-[rgba(255,100,100,0.2)] bg-[rgba(255,100,100,0.05)] px-4 py-3">
                <p className="text-[12px] text-[#e05c5c]">{error}</p>
              </div>
            )}

            <div className="flex gap-3 pt-1">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 py-2.5 rounded-xl bg-[#111111] border border-[rgba(255,255,255,0.08)] text-[13px] text-[#666] hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl gradient-blue text-white text-[13px] font-semibold hover:opacity-90 disabled:opacity-50 transition-all"
              >
                {submitting ? (
                  <><Loader2 className="w-4 h-4 animate-spin" />Creating doc…</>
                ) : (
                  "Log post"
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

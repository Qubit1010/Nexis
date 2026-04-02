"use client";

import { useState } from "react";
import { Copy, Check, Loader2 } from "lucide-react";

interface ContentOutputProps {
  platform: string;
  topic: string;
  format: string;
  generatedContent?: string;
  generating?: boolean;
}

export function ContentOutput({
  platform,
  topic,
  format,
  generatedContent = "",
  generating = false,
}: ContentOutputProps) {
  const [copied, setCopied] = useState(false);
  const [manualText, setManualText] = useState("");

  const displayText = generatedContent || manualText;

  async function copyText() {
    if (!displayText) return;
    await navigator.clipboard.writeText(displayText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="bg-[#111111] border border-[rgba(255,255,255,0.07)] rounded-2xl p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <p className="text-[12px] font-semibold text-[#444] uppercase tracking-wider">
          {platform} · {format}
        </p>
        {displayText && (
          <button
            onClick={copyText}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[rgba(32,142,199,0.08)] border border-[rgba(32,142,199,0.18)] text-[12px] text-[#208ec7] hover:bg-[rgba(32,142,199,0.15)] transition-colors font-medium"
          >
            {copied ? (
              <><Check className="w-3.5 h-3.5 text-green-400" />Copied</>
            ) : (
              <><Copy className="w-3.5 h-3.5" />Copy</>
            )}
          </button>
        )}
      </div>

      {/* Content area */}
      {generating ? (
        <div className="flex flex-col items-center justify-center min-h-[180px] rounded-xl bg-[#0a0a0a] border border-[rgba(255,255,255,0.04)]">
          <Loader2 className="w-6 h-6 text-[#208ec7] animate-spin mb-3" />
          <p className="text-[13px] text-[#444]">Writing {format} for {platform}…</p>
        </div>
      ) : generatedContent ? (
        <pre className="w-full min-h-[180px] px-4 py-4 rounded-xl bg-[#0a0a0a] border border-[rgba(255,255,255,0.05)] text-[14px] text-[#d8d8d8] leading-relaxed whitespace-pre-wrap font-sans overflow-auto max-h-[500px]">
          {generatedContent}
        </pre>
      ) : (
        <textarea
          value={manualText}
          onChange={(e) => setManualText(e.target.value)}
          placeholder={`Generated ${format} will appear here. Or paste content manually…`}
          className="w-full min-h-[180px] px-4 py-4 rounded-xl bg-[#0a0a0a] border border-[rgba(255,255,255,0.05)] text-[14px] text-[#d8d8d8] placeholder-[#333] resize-y focus:outline-none focus:border-[rgba(32,142,199,0.3)] transition-colors leading-relaxed"
        />
      )}

      {/* Topic label */}
      <p className="text-[12px] text-[#333] truncate">
        Topic: <span className="text-[#555]">{topic}</span>
      </p>
    </div>
  );
}

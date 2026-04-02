"use client";

import { useRouter } from "next/navigation";
import { ArrowRight, AlertTriangle } from "lucide-react";
import type { ScoredIdea } from "@/lib/types";

interface IdeaCardProps {
  idea: ScoredIdea;
  rank: number;
}

function ScoreBadge({ score }: { score: number }) {
  let bg: string;
  let text: string;
  let label: string;

  if (score >= 9) {
    bg = "bg-[rgba(32,142,199,0.12)] border-[rgba(32,142,199,0.3)]";
    text = "text-[#4fb3e0]";
    label = "Strong";
  } else if (score >= 7) {
    bg = "bg-[rgba(31,91,153,0.12)] border-[rgba(31,91,153,0.25)]";
    text = "text-[#7ab8d8]";
    label = "Good";
  } else {
    bg = "bg-[rgba(255,255,255,0.04)] border-[rgba(255,255,255,0.08)]";
    text = "text-[#555]";
    label = "Low";
  }

  return (
    <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border ${bg} ${text}`}>
      <span className="text-[14px] font-bold tabular-nums">{score}</span>
      <span className="text-[11px] opacity-60">/10</span>
      <span className="text-[11px] font-semibold">{label}</span>
    </div>
  );
}

function Chip({ label, variant = "default" }: { label: string; variant?: "default" | "platform" | "source" | "pillar" }) {
  const styles: Record<string, string> = {
    default: "bg-[rgba(255,255,255,0.04)] text-[#777] border-[rgba(255,255,255,0.07)]",
    platform: "bg-[rgba(32,142,199,0.08)] text-[#6ab4d8] border-[rgba(32,142,199,0.15)]",
    source: "bg-[rgba(31,91,153,0.08)] text-[#5b9fd4] border-[rgba(31,91,153,0.18)]",
    pillar: "bg-[rgba(32,142,199,0.05)] text-[#5c9ab8] border-[rgba(32,142,199,0.1)]",
  };

  return (
    <span className={`inline-block px-2.5 py-0.5 rounded-full text-[12px] font-medium border ${styles[variant]}`}>
      {label}
    </span>
  );
}

export function IdeaCard({ idea, rank }: IdeaCardProps) {
  const router = useRouter();

  function handleCreate() {
    const params = new URLSearchParams({
      platform: idea.platform,
      topic: idea.topic,
      format: idea.format,
    });
    router.push(`/create?${params.toString()}`);
  }

  return (
    <div className="group relative bg-[#111111] border border-[rgba(255,255,255,0.06)] rounded-2xl p-5 hover:border-[rgba(32,142,199,0.22)] hover:bg-[#141414] transition-all duration-200">
      {/* Rank + score row */}
      <div className="flex items-start justify-between gap-3 mb-3.5">
        <div className="flex items-center gap-2.5">
          <span className="text-[12px] font-bold text-[#333] tabular-nums w-5">
            #{rank}
          </span>
          <ScoreBadge score={idea.score} />
          {idea.isCooling && (
            <div className="flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[rgba(245,165,35,0.08)] border border-[rgba(245,165,35,0.18)] text-[12px] text-[#f5a623]">
              <AlertTriangle className="w-3 h-3" />
              <span>Cooling</span>
            </div>
          )}
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center gap-1.5 text-[13px] text-[#208ec7] opacity-0 group-hover:opacity-100 transition-opacity duration-150 hover:text-white font-semibold shrink-0"
        >
          Create
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Topic */}
      <h3 className="text-[16px] font-semibold text-white leading-snug mb-2.5 tracking-tight">
        {idea.topic}
      </h3>

      {/* Hook */}
      {idea.hook && (
        <p className="text-[13px] text-[#666] leading-relaxed mb-3 italic border-l-2 border-[rgba(32,142,199,0.2)] pl-3">
          &quot;{idea.hook}&quot;
        </p>
      )}

      {/* Angle / why now */}
      {(idea.angle || idea.whyNow) && (
        <p className="text-[13px] text-[#555] leading-relaxed mb-3.5">
          {idea.angle || idea.whyNow}
        </p>
      )}

      {/* Chips row */}
      <div className="flex flex-wrap gap-1.5 items-center">
        <Chip label={idea.platform} variant="platform" />
        <Chip label={idea.format} variant="default" />
        <Chip label={idea.pillar} variant="pillar" />
        <Chip label={idea.source} variant="source" />
        {idea.timeliness && <Chip label={idea.timeliness} variant="default" />}
      </div>

      {/* Create button — always visible on mobile */}
      <button
        onClick={handleCreate}
        className="mt-4 w-full flex items-center justify-center gap-2 py-2.5 rounded-xl border border-[rgba(32,142,199,0.18)] text-[13px] text-[#208ec7] font-semibold hover:bg-[rgba(32,142,199,0.08)] hover:border-[rgba(32,142,199,0.3)] transition-all duration-150 lg:hidden"
      >
        Create this
        <ArrowRight className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}

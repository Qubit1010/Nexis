import { AlertCircle, ArrowUpRight } from "lucide-react";
import type { Recommendation } from "@/lib/types";

const DIMENSION_LABELS = {
  ux: "UX",
  content: "Content",
  technical: "Technical",
  trust: "Trust",
} as const;

const DIMENSION_COLORS = {
  ux: "#6366f1",
  content: "#10b981",
  technical: "#f59e0b",
  trust: "#ec4899",
} as const;

interface Props {
  recommendations: Recommendation[];
}

export function RecommendationsList({ recommendations }: Props) {
  if (recommendations.length === 0) {
    return (
      <div className="rounded-xl border border-[#1c1d2e] bg-[#131420] p-6 text-center">
        <p className="text-[#a0a0b8]">No specific recommendations — the site is performing well across all measured dimensions.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {recommendations.map((rec) => (
        <div
          key={rec.feature}
          className="rounded-xl border border-[#2a2b40] bg-[#131420] p-5 hover:border-[#3a3b55] transition"
        >
          <div className="flex items-start gap-4">
            <div
              className="flex items-center justify-center w-8 h-8 rounded-full shrink-0 text-sm font-semibold"
              style={{
                background: `${DIMENSION_COLORS[rec.dimension]}20`,
                color: DIMENSION_COLORS[rec.dimension],
              }}
            >
              {rec.priority}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1.5">
                <h3 className="font-semibold text-base">{rec.title}</h3>
                <span
                  className="text-xs px-2 py-0.5 rounded-full"
                  style={{
                    background: `${DIMENSION_COLORS[rec.dimension]}15`,
                    color: DIMENSION_COLORS[rec.dimension],
                  }}
                >
                  {DIMENSION_LABELS[rec.dimension]}
                </span>
              </div>
              <p className="text-sm text-[#a0a0b8] leading-relaxed mb-2">{rec.rationale}</p>
              <div className="flex items-center gap-1.5 text-xs text-[#10b981]">
                <ArrowUpRight className="w-3.5 h-3.5" />
                Estimated impact: {rec.impact}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export function NoRecommendations() {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-[#1c1d2e] bg-[#131420] p-5">
      <AlertCircle className="w-5 h-5 text-[#a0a0b8] shrink-0" />
      <p className="text-sm text-[#a0a0b8]">No actionable issues detected at this score level.</p>
    </div>
  );
}

import { Tag, TrendingUp, HelpCircle, Lightbulb, Link2 } from "lucide-react";
import type { ResearchOutput } from "@/lib/types";

interface ResearchPanelProps {
  data: ResearchOutput;
}

export function ResearchPanel({ data }: ResearchPanelProps) {
  if (!data.available) {
    return (
      <div className="rounded-xl border border-[rgba(255,100,100,0.2)] bg-[rgba(255,100,100,0.05)] p-4">
        <p className="text-[13px] text-[#e05c5c]">
          Research failed: {data.error}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Keywords */}
      <div className="bg-[#111111] border border-[rgba(32,142,199,0.12)] rounded-xl p-4">
        <div className="flex items-center gap-2 mb-3">
          <TrendingUp className="w-4 h-4 text-[#208ec7]" />
          <h3 className="text-[13px] font-semibold text-white">Keywords</h3>
        </div>
        {data.primary_keyword && (
          <div className="mb-2">
            <p className="text-[10px] text-[#555] uppercase tracking-wide mb-1">
              Primary
            </p>
            <span className="inline-block px-3 py-1 rounded-full bg-[rgba(32,142,199,0.12)] border border-[rgba(32,142,199,0.25)] text-[#208ec7] text-[12px] font-medium">
              {data.primary_keyword}
            </span>
          </div>
        )}
        {data.secondary_keywords && data.secondary_keywords.length > 0 && (
          <div>
            <p className="text-[10px] text-[#555] uppercase tracking-wide mb-1.5">
              Secondary
            </p>
            <div className="flex flex-wrap gap-1.5">
              {data.secondary_keywords.map((kw) => (
                <span
                  key={kw}
                  className="px-2.5 py-0.5 rounded-full bg-[rgba(255,255,255,0.04)] border border-[rgba(255,255,255,0.08)] text-[11px] text-[#8a8a8a]"
                >
                  {kw}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Content gap */}
      {data.content_gap && (
        <div className="bg-[rgba(32,142,199,0.06)] border border-[rgba(32,142,199,0.2)] rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <Lightbulb className="w-4 h-4 text-[#208ec7]" />
            <h3 className="text-[13px] font-semibold text-[#208ec7]">
              Content Gap
            </h3>
          </div>
          <p className="text-[13px] text-[#d0e8f5] leading-relaxed">
            {data.content_gap}
          </p>
        </div>
      )}

      {/* Data points */}
      {data.data_points && data.data_points.length > 0 && (
        <div className="bg-[#111111] border border-[rgba(32,142,199,0.12)] rounded-xl p-4">
          <div className="flex items-center gap-2 mb-3">
            <Link2 className="w-4 h-4 text-[#208ec7]" />
            <h3 className="text-[13px] font-semibold text-white">
              Data Points
            </h3>
          </div>
          <div className="space-y-2.5">
            {data.data_points.map((dp, i) => (
              <div key={i} className="flex gap-3">
                <span className="text-[#208ec7] text-[11px] font-bold tabular-nums mt-0.5 shrink-0">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <div>
                  <p className="text-[13px] text-[#e0e0e0] leading-snug">
                    {dp.fact}
                  </p>
                  <p className="text-[11px] text-[#555] mt-0.5">{dp.source}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* PAA */}
      {data.people_also_ask && data.people_also_ask.length > 0 && (
        <div className="bg-[#111111] border border-[rgba(32,142,199,0.12)] rounded-xl p-4">
          <div className="flex items-center gap-2 mb-3">
            <HelpCircle className="w-4 h-4 text-[#208ec7]" />
            <h3 className="text-[13px] font-semibold text-white">
              People Also Ask
            </h3>
          </div>
          <ul className="space-y-1.5">
            {data.people_also_ask.map((q, i) => (
              <li
                key={i}
                className="text-[12px] text-[#8a8a8a] flex gap-2 leading-snug"
              >
                <span className="text-[#444] shrink-0">—</span>
                {q}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Hashtags */}
      {data.hashtags && data.hashtags.length > 0 && (
        <div className="bg-[#111111] border border-[rgba(32,142,199,0.12)] rounded-xl p-4">
          <div className="flex items-center gap-2 mb-3">
            <Tag className="w-4 h-4 text-[#208ec7]" />
            <h3 className="text-[13px] font-semibold text-white">Hashtags</h3>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {data.hashtags.map((tag) => (
              <span
                key={tag}
                className="px-2.5 py-1 rounded-full bg-[rgba(31,91,153,0.12)] border border-[rgba(31,91,153,0.2)] text-[#5b9fd4] text-[11px] font-medium"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

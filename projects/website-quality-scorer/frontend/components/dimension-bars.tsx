import type { SubScores } from "@/lib/types";

interface Props {
  subScores: SubScores;
}

const DIMENSIONS: { key: keyof SubScores; label: string; color: string }[] = [
  { key: "ux",        label: "UX & Layout",   color: "#6366f1" },
  { key: "content",   label: "Content",       color: "#10b981" },
  { key: "technical", label: "Technical",     color: "#f59e0b" },
  { key: "trust",     label: "Trust & Conv.", color: "#ec4899" },
];

const MAX = 25;

export function DimensionBars({ subScores }: Props) {
  return (
    <div className="space-y-4">
      {DIMENSIONS.map(({ key, label, color }) => {
        const value = subScores[key];
        const pct = Math.max(0, Math.min(100, (value / MAX) * 100));
        return (
          <div key={key}>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-sm font-medium">{label}</span>
              <span className="text-sm tabular-nums text-[#a0a0b8]">
                {value.toFixed(1)} <span className="text-[#5a5b75]">/ {MAX}</span>
              </span>
            </div>
            <div className="h-2 rounded-full overflow-hidden bg-[#1c1d2e]">
              <div
                className="h-full rounded-full transition-all duration-700"
                style={{ width: `${pct}%`, background: color }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

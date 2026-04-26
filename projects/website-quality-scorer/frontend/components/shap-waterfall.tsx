import type { ShapValue } from "@/lib/types";

interface Props {
  shapValues: ShapValue[];
  maxItems?: number;
}

const DIMENSION_COLORS = {
  ux: "#6366f1",
  content: "#10b981",
  technical: "#f59e0b",
  trust: "#ec4899",
} as const;

function formatFeatureName(feature: string): string {
  return feature
    .replace(/^(ux|content|tech|trust)_/, "")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatRawValue(value: number | boolean | null): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "number") {
    if (Number.isInteger(value)) return String(value);
    return value.toFixed(2);
  }
  return String(value);
}

export function ShapWaterfall({ shapValues, maxItems = 10 }: Props) {
  const items = shapValues.slice(0, maxItems);
  if (items.length === 0) {
    return <p className="text-sm text-[#5a5b75]">No SHAP data available.</p>;
  }

  const maxAbs = Math.max(...items.map((v) => Math.abs(v.shap_value)), 0.001);

  return (
    <div className="space-y-2">
      {items.map((item) => {
        const isPositive = item.shap_value >= 0;
        const widthPct = (Math.abs(item.shap_value) / maxAbs) * 50;
        const color = DIMENSION_COLORS[item.dimension];

        return (
          <div key={item.feature} className="text-sm">
            <div className="flex items-center justify-between mb-1">
              <span className="font-medium truncate pr-2">{formatFeatureName(item.feature)}</span>
              <span className="text-xs text-[#a0a0b8] tabular-nums shrink-0">
                value: {formatRawValue(item.raw_value)}
              </span>
            </div>
            <div className="relative h-5 bg-[#131420] rounded">
              <div className="absolute inset-y-0 left-1/2 w-px bg-[#2a2b40]" />
              <div
                className="absolute inset-y-0 transition-all duration-500"
                style={{
                  background: isPositive ? color : "#ef4444",
                  opacity: 0.85,
                  left: isPositive ? "50%" : `${50 - widthPct}%`,
                  width: `${widthPct}%`,
                  borderRadius: isPositive ? "0 4px 4px 0" : "4px 0 0 4px",
                }}
              />
              <div className="absolute inset-0 flex items-center justify-end pr-2 text-xs tabular-nums text-[#a0a0b8]">
                {item.shap_value >= 0 ? "+" : ""}
                {item.shap_value.toFixed(2)}
              </div>
            </div>
          </div>
        );
      })}
      <div className="flex items-center gap-4 text-xs text-[#5a5b75] pt-2">
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-sm bg-[#10b981]" /> Increases score
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-sm bg-[#ef4444]" /> Decreases score
        </span>
      </div>
    </div>
  );
}

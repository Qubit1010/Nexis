import type { Tier } from "@/lib/types";

interface Props {
  score: number;
  tier: Tier;
}

const TIER_COLORS: Record<Tier, string> = {
  Poor: "#ef4444",
  Average: "#f59e0b",
  Good: "#10b981",
  Excellent: "#6366f1",
};

export function ScoreGauge({ score, tier }: Props) {
  const radius = 90;
  const stroke = 14;
  const normalizedRadius = radius - stroke / 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const dash = (score / 100) * circumference;
  const color = TIER_COLORS[tier];

  return (
    <div className="relative flex items-center justify-center">
      <svg height={radius * 2} width={radius * 2}>
        <circle
          stroke="#1c1d2e"
          fill="transparent"
          strokeWidth={stroke}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
        />
        <circle
          stroke={color}
          fill="transparent"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${dash} ${circumference}`}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
          transform={`rotate(-90 ${radius} ${radius})`}
          style={{ transition: "stroke-dasharray 1s ease-out" }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-5xl font-bold tabular-nums">{Math.round(score)}</span>
        <span className="text-xs uppercase tracking-wider mt-1" style={{ color }}>
          {tier}
        </span>
      </div>
    </div>
  );
}

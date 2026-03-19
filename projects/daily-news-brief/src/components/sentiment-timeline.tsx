"use client";

import { useEffect, useState, useRef } from "react";

interface SentimentPoint {
  date: string;
  label: string;
  score: number;
  summary: string;
}

const LABEL_COLORS: Record<string, string> = {
  bullish: "#22c55e",
  cautious: "#f59e0b",
  mixed: "#a78bfa",
  bearish: "#ef4444",
};

const LABEL_NAMES: Record<string, string> = {
  bullish: "Bullish",
  cautious: "Cautious",
  mixed: "Mixed",
  bearish: "Bearish",
};

export function SentimentTimeline({ date }: { date: string }) {
  const [points, setPoints] = useState<SentimentPoint[]>([]);
  const [hovered, setHovered] = useState<number | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    fetch(`/api/sentiment/history?date=${date}`)
      .then((r) => r.json())
      .then(setPoints)
      .catch(() => {});
  }, [date]);

  if (points.length < 2) return null;

  const w = 500;
  const h = 120;
  const px = 40;
  const py = 20;
  const chartW = w - px * 2;
  const chartH = h - py * 2;

  const scores = points.map((p) => p.score);
  const min = Math.min(...scores) - 0.5;
  const max = Math.max(...scores) + 0.5;
  const range = max - min || 1;

  const coords = points.map((p, i) => ({
    x: px + (i / (points.length - 1)) * chartW,
    y: py + (1 - (p.score - min) / range) * chartH,
  }));

  // Smooth line path
  const linePath = coords
    .map((c, i) => `${i === 0 ? "M" : "L"} ${c.x} ${c.y}`)
    .join(" ");

  // Fill path under the line
  const fillPath = `${linePath} L ${coords[coords.length - 1].x} ${h - py} L ${coords[0].x} ${h - py} Z`;

  return (
    <div className="rounded-xl border border-border/60 p-5 animate-fade-in">
      <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-[0.12em] mb-4">
        Sentiment Trend (7 days)
      </p>

      <div className="relative">
        <svg
          ref={svgRef}
          viewBox={`0 0 ${w} ${h}`}
          className="w-full"
          style={{ maxWidth: w }}
        >
          <defs>
            <linearGradient id="timeline-fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f59e0b" stopOpacity="0.18" />
              <stop offset="100%" stopColor="#f59e0b" stopOpacity="0" />
            </linearGradient>
          </defs>

          {/* Gradient fill */}
          <path d={fillPath} fill="url(#timeline-fill)" />

          {/* Line */}
          <path
            d={linePath}
            fill="none"
            stroke="#f59e0b"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Data points + date labels */}
          {coords.map((c, i) => {
            const color = LABEL_COLORS[points[i].label] || "#a1a1aa";
            const isHovered = hovered === i;
            return (
              <g
                key={i}
                onMouseEnter={() => setHovered(i)}
                onMouseLeave={() => setHovered(null)}
                className="cursor-pointer"
              >
                {/* Larger invisible hit area */}
                <circle cx={c.x} cy={c.y} r="12" fill="transparent" />

                {/* Outer glow on hover */}
                {isHovered && (
                  <circle
                    cx={c.x}
                    cy={c.y}
                    r="8"
                    fill={color}
                    opacity="0.2"
                  />
                )}

                {/* Dot */}
                <circle
                  cx={c.x}
                  cy={c.y}
                  r={isHovered ? 5.5 : 4}
                  fill={color}
                  stroke="var(--background)"
                  strokeWidth="2"
                  style={{ transition: "r 0.15s ease" }}
                />

                {/* Date label */}
                <text
                  x={c.x}
                  y={h - 3}
                  textAnchor="middle"
                  className="fill-muted-foreground"
                  style={{ fontSize: "9px" }}
                >
                  {points[i].date.slice(5)}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Tooltip */}
        {hovered !== null && (
          <div
            className="absolute z-10 bg-card border border-border rounded-lg px-3 py-2.5 shadow-xl pointer-events-none text-xs"
            style={{
              left: `${(coords[hovered].x / w) * 100}%`,
              top: `${(coords[hovered].y / h) * 100 - 12}%`,
              transform: "translate(-50%, -100%)",
              minWidth: 180,
            }}
          >
            <div className="flex items-center gap-2 mb-1">
              <span
                className="w-2.5 h-2.5 rounded-full"
                style={{
                  backgroundColor:
                    LABEL_COLORS[points[hovered].label] || "#a1a1aa",
                }}
              />
              <span className="font-semibold text-foreground">
                {LABEL_NAMES[points[hovered].label] || points[hovered].label}
              </span>
              <span className="text-muted-foreground ml-auto">
                {points[hovered].date}
              </span>
            </div>
            <p className="text-muted-foreground leading-snug line-clamp-2">
              {points[hovered].summary}
            </p>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mt-3">
        {Object.entries(LABEL_COLORS).map(([label, color]) => (
          <div
            key={label}
            className="flex items-center gap-1.5 text-[11px] text-muted-foreground/60"
          >
            <span
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: color }}
            />
            <span className="capitalize">{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

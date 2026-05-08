"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, ExternalLink } from "lucide-react";
import { ScoreGauge } from "@/components/score-gauge";
import { DimensionBars } from "@/components/dimension-bars";
import { ShapWaterfall } from "@/components/shap-waterfall";
import { RecommendationsList } from "@/components/recommendations-list";
import type { ScoreData } from "@/lib/types";

export default function ScorePage() {
  const [data, setData] = useState<ScoreData | null>(null);

  useEffect(() => {
    const cached = sessionStorage.getItem("scoreResult");
    if (cached) {
      try {
        setData(JSON.parse(cached) as ScoreData);
      } catch {
        // ignore
      }
    }
  }, []);

  if (!data) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-6 py-16">
        <p className="text-[#a0a0b8] mb-6">No score data available.</p>
        <Link
          href="/"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[#6366f1] hover:bg-[#7c7fff] transition"
        >
          <ArrowLeft className="w-4 h-4" />
          Score a website
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen px-6 py-10 md:py-16">
      <div className="max-w-5xl mx-auto">

        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm text-[#a0a0b8] hover:text-white transition mb-8"
        >
          <ArrowLeft className="w-4 h-4" />
          Score another site
        </Link>

        <div className="flex items-start justify-between mb-8 gap-4">
          <div className="min-w-0">
            <p className="text-xs uppercase tracking-wider text-[#a0a0b8] mb-2">Scored URL</p>
            <a
              href={data.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-2xl md:text-3xl font-semibold text-white hover:text-[#818cf8] transition truncate max-w-full"
            >
              <span className="truncate">{data.url}</span>
              <ExternalLink className="w-5 h-5 shrink-0 opacity-60" />
            </a>
            <p className="text-xs text-[#5a5b75] mt-2">
              Model: {data.model_version}  ·  Analyzed in {(data.elapsed_ms / 1000).toFixed(1)}s
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-5">
          <Card title="Composite Score">
            <div className="flex flex-col items-center py-6">
              <ScoreGauge score={data.score} tier={data.tier} />
              <p className="text-xs text-[#5a5b75] mt-4">Out of 100</p>
            </div>
          </Card>

          <Card title="Sub-scores by Dimension">
            <DimensionBars subScores={data.sub_scores} />
          </Card>
        </div>

        <Card title="What's driving the score (SHAP)" className="mb-5">
          <p className="text-sm text-[#a0a0b8] mb-5">
            Top features contributing positively or negatively to this score.
            Computed from the model's exact Shapley values.
          </p>
          <ShapWaterfall shapValues={data.shap_values} />
        </Card>

        <Card title={`Recommendations (${data.recommendations.length})`}>
          <p className="text-sm text-[#a0a0b8] mb-5">
            Highest-impact gaps to address, ranked by SHAP magnitude.
          </p>
          <RecommendationsList recommendations={data.recommendations} />
        </Card>
      </div>
    </div>
  );
}

function Card({
  title,
  children,
  className = "",
}: {
  title: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={`rounded-2xl border border-[#1c1d2e] bg-[#131420] p-6 ${className}`}>
      <h2 className="text-sm font-semibold uppercase tracking-wider text-[#a0a0b8] mb-4">
        {title}
      </h2>
      {children}
    </section>
  );
}

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Loader2, Sparkles } from "lucide-react";
import { scoreUrl } from "@/lib/api-client";

export default function HomePage() {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    const trimmed = url.trim();
    if (!trimmed) {
      setError("Please enter a URL.");
      return;
    }

    setLoading(true);
    const res = await scoreUrl(trimmed);
    setLoading(false);

    if (!res.ok || !res.data) {
      setError(res.error || "Something went wrong.");
      return;
    }

    sessionStorage.setItem("scoreResult", JSON.stringify(res.data));
    router.push("/score");
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 py-16">
      <div className="max-w-2xl w-full text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs uppercase tracking-wider bg-[#1c1d2e] text-[#818cf8] mb-6 border border-[#2a2b40]">
          <Sparkles className="w-3.5 h-3.5" />
          ML-Powered Website Audit
        </div>

        <h1 className="text-5xl md:text-6xl font-bold tracking-tight mb-4 bg-gradient-to-br from-white to-[#a0a0b8] bg-clip-text text-transparent">
          Score any website in seconds
        </h1>

        <p className="text-lg text-[#a0a0b8] mb-10 max-w-xl mx-auto">
          Paste a URL, get an instant 0-100 quality score across UX, content, technical, and trust dimensions, with SHAP-explained recommendations.
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 max-w-xl mx-auto">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            disabled={loading}
            className="flex-1 px-5 py-3.5 rounded-xl bg-[#131420] border border-[#2a2b40] focus:border-[#6366f1] focus:outline-none focus:ring-2 focus:ring-[#6366f1]/30 transition placeholder:text-[#5a5b75] text-base"
          />
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-[#6366f1] hover:bg-[#7c7fff] disabled:opacity-50 disabled:cursor-not-allowed font-medium transition"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Scoring
              </>
            ) : (
              <>
                Score it
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {error && (
          <p className="mt-4 text-sm text-[#ef4444]">{error}</p>
        )}

        {loading && (
          <p className="mt-6 text-sm text-[#a0a0b8]">
            Crawling site, fetching PageSpeed metrics, running model... up to 30s.
          </p>
        )}
      </div>

      <footer className="absolute bottom-6 text-xs text-[#5a5b75]">
        Machine Learning AIN-373  ·  Iqra University  ·  Spring 2026
      </footer>
    </div>
  );
}

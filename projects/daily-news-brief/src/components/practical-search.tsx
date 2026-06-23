"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search, Loader2 } from "lucide-react";

const DAY_OPTIONS = [2, 7, 14, 30];

export function PracticalSearch() {
  const [tool, setTool] = useState("");
  const [days, setDays] = useState(7);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    const q = tool.trim();
    if (!q || loading) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/practical/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tool: q, days }),
      });
      const data = await res.json();
      if (!res.ok || !data.id) {
        throw new Error(data.error || "Lookup failed");
      }
      router.push(`/practical/lookup/${data.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lookup failed");
      setLoading(false);
    }
  }

  return (
    <div className="rounded-xl border border-teal-500/20 bg-teal-500/[0.03] p-4">
      <p className="text-[11px] font-semibold text-teal-500/80 uppercase tracking-[0.15em] mb-3">
        Look up any tool
      </p>
      <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground/50" />
          <input
            value={tool}
            onChange={(e) => setTool(e.target.value)}
            placeholder="e.g. Claude Code, n8n, Cursor..."
            disabled={loading}
            className="w-full h-10 pl-9 pr-3 rounded-lg bg-background/60 border border-border/50 text-sm focus:outline-none focus:border-teal-500/50 transition-colors disabled:opacity-60"
          />
        </div>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          disabled={loading}
          className="h-10 px-3 rounded-lg bg-background/60 border border-border/50 text-sm focus:outline-none focus:border-teal-500/50 disabled:opacity-60"
        >
          {DAY_OPTIONS.map((d) => (
            <option key={d} value={d}>
              {d} days
            </option>
          ))}
        </select>
        <button
          type="submit"
          disabled={loading || !tool.trim()}
          className="h-10 px-5 rounded-lg text-sm font-medium bg-teal-500/15 text-teal-400 border border-teal-500/30 hover:bg-teal-500/25 transition-all disabled:opacity-50 inline-flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Fetching...
            </>
          ) : (
            "Look up"
          )}
        </button>
      </form>
      {loading && (
        <p className="text-[12px] text-muted-foreground/60 mt-2">
          Fetching fresh updates and how people use it. This takes a minute or two.
        </p>
      )}
      {error && (
        <p
          className={`text-[12px] mt-2 ${
            error.startsWith("No evidence found")
              ? "text-muted-foreground/60"
              : "text-red-400/80"
          }`}
        >
          {error.startsWith("No evidence found")
            ? `${error}. Try a more specific name like "Claude Code", "n8n", or "Cursor".`
            : error}
        </p>
      )}
    </div>
  );
}

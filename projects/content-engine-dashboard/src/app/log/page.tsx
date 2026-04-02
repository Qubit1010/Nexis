"use client";

import { useState, useEffect } from "react";
import { RefreshCw, ExternalLink, Loader2 } from "lucide-react";

interface LogData {
  headers: string[];
  rows: string[][];
  note?: string;
  error?: string;
}

const STATUS_COLORS: Record<string, string> = {
  Draft: "bg-[rgba(255,165,0,0.1)] text-[#f5a623] border-[rgba(255,165,0,0.2)]",
  Published:
    "bg-[rgba(32,142,199,0.1)] text-[#208ec7] border-[rgba(32,142,199,0.2)]",
  Scheduled:
    "bg-[rgba(31,91,153,0.1)] text-[#5b9fd4] border-[rgba(31,91,153,0.2)]",
};

function StatusChip({ status }: { status: string }) {
  const styles =
    STATUS_COLORS[status] ||
    "bg-[rgba(255,255,255,0.04)] text-[#666] border-[rgba(255,255,255,0.08)]";
  return (
    <span
      className={`inline-block px-2.5 py-0.5 rounded-full text-[11px] font-medium border ${styles}`}
    >
      {status}
    </span>
  );
}

export default function LogPage() {
  const [logData, setLogData] = useState<LogData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function fetchLog() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/log");
      const data: LogData = await res.json();
      if (data.error) throw new Error(data.error);
      setLogData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchLog();
  }, []);

  const headers = logData?.headers ?? [];
  const rows = logData?.rows ?? [];

  // Column index helpers
  function col(row: string[], header: string): string {
    const i = headers.indexOf(header);
    return i >= 0 && i < row.length ? (row[i] ?? "") : "";
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-[26px] font-bold text-white leading-tight">
            Content Log
          </h1>
          <p className="text-[13px] text-[#666] mt-1">
            All logged posts from the Google Sheets Content Log tab.
          </p>
        </div>
        <button
          onClick={fetchLog}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl gradient-blue text-white text-[13px] font-semibold hover:opacity-90 disabled:opacity-50 transition-all duration-150 shrink-0"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4" />
          )}
          Refresh
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-xl border border-[rgba(255,100,100,0.2)] bg-[rgba(255,100,100,0.05)] p-4 mb-5">
          <p className="text-[13px] text-[#e05c5c]">Error: {error}</p>
        </div>
      )}

      {/* Note (e.g. tab not created yet) */}
      {logData?.note && (
        <div className="rounded-xl border border-[rgba(32,142,199,0.15)] bg-[rgba(32,142,199,0.05)] p-4 mb-5">
          <p className="text-[13px] text-[#7ab8d8]">{logData.note}</p>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-14 rounded-xl bg-[#111111] border border-[rgba(255,255,255,0.04)] animate-pulse"
            />
          ))}
        </div>
      )}

      {/* Empty */}
      {!loading && !error && rows.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="w-14 h-14 rounded-2xl bg-[#111111] flex items-center justify-center mb-4 opacity-40">
            <RefreshCw className="w-6 h-6 text-[#555]" />
          </div>
          <p className="text-[15px] font-medium text-[#555]">No posts logged yet</p>
          <p className="text-[13px] text-[#444] mt-1">
            Use <code className="text-[#208ec7]">log post</code> in Claude Code to log a post.
          </p>
        </div>
      )}

      {/* Table */}
      {!loading && rows.length > 0 && (
        <div className="rounded-xl border border-[rgba(32,142,199,0.1)] overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-[13px]">
              <thead>
                <tr className="border-b border-[rgba(32,142,199,0.1)] bg-[#111111]">
                  <th className="text-left px-4 py-3 text-[12px] font-semibold text-[#555] uppercase tracking-wide whitespace-nowrap">
                    Date
                  </th>
                  <th className="text-left px-4 py-3 text-[12px] font-semibold text-[#555] uppercase tracking-wide whitespace-nowrap">
                    Platform
                  </th>
                  <th className="text-left px-4 py-3 text-[12px] font-semibold text-[#555] uppercase tracking-wide whitespace-nowrap">
                    Format
                  </th>
                  <th className="text-left px-4 py-3 text-[12px] font-semibold text-[#555] uppercase tracking-wide">
                    Title / Topic
                  </th>
                  <th className="text-left px-4 py-3 text-[12px] font-semibold text-[#555] uppercase tracking-wide">
                    Goal
                  </th>
                  <th className="text-left px-4 py-3 text-[12px] font-semibold text-[#555] uppercase tracking-wide">
                    Status
                  </th>
                  <th className="text-left px-4 py-3 text-[12px] font-semibold text-[#555] uppercase tracking-wide">
                    Doc
                  </th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row, i) => {
                  const docUrl = col(row, "Doc URL");
                  return (
                    <tr
                      key={i}
                      className="border-b border-[rgba(255,255,255,0.04)] last:border-0 hover:bg-[rgba(32,142,199,0.03)] transition-colors"
                    >
                      <td className="px-4 py-3 text-[#666] whitespace-nowrap">
                        {col(row, "Date Posted")}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <span className="px-2.5 py-0.5 rounded-full bg-[rgba(32,142,199,0.08)] border border-[rgba(32,142,199,0.15)] text-[#7ab8d8] text-[11px] font-medium">
                          {col(row, "Platform")}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-[#8a8a8a] whitespace-nowrap">
                        {col(row, "Format")}
                      </td>
                      <td className="px-4 py-3 text-white max-w-[240px]">
                        <p className="truncate">{col(row, "Title/Topic")}</p>
                        {col(row, "Hook") && (
                          <p className="text-[11px] text-[#555] truncate mt-0.5 italic">
                            {col(row, "Hook")}
                          </p>
                        )}
                      </td>
                      <td className="px-4 py-3 text-[#666] max-w-[160px]">
                        <p className="truncate">{col(row, "Goal")}</p>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <StatusChip status={col(row, "Status") || "Draft"} />
                      </td>
                      <td className="px-4 py-3">
                        {docUrl ? (
                          <a
                            href={docUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-[#208ec7] hover:text-white transition-colors text-[12px]"
                          >
                            Open
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        ) : (
                          <span className="text-[#333]">—</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <div className="px-4 py-2.5 border-t border-[rgba(255,255,255,0.04)] bg-[#111111]">
            <p className="text-[11px] text-[#444]">
              {rows.length} {rows.length === 1 ? "post" : "posts"} logged
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

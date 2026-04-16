"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import { RefreshCw, Loader2, ChevronLeft, ChevronRight, CalendarPlus, Pencil } from "lucide-react";
import { ScheduleModal } from "@/components/schedule-modal";

interface ScheduleData {
  headers: string[];
  rows: string[][];
  error?: string;
}

// ---- Status chip ----
const STATUS_COLORS: Record<string, string> = {
  Draft: "bg-[rgba(255,165,0,0.1)] text-[#f5a623] border-[rgba(255,165,0,0.2)]",
  Published: "bg-[rgba(32,142,199,0.1)] text-[#208ec7] border-[rgba(32,142,199,0.2)]",
  Scheduled: "bg-[rgba(31,91,153,0.1)] text-[#5b9fd4] border-[rgba(31,91,153,0.2)]",
  Cancelled: "bg-[rgba(255,80,80,0.08)] text-[#e05c5c] border-[rgba(255,80,80,0.18)]",
};

function StatusChip({ status }: { status: string }) {
  const styles =
    STATUS_COLORS[status] ||
    "bg-[rgba(255,255,255,0.04)] text-[#666] border-[rgba(255,255,255,0.08)]";
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-[11px] font-medium border ${styles}`}>
      {status || "Draft"}
    </span>
  );
}

// ---- Platform chip ----
function PlatformChip({ platform }: { platform: string }) {
  return (
    <span className="px-2 py-0.5 rounded-full bg-[rgba(32,142,199,0.08)] border border-[rgba(32,142,199,0.15)] text-[#7ab8d8] text-[11px] font-medium whitespace-nowrap">
      {platform || "All"}
    </span>
  );
}

// ---- Week helpers ----
function getMonday(d: Date): Date {
  const date = new Date(d);
  const day = date.getDay();
  const diff = day === 0 ? -6 : 1 - day; // Monday = 1
  date.setDate(date.getDate() + diff);
  date.setHours(0, 0, 0, 0);
  return date;
}

function getWeekDays(monday: Date): Date[] {
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(monday);
    d.setDate(d.getDate() + i);
    return d;
  });
}

function formatDisplayDate(d: Date): string {
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function formatDayLabel(d: Date): string {
  return d.toLocaleDateString("en-US", { weekday: "long" });
}

function isToday(d: Date): boolean {
  const today = new Date();
  return (
    d.getDate() === today.getDate() &&
    d.getMonth() === today.getMonth() &&
    d.getFullYear() === today.getFullYear()
  );
}

// Normalise "Mar 2" / "Mar 02" / "2026-03-02" → "Mar 2" for matching
function normaliseDateStr(raw: string): string {
  if (!raw) return "";
  // Already "Mon DD" style (from sheet)
  const shortMatch = raw.match(/^([A-Za-z]+)\s+(\d+)$/);
  if (shortMatch) return `${shortMatch[1]} ${parseInt(shortMatch[2])}`;
  // ISO "YYYY-MM-DD"
  const isoMatch = raw.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (isoMatch) {
    const d = new Date(`${raw}T00:00:00`);
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  }
  return raw.trim();
}

// ---- Main page ----
export default function SchedulePage() {
  const [scheduleData, setScheduleData] = useState<ScheduleData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [weekStart, setWeekStart] = useState<Date>(() => getMonday(new Date()));
  const [platformFilter, setPlatformFilter] = useState("All");
  const [statusFilter, setStatusFilter] = useState("All");
  const [modalOpen, setModalOpen] = useState(false);
  const [editData, setEditData] = useState<{ rowNumber: number; row: Record<string, string> } | null>(null);
  const [refreshTick, setRefreshTick] = useState(0);

  const fetchSchedule = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/schedule");
      const data: ScheduleData = await res.json();
      if (data.error) throw new Error(data.error);
      setScheduleData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSchedule();
  }, [fetchSchedule, refreshTick]);

  const headers = scheduleData?.headers ?? [];
  const rows = scheduleData?.rows ?? [];

  function col(row: string[], header: string): string {
    const i = headers.indexOf(header);
    return i >= 0 && i < row.length ? (row[i] ?? "") : "";
  }

  const weekDays = useMemo(() => getWeekDays(weekStart), [weekStart]);

  // Build a map: normalised date string → { row, sheetRowNumber }[]
  // rows[i] corresponds to sheet row i+2 (row 1 is the header)
  const rowsByDate = useMemo(() => {
    const map = new Map<string, { row: string[]; sheetRowNumber: number }[]>();
    for (let i = 0; i < rows.length; i++) {
      const row = rows[i];
      const dateRaw = col(row, "Date");
      const key = normaliseDateStr(dateRaw);
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push({ row, sheetRowNumber: i + 2 });
    }
    return map;
  }, [rows, headers]);

  const weekLabel = `${formatDisplayDate(weekDays[0])} – ${formatDisplayDate(weekDays[6])}`;

  const allPlatforms = useMemo(() => {
    const set = new Set<string>();
    for (const row of rows) {
      const p = col(row, "Platform");
      if (p) set.add(p);
    }
    return ["All", ...Array.from(set)];
  }, [rows, headers]);

  function filterRow(row: string[]): boolean {
    if (platformFilter !== "All" && col(row, "Platform") !== platformFilter) return false;
    if (statusFilter !== "All" && (col(row, "Status") || "Draft") !== statusFilter) return false;
    return true;
  }

  const totalWeekPosts = useMemo(() => {
    let count = 0;
    for (const day of weekDays) {
      const key = formatDisplayDate(day);
      const dayEntries = rowsByDate.get(key) ?? [];
      count += dayEntries.filter((e) => filterRow(e.row)).length;
    }
    return count;
  }, [weekDays, rowsByDate, platformFilter, statusFilter]);

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-[26px] font-bold text-white leading-tight">Weekly Schedule</h1>
          <p className="text-[13px] text-[#666] mt-1">
            Content calendar from Google Sheets · SM Schedule tab.
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => { setModalOpen(true); }}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-[rgba(32,142,199,0.25)] text-[#208ec7] text-[13px] font-semibold hover:bg-[rgba(32,142,199,0.08)] transition-all duration-150"
          >
            <CalendarPlus className="w-4 h-4" />
            Add Post
          </button>
          <button
            onClick={fetchSchedule}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl gradient-blue text-white text-[13px] font-semibold hover:opacity-90 disabled:opacity-50 transition-all duration-150 shadow-[0_0_20px_rgba(32,142,199,0.2)]"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
            Refresh
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-xl border border-[rgba(255,100,100,0.2)] bg-[rgba(255,100,100,0.05)] p-4 mb-5">
          <p className="text-[13px] text-[#e05c5c]">Error: {error}</p>
        </div>
      )}

      {/* Week nav + filters */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
        {/* Week navigation */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setWeekStart((w) => { const d = new Date(w); d.setDate(d.getDate() - 7); return d; })}
            className="p-1.5 rounded-lg text-[#555] hover:text-white hover:bg-[rgba(255,255,255,0.06)] transition-all"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="text-[13px] font-semibold text-white min-w-[160px] text-center">{weekLabel}</span>
          <button
            onClick={() => setWeekStart((w) => { const d = new Date(w); d.setDate(d.getDate() + 7); return d; })}
            className="p-1.5 rounded-lg text-[#555] hover:text-white hover:bg-[rgba(255,255,255,0.06)] transition-all"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
          <button
            onClick={() => setWeekStart(getMonday(new Date()))}
            className="px-3 py-1 rounded-lg text-[11px] font-semibold text-[#555] border border-[rgba(255,255,255,0.07)] hover:text-white hover:border-[rgba(255,255,255,0.15)] transition-all"
          >
            Today
          </button>
          {!loading && (
            <span className="text-[11px] text-[#444]">{totalWeekPosts} posts this week</span>
          )}
        </div>

        {/* Filters */}
        <div className="flex items-center gap-2">
          <select
            value={platformFilter}
            onChange={(e) => setPlatformFilter(e.target.value)}
            className="bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.07)] rounded-lg px-3 py-1.5 text-[12px] text-[#888] focus:outline-none focus:border-[rgba(32,142,199,0.3)] transition-colors"
          >
            {allPlatforms.map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.07)] rounded-lg px-3 py-1.5 text-[12px] text-[#888] focus:outline-none focus:border-[rgba(32,142,199,0.3)] transition-colors"
          >
            {["All", "Draft", "Scheduled", "Published", "Cancelled"].map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Loading skeleton */}
      {loading && (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 rounded-xl bg-[#111111] border border-[rgba(255,255,255,0.04)] animate-pulse" />
          ))}
        </div>
      )}

      {/* Week days */}
      {!loading && (
        <div className="space-y-2.5">
          {weekDays.map((day) => {
            const key = formatDisplayDate(day);
            const dayEntries = (rowsByDate.get(key) ?? []).filter((e) => filterRow(e.row));
            const today = isToday(day);

            return (
              <div
                key={key}
                className={`rounded-xl border transition-all ${
                  today
                    ? "border-[rgba(32,142,199,0.25)] bg-[rgba(32,142,199,0.03)]"
                    : "border-[rgba(255,255,255,0.06)] bg-[#111111]"
                }`}
              >
                {/* Day header */}
                <div className="flex items-center gap-3 px-4 py-3 border-b border-[rgba(255,255,255,0.04)]">
                  <div className="flex items-center gap-2.5">
                    <span className={`text-[13px] font-bold ${today ? "text-[#208ec7]" : "text-[#555]"}`}>
                      {formatDayLabel(day)}
                    </span>
                    <span className="text-[12px] text-[#3a3a3a]">{key}</span>
                    {today && (
                      <span className="px-2 py-0.5 rounded-full bg-[rgba(32,142,199,0.12)] border border-[rgba(32,142,199,0.25)] text-[#208ec7] text-[10px] font-semibold">
                        Today
                      </span>
                    )}
                  </div>
                  {dayEntries.length > 0 && (
                    <span className="ml-auto text-[11px] font-semibold text-[#444]">
                      {dayEntries.length} {dayEntries.length === 1 ? "post" : "posts"}
                    </span>
                  )}
                </div>

                {/* Posts */}
                {dayEntries.length === 0 ? (
                  <div className="px-4 py-3.5">
                    <p className="text-[12px] text-[#2a2a2a]">No posts scheduled</p>
                  </div>
                ) : (
                  <div className="divide-y divide-[rgba(255,255,255,0.03)]">
                    {dayEntries.map(({ row, sheetRowNumber }, i) => {
                      const topic = col(row, "Topic / Idea");
                      const platform = col(row, "Platform");
                      const mediaType = col(row, "Media Type");
                      const contentTheme = col(row, "Content Theme");
                      const status = col(row, "Status") || "Draft";
                      const editor = col(row, "Editor");
                      const publishTime = col(row, "Publish Time");

                      // Build a column-name → value map for the edit modal
                      const rowMap = Object.fromEntries(
                        headers.map((h, idx) => [h, row[idx] ?? ""])
                      );

                      return (
                        <div
                          key={i}
                          className="group/row flex items-start gap-3 px-4 py-3 hover:bg-[rgba(255,255,255,0.02)] transition-colors"
                        >
                          {/* Time */}
                          <div className="w-14 shrink-0 pt-0.5">
                            <span className="text-[11px] text-[#3a3a3a]">{publishTime || "--:--"}</span>
                          </div>

                          {/* Main content */}
                          <div className="flex-1 min-w-0">
                            <div className="flex flex-wrap items-center gap-1.5 mb-1.5">
                              <PlatformChip platform={platform} />
                              {mediaType && (
                                <span className="text-[11px] text-[#555] bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.06)] px-2 py-0.5 rounded-full">
                                  {mediaType}
                                </span>
                              )}
                              {contentTheme && (
                                <span className="text-[11px] text-[#444] truncate max-w-[140px]">
                                  {contentTheme.replace(/^[\p{Emoji}\s]+/u, "").trim()}
                                </span>
                              )}
                            </div>
                            <p className="text-[13px] text-white font-medium leading-snug truncate">
                              {topic || "Untitled"}
                            </p>
                          </div>

                          {/* Right side */}
                          <div className="flex items-center gap-2 shrink-0">
                            <StatusChip status={status} />
                            {editor && (
                              <span className="text-[11px] text-[#444] hidden sm:block">{editor}</span>
                            )}
                            <button
                              onClick={() => setEditData({ rowNumber: sheetRowNumber, row: rowMap })}
                              className="opacity-0 group-hover/row:opacity-100 transition-opacity p-1 rounded-lg text-[#444] hover:text-white hover:bg-[rgba(255,255,255,0.06)]"
                              title="Edit post"
                            >
                              <Pencil className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Add to Schedule modal */}
      <ScheduleModal
        open={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setRefreshTick((t) => t + 1);
        }}
      />

      {/* Edit post modal */}
      <ScheduleModal
        open={!!editData}
        onClose={() => {
          setEditData(null);
          setRefreshTick((t) => t + 1);
        }}
        editData={editData ?? undefined}
      />
    </div>
  );
}

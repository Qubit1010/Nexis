"use client";

import { useState, useEffect } from "react";
import { X, CalendarPlus, Loader2 } from "lucide-react";
import { SCHEDULE_COLUMNS } from "@/lib/types";

interface ScheduleModalProps {
  open: boolean;
  onClose: () => void;
  prefill?: {
    topic?: string;
    platform?: string;
    format?: string;
    angle?: string;
  };
  // When provided, modal is in edit mode — fields pre-filled, submits a PUT
  editData?: {
    rowNumber: number;         // 1-based sheet row number
    row: Record<string, string>; // column name → value
  };
}

const PLATFORMS = ["All", "LinkedIn", "Instagram", "Blog"];
const POST_TYPES = ["Text + Images", "Video", "Reel", "Carousel", "Static Image", "Short Video", "Newsletter"];
const MEDIA_TYPES = ["Carousel", "Static Image", "Short Video", "Reel", "Text Post", "Article", "Thread"];
const EDITORS = ["Aleem", "Moiz", "Tooba", "Areeba", "Sher Nadir"];
const STATUS_OPTIONS = ["Draft", "Scheduled"];

function formatPlatform(p: string): string {
  if (p === "LinkedIn") return "LinkedIn";
  if (p === "Instagram") return "Instagram";
  if (p === "Blog") return "Blog";
  return "All";
}

function formatToMediaType(format: string): string {
  const f = format.toLowerCase();
  if (f.includes("carousel")) return "Carousel";
  if (f.includes("reel")) return "Reel";
  if (f.includes("short")) return "Short Video";
  if (f.includes("article")) return "Static Image";
  if (f.includes("newsletter")) return "Text Post";
  if (f.includes("thread")) return "Static Image";
  return "Static Image";
}

function todayStr(): string {
  const d = new Date();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${mm}-${dd}`;
}

function getDayName(dateStr: string): string {
  if (!dateStr) return "";
  const d = new Date(dateStr + "T00:00:00");
  return ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][d.getDay()];
}

export function ScheduleModal({ open, onClose, prefill, editData }: ScheduleModalProps) {
  const isEdit = !!editData;

  const [date, setDate] = useState(todayStr());
  const [platform, setPlatform] = useState("All");
  const [postType, setPostType] = useState("Text + Images");
  const [mediaType, setMediaType] = useState("Carousel");
  const [contentTheme, setContentTheme] = useState("Tech & AI News");
  const [topic, setTopic] = useState("");
  const [description, setDescription] = useState("");
  const [editor, setEditor] = useState("Aleem");
  const [publishTime, setPublishTime] = useState("");
  const [status, setStatus] = useState("Draft");
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Apply prefill / editData when opened
  useEffect(() => {
    if (!open) return;
    setSuccess(false);
    setError(null);

    if (editData) {
      const r = editData.row;
      // Convert "Mar 2" → ISO date for the date input
      const rawDate = r["Date"] ?? "";
      const isoDate = (() => {
        const m = rawDate.match(/^([A-Za-z]+)\s+(\d+)$/);
        if (m) {
          const d = new Date(`${m[1]} ${m[2]}, ${new Date().getFullYear()}`);
          if (!isNaN(d.getTime())) {
            return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
          }
        }
        return todayStr();
      })();
      setDate(isoDate);
      setPlatform(r["Platform"] || "All");
      setPostType(r["Post Type"] || "Text + Images");
      setMediaType(r["Media Type"] || "Carousel");
      setContentTheme(r["Content Theme"] || "Tech & AI News");
      setTopic(r["Topic / Idea"] || "");
      setDescription(r["Post Description"] || "");
      setEditor(r["Editor"] || "Aleem");
      setPublishTime(r["Publish Time"] || "");
      setStatus(r["Status"] || "Draft");
    } else if (prefill) {
      if (prefill.topic) setTopic(prefill.topic);
      if (prefill.platform) setPlatform(formatPlatform(prefill.platform));
      if (prefill.format) setMediaType(formatToMediaType(prefill.format));
      if (prefill.angle) setDescription(prefill.angle);
    }
  }, [open, editData, prefill]);

  if (!open) return null;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    // Build row matching SCHEDULE_COLUMNS order exactly:
    // Date, Day, Platform, Post Type, Media Type, Content Theme,
    // Topic / Idea, Post Description, Video/Post Script, Video Prompt,
    // Image Prompt, Reference Images, Thumbnail, Audio, Draft,
    // Final Video/Post, Reference, Hashtags, Publish Time, Status, Editor
    const dayName = getDayName(date);
    const displayDate = date
      ? new Date(date + "T00:00:00").toLocaleDateString("en-US", { month: "short", day: "numeric" })
      : "";

    const row = SCHEDULE_COLUMNS.map((col) => {
      switch (col) {
        case "Date": return displayDate;
        case "Day": return dayName;
        case "Platform": return platform;
        case "Post Type": return postType;
        case "Media Type": return mediaType;
        case "Content Theme": return contentTheme;
        case "Topic / Idea": return topic;
        case "Post Description": return description;
        case "Publish Time": return publishTime;
        case "Status": return status;
        case "Editor": return editor;
        default: return "";
      }
    });

    try {
      const res = await fetch("/api/schedule", {
        method: isEdit ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(isEdit ? { rowNumber: editData!.rowNumber, row } : { row }),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.error || "Failed to save");
      setSuccess(true);
      setTimeout(() => {
        onClose();
        setSuccess(false);
      }, 1200);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative z-10 w-full max-w-lg bg-[#111111] border border-[rgba(32,142,199,0.2)] rounded-2xl shadow-[0_0_40px_rgba(32,142,199,0.15)] max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between px-5 pt-5 pb-4 border-b border-[rgba(255,255,255,0.06)]">
          <div className="flex items-center gap-2.5">
            <CalendarPlus className="w-[18px] h-[18px] text-[#208ec7]" />
            <h2 className="text-[15px] font-bold text-white">{isEdit ? "Edit Post" : "Add to Schedule"}</h2>
          </div>
          <button
            onClick={onClose}
            className="text-[#555] hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="px-5 py-5 space-y-4">
          {/* Date + Platform row */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-semibold text-[#555] uppercase tracking-wide mb-1.5">Date</label>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                required
                className="w-full bg-[#0d0d0d] border border-[rgba(255,255,255,0.08)] rounded-lg px-3 py-2 text-[13px] text-white focus:outline-none focus:border-[rgba(32,142,199,0.4)] transition-colors"
              />
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-[#555] uppercase tracking-wide mb-1.5">Platform</label>
              <select
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
                className="w-full bg-[#0d0d0d] border border-[rgba(255,255,255,0.08)] rounded-lg px-3 py-2 text-[13px] text-white focus:outline-none focus:border-[rgba(32,142,199,0.4)] transition-colors"
              >
                {PLATFORMS.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
          </div>

          {/* Post Type + Media Type row */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-semibold text-[#555] uppercase tracking-wide mb-1.5">Post Type</label>
              <select
                value={postType}
                onChange={(e) => setPostType(e.target.value)}
                className="w-full bg-[#0d0d0d] border border-[rgba(255,255,255,0.08)] rounded-lg px-3 py-2 text-[13px] text-white focus:outline-none focus:border-[rgba(32,142,199,0.4)] transition-colors"
              >
                {POST_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-[#555] uppercase tracking-wide mb-1.5">Media Type</label>
              <select
                value={mediaType}
                onChange={(e) => setMediaType(e.target.value)}
                className="w-full bg-[#0d0d0d] border border-[rgba(255,255,255,0.08)] rounded-lg px-3 py-2 text-[13px] text-white focus:outline-none focus:border-[rgba(32,142,199,0.4)] transition-colors"
              >
                {MEDIA_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
          </div>

          {/* Content Theme */}
          <div>
            <label className="block text-[11px] font-semibold text-[#555] uppercase tracking-wide mb-1.5">Content Theme</label>
            <input
              type="text"
              value={contentTheme}
              onChange={(e) => setContentTheme(e.target.value)}
              placeholder="e.g. Tech & AI News"
              className="w-full bg-[#0d0d0d] border border-[rgba(255,255,255,0.08)] rounded-lg px-3 py-2 text-[13px] text-white placeholder-[#444] focus:outline-none focus:border-[rgba(32,142,199,0.4)] transition-colors"
            />
          </div>

          {/* Topic / Idea */}
          <div>
            <label className="block text-[11px] font-semibold text-[#555] uppercase tracking-wide mb-1.5">Topic / Idea</label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              required
              placeholder="Content topic or title"
              className="w-full bg-[#0d0d0d] border border-[rgba(255,255,255,0.08)] rounded-lg px-3 py-2 text-[13px] text-white placeholder-[#444] focus:outline-none focus:border-[rgba(32,142,199,0.4)] transition-colors"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-[11px] font-semibold text-[#555] uppercase tracking-wide mb-1.5">Post Description <span className="normal-case text-[#444] font-normal">(optional)</span></label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              placeholder="Brief description or angle"
              className="w-full bg-[#0d0d0d] border border-[rgba(255,255,255,0.08)] rounded-lg px-3 py-2 text-[13px] text-white placeholder-[#444] focus:outline-none focus:border-[rgba(32,142,199,0.4)] transition-colors resize-none"
            />
          </div>

          {/* Editor + Status + Time row */}
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-[11px] font-semibold text-[#555] uppercase tracking-wide mb-1.5">Editor</label>
              <select
                value={editor}
                onChange={(e) => setEditor(e.target.value)}
                className="w-full bg-[#0d0d0d] border border-[rgba(255,255,255,0.08)] rounded-lg px-3 py-2 text-[13px] text-white focus:outline-none focus:border-[rgba(32,142,199,0.4)] transition-colors"
              >
                {EDITORS.map((e) => <option key={e} value={e}>{e}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-[#555] uppercase tracking-wide mb-1.5">Status</label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                className="w-full bg-[#0d0d0d] border border-[rgba(255,255,255,0.08)] rounded-lg px-3 py-2 text-[13px] text-white focus:outline-none focus:border-[rgba(32,142,199,0.4)] transition-colors"
              >
                {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-[#555] uppercase tracking-wide mb-1.5">Time</label>
              <input
                type="time"
                value={publishTime}
                onChange={(e) => setPublishTime(e.target.value)}
                className="w-full bg-[#0d0d0d] border border-[rgba(255,255,255,0.08)] rounded-lg px-3 py-2 text-[13px] text-white focus:outline-none focus:border-[rgba(32,142,199,0.4)] transition-colors"
              />
            </div>
          </div>

          {/* Error */}
          {error && (
            <p className="text-[12px] text-[#e05c5c] bg-[rgba(255,100,100,0.05)] border border-[rgba(255,100,100,0.15)] rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={submitting || success}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl gradient-blue text-white text-[13px] font-semibold hover:opacity-90 disabled:opacity-60 transition-all duration-150 shadow-[0_0_20px_rgba(32,142,199,0.2)]"
          >
            {submitting ? (
              <><Loader2 className="w-4 h-4 animate-spin" /> Saving...</>
            ) : success ? (
              isEdit ? "Updated!" : "Added to schedule!"
            ) : isEdit ? (
              <><CalendarPlus className="w-4 h-4" /> Save Changes</>
            ) : (
              <><CalendarPlus className="w-4 h-4" /> Add to Schedule</>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

"use client";

import { useCallback, useEffect, useState } from "react";
import { Copy, Check, Loader2, Zap, MessageSquare, X } from "lucide-react";

type Situation = "pre_hire" | "active" | "closeout" | "reactivation";
type JobType = "ai-services" | "marketing-automation" | "web-dev";

type Meta = { situation: string; move: string; why: string };

type Conversation = {
  id: number;
  identity: string;
  client_name: string;
  job_title: string;
  job_type: string;
  profile: string;
  situation: string;
  stage: string;
  exchange_count: number;
  thread: string;
  last_draft: string;
  last_contact: string;
  updated_at: string;
};

const ACCENT = "#14a800"; // Upwork green

const SITUATIONS: { value: Situation; label: string }[] = [
  { value: "pre_hire", label: "Pre-hire" },
  { value: "active", label: "Active project" },
  { value: "closeout", label: "Closeout" },
  { value: "reactivation", label: "Reactivation" },
];

const JOB_TYPES: { value: JobType; label: string }[] = [
  { value: "ai-services", label: "AI Services" },
  { value: "marketing-automation", label: "Marketing Automation" },
  { value: "web-dev", label: "Web Dev" },
];

const STAGES = ["pre_hire", "negotiating", "active", "delivered", "reviewed", "reactivation", "dead"] as const;

const GOALS: Record<Situation, string[]> = {
  pre_hire: ["win the hire", "hold my rate", "clarify scope", "move to a contract"],
  active: ["contain scope", "handle feedback", "push to next milestone", "unblock the work"],
  closeout: ["land the 5-star review", "open a retainer", "confirm delivery"],
  reactivation: ["reopen with a reason", "offer an Ops Teardown", "keep it warm"],
};

// New conversations inherit a stage from the situation; existing ones keep theirs.
const SITUATION_DEFAULT_STAGE: Record<Situation, string> = {
  pre_hire: "pre_hire",
  active: "active",
  closeout: "delivered",
  reactivation: "reactivation",
};

const inputClass =
  "w-full rounded-lg bg-[--input] border border-[--border] text-[--foreground] placeholder:text-[--muted-foreground] text-sm px-3 py-2 focus:outline-none focus:ring-1 focus:ring-white/20";

const labelClass =
  "text-xs font-medium text-[--muted-foreground] uppercase tracking-wider mb-1.5 block";

export default function Home() {
  const [situation, setSituation] = useState<Situation>("pre_hire");
  const [jobType, setJobType] = useState<JobType>("ai-services");

  const [clientMessage, setClientMessage] = useState("");
  const [thread, setThread] = useState("");
  const [profile, setProfile] = useState("");
  const [clientName, setClientName] = useState("");
  const [identityRaw, setIdentityRaw] = useState("");
  const [goal, setGoal] = useState("");

  const [convos, setConvos] = useState<Conversation[]>([]);
  const [selectedConvoId, setSelectedConvoId] = useState<number | null>(null);
  const [memoryAvailable, setMemoryAvailable] = useState(true);

  const [message, setMessage] = useState("");
  const [meta, setMeta] = useState<Meta | null>(null);

  const [generating, setGenerating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const wordCount = message.trim() ? message.trim().split(/\s+/).length : 0;
  const over = wordCount > 200;

  function resetOutput() {
    setMessage("");
    setMeta(null);
    setError(null);
  }

  const loadConvos = useCallback(async () => {
    try {
      const res = await fetch("/api/conversations");
      if (res.status === 503) {
        setMemoryAvailable(false);
        return;
      }
      const data = await res.json();
      if (res.ok) {
        setMemoryAvailable(true);
        setConvos(data.conversations ?? []);
      }
    } catch {
      setMemoryAvailable(false);
    }
  }, []);

  useEffect(() => {
    loadConvos();
  }, [loadConvos]);

  const selectedConvo = convos.find((c) => c.id === selectedConvoId) ?? null;

  function selectConvo(id: number | null) {
    setSelectedConvoId(id);
    const c = convos.find((x) => x.id === id);
    if (c) {
      setThread(c.thread);
      setProfile(c.profile);
      setClientName(c.client_name);
      setIdentityRaw(c.identity);
      setClientMessage("");
      if (["pre_hire", "active", "closeout", "reactivation"].includes(c.situation)) {
        setSituation(c.situation as Situation);
      }
      if (c.job_type && JOB_TYPES.some((j) => j.value === c.job_type)) setJobType(c.job_type as JobType);
    } else {
      setThread("");
      setProfile("");
      setClientName("");
      setIdentityRaw("");
      setClientMessage("");
    }
    resetOutput();
  }

  async function saveConvo(fields: Record<string, unknown>): Promise<void> {
    if (!memoryAvailable || !identityRaw.trim()) return;
    try {
      const res = await fetch("/api/conversations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          identityRaw,
          client_name: clientName || undefined,
          profile: profile || undefined,
          job_type: jobType,
          ...fields,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        await loadConvos();
        if (data.conversation?.id) setSelectedConvoId(data.conversation.id);
      }
    } catch {
      // memory is a convenience layer; drafting still works without it
    }
  }

  const canGenerate =
    profile.trim() && (situation === "reactivation" || clientMessage.trim());

  async function handleGenerate() {
    setGenerating(true);
    resetOutput();
    try {
      const res = await fetch("/api/draft", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          situation,
          jobType,
          clientMessage,
          thread,
          profile,
          goal,
          identityRaw: identityRaw.trim() || undefined,
          state: selectedConvo
            ? {
                exchange_count: selectedConvo.exchange_count,
                stage: selectedConvo.stage,
                last_contact: selectedConvo.last_contact,
              }
            : undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Generation failed");
      setMessage(data.message);
      setMeta(data.meta ?? null);

      // Persist the thread + draft. Keep an existing convo's stage; a new one inherits from the situation.
      await saveConvo({
        situation,
        stage: selectedConvo ? selectedConvo.stage : SITUATION_DEFAULT_STAGE[situation],
        thread: [thread, clientMessage].filter(Boolean).join("\n\n"),
        last_draft: data.message,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setGenerating(false);
    }
  }

  async function handleCopy() {
    if (!message) return;
    await navigator.clipboard.writeText(message);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-[--border] px-6 py-4 flex items-center gap-3 shrink-0">
        <div className="w-7 h-7 rounded-md flex items-center justify-center" style={{ backgroundColor: `${ACCENT}26` }}>
          <MessageSquare size={14} style={{ color: ACCENT }} />
        </div>
        <div>
          <h1 className="text-sm font-semibold text-[--foreground]">Upwork Reply Drafter</h1>
          <p className="text-xs text-[--muted-foreground]">NexusPoint — research-backed client replies</p>
        </div>
      </header>

      {/* Main */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel */}
        <div className="w-1/2 flex flex-col border-r border-[--border] p-6 gap-4 overflow-y-auto">
          {/* Situation */}
          <div>
            <label className={labelClass}>Situation</label>
            <div className="grid grid-cols-2 gap-1 p-1 rounded-lg bg-[--muted]">
              {SITUATIONS.map((s) => {
                const active = situation === s.value;
                return (
                  <button
                    key={s.value}
                    onClick={() => {
                      setSituation(s.value);
                      setGoal("");
                      resetOutput();
                    }}
                    className={`py-1.5 text-xs font-medium rounded-md transition-colors ${
                      active ? "text-white" : "text-[--muted-foreground] hover:text-[--foreground]"
                    }`}
                    style={active ? { backgroundColor: ACCENT } : undefined}
                  >
                    {s.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Job type */}
          <div>
            <label className={labelClass}>Job type</label>
            <div className="flex gap-1 p-1 rounded-lg bg-[--muted]">
              {JOB_TYPES.map((j) => {
                const active = jobType === j.value;
                return (
                  <button
                    key={j.value}
                    onClick={() => setJobType(j.value)}
                    className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-colors ${
                      active
                        ? "bg-[--card] text-[--foreground] border border-[--border]"
                        : "text-[--muted-foreground] hover:text-[--foreground]"
                    }`}
                  >
                    {j.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Memory */}
          {memoryAvailable ? (
            <div>
              <label className={labelClass}>Saved conversations</label>
              <select
                value={selectedConvoId ?? ""}
                onChange={(e) => selectConvo(e.target.value ? Number(e.target.value) : null)}
                className={`${inputClass} cursor-pointer`}
              >
                <option value="">New conversation</option>
                {convos.map((c) => (
                  <option key={c.id} value={c.id}>
                    {`${c.client_name || c.identity} · ${c.stage} · ${c.exchange_count} ${
                      c.exchange_count === 1 ? "reply" : "replies"
                    }`}
                  </option>
                ))}
              </select>
              {selectedConvo && (
                <div className="flex items-center gap-2 mt-2">
                  <span className="text-xs text-[--muted-foreground]">Stage</span>
                  <select
                    value={selectedConvo.stage}
                    onChange={(e) => saveConvo({ stage: e.target.value })}
                    className="rounded-lg bg-[--input] border border-[--border] text-[--foreground] text-xs px-2 py-1 cursor-pointer focus:outline-none focus:ring-1 focus:ring-white/20"
                  >
                    {STAGES.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-[--muted-foreground]">
              Conversation memory is off. Set SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY in .env.local to save
              threads across sessions.
            </p>
          )}

          {/* Client's latest message */}
          <div>
            <label className={labelClass}>
              Client&apos;s latest message {situation === "reactivation" ? "(optional for reactivation)" : "*"}
            </label>
            <textarea
              value={clientMessage}
              onChange={(e) => setClientMessage(e.target.value)}
              placeholder={
                situation === "reactivation"
                  ? "Leave blank — reactivation opens a cold thread from the profile + past outcome."
                  : "Paste the client's message you're replying to..."
              }
              className={`${inputClass} resize-none h-24`}
            />
          </div>

          {/* Full thread (optional) */}
          <div>
            <label className={labelClass}>Full thread so far (optional)</label>
            <textarea
              value={thread}
              onChange={(e) => setThread(e.target.value)}
              placeholder={`Paste both sides for context.\n\n[Me]: ...\n[Them]: ...`}
              className={`${inputClass} resize-none h-28`}
            />
          </div>

          {/* Profile */}
          <div>
            <label className={labelClass}>Client / job profile *</label>
            <input
              value={profile}
              onChange={(e) => setProfile(e.target.value)}
              placeholder="SaaS founder, 200+ support tickets/day, wants AI triage; posted $400 budget"
              className={inputClass}
            />
          </div>

          {/* Client name + identity */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={labelClass}>Client name</label>
              <input
                value={clientName}
                onChange={(e) => setClientName(e.target.value)}
                placeholder="John"
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>Profile URL / label (memory key)</label>
              <input
                value={identityRaw}
                onChange={(e) => setIdentityRaw(e.target.value)}
                placeholder="upwork.com/... or acme-john"
                className={inputClass}
              />
            </div>
          </div>

          {/* Goal */}
          <div>
            <label className={labelClass}>Goal (optional)</label>
            <select value={goal} onChange={(e) => setGoal(e.target.value)} className={`${inputClass} cursor-pointer`}>
              <option value="">Auto-detect from the situation</option>
              {GOALS[situation].map((g) => (
                <option key={g} value={g}>
                  {g}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleGenerate}
            disabled={generating || !canGenerate}
            className="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg text-white text-sm font-medium transition-opacity disabled:opacity-40 disabled:cursor-not-allowed hover:opacity-90"
            style={{ backgroundColor: ACCENT }}
          >
            {generating ? (
              <>
                <Loader2 size={15} className="animate-spin" />
                Drafting...
              </>
            ) : (
              <>
                <Zap size={15} />
                Draft reply
              </>
            )}
          </button>
        </div>

        {/* Right Panel */}
        <div className="w-1/2 flex flex-col p-6 gap-4">
          <div className="flex items-center justify-between shrink-0">
            <label className={labelClass}>Generated reply</label>
            <div className="flex items-center gap-2">
              {message && (
                <span
                  className={`text-xs font-mono px-2 py-0.5 rounded border ${
                    over
                      ? "bg-amber-500/15 text-amber-400 border-amber-500/25"
                      : "bg-emerald-500/15 text-emerald-400 border-emerald-500/25"
                  }`}
                  title="Research target: 150-200 words"
                >
                  {wordCount} words
                </span>
              )}
              {message && (
                <button
                  onClick={resetOutput}
                  className="text-[--muted-foreground] hover:text-[--foreground] transition-colors"
                >
                  <X size={14} />
                </button>
              )}
            </div>
          </div>

          {/* Empty state */}
          {!message && !generating && !error && (
            <div className="flex-1 flex items-center justify-center text-[--muted-foreground] text-sm text-center">
              <div>
                <MessageSquare size={36} className="mx-auto mb-3 opacity-15" />
                <p>Your {SITUATIONS.find((s) => s.value === situation)?.label.toLowerCase()} reply will appear here</p>
                <p className="text-xs mt-1 opacity-50">Fill in the fields and click Draft reply</p>
              </div>
            </div>
          )}

          {/* Loading */}
          {generating && (
            <div className="flex-1 flex items-center justify-center text-[--muted-foreground] text-sm gap-2">
              <Loader2 size={18} className="animate-spin" style={{ color: ACCENT }} />
              Drafting from the playbook...
            </div>
          )}

          {/* Output */}
          {message && (
            <>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="flex-1 resize-none rounded-lg bg-[--input] border border-[--border] text-[--foreground] text-sm p-4 focus:outline-none focus:ring-1 focus:ring-white/20 leading-relaxed"
              />

              {meta && (meta.situation || meta.move || meta.why) && (
                <div className="shrink-0 border border-[--border] rounded-lg p-3 bg-[--card] flex flex-col gap-2">
                  {meta.situation && (
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-[--muted-foreground] w-14 shrink-0">Situation</span>
                      <span
                        className="text-xs font-medium px-2.5 py-0.5 rounded-full border"
                        style={{ backgroundColor: `${ACCENT}26`, color: ACCENT, borderColor: `${ACCENT}40` }}
                      >
                        {meta.situation}
                      </span>
                    </div>
                  )}
                  {meta.move && (
                    <div className="flex items-start gap-2">
                      <span className="text-xs text-[--muted-foreground] w-14 shrink-0 pt-px">Move</span>
                      <span className="text-xs text-[--muted-foreground] leading-relaxed">{meta.move}</span>
                    </div>
                  )}
                  {meta.why && (
                    <div className="flex items-start gap-2">
                      <span className="text-xs text-[--muted-foreground] w-14 shrink-0 pt-px">Why</span>
                      <span className="text-xs text-[--muted-foreground] leading-relaxed">{meta.why}</span>
                    </div>
                  )}
                </div>
              )}
            </>
          )}

          {/* Error */}
          {error && (
            <div className="shrink-0 text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
              {error}
            </div>
          )}

          {/* Copy */}
          <button
            onClick={handleCopy}
            disabled={!message}
            className="shrink-0 flex items-center gap-2 justify-center py-2.5 rounded-lg bg-[--muted] hover:bg-[--card] disabled:opacity-40 disabled:cursor-not-allowed text-[--foreground] text-sm font-medium transition-colors border border-[--border]"
          >
            {copied ? (
              <>
                <Check size={14} className="text-emerald-400" />
                Copied
              </>
            ) : (
              <>
                <Copy size={14} />
                Copy to clipboard
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

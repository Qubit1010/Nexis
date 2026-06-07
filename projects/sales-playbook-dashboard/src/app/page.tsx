"use client";

import { useState } from "react";
import { Copy, Check, Loader2, Zap, Linkedin, Instagram, X } from "lucide-react";

type Platform = "linkedin" | "instagram";
type Mode = "opener" | "followup" | "reply";
type TouchNumber = 2 | 3 | 4;

type Meta = { archetype: string; phase: string; tactic: string; why: string };

const ACCENT: Record<Platform, string> = {
  linkedin: "#0a66c2",
  instagram: "#e1306c",
};

const ARCHETYPES = [
  "auto",
  "Permission-Based",
  "Anti-Pitch",
  "Observation + Confession",
  "Loom-First",
  "Pattern from the field",
  "Quantified peer result",
];

const PHASE_STYLES: Record<string, string> = {
  Qualify: "bg-blue-500/15 text-blue-400 border border-blue-500/25",
  Open: "bg-sky-500/15 text-sky-400 border border-sky-500/25",
  Label: "bg-purple-500/15 text-purple-400 border border-purple-500/25",
  Deepen: "bg-indigo-500/15 text-indigo-400 border border-indigo-500/25",
  Proof: "bg-amber-500/15 text-amber-400 border border-amber-500/25",
  Warm: "bg-orange-500/15 text-orange-400 border border-orange-500/25",
  Pull: "bg-cyan-500/15 text-cyan-400 border border-cyan-500/25",
  Call: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/25",
};

const inputClass =
  "w-full rounded-lg bg-[--input] border border-[--border] text-[--foreground] placeholder:text-[--muted-foreground] text-sm px-3 py-2 focus:outline-none focus:ring-1 focus:ring-white/20";

const labelClass =
  "text-xs font-medium text-[--muted-foreground] uppercase tracking-wider mb-1.5 block";

const MODE_LABELS: Record<Mode, string> = {
  opener: "Cold Opener",
  followup: "Follow-up",
  reply: "Live Reply",
};

function charLimit(platform: Platform, mode: Mode): number {
  if (platform === "linkedin") return mode === "opener" ? 300 : 600;
  return 400;
}

export default function Home() {
  const [platform, setPlatform] = useState<Platform>("linkedin");
  const [mode, setMode] = useState<Mode>("opener");

  // Opener / Follow-up shared
  const [name, setName] = useState("");
  const [role, setRole] = useState("");
  const [company, setCompany] = useState("");
  const [signal, setSignal] = useState("");
  // Opener
  const [archetype, setArchetype] = useState("auto");
  // Follow-up
  const [touchNumber, setTouchNumber] = useState<TouchNumber>(2);
  const [previousMessage, setPreviousMessage] = useState("");
  const [showPrevious, setShowPrevious] = useState(false);
  // Reply
  const [conversation, setConversation] = useState("");
  const [profileLine, setProfileLine] = useState("");
  const [goal, setGoal] = useState("");

  // Output
  const [message, setMessage] = useState("");
  const [meta, setMeta] = useState<Meta | null>(null);

  // UI
  const [generating, setGenerating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const accent = ACCENT[platform];
  const limit = charLimit(platform, mode);
  const charCount = message.length;
  const over = charCount > limit;

  const roleLabel = platform === "linkedin" ? "Role / Headline" : "Bio";
  const rolePlaceholder =
    platform === "linkedin"
      ? "Founder & CEO at Loop & Co — scaling a social media agency"
      : "social agency owner | content + ops | building in public";

  function resetOutput() {
    setMessage("");
    setMeta(null);
    setError(null);
  }

  function touchLabel(n: TouchNumber): string {
    if (platform === "linkedin") {
      return n === 2 ? "DM 2 · Day 4" : n === 3 ? "DM 3 · Day 9" : "DM 4 · Day 16";
    }
    return n === 2 ? "Touch 2 · Day 3" : n === 3 ? "Touch 3 · Day 5" : "Touch 4 · Day 7-14";
  }

  const canGenerate =
    mode === "reply"
      ? conversation.trim() && profileLine.trim()
      : name.trim() && role.trim();

  async function handleGenerate() {
    setGenerating(true);
    resetOutput();
    try {
      const base = { platform, mode };
      const payload =
        mode === "reply"
          ? { ...base, conversation, profileLine, goal }
          : mode === "followup"
          ? { ...base, name, role, company, signal, touchNumber, previousMessage }
          : { ...base, name, role, company, signal, archetype };

      const res = await fetch("/api/draft", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Generation failed");
      setMessage(data.message);
      setMeta(data.meta ?? null);
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

  const basePhase = meta?.phase ? meta.phase.split(" ")[0] : "";

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-[--border] px-6 py-4 flex items-center gap-3 shrink-0">
        <div
          className="w-7 h-7 rounded-md flex items-center justify-center"
          style={{ backgroundColor: `${accent}33` }}
        >
          {platform === "linkedin" ? (
            <Linkedin size={14} style={{ color: accent }} />
          ) : (
            <Instagram size={14} style={{ color: accent }} />
          )}
        </div>
        <div>
          <h1 className="text-sm font-semibold text-[--foreground]">Sales Playbook Dashboard</h1>
          <p className="text-xs text-[--muted-foreground]">NexusPoint — drafts straight from the playbook</p>
        </div>
      </header>

      {/* Main */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel */}
        <div className="w-1/2 flex flex-col border-r border-[--border] p-6 gap-4 overflow-y-auto">
          {/* Platform toggle */}
          <div>
            <label className={labelClass}>Platform</label>
            <div className="flex gap-1 p-1 rounded-lg bg-[--muted]">
              {(["linkedin", "instagram"] as Platform[]).map((p) => {
                const active = platform === p;
                return (
                  <button
                    key={p}
                    onClick={() => {
                      setPlatform(p);
                      resetOutput();
                    }}
                    className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-colors flex items-center justify-center gap-1.5 ${
                      active ? "text-white" : "text-[--muted-foreground] hover:text-[--foreground]"
                    }`}
                    style={active ? { backgroundColor: ACCENT[p] } : undefined}
                  >
                    {p === "linkedin" ? <Linkedin size={13} /> : <Instagram size={13} />}
                    {p === "linkedin" ? "LinkedIn" : "Instagram"}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Mode toggle */}
          <div>
            <label className={labelClass}>Mode</label>
            <div className="flex gap-1 p-1 rounded-lg bg-[--muted]">
              {(["opener", "followup", "reply"] as Mode[]).map((m) => {
                const active = mode === m;
                return (
                  <button
                    key={m}
                    onClick={() => {
                      setMode(m);
                      resetOutput();
                    }}
                    className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-colors ${
                      active
                        ? "bg-[--card] text-[--foreground] border border-[--border]"
                        : "text-[--muted-foreground] hover:text-[--foreground]"
                    }`}
                  >
                    {MODE_LABELS[m]}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Opener / Follow-up shared fields */}
          {(mode === "opener" || mode === "followup") && (
            <>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className={labelClass}>Name *</label>
                  <input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Sarah Lin"
                    className={inputClass}
                  />
                </div>
                <div>
                  <label className={labelClass}>Company</label>
                  <input
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    placeholder="Loop & Co"
                    className={inputClass}
                  />
                </div>
              </div>

              <div>
                <label className={labelClass}>{roleLabel} *</label>
                <input
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  placeholder={rolePlaceholder}
                  className={inputClass}
                />
              </div>

              <div>
                <label className={labelClass}>Recent post / trigger signal</label>
                <textarea
                  value={signal}
                  onChange={(e) => setSignal(e.target.value)}
                  placeholder="Paste a recent post or trigger — highest-signal personalization input (e.g. 'posted about landing 3 new retainers and drowning in content ops')"
                  className={`${inputClass} resize-none h-20`}
                />
              </div>

              {mode === "opener" && (
                <div>
                  <label className={labelClass}>Opener archetype</label>
                  <select
                    value={archetype}
                    onChange={(e) => setArchetype(e.target.value)}
                    className={`${inputClass} cursor-pointer`}
                  >
                    {ARCHETYPES.map((a) => (
                      <option key={a} value={a}>
                        {a === "auto" ? "Auto-rotate (best fit for signal)" : a}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {mode === "followup" && (
                <>
                  <div>
                    <label className={labelClass}>Which {platform === "linkedin" ? "DM" : "touch"} *</label>
                    <div className="flex gap-2">
                      {([2, 3, 4] as TouchNumber[]).map((n) => {
                        const active = touchNumber === n;
                        return (
                          <button
                            key={n}
                            onClick={() => setTouchNumber(n)}
                            className={`flex-1 py-2 text-xs font-medium rounded-lg border transition-colors ${
                              active
                                ? "text-white"
                                : "bg-[--input] text-[--muted-foreground] border-[--border] hover:text-[--foreground]"
                            }`}
                            style={active ? { backgroundColor: accent, borderColor: accent } : undefined}
                          >
                            {touchLabel(n)}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  <div>
                    <button
                      onClick={() => setShowPrevious(!showPrevious)}
                      className="text-xs text-[--muted-foreground] hover:text-[--foreground] transition-colors flex items-center gap-1.5"
                    >
                      <span className="font-medium text-sm leading-none" style={{ color: accent }}>
                        {showPrevious ? "−" : "+"}
                      </span>
                      {showPrevious ? "Hide" : "Add"} previous message sent
                    </button>
                    {showPrevious && (
                      <textarea
                        value={previousMessage}
                        onChange={(e) => setPreviousMessage(e.target.value)}
                        placeholder="Paste the touch you already sent — avoids repeating the same angle or phrasing..."
                        className={`${inputClass} resize-none h-24 mt-2`}
                      />
                    )}
                  </div>
                </>
              )}
            </>
          )}

          {/* Reply fields */}
          {mode === "reply" && (
            <>
              <div>
                <label className={labelClass}>Conversation thread *</label>
                <textarea
                  value={conversation}
                  onChange={(e) => setConversation(e.target.value)}
                  placeholder={`Paste the full thread — both sides.\n\n[Me]: ...\n[Them]: ...`}
                  className={`${inputClass} resize-none h-48`}
                />
              </div>
              <div>
                <label className={labelClass}>Profile *</label>
                <input
                  value={profileLine}
                  onChange={(e) => setProfileLine(e.target.value)}
                  placeholder="Sarah Lin, founder of Loop & Co — 9-person social agency, content ops pain"
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Goal (optional)</label>
                <select
                  value={goal}
                  onChange={(e) => setGoal(e.target.value)}
                  className={`${inputClass} cursor-pointer`}
                >
                  <option value="">Auto-detect from conversation</option>
                  <option value="build rapport">Build rapport</option>
                  <option value="surface their pain">Surface their pain</option>
                  <option value="drop proof">Drop proof</option>
                  <option value="move to a call">Move to a call (Ops Teardown)</option>
                  <option value="keep it warm">Keep it warm</option>
                </select>
              </div>
            </>
          )}

          <button
            onClick={handleGenerate}
            disabled={generating || !canGenerate}
            className="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg text-white text-sm font-medium transition-opacity disabled:opacity-40 disabled:cursor-not-allowed hover:opacity-90"
            style={{ backgroundColor: accent }}
          >
            {generating ? (
              <>
                <Loader2 size={15} className="animate-spin" />
                Drafting...
              </>
            ) : (
              <>
                <Zap size={15} />
                Draft message
              </>
            )}
          </button>
        </div>

        {/* Right Panel */}
        <div className="w-1/2 flex flex-col p-6 gap-4">
          <div className="flex items-center justify-between shrink-0">
            <label className={labelClass}>Generated message</label>
            <div className="flex items-center gap-2">
              {message && (
                <span
                  className={`text-xs font-mono px-2 py-0.5 rounded border ${
                    over
                      ? "bg-red-500/15 text-red-400 border-red-500/25"
                      : "bg-emerald-500/15 text-emerald-400 border-emerald-500/25"
                  }`}
                >
                  {charCount} / {limit}
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
                {platform === "linkedin" ? (
                  <Linkedin size={36} className="mx-auto mb-3 opacity-15" />
                ) : (
                  <Instagram size={36} className="mx-auto mb-3 opacity-15" />
                )}
                <p>Your {MODE_LABELS[mode].toLowerCase()} will appear here</p>
                <p className="text-xs mt-1 opacity-50">Fill in the fields and click Draft message</p>
              </div>
            </div>
          )}

          {/* Loading */}
          {generating && (
            <div className="flex-1 flex items-center justify-center text-[--muted-foreground] text-sm gap-2">
              <Loader2 size={18} className="animate-spin" style={{ color: accent }} />
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

              {meta && (meta.archetype || meta.phase || meta.tactic || meta.why) && (
                <div className="shrink-0 border border-[--border] rounded-lg p-3 bg-[--card] flex flex-col gap-2">
                  {meta.archetype && (
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-[--muted-foreground] w-14 shrink-0">Archetype</span>
                      <span
                        className="text-xs font-medium px-2.5 py-0.5 rounded-full border"
                        style={{ backgroundColor: `${accent}26`, color: accent, borderColor: `${accent}40` }}
                      >
                        {meta.archetype}
                      </span>
                    </div>
                  )}
                  {meta.phase && (
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-[--muted-foreground] w-14 shrink-0">Phase</span>
                      <span
                        className={`text-xs font-medium px-2.5 py-0.5 rounded-full border ${
                          PHASE_STYLES[basePhase] ?? "bg-[--muted] text-[--muted-foreground] border-[--border]"
                        }`}
                      >
                        {meta.phase}
                      </span>
                    </div>
                  )}
                  {meta.tactic && (
                    <div className="flex items-start gap-2">
                      <span className="text-xs text-[--muted-foreground] w-14 shrink-0 pt-px">Tactic</span>
                      <span className="text-xs text-[--muted-foreground] leading-relaxed">{meta.tactic}</span>
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

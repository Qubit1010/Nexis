"use client";

import { useState } from "react";
import { Copy, Check, Loader2, Zap, MessageSquare, X } from "lucide-react";

type Scenario = "A" | "B";
type DmNumber = 2 | 3 | 4;

const PHASE_STYLES: Record<string, string> = {
  Qualify: "bg-blue-500/15 text-blue-400 border border-blue-500/25",
  Label: "bg-purple-500/15 text-purple-400 border border-purple-500/25",
  Proof: "bg-amber-500/15 text-amber-400 border border-amber-500/25",
  Pull: "bg-cyan-500/15 text-cyan-400 border border-cyan-500/25",
  Call: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/25",
};

const inputClass =
  "w-full rounded-lg bg-[--input] border border-[--border] text-[--foreground] placeholder:text-[--muted-foreground] text-sm px-3 py-2 focus:outline-none focus:ring-1 focus:ring-[#208ec7]/50";

const labelClass =
  "text-xs font-medium text-[--muted-foreground] uppercase tracking-wider mb-1.5 block";

export default function Home() {
  const [scenario, setScenario] = useState<Scenario>("A");

  // Scenario A
  const [name, setName] = useState("");
  const [role, setRole] = useState("");
  const [company, setCompany] = useState("");
  const [companySize, setCompanySize] = useState("");
  const [dmNumber, setDmNumber] = useState<DmNumber>(2);
  const [recentPost, setRecentPost] = useState("");
  const [previousDm, setPreviousDm] = useState("");
  const [showPreviousDm, setShowPreviousDm] = useState(false);

  // Scenario B
  const [conversation, setConversation] = useState("");
  const [profileLine, setProfileLine] = useState("");
  const [goal, setGoal] = useState("");

  // Output
  const [dm, setDm] = useState("");
  const [phase, setPhase] = useState("");
  const [tactic, setTactic] = useState("");

  // UI
  const [generating, setGenerating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const charCount = dm.length;

  function switchScenario(s: Scenario) {
    setScenario(s);
    setDm("");
    setPhase("");
    setTactic("");
    setError(null);
  }

  function clearOutput() {
    setDm("");
    setPhase("");
    setTactic("");
    setError(null);
  }

  async function handleGenerate() {
    setGenerating(true);
    setError(null);
    setDm("");
    setPhase("");
    setTactic("");

    try {
      const body =
        scenario === "A"
          ? { scenario, name, role, company, companySize, dmNumber, recentPost, previousDm }
          : { scenario, conversation, profileLine, goal };

      const res = await fetch("/api/draft", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Generation failed");

      setDm(data.dm);
      if (data.phase) setPhase(data.phase);
      if (data.tactic) setTactic(data.tactic);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setGenerating(false);
    }
  }

  async function handleCopy() {
    if (!dm) return;
    await navigator.clipboard.writeText(dm);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  const canGenerate =
    scenario === "A"
      ? name.trim() && role.trim() && company.trim()
      : conversation.trim() && profileLine.trim();

  // Extract base phase name for color lookup (e.g. "Qualify (peer track)" -> "Qualify")
  const basePhase = phase.split(" ")[0];

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-[--border] px-6 py-4 flex items-center gap-3 shrink-0">
        <div className="w-7 h-7 rounded-md bg-[#208ec7]/20 flex items-center justify-center">
          <MessageSquare size={14} className="text-[#208ec7]" />
        </div>
        <div>
          <h1 className="text-sm font-semibold text-[--foreground]">LinkedIn DM Responder</h1>
          <p className="text-xs text-[--muted-foreground]">NexusPoint — Outreach</p>
        </div>
      </header>

      {/* Main */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel */}
        <div className="w-1/2 flex flex-col border-r border-[--border] p-6 gap-4 overflow-y-auto">
          {/* Scenario toggle */}
          <div className="flex gap-1 p-1 rounded-lg bg-[--muted] shrink-0">
            {(["A", "B"] as Scenario[]).map((s) => (
              <button
                key={s}
                onClick={() => switchScenario(s)}
                className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-colors ${
                  scenario === s
                    ? "bg-[--card] text-[--foreground] border border-[--border]"
                    : "text-[--muted-foreground] hover:text-[--foreground]"
                }`}
              >
                {s === "A" ? "Sequence Follow-up" : "Reply Drafter"}
              </button>
            ))}
          </div>

          {/* Scenario A fields */}
          {scenario === "A" && (
            <>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className={labelClass}>Name *</label>
                  <input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Sarah Chen"
                    className={inputClass}
                  />
                </div>
                <div>
                  <label className={labelClass}>Company *</label>
                  <input
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    placeholder="Growlio"
                    className={inputClass}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className={labelClass}>Role *</label>
                  <input
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    placeholder="Co-founder & CEO"
                    className={inputClass}
                  />
                </div>
                <div>
                  <label className={labelClass}>Company size</label>
                  <input
                    value={companySize}
                    onChange={(e) => setCompanySize(e.target.value)}
                    placeholder="e.g. 4, 20, Series A"
                    className={inputClass}
                  />
                </div>
              </div>

              <div>
                <label className={labelClass}>Which DM *</label>
                <div className="flex gap-2">
                  {([2, 3, 4] as DmNumber[]).map((n) => (
                    <button
                      key={n}
                      onClick={() => setDmNumber(n)}
                      className={`flex-1 py-2 text-xs font-medium rounded-lg border transition-colors ${
                        dmNumber === n
                          ? "bg-[#208ec7]/15 text-[#208ec7] border-[#208ec7]/30"
                          : "bg-[--input] text-[--muted-foreground] border-[--border] hover:text-[--foreground]"
                      }`}
                    >
                      {n === 2 ? "DM 2 · Day 4" : n === 3 ? "DM 3 · Day 9" : "DM 4 · Day 16"}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className={labelClass}>Recent post or bio detail</label>
                <textarea
                  value={recentPost}
                  onChange={(e) => setRecentPost(e.target.value)}
                  placeholder="Any recent post, bio detail, or context to personalize the DM..."
                  className={`${inputClass} resize-none h-20`}
                />
              </div>

              <div>
                <button
                  onClick={() => setShowPreviousDm(!showPreviousDm)}
                  className="text-xs text-[--muted-foreground] hover:text-[--foreground] transition-colors flex items-center gap-1.5"
                >
                  <span className="text-[#208ec7] font-medium text-sm leading-none">
                    {showPreviousDm ? "−" : "+"}
                  </span>
                  {showPreviousDm ? "Hide" : "Add"} previous DM sent
                </button>
                {showPreviousDm && (
                  <textarea
                    value={previousDm}
                    onChange={(e) => setPreviousDm(e.target.value)}
                    placeholder="Paste the DM you already sent — avoids repeating the same phrasing..."
                    className={`${inputClass} resize-none h-24 mt-2`}
                  />
                )}
              </div>
            </>
          )}

          {/* Scenario B fields */}
          {scenario === "B" && (
            <>
              <div>
                <label className={labelClass}>Conversation thread *</label>
                <textarea
                  value={conversation}
                  onChange={(e) => setConversation(e.target.value)}
                  placeholder={`Paste the full conversation — both sides.\n\n[Me]: ...\n[Them]: ...`}
                  className={`${inputClass} resize-none h-52`}
                />
              </div>

              <div>
                <label className={labelClass}>Profile *</label>
                <input
                  value={profileLine}
                  onChange={(e) => setProfileLine(e.target.value)}
                  placeholder="e.g. James Tanaka, VP Operations at Inflect (40-person fintech, Series A, NYC)"
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
                  <option value="qualify">Qualify — surface their pain</option>
                  <option value="book a call">Book a call</option>
                  <option value="stay warm">Stay warm</option>
                </select>
              </div>
            </>
          )}

          <button
            onClick={handleGenerate}
            disabled={generating || !canGenerate}
            className="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium transition-colors"
          >
            {generating ? (
              <>
                <Loader2 size={15} className="animate-spin" />
                Drafting...
              </>
            ) : (
              <>
                <Zap size={15} />
                Draft DM
              </>
            )}
          </button>
        </div>

        {/* Right Panel */}
        <div className="w-1/2 flex flex-col p-6 gap-4">
          {/* Panel header */}
          <div className="flex items-center justify-between shrink-0">
            <label className={labelClass}>Generated DM</label>
            <div className="flex items-center gap-2">
              {dm && (
                <span
                  className={`text-xs font-mono px-2 py-0.5 rounded border ${
                    charCount > 1000
                      ? "bg-red-500/15 text-red-400 border-red-500/25"
                      : "bg-emerald-500/15 text-emerald-400 border-emerald-500/25"
                  }`}
                >
                  {charCount} / 1000
                </span>
              )}
              {dm && (
                <button
                  onClick={clearOutput}
                  className="text-[--muted-foreground] hover:text-[--foreground] transition-colors"
                >
                  <X size={14} />
                </button>
              )}
            </div>
          </div>

          {/* Empty state */}
          {!dm && !generating && !error && (
            <div className="flex-1 flex items-center justify-center text-[--muted-foreground] text-sm text-center">
              <div>
                <MessageSquare size={36} className="mx-auto mb-3 opacity-15" />
                <p>Your DM will appear here</p>
                <p className="text-xs mt-1 opacity-50">Fill in the fields and click Draft DM</p>
              </div>
            </div>
          )}

          {/* Loading state */}
          {generating && (
            <div className="flex-1 flex items-center justify-center text-[--muted-foreground] text-sm gap-2">
              <Loader2 size={18} className="animate-spin text-[#208ec7]" />
              Drafting your DM...
            </div>
          )}

          {/* Output */}
          {dm && (
            <>
              <textarea
                value={dm}
                onChange={(e) => setDm(e.target.value)}
                className="flex-1 resize-none rounded-lg bg-[--input] border border-[--border] text-[--foreground] text-sm p-4 focus:outline-none focus:ring-1 focus:ring-[#208ec7]/50 leading-relaxed"
              />

              {/* Scenario B metadata */}
              {scenario === "B" && (phase || tactic) && (
                <div className="shrink-0 border border-[--border] rounded-lg p-3 bg-[--card] flex flex-col gap-2">
                  {phase && (
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-[--muted-foreground] w-10 shrink-0">Phase</span>
                      <span
                        className={`text-xs font-medium px-2.5 py-0.5 rounded-full border ${
                          PHASE_STYLES[basePhase] ?? "bg-[--muted] text-[--muted-foreground] border-[--border]"
                        }`}
                      >
                        {phase}
                      </span>
                    </div>
                  )}
                  {tactic && (
                    <div className="flex items-start gap-2">
                      <span className="text-xs text-[--muted-foreground] w-10 shrink-0 pt-px">Tactic</span>
                      <span className="text-xs text-[--muted-foreground] leading-relaxed">{tactic}</span>
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

          {/* Copy button */}
          <button
            onClick={handleCopy}
            disabled={!dm}
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
                Copy to Clipboard
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

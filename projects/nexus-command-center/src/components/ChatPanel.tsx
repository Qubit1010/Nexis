import DOMPurify from "dompurify";
import { marked } from "marked";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  api,
  ApiError,
  streamChatMessage,
  type ChatMessage,
  type ChatThread,
  type ChatThreadSummary,
  type ChatToolUse,
} from "../api";
import { useStore } from "../store";

marked.setOptions({ gfm: true, breaks: true, async: false });

// Claude can echo file content into replies, so sanitize before injecting.
function md(text: string): { __html: string } {
  return { __html: DOMPurify.sanitize(marked.parse(text) as string) };
}

function ToolChips({ tools }: { tools: ChatToolUse[] }) {
  return (
    <div className="mb-1.5 flex flex-wrap gap-1.5">
      {tools.map((t, i) => (
        <span key={i} className="np-chip" style={{ cursor: "default" }} title={t.detail}>
          <span style={{ color: "var(--np-blue-300)" }}>{t.name}</span>
          <span className="max-w-48 truncate">{t.detail}</span>
        </span>
      ))}
    </div>
  );
}

function Message({ m }: { m: ChatMessage }) {
  if (m.role === "user") {
    return (
      <div className="flex justify-end">
        <div
          className="max-w-[75%] rounded-xl px-4 py-2.5 text-[13.5px]"
          style={{
            background: "rgba(32,142,199,0.14)",
            border: "1px solid rgba(32,142,199,0.35)",
            whiteSpace: "pre-wrap",
          }}
        >
          {m.text}
        </div>
      </div>
    );
  }
  return (
    <div className="max-w-[85%]">
      {m.tools?.length ? <ToolChips tools={m.tools} /> : null}
      <div className="chat-md text-[13.5px]" dangerouslySetInnerHTML={md(m.text)} />
      <div className="np-mono mt-1" style={{ color: "var(--np-fog)", fontSize: "10.5px" }}>
        {m.exit && m.exit !== "ok" ? `${m.exit} · ` : ""}${(m.cost_usd ?? 0).toFixed(4)}
      </div>
    </div>
  );
}

/**
 * Chat tab: freeform conversation with Nexis (the spawned claude runs from
 * the repo root, so it answers with full CLAUDE.md context). Advise-only —
 * chat profile has read tools only. Turns stream in over NDJSON and share
 * the global run mutex + ceiling with the deck and skill actions.
 */
export default function ChatPanel() {
  const deck = useStore((s) => s.deck);
  const setDeck = useStore((s) => s.setDeck);
  const [threads, setThreads] = useState<ChatThreadSummary[]>([]);
  const [active, setActive] = useState<ChatThread | null>(null);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [stream, setStream] = useState<{ text: string; tools: ChatToolUse[] } | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const loadThreads = useCallback(async () => {
    try {
      setThreads((await api.chatThreads()).threads);
    } catch {
      /* rail keeps last known list */
    }
  }, []);

  useEffect(() => {
    void loadThreads();
  }, [loadThreads]);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [active?.messages.length, stream?.text, stream?.tools.length]);

  const open = async (id: string) => {
    try {
      setActive(await api.chatThread(id));
      setErr(null);
    } catch {
      setErr("Failed to load thread.");
    }
  };

  const newChat = async () => {
    try {
      const t = await api.chatCreate();
      setActive(t);
      setErr(null);
      void loadThreads();
    } catch {
      setErr("Failed to create thread.");
    }
  };

  const remove = async (id: string) => {
    try {
      await api.chatDelete(id);
      if (active?.id === id) setActive(null);
      void loadThreads();
    } catch {
      /* already gone */
    }
  };

  const send = async () => {
    if (!active || !input.trim() || sending) return;
    const threadId = active.id;
    const text = input.trim();
    setInput("");
    setErr(null);
    setSending(true);
    setStream({ text: "", tools: [] });
    setActive((a) =>
      a ? { ...a, messages: [...a.messages, { role: "user", text, ts: new Date().toISOString() }] } : a,
    );
    try {
      await streamChatMessage(threadId, text, (e) => {
        if (e.type === "delta") setStream((s) => s && { ...s, text: s.text + e.text });
        else if (e.type === "tool") setStream((s) => s && { ...s, tools: [...s.tools, e] });
        else if (e.type === "done" && e.exit !== "ok") {
          setErr(e.exit === "killed" ? "Stopped." : (e.error ?? `run ${e.exit}`));
        }
      });
    } catch (e) {
      if (e instanceof ApiError) {
        const msg: Record<string, string> = {
          RUN_IN_PROGRESS: "Another run is in progress.",
          CEILING_LOCKED: "Console is locked — acknowledge the over-ceiling run first.",
          MESSAGE_TOO_LONG: "Message too long (8000 chars max).",
          UNKNOWN_THREAD: "This thread no longer exists.",
        };
        setErr(msg[e.code] ?? e.message);
      } else {
        setErr("Message failed.");
      }
    } finally {
      setSending(false);
      setStream(null);
      // Server truth after the turn: thread content, rail summaries, lock state.
      try {
        const [t, list, st] = await Promise.all([api.chatThread(threadId), api.chatThreads(), api.status()]);
        setActive((a) => (a?.id === threadId ? t : a));
        setThreads(list.threads);
        setDeck(st);
      } catch {
        /* next poll catches up */
      }
    }
  };

  const otherRun = !!deck?.running && !sending;
  const locked = !!deck?.locked;
  const canSend = !!active && !sending && !locked && !otherRun && input.trim().length > 0;

  return (
    <div className="flex h-full">
      <aside
        className="flex w-64 shrink-0 flex-col p-3"
        style={{ borderRight: "1px solid var(--np-hairline)" }}
      >
        <button className="np-btn-ghost mb-2 w-full" onClick={newChat}>
          + New chat
        </button>
        <div className="min-h-0 flex-1 space-y-1 overflow-y-auto">
          {threads.map((t) => (
            <div key={t.id} className="flex items-center gap-1">
              <button
                className="np-t min-w-0 flex-1 rounded-md px-2.5 py-1.5 text-left"
                style={{
                  border: "1px solid",
                  borderColor: active?.id === t.id ? "rgba(32,142,199,0.45)" : "transparent",
                  background: active?.id === t.id ? "rgba(32,142,199,0.08)" : "transparent",
                }}
                onClick={() => open(t.id)}
              >
                <div className="truncate text-[13px]">{t.title}</div>
                <div className="np-mono" style={{ color: "var(--np-fog)", fontSize: "10.5px" }}>
                  {t.message_count} msgs · ${t.total_cost_usd.toFixed(2)}
                </div>
              </button>
              <button
                className="np-t shrink-0 rounded px-1.5 text-[15px]"
                style={{ color: "var(--np-fog)", background: "transparent", border: "none", cursor: "pointer" }}
                title="Delete thread"
                onClick={() => remove(t.id)}
              >
                ×
              </button>
            </div>
          ))}
          {threads.length === 0 && <span className="np-mono opacity-50">no chats yet</span>}
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        {!active ? (
          <div className="flex h-full flex-col items-center justify-center gap-3">
            <span className="np-display text-xl">Talk to Nexis</span>
            <span className="text-[13px]" style={{ color: "var(--np-fog)" }}>
              Advise-only: it reads the whole system (repo + vault) but never edits or runs commands.
            </span>
            <button className="np-btn-primary" onClick={newChat}>
              Start a conversation
            </button>
          </div>
        ) : (
          <>
            <div ref={scrollRef} className="min-h-0 flex-1 space-y-4 overflow-y-auto p-5">
              {active.messages.map((m, i) => (
                <Message key={i} m={m} />
              ))}
              {stream && (
                <div className="max-w-[85%]">
                  {stream.tools.length > 0 && <ToolChips tools={stream.tools} />}
                  {stream.text ? (
                    <div className="chat-md text-[13.5px]" dangerouslySetInnerHTML={md(stream.text)} />
                  ) : (
                    <span className="text-[13px] italic" style={{ color: "var(--np-fog)" }}>
                      thinking…
                    </span>
                  )}
                  <span
                    className="np-pulse mt-1.5 inline-block h-2 w-2 rounded-full"
                    style={{ background: "var(--np-blue)" }}
                  />
                </div>
              )}
            </div>

            <div className="shrink-0 p-3" style={{ borderTop: "1px solid var(--np-hairline)" }}>
              {err && (
                <p className="mb-2 text-[13px]" style={{ color: "var(--np-err)" }}>
                  {err}
                </p>
              )}
              <div className="flex items-end gap-2">
                <textarea
                  className="np-input resize-none"
                  rows={2}
                  placeholder={
                    locked
                      ? "console locked — acknowledge the over-ceiling run"
                      : otherRun
                        ? "another run is in progress…"
                        : "Ask Nexis anything about the system…"
                  }
                  value={input}
                  disabled={locked || otherRun}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      void send();
                    }
                  }}
                />
                {sending ? (
                  <button className="np-btn-ghost" onClick={() => void api.chatStop(active.id)}>
                    Stop
                  </button>
                ) : (
                  <button className="np-btn-primary" disabled={!canSend} onClick={() => void send()}>
                    Send
                  </button>
                )}
              </div>
              <p className="np-mono mt-1.5" style={{ color: "var(--np-fog)", fontSize: "10.5px" }}>
                advise-only · read tools, no edits/shell · max ${(deck?.ceilings.chat ?? 0.5).toFixed(2)}
                /turn · Enter sends, Shift+Enter for a new line
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

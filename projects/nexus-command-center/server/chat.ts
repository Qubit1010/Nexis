import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import * as cfg from "./config.ts";
import { HttpError, startStreamRun, type StreamRunEvent } from "./spawn.ts";

export interface ChatToolUse {
  name: string;
  detail: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  text: string;
  ts: string;
  cost_usd?: number;
  exit?: string;
  tools?: ChatToolUse[];
}

export interface ChatThread {
  id: string;
  title: string;
  session_id: string | null; // CLI session for --resume continuity
  created: string;
  updated: string;
  messages: ChatMessage[];
}

/** Wire events streamed to the browser as NDJSON lines. */
export type ChatWireEvent =
  | { type: "delta"; text: string }
  | { type: "tool"; name: string; detail: string }
  | {
      type: "done";
      exit: string;
      cost_usd: number;
      duration_ms: number;
      text: string;
      error: string | null;
    };

// Threads live in one JSON file under runs/ (gitignored). Single process +
// sync fs keeps mutation race-free without a lock.
function loadThreads(): ChatThread[] {
  try {
    return (JSON.parse(fs.readFileSync(cfg.CHAT_FILE, "utf8")).threads as ChatThread[]) ?? [];
  } catch {
    return [];
  }
}

function saveThreads(threads: ChatThread[]): void {
  fs.mkdirSync(path.dirname(cfg.CHAT_FILE), { recursive: true });
  fs.writeFileSync(cfg.CHAT_FILE, JSON.stringify({ threads }, null, 2), "utf8");
}

export function listThreads() {
  return loadThreads()
    .map((t) => ({
      id: t.id,
      title: t.title,
      updated: t.updated,
      message_count: t.messages.length,
      total_cost_usd: t.messages.reduce((s, m) => s + (m.cost_usd ?? 0), 0),
    }))
    .sort((a, b) => (a.updated < b.updated ? 1 : -1));
}

export function createThread(): ChatThread {
  const threads = loadThreads();
  const now = new Date().toISOString();
  const t: ChatThread = {
    id: crypto.randomBytes(5).toString("hex"),
    title: "New chat",
    session_id: null,
    created: now,
    updated: now,
    messages: [],
  };
  threads.push(t);
  saveThreads(threads);
  return t;
}

export function getThread(id: string): ChatThread {
  const t = loadThreads().find((x) => x.id === id);
  if (!t) throw new HttpError(404, "UNKNOWN_THREAD", `unknown thread: ${id}`);
  return t;
}

export function deleteThread(id: string): void {
  const threads = loadThreads();
  const idx = threads.findIndex((x) => x.id === id);
  if (idx < 0) throw new HttpError(404, "UNKNOWN_THREAD", `unknown thread: ${id}`);
  threads.splice(idx, 1);
  saveThreads(threads);
}

// Which thread owns the in-flight turn (spawn's mutex already enforces one
// run globally; this scopes /stop to the right thread).
let activeTurn: { thread_id: string; stop: () => void } | null = null;

/**
 * Fire one chat turn. Throws HttpError 400/404/409/423 synchronously (before
 * any streaming), then emits wire events until a single terminal "done".
 */
export function startChatTurn(
  threadId: string,
  text: string,
  emit: (e: ChatWireEvent) => void,
): { run_id: string; started: string } {
  const clean = (text ?? "").trim();
  if (!clean) throw new HttpError(400, "EMPTY_MESSAGE", "message text required");
  if (clean.length > cfg.MAX_CHAT_CHARS) {
    throw new HttpError(400, "MESSAGE_TOO_LONG", `message exceeds ${cfg.MAX_CHAT_CHARS} chars`);
  }
  const thread = getThread(threadId); // 404s

  const usedResume = thread.session_id;
  const title = thread.messages.length === 0 ? clean.slice(0, 48) : thread.title;
  let deltaText = "";
  const turnTexts: string[] = [];
  const tools: ChatToolUse[] = [];

  const handle = startStreamRun(
    { id: `chat-${thread.id}`, label: `Chat: ${title.slice(0, 40)}`, prompt: clean, profile: "chat" },
    {
      resume: usedResume,
      onEvent: (e: StreamRunEvent) => {
        if (e.kind === "delta") {
          deltaText += e.text;
          emit({ type: "delta", text: e.text });
        } else if (e.kind === "turn_text") {
          turnTexts.push(e.text);
        } else if (e.kind === "tool") {
          tools.push({ name: e.name, detail: e.detail });
          emit({ type: "tool", name: e.name, detail: e.detail });
        } else if (e.kind === "final") {
          activeTurn = null;
          // Best answer text available: streamed deltas; else whole-turn text
          // blocks (no partial support); else the CLI's final result field.
          const answer = deltaText || turnTexts.join("\n\n") || e.result_text;
          const threads = loadThreads();
          const t = threads.find((x) => x.id === thread.id);
          if (t) {
            const now = new Date().toISOString();
            if (answer || e.exit !== "ok") {
              t.messages.push({
                role: "assistant",
                text: answer || (e.error ?? "(no reply)"),
                ts: now,
                cost_usd: e.cost_usd,
                exit: e.exit,
                ...(tools.length ? { tools } : {}),
              });
            }
            // Continuity: keep the session on success; drop one that failed to
            // resume (no output at all) so the next turn starts fresh.
            t.session_id =
              e.exit === "error" && usedResume && !deltaText && turnTexts.length === 0
                ? null
                : (e.session_id ?? t.session_id);
            t.updated = now;
            saveThreads(threads);
          }
          emit({
            type: "done",
            exit: e.exit,
            cost_usd: e.cost_usd,
            duration_ms: e.duration_ms,
            text: answer,
            error: e.error,
          });
        }
      },
    },
  );

  // Persist the user message right away (the run is committed now); the
  // assistant message lands on "final".
  {
    const threads = loadThreads();
    const t = threads.find((x) => x.id === thread.id);
    if (t) {
      const now = new Date().toISOString();
      t.title = title;
      t.messages.push({ role: "user", text: clean, ts: now });
      t.updated = now;
      saveThreads(threads);
    }
  }

  activeTurn = { thread_id: thread.id, stop: handle.stop };
  return { run_id: handle.run_id, started: handle.started };
}

export function stopChatTurn(threadId: string): { stopped: boolean } {
  if (activeTurn?.thread_id === threadId) {
    activeTurn.stop();
    return { stopped: true };
  }
  return { stopped: false };
}

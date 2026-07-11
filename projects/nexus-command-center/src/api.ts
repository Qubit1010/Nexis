/** Typed client for the server contract (architecture.md §6). */

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  group: string | number;
  summary: string;
  source_file: string;
  size: number;
  // client-side enrichment / d3 mutation:
  colorIndex?: number;
  x?: number;
  y?: number;
}

export interface GraphLink {
  source: string | GraphNode;
  target: string | GraphNode;
  relation: string;
  weight: number;
}

export interface GraphMeta {
  generated_at: string;
  counts: Record<string, number>;
}

export interface GraphData {
  meta: GraphMeta;
  nodes: GraphNode[];
  links: GraphLink[];
}

export interface Vitals {
  counts: Record<string, number>;
  last_sync: { ts: string; line: string } | null;
  last_vault_commit: { ts: string; message: string } | null;
  command_spend: { total_usd: number; runs: number };
  graph_generated_at: string | null;
}

export interface CommandInfo {
  id: string;
  label: string;
  description: string;
}

export interface ActionInput {
  name: string;
  label: string;
  placeholder?: string;
  multiline?: boolean;
}

export interface SkillActionInfo {
  id: string;
  label: string;
  description: string;
  inputs: ActionInput[];
  /** Skill folder name — lets graph skill-nodes map to their action. */
  skill?: string;
}

export interface BrainFreshness {
  last_ingest: string | null;
  days_since: number | null;
  stale: boolean;
  new_skills: string[];
  new_decisions: number;
}

export interface BrainDrift {
  in_sync: boolean;
  nexis_only: string[];
  vault_only: string[];
  differ: { file: string; newer: string }[];
}

export interface BrainStatus {
  freshness: BrainFreshness | null;
  drift: BrainDrift | null;
  critical_facts: string | null;
  wiki_log: string[];
  recent_decisions: string[];
}

export interface OpsRun {
  ts: string;
  label: string;
  profile: string;
  cost_usd: number;
  duration_ms: number;
  exit: string;
  result_file: string | null;
}

export interface OpsData {
  spend_by_day: { day: string; usd: number; runs: number }[];
  recent_runs: OpsRun[];
  recent_outputs: { ts: string; label: string; file: string }[];
}

export type ProjectStatus = "stopped" | "starting" | "running" | "exited";

export interface ProjectView {
  id: string;
  label: string;
  description: string;
  url: string;
  port: number;
  status: ProjectStatus;
  pid: number | null;
  started: string | null;
  exit_code: number | null;
  logs: string[];
}

export interface DeckLastRun {
  run_id: string;
  label: string;
  cost_usd: number;
  duration_ms: number;
  exit: "ok" | "timeout" | "error" | "killed";
  result_file: string | null;
  over_ceiling: boolean;
}

export interface DeckStatus {
  running: boolean;
  current: { run_id: string; label: string; started: string } | null;
  last: DeckLastRun | null;
  locked: boolean;
  ceilings: { read: number; act: number; chat: number };
}

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

export interface ChatThreadSummary {
  id: string;
  title: string;
  updated: string;
  message_count: number;
  total_cost_usd: number;
}

export interface ChatThread {
  id: string;
  title: string;
  session_id: string | null;
  created: string;
  updated: string;
  messages: ChatMessage[];
}

/** NDJSON events streamed by POST /api/chat/threads/:id/message. */
export type ChatStreamEvent =
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

export class ApiError extends Error {
  code: string;
  status: number;
  constructor(message: string, code: string, status: number) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(path, init);
  const body = await r.json().catch(() => null);
  if (!r.ok) {
    throw new ApiError(body?.error ?? r.statusText, body?.code ?? "UNKNOWN", r.status);
  }
  return body as T;
}

const json = { "Content-Type": "application/json" };

export const api = {
  graph: () => req<GraphData>("/api/graph"),
  vitals: () => req<Vitals>("/api/vitals"),
  commands: () => req<{ commands: CommandInfo[] }>("/api/commands"),
  run: (id: string) =>
    req<{ run_id: string; label: string; started: string }>("/api/command", {
      method: "POST",
      headers: json,
      body: JSON.stringify({ id, confirm: true }),
    }),
  status: () => req<DeckStatus>("/api/command/status"),
  ack: () =>
    req<{ locked: boolean }>("/api/command/ack", {
      method: "POST",
      headers: json,
      body: "{}",
    }),
  skillActions: () => req<{ actions: SkillActionInfo[] }>("/api/skill-actions"),
  brain: () => req<BrainStatus>("/api/brain"),
  ops: () => req<OpsData>("/api/ops"),
  scanGraph: () =>
    req<{ generated_at: string | null; counts: Record<string, number> }>("/api/graph/scan", {
      method: "POST",
      headers: json,
      body: "{}",
    }),
  runSkillAction: (id: string, inputs: Record<string, string>) =>
    req<{ run_id: string; label: string; started: string }>("/api/skill-action", {
      method: "POST",
      headers: json,
      body: JSON.stringify({ id, inputs, confirm: true }),
    }),
  projects: () => req<{ projects: ProjectView[] }>("/api/projects"),
  projectStart: (id: string) =>
    req<ProjectView>(`/api/projects/${id}/start`, { method: "POST", headers: json, body: "{}" }),
  projectStop: (id: string) =>
    req<ProjectView>(`/api/projects/${id}/stop`, { method: "POST", headers: json, body: "{}" }),
  openEditor: (id: string) =>
    req<{ ok: boolean }>(`/api/projects/${id}/open-editor`, { method: "POST", headers: json, body: "{}" }),
  chatThreads: () => req<{ threads: ChatThreadSummary[] }>("/api/chat/threads"),
  chatThread: (id: string) => req<ChatThread>(`/api/chat/threads/${id}`),
  chatCreate: () => req<ChatThread>("/api/chat/threads", { method: "POST", headers: json, body: "{}" }),
  chatDelete: (id: string) => req<{ ok: boolean }>(`/api/chat/threads/${id}`, { method: "DELETE" }),
  chatStop: (id: string) =>
    req<{ stopped: boolean }>(`/api/chat/threads/${id}/stop`, { method: "POST", headers: json, body: "{}" }),
};

/**
 * Send a chat message and consume the NDJSON stream. Resolves after the
 * terminal "done" event; throws ApiError for pre-stream failures (400/404/
 * 409/423 arrive as plain JSON before any streaming starts).
 */
export async function streamChatMessage(
  threadId: string,
  text: string,
  onEvent: (e: ChatStreamEvent) => void,
): Promise<void> {
  const r = await fetch(`/api/chat/threads/${threadId}/message`, {
    method: "POST",
    headers: json,
    body: JSON.stringify({ text }),
  });
  if (!r.ok) {
    const body = await r.json().catch(() => null);
    throw new ApiError(body?.error ?? r.statusText, body?.code ?? "UNKNOWN", r.status);
  }
  const reader = r.body?.getReader();
  if (!reader) throw new ApiError("no stream body", "NO_STREAM", 500);
  const dec = new TextDecoder();
  let buf = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    let i: number;
    while ((i = buf.indexOf("\n")) >= 0) {
      const line = buf.slice(0, i).trim();
      buf = buf.slice(i + 1);
      if (line) onEvent(JSON.parse(line) as ChatStreamEvent);
    }
  }
  if (buf.trim()) onEvent(JSON.parse(buf.trim()) as ChatStreamEvent);
}

/** d3 mutates link endpoints from id -> node object; normalize back to id. */
export function endpointId(v: string | GraphNode): string {
  return typeof v === "object" ? v.id : v;
}

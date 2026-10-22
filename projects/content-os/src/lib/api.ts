export class ApiError extends Error {
  status: number;
  code: string;
  constructor(status: number, code: string, message: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const res = await fetch(`/api${path}`, {
    method,
    headers: body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const text = await res.text();
  let data: any = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { error: text };
  }
  if (!res.ok) throw new ApiError(res.status, data?.code ?? "ERROR", data?.error ?? `HTTP ${res.status}`);
  return data as T;
}

export const api = {
  get: <T>(p: string) => request<T>("GET", p),
  post: <T>(p: string, body: unknown = {}) => request<T>("POST", p, body),
  patch: <T>(p: string, body: unknown) => request<T>("PATCH", p, body),
  put: <T>(p: string, body: unknown) => request<T>("PUT", p, body),
  del: <T>(p: string) => request<T>("DELETE", p),
  async upload<T>(p: string, form: FormData): Promise<T> {
    const res = await fetch(`/api${p}`, { method: "POST", body: form });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new ApiError(res.status, data.code ?? "ERROR", data.error ?? `HTTP ${res.status}`);
    return data as T;
  },
};

export const fileUrl = (absPath: string) => `/api/files?path=${encodeURIComponent(absPath)}`;

// ---- Shared types (mirrors the server rows) ----

export type Format = "linkedin_post" | "personal_blog" | "agency_blog" | "li_newsletter";
export const FORMATS: Format[] = ["linkedin_post", "personal_blog", "agency_blog", "li_newsletter"];
export const FORMAT_LABELS: Record<Format, string> = {
  linkedin_post: "LinkedIn post",
  personal_blog: "Personal blog",
  agency_blog: "Agency blog",
  li_newsletter: "Newsletter",
};

export interface Idea {
  id: string;
  title: string;
  summary: string | null;
  url: string | null;
  source: string;
  sourceRef: string | null;
  payloadJson: string | null;
  status: "inbox" | "shortlisted" | "used" | "archived";
  pillar: string | null;
  notes: string | null;
  seenCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface ItemSummary {
  id: string;
  ideaId: string | null;
  format: Format;
  channelId: string | null;
  title: string;
  brief: Record<string, any>;
  scheduledFor: string | null;
  status: string;
  currentVersionId: string | null;
  dependsOnItemId: string | null;
  approvedAt: string | null;
  publishedAt: string | null;
  publishedUrl: string | null;
  externalId: string | null;
  docUrl: string | null;
  error: string | null;
  createdAt: string;
  updatedAt: string;
  version?: { id: string; n: number; kind: string; title: string | null; status: string | null; fails: number; warns: number; createdAt: string } | null;
}

export interface Check {
  id: string;
  level: "pass" | "warn" | "fail";
  message: string;
}

export interface Version {
  id: string;
  n: number;
  kind: string;
  runId: string | null;
  bodyMd: string;
  meta: { title?: string; status?: string; blocked_reason?: string | null; rescue?: string | null; gate?: Record<string, unknown> | null; meta?: Record<string, any>; sources?: { url: string; title?: string | null }[]; notes?: string | null };
  files: { runDir?: string; main?: string; extra?: { name: string; path: string }[]; images?: string[] };
  checks: Check[];
  extraFiles: { name: string; content: string }[];
  feedback: string | null;
  createdAt: string;
}

export interface Run {
  id: string;
  jobId: string | null;
  itemId: string | null;
  model: string | null;
  status: string;
  startedAt: string;
  endedAt: string | null;
  durationMs: number | null;
  numTurns: number | null;
  costUsdEquiv: number | null;
  apiKeySource: string | null;
  error: string | null;
  live?: boolean;
  item?: { id: string; title: string; format: string } | null;
}

export interface Job {
  id: string;
  type: string;
  lane: string;
  itemId: string | null;
  automationId: string | null;
  status: string;
  dueAt: string;
  attempts: number;
  maxAttempts: number;
  lastError: string | null;
  createdAt: string;
  updatedAt: string;
  finishedAt: string | null;
}

export interface Channel {
  id: string;
  kind: "buffer" | "git_astro" | "manual_newsletter";
  format: Format;
  name: string;
  enabled: boolean;
  config: Record<string, any>;
}

export interface Asset {
  id: string;
  itemId: string;
  kind: string;
  localPath: string;
  publicUrl: string | null;
  alt: string | null;
}

export interface ItemDetail {
  item: ItemSummary;
  versions: Version[];
  runs: Run[];
  jobs: Job[];
  assets: Asset[];
  channel: Channel | null;
  idea: (Idea & { payload: Record<string, any> }) | null;
  dependsOn: ItemSummary | null;
  dependents: ItemSummary[];
  events: { id: number; ts: string; actor: string; type: string; data: any }[];
}

export interface Overview {
  attention: { reason: string; item: ItemSummary }[];
  byStatus: Record<string, number>;
  inbox: number;
  jobs: { queued: number; running: number; needsCheck: number };
  lanes: { running: Record<string, number>; capacity: Record<string, number> };
  rateLimit: { status: string; resetsAt: number | null; sevenDayUtilization?: number; fiveHourUtilization?: number } | null;
  cadence: Record<Format, number>;
  liveRuns: string[];
}

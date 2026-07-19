// Conversation memory via the Supabase REST API (PostgREST). Server-side only:
// the service-role key must never reach the client (no NEXT_PUBLIC_ vars here).
// Separate table from the sales-playbook `conversations` (Upwork stages/fields differ).
// ponytail: raw PostgREST fetch, swap to @supabase/supabase-js only if queries outgrow this.

const TABLE = "upwork_conversations";

export type UpworkStage =
  | "pre_hire"
  | "negotiating"
  | "active"
  | "delivered"
  | "reviewed"
  | "reactivation"
  | "dead";

export type Conversation = {
  id: number;
  identity: string;
  client_name: string;
  job_title: string;
  job_type: string;
  profile: string;
  situation: string;
  stage: UpworkStage;
  exchange_count: number;
  thread: string;
  last_draft: string;
  last_contact: string;
  updated_at: string;
};

function env(): { url: string; key: string } | null {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  return url && key ? { url: url.replace(/\/$/, ""), key } : null;
}

export function dbConfigured(): boolean {
  return env() !== null;
}

async function rest(
  method: string,
  query: string,
  body?: unknown,
  prefer?: string
): Promise<Conversation[]> {
  const cfg = env();
  if (!cfg) throw new Error("Supabase env not configured");
  const res = await fetch(`${cfg.url}/rest/v1/${TABLE}${query}`, {
    method,
    headers: {
      apikey: cfg.key,
      Authorization: `Bearer ${cfg.key}`,
      "Content-Type": "application/json",
      ...(prefer ? { Prefer: prefer } : {}),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Supabase ${res.status}: ${(await res.text()).slice(0, 300)}`);
  }
  const text = await res.text();
  return text.trim() ? JSON.parse(text) : [];
}

export function listConversations(): Promise<Conversation[]> {
  return rest("GET", "?order=updated_at.desc");
}

export async function getConversation(identity: string): Promise<Conversation | null> {
  const rows = await rest("GET", `?identity=eq.${encodeURIComponent(identity)}`);
  return rows[0] ?? null;
}

// Partial upsert: PATCH when the row exists so omitted fields keep their values,
// POST otherwise.
export async function upsertConversation(
  identity: string,
  fields: Partial<Omit<Conversation, "id" | "identity">>
): Promise<Conversation | null> {
  const rec = { ...fields, identity, updated_at: new Date().toISOString() };
  const match = `?identity=eq.${encodeURIComponent(identity)}`;
  const existing = await rest("GET", `${match}&select=id`);
  const rows = existing.length
    ? await rest("PATCH", match, rec, "return=representation")
    : await rest("POST", "", rec, "return=representation");
  return rows[0] ?? null;
}

export function deleteConversation(id: number): Promise<Conversation[]> {
  return rest("DELETE", `?id=eq.${id}`);
}

// --- identity + exchange counting --------------------------------------------

// One channel (Upwork), so identity is derived from whatever handle Aleem has:
// an Upwork profile/job URL (use the stable ~token), else a slug of the client
// name/label. Stable + collision-resistant enough for a personal pipeline.
export function normalizeIdentity(raw: string): string {
  const s = (raw ?? "").trim().toLowerCase();
  if (!s) return "";
  if (s.includes("upwork.com")) {
    const token = s.match(/~[a-z0-9]{6,}/); // ~01abcdef... profile/job id
    if (token) return token[0];
    const seg = s.match(/upwork\.com\/(?:freelancers|jobs|agencies|nx\/[^/]+)\/([^/?#]+)/);
    if (seg) return `upwork:${seg[1].replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "")}`;
  }
  // Plain name/label -> slug.
  return s.replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 80);
}

// An exchange = one CLIENT turn. Two formats supported:
// 1. The "[Me]: / [Them]:" prefix convention (explicit, preferred).
// 2. Raw pasted Upwork thread: a line counts as a new speaker turn only if it
//    "looks like a name" (short, all words capitalized, trailing timestamp
//    stripped first) or matches the known client name hint, and isn't Aleem.
//    Standalone timestamps / read receipts are skipped.
const SELF_NAMES = new Set(["aleem", "aleem ul hassan", "aleem hassan"]);

function stripTrailingTime(line: string): string {
  return line.replace(/\s+\d{1,2}[:.]\d{2}\s*([AaPp][Mm])?$/, "").trim();
}

function looksLikeName(line: string): boolean {
  const stripped = stripTrailingTime(line);
  if (!stripped || stripped.length > 40) return false;
  const words = stripped.split(/\s+/);
  return words.every((w) => /^[A-Z][A-Za-z'-]*$/.test(w));
}

export function countExchanges(thread: string, contactHint?: string): number {
  const text = thread ?? "";
  const bracketCount = (text.match(/^\s*\[?(them|client|prospect)\b/gim) ?? []).length;
  if (bracketCount > 0 || /^\s*\[?me\]?\s*:/im.test(text)) return bracketCount;

  const hint = (contactHint ?? "").trim().toLowerCase();
  let count = 0;
  for (const rawLine of text.split("\n")) {
    const line = stripTrailingTime(rawLine.trim());
    if (!line) continue;
    const lower = line.toLowerCase();
    const isName = looksLikeName(rawLine) || (hint !== "" && lower === hint);
    if (isName && !SELF_NAMES.has(lower)) count++;
  }
  return count;
}

// Supabase via raw PostgREST (pattern: projects/upwork-reply-dashboard/src/lib/db.ts).
// Server-side only: the service-role key never reaches the browser.

export type Json = Record<string, unknown>;

export type Business = {
  slug: string; token: string; code: string; sector: "healthcare" | "food" | "education"; name: string;
  profile: Profile; xray: Xray | null; site: { posts: { en: string[]; ur: string[] } } | null;
  roi: RoiDefaults | null; health: Health | null; created_at: string; expires_at: string;
};
export type Profile = {
  facts: { name: string; category: string | null; address: string | null; neighborhood: string | null; city?: string | null;
    hours: { day: string; hours: string }[]; extras: string[]; rating: number | null; reviews: number | null;
    maps_url: string; location?: { lat: number; lng: number } };
  about: string; sector: string; services_sample: string[]; questions: { key: string; ask: string }[];
  warm_when: string; unqualified_when: string; action: string; demo_hint: string;
  fallback_reply: { en: string; ur: string };
};
export type Theme = { theme_en: string; theme_ur: string; count: number; quotes: string[] };
export type Xray = {
  summary_en: string; summary_ur: string; complaints: Theme[]; praise: Theme[];
  fixes: { en: string; ur: string }[]; faq: { en: string; ur: string }[];
  stats: { analysed: number; with_text: number; avg: number | null; recent_avg: number | null;
    mix: Record<string, number>; owner_reply_pct: number; newest: string | null; oldest: string | null };
};
export type RoiDefaults = { missed_per_week: number; ticket: number; recover_pct: number;
  ticket_label: { en: string; ur: string }; missed_label: { en: string; ur: string } };
export type Health = { score: number; items: { key: string; ok: boolean; weight: number; en: string; ur: string }[] };

export type Conversation = { id: string; slug: string; channel: string; visitor: string; stage: string | null;
  summary: string | null; answers: { key: string; value: string }[] | null; action: Action | null;
  handoff: boolean; created_at: string; last_at: string; staff_mode?: boolean; assigned_to?: string | null; booking_context?: Record<string, string> | null };
export type Action = { type: string; details: { key: string; value: string }[] };
export type Message = { id: number; conversation_id: string; role: "customer" | "business"; content: string;
  source: string | null; latency_ms: number | null; at: string; cards?: import("./healthcare-types.ts").Choice[] | null };

function cfg() {
  const url = process.env.SUPABASE_URL, key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) throw new Error("Supabase env not configured");
  return { url: url.replace(/\/$/, ""), key };
}

export async function rest<T = Json>(method: string, path: string, body?: unknown, prefer?: string): Promise<T[]> {
  const { url, key } = cfg();
  const res = await fetch(`${url}/rest/v1/${path}`, {
    method,
    headers: { apikey: key, Authorization: `Bearer ${key}`, "Content-Type": "application/json",
      ...(prefer ? { Prefer: prefer } : {}) },
    body: body === undefined ? undefined : JSON.stringify(body),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Supabase ${method} ${path.split("?")[0]} ${res.status}: ${(await res.text()).slice(0, 200)}`);
  const text = await res.text();
  return text ? (JSON.parse(text) as T[]) : [];
}

export async function getBusiness(slug: string): Promise<Business | null> {
  const rows = await rest<Business>("GET", `demo_businesses?slug=eq.${encodeURIComponent(slug)}&limit=1`);
  return rows[0] ?? null;
}

export async function getBusinessByCode(code: string): Promise<Business | null> {
  const rows = await rest<Business>("GET", `demo_businesses?code=eq.${encodeURIComponent(code.toUpperCase())}&limit=1`);
  return rows[0] ?? null;
}

export function authorised(b: Business | null, token: string | null): b is Business {
  return !!b && !!token && token === b.token;
}

export function expired(b: Business): boolean {
  return new Date(b.expires_at).getTime() < Date.now();
}

export async function logEvent(slug: string, kind: string, detail?: Json) {
  try { await rest("POST", "demo_events", { slug, kind, detail: detail ?? null }, "return=minimal"); } catch { /* never block on analytics */ }
}

export async function getOrCreateConversation(slug: string, channel: string, visitor: string): Promise<Conversation> {
  const q = `demo_conversations?slug=eq.${encodeURIComponent(slug)}&channel=eq.${channel}&visitor=eq.${encodeURIComponent(visitor)}&limit=1`;
  const found = await rest<Conversation>("GET", q);
  if (found[0]) return found[0];
  const made = await rest<Conversation>("POST", "demo_conversations?on_conflict=slug,channel,visitor",
    { slug, channel, visitor }, "resolution=merge-duplicates,return=representation");
  await logEvent(slug, "chat_start", { channel });
  return made[0];
}

export async function latestConversationForVisitor(visitor: string): Promise<Conversation | null> {
  const rows = await rest<Conversation>("GET", `demo_conversations?visitor=eq.${encodeURIComponent(visitor)}&order=last_at.desc&limit=1`);
  return rows[0] ?? null;
}

export async function transcript(conversationId: string): Promise<Message[]> {
  return (await rest<Message>("GET", `demo_messages?conversation_id=eq.${conversationId}&order=id.desc&limit=120`)).reverse();
}

export async function addMessage(m: Omit<Message, "id" | "at">) {
  await rest("POST", "demo_messages", m, "return=minimal");
}

export async function updateConversation(id: string, patch: Partial<Conversation>) {
  await rest("PATCH", `demo_conversations?id=eq.${id}`, { ...patch, last_at: new Date().toISOString() }, "return=minimal");
}

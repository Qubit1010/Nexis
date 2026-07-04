// Conversation memory via the Supabase REST API (PostgREST). Server-side only:
// the service-role key must never reach the client (no NEXT_PUBLIC_ vars here).
// ponytail: raw PostgREST fetch, swap to @supabase/supabase-js only if queries
// outgrow these three endpoints.

export type Conversation = {
  id: number;
  channel: "linkedin" | "instagram" | "facebook";
  identity: string;
  name: string;
  profile: string;
  stage: string;
  exchange_count: number;
  meeting_status: "none" | "asked" | "booked" | "declined" | "ghosted";
  last_contact: string;
  thread: string;
  last_draft: string;
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
  const res = await fetch(`${cfg.url}/rest/v1/conversations${query}`, {
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

export async function getConversation(
  channel: string,
  identity: string
): Promise<Conversation | null> {
  const rows = await rest(
    "GET",
    `?channel=eq.${channel}&identity=eq.${encodeURIComponent(identity)}`
  );
  return rows[0] ?? null;
}

// Partial upsert, same semantics as convo.py: PATCH when the row exists so
// omitted fields keep their values, POST otherwise.
export async function upsertConversation(
  channel: string,
  identity: string,
  fields: Partial<Omit<Conversation, "id" | "channel" | "identity">>
): Promise<Conversation | null> {
  const rec = { ...fields, channel, identity, updated_at: new Date().toISOString() };
  const match = `?channel=eq.${channel}&identity=eq.${encodeURIComponent(identity)}`;
  const existing = await rest("GET", `${match}&select=id`);
  const rows = existing.length
    ? await rest("PATCH", match, rec, "return=representation")
    : await rest("POST", "", rec, "return=representation");
  return rows[0] ?? null;
}

export function deleteConversation(id: number): Promise<Conversation[]> {
  return rest("DELETE", `?id=eq.${id}`);
}

// --- identity + exchange counting; keep in sync with convo.py -----------------

const IG_SYSTEM = new Set([
  "p", "reel", "reels", "tv", "explore", "stories", "live", "popular",
  "accounts", "direct", "about", "developer", "legal",
]);

export function normalizeIdentity(channel: string, raw: string): string {
  const lower = (raw ?? "").trim().toLowerCase();
  if (!lower) return "";
  if (channel === "instagram") {
    let h = lower;
    if (lower.includes("instagram.com")) {
      h = lower.match(/instagram\.com\/([^/?#]+)/)?.[1] ?? "";
    }
    h = h.replace(/^@/, "").replace(/\/+$/, "").split("?")[0];
    return !h || IG_SYSTEM.has(h) ? "" : h;
  }
  if (channel === "linkedin") {
    if (lower.includes("linkedin.com")) {
      const m = lower.match(/linkedin\.com\/in\/([^/?#]+)/);
      return m ? m[1].replace(/\/+$/, "") : "";
    }
    return lower.replace(/^@/, "").replace(/\/+$/, "");
  }
  if (lower.includes("facebook.com")) {
    const id = lower.match(/[?&]id=(\d+)/);
    if (id) return `id:${id[1]}`;
    const slug = lower.match(/facebook\.com\/([^/?#]+)/)?.[1]?.replace(/\/+$/, "") ?? "";
    return ["profile.php", "groups", "people", "pages"].includes(slug) ? "" : slug;
  }
  return lower.replace(/^@/, "").replace(/\/+$/, "");
}

// An exchange = one prospect turn. Two formats supported:
// 1. The "[Me]: / [Them]:" prefix convention (explicit, preferred).
// 2. Raw copy-pasted DM exports: scan line by line, and treat a line as a new
//    speaker turn only if it "looks like a name" (short, no digits/sentence
//    punctuation, every word capitalized, trailing timestamp stripped first
//    since some exports - LinkedIn - put "Name   10:33 PM" on one line) OR it
//    exactly matches the known contact's handle (some IG handles are plain
//    lowercase, e.g. "hupru", so the Title-Case check alone would miss them).
//    NOT just any line after a blank line, since a single message can have
//    its own paragraph breaks (which would otherwise be miscounted as extra
//    turns) and exports often have standalone timestamp/read-receipt lines
//    ("05:38", "Seen 23m ago") mixed in. Aleem is the one constant name
//    across every conversation (the lead's name/handle varies), so any
//    recognized name line that isn't his is a prospect turn. Keep SELF_NAMES
//    + this fallback in sync with count_exchanges() in convo.py.
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
  const bracketCount = (text.match(/^\s*\[?(them|prospect)\b/gim) ?? []).length;
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

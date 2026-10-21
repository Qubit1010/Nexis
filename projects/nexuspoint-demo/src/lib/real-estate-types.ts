// Pure real-estate logic shared by the server, the chat flow, the UI and the unit tests:
// types, pipeline rules (mirroring sql/real_estate_schema.sql), site-visit slots, PKR crore/lakh
// formatting, buyer-message parsing and manager statistics. No I/O here.
import { dayAfter, localDate } from "./healthcare-types.ts";

export type ReRole = "buyer" | "agent" | "manager";
export type Stage = "new" | "qualified" | "visit_booked" | "negotiating" | "won" | "lost";
export type Source = "chat" | "website" | "facebook" | "zameen" | "walk_in" | "referral" | "phone";
export type Agent = { id: string; name: string; name_ur: string; title: string; areas: string; active: boolean };
export type Listing = {
  id: string; code: string; title: string; title_ur: string; kind: "plot" | "house" | "apartment" | "commercial" | "file";
  society: string; society_ur: string; block: string; size_value: number; size_unit: "marla" | "kanal" | "sqft";
  beds: number | null; baths: number | null; price: number; status: "available" | "reserved" | "sold";
  features: string[]; description: string; description_ur: string; art: string;
};
export type Buyer = { id: string; visitor: string; name: string; overseas: boolean; country: string; created_at: string };
export type HistoryItem = { kind: string; text: string; at: string };
export type Lead = {
  id: string; buyer_id: string; source: Source; stage: Stage; budget: number | null; area: string; size: string; kind: string;
  timeline: string; overseas: boolean | null; country: string; listing_id: string | null; agent_id: string | null;
  conversation_id: string | null; summary: string; notes: string; lost_reason: string; history: HistoryItem[];
  created_at: string; first_reply_at: string | null; updated_at: string;
};
export type Visit = {
  id: string; lead_id: string; buyer_id: string; agent_id: string; listing_id: string | null; starts_at: string; ends_at: string;
  status: "confirmed" | "completed" | "cancelled" | "no_show"; notes: string; source: string; created_at: string;
};
export type ReSettings = { open_min: number; close_min: number; visit_minutes: number; seeded?: boolean };
export type Busy = Pick<Visit, "agent_id" | "starts_at" | "ends_at" | "status">;
export type ReState = {
  role: ReRole; city: string; buyer: Buyer; buyers: Buyer[]; agents: Agent[]; listings: Listing[]; leads: Lead[]; visits: Visit[];
  busy: Busy[]; settings: ReSettings; conversations: import("./healthcare-types.ts").ClinicConversation[];
  activity: { kind: string; at: string; detail: Record<string, unknown> }[]; server_time: string; expires_at: string;
};

export const STAGES: Stage[] = ["new", "qualified", "visit_booked", "negotiating", "won", "lost"];
export const stageLabel: Record<Stage, { en: string; ur: string }> = {
  new: { en: "New", ur: "نئی" }, qualified: { en: "Qualified", ur: "جانچ شدہ" }, visit_booked: { en: "Visit booked", ur: "وزٹ بک" },
  negotiating: { en: "Negotiating", ur: "بات چیت" }, won: { en: "Won", ur: "سودا مکمل" }, lost: { en: "Lost", ur: "ضائع" },
};
export const sourceLabel: Record<Source, { en: string; ur: string }> = {
  chat: { en: "WhatsApp assistant", ur: "واٹس ایپ اسسٹنٹ" }, website: { en: "Website form", ur: "ویب سائٹ فارم" },
  facebook: { en: "Facebook lead form", ur: "فیس بک فارم" }, zameen: { en: "Zameen enquiry", ur: "زمین انکوائری" },
  walk_in: { en: "Walk-in", ur: "دفتر آمد" }, referral: { en: "Referral", ur: "حوالہ" }, phone: { en: "Phone call", ur: "فون کال" },
};

const MOVES: Record<Stage, Stage[]> = {
  new: ["qualified", "lost"], qualified: ["visit_booked", "negotiating", "lost"], visit_booked: ["qualified", "negotiating", "lost"],
  negotiating: ["won", "lost", "visit_booked"], won: [], lost: ["new"],
};
/** Same transition table as demo_re_action('stage'). */
export function canMove(from: Stage, to: Stage): boolean {
  return MOVES[from].includes(to);
}
export function nextStages(from: Stage): Stage[] {
  return MOVES[from];
}

// ---------------------------------------------------------------- money
const CRORE = 10_000_000, LAKH = 100_000;
const trim = (n: number) => (Math.round(n * 100) / 100).toString();
/** PKR in the units Pakistani buyers use: crore above one crore, lakh above one lakh. */
export function formatPkr(n: number | null | undefined, lang: "en" | "ur" = "en"): string {
  if (n == null || !Number.isFinite(n)) return lang === "ur" ? "درج نہیں" : "Not given";
  if (n >= CRORE) return lang === "ur" ? `${trim(n / CRORE)} کروڑ روپے` : `PKR ${trim(n / CRORE)} crore`;
  if (n >= LAKH) return lang === "ur" ? `${trim(n / LAKH)} لاکھ روپے` : `PKR ${trim(n / LAKH)} lakh`;
  return lang === "ur" ? `${n.toLocaleString("en-US")} روپے` : `PKR ${n.toLocaleString("en-US")}`;
}

// ---------------------------------------------------------------- message parsing
const URDU_DIGITS = "۰۱۲۳۴۵۶۷۸۹";
const toAscii = (t: string) => t.replace(/[۰-۹]/g, (d) => String(URDU_DIGITS.indexOf(d)));
// Number words buyers actually type, in Roman Urdu and Urdu script. \b does not work for Urdu
// letters, so Urdu words are bounded by "not another Urdu letter" instead.
const w = (roman: string, urdu: string) => new RegExp(`\\b(?:${roman})\\b|(?<![\\u0600-\\u06FF])(?:${urdu})(?![\\u0600-\\u06FF])`, "i");
const WORDS: [RegExp, number][] = [
  [w("dhai|dhaai|adhai", "ڈھائی|اڑھائی"), 2.5], [w("derh|dairh|deirh", "ڈیڑھ"), 1.5], [w("sawa", "سوا"), 1.25],
  [w("ek|aik|one", "ایک"), 1], [w("do|two", "دو"), 2], [w("teen|three", "تین"), 3], [w("char|chaar|four", "چار"), 4],
  [w("panch|paanch|five", "پانچ"), 5], [w("saat|seven", "سات"), 7], [w("aath|eight", "آٹھ"), 8], [w("das|ten", "دس"), 10],
  [w("barah|twelve", "بارہ"), 12], [w("bees|twenty", "بیس"), 20], [w("pachas|fifty", "پچاس"), 50],
];
function wordNumber(t: string): number | null {
  for (const [re, n] of WORDS) if (re.test(t)) return n;
  return null;
}
const UNIT_CRORE = "crore|crores|cr|karor|karore|کروڑ";
const UNIT_LAKH = "lakh|lakhs|lac|lacs|laakh|لاکھ";
const UNIT_MILLION = "million|m(?=\\b)";

/** Budget ceiling in PKR from "2.5 crore", "85 lakh", "1.2cr", "ڈھائی کروڑ", "2 to 3 crore". */
export function parseBudget(text: string): number | null {
  const t = toAscii(text.toLowerCase().replace(/,/g, ""));
  const values: number[] = [];
  const re = new RegExp(`(\\d+(?:\\.\\d+)?)\\s*(?:-|to|se|سے)?\\s*(\\d+(?:\\.\\d+)?)?\\s*(${UNIT_CRORE}|${UNIT_LAKH}|${UNIT_MILLION})`, "gi");
  for (const m of t.matchAll(re)) {
    const n = Math.max(Number(m[1]), Number(m[2] ?? 0));
    const unit = m[3];
    const mult = new RegExp(`^(${UNIT_CRORE})$`).test(unit) ? CRORE : new RegExp(`^(${UNIT_LAKH})$`).test(unit) ? LAKH : 1_000_000;
    values.push(n * mult);
  }
  if (!values.length) {
    const word = new RegExp(`([^\\d]{0,14})\\s*(${UNIT_CRORE}|${UNIT_LAKH})`, "i").exec(t);
    if (word) {
      const n = wordNumber(word[1]) ?? 1;
      values.push(n * (new RegExp(UNIT_CRORE).test(word[2]) ? CRORE : LAKH));
    }
  }
  const best = values.length ? Math.max(...values) : null;
  return best != null && best >= LAKH && best <= 100_000_000_000 ? Math.round(best) : null;
}

/** "10 marla", "1 kanal", "1200 sq ft", "دس مرلہ". */
export function parseSize(text: string): { value: number; unit: "marla" | "kanal" | "sqft"; label: string } | null {
  const t = toAscii(text.toLowerCase());
  const unitOf = (u: string) => /kanal|کنال/.test(u) ? "kanal" : /marla|مرلہ|مرلے/.test(u) ? "marla" : "sqft";
  const m = /(\d+(?:\.\d+)?)\s*(marla|marlay|marle|kanal|kanals|sq\.?\s*ft|sqft|square\s*feet|sq\s*feet|مرلہ|مرلے|کنال|مربع فٹ)/i.exec(t);
  let value: number | null = null, unit: "marla" | "kanal" | "sqft" | null = null;
  if (m) { value = Number(m[1]); unit = unitOf(m[2]); }
  else {
    const w = /([^\d]{0,12})\s*(marla|kanal|مرلہ|مرلے|کنال)/i.exec(t);
    if (w) { value = wordNumber(w[1]) ?? (unitOf(w[2]) === "kanal" ? 1 : null); unit = unitOf(w[2]); }
  }
  if (value == null || unit == null || value <= 0 || value > 100000) return null;
  return { value, unit, label: `${trim(value)} ${unit === "sqft" ? "sq ft" : unit}` };
}

export function parseKind(text: string): Listing["kind"] | null {
  const t = text.toLowerCase();
  if (/\b(file|files)\b|فائل/.test(t)) return "file";
  if (/\b(apartment|flat|penthouse|studio)\b|اپارٹمنٹ|فلیٹ/.test(t)) return "apartment";
  if (/\b(shop|commercial|office space|showroom|plaza)\b|دکان|کمرشل/.test(t)) return "commercial";
  if (/\b(house|home|villa|ghar|makan|bungalow)\b|گھر|مکان|ولا/.test(t)) return "house";
  if (/\b(plot|plots|zameen|land)\b|پلاٹ|زمین/.test(t)) return "plot";
  return null;
}

// Societies and sectors buyers name. Extra names come from the demo's own listings.
const AREAS: [RegExp, string][] = [
  [/\b(dha|defen[cs]e)\b|ڈی ایچ اے/i, "DHA"], [/\bbahria\b|بحریہ/i, "Bahria Town"], [/\bgulberg\b|گلبرگ/i, "Gulberg Greens"],
  [/\bb[\s-]?17\b|multi ?gardens?|بی ?17|بی سترہ/i, "B-17"], [/\btop ?city\b|ٹاپ سٹی/i, "Top City-1"], [/\bpark ?view\b|پارک ویو/i, "Park View City"],
  [/\bcapital smart\b|سمارٹ سٹی/i, "Capital Smart City"], [/\bfaisal (town|hills)\b|فیصل ٹاؤن/i, "Faisal Town"],
  [/\bjinnah town\b|جناح ٹاؤن/i, "Jinnah Town"], [/\bsamungli\b|سمنگلی/i, "Samungli Housing Scheme"], [/\bchiltan\b|چلتن/i, "Chiltan Housing Scheme"],
  [/\bmodel town\b|ماڈل ٹاؤن/i, "Model Town"], [/\bshahbaz town\b|شہباز ٹاؤن/i, "Shahbaz Town"],
];
export function parseArea(text: string, known: string[] = []): string | null {
  const t = toAscii(text);
  for (const name of known) {
    const head = name.split(/[\s(]/)[0];
    if (head.length >= 4 && new RegExp(`\\b${head.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`, "i").test(t)) return name;
  }
  const phase = /\bphase[\s-]*(\d{1,2}|i{1,3}|iv|v|vi{0,3})\b|فیز\s*(\d{1,2}|ٹو|ون|تھری)/i.exec(t);
  const phaseNo = phase ? (phase[1] ?? ({ "ٹو": "2", "ون": "1", "تھری": "3" } as Record<string, string>)[phase[2]] ?? phase[2]).toUpperCase() : null;
  // Buyers often name two options ("Gulberg ya DHA phase 2"); keep both, in the order they wrote them.
  const hits = AREAS.map(([re, name]) => ({ i: t.search(re), name })).filter((h) => h.i >= 0).sort((a, b) => a.i - b.i)
    .map((h) => phaseNo && /DHA|Bahria/.test(h.name) ? `${h.name} Phase ${phaseNo}` : h.name);
  if (hits.length) return [...new Set(hits)].slice(0, 2).join(" or ");
  const sector = /\b([DEFGHI])[\s-]?(\d{1,2})(?:\/(\d))?\b/i.exec(t);
  if (sector && Number(sector[2]) >= 5 && Number(sector[2]) <= 18) return `${sector[1].toUpperCase()}-${sector[2]}${sector[3] ? "/" + sector[3] : ""}`;
  return null;
}

export function parseTimeline(text: string): string | null {
  const t = toAscii(text.toLowerCase());
  if (/\b(just looking|exploring|browsing|not sure|no hurry|abhi nahi)\b|صرف دیکھ رہا|جلدی نہیں/.test(t)) return "Exploring, no fixed date";
  if (/\b(immediately|asap|right away|urgent|this week|is hafte|foran|fauran)\b|فوراً|فوری|اسی ہفتے/.test(t)) return "Ready now";
  const months = /(\d{1,2})\s*(?:-|to|se|یا|سے)?\s*(\d{1,2})?\s*(months?|mahin[ey]|maheen[ey]|مہینے|ماہ)/.exec(t);
  if (months) return months[2] ? `${months[1]}-${months[2]} months` : `${months[1]} month${months[1] === "1" ? "" : "s"}`;
  if (/(do|دو)\s*(teen|تین)\s*(mahin|مہینے)/.test(t)) return "2-3 months";
  if (/\b(next month|agle mahine)\b|اگلے مہینے/.test(t)) return "Next month";
  if (/\b(this year|is saal)\b|اس سال/.test(t)) return "This year";
  if (/\b(next year|agle saal)\b|اگلے سال/.test(t)) return "Next year";
  const month = /\b(january|february|march|april|may|june|july|august|september|october|november|december)\b|جنوری|فروری|مارچ|اپریل|مئی|جون|جولائی|اگست|ستمبر|اکتوبر|نومبر|دسمبر/.exec(t);
  if (month) return `By ${month[0].replace(/^./, (c) => c.toUpperCase())}`;
  return null;
}

const ABROAD: [RegExp, string][] = [
  [/\b(dubai|uae|abu dhabi|sharjah|emirates)\b|دبئی|ابوظہبی|امارات/i, "UAE"], [/\b(saudi|ksa|riyadh|jeddah|dammam)\b|سعودی|ریاض|جدہ/i, "Saudi Arabia"],
  [/\b(qatar|doha)\b|قطر|دوحہ/i, "Qatar"], [/\b(oman|muscat|bahrain|kuwait)\b|عمان|بحرین|کویت/i, "Gulf"],
  [/\b(uk|england|london|manchester|birmingham|britain)\b|برطانیہ|لندن|انگلینڈ/i, "UK"], [/\b(usa|america|us|new york|texas|chicago)\b|امریکہ/i, "USA"],
  [/\b(canada|toronto)\b|کینیڈا/i, "Canada"], [/\b(australia|sydney|melbourne)\b|آسٹریلیا/i, "Australia"],
  [/\b(germany|italy|spain|france|europe|norway|sweden)\b|جرمنی|اٹلی|یورپ/i, "Europe"],
];
/** Whether the buyer is overseas, and where. Null when the message says nothing about it. */
export function parseOverseas(text: string): { overseas: boolean; country: string } | null {
  for (const [re, country] of ABROAD) if (re.test(text)) return { overseas: true, country };
  if (/\b(overseas|abroad|bahar|bahir|outside pakistan|nri|opf)\b|بیرون ملک|باہر/i.test(text)) return { overseas: true, country: "" };
  if (/\b(in pakistan|pakistan mein|pakistan me|local|islamabad mein|pindi mein|rawalpindi mein|quetta mein|yahin|yaheen)\b|پاکستان میں|یہیں|اسلام آباد میں|کوئٹہ میں/i.test(text)) return { overseas: false, country: "Pakistan" };
  return null;
}

export const LEGAL = /\b(noc|n\.o\.c|approved|approval|legal|legally|transfer|mutation|registry|intiqal|possession|tax|taxes|fbr|cda|rda|stamp duty|fard|title deed|verify (the )?documents?|litigation|dispute)\b|این او سی|منظور|قانونی|انتقال|رجسٹری|ٹیکس|قبضہ|کاغذات/i;
export const HUMAN = /\b(agent|human|real person|call me|phone me|talk to (someone|a person)|manager|baat karni|baat karwa|call karein)\b|ایجنٹ|انسان|کال کریں|بات کروائیں/i;
export const PRICE_TALK = /\b(discount|negotiat|last price|final price|kam ho|installment|instalment|qist|payment plan|down ?payment|rate kya|kitne ka|price kya|kitni price)\b|رعایت|قسط|ڈاؤن پیمنٹ|آخری قیمت|کتنے کا/i;

export type Criteria = { budget: number | null; area: string; size: string; kind: string };

/** Deterministic match against stored sample listings. Never adds a listing that is not stored. */
export function matchListings(listings: Listing[], c: Criteria, limit = 3): Listing[] {
  const size = c.size ? parseSize(c.size) : null;
  // A listing more than 20% over the buyer's stated budget is never offered.
  const scored = listings.filter((l) => l.status === "available" && (c.budget == null || l.price <= c.budget * 1.2)).map((l) => {
    let score = 0;
    const society = l.society.toLowerCase();
    if (c.area && c.area.toLowerCase().split(" or ").some((a) => society.includes(a.split(" ")[0]) || a.includes(society.split(" ")[0]))) score += 4;
    if (c.kind && l.kind === c.kind) score += 3;
    if (size && l.size_unit === size.unit && Math.abs(l.size_value - size.value) / size.value <= 0.25) score += 3;
    if (c.budget != null) score += l.price <= c.budget * 1.05 ? 3 : l.price <= c.budget * 1.2 ? 1 : -4;
    return { l, score };
  });
  return scored.filter((x) => x.score > 0).sort((a, b) => b.score - a.score || a.l.price - b.l.price).slice(0, limit).map((x) => x.l);
}

// ---------------------------------------------------------------- site visits
/** Free site-visit start times on a PKT date: inside office hours, on the visit grid, at least
 *  one active agent without an overlapping confirmed visit, within 14 days and before expiry. */
export function visitSlots(date: string, agents: Pick<Agent, "id" | "active">[], busy: Busy[], settings: ReSettings, expires: string, now = new Date()): string[] {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || date < localDate(now) || date > dayAfter(localDate(now), 13)) return [];
  const midnight = new Date(`${date}T00:00:00+05:00`).getTime();
  if (Number.isNaN(midnight)) return [];
  const step = settings.visit_minutes * 60000, out: string[] = [];
  for (let m = settings.open_min; m + settings.visit_minutes <= settings.close_min; m += settings.visit_minutes) {
    const start = midnight + m * 60000, end = start + step;
    if (start <= now.getTime() || end > new Date(expires).getTime()) continue;
    const free = agents.some((a) => a.active && !busy.some((v) => v.agent_id === a.id && v.status === "confirmed" &&
      new Date(v.starts_at).getTime() < end && new Date(v.ends_at).getTime() > start));
    if (free) out.push(new Date(start).toISOString());
  }
  return out;
}

/** The first date (from today) with free slots, for offering concrete times in chat. */
export function firstOpenDay(agents: Pick<Agent, "id" | "active">[], busy: Busy[], settings: ReSettings, expires: string, now = new Date(), from?: string) {
  let day = from ?? localDate(now);
  for (let i = 0; i < 14; i++, day = dayAfter(day)) {
    const slots = visitSlots(day, agents, busy, settings, expires, now);
    if (slots.length) return { day, slots };
  }
  return null;
}

// ---------------------------------------------------------------- qualification + summary
export type Qualification = { budget: number | null; area: string; size: string; kind: string; timeline: string; overseas: boolean | null; country: string };
export const QUESTION_ORDER = ["budget", "area", "size", "timeline", "overseas"] as const;
export function nextQuestion(q: Qualification): (typeof QUESTION_ORDER)[number] | null {
  if (q.budget == null) return "budget";
  if (!q.area) return "area";
  if (!q.size) return "size";
  if (!q.timeline) return "timeline";
  if (q.overseas == null) return "overseas";
  return null;
}

/** One line for the agent, built only from what the buyer actually said. */
export function leadSummary(q: Qualification & { name?: string }, extra: { agent?: string; visit?: string; handoff?: string } = {}): string {
  const who = q.overseas ? `Overseas buyer${q.country && q.country !== "Pakistan" ? ` (${q.country})` : ""}` : q.overseas === false ? "Local buyer" : "Buyer";
  const want = [q.size, q.kind || "property"].filter(Boolean).join(" ");
  const subject = q.name && q.name !== "Demo buyer" ? `${q.name}, ${who.charAt(0).toLowerCase()}${who.slice(1)},` : who;
  const parts = [`${subject} wants a ${want}${q.area ? ` in ${q.area}` : ""}`];
  if (q.budget != null) parts.push(`budget ${formatPkr(q.budget)}`);
  if (q.timeline) parts.push(`timeline: ${q.timeline}`);
  let s = parts.join(", ") + ".";
  if (extra.visit) s += ` Site visit ${extra.visit}${extra.agent ? ` with ${extra.agent}` : ""}.`;
  if (extra.handoff) s += ` Needs an agent: ${extra.handoff}.`;
  return s;
}

// ---------------------------------------------------------------- manager statistics
const median = (xs: number[]) => {
  if (!xs.length) return null;
  const s = [...xs].sort((a, b) => a - b), m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : Math.round((s[m - 1] + s[m]) / 2);
};
export function replySeconds(l: Pick<Lead, "created_at" | "first_reply_at">): number | null {
  if (!l.first_reply_at) return null;
  return Math.max(0, Math.round((new Date(l.first_reply_at).getTime() - new Date(l.created_at).getTime()) / 1000));
}
export type SourceStats = { source: Source; leads: number; visits: number; won: number; medianReply: number | null };
export function responseStats(leads: Lead[], visits: Pick<Visit, "lead_id" | "status">[]) {
  const visited = new Set(visits.filter((v) => v.status !== "cancelled").map((v) => v.lead_id));
  const bySource = new Map<Source, Lead[]>();
  for (const l of leads) bySource.set(l.source, [...(bySource.get(l.source) ?? []), l]);
  const sources: SourceStats[] = [...bySource.entries()].map(([source, ls]) => ({
    source, leads: ls.length, visits: ls.filter((l) => visited.has(l.id)).length, won: ls.filter((l) => l.stage === "won").length,
    medianReply: median(ls.map(replySeconds).filter((x): x is number => x != null)),
  })).sort((a, b) => b.leads - a.leads);
  const replies = leads.map(replySeconds).filter((x): x is number => x != null);
  return {
    total: leads.length, sources, medianReply: median(replies), unanswered: leads.filter((l) => !l.first_reply_at).length,
    underFiveMin: replies.length ? Math.round((100 * replies.filter((x) => x <= 300).length) / replies.length) : null,
    visitRate: leads.length ? Math.round((100 * visited.size) / leads.length) : null,
  };
}
export function duration(seconds: number | null, lang: "en" | "ur" = "en"): string {
  if (seconds == null) return lang === "ur" ? "جواب نہیں" : "No reply";
  if (seconds < 90) return lang === "ur" ? `${seconds} سیکنڈ` : `${seconds}s`;
  if (seconds < 5400) return lang === "ur" ? `${Math.round(seconds / 60)} منٹ` : `${Math.round(seconds / 60)} min`;
  return lang === "ur" ? `${Math.round(seconds / 3600)} گھنٹے` : `${Math.round(seconds / 3600)} h`;
}
export function sizeLabel(l: Pick<Listing, "size_value" | "size_unit">, lang: "en" | "ur" = "en"): string {
  const u = { marla: ["marla", "مرلہ"], kanal: ["kanal", "کنال"], sqft: ["sq ft", "مربع فٹ"] }[l.size_unit];
  return `${trim(Number(l.size_value))} ${lang === "ur" ? u[1] : u[0]}`;
}

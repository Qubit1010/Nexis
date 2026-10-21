// Server-side real-estate workspace: seeding, scoped reads and the single RPC that every write goes
// through (demo_re_action in sql/real_estate_schema.sql). All listings, agents and buyers are synthetic.
import { rest, transcript, type Business, type Conversation } from "./db.ts";
import { rpc } from "./healthcare.ts";
import { cityOf } from "./city.ts";
import { visitSlots, type Agent, type Buyer, type Busy, type Lead, type Listing, type ReRole, type ReSettings, type ReState, type Visit } from "./real-estate-types.ts";

const q = (slug: string) => `slug=eq.${encodeURIComponent(slug)}`;
const cr = (n: number) => Math.round(n * 10_000_000), lk = (n: number) => Math.round(n * 100_000);

type SeedListing = Omit<Listing, "id" | "status" | "beds" | "baths"> & { beds?: number; baths?: number; status?: Listing["status"] };
const ISLAMABAD: SeedListing[] = [
  { code: "NP-101", title: "10 marla plot, Sector J", title_ur: "دس مرلہ پلاٹ، سیکٹر جے", kind: "plot", society: "DHA Phase 2", society_ur: "ڈی ایچ اے فیز ٹو", block: "Sector J", size_value: 10, size_unit: "marla", price: cr(2.35), features: ["Park facing", "Possession", "Near main boulevard"], description: "A sample residential plot facing a park, close to the main boulevard.", description_ur: "پارک کے سامنے نمونہ رہائشی پلاٹ، مین بلیوارڈ کے قریب۔", art: "plot" },
  { code: "NP-102", title: "10 marla plot, Block C", title_ur: "دس مرلہ پلاٹ، بلاک سی", kind: "plot", society: "Gulberg Greens", society_ur: "گلبرگ گرینز", block: "Block C", size_value: 10, size_unit: "marla", price: cr(2.1), features: ["Developed block", "Wide street"], description: "A sample plot in a developed block on a wide street.", description_ur: "ترقی یافتہ بلاک میں چوڑی گلی پر نمونہ پلاٹ۔", art: "plot" },
  { code: "NP-103", title: "10 marla house, 5 bed", title_ur: "دس مرلہ گھر، پانچ بیڈ", kind: "house", society: "Bahria Town Phase 8", society_ur: "بحریہ ٹاؤن فیز آٹھ", block: "Usman Block", size_value: 10, size_unit: "marla", beds: 5, baths: 6, price: cr(4.4), features: ["Double storey", "Solar ready", "Near mosque"], description: "A sample double-storey family house, ready to move in.", description_ur: "رہائش کے لیے تیار، دو منزلہ نمونہ خاندانی گھر۔", art: "house" },
  { code: "NP-104", title: "2 bed apartment, 1,150 sq ft", title_ur: "دو بیڈ اپارٹمنٹ، ۱۱۵۰ مربع فٹ", kind: "apartment", society: "E-11", society_ur: "ای الیون", block: "E-11/2", size_value: 1150, size_unit: "sqft", beds: 2, baths: 2, price: cr(1.25), features: ["Lift", "Parking", "Margalla view"], description: "A sample apartment with lift, basement parking and hill views.", description_ur: "لفٹ، پارکنگ اور پہاڑوں کے منظر کے ساتھ نمونہ اپارٹمنٹ۔", art: "apartment" },
  { code: "NP-105", title: "8 marla plot, Block F", title_ur: "آٹھ مرلہ پلاٹ، بلاک ایف", kind: "plot", society: "B-17", society_ur: "بی سترہ", block: "Block F", size_value: 8, size_unit: "marla", price: lk(72), features: ["On instalments", "Near GT Road"], description: "A sample plot close to GT Road, a common first purchase.", description_ur: "جی ٹی روڈ کے قریب نمونہ پلاٹ، پہلی خریداری کے لیے عام انتخاب۔", art: "plot" },
  { code: "NP-106", title: "1 kanal house, 6 bed", title_ur: "ایک کنال گھر، چھ بیڈ", kind: "house", society: "DHA Phase 2", society_ur: "ڈی ایچ اے فیز ٹو", block: "Sector E", size_value: 1, size_unit: "kanal", beds: 6, baths: 7, price: cr(8.9), features: ["Basement", "Lawn", "Servant quarter"], description: "A sample one-kanal house with basement and front lawn.", description_ur: "تہہ خانے اور لان کے ساتھ ایک کنال کا نمونہ گھر۔", art: "house" },
  { code: "NP-107", title: "4 marla commercial plot", title_ur: "چار مرلہ کمرشل پلاٹ", kind: "commercial", society: "Gulberg Greens", society_ur: "گلبرگ گرینز", block: "Business Square", size_value: 4, size_unit: "marla", price: cr(3.2), status: "reserved", features: ["Main road", "Rental potential"], description: "A sample commercial plot on the main road.", description_ur: "مین روڈ پر نمونہ کمرشل پلاٹ۔", art: "commercial" },
  { code: "NP-108", title: "5 marla plot file", title_ur: "پانچ مرلہ پلاٹ فائل", kind: "file", society: "Top City-1", society_ur: "ٹاپ سٹی ون", block: "Open file", size_value: 5, size_unit: "marla", price: lk(38), features: ["File only", "Balloting pending"], description: "A sample plot file. Balloting and allocation are confirmed by an agent.", description_ur: "نمونہ پلاٹ فائل۔ قرعہ اندازی اور الاٹمنٹ کی تصدیق ایجنٹ کرے گا۔", art: "file" },
];
const QUETTA: SeedListing[] = [
  { code: "NP-201", title: "10 marla plot", title_ur: "دس مرلہ پلاٹ", kind: "plot", society: "Jinnah Town", society_ur: "جناح ٹاؤن", block: "Block B", size_value: 10, size_unit: "marla", price: cr(1.6), features: ["Corner", "Paved street"], description: "A sample corner plot on a paved street.", description_ur: "پکی گلی پر نمونہ کونے کا پلاٹ۔", art: "plot" },
  { code: "NP-202", title: "8 marla plot", title_ur: "آٹھ مرلہ پلاٹ", kind: "plot", society: "Samungli Housing Scheme", society_ur: "سمنگلی ہاؤسنگ سکیم", block: "Phase 1", size_value: 8, size_unit: "marla", price: lk(95), features: ["Near main road"], description: "A sample plot near the main road.", description_ur: "مین روڈ کے قریب نمونہ پلاٹ۔", art: "plot" },
  { code: "NP-203", title: "10 marla house, 5 bed", title_ur: "دس مرلہ گھر، پانچ بیڈ", kind: "house", society: "Chiltan Housing Scheme", society_ur: "چلتن ہاؤسنگ سکیم", block: "Block A", size_value: 10, size_unit: "marla", beds: 5, baths: 5, price: cr(3.1), features: ["Double storey", "Gas connection"], description: "A sample double-storey family house.", description_ur: "دو منزلہ نمونہ خاندانی گھر۔", art: "house" },
  { code: "NP-204", title: "1 kanal house, 6 bed", title_ur: "ایک کنال گھر، چھ بیڈ", kind: "house", society: "Shahbaz Town", society_ur: "شہباز ٹاؤن", block: "Phase 2", size_value: 1, size_unit: "kanal", beds: 6, baths: 6, price: cr(5.5), features: ["Lawn", "Basement"], description: "A sample one-kanal house with a lawn.", description_ur: "لان کے ساتھ ایک کنال کا نمونہ گھر۔", art: "house" },
  { code: "NP-205", title: "Ground floor shop", title_ur: "گراؤنڈ فلور دکان", kind: "commercial", society: "Model Town", society_ur: "ماڈل ٹاؤن", block: "Main market", size_value: 400, size_unit: "sqft", price: cr(1.8), features: ["Main market", "Rented"], description: "A sample shop in the main market.", description_ur: "مین مارکیٹ میں نمونہ دکان۔", art: "commercial" },
  { code: "NP-206", title: "5 marla plot", title_ur: "پانچ مرلہ پلاٹ", kind: "plot", society: "Samungli Housing Scheme", society_ur: "سمنگلی ہاؤسنگ سکیم", block: "Phase 2", size_value: 5, size_unit: "marla", price: lk(55), features: ["Instalments"], description: "A sample plot on instalments.", description_ur: "قسطوں پر نمونہ پلاٹ۔", art: "plot" },
];
const AGENTS = [
  { name: "Bilal Ahmed", name_ur: "بلال احمد", title: "Senior sales agent", areas: "Plots and houses" },
  { name: "Sana Malik", name_ur: "ثنا ملک", title: "Sales agent", areas: "Overseas buyers" },
  { name: "Usman Raza", name_ur: "عثمان رضا", title: "Sales agent", areas: "Apartments and commercial" },
];
// Sample pipeline history so the agent board and manager view are not empty on first open.
// listing / agent are indexes into the seeded arrays above.
function sampleLeads(islamabad: boolean) {
  const a = (isb: string, qta: string) => islamabad ? isb : qta;
  return [
    { name: "Hamza Qureshi", source: "facebook", stage: "visit_booked", budget: cr(2.5), area: a("DHA Phase 2", "Jinnah Town"), size: "10 marla", kind: "plot", timeline: "2-3 months", overseas: true, country: "UAE", listing: 0, agent: 0, age_hours: 20, reply_seconds: 41, visit_day: 1, visit_hour: 11, summary: `Overseas buyer (UAE) wants a 10 marla plot in ${a("DHA Phase 2", "Jinnah Town")}, budget PKR 2.5 crore, timeline: 2-3 months. Site visit booked with Bilal Ahmed.` },
    { name: "Ayesha Siddiqui", source: "zameen", stage: "qualified", budget: cr(1.3), area: a("E-11", "Model Town"), size: a("1,150 sq ft", "10 marla"), kind: a("apartment", "house"), timeline: "This year", overseas: false, country: "Pakistan", agent: 2, age_hours: 30, reply_seconds: 58, summary: `Local buyer wants a ${a("2 bed apartment in E-11", "house in Model Town")}, budget PKR 1.3 crore, timeline: this year.` },
    { name: "Imran Khattak", source: "chat", stage: "new", budget: null, area: a("Bahria Town", "Chiltan Housing Scheme"), size: "", kind: "house", timeline: "", overseas: null, country: "", age_hours: 2, reply_seconds: 9, summary: `Buyer asking about houses in ${a("Bahria Town", "Chiltan Housing Scheme")}. Budget and size not given yet.` },
    { name: "Farah Naz", source: "website", stage: "negotiating", budget: cr(4.5), area: a("Bahria Town Phase 8", "Chiltan Housing Scheme"), size: "10 marla", kind: "house", timeline: "Ready now", overseas: true, country: "UK", listing: 2, agent: 1, age_hours: 120, reply_seconds: 33, visit_day: -3, visit_hour: 15, summary: "Overseas buyer (UK) negotiating on the sample 10 marla house after a site visit. Wants a payment plan confirmed by the office." },
    { name: "Kamran Shah", source: "referral", stage: "won", budget: lk(75), area: a("B-17", "Samungli Housing Scheme"), size: "8 marla", kind: "plot", timeline: "Ready now", overseas: false, country: "Pakistan", listing: 4, agent: 0, age_hours: 260, reply_seconds: 1800, visit_day: -9, visit_hour: 12, summary: "Local buyer closed on the sample 8 marla plot after one site visit." },
    { name: "Nadia Hussain", source: "phone", stage: "lost", budget: lk(60), area: a("Gulberg Greens", "Jinnah Town"), size: "10 marla", kind: "plot", timeline: "Next year", overseas: false, country: "Pakistan", agent: 1, age_hours: 200, reply_seconds: 14400, lost_reason: "Budget below current sample listings", summary: "Missed call returned after 4 hours. Budget was below the sample listings." },
    { name: "Tariq Mehmood", source: "facebook", stage: "new", budget: cr(3), area: "", size: "1 kanal", kind: "house", timeline: "", overseas: true, country: "Saudi Arabia", age_hours: 1, reply_seconds: 52, summary: "Overseas buyer (Saudi Arabia) wants a 1 kanal house, budget PKR 3 crore. Area not given yet." },
    { name: "Mehwish Akhtar", source: "walk_in", stage: "qualified", budget: lk(40), area: a("Top City-1", "Samungli Housing Scheme"), size: "5 marla", kind: a("file", "plot"), timeline: "1 month", overseas: false, country: "Pakistan", agent: 2, age_hours: 50, reply_seconds: 600, summary: `Walk-in buyer wants a 5 marla ${a("file in Top City-1", "plot in Samungli")}, budget PKR 40 lakh, within a month.` },
  ];
}

export async function ensureRealEstate(b: Business) {
  const s = (await rest<ReSettings>("GET", `demo_re_settings?${q(b.slug)}&seeded=eq.true&limit=1`))[0];
  if (s) return;
  const islamabad = /islamabad|rawalpindi/i.test(cityOf(b.profile));
  await rpc("demo_re_action", { p_slug: b.slug, p_visitor: "system-seed", p_role: "system", p_action: "seed",
    p_data: { agents: AGENTS, listings: islamabad ? ISLAMABAD : QUETTA, leads: sampleLeads(islamabad) } });
}

export async function reAction<T = unknown>(b: Business, visitor: string, role: ReRole, action: string, data: Record<string, unknown>): Promise<T> {
  await ensureRealEstate(b);
  return rpc<T>("demo_re_action", { p_slug: b.slug, p_visitor: visitor, p_role: role, p_action: action, p_data: data });
}

export async function reState(b: Business, visitor: string, role: ReRole): Promise<ReState> {
  await ensureRealEstate(b);
  const buyer = await reAction<Buyer>(b, visitor, role, "buyer", {});
  const scope = q(b.slug), staff = role !== "buyer";
  const [agents, listings, settings, buyers, leads, visits, conversations, activity] = await Promise.all([
    rest<Agent>("GET", `demo_re_agents?${scope}&order=name`),
    rest<Listing>("GET", `demo_re_listings?${scope}&order=code`),
    rest<ReSettings>("GET", `demo_re_settings?${scope}`),
    staff ? rest<Buyer>("GET", `demo_re_buyers?${scope}&order=created_at.desc&limit=300`) : Promise.resolve([buyer]),
    rest<Lead>("GET", `demo_re_leads?${scope}${staff ? "" : `&buyer_id=eq.${buyer.id}`}&order=updated_at.desc&limit=300`),
    rest<Visit>("GET", `demo_re_visits?${scope}&order=starts_at&limit=1000`),
    staff ? rest<Conversation>("GET", `demo_conversations?${scope}&order=last_at.desc&limit=40`) : Promise.resolve([]),
    role === "manager" ? rest<ReState["activity"][number]>("GET", `demo_events?${scope}&kind=like.re_*&order=at.desc&limit=40`) : Promise.resolve([]),
  ]);
  return {
    role, city: cityOf(b.profile), buyer, buyers, agents, listings, settings: settings[0], leads,
    visits: staff ? visits : visits.filter((v) => v.buyer_id === buyer.id),
    busy: visits.map(({ agent_id, starts_at, ends_at, status }): Busy => ({ agent_id, starts_at, ends_at, status })),
    conversations: await Promise.all(conversations.map(async (c) => ({ ...c, staff_mode: !!c.staff_mode, assigned_to: c.assigned_to ?? null, messages: await transcript(c.id) }))),
    activity, server_time: new Date().toISOString(), expires_at: b.expires_at,
  };
}

export async function reAvailability(b: Business, date: string) {
  await ensureRealEstate(b);
  const scope = q(b.slug);
  const [agents, busy, settings] = await Promise.all([
    rest<Agent>("GET", `demo_re_agents?${scope}`),
    rest<Busy>("GET", `demo_re_visits?${scope}&status=eq.confirmed&select=agent_id,starts_at,ends_at,status`),
    rest<ReSettings>("GET", `demo_re_settings?${scope}`),
  ]);
  return { agents, busy, settings: settings[0], slots: visitSlots(date, agents, busy, settings[0], b.expires_at) };
}

export async function landingListings(b: Business): Promise<{ listings: Listing[]; unavailable: boolean }> {
  try {
    await ensureRealEstate(b);
    return { listings: await rest<Listing>("GET", `demo_re_listings?${q(b.slug)}&order=code`), unavailable: false };
  } catch {
    return { listings: [], unavailable: true };
  }
}

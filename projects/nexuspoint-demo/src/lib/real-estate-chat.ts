// Deterministic buyer flow for property demos: qualify budget, area, size, timeline and overseas
// status one question at a time, show only stored sample listings, then offer concrete site-visit
// slots and book one through the atomic reservation. Legal, NOC, payment-plan and "talk to a person"
// messages go to an agent. Everything else (hours, location, bot questions) falls through to the brain.
import { randomUUID } from "node:crypto";
import { updateConversation, type Business, type Conversation } from "./db.ts";
import { reAction, reAvailability, reState } from "./real-estate.ts";
import {
  HUMAN, LEGAL, PRICE_TALK, firstOpenDay, formatPkr, leadSummary, matchListings, nextQuestion, parseArea, parseBudget, parseKind,
  parseOverseas, parseSize, parseTimeline, sizeLabel, type Lead, type Listing, type Qualification, type Visit,
} from "./real-estate-types.ts";
import { dateLabel, timeLabel, type Choice } from "./healthcare-types.ts";
import { detectLang, type Lang } from "./scripted.ts";
import { urgentMessage } from "./brain.ts";

export const RE_INTENT = /\b(plot|plots|house|home|ghar|makan|apartment|flat|marla|kanal|crore|cr|lakh|lac|budget|society|dha|bahria|gulberg|sector|site visit|visit|buy|buying|purchase|invest|investment|property|listing|file|commercial|shop|overseas|abroad|kharidna|lena)\b|پلاٹ|گھر|مکان|اپارٹمنٹ|فلیٹ|مرلہ|کنال|کروڑ|لاکھ|بجٹ|سوسائٹی|وزٹ|خرید|پراپرٹی|فائل|ڈی ایچ اے|بحریہ|گلبرگ/i;
const BOT = /\b(are you|r u|kya aap|aap).{0,20}\b(bot|robot|real|human|insaan|machine|ai)\b|کیا آپ.{0,20}(بوٹ|انسان|مشین)/i;

type Ctx = Record<string, string>;
const qOf = (ctx: Ctx): Qualification => ({
  budget: ctx.budget ? Number(ctx.budget) : null, area: ctx.area ?? "", size: ctx.size ?? "", kind: ctx.kind ?? "",
  timeline: ctx.timeline ?? "", overseas: ctx.overseas === "true" ? true : ctx.overseas === "false" ? false : null, country: ctx.country ?? "",
});

export async function realEstateChat(b: Business, c: Conversation, text: string, choice?: Choice) {
  // The shared emergency handler in brain.ts keeps priority over any open property flow.
  if (urgentMessage(text)) return null;
  let ctx: Ctx = { ...(c.booking_context ?? {}) };
  const reChoice = !!choice?.kind.startsWith("re_");
  const lang: Lang = reChoice && ["en", "ur", "roman"].includes(ctx.reLang ?? "") ? (ctx.reLang as Lang) : detectLang(text);
  const say = (en: string, ur: string, roman?: string) => lang === "ur" ? ur : lang === "roman" ? roman ?? en : en;
  const wantsAgent = HUMAN.test(text), legal = LEGAL.test(text), priceTalk = PRICE_TALK.test(text);
  if (!reChoice && ctx.reFlow !== "on" && !RE_INTENT.test(text) && !wantsAgent && !legal && !priceTalk) return null;
  if (!reChoice && BOT.test(text)) return null; // honest bot disclosure stays with the shared brain

  const receivedAt = new Date().toISOString();
  const s = await reState(b, c.visitor, "buyer");
  const card = (kind: Choice["kind"], value: string, label: string): Choice => ({ kind, value, label });
  ctx.reFlow = "on"; ctx.reLang = lang; ctx.leadRequest ??= `chat-${c.id}`;
  const listingOf = (id?: string) => s.listings.find((l) => l.id === id);
  const save = async (extra: Record<string, unknown> = {}) => {
    const q = qOf(ctx);
    const visitText = extra.visitLabel as string | undefined;
    const summary = leadSummary({ ...q, name: s.buyer.name }, { visit: visitText, agent: extra.agentName as string | undefined, handoff: extra.handoffReason as string | undefined });
    const lead = await reAction<Lead>(b, c.visitor, "buyer", "qualify", {
      requestId: ctx.leadRequest, conversationId: c.id, receivedAt, summary,
      ...(q.budget != null ? { budget: q.budget } : {}), area: q.area, size: q.size, kind: q.kind, timeline: q.timeline,
      ...(q.overseas != null ? { overseas: q.overseas, country: q.country } : {}),
      ...(ctx.listing ? { listingId: ctx.listing } : {}),
      ...(extra.handoffReason ? { handoff: true, handoffReason: extra.handoffReason } : {}),
    });
    ctx.leadId = lead.id;
    return { lead, summary };
  };
  const finish = async (reply: string, cards: Choice[] = [], stage = "qualifying", summary = "") => {
    await updateConversation(c.id, { booking_context: ctx });
    return { reply, cards, stage, summary: summary || leadSummary(qOf(ctx)) };
  };
  const handoff = async (reason: string, en: string, ur: string, roman: string) => {
    const { summary } = await save({ handoffReason: reason });
    return finish(say(en, ur, roman), [], "needs_human", summary);
  };

  // 1. Questions only an agent can answer. Never guessed, never answered from listing data.
  if (!reChoice && legal) return handoff("legal or NOC question",
    "Legal status, NOC, approvals, transfer and tax questions are answered by an agent who checks the documents for that exact property. I have passed your question to an agent; they will reply in this chat.",
    "قانونی حیثیت، این او سی، منظوری، انتقال اور ٹیکس کے سوالات کا جواب ایجنٹ اسی پراپرٹی کے کاغذات دیکھ کر دیتا ہے۔ آپ کا سوال ایجنٹ کو بھیج دیا گیا ہے، وہ اسی چیٹ میں جواب دیں گے۔",
    "Legal status, NOC, approval, transfer aur tax ke sawal ka jawab agent us property ke kaghzat dekh kar deta hai. Aap ka sawal agent ko bhej diya hai, woh isi chat mein jawab denge.");
  if (!reChoice && priceTalk) return handoff("payment plan or final price",
    "Final prices, discounts and payment plans are confirmed only by an agent. I have asked an agent to reply here. Meanwhile I can note your budget and book a site visit.",
    "آخری قیمت، رعایت اور قسطوں کا پلان صرف ایجنٹ کنفرم کرتا ہے۔ ایجنٹ کو جواب کے لیے کہہ دیا ہے۔ اس دوران میں آپ کا بجٹ نوٹ کر کے سائٹ وزٹ بک کر سکتا ہوں۔",
    "Final price, discount aur qiston ka plan sirf agent confirm karta hai. Agent ko jawab ke liye keh diya hai. Is dauran main aap ka budget note kar ke site visit book kar sakta hoon.");
  if (!reChoice && wantsAgent) return handoff("asked for a person",
    "Of course. I have asked an agent to take over this conversation; they will reply here. This demo does not send real calls or messages.",
    "ضرور۔ ایجنٹ کو یہ گفتگو سنبھالنے کا کہہ دیا ہے، وہ یہیں جواب دیں گے۔ یہ ڈیمو حقیقی کال یا پیغام نہیں بھیجتا۔",
    "Zaroor. Agent ko yeh guftagu sambhalne ka keh diya hai, woh yahin jawab denge. Yeh demo asal call ya message nahi bhejta.");

  // 2. Read whatever the buyer told us. Only what they said is stored.
  if (choice?.kind === "re_restart") { ctx = { reFlow: "on", reLang: lang, leadRequest: `chat-${c.id}-${randomUUID().slice(0, 8)}` }; }
  if (!reChoice) {
    const budget = parseBudget(text), area = parseArea(text, [...new Set(s.listings.map((l) => l.society))]), size = parseSize(text),
      kind = parseKind(text), timeline = parseTimeline(text), abroad = parseOverseas(text);
    const parsed = budget != null || !!area || !!size || !!kind || !!timeline || !!abroad;
    // Hours, directions, thanks and small talk go back to the shared brain, even mid-flow.
    if (!parsed && !RE_INTENT.test(text) && (ctx.booked || !ctx.asked || /\b(hours?|timings?|open|close|where|address|location|kahan|office|thanks|shukriya)\b|اوقات|کہاں|پتہ|شکریہ/i.test(text))) return null;
    if (budget != null) ctx.budget = String(budget);
    if (area) ctx.area = area;
    if (size) ctx.size = size.label;
    if (kind) ctx.kind = kind;
    if (timeline) ctx.timeline = timeline;
    if (abroad) { ctx.overseas = String(abroad.overseas); ctx.country = abroad.country; }
    if (!area && ctx.asked === "area" && text.trim().length <= 40 && !budget && !size) ctx.area = text.trim();
  }
  if (choice?.kind === "re_budget") ctx.budget = choice.value;
  if (choice?.kind === "re_area") ctx.area = choice.value;
  if (choice?.kind === "re_size") { const [size, kind] = choice.value.split("|"); ctx.size = size; if (kind) ctx.kind = kind; }
  if (choice?.kind === "re_timeline") ctx.timeline = choice.value;
  if (choice?.kind === "re_overseas") { const [o, country] = choice.value.split("|"); ctx.overseas = o; ctx.country = country ?? ""; }
  if (choice?.kind === "re_listing") { const l = listingOf(choice.value); if (l) { ctx.listing = l.id; ctx.offer = "slots"; } }
  if (choice?.kind === "re_visit") ctx.offer = "slots";
  if (choice?.kind === "re_time") { ctx.start = choice.value; ctx.offer = "confirm"; }
  if (!reChoice && /\b(site visit|visit|dekhna|dekhne|appointment|meeting)\b|وزٹ|دیکھنے|ملاقات/i.test(text) && ctx.budget) ctx.offer = "slots";

  const slotCards = async () => {
    const { agents, busy, settings } = await reAvailability(b, "");
    const open = firstOpenDay(agents, busy, settings, b.expires_at);
    return open ? open.slots.slice(0, 6).map((t) => card("re_time", t, `${dateLabel(t, lang === "ur" ? "ur" : "en")} · ${timeLabel(t, lang === "ur" ? "ur" : "en")}`)) : [];
  };

  // 3. Book the visit: the database decides, the assistant only reports what was saved.
  if (choice?.kind === "re_confirm") {
    if (!ctx.start) { ctx.offer = "slots"; }
    else {
      try {
        ctx.visitRequest ??= randomUUID();
        const { lead } = await save();
        const v = await reAction<Visit>(b, c.visitor, "buyer", "reserve", { start: ctx.start, leadId: lead.id, requestId: ctx.visitRequest, source: "chat",
          notes: "Booked by the WhatsApp assistant", ...(ctx.listing ? { listingId: ctx.listing } : {}) });
        const agent = s.agents.find((a) => a.id === v.agent_id);
        const when = `${dateLabel(v.starts_at)}, ${timeLabel(v.starts_at)} PKT`;
        const { summary } = await save({ visitLabel: when, agentName: agent?.name });
        const l = listingOf(v.listing_id ?? undefined);
        await updateConversation(c.id, { action: { type: "visit", details: [
          { key: "Site visit", value: when }, { key: "Agent", value: agent?.name ?? "Assigned agent" },
          ...(l ? [{ key: "Sample listing", value: `${l.code} · ${l.title}, ${l.society}` }] : []),
        ] } });
        delete ctx.start; delete ctx.offer; delete ctx.visitRequest; ctx.booked = v.id;
        return finish(say(
          `Done. Your sample site visit is booked for ${when} with ${agent?.name ?? "an agent"}. It is saved in your buyer portal and the agent's pipeline. The agent will confirm the meeting point.`,
          `ہو گیا۔ آپ کا نمونہ سائٹ وزٹ ${dateLabel(v.starts_at, "ur")}، ${timeLabel(v.starts_at, "ur")} کو ${agent?.name_ur || agent?.name || "ایجنٹ"} کے ساتھ بک ہے۔ یہ خریدار پورٹل اور ایجنٹ پائپ لائن میں محفوظ ہے۔ ملنے کی جگہ ایجنٹ کنفرم کرے گا۔`,
          `Ho gaya. Aap ka sample site visit ${when} ko ${agent?.name ?? "agent"} ke saath book hai. Yeh buyer portal aur agent pipeline mein save hai. Milne ki jagah agent confirm karega.`), [], "warm", summary);
      } catch {
        delete ctx.start; delete ctx.visitRequest; ctx.offer = "slots";
        return finish(say("That time was just taken. Here are the next free times.", "یہ وقت ابھی بک ہو گیا۔ یہ اگلے دستیاب اوقات ہیں۔", "Yeh waqt abhi book ho gaya. Yeh agle free waqt hain."), await slotCards());
      }
    }
  }
  if (ctx.offer === "confirm" && ctx.start) {
    const l = listingOf(ctx.listing);
    await save();
    const when = `${dateLabel(ctx.start, lang === "ur" ? "ur" : "en")}, ${timeLabel(ctx.start, lang === "ur" ? "ur" : "en")}`;
    return finish(say(`Book a sample site visit on ${when} PKT${l ? ` for ${l.code}, ${l.title}` : ""}?`, `کیا ${when} کو${l ? ` ${l.code} کے لیے` : ""} نمونہ سائٹ وزٹ بک کر دوں؟`, `Kya ${when} ko${l ? ` ${l.code} ke liye` : ""} sample site visit book kar doon?`),
      [card("re_confirm", "confirm", say("Confirm visit", "وزٹ کنفرم کریں", "Visit confirm karein")), card("re_visit", "other", say("Other times", "دوسرے اوقات", "Doosre waqt"))], "warm");
  }
  if (ctx.offer === "slots") {
    await save();
    const cards = await slotCards();
    if (!cards.length) return handoff("no free site-visit slot in the demo window", "No sample visit times are free in the next two weeks. I have asked an agent to arrange a time with you.", "اگلے دو ہفتوں میں کوئی نمونہ وقت خالی نہیں۔ ایجنٹ کو آپ سے وقت طے کرنے کا کہہ دیا ہے۔", "Agle do hafton mein koi sample waqt khali nahi. Agent ko aap se waqt tay karne ka keh diya hai.");
    ctx.offer = "picking";
    return finish(say("Here are the next free site-visit times (PKT). An agent meets you at the site.", "سائٹ وزٹ کے اگلے دستیاب اوقات یہ ہیں۔ ایجنٹ آپ سے سائٹ پر ملے گا۔", "Site visit ke agle free waqt yeh hain (PKT). Agent aap se site par milega."), cards, "warm");
  }

  // 4. Qualify, one question per message, with quick replies.
  const q = qOf(ctx), next = nextQuestion(q);
  const { summary } = await save();
  if (next) {
    ctx.asked = next;
    const ask: Record<string, [string, string, string, Choice[]]> = {
      budget: ["What budget do you have in mind? A range in crore or lakh is fine.", "آپ کا بجٹ کتنا ہے؟ کروڑ یا لاکھ میں اندازہ کافی ہے۔", "Aap ka budget kitna hai? Crore ya lakh mein andaza kaafi hai.",
        [["5000000", "Up to 50 lakh", "پچاس لاکھ تک"], ["10000000", "50 lakh to 1 crore", "پچاس لاکھ سے ایک کروڑ"], ["25000000", "1 to 2.5 crore", "ایک سے ڈھائی کروڑ"], ["50000000", "2.5 to 5 crore", "ڈھائی سے پانچ کروڑ"], ["100000000", "Above 5 crore", "پانچ کروڑ سے زیادہ"]]
          .map(([v, en, ur]) => card("re_budget", v, say(en, ur)))],
      area: ["Which society or sector do you prefer?", "آپ کس سوسائٹی یا سیکٹر کو ترجیح دیتے ہیں؟", "Aap kis society ya sector ko tarjeeh dete hain?",
        [...[...new Set(s.listings.map((l) => l.society))].slice(0, 5).map((a) => card("re_area", a, lang === "ur" ? s.listings.find((l) => l.society === a)?.society_ur || a : a)),
          card("re_area", "Open to suggestions", say("Open to suggestions", "تجاویز چاہییں", "Suggestions chahiye"))]],
      size: ["What size and type are you looking for? For example a 10 marla plot or a 2 bed apartment.", "کس سائز اور قسم کی پراپرٹی چاہیے؟ مثلاً دس مرلہ پلاٹ یا دو بیڈ اپارٹمنٹ۔", "Kis size aur qisam ki property chahiye? Maslan 10 marla plot ya 2 bed apartment.",
        [["5 marla|plot", "5 marla plot", "پانچ مرلہ پلاٹ"], ["10 marla|plot", "10 marla plot", "دس مرلہ پلاٹ"], ["10 marla|house", "10 marla house", "دس مرلہ گھر"], ["1 kanal|house", "1 kanal house", "ایک کنال گھر"], ["1150 sq ft|apartment", "2 bed apartment", "دو بیڈ اپارٹمنٹ"]]
          .map(([v, en, ur]) => card("re_size", v, say(en, ur)))],
      timeline: ["When are you planning to buy?", "آپ کب تک خریدنا چاہتے ہیں؟", "Aap kab tak khareedna chahte hain?",
        [["Ready now", "Ready now", "ابھی تیار ہوں"], ["1-3 months", "In 1 to 3 months", "ایک سے تین مہینے"], ["This year", "This year", "اس سال"], ["Exploring, no fixed date", "Just exploring", "صرف دیکھ رہا ہوں"]]
          .map(([v, en, ur]) => card("re_timeline", v, say(en, ur)))],
      overseas: ["Are you in Pakistan at the moment, or overseas?", "کیا آپ اس وقت پاکستان میں ہیں یا بیرون ملک؟", "Kya aap is waqt Pakistan mein hain ya overseas?",
        [["false|Pakistan", "In Pakistan", "پاکستان میں"], ["true|UAE", "UAE or Gulf", "متحدہ عرب امارات یا خلیج"], ["true|UK", "UK or Europe", "برطانیہ یا یورپ"], ["true|", "Another country", "کوئی اور ملک"]]
          .map(([v, en, ur]) => card("re_overseas", v, say(en, ur)))],
    };
    const [en, ur, roman, cards] = ask[next];
    const ack = q.budget != null || q.area || q.size ? say("Noted. ", "نوٹ کر لیا۔ ", "Note kar liya. ") : "";
    return finish(ack + say(en, ur, roman), cards, "qualifying", summary);
  }

  // 5. Fully qualified: show only stored sample listings, then offer a visit.
  const matches = matchListings(s.listings, q);
  delete ctx.asked;
  const lines = matches.map((l: Listing) => lang === "ur"
    ? `${l.code}: ${l.title_ur || l.title}، ${l.society_ur || l.society}، ${sizeLabel(l, "ur")}، نمونہ ڈیمانڈ ${formatPkr(l.price, "ur")}`
    : `${l.code}: ${l.title}, ${l.society}, sample demand ${formatPkr(l.price)}`);
  const intro = matches.length
    ? say(`Thank you, that is everything an agent needs. Sample listings that fit:\n${lines.join("\n")}\nPrices are fictional demo data; an agent confirms real availability. Shall I book a site visit?`,
      `شکریہ، ایجنٹ کو درکار تمام معلومات مل گئیں۔ موزوں نمونہ لسٹنگز:\n${lines.join("\n")}\nقیمتیں فرضی ڈیمو ڈیٹا ہیں، اصل دستیابی ایجنٹ کنفرم کرے گا۔ کیا سائٹ وزٹ بک کر دوں؟`,
      `Shukriya, agent ko zaroori sab maloomat mil gayi. Munasib sample listings:\n${lines.join("\n")}\nPrices farzi demo data hain, asal availability agent confirm karega. Site visit book kar doon?`)
    : say("Thank you, that is everything an agent needs. None of the sample listings match exactly, so an agent will share options. Shall I book a site visit or an office meeting?",
      "شکریہ، تمام معلومات مل گئیں۔ کوئی نمونہ لسٹنگ پوری طرح موزوں نہیں، ایجنٹ آپشنز بھیجے گا۔ کیا سائٹ وزٹ یا آفس میٹنگ بک کر دوں؟",
      "Shukriya, sab maloomat mil gayi. Koi sample listing poori tarah match nahi karti, agent options bhejega. Site visit ya office meeting book kar doon?");
  return finish(intro, [...matches.map((l) => card("re_listing", l.id, `${l.code} · ${say("Visit this", "یہ دیکھیں", "Yeh dekhein")}`)), card("re_visit", "any", say("Book a site visit", "سائٹ وزٹ بک کریں", "Site visit book karein"))], "warm", summary);
}

// Shared by the web chat and the WhatsApp webhook: store the customer message, decide, store and
// return the reply, and update the conversation card the owner dashboard reads.
import { decide } from "./brain.ts";
import { chatJson } from "./llm.ts";
import {
  getOrCreateConversation,
  logEvent,
  rest,
  transcript,
  updateConversation,
  type Business,
  type Conversation,
} from "./db.ts";
import { healthcareChat } from "./healthcare-chat.ts";
import { restaurantChat } from "./restaurant-chat.ts";
import { schoolChat } from "./school-chat.ts";
import type { Choice } from "./healthcare-types.ts";
import { detectLang, introLine } from "./scripted.ts";

export function quettaToday(): string {
  return (
    new Date().toLocaleDateString("en-GB", {
      timeZone: "Asia/Karachi",
      weekday: "long",
      day: "numeric",
      month: "long",
      year: "numeric",
    }) +
    ", " +
    new Date().toLocaleTimeString("en-US", {
      timeZone: "Asia/Karachi",
      hour: "numeric",
      minute: "2-digit",
    })
  );
}

export async function respond(
  b: Business,
  channel: string,
  visitor: string,
  text: string,
  choice?: Choice,
) {
  const started = Date.now();
  const conv = await getOrCreateConversation(b.slug, channel, visitor);
  if (conv.staff_mode) {
    await rest(
      "POST",
      "demo_messages",
      {
        conversation_id: conv.id,
        role: "customer",
        content: text.slice(0, 1000),
        source: null,
        latency_ms: null,
      },
      "return=minimal",
    );
    await updateConversation(conv.id, {});
    return {
      reply: null,
      stage: "needs_human",
      latency: 0,
      source: "staff",
      provider: null,
      cards: [],
    };
  }
  const prior = await transcript(conv.id);
  const history = [
    ...prior.map((m) => ({ role: m.role, content: m.content })),
    { role: "customer", content: text.slice(0, 1000) },
  ];
  if (b.sector === "healthcare" || b.sector === "food" || b.sector === "education") {
    const h = b.sector === "food" ? await restaurantChat(b, conv, text, choice) : b.sector === "education" ? await schoolChat(b, conv, text, choice) : await healthcareChat(b, conv, text, choice);
    if (h) {
      if (!prior.some((m) => m.role === "business"))
        h.reply = introLine(detectLang(text), b.name) + h.reply;
      const fresh = (
        await rest<Conversation>(
          "GET",
          `demo_conversations?id=eq.${conv.id}&limit=1`,
        )
      )[0];
      const paused = !!fresh?.staff_mode;
      await rest(
        "POST",
        "demo_messages",
        [
          {
            conversation_id: conv.id,
            role: "customer",
            content: text.slice(0, 1000),
            source: null,
            latency_ms: null,
            cards: null,
          },
          ...(!paused
            ? [
                {
                  conversation_id: conv.id,
                  role: "business",
                  content: h.reply,
                  source: b.sector === "food" ? "restaurant" : b.sector === "education" ? "school" : "healthcare",
                  latency_ms: Date.now() - started,
                  cards: h.cards,
                },
              ]
            : []),
        ],
        "return=minimal",
      );
      await updateConversation(conv.id, {
        stage: paused ? "needs_human" : h.stage,
        summary: h.summary,
        handoff: paused || fresh?.handoff || h.stage === "needs_human",
      });
      if ('appointment' in h && h.appointment)
        await logEvent(b.slug, "booking", {
          channel,
          appointment_id: (h.appointment as {id:string}).id,
        });
      return {
        reply: paused ? null : h.reply,
        stage: paused ? "needs_human" : h.stage,
        latency: Date.now() - started,
        source: paused ? "staff" : b.sector === "food" ? "restaurant" : b.sector === "education" ? "school" : "healthcare",
        provider: null,
        cards: paused ? [] : h.cards,
      };
    }
  }
  const brainBusiness=b.sector==='education'?{...b,profile:{...b.profile,demo_hint:'Student records, fee verification, results and campus reservations are handled by a separate persistent school service. Do not infer or invent records. Refer unknown questions to the school office.'}}:b;
  const d = await decide(brainBusiness, history, chatJson, quettaToday());
  if (b.sector==='education'&&d.action.type!=='none') {
    d.action={type:'none',details:[]};d.stage='needs_human';
    d.reply=detectLang(text)==='ur'?'دفتر اس معلومات کی تصدیق کرے گا۔ نمونہ ریکارڈ اور کیمپس بکنگ والدین پورٹل میں دیکھیں۔':'The office can confirm that information. Use the parent portal for recorded sample information and available campus visits.';
  }
  if (b.sector === "food" && d.action.type === "order") {
    d.action = { type: "none", details: [] }; d.stage = "needs_human";
    d.reply = detectLang(text) === "ur" ? "نمونہ مینو سے آئٹمز منتخب کریں۔ آرڈر محفوظ ہونے کے بعد ہی تصدیق ہوگی۔ عملہ مدد کر سکتا ہے۔" : "Use the sample menu to choose items. Orders are confirmed only after they are saved. Staff can help with details.";
  }
  // Healthcare confirmations only come from the booking service, never model-generated actions.
  if (b.sector === "healthcare" && d.action.type === "booking") {
    d.action = { type: "none", details: [] };
    d.stage = "needs_human";
    const lang = detectLang(text);
    d.reply =
      lang === "ur"
        ? "مریض پورٹل میں دستیاب نمونہ ڈاکٹر اور وقت منتخب کریں۔ بکنگ محفوظ ہونے کے بعد ہی تصدیق ہوگی۔ اگر وقت معلوم نہ ہو تو عملہ مدد کرے گا۔"
        : lang === "roman"
          ? "Patient portal mein available sample doctor aur waqt chunein. Booking save hone ke baad hi confirm hogi. Waqt maloom na ho to staff madad karega."
          : "Please use the patient portal to choose an available sample doctor and time. A booking is confirmed only after it is saved. Staff can help with unknown availability.";
  }
  const fresh = (
    await rest<Conversation>(
      "GET",
      `demo_conversations?id=eq.${conv.id}&limit=1`,
    )
  )[0];
  if (fresh?.staff_mode) {
    await rest(
      "POST",
      "demo_messages",
      {
        conversation_id: conv.id,
        role: "customer",
        content: text.slice(0, 1000),
        source: null,
        latency_ms: null,
      },
      "return=minimal",
    );
    await updateConversation(conv.id, {});
    return {
      reply: null,
      stage: "needs_human",
      latency: Date.now() - started,
      source: "staff",
      provider: null,
      cards: [],
    };
  }
  const latency = Date.now() - started;
  const hasAction = d.action.type !== "none" && d.action.details.length > 0;
  await Promise.all([
    rest(
      "POST",
      "demo_messages",
      [
        {
          conversation_id: conv.id,
          role: "customer",
          content: text.slice(0, 1000),
          source: null,
          latency_ms: null,
        },
        {
          conversation_id: conv.id,
          role: "business",
          content: d.reply,
          source: d.provider ?? d.source ?? null,
          latency_ms: latency,
        },
      ],
      "return=minimal",
    ),
    updateConversation(conv.id, {
      stage: d.stage,
      summary: d.summary || conv.summary,
      answers: d.answers.length ? d.answers : conv.answers,
      action: hasAction ? d.action : conv.action,
      handoff: conv.handoff || d.stage === "needs_human",
    }),
  ]);
  if (hasAction) await logEvent(b.slug, d.action.type, { channel });
  if (d.stage === "needs_human") await logEvent(b.slug, "handoff", { channel });
  return {
    reply: d.reply,
    stage: d.stage,
    latency,
    source: d.source,
    provider: d.provider ?? null,
  };
}

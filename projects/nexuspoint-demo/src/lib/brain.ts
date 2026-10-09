// The demo assistant's brain. TypeScript port of Sixty Second Responder src/responder/brain.py:
// same decision contract (reply, stage, answers, summary), facts-only rules, honest bot disclosure,
// and the rule that matters most: a customer is never left unanswered. Extended with `action`
// (booking | order | fee_lookup | visit) to drive the owner dashboard cards.
//
// Order of fall-through: AI provider chain -> scripted sector brain -> fixed fallback reply.

import { clean, problems } from "./guards.ts";
import {
  detectLang,
  introLine,
  scriptedDecide,
  type Lang,
} from "./scripted.ts";

export type Stage =
  | "qualifying"
  | "warm"
  | "cold"
  | "unqualified"
  | "needs_human";
export type Decision = {
  reply: string;
  stage: Stage;
  answers: { key: string; value: string }[];
  summary: string;
  action: { type: string; details: { key: string; value: string }[] };
  source?: "ai" | "scripted" | "fallback";
  provider?: string;
};

export type BrainBusiness = {
  name: string;
  sector: string;
  profile: {
    about: string;
    services_sample: string[];
    questions: { key: string; ask: string }[];
    warm_when: string;
    unqualified_when: string;
    action: string;
    demo_hint: string;
    fallback_reply: { en: string; ur: string };
    facts: {
      name: string;
      address: string | null;
      city?: string | null;
      hours: { day: string; hours: string }[];
    };
  };
};

const STAGES: Stage[] = [
  "qualifying",
  "warm",
  "cold",
  "unqualified",
  "needs_human",
];

export function systemPrompt(b: BrainBusiness, today: string): string {
  const p = b.profile;
  const qs = p.questions.map((q) => `- ${q.key}: ${q.ask}`).join("\n");
  return `You are the ${p.action === "order" ? "ordering" : "front-desk"} assistant for ${b.name} in ${p.facts.city || "Quetta"}, replying on WhatsApp within a minute.
This is a live DEMO that NexusPoint built to show the owner how it works.

About the business (facts from its Google listing):
${p.about}

Services or items (SAMPLE for the demo, not confirmed by the owner): ${p.services_sample.join(", ")}.
Demo scenario: ${p.demo_hint}
Today in ${p.facts.city || "Quetta"}: ${today}.

Every turn:
1. Write the business's next message. Answer what they asked, then move forward.
2. Collect, one per message and only if not already given:
${qs}
3. Decide the stage:
- qualifying: still collecting.
- warm: ${p.warm_when} Confirm what was agreed and say the team will confirm.
- cold: interested but not now. Stay helpful.
- unqualified: ${p.unqualified_when}
- needs_human: they ask for a person, complain, have an emergency or medical question, or ask anything the facts do not answer (prices, fees, doctor availability, discounts). Say a team member will confirm. Never guess.
4. action: when a booking, order, fee lookup or visit is agreed, set type to booking | order | fee_lookup | visit and list the agreed details (day, time, name, items, address...). Otherwise type "none" and empty details.

Rules:
${b.sector === "healthcare" ? "- Doctor availability and reservations are handled by a separate database booking service. Never offer free slots or confirm a reservation from this conversation alone. Direct booking requests to the patient portal or staff and use action none." : ""}
${b.sector === "education" ? "- Attendance, homework, fees, admissions, results and campus reservations use a separate stored school service. Never infer student records or confirm a payment or visit. Unknown information goes to the school office. Use action none." : ""}
- Use only the facts above. Never invent prices, fees, delivery charges, doctor names or availability outside the opening hours.
- Reply in the customer's language and script: Roman Urdu if they write Roman Urdu, Urdu script if they write Urdu, otherwise English.
- At most one question per message. Under 60 words. No em dashes. Friendly, like a helpful front-desk person texting back.
- If this is your first message in the conversation, begin with one short line saying you are the demo assistant for ${b.name} built by NexusPoint.
- Emergencies (chest pain, severe bleeding, breathing trouble, unconsciousness, an accident, anyone in danger): first tell them to call Rescue 1122 now or go to the nearest emergency department, then say the team is alerted. Stage needs_human.
- If asked whether they are talking to a bot, say honestly that this is ${b.name}'s automated assistant and a team member can take over any time.

Return ONLY a JSON object: {"reply": str, "stage": one of ${JSON.stringify(STAGES)}, "answers": [{"key": str, "value": str}], "summary": str (one or two sentences for the owner), "action": {"type": str, "details": [{"key": str, "value": str}]}}`;
}

export function renderConversation(
  history: { role: string; content: string }[],
  note = "",
): string {
  const lines = history.map(
    (m) => `${m.role === "customer" ? "Customer" : "Business"}: ${m.content}`,
  );
  return `Conversation so far:\n${lines.join("\n")}\n\n${note ? note + "\n" : ""}Write the business's next message as the JSON object.`;
}

const SCRIPT_NOTE: Record<Lang, string> = {
  roman:
    "The customer writes Roman Urdu (Urdu in Latin letters). Write the reply ONLY in Roman Urdu with Latin letters, no Urdu script at all.",
  ur: "The customer writes in Urdu script. Write the reply in Urdu script (English terms like RCT or AM/PM are fine).",
  en: "The customer writes in English. Reply in English.",
};

// Models drift into mixed Roman Urdu and Urdu script; a reply must match the customer's script.
export function wrongScript(reply: string, lang: Lang): boolean {
  const urdu = (reply.match(/[؀-ۿ]/g) ?? []).length;
  const latin = (reply.match(/[A-Za-z]/g) ?? []).length;
  return lang === "ur" ? urdu < latin : urdu > 0;
}

export function validate(raw: Record<string, unknown>): Decision {
  const stage = STAGES.includes(raw.stage as Stage)
    ? (raw.stage as Stage)
    : "qualifying";
  const kv = (x: unknown) =>
    (Array.isArray(x) ? x : [])
      .filter((a) => a && typeof a === "object")
      .map((a) => ({
        key: String((a as { key?: unknown }).key ?? ""),
        value: String((a as { value?: unknown }).value ?? ""),
      }))
      .filter((a) => a.key && a.value);
  const act = (raw.action ?? {}) as { type?: unknown; details?: unknown };
  if (typeof raw.reply !== "string") throw new Error("reply missing");
  return {
    reply: raw.reply,
    stage,
    answers: kv(raw.answers),
    summary: String(raw.summary ?? ""),
    action: {
      type: typeof act.type === "string" ? act.type : "none",
      details: kv(act.details),
    },
  };
}

export type AskFn = (
  system: string,
  user: string,
) => Promise<{ data: Record<string, unknown>; provider: string }>;

export function urgentMessage(text:string):boolean {
  return /\b(chest pain|emergency|bleeding|can't breathe|cannot breathe|unconscious|accident|behosh|saans|khoon)\b|ایمرجنسی|سینے میں درد|سانس|خون|بے ہوش|حادثہ/i.test(text);
}

export async function decide(
  b: BrainBusiness,
  history: { role: string; content: string }[],
  ask: AskFn | null,
  today: string,
): Promise<Decision> {
  const lastCustomer =
    history.filter((m) => m.role === "customer").at(-1)?.content ?? "";
  const lang = detectLang(lastCustomer);
  const first = !history.some((m) => m.role === "business");
  // Urgent messages are handled deterministically before any provider is called.
  if (urgentMessage(lastCustomer)) {
    return {
      ...scriptedDecide(b.sector, b.profile.facts, history),
      source: "scripted",
    };
  }
  if (
    b.sector === "healthcare" &&
    /\b(diagnose|diagnosis|medicine|medication|dosage|treatment|prescribe)\b|تشخیص|دوا|علاج/i.test(
      lastCustomer,
    )
  ) {
    const reply =
      lang === "ur"
        ? "طبی سوال کا جواب ڈاکٹر یا عملہ دے گا۔ نمونہ رپورٹس مریض پورٹل میں دیکھ سکتے ہیں۔"
        : lang === "roman"
          ? "Medical sawal doctor ya staff confirm karega. Sample reports patient portal mein dekh sakte hain."
          : "A clinician or staff member should answer medical questions. You can view clinician-entered sample reports in the patient portal.";
    return {
      reply: (first ? introLine(lang, b.name) : "") + reply,
      stage: "needs_human",
      answers: [],
      summary: "Clinical question requires staff.",
      action: { type: "none", details: [] },
      source: "scripted",
    };
  }
  if (ask) {
    // one corrective retry when the reply comes back in the wrong script
    for (const retry of [false, true]) {
      try {
        const note =
          (retry ? "Your previous reply used the wrong script. " : "") +
          SCRIPT_NOTE[lang];
        const { data, provider } = await ask(
          systemPrompt(b, today),
          renderConversation(history, note),
        );
        const d = validate(data);
        let reply = clean(d.reply);
        if (problems(reply).length) break;
        if (wrongScript(reply, lang)) continue;
        // the demo disclosure is a promise to the owner, so it is never left to the model
        if (first && !/nexus\s*point|نیکسس/i.test(reply))
          reply = introLine(lang, b.name) + reply;
        return { ...d, reply, source: "ai", provider };
      } catch {
        break; /* fall through to the scripted brain */
      }
    }
  }
  try {
    const d = scriptedDecide(b.sector, b.profile.facts, history);
    const reply = clean(d.reply);
    if (!problems(reply).length) return { ...d, reply, source: "scripted" };
  } catch {
    /* fall through to the fixed reply */
  }
  return {
    reply:
      lang === "ur" ? b.profile.fallback_reply.ur : b.profile.fallback_reply.en,
    stage: "needs_human",
    answers: [],
    summary: "Auto-reply failed; please reply to this customer.",
    action: { type: "none", details: [] },
    source: "fallback",
  };
}

// Deterministic sector brain: the demo's safety net when every AI provider is down.
// Keyword intents in English, Roman Urdu and Urdu script; replies built only from the business's
// Google facts. Never invents prices; fee and price questions go to staff.

import type { Decision } from "./brain.ts";

export type Lang = "en" | "roman" | "ur";
type Facts = {
  name: string;
  address: string | null;
  hours: { day: string; hours: string }[];
};

const has = (t: string, re: RegExp) => re.test(t);
const URDU = /[؀-ۿ]/;
const ROMAN =
  /\b(hai|hain|kya|kal|aaj|mil|chahiye|kitni|kitna|kahan|kab|baje|sakte|sakta|karna|mujhe|meri|mera|mere|aap|ji|shukriya|salam|assalam|nahi|haan|mein|bohat|bhi|aur|karwana|hoga|chahta|chahti)\b/i;

export function detectLang(text: string): Lang {
  if (URDU.test(text)) return "ur";
  return ROMAN.test(text) ? "roman" : "en";
}

const I = {
  emergency:
    /\b(chest pain|emergency|bleeding|can't breathe|cannot breathe|unconscious|accident|behosh|saans|khoon)\b|ایمرجنسی|سینے میں درد|سانس|خون|بے ہوش|حادثہ/i,
  bot: /\b(bot|robot|machine|ai|insaan|human)\b|انسان|بوٹ|مشین/i,
  hours:
    /\b(time|timing|timings|hours|open|close|khula|band|kab|baje)\b|اوقات|کھلا|بند|کب/i,
  where: /\b(where|address|location|kahan|pata|map)\b|کہاں|پتہ|لوکیشن/i,
  price:
    /\b(fee|fees|price|rate|charges|kitna|kitni|cost)\b|فیس|قیمت|کتنی|کتنا/i,
  book: /\b(appointment|book|booking|mil sakte|milna|dr|doctor|checkup|visit)\b|اپائنٹمنٹ|بک|ملاقات|ڈاکٹر|وزٹ/i,
  order:
    /\b(order|karahi|naan|roti|biryani|sajji|tikka|chai|tea|delivery|pickup|chahiye|burger|pizza)\b|آرڈر|کڑاہی|نان|چاہیے|ڈیلیوری/i,
  fee: /\b(fee|fees|baqi|due|dues|challan)\b|فیس|باقی|واجب/i,
  admission: /\b(admission|dakhla|enroll|seat|seats)\b|داخلہ|داخلے/i,
  thanks: /\b(thanks|thank you|shukriya|ok|okay|theek)\b|شکریہ|ٹھیک/i,
};

export function introLine(lang: Lang, name: string): string {
  return say(
    lang,
    `(Demo assistant for ${name}, built by NexusPoint.) `,
    `(${name} ka demo assistant, NexusPoint ki taraf se.) `,
    `(${name} کا ڈیمو اسسٹنٹ، نیکسس پوائنٹ کی طرف سے۔) `,
  );
}

function say(lang: Lang, en: string, roman: string, ur: string) {
  return lang === "ur" ? ur : lang === "roman" ? roman : en;
}

function tomorrow(f: Facts): { day: string; hours: string } | null {
  const days = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ];
  const now = new Date(
    new Date().toLocaleString("en-US", { timeZone: "Asia/Karachi" }),
  );
  for (let i = 1; i <= 7; i++) {
    const d = days[(now.getDay() + i) % 7];
    const h = f.hours.find((x) => x.day === d);
    if (h && !/closed/i.test(h.hours)) return h;
  }
  return null;
}

export function scriptedDecide(
  sector: string,
  f: Facts,
  history: { role: string; content: string }[],
): Decision {
  const last =
    history.filter((m) => m.role === "customer").at(-1)?.content ?? "";
  const lang = detectLang(last);
  const t = last.toLowerCase();
  const first = history.filter((m) => m.role === "business").length === 0;
  const intro = first ? introLine(lang, f.name) : "";
  const nx = tomorrow(f);
  const hoursLine = f.hours.length
    ? f.hours.map((h) => `${h.day.slice(0, 3)} ${h.hours}`).join(", ")
    : "";
  const base: Decision = {
    reply: "",
    stage: "qualifying",
    answers: [],
    summary: "",
    action: { type: "none", details: [] },
  };

  if (has(t, I.emergency))
    return {
      ...base,
      stage: "needs_human",
      reply: say(
        lang,
        "Please call Rescue 1122 now or go to the nearest emergency department. Our team has been alerted.",
        "Foran Rescue 1122 par call karein ya qareebi emergency jayein. Hamari team ko ittila de di gayi hai.",
        "فوراً ریسکیو 1122 پر کال کریں یا قریبی ایمرجنسی جائیں۔ ہماری ٹیم کو اطلاع دے دی گئی ہے۔",
      ),
      summary: "EMERGENCY reported; told to call 1122.",
    };
  if (has(t, I.bot))
    return {
      ...base,
      reply:
        intro +
        say(
          lang,
          `Yes, this is ${f.name}'s automated assistant. A team member can take over any time.`,
          `Ji, yeh ${f.name} ka automated assistant hai. Hamari team kabhi bhi baat sambhal sakti hai.`,
          `جی، یہ ${f.name} کا خودکار اسسٹنٹ ہے۔ ہماری ٹیم کسی بھی وقت بات سنبھال سکتی ہے۔`,
        ),
      summary: "Asked if this is a bot.",
    };
  if (has(t, I.where))
    return {
      ...base,
      reply:
        intro +
        say(
          lang,
          `We are at ${f.address}. Would you like to book a time?`,
          `Hum ${f.address} par hain. Kya aap time book karna chahenge?`,
          `ہم ${f.address} پر ہیں۔ کیا آپ وقت بک کرنا چاہیں گے؟`,
        ),
      summary: "Asked for the location.",
    };
  if (sector === "education" && has(t, I.fee) && /ayesha|عائشہ|6/i.test(t))
    return {
      ...base,
      stage: "warm",
      reply:
        intro +
        say(
          lang,
          "Ayesha Khan, Class 6-B: the September fee is pending, due 10 October. You can pay by JazzCash, Easypaisa or bank.",
          "Ayesha Khan, Class 6-B: September ki fee baqi hai, due 10 October. JazzCash, Easypaisa ya bank se jama kar sakte hain.",
          "عائشہ خان، کلاس 6-بی: ستمبر کی فیس باقی ہے، آخری تاریخ 10 اکتوبر۔ جاز کیش، ایزی پیسہ یا بینک سے جمع کروا سکتے ہیں۔",
        ),
      answers: [{ key: "student", value: "Ayesha Khan, 6-B" }],
      summary: "Parent checked Ayesha Khan's pending September fee.",
      action: {
        type: "fee_lookup",
        details: [
          { key: "Student", value: "Ayesha Khan, 6-B" },
          { key: "Status", value: "September pending" },
          { key: "Due", value: "10 October" },
        ],
      },
    };
  if (has(t, I.price))
    return {
      ...base,
      stage: "needs_human",
      reply:
        intro +
        say(
          lang,
          "A team member will confirm the exact fee for you shortly. Anything else I can help with?",
          "Exact fee hamari team thori der mein confirm kar degi. Aur kuch madad?",
          "درست فیس ہماری ٹیم تھوڑی دیر میں بتا دے گی۔ اور کوئی مدد؟",
        ),
      summary: "Asked about prices; needs staff to confirm.",
    };
  // Connected healthcare reservations are handled by the server booking service.
  // This pure fallback cannot infer doctor availability or create a reservation.
  if (sector === "healthcare" && has(t, I.book))
    return {
      ...base,
      stage: "needs_human",
      reply:
        intro +
        say(
          lang,
          "Choose an available sample doctor and time in your patient portal. Staff can help with the clinic's actual availability.",
          "Patient portal mein available sample doctor aur waqt select karein. Clinic ki asal availability staff confirm karega.",
          "مریض پورٹل میں دستیاب نمونہ ڈاکٹر اور وقت منتخب کریں۔ کلینک کے اصل اوقات کی تصدیق عملہ کرے گا۔",
        ),
      summary:
        "Booking requires stored doctor availability and a saved reservation.",
    };
  if (sector === "food" && has(t, I.order))
    return {
      ...base,
      stage: "warm",
      reply:
        intro +
        say(
          lang,
          "Got it, order noted ✓ Delivery or pickup? If delivery, share the address and the restaurant will confirm the total and time.",
          "Order note ho gaya ✓ Delivery ya pickup? Delivery ho to address bhej dein, restaurant total aur time confirm kar dega.",
          "آرڈر نوٹ ہو گیا ✓ ڈیلیوری یا پک اپ؟ ڈیلیوری ہو تو پتہ بھیج دیں، ریسٹورنٹ کل رقم اور وقت کنفرم کر دے گا۔",
        ),
      answers: [{ key: "items", value: last.slice(0, 120) }],
      summary: `Order: ${last.slice(0, 80)}`,
      action: {
        type: "order",
        details: [{ key: "Items", value: last.slice(0, 120) }],
      },
    };
  if (sector === "education" && has(t, I.admission))
    return {
      ...base,
      stage: "warm",
      reply:
        intro +
        say(
          lang,
          `Admissions are open. Would you like to visit the campus${nx ? ` on ${nx.day}` : ""}? Please share the class you are asking about.`,
          `Admissions jari hain. Kya aap campus visit karna chahenge${nx ? ` ${nx.day} ko` : ""}? Kis class ke liye pooch rahe hain?`,
          `داخلے جاری ہیں۔ کیا آپ کیمپس وزٹ کرنا چاہیں گے؟ کس کلاس کے لیے پوچھ رہے ہیں؟`,
        ),
      summary: "Admission enquiry; offered a campus visit.",
      action: {
        type: "visit",
        details: [{ key: "Interest", value: "Admission" }],
      },
    };
  if (has(t, I.hours))
    return {
      ...base,
      reply:
        intro +
        (hoursLine
          ? say(
              lang,
              `Our hours: ${hoursLine}. Can I help you book?`,
              `Hamare auqaat: ${hoursLine}. Kya booking kar doon?`,
              `ہمارے اوقات: ${hoursLine}۔ کیا بکنگ کر دوں؟`,
            )
          : say(
              lang,
              "A team member will confirm today's timings shortly.",
              "Aaj ke auqaat team thori der mein confirm kar degi.",
              "آج کے اوقات ٹیم تھوڑی دیر میں بتا دے گی۔",
            )),
      summary: "Asked for opening hours.",
    };
  if (has(t, I.thanks))
    return {
      ...base,
      stage: "cold",
      reply: say(
        lang,
        "You're welcome! Message any time.",
        "Koi baat nahi! Kabhi bhi message karein.",
        "کوئی بات نہیں! کسی بھی وقت میسج کریں۔",
      ),
      summary: "Conversation closed politely.",
    };
  return {
    ...base,
    reply:
      intro +
      say(
        lang,
        `Welcome to ${f.name}! How can I help: timings, location or a booking?`,
        `${f.name} mein khush aamdeed! Kaise madad karoon: timings, location ya booking?`,
        `${f.name} میں خوش آمدید! کیسے مدد کروں: اوقات، لوکیشن یا بکنگ؟`,
      ),
    summary: "Opened the conversation.",
  };
}

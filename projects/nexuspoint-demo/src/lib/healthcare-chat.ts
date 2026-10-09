import { randomUUID } from "node:crypto";
import {
  rest,
  updateConversation,
  type Business,
  type Conversation,
} from "./db.ts";
import {
  availability,
  book,
  ensureHealthcare,
  ensurePatient,
  rpc,
} from "./healthcare.ts";
import {
  dateLabel,
  dayAfter,
  localDate,
  timeLabel,
  type Appointment,
  type Choice,
  type Doctor,
} from "./healthcare-types.ts";
import { detectLang, type Lang } from "./scripted.ts";

type Reply = {
  reply: string;
  cards: Choice[];
  stage: "qualifying" | "warm" | "needs_human";
  summary: string;
  appointment?: Appointment;
};
export async function healthcareChat(
  b: Business,
  c: Conversation,
  text: string,
  choice?: Choice,
): Promise<Reply | null> {
  const previousLang = c.booking_context?.language;
  const lang: Lang =
      choice && previousLang && ["en", "roman", "ur"].includes(previousLang)
        ? (previousLang as Lang)
        : detectLang(text),
    say = (en: string, roman: string, ur: string) =>
      lang === "ur" ? ur : lang === "roman" ? roman : en;
  // General front-desk questions still work during a booking conversation.
  if (
    !choice &&
    /\b(fee|fees|price|cost|charges|location|address|where|bot|robot|human)\b|فیس|قیمت|کہاں|پتہ|بوٹ/i.test(
      text,
    )
  )
    return null;
  // Medical questions and emergencies continue through the existing handoff path.
  if (
    /chest pain|bleeding|can't breathe|cannot breathe|emergency|unconscious|سینے|سانس|خون|behosh|saans|diagnos|medicine|dosage|medical advice|علاج|دوا/i.test(
      text,
    ) &&
    !choice
  )
    return null;
  const context = { ...(c.booking_context ?? {}) };
  context.language = lang;
  const intent =
    /\bdr\b|doctor|consultant|consultation|appointment|book|checkup|availability|available|slot|visit|phone|video|call|mil sak|milna|ڈاکٹر|اپائنٹمنٹ|بکنگ|ملاقات|دستیاب|کال|cancel|resched|منسوخ|وقت بدل/i.test(
      text,
    );
  if (
    !choice &&
    !intent &&
    !context.doctor &&
    !/report|record|رپورٹ/i.test(text)
  )
    return null;
  await ensureHealthcare(b);
  const patient = await ensurePatient(b, c.visitor);
  const doctors = await rest<Doctor>(
    "GET",
    `demo_doctors?slug=eq.${encodeURIComponent(b.slug)}&active=eq.true&order=id.asc`,
  );
  const apps = await rest<Appointment>(
    "GET",
    `demo_appointments?slug=eq.${encodeURIComponent(b.slug)}&patient_id=eq.${patient.id}&status=eq.confirmed&order=starts_at.asc`,
  );
  const base = (
    reply: string,
    cards: Choice[] = [],
    stage: Reply["stage"] = "qualifying",
  ): Reply => ({
    reply,
    cards,
    stage,
    summary: "Patient using the connected demo booking assistant.",
  });
  if (/report|record|رپورٹ/i.test(text) && !choice)
    return base(
      say(
        "Your published sample diagnoses, prescriptions and reports are in your patient portal. Open Health records to view or print them.",
        "Aap ki sample reports, diagnoses aur prescriptions patient portal ke Health records mein hain. Wahan dekh ya print kar sakte hain.",
        "آپ کی شائع شدہ نمونہ رپورٹس، تشخیص اور نسخے مریض پورٹل کے طبی ریکارڈ میں ہیں۔ وہاں دیکھیں یا پرنٹ کریں۔",
      ),
    );
  if (choice?.kind === "cancel") {
    const a = apps.find((a) => a.id === choice.value);
    if (!a)
      return base(
        say(
          "That booking is no longer available to cancel.",
          "Yeh booking ab cancel nahi ho sakti.",
          "یہ بکنگ اب منسوخ نہیں ہو سکتی۔",
        ),
      );
    await rpc("demo_change_appointment", {
      p_slug: b.slug,
      p_id: a.id,
      p_status: "cancelled",
    });
    await updateConversation(c.id, {
      booking_context: null,
      action: { type: "none", details: [] },
    });
    return base(
      say(
        "Your demo appointment is cancelled. The slot is available again.",
        "Aap ki demo appointment cancel ho gayi. Slot dobara khali hai.",
        "آپ کی ڈیمو اپائنٹمنٹ منسوخ ہو گئی۔ وقت دوبارہ دستیاب ہے۔",
      ),
      [],
      "warm",
    );
  }
  if (choice?.kind === "reschedule") {
    const a = apps.find((a) => a.id === choice.value);
    if (!a)
      return base(
        say(
          "That appointment cannot be rescheduled.",
          "Yeh appointment reschedule nahi ho sakti.",
          "یہ اپائنٹمنٹ تبدیل نہیں ہو سکتی۔",
        ),
      );
    context.reschedule = a.id;
    context.doctor = a.doctor_id;
    context.mode = a.mode;
    delete context.date;
  } else if (/cancel|resched|منسوخ|وقت بدل/i.test(text) && !choice) {
    const cancel = /cancel|منسوخ/i.test(text);
    return base(
      apps.length
        ? say(
            "Select the demo appointment to change.",
            "Jo demo appointment badalni hai woh select karein.",
            "جس ڈیمو اپائنٹمنٹ کو تبدیل کرنا ہے اسے منتخب کریں۔",
          )
        : say(
            "You have no confirmed demo appointments yet.",
            "Abhi aap ki koi confirmed demo appointment nahi.",
            "ابھی آپ کی کوئی تصدیق شدہ ڈیمو اپائنٹمنٹ نہیں ہے۔",
          ),
      apps.map((a) => ({
        kind: cancel ? "cancel" : "reschedule",
        value: a.id,
        label: `${dateLabel(a.starts_at)} · ${timeLabel(a.starts_at)}`,
      })),
    );
  }
  if (choice?.kind === "doctor") {
    if (!doctors.some((d) => d.id === choice.value))
      return base(
        say(
          "Please choose a listed sample doctor.",
          "List mein se sample doctor select karein.",
          "فہرست میں سے نمونہ ڈاکٹر منتخب کریں۔",
        ),
      );
    context.doctor = choice.value;
  }
  if (
    choice?.kind === "mode" &&
    ["in_person", "phone", "video"].includes(choice.value)
  )
    context.mode = choice.value;
  const matched = doctors.find(
    (d) =>
      text.toLowerCase().includes(d.name.toLowerCase().replace("dr. ", "")) ||
      new RegExp(`\\b${d.name.replace("Dr. ", "").split(" ")[0]}\\b`, "i").test(
        text,
      ) ||
      text.toLowerCase().includes(d.specialty.toLowerCase()),
  );
  const requestedName = text.match(/\bdr\.?\s+([a-z]+)\b/i)?.[1];
  if (
    !choice &&
    requestedName &&
    !/^(sahab|sahib|doctor)$/i.test(requestedName) &&
    !matched
  ) {
    await updateConversation(c.id, { booking_context: null });
    return base(
      say(
        "That doctor is not in the sample directory. Staff must confirm the clinic’s actual doctors and availability.",
        "Yeh doctor sample directory mein nahi. Clinic ke asal doctors aur availability staff confirm karega.",
        "یہ ڈاکٹر نمونہ فہرست میں نہیں۔ کلینک کے اصل ڈاکٹروں اور اوقات کی تصدیق عملہ کرے گا۔",
      ),
      [],
      "needs_human",
    );
  }
  if (matched && !choice) context.doctor = matched.id;
  if (/video|ویڈیو/i.test(text)) context.mode = "video";
  else if (/phone|call|کال/i.test(text)) context.mode = "phone";
  context.mode = context.mode ?? "in_person";
  const iso = text.match(/\b20\d{2}-\d{2}-\d{2}\b/)?.[0];
  if (iso) context.date = iso;
  else if (/tomorrow|kal|کل/i.test(text)) context.date = dayAfter(localDate());
  else if (/today|aaj|آج/i.test(text)) context.date = localDate();
  else {
    const days = [
      "sunday",
      "monday",
      "tuesday",
      "wednesday",
      "thursday",
      "friday",
      "saturday",
    ];
    const wanted = days.findIndex((d) => text.toLowerCase().includes(d));
    if (wanted >= 0) {
      let date = localDate();
      while (new Date(`${date}T12:00:00+05:00`).getUTCDay() !== wanted)
        date = dayAfter(date);
      context.date = date;
    }
  }
  const doctor = doctors.find((d) => d.id === context.doctor);
  if (!doctor) {
    await updateConversation(c.id, { booking_context: context });
    return base(
      say(
        "Choose a sample consultant. These are fictional demo profiles, not the clinic’s confirmed doctors.",
        "Sample consultant select karein. Yeh demo profiles hain, clinic ke confirmed doctors nahi.",
        "نمونہ کنسلٹنٹ منتخب کریں۔ یہ فرضی ڈیمو پروفائل ہیں، کلینک کے تصدیق شدہ ڈاکٹر نہیں۔",
      ),
      doctors.map((d) => ({
        kind: "doctor",
        value: d.id,
        label: `${d.name} · ${d.specialty}`,
      })),
    );
  }
  let date = context.date ?? dayAfter(localDate());
  let slots = await availability(b, doctor, date);
  if (!context.date) {
    for (let n = 0; n < 12 && !slots.length; n++) {
      date = dayAfter(date);
      slots = await availability(b, doctor, date);
    }
  }
  context.date = date;
  // A typed time is accepted only when it matches an actual available slot.
  let selected = choice?.kind === "slot" ? choice.value : "";
  if (!choice) {
    const time = text.match(/\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b/i);
    if (time) {
      const h = (+time[1] % 12) + (time[3].toLowerCase() === "pm" ? 12 : 0);
      selected =
        slots.find(
          (s) =>
            new Date(s).getTime() ===
            new Date(
              `${date}T${String(h).padStart(2, "0")}:${time[2] ?? "00"}:00+05:00`,
            ).getTime(),
        ) ?? "";
    }
  }
  if (selected) {
    try {
      let a: Appointment;
      if (context.reschedule) {
        if (!apps.some((a) => a.id === context.reschedule))
          throw new Error("Appointment not found");
        a = (
          await rpc<Appointment[]>("demo_change_appointment", {
            p_slug: b.slug,
            p_id: context.reschedule,
            p_status: "confirmed",
            p_start: selected,
            p_doctor: doctor.id,
            p_mode: context.mode,
          })
        )[0];
      } else
        a = await book(
          b,
          patient.id,
          doctor.id,
          selected,
          context.mode,
          c.channel === "web" ? "chat" : "whatsapp",
          "Booked through demo assistant",
          context.request ?? randomUUID(),
        );
      await updateConversation(c.id, {
        booking_context: null,
        action: {
          type: "booking",
          details: [
            { key: "Doctor", value: doctor.name },
            {
              key: "Time",
              value: `${dateLabel(a.starts_at)} ${timeLabel(a.starts_at)} PKT`,
            },
            { key: "Appointment", value: a.id },
          ],
        },
      });
      return {
        ...base(
          say(
            `Demo booking confirmed: ${doctor.name}, ${dateLabel(a.starts_at)}, ${timeLabel(a.starts_at)} PKT. See your patient portal for details. This is not a real clinic appointment.`,
            `Demo booking confirm: ${doctor.name}, ${dateLabel(a.starts_at)}, ${timeLabel(a.starts_at)} PKT. Patient portal mein details hain. Yeh asli clinic appointment nahi hai.`,
            `ڈیمو بکنگ تصدیق شدہ: ${doctor.name}، ${dateLabel(a.starts_at, "ur")}، ${timeLabel(a.starts_at, "ur")}۔ تفصیل مریض پورٹل میں ہے۔ یہ اصل کلینک کی اپائنٹمنٹ نہیں۔`,
          ),
          [],
          "warm",
        ),
        appointment: a,
      };
    } catch {
      slots = await availability(b, doctor, date);
      await updateConversation(c.id, {
        booking_context: { ...context, request: randomUUID() },
      });
      return base(
        say(
          "That slot is unavailable now. Your existing booking is unchanged. Choose another available time.",
          "Yeh slot ab khali nahi. Purani booking wahi hai. Koi aur waqt select karein.",
          "یہ وقت اب دستیاب نہیں۔ سابقہ بکنگ برقرار ہے۔ دوسرا دستیاب وقت منتخب کریں۔",
        ),
        slots
          .slice(0, 8)
          .map((s) => ({ kind: "slot", value: s, label: timeLabel(s, lang) })),
      );
    }
  }
  await updateConversation(c.id, {
    booking_context: { ...context, request: context.request ?? randomUUID() },
  });
  const modeCards: Choice[] = doctor.modes.map((m) => ({
    kind: "mode",
    value: m,
    label:
      m === "in_person"
        ? say("In person", "Clinic mein", "کلینک میں")
        : m === "phone"
          ? say("Phone call", "Phone call", "فون کال")
          : say("Video call", "Video call", "ویڈیو کال"),
  }));
  return base(
    slots.length
      ? say(
          `${doctor.name}: available sample slots on ${dateLabel(`${date}T12:00:00+05:00`)}. Choose a consultation mode and time. All times are PKT.`,
          `${doctor.name}: ${dateLabel(`${date}T12:00:00+05:00`)} ke sample slots khali hain. Mode aur waqt select karein. Sab waqt PKT hain.`,
          `${doctor.name} کے ${dateLabel(`${date}T12:00:00+05:00`, "ur")} کے نمونہ اوقات دستیاب ہیں۔ ملاقات کی قسم اور وقت منتخب کریں۔`,
        )
      : say(
          "No available slots on that day. Try another date in your patient portal.",
          "Us din koi slot khali nahi. Patient portal mein koi aur din select karein.",
          "اس دن وقت دستیاب نہیں۔ مریض پورٹل میں دوسری تاریخ منتخب کریں۔",
        ),
    [
      ...modeCards,
      ...slots.slice(0, 8).map((s) => ({
        kind: "slot" as const,
        value: s,
        label: timeLabel(s, lang),
      })),
    ],
  );
}

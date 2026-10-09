"use client";
import { useEffect, useRef, useState, type ReactNode } from "react";
import {
  dateLabel,
  dayAfter,
  emptyRecord,
  localDate,
  timeLabel,
  type Appointment,
  type ClinicalRecord,
  type HealthcareState,
  type Patient,
  type RecordData,
  type Schedule,
} from "@/lib/healthcare-types";
import type { Run, Translator } from "./Healthcare";

const paths: Record<string, string> = {
  overview: "M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z",
  heart:
    "M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z",
  calendar:
    "M5 4h14a2 2 0 0 1 2 2v14H3V6a2 2 0 0 1 2-2ZM7 2v5M17 2v5M3 10h18M7 14h2M13 14h2M7 17h2",
  messages: "M21 11a8 8 0 0 1-8 8H7l-5 3V11a9 9 0 1 1 19 0ZM7 10h10M7 14h6",
  doctors:
    "M9 3v5a4 4 0 0 0 8 0V3M7 3h4M15 3h4M13 12v3a5 5 0 0 1-10 0v-3M3 10a2 2 0 1 0 0 4a2 2 0 0 0 0-4",
  records: "M6 3h9l4 4v14H6ZM14 3v5h5M9 12h7M9 16h7",
  patients: "M12 12a4 4 0 1 0 0-8a4 4 0 0 0 0 8ZM4 21v-2a8 8 0 0 1 16 0v2",
  queue: "M8 5h13M8 12h13M8 19h13M3 5h1M3 12h1M3 19h1",
  shield: "M12 2 3 6v6c0 5 9 10 9 10s9-5 9-10V6ZM8 12l3 3 5-6",
  plus: "M12 5v14M5 12h14",
  arrow: "M5 12h14M14 7l5 5-5 5",
  theme:
    "M12 3v2M12 19v2M3 12h2M19 12h2M5 5l2 2M17 17l2 2M5 19l2-2M17 7l2-2M16 12a4 4 0 1 0-8 0a4 4 0 0 0 8 0",
  pulse: "M2 12h5l3-8 4 16 3-8h5",
  drop: "M12 2s-7 8-7 13a7 7 0 0 0 14 0c0-5-7-13-7-13Z",
  video: "M3 6h12v12H3ZM15 10l6-3v10l-6-3",
  phone: "M7 3H3v4c0 8 6 14 14 14h4v-4l-5-2-2 2c-3-1-6-4-7-7l2-2Z",
  print: "M7 8V3h10v5M7 17H3V8h18v9h-4M7 13h10v8H7Z",
  search: "M10 17a7 7 0 1 0 0-14a7 7 0 0 0 0 14ZM15 15l6 6",
};
export function Icon({ name }: { name: string }) {
  const alias =
    name === "appointments" || name === "schedules"
      ? "calendar"
      : name === "inbox"
        ? "messages"
        : name;
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d={paths[alias] ?? paths.overview} />
    </svg>
  );
}
export function Avatar({
  name,
  large = false,
}: {
  name: string;
  large?: boolean;
}) {
  return (
    <span className={`hc-avatar ${large ? "large" : ""}`} aria-hidden="true">
      {name
        .replace(/^Dr\. /, "")
        .split(" ")
        .slice(0, 2)
        .map((s) => s[0])
        .join("")}
    </span>
  );
}
const modes = (mode: string, S: Translator) =>
  mode === "video"
    ? S("Video call", "ویڈیو کال")
    : mode === "phone"
      ? S("Phone call", "فون کال")
      : S("In person", "کلینک میں");
export function statusLabel(status: string, S: Translator) {
  const labels: Record<string, [string, string]> = {
    confirmed: ["Confirmed", "تصدیق شدہ"],
    checked_in: ["Checked in", "پہنچ گیا"],
    in_consultation: ["In consultation", "ملاقات جاری"],
    completed: ["Completed", "مکمل"],
    cancelled: ["Cancelled", "منسوخ"],
    no_show: ["No-show", "غیر حاضر"],
  };
  return labels[status] ? S(...labels[status]) : status;
}
export function Modal({
  children,
  title,
  onClose,
  small = false,
}: {
  children: ReactNode;
  title: string;
  onClose: () => void;
  small?: boolean;
}) {
  const ref = useRef<HTMLElement>(null);
  const closeRef = useRef(onClose);
  closeRef.current = onClose;
  useEffect(() => {
    const before = document.activeElement as HTMLElement | null;
    ref.current?.focus();
    const listener = (e: KeyboardEvent) => {
      if (e.key === "Escape") closeRef.current();
      if (e.key === "Tab") {
        const nodes = Array.from(
          ref.current?.querySelectorAll<HTMLElement>(
            "button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),a[href]",
          ) ?? [],
        );
        const first = nodes[0],
          last = nodes.at(-1);
        if (
          e.shiftKey &&
          (document.activeElement === first ||
            document.activeElement === ref.current)
        ) {
          e.preventDefault();
          last?.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first?.focus();
        }
      }
    };
    document.addEventListener("keydown", listener);
    return () => {
      document.removeEventListener("keydown", listener);
      before?.focus();
    };
  }, []);
  return (
    <div
      className="hc-modal-backdrop"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <section
        className={`hc-modal ${small ? "small" : ""}`}
        ref={ref}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        <div className="hc-modal-title">
          <h2>{title}</h2>
          <button
            className="hc-icon-btn"
            onClick={onClose}
            aria-label="Close / بند کریں"
          >
            ×
          </button>
        </div>
        {children}
      </section>
    </div>
  );
}

export function DoctorDirectory({
  state,
  S,
  onBook,
}: {
  state: HealthcareState;
  S: Translator;
  onBook: (id: string) => void;
}) {
  const [search, setSearch] = useState("");
  const doctors = state.doctors.filter(
    (d) =>
      d.active &&
      `${d.name} ${d.specialty}`.toLowerCase().includes(search.toLowerCase()),
  );
  return (
    <>
      <div className="hc-section-toolbar">
        <label className="hc-search">
          <Icon name="search" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={S(
              "Search a doctor or specialty",
              "ڈاکٹر یا تخصص تلاش کریں",
            )}
            aria-label={S("Search doctors", "ڈاکٹر تلاش کریں")}
          />
        </label>
        <span className="hc-caption">
          {S(
            "All profiles and schedules are illustrative.",
            "تمام پروفائل اور اوقات نمونہ ہیں۔",
          )}
        </span>
      </div>
      <div className="hc-doctor-grid">
        {doctors.map((d, i) => (
          <article className="hc-card hc-doctor-card" key={d.id}>
            <div className={`hc-doctor-portrait portrait-${i % 4}`}>
              <Avatar name={d.name} large />
              <span className="hc-pill">
                {S("Sample consultant", "نمونہ کنسلٹنٹ")}
              </span>
            </div>
            <h2>{d.name}</h2>
            <p className="hc-specialty">{d.specialty}</p>
            <p className="hc-caption">{d.bio}</p>
            <div className="hc-tags">
              {d.modes.map((m) => (
                <span key={m}>{modes(m, S)}</span>
              ))}
            </div>
            <button className="hc-btn" onClick={() => onBook(d.id)}>
              {S("View availability", "دستیاب اوقات دیکھیں")}
              <Icon name="arrow" />
            </button>
          </article>
        ))}
      </div>
      {!doctors.length && (
        <p className="hc-empty">
          {S(
            "No matching doctors. Try another search.",
            "کوئی ڈاکٹر نہیں ملا۔ دوبارہ تلاش کریں۔",
          )}
        </p>
      )}
    </>
  );
}

export function AppointmentList({
  appointments,
  state,
  lang,
  S,
  compact = false,
  staff = false,
  busy = false,
  onBook,
  onStatus,
  onCancel,
  onReschedule,
  onRecord,
  onCall,
}: {
  appointments: Appointment[];
  state: HealthcareState;
  lang: string;
  S: Translator;
  compact?: boolean;
  staff?: boolean;
  busy?: boolean;
  onBook?: () => void;
  onStatus?: (a: Appointment, s: string) => void;
  onCancel?: (a: Appointment) => void;
  onReschedule?: (a: Appointment) => void;
  onRecord?: (a: Appointment) => void;
  onCall?: (a: Appointment) => void;
}) {
  if (!appointments.length)
    return (
      <div className="hc-empty">
        <Icon name="calendar" />
        <h3>{S("No appointments here yet", "ابھی کوئی اپائنٹمنٹ نہیں")}</h3>
        <p>
          {S(
            "Book a sample visit to see the connected workflow.",
            "مربوط ورک فلو دیکھنے کے لیے نمونہ ملاقات بک کریں۔",
          )}
        </p>
        {onBook && (
          <button className="hc-btn secondary" onClick={onBook}>
            {S("Book a visit", "ملاقات بک کریں")}
          </button>
        )}
      </div>
    );
  return (
    <div className={`hc-appointment-list ${compact ? "compact" : ""}`}>
      {appointments.map((a) => {
        const d = state.doctors.find((d) => d.id === a.doctor_id),
          p = state.patients.find((p) => p.id === a.patient_id);
        return (
          <article className={`hc-appointment ${a.status}`} key={a.id}>
            <div className="hc-appointment-date">
              <b>{timeLabel(a.starts_at, lang)}</b>
              <small>{dateLabel(a.starts_at, lang)}</small>
            </div>
            <Avatar name={d?.name ?? "Doctor"} />
            <div className="hc-appointment-info">
              <h3>{staff ? p?.name : d?.name}</h3>
              <p>
                {staff ? d?.name : d?.specialty} · {modes(a.mode, S)}
              </p>
              {!compact && (
                <small>
                  {a.reason || S("Sample consultation", "نمونہ ملاقات")} ·{" "}
                  {S("Source", "ذریعہ")}: {a.source}
                </small>
              )}
              {a.queue_number !== null && (
                <span className="hc-queue-token">
                  {S("Queue token", "قطار نمبر")} {a.queue_number}
                </span>
              )}
            </div>
            <span className={`hc-status ${a.status}`}>
              {statusLabel(a.status, S)}
            </span>
            {!compact && (
              <div className="hc-appointment-actions">
                {a.status === "confirmed" && (
                  <>
                    {onReschedule && (
                      <button
                        className="hc-link"
                        disabled={busy}
                        onClick={() => onReschedule(a)}
                      >
                        {S("Reschedule", "وقت بدلیں")}
                      </button>
                    )}
                    {onCancel && (
                      <button
                        className="hc-link danger"
                        disabled={busy}
                        onClick={() => onCancel(a)}
                      >
                        {S("Cancel", "منسوخ کریں")}
                      </button>
                    )}
                    {staff && onStatus && (
                      <>
                        <button
                          className="hc-btn secondary"
                          disabled={
                            busy ||
                            localDate(a.starts_at) !==
                              localDate(state.server_time)
                          }
                          onClick={() => onStatus(a, "checked_in")}
                        >
                          {S("Check in", "آمد درج کریں")}
                        </button>
                        <button
                          className="hc-link"
                          disabled={busy}
                          onClick={() => onStatus(a, "no_show")}
                        >
                          {S("No-show", "غیر حاضر")}
                        </button>
                        <button
                          className="hc-link danger"
                          disabled={busy}
                          onClick={() => onStatus(a, "cancelled")}
                        >
                          {S("Cancel", "منسوخ کریں")}
                        </button>
                      </>
                    )}
                  </>
                )}
                {staff &&
                  onStatus &&
                  ["confirmed", "checked_in"].includes(a.status) && (
                    <button
                      className="hc-btn"
                      disabled={busy}
                      onClick={() => onStatus(a, "in_consultation")}
                    >
                      {S("Start visit", "ملاقات شروع")}
                    </button>
                  )}
                {staff && onStatus && a.status === "in_consultation" && (
                  <button
                    className="hc-btn"
                    disabled={busy}
                    onClick={() => onStatus(a, "completed")}
                  >
                    {S("Complete visit", "ملاقات مکمل")}
                  </button>
                )}
                {onRecord &&
                  ["in_consultation", "completed"].includes(a.status) && (
                    <button
                      className="hc-btn secondary"
                      onClick={() => onRecord(a)}
                    >
                      {S("Write visit note", "ملاقات کا نوٹ")}
                    </button>
                  )}
                {onCall &&
                  a.mode !== "in_person" &&
                  !["cancelled", "no_show", "completed"].includes(a.status) && (
                    <button
                      className="hc-btn secondary"
                      onClick={() => onCall(a)}
                    >
                      <Icon name={a.mode === "video" ? "video" : "phone"} />
                      {S("Try demo call", "نمونہ کال")}
                    </button>
                  )}
              </div>
            )}
          </article>
        );
      })}
    </div>
  );
}

export function BookingDialog({
  state,
  initial,
  credentials,
  S,
  lang,
  run,
  busy,
  onClose,
}: {
  state: HealthcareState;
  initial: { doctorId?: string; appointment?: Appointment; patientId?: string };
  credentials: Record<string, string>;
  S: Translator;
  lang: string;
  run: Run;
  busy: boolean;
  onClose: () => void;
}) {
  const [doctorId, setDoctorId] = useState(
      initial.doctorId ?? state.doctors[0]?.id ?? "",
    ),
    [patientId, setPatientId] = useState(initial.patientId ?? state.patient.id);
  const [date, setDate] = useState(
      initial.appointment
        ? localDate(initial.appointment.starts_at)
        : dayAfter(localDate(state.server_time)),
    ),
    [mode, setMode] = useState(initial.appointment?.mode ?? "in_person"),
    [selected, setSelected] = useState("");
  const [slots, setSlots] = useState<string[]>([]),
    [loading, setLoading] = useState(true),
    [error, setError] = useState(""),
    [reason, setReason] = useState(initial.appointment?.reason ?? "");
  const request = useRef(crypto.randomUUID());
  const doctor = state.doctors.find((d) => d.id === doctorId);
  useEffect(() => {
    let live = true;
    const load = async () => {
      try {
        const q = new URLSearchParams({ ...credentials, doctorId, date });
        const r = await fetch(`/api/healthcare?${q}`);
        const d = await r.json();
        if (!r.ok) throw new Error(d.error);
        if (live) {
          setSlots(d.slots);
          setLoading(false);
        }
      } catch (e) {
        if (live) {
          setError(e instanceof Error ? e.message : "Connection problem");
          setLoading(false);
        }
      }
    };
    setLoading(true);
    setSelected("");
    setError("");
    load();
    const id = setInterval(() => {
      if (document.visibilityState === "visible") load();
    }, 2000);
    return () => {
      live = false;
      clearInterval(id);
    };
  }, [
    credentials.slug,
    credentials.t,
    credentials.visitor,
    credentials.role,
    doctorId,
    date,
  ]);
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!selected) return;
    setError("");
    try {
      await run(
        initial.appointment
          ? {
              action: "appointment",
              id: initial.appointment.id,
              start: selected,
              doctorId,
              mode,
            }
          : {
              action: "book",
              doctorId,
              patientId,
              start: selected,
              mode,
              reason,
              requestId: request.current,
            },
      );
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not save booking");
      setSelected("");
    }
  }
  if (
    initial.appointment &&
    !["confirmed", "checked_in"].includes(initial.appointment.status)
  )
    return (
      <Modal
        title={S("Appointment details", "اپائنٹمنٹ کی تفصیل")}
        onClose={onClose}
      >
        <AppointmentList
          appointments={[initial.appointment]}
          state={state}
          lang={lang}
          S={S}
          compact
        />
        <p className="hc-caption">
          {
            state.patients.find((p) => p.id === initial.appointment?.patient_id)
              ?.name
          }{" "}
          · {statusLabel(initial.appointment.status, S)}
        </p>
        <p>{initial.appointment.reason}</p>
        <p className="hc-caption">
          {S(
            "This appointment is final. Published visit notes are available in the patient’s health history.",
            "یہ اپائنٹمنٹ مکمل ہو چکی ہے۔ شائع شدہ نوٹس مریض کی طبی تاریخ میں ہیں۔",
          )}
        </p>
      </Modal>
    );
  return (
    <Modal
      title={
        initial.appointment
          ? S("Reschedule appointment", "اپائنٹمنٹ کا وقت بدلیں")
          : S("Book a sample appointment", "نمونہ اپائنٹمنٹ بک کریں")
      }
      onClose={onClose}
    >
      <p className="hc-caption">
        {S(
          "These doctors and times are fictional. Your selection is saved only in the demo. All times are PKT.",
          "ڈاکٹر اور اوقات فرضی ہیں۔ انتخاب صرف ڈیمو میں محفوظ ہو گا۔ تمام اوقات پاکستانی وقت میں ہیں۔",
        )}
      </p>
      <form onSubmit={submit}>
        <div className="hc-form-grid">
          <label>
            {S("Consultant", "کنسلٹنٹ")}
            <select
              value={doctorId}
              onChange={(e) => {
                setDoctorId(e.target.value);
                setMode("in_person");
              }}
            >
              {state.doctors
                .filter((d) => d.active)
                .map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name} · {d.specialty}
                  </option>
                ))}
            </select>
          </label>
          {credentials.role !== "patient" && (
            <label>
              {S("Patient", "مریض")}
              <select
                value={patientId}
                disabled={!!initial.appointment}
                onChange={(e) => setPatientId(e.target.value)}
              >
                {state.patients.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </label>
          )}
          <label>
            {S("Visit date", "ملاقات کی تاریخ")}
            <input
              type="date"
              value={date}
              min={localDate(state.server_time)}
              max={dayAfter(localDate(state.server_time), 13)}
              onChange={(e) => setDate(e.target.value)}
              required
            />
          </label>
          <label>
            {S("Consultation mode", "ملاقات کی قسم")}
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value as typeof mode)}
            >
              {doctor?.modes.map((m) => (
                <option key={m} value={m}>
                  {modes(m, S)}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div className="hc-booking-days">
          {Array.from({ length: 7 }, (_, i) =>
            dayAfter(localDate(state.server_time), i),
          ).map((d) => (
            <button
              type="button"
              className={date === d ? "selected" : ""}
              key={d}
              onClick={() => setDate(d)}
            >
              <small>
                {new Date(`${d}T12:00:00+05:00`).toLocaleDateString(
                  lang === "ur" ? "ur-PK" : "en-GB",
                  { weekday: "short" },
                )}
              </small>
              <b>{d.slice(-2)}</b>
            </button>
          ))}
        </div>
        <h3>{S("Available times", "دستیاب اوقات")}</h3>
        <div className="hc-slots" aria-live="polite">
          {loading ? (
            <p>{S("Checking availability…", "دستیاب اوقات کی جانچ…")}</p>
          ) : slots.length ? (
            slots.map((s) => (
              <button
                type="button"
                className={selected === s ? "selected" : ""}
                aria-pressed={selected === s}
                key={s}
                onClick={() => setSelected(s)}
              >
                {timeLabel(s, lang)}
              </button>
            ))
          ) : (
            <p className="hc-empty">
              {S(
                "No available slots on this day. Choose another date.",
                "اس دن وقت دستیاب نہیں۔ دوسری تاریخ منتخب کریں۔",
              )}
            </p>
          )}
        </div>
        <label>
          {S("Reason for visit (fictional)", "ملاقات کی وجہ (فرضی)")}
          <input
            maxLength={500}
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder={S("Example: sample follow-up", "مثال: نمونہ فالو اپ")}
          />
        </label>
        {error && (
          <p className="hc-form-error" role="alert">
            {error}
          </p>
        )}
        <div className="hc-modal-actions">
          <button type="button" className="hc-btn secondary" onClick={onClose}>
            {S("Close", "بند کریں")}
          </button>
          <button
            className="hc-btn"
            disabled={!selected || !slots.includes(selected) || busy}
          >
            {busy
              ? S("Saving…", "محفوظ ہو رہا ہے…")
              : S("Confirm demo booking", "ڈیمو بکنگ کی تصدیق")}
          </button>
        </div>
      </form>
    </Modal>
  );
}

export function CalendarView({
  state,
  doctorId,
  S,
  lang,
  onSelect,
  onRecord,
}: {
  state: HealthcareState;
  doctorId?: string;
  S: Translator;
  lang: string;
  onSelect: (a: Appointment) => void;
  onRecord?: (a: Appointment) => void;
}) {
  const [date, setDate] = useState(localDate(state.server_time)),
    [view, setView] = useState("day"),
    [filter, setFilter] = useState(doctorId ?? "");
  useEffect(() => {
    setFilter(doctorId ?? "");
  }, [doctorId]);
  const doctors = state.doctors.filter((d) => !filter || d.id === filter),
    dates =
      view === "day"
        ? [date]
        : Array.from({ length: 7 }, (_, i) => dayAfter(date, i));
  const apps = state.appointments.filter(
    (a) =>
      !["cancelled", "no_show"].includes(a.status) &&
      (!filter || a.doctor_id === filter),
  );
  const startHour = Math.min(
    9,
    ...doctors.flatMap((d) =>
      d.schedule.map((s) => Number(s.start.slice(0, 2))),
    ),
  );
  const endHour = Math.max(
    17,
    ...doctors.flatMap((d) =>
      d.schedule.map((s) =>
        Math.ceil(Number(s.end.slice(0, 2)) + Number(s.end.slice(3)) / 60),
      ),
    ),
  );
  return (
    <section className="hc-card hc-calendar-card">
      <div className="hc-calendar-toolbar">
        <div>
          <button
            className="hc-icon-btn"
            onClick={() => setDate(dayAfter(date, view === "day" ? -1 : -7))}
            aria-label={S("Previous", "پچھلا")}
          >
            ‹
          </button>
          <input
            type="date"
            value={date}
            aria-label={S("Calendar date", "کیلنڈر کی تاریخ")}
            onChange={(e) => setDate(e.target.value)}
          />
          <button
            className="hc-icon-btn"
            onClick={() => setDate(dayAfter(date, view === "day" ? 1 : 7))}
            aria-label={S("Next", "اگلا")}
          >
            ›
          </button>
          <button
            className="hc-link"
            onClick={() => setDate(localDate(state.server_time))}
          >
            {S("Today", "آج")}
          </button>
        </div>
        <div>
          {!doctorId && (
            <select
              value={filter}
              aria-label={S("Filter doctor", "ڈاکٹر فلٹر")}
              onChange={(e) => setFilter(e.target.value)}
            >
              <option value="">{S("All doctors", "تمام ڈاکٹر")}</option>
              {state.doctors.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          )}
          <div className="hc-segment">
            <button
              className={view === "day" ? "selected" : ""}
              onClick={() => setView("day")}
            >
              {S("Day", "دن")}
            </button>
            <button
              className={view === "week" ? "selected" : ""}
              onClick={() => setView("week")}
            >
              {S("Week", "ہفتہ")}
            </button>
          </div>
        </div>
      </div>
      <div className="hc-calendar-scroll">
        <div
          className={`hc-calendar ${view}`}
          style={{
            gridTemplateColumns:
              view === "day"
                ? `70px repeat(${doctors.length}, minmax(170px,1fr))`
                : `repeat(7,minmax(150px,1fr))`,
          }}
        >
          {view === "day" ? (
            <>
              <div className="hc-calendar-corner">PKT</div>
              {doctors.map((d) => (
                <div className="hc-calendar-doctor" key={d.id}>
                  <Avatar name={d.name} />
                  <span>
                    <b>{d.name}</b>
                    <small>{d.specialty}</small>
                  </span>
                </div>
              ))}
              <div className="hc-time-axis">
                {Array.from({ length: endHour - startHour }, (_, i) => (
                  <span key={i}>
                    {(i + startHour) % 12 || 12}
                    {i + startHour < 12 ? "am" : "pm"}
                  </span>
                ))}
              </div>
              {doctors.map((d, i) => (
                <div
                  className="hc-day-column"
                  key={d.id}
                  style={{ height: (endHour - startHour) * 66 }}
                >
                  {apps
                    .filter(
                      (a) =>
                        a.doctor_id === d.id && localDate(a.starts_at) === date,
                    )
                    .map((a) => {
                      const start = new Date(
                        new Date(a.starts_at).getTime() + 18000000,
                      );
                      const minutes =
                        start.getUTCHours() * 60 + start.getUTCMinutes();
                      return (
                        <button
                          key={a.id}
                          className={`hc-calendar-appointment color-${i % 4}`}
                          style={{
                            top: (minutes - startHour * 60) * 1.1,
                            height: 32,
                          }}
                          onClick={() =>
                            onRecord &&
                            ["in_consultation", "completed"].includes(a.status)
                              ? onRecord(a)
                              : onSelect(a)
                          }
                        >
                          <b>
                            {
                              state.patients.find((p) => p.id === a.patient_id)
                                ?.name
                            }
                          </b>
                          <span>
                            {timeLabel(a.starts_at, lang)} · {modes(a.mode, S)}
                          </span>
                        </button>
                      );
                    })}
                </div>
              ))}
            </>
          ) : (
            dates.map((d) => (
              <div className="hc-week-column" key={d}>
                <h3>{dateLabel(`${d}T12:00:00+05:00`, lang)}</h3>
                {apps
                  .filter((a) => localDate(a.starts_at) === d)
                  .map((a) => (
                    <button
                      className="hc-week-appointment"
                      key={a.id}
                      onClick={() =>
                        onRecord &&
                        ["in_consultation", "completed"].includes(a.status)
                          ? onRecord(a)
                          : onSelect(a)
                      }
                    >
                      <b>{timeLabel(a.starts_at, lang)}</b>
                      <span>
                        {
                          state.patients.find((p) => p.id === a.patient_id)
                            ?.name
                        }
                      </span>
                      <small>
                        {
                          state.doctors.find((dr) => dr.id === a.doctor_id)
                            ?.name
                        }
                      </small>
                      <span className={`hc-status ${a.status}`}>
                        {statusLabel(a.status, S)}
                      </span>
                    </button>
                  ))}
              </div>
            ))
          )}
        </div>
      </div>
      <div className="hc-calendar-legend">
        <span className="hc-status confirmed">
          {S("Confirmed", "تصدیق شدہ")}
        </span>
        <span className="hc-status checked_in">
          {S("Checked in", "پہنچ گیا")}
        </span>
        <span className="hc-status completed">{S("Completed", "مکمل")}</span>
        <p>
          {S(
            "Select a visit to open its details. Every time is PKT.",
            "تفصیل کے لیے ملاقات منتخب کریں۔ تمام اوقات پاکستانی ہیں۔",
          )}
        </p>
      </div>
    </section>
  );
}

export function PatientList({
  patients,
  selected,
  onSelect,
  search,
  onSearch,
  S,
}: {
  patients: Patient[];
  selected: string;
  onSelect: (id: string) => void;
  search: string;
  onSearch: (s: string) => void;
  S: Translator;
}) {
  return (
    <section className="hc-card hc-patient-list">
      <label className="hc-search">
        <Icon name="search" />
        <input
          value={search}
          onChange={(e) => onSearch(e.target.value)}
          placeholder={S("Search patients", "مریض تلاش کریں")}
          aria-label={S("Search patients", "مریض تلاش کریں")}
        />
      </label>
      {patients.map((p) => (
        <button
          className={selected === p.id ? "selected" : ""}
          key={p.id}
          onClick={() => onSelect(p.id)}
        >
          <Avatar name={p.name} />
          <span>
            <b>{p.name}</b>
            <small>{S("Sample patient", "نمونہ مریض")}</small>
          </span>
        </button>
      ))}
      {!patients.length && (
        <p className="hc-empty">
          {S("No matching patients", "کوئی مریض نہیں ملا")}
        </p>
      )}
    </section>
  );
}

export function RecordList({
  records,
  state,
  lang,
  S,
  onEdit,
}: {
  records: ClinicalRecord[];
  state: HealthcareState;
  lang: string;
  S: Translator;
  onEdit?: (r: ClinicalRecord) => void;
}) {
  const [selected, setSelected] = useState<ClinicalRecord | null>(null);
  return (
    <>
      <div className="hc-records-list">
        {records.map((r) => (
          <article className="hc-card hc-record-card" key={r.id}>
            <div className="hc-card-title">
              <span className="hc-icon-tile">
                <Icon name="records" />
              </span>
              <span
                className={`hc-status ${r.published ? "completed" : "confirmed"}`}
              >
                {r.published
                  ? S("Published", "شائع شدہ")
                  : S("Draft · staff only", "ڈرافٹ، صرف عملہ")}
              </span>
            </div>
            <h2>{r.data.title}</h2>
            <p className="hc-caption">
              {dateLabel(r.visit_at, lang)} ·{" "}
              {state.doctors.find((d) => d.id === r.doctor_id)?.name}
            </p>
            <div className="hc-tags">
              {r.data.diagnoses.map((d) => (
                <span key={d}>{d}</span>
              ))}
            </div>
            <p className="hc-record-note">{r.data.notes}</p>
            <div className="hc-record-actions">
              <button
                className="hc-btn secondary"
                onClick={() => setSelected(r)}
              >
                <Icon name="records" />
                {S("View report", "رپورٹ دیکھیں")}
              </button>
              {!r.published && onEdit && (
                <button className="hc-btn" onClick={() => onEdit(r)}>
                  {S("Edit / publish", "ترمیم / شائع کریں")}
                </button>
              )}
            </div>
          </article>
        ))}
      </div>
      {!records.length && (
        <section className="hc-card hc-empty">
          <Icon name="records" />
          <h3>{S("No visit records yet", "ابھی ملاقات کا ریکارڈ نہیں")}</h3>
          <p>
            {S(
              "Published clinical notes will appear here after a consultation.",
              "ملاقات کے بعد شائع شدہ طبی نوٹس یہاں آئیں گے۔",
            )}
          </p>
        </section>
      )}
      {selected && (
        <Modal
          title={S("Sample health report", "نمونہ طبی رپورٹ")}
          onClose={() => setSelected(null)}
        >
          <section className="hc-print-record">
            <div className="hc-report-brand">
              <Icon name="heart" />
              <div>
                <h2>{S("Sample visit report", "نمونہ ملاقات رپورٹ")}</h2>
                <p>
                  {
                    state.patients.find((p) => p.id === selected.patient_id)
                      ?.name
                  }{" "}
                  · {dateLabel(selected.visit_at, lang)}
                </p>
              </div>
              <span className="hc-pill">
                {S("FICTIONAL DATA", "فرضی معلومات")}
              </span>
            </div>
            <h3>{selected.data.title}</h3>
            <p>
              {state.doctors.find((d) => d.id === selected.doctor_id)?.name} ·{" "}
              {selected.published
                ? S("Published", "شائع شدہ")
                : S("Draft", "ڈرافٹ")}
            </p>
            <h4>{S("Recorded diagnoses", "درج شدہ تشخیص")}</h4>
            <ul>
              {selected.data.diagnoses.map((x) => (
                <li key={x}>{x}</li>
              ))}
            </ul>
            <h4>{S("Clinician notes", "ڈاکٹر کے نوٹس")}</h4>
            <p className="hc-prewrap">
              {selected.data.notes || S("Not recorded", "درج نہیں")}
            </p>
            <h4>{S("Prescriptions", "نسخے")}</h4>
            <ul>
              {selected.data.prescriptions.map((x) => (
                <li key={x}>{x}</li>
              ))}
            </ul>
            <h4>{S("Vital readings", "اہم پیمائشیں")}</h4>
            <div className="hc-report-vitals">
              <span>
                BP: {selected.data.vitals.systolic ?? "—"}/
                {selected.data.vitals.diastolic ?? "—"} mmHg
              </span>
              <span>HR: {selected.data.vitals.heart_rate ?? "—"} bpm</span>
              <span>SpO₂: {selected.data.vitals.oxygen ?? "—"}%</span>
              <span>Temp: {selected.data.vitals.temperature ?? "—"}°C</span>
            </div>
            <h4>{S("Test results", "ٹیسٹ کے نتائج")}</h4>
            {selected.data.tests.length ? (
              <table>
                <thead>
                  <tr>
                    {[
                      S("Test", "ٹیسٹ"),
                      S("Result", "نتیجہ"),
                      S("Reference", "حوالہ"),
                    ].map((x) => (
                      <th key={x}>{x}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {selected.data.tests.map((t, i) => (
                    <tr key={i}>
                      <td>{t.name}</td>
                      <td>
                        {t.value} {t.unit}
                      </td>
                      <td>{t.range}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p>{S("No test results recorded", "کوئی ٹیسٹ درج نہیں")}</p>
            )}
            <h4>{S("Follow-up", "فالو اپ")}</h4>
            <p>{selected.data.follow_up || S("Not recorded", "درج نہیں")}</p>
            <p className="hc-caption">
              {S(
                "Fictional record for a NexusPoint product demonstration. Not medical advice or a real prescription.",
                "نیکسس پوائنٹ کے ڈیمو کے لیے فرضی ریکارڈ۔ یہ طبی مشورہ یا حقیقی نسخہ نہیں ہے۔",
              )}
            </p>
          </section>
          <div className="hc-modal-actions">
            <button className="hc-btn" onClick={() => window.print()}>
              <Icon name="print" />
              {S("Print / save PDF", "پرنٹ / پی ڈی ایف محفوظ کریں")}
            </button>
          </div>
        </Modal>
      )}
    </>
  );
}

export function ClinicalDialog({
  state,
  initial,
  doctorId,
  S,
  run,
  busy,
  onClose,
}: {
  state: HealthcareState;
  initial: {
    patientId: string;
    appointment?: Appointment;
    record?: ClinicalRecord;
  };
  doctorId: string;
  S: Translator;
  run: Run;
  busy: boolean;
  onClose: () => void;
}) {
  const [data, setData] = useState<RecordData>(
      initial.record?.data ?? emptyRecord(),
    ),
    [error, setError] = useState("");
  const [id, setId] = useState(initial.record?.id ?? "");
  const doctor =
    initial.record?.doctor_id ?? initial.appointment?.doctor_id ?? doctorId;
  const patient = state.patients.find((p) => p.id === initial.patientId);
  const [testText, setTestText] = useState(
    data.tests
      .map((t) => [t.name, t.value, t.unit, t.range].join(" | "))
      .join("\n"),
  );
  async function save(published: boolean) {
    setError("");
    try {
      const tests = testText
        .split("\n")
        .filter((x) => x.trim())
        .map((x) => {
          const [name = "", value = "", unit = "", range = ""] = x
            .split("|")
            .map((s) => s.trim());
          return { name, value, unit, range };
        });
      const result = (await run({
        action: "record",
        id: id || undefined,
        patientId: initial.patientId,
        doctorId: doctor,
        appointmentId:
          initial.appointment?.id ?? initial.record?.appointment_id,
        published,
        data: { ...data, tests },
        visitAt: initial.record?.visit_at,
      })) as ClinicalRecord;
      if (published) onClose();
      else setId(result.id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not save record");
    }
  }
  return (
    <Modal
      title={S("Clinical visit record", "طبی ملاقات کا ریکارڈ")}
      onClose={onClose}
    >
      <div className="hc-clinical-heading">
        <Avatar name={patient?.name ?? "Patient"} />
        <div>
          <b>{patient?.name}</b>
          <p>{state.doctors.find((d) => d.id === doctor)?.name}</p>
        </div>
        <span className="hc-pill">
          {S("Sample data only", "صرف فرضی معلومات")}
        </span>
      </div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          save(false);
        }}
      >
        <label>
          {S("Visit title", "ملاقات کا عنوان")}
          <input
            required
            value={data.title}
            onChange={(e) => setData({ ...data, title: e.target.value })}
          />
        </label>
        <div className="hc-form-grid">
          <label>
            {S("Diagnoses (one per line)", "تشخیص، ہر سطر میں ایک")}
            <textarea
              rows={3}
              value={data.diagnoses.join("\n")}
              onChange={(e) =>
                setData({ ...data, diagnoses: e.target.value.split("\n") })
              }
            />
          </label>
          <label>
            {S("Prescription entries (one per line)", "نسخے، ہر سطر میں ایک")}
            <textarea
              rows={3}
              value={data.prescriptions.join("\n")}
              onChange={(e) =>
                setData({ ...data, prescriptions: e.target.value.split("\n") })
              }
            />
          </label>
        </div>
        <label>
          {S("Clinician notes", "ڈاکٹر کے نوٹس")}
          <textarea
            rows={4}
            maxLength={5000}
            value={data.notes}
            onChange={(e) => setData({ ...data, notes: e.target.value })}
          />
        </label>
        <div className="hc-vital-inputs">
          {(
            [
              "systolic",
              "diastolic",
              "heart_rate",
              "temperature",
              "oxygen",
            ] as const
          ).map((key, i) => (
            <label key={key}>
              {
                [
                  S("Systolic BP", "اوپری بلڈ پریشر"),
                  S("Diastolic BP", "نچلا بلڈ پریشر"),
                  S("Heart rate", "دل کی دھڑکن"),
                  S("Temperature °C", "درجہ حرارت"),
                  S("Oxygen %", "آکسیجن"),
                ][i]
              }
              <input
                type="number"
                min="0"
                max="1000"
                step="any"
                value={data.vitals[key] ?? ""}
                onChange={(e) =>
                  setData({
                    ...data,
                    vitals: {
                      ...data.vitals,
                      [key]:
                        e.target.value === "" ? null : Number(e.target.value),
                    },
                  })
                }
              />
            </label>
          ))}
        </div>
        <label>
          {S(
            "Test results: name | result | unit | reference, one per line",
            "ٹیسٹ: نام | نتیجہ | اکائی | حوالہ، ہر سطر میں ایک",
          )}
          <textarea
            rows={3}
            value={testText}
            onChange={(e) => setTestText(e.target.value)}
            placeholder="Hemoglobin | 13.8 | g/dL | Sample reference 12–16"
          />
        </label>
        <label>
          {S("Follow-up date", "فالو اپ تاریخ")}
          <input
            type="date"
            value={data.follow_up}
            onChange={(e) => setData({ ...data, follow_up: e.target.value })}
          />
        </label>
        <p className="hc-caption">
          {S(
            "Drafts stay in staff views. Publishing makes this record visible in the linked patient portal. Published records are final; use a new record for a later visit.",
            "ڈرافٹ صرف عملے کو نظر آتے ہیں۔ شائع کرنے سے ریکارڈ مریض پورٹل میں دکھائی دے گا۔ بعد کی ملاقات کے لیے نیا ریکارڈ بنائیں۔",
          )}
        </p>
        {error && (
          <p className="hc-form-error" role="alert">
            {error}
          </p>
        )}
        {id && (
          <p className="hc-success">{S("Draft saved", "ڈرافٹ محفوظ ہو گیا")}</p>
        )}
        <div className="hc-modal-actions">
          <button className="hc-btn secondary" disabled={busy} type="submit">
            {S("Save draft", "ڈرافٹ محفوظ کریں")}
          </button>
          <button
            className="hc-btn"
            disabled={busy || !data.title.trim()}
            type="button"
            onClick={() => save(true)}
          >
            {S("Publish to patient", "مریض کے لیے شائع کریں")}
          </button>
        </div>
      </form>
    </Modal>
  );
}

export function Inbox({
  state,
  S,
  lang,
  run,
  busy,
}: {
  state: HealthcareState;
  S: Translator;
  lang: string;
  run: Run;
  busy: boolean;
}) {
  const [selected, setSelected] = useState(""),
    [text, setText] = useState("");
  const c =
    state.conversations.find((c) => c.id === selected) ??
    state.conversations[0];
  const patient = state.patients.find((p) => p.visitor === c?.visitor);
  const related = state.appointments.filter(
    (a) => a.patient_id === patient?.id,
  );
  const messagesRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    messagesRef.current?.scrollTo({ top: messagesRef.current.scrollHeight });
  }, [c?.id, c?.messages.length]);
  if (!c)
    return (
      <section className="hc-card hc-empty">
        <Icon name="messages" />
        <h3>{S("The inbox is ready", "ان باکس تیار ہے")}</h3>
        <p>
          {S(
            "Send a message from the patient portal or the original demo assistant to see it here.",
            "مریض پورٹل یا اسسٹنٹ سے پیغام بھیجیں، یہاں نظر آئے گا۔",
          )}
        </p>
      </section>
    );
  return (
    <div className="hc-inbox">
      <section className="hc-card hc-inbox-list">
        <h2>{S("Conversations", "گفتگو")}</h2>
        {state.conversations.map((conv) => (
          <button
            key={conv.id}
            className={conv.id === c.id ? "selected" : ""}
            onClick={() => setSelected(conv.id)}
          >
            <Avatar
              name={
                state.patients.find((p) => p.visitor === conv.visitor)?.name ??
                "Visitor"
              }
            />
            <span>
              <b>
                {state.patients.find((p) => p.visitor === conv.visitor)?.name ??
                  S("Demo visitor", "ڈیمو وزیٹر")}
              </b>
              <small>
                {conv.summary ?? S("New conversation", "نئی گفتگو")}
              </small>
            </span>
            {conv.handoff && <i className="hc-unread" />}
          </button>
        ))}
      </section>
      <section className="hc-card hc-inbox-conversation">
        <div className="hc-card-title">
          <div>
            <h2>{patient?.name ?? S("Demo visitor", "ڈیمو وزیٹر")}</h2>
            <p className="hc-caption">
              {c.channel} ·{" "}
              {c.staff_mode
                ? S("Staff is replying", "عملہ جواب دے رہا ہے")
                : S("Assistant is replying", "اسسٹنٹ جواب دے رہا ہے")}
            </p>
          </div>
          <button
            className={`hc-btn ${c.staff_mode ? "secondary" : ""}`}
            disabled={busy}
            onClick={() =>
              run({
                action: "conversation",
                id: c.id,
                staffMode: !c.staff_mode,
              }).catch(() => {})
            }
          >
            {c.staff_mode
              ? S("Return to assistant", "اسسٹنٹ کو واپس دیں")
              : S("Take over chat", "گفتگو سنبھالیں")}
          </button>
        </div>
        <div className="hc-inbox-messages" ref={messagesRef}>
          {c.messages.map((m, i) => (
            <div className={`hc-inbox-bubble ${m.role}`} key={`${m.at}-${i}`}>
              <small>
                {m.role === "customer"
                  ? S("Patient", "مریض")
                  : m.source === "staff"
                    ? S("Staff", "عملہ")
                    : S("Assistant", "اسسٹنٹ")}
              </small>
              <p dir="auto">{m.content}</p>
              <time>{timeLabel(m.at, lang)}</time>
            </div>
          ))}
        </div>
        <form
          className="hc-inbox-composer"
          onSubmit={async (e) => {
            e.preventDefault();
            if (!text.trim()) return;
            try {
              await run({ action: "conversation", id: c.id, text });
              setText("");
            } catch {}
          }}
        >
          <input
            value={text}
            onChange={(e) => setText(e.target.value)}
            disabled={!c.staff_mode || busy}
            placeholder={S(
              "Take over to reply as staff",
              "عملے کے جواب کے لیے گفتگو سنبھالیں",
            )}
            aria-label={S("Staff reply", "عملے کا جواب")}
          />
          <button
            className="hc-btn"
            disabled={!c.staff_mode || busy || !text.trim()}
          >
            {S("Send", "بھیجیں")}
          </button>
        </form>
      </section>
      <aside className="hc-card hc-inbox-details">
        <Avatar name={patient?.name ?? "Patient"} large />
        <h2>{patient?.name ?? S("Demo visitor", "ڈیمو وزیٹر")}</h2>
        <span className="hc-pill">
          {S("Sample patient context", "نمونہ مریض کی تفصیل")}
        </span>
        <label>
          {S("Assigned to", "ذمہ دار")}
          <select
            value={c.assigned_to ?? ""}
            onChange={(e) =>
              run({
                action: "conversation",
                id: c.id,
                assignedTo: e.target.value,
              }).catch(() => {})
            }
          >
            <option value="">{S("Unassigned", "غیر مقرر")}</option>
            <option>Reception</option>
            {state.doctors.map((d) => (
              <option key={d.id}>{d.name}</option>
            ))}
          </select>
        </label>
        <h3>{S("Appointments", "اپائنٹمنٹس")}</h3>
        {related.map((a) => (
          <div className="hc-context-appointment" key={a.id}>
            <b>{state.doctors.find((d) => d.id === a.doctor_id)?.name}</b>
            <p>
              {dateLabel(a.starts_at, lang)} · {timeLabel(a.starts_at, lang)}
            </p>
            <span className={`hc-status ${a.status}`}>
              {statusLabel(a.status, S)}
            </span>
          </div>
        ))}
        {!related.length && (
          <p className="hc-caption">
            {S("No linked appointments yet", "ابھی منسلک اپائنٹمنٹ نہیں")}
          </p>
        )}
        <h3>{S("Staff handoff", "عملے کو منتقلی")}</h3>
        <p>
          {c.handoff
            ? S("A staff reply is needed.", "عملے کے جواب کی ضرورت ہے۔")
            : S("No unresolved handoff.", "کوئی زیر التوا منتقلی نہیں۔")}
        </p>
      </aside>
    </div>
  );
}

export function ScheduleEditor({
  state,
  S,
  lang,
  run,
  busy,
}: {
  state: HealthcareState;
  S: Translator;
  lang: string;
  run: Run;
  busy: boolean;
}) {
  const [doctorId, setDoctorId] = useState(state.doctors[0]?.id ?? ""),
    [schedule, setSchedule] = useState<Schedule>(
      state.doctors[0]?.schedule ?? [],
    ),
    [error, setError] = useState("");
  const doctor = state.doctors.find((d) => d.id === doctorId);
  useEffect(() => {
    setSchedule(doctor?.schedule ?? []);
    setError("");
  }, [doctorId]);
  const days = [
    S("Sunday", "اتوار"),
    S("Monday", "پیر"),
    S("Tuesday", "منگل"),
    S("Wednesday", "بدھ"),
    S("Thursday", "جمعرات"),
    S("Friday", "جمعہ"),
    S("Saturday", "ہفتہ"),
  ];
  async function save(input: Record<string, unknown>) {
    setError("");
    try {
      await run({ action: "schedule", doctorId, ...input });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not change schedule");
    }
  }
  return (
    <div className="hc-two-grid">
      <section className="hc-card">
        <div className="hc-card-title">
          <h2>{S("Weekly working hours", "ہفتہ وار اوقات")}</h2>
          <span className="hc-pill">{S("Sample schedule", "نمونہ شیڈول")}</span>
        </div>
        <label>
          {S("Doctor", "ڈاکٹر")}
          <select
            value={doctorId}
            onChange={(e) => setDoctorId(e.target.value)}
          >
            {state.doctors.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
        </label>
        <div className="hc-schedule-rows">
          {days.map((name, day) => {
            const s = schedule.find((s) => s.day === day);
            return (
              <div key={day}>
                <label>
                  <input
                    type="checkbox"
                    checked={!!s}
                    onChange={(e) =>
                      setSchedule(
                        e.target.checked
                          ? [...schedule, { day, start: "09:00", end: "16:00" }]
                          : schedule.filter((s) => s.day !== day),
                      )
                    }
                  />
                  {name}
                </label>
                {s ? (
                  <>
                    <input
                      type="time"
                      step="1800"
                      value={s.start}
                      aria-label={`${name} start`}
                      onChange={(e) =>
                        setSchedule(
                          schedule.map((x) =>
                            x.day === day ? { ...x, start: e.target.value } : x,
                          ),
                        )
                      }
                    />
                    <span>–</span>
                    <input
                      type="time"
                      step="1800"
                      value={s.end}
                      aria-label={`${name} end`}
                      onChange={(e) =>
                        setSchedule(
                          schedule.map((x) =>
                            x.day === day ? { ...x, end: e.target.value } : x,
                          ),
                        )
                      }
                    />
                  </>
                ) : (
                  <span className="hc-caption">
                    {S("Unavailable", "غیر دستیاب")}
                  </span>
                )}
              </div>
            );
          })}
        </div>
        <p className="hc-caption">
          {S(
            "Changes cannot invalidate existing bookings. Reschedule affected visits first.",
            "تبدیلی سے موجودہ بکنگ متاثر نہیں ہو سکتی۔ متعلقہ ملاقاتوں کا وقت پہلے بدلیں۔",
          )}
        </p>
        <button
          className="hc-btn"
          disabled={busy}
          onClick={() => save({ schedule })}
        >
          {S("Save working hours", "اوقات محفوظ کریں")}
        </button>
      </section>
      <section className="hc-card">
        <h2>{S("Block unavailable time", "غیر دستیاب وقت بند کریں")}</h2>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const form = new FormData(e.currentTarget);
            save({
              start: `${form.get("start")}:00+05:00`,
              end: `${form.get("end")}:00+05:00`,
              reason: form.get("reason"),
            });
          }}
        >
          <label>
            {S("From (PKT)", "آغاز، پاکستانی وقت")}
            <input type="datetime-local" name="start" required />
          </label>
          <label>
            {S("Until (PKT)", "اختتام، پاکستانی وقت")}
            <input type="datetime-local" name="end" required />
          </label>
          <label>
            {S("Reason", "وجہ")}
            <input
              name="reason"
              maxLength={200}
              placeholder={S("Example: sample leave", "مثال: نمونہ چھٹی")}
            />
          </label>
          <button className="hc-btn" disabled={busy}>
            {S("Block this time", "وقت بند کریں")}
          </button>
        </form>
        <h3 className="hc-space-top">
          {S("Unavailable periods", "غیر دستیاب اوقات")}
        </h3>
        {state.blocks
          .filter((b) => b.doctor_id === doctorId)
          .map((b) => (
            <div className="hc-block" key={b.id}>
              <span>
                <b>{b.reason}</b>
                <small>
                  {dateLabel(b.starts_at, lang)} {timeLabel(b.starts_at, lang)}{" "}
                  – {dateLabel(b.ends_at, lang)} {timeLabel(b.ends_at, lang)}
                </small>
              </span>
              <button
                className="hc-link"
                disabled={busy}
                onClick={() => save({ remove: b.id })}
              >
                {S("Restore time", "وقت بحال کریں")}
              </button>
            </div>
          ))}
        {error && (
          <p className="hc-form-error" role="alert">
            {error}
          </p>
        )}
      </section>
    </div>
  );
}

export function CallDialog({
  appointment,
  state,
  S,
  onClose,
  onComplete,
}: {
  appointment: Appointment;
  state: HealthcareState;
  S: Translator;
  onClose: () => void;
  onComplete?: () => void;
}) {
  const [started, setStarted] = useState(false),
    [seconds, setSeconds] = useState(0),
    [muted, setMuted] = useState(false),
    [camera, setCamera] = useState(true);
  const doctor = state.doctors.find((d) => d.id === appointment.doctor_id),
    patient = state.patients.find((p) => p.id === appointment.patient_id);
  useEffect(() => {
    if (!started) return;
    const id = setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => clearInterval(id);
  }, [started]);
  return (
    <Modal title={S("Demo consultation", "نمونہ ملاقات")} onClose={onClose}>
      <div className="hc-call-label">
        <span className="hc-pill">{S("SIMULATED CALL", "نمونہ کال")}</span>
        <p>
          {S(
            "No live connection, camera or microphone access.",
            "اصل رابطہ، کیمرہ یا مائیکروفون استعمال نہیں ہوتا۔",
          )}
        </p>
      </div>
      {!started ? (
        <div className="hc-waiting-room">
          <Avatar name={doctor?.name ?? "Doctor"} large />
          <h2>{S("Your waiting room is ready", "انتظار گاہ تیار ہے")}</h2>
          <p>
            {doctor?.name} · {dateLabel(appointment.starts_at)} ·{" "}
            {timeLabel(appointment.starts_at)} PKT
          </p>
          <button className="hc-btn" onClick={() => setStarted(true)}>
            {S("Start sample call", "نمونہ کال شروع کریں")}
          </button>
        </div>
      ) : (
        <>
          <div className="hc-call-grid">
            <div>
              <span>{patient?.name}</span>
              <Avatar name={patient?.name ?? "Demo patient"} large />
              <small>
                {muted
                  ? S("Microphone off (simulated)", "مائیک بند، نمونہ")
                  : S("Microphone on (simulated)", "مائیک کھلا، نمونہ")}
              </small>
            </div>
            <div>
              <span>{doctor?.name}</span>
              <Avatar name={doctor?.name ?? "Doctor"} large />
              <small>
                {camera
                  ? S("Sample consultant", "نمونہ کنسلٹنٹ")
                  : S("Camera off (simulated)", "کیمرہ بند، نمونہ")}
              </small>
            </div>
          </div>
          <div className="hc-call-controls">
            <time>
              {String(Math.floor(seconds / 60)).padStart(2, "0")}:
              {String(seconds % 60).padStart(2, "0")}
            </time>
            <button
              className="hc-btn secondary"
              aria-pressed={muted}
              onClick={() => setMuted(!muted)}
            >
              {muted ? S("Unmute", "مائیک کھولیں") : S("Mute", "مائیک بند")}
            </button>
            {appointment.mode === "video" && (
              <button
                className="hc-btn secondary"
                aria-pressed={!camera}
                onClick={() => setCamera(!camera)}
              >
                <Icon name="video" />
                {camera
                  ? S("Camera off", "کیمرہ بند")
                  : S("Camera on", "کیمرہ کھولیں")}
              </button>
            )}
            <button
              className="hc-btn end"
              onClick={() => {
                if (onComplete && appointment.status === "in_consultation")
                  onComplete();
                else onClose();
              }}
            >
              {S("End sample call", "نمونہ کال ختم")}
            </button>
          </div>
        </>
      )}
    </Modal>
  );
}

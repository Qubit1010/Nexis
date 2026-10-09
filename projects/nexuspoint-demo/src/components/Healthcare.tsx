"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import ChatWindow, { visitorId } from "./ChatWindow";
import {
  AppointmentList,
  BookingDialog,
  CalendarView,
  CallDialog,
  ClinicalDialog,
  DoctorDirectory,
  Inbox,
  PatientList,
  RecordList,
  ScheduleEditor,
  Icon,
  Avatar,
  Modal,
} from "./HealthcareViews";
import {
  dateLabel,
  dayAfter,
  localDate,
  timeLabel,
  type Appointment,
  type ClinicalRecord,
  type HealthcareState,
} from "@/lib/healthcare-types";
import "./healthcare.css";

type Role = "patient" | "clinic" | "doctor";
export type Translator = (en: string, ur: string) => string;
export type Run = (input: Record<string, unknown>) => Promise<unknown>;
const menus = {
  patient: ["overview", "doctors", "appointments", "records", "messages"],
  clinic: ["overview", "calendar", "queue", "inbox", "patients", "schedules"],
  doctor: ["overview", "calendar", "patients", "records"],
};
const labels: Record<string, [string, string]> = {
  overview: ["Overview", "جائزہ"],
  doctors: ["Find a doctor", "ڈاکٹر تلاش کریں"],
  appointments: ["Appointments", "اپائنٹمنٹس"],
  records: ["Health records", "طبی ریکارڈ"],
  messages: ["Messages", "پیغامات"],
  calendar: ["Schedule", "شیڈول"],
  queue: ["Waiting queue", "انتظار کی قطار"],
  inbox: ["Conversation inbox", "گفتگو"],
  patients: ["Patients", "مریض"],
  schedules: ["Doctor availability", "ڈاکٹر کے اوقات"],
};
export default function Healthcare({
  slug,
  token,
  name,
  role,
  initialLang,
  initialTab,
  initialBookingDoctor,
  initialBooking = false,
}: {
  slug: string;
  token: string;
  name: string;
  role: Role;
  initialLang: "en" | "ur";
  initialTab?: string;
  initialBookingDoctor?: string;
  initialBooking?: boolean;
}) {
  const [lang, setLang] = useState(initialLang),
    [theme, setTheme] = useState("light"),
    [tab, setTab] = useState(
      menus[role].includes(initialTab ?? "") ? initialTab! : "overview",
    );
  const [visitor, setVisitor] = useState(""),
    [state, setState] = useState<HealthcareState | null>(null),
    [error, setError] = useState(""),
    [notice, setNotice] = useState(""),
    [busy, setBusy] = useState(false);
  const [doctorId, setDoctorId] = useState(""),
    [patientId, setPatientId] = useState(""),
    [search, setSearch] = useState("");
  const openedLandingBooking = useRef(false);
  const [booking, setBooking] = useState<{
      doctorId?: string;
      appointment?: Appointment;
      patientId?: string;
    } | null>(null),
    [call, setCall] = useState<Appointment | null>(null);
  const [clinical, setClinical] = useState<{
      patientId: string;
      appointment?: Appointment;
      record?: ClinicalRecord;
    } | null>(null),
    [profile, setProfile] = useState(false);
  const S: Translator = (en, ur) => (lang === "ur" ? ur : en);
  useEffect(() => {
    if (role !== "patient" || !state || !initialBooking || openedLandingBooking.current) return;
    openedLandingBooking.current = true;
    if (!initialBookingDoctor) { setBooking({}); return; }
    const chosen = state.doctors.find(d => d.id === initialBookingDoctor && d.active);
    if (chosen) setBooking({ doctorId: chosen.id });
  }, [state, role, initialBooking, initialBookingDoctor]);
  useEffect(() => {
    setVisitor(visitorId(slug));
    try {
      setTheme(localStorage.getItem("np-clinic-theme") ?? "light");
    } catch {}
  }, [slug]);
  const load = useCallback(async () => {
    if (!visitor) return;
    try {
      const p = new URLSearchParams({ slug, t: token, visitor, role });
      const r = await fetch(`/api/healthcare?${p}`, { cache: "no-store" });
      const data = await r.json();
      if (!r.ok) throw new Error(data.error);
      setState(data);
      setError("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Connection problem");
    }
  }, [slug, token, visitor, role]);
  useEffect(() => {
    load();
    const id = setInterval(() => {
      if (document.visibilityState === "visible") load();
    }, 2000);
    return () => clearInterval(id);
  }, [load]);
  useEffect(() => {
    if (state && !doctorId) setDoctorId(state.doctors[0]?.id ?? "");
    if (state && !patientId) setPatientId(state.patient.id);
  }, [state, doctorId, patientId]);
  async function run(input: Record<string, unknown>) {
    setBusy(true);
    setNotice("");
    try {
      const r = await fetch("/api/healthcare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ slug, t: token, visitor, role, ...input }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.error);
      await load();
      setNotice(S("Saved in this demo.", "ڈیمو میں محفوظ ہو گیا۔"));
      return data.result;
    } catch (e) {
      setNotice(e instanceof Error ? e.message : "Connection problem");
      throw e;
    } finally {
      setBusy(false);
    }
  }
  const act = (input: Record<string, unknown>) => {
    run(input).catch(() => {});
  };
  const changeTab = (next: string) => {
    setTab(next);
    setSearch("");
    const u = new URL(location.href);
    u.searchParams.set("tab", next);
    history.replaceState(null, "", u);
  };
  const go = (r: string) =>
    `/d/${slug}/${r}?t=${encodeURIComponent(token)}${lang === "ur" ? "&lang=ur" : ""}`;
  const own = role === "patient";
  const doctor = state?.doctors.find((d) => d.id === doctorId);
  const appointments = (state?.appointments ?? []).filter(
    (a) => role !== "doctor" || a.doctor_id === doctorId,
  );
  const today = localDate(state?.server_time),
    todays = appointments.filter((a) => localDate(a.starts_at) === today);
  const future = appointments.filter(
    (a) => a.status === "confirmed" && new Date(a.starts_at) > new Date(),
  );
  const records = state?.records ?? [],
    latest = records.find(
      (r) => r.patient_id === state?.patient.id && r.published,
    );
  const selectedPatient =
    state?.patients.find((p) => p.id === patientId) ?? state?.patient;
  const filteredPatients = (state?.patients ?? []).filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase()),
  );
  const queue = todays
    .filter((a) => ["checked_in", "in_consultation"].includes(a.status))
    .sort((a, b) => (a.queue_number ?? 0) - (b.queue_number ?? 0));
  const status = (a: Appointment, status: string) =>
    act({ action: "appointment", id: a.id, status });
  const showClinical = (a: Appointment) => {
    setPatientId(a.patient_id);
    setClinical({ patientId: a.patient_id, appointment: a });
  };
  return (
    <div
      className="hc"
      data-clinic-theme={theme}
      dir={lang === "ur" ? "rtl" : "ltr"}
      lang={lang}
    >
      <aside className="hc-sidebar">
        <a
          className="hc-brand"
          href={`/d/${slug}?t=${encodeURIComponent(token)}`}
        >
          <span className="hc-brand-symbol">
            <Icon name="heart" />
          </span>
          <span>
            Care<span className="hc-brand-accent">desk</span>
            <small>{S("by NexusPoint", "نیکسس پوائنٹ")}</small>
          </span>
        </a>
        <div className="hc-clinic">
          <span className="hc-live" />
          {name}
          <small>{S("Connected clinic demo", "کلینک کا مربوط ڈیمو")}</small>
        </div>
        <span className="hc-eyebrow">
          {S(
            own
              ? "PATIENT PORTAL"
              : role === "doctor"
                ? "DOCTOR WORKSPACE"
                : "CLINIC OPERATIONS",
            own
              ? "مریض پورٹل"
              : role === "doctor"
                ? "ڈاکٹر ورک اسپیس"
                : "کلینک انتظام",
          )}
        </span>
        <nav
          className="hc-nav"
          aria-label={S("Workspace navigation", "ورک اسپیس نیویگیشن")}
        >
          {menus[role].map((k) => (
            <button
              key={k}
              className={tab === k ? "active" : ""}
              aria-current={tab === k ? "page" : undefined}
              onClick={() => changeTab(k)}
            >
              <Icon name={k} />
              {S(...labels[k])}
              {k === "inbox" &&
                !!state?.conversations.filter((c) => c.handoff).length && (
                  <b>{state.conversations.filter((c) => c.handoff).length}</b>
                )}
            </button>
          ))}
        </nav>
        <div className="hc-sidebar-bottom">
          <div className="hc-demo-label">
            <Icon name="shield" />
            <b>{S("A working preview", "قابل استعمال پیش نظارہ")}</b>
            <p>
              {S(
                "Fictional doctors and medical records. No real appointments or messages are sent.",
                "ڈاکٹر اور طبی ریکارڈ فرضی ہیں۔ اصل اپائنٹمنٹ یا پیغام نہیں بھیجا جاتا۔",
              )}
            </p>
          </div>
          <a href={`/d/${slug}?t=${encodeURIComponent(token)}`}>
            {S("Back to your review report", "ریویو رپورٹ پر واپس")}
          </a>
        </div>
      </aside>
      <div className="hc-main">
        <header className="hc-topbar">
          <div className="hc-breadcrumb">
            {S("Workspace", "ورک اسپیس")} <span>/</span>{" "}
            <b>{S(...labels[tab])}</b>
          </div>
          <div className="hc-top-actions">
            <select
              aria-label={S("Switch demo role", "ڈیمو کردار تبدیل کریں")}
              value={role}
              onChange={(e) => {
                location.href = go(e.target.value);
              }}
            >
              <option value="patient">{S("Patient view", "مریض")}</option>
              <option value="clinic">
                {S("Admin / reception", "انتظامیہ")}
              </option>
              <option value="doctor">{S("Doctor view", "ڈاکٹر")}</option>
            </select>
            <button
              className="hc-icon-btn"
              onClick={() => {
                const next = theme === "light" ? "dark" : "light";
                setTheme(next);
                try {
                  localStorage.setItem("np-clinic-theme", next);
                } catch {}
              }}
              aria-label={S("Switch theme", "تھیم بدلیں")}
            >
              <Icon name="theme" />
            </button>
            <button
              className="hc-language"
              onClick={() => {
                const next = lang === "en" ? "ur" : "en";
                setLang(next);
                const u = new URL(location.href);
                u.searchParams.set("lang", next);
                history.replaceState(null, "", u);
              }}
            >
              {lang === "en" ? "اردو" : "English"}
            </button>
            <button
              className="hc-profile"
              onClick={() => setProfile(true)}
              aria-label={S(
                "Edit sample patient name",
                "نمونہ مریض کا نام بدلیں",
              )}
            >
              <Avatar name={state?.patient.name ?? "Demo patient"} />
            </button>
          </div>
        </header>
        <main className="hc-content">
          <div className="hc-page-heading">
            <div>
              <p className="hc-eyebrow">
                {S("EVERY VISIT, CONNECTED", "ہر ملاقات، مربوط")}
              </p>
              <h1>
                {tab === "overview"
                  ? S(
                      own
                        ? `Welcome back, ${state?.patient.name ?? "patient"}`
                        : role === "doctor"
                          ? `Good day, ${doctor?.name ?? "doctor"}`
                          : "Your clinic, at a glance",
                      own
                        ? `${state?.patient.name ?? "مریض"}، خوش آمدید`
                        : role === "doctor"
                          ? "آپ کا روزانہ شیڈول"
                          : "آپ کا کلینک، ایک نظر میں",
                    )
                  : S(...labels[tab])}
              </h1>
              <p>
                {S(
                  "Sample workspace · All appointment times are Pakistan Standard Time (PKT)",
                  "نمونہ ورک اسپیس۔ اپائنٹمنٹ کے تمام اوقات پاکستانی وقت کے مطابق ہیں۔",
                )}
              </p>
            </div>
            <div className="hc-heading-actions">
              {role === "doctor" && state && (
                <select
                  value={doctorId}
                  aria-label={S(
                    "Select sample doctor",
                    "نمونہ ڈاکٹر منتخب کریں",
                  )}
                  onChange={(e) => setDoctorId(e.target.value)}
                >
                  {state.doctors.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name}
                    </option>
                  ))}
                </select>
              )}
              {role !== "doctor" && (
                <button className="hc-btn" onClick={() => setBooking({})}>
                  <Icon name="plus" />
                  {S("Book an appointment", "اپائنٹمنٹ بک کریں")}
                </button>
              )}
            </div>
          </div>
          <div className="hc-alerts" aria-live="polite">
            {notice && (
              <div className="hc-notice">
                {notice}
                <button
                  onClick={() => setNotice("")}
                  aria-label={S("Dismiss", "بند کریں")}
                >
                  ×
                </button>
              </div>
            )}
            {error && (
              <div className="hc-error">
                {S("Connection issue: ", "کنکشن کا مسئلہ: ")}
                {error}
                <button onClick={load}>{S("Retry", "دوبارہ کوشش")}</button>
              </div>
            )}
          </div>
          {!state && !error && (
            <div className="hc-loading">
              <div className="hc-skeleton" />
              <p>
                {S("Opening your clinic workspace…", "ورک اسپیس کھل رہی ہے…")}
              </p>
            </div>
          )}
          {state && (
            <>
              {tab === "overview" && (
                <>
                  {own ? (
                    <>
                      <div className="hc-patient-grid">
                        <section className="hc-welcome hc-card">
                          <div className="hc-welcome-text">
                            <span className="hc-pill">
                              {S("YOUR NEXT STEP", "آپ کا اگلا قدم")}
                            </span>
                            <h2>
                              {future[0]
                                ? S(
                                    "Your next visit is arranged.",
                                    "آپ کی اگلی ملاقات طے ہے۔",
                                  )
                                : S(
                                    "A little clarity. Better care.",
                                    "واضح معلومات، بہتر نگہداشت۔",
                                  )}
                            </h2>
                            <p>
                              {future[0]
                                ? `${state.doctors.find((d) => d.id === future[0].doctor_id)?.name} · ${dateLabel(future[0].starts_at, lang)} · ${timeLabel(future[0].starts_at, lang)} PKT`
                                : S(
                                    "Find a consultant, choose a time and keep your visit history in one place.",
                                    "ڈاکٹر اور وقت منتخب کریں، ملاقاتوں کا ریکارڈ ایک جگہ رکھیں۔",
                                  )}
                            </p>
                            <button
                              className="hc-btn"
                              onClick={() =>
                                future[0]
                                  ? changeTab("appointments")
                                  : setBooking({})
                              }
                            >
                              {future[0]
                                ? S("View appointment", "اپائنٹمنٹ دیکھیں")
                                : S(
                                    "Find your next appointment",
                                    "اگلی اپائنٹمنٹ تلاش کریں",
                                  )}
                              <Icon name="arrow" />
                            </button>
                          </div>
                          <div className="hc-orbit" aria-hidden="true">
                            <span />
                            <span />
                            <div>
                              <Icon name="heart" />
                            </div>
                          </div>
                        </section>
                        <section className="hc-card hc-health-summary">
                          <div className="hc-card-title">
                            <h2>{S("At a glance", "ایک نظر میں")}</h2>
                            <span className="hc-pill">
                              {S("Sample", "نمونہ")}
                            </span>
                          </div>
                          <div className="hc-vitals">
                            <div>
                              <Icon name="heart" />
                              <b>
                                {latest?.data.vitals.heart_rate ?? "—"}
                                <small>bpm</small>
                              </b>
                              <span>{S("Heart rate", "دل کی دھڑکن")}</span>
                            </div>
                            <div>
                              <Icon name="pulse" />
                              <b>
                                {latest?.data.vitals.systolic ?? "—"}/
                                {latest?.data.vitals.diastolic ?? "—"}
                              </b>
                              <span>{S("Blood pressure", "بلڈ پریشر")}</span>
                            </div>
                            <div>
                              <Icon name="drop" />
                              <b>
                                {latest?.data.vitals.oxygen ?? "—"}
                                <small>%</small>
                              </b>
                              <span>{S("Oxygen", "آکسیجن")}</span>
                            </div>
                          </div>
                          <p className="hc-caption">
                            {latest
                              ? `${S("Recorded", "درج شدہ")} ${dateLabel(latest.visit_at, lang)}`
                              : S(
                                  "No readings recorded",
                                  "کوئی پیمائش درج نہیں",
                                )}
                          </p>
                        </section>
                      </div>
                      <div className="hc-three-grid">
                        <section className="hc-card">
                          <div className="hc-card-title">
                            <h2>{S("Appointments", "اپائنٹمنٹس")}</h2>
                            <button
                              className="hc-link"
                              onClick={() => changeTab("appointments")}
                            >
                              {S("See all", "تمام دیکھیں")}
                            </button>
                          </div>
                          <div className="hc-date-strip">
                            {Array.from({ length: 7 }, (_, i) =>
                              dayAfter(today, i),
                            ).map((d) => (
                              <span
                                key={d}
                                className={d === today ? "selected" : ""}
                              >
                                <small>
                                  {new Date(
                                    `${d}T12:00:00+05:00`,
                                  ).toLocaleDateString(
                                    lang === "ur" ? "ur-PK" : "en-GB",
                                    { weekday: "short" },
                                  )}
                                </small>
                                <b>{d.slice(-2)}</b>
                              </span>
                            ))}
                          </div>
                          <AppointmentList
                            appointments={future.slice(0, 2)}
                            state={state}
                            lang={lang}
                            S={S}
                            compact
                            onBook={() => setBooking({})}
                          />
                        </section>
                        <section className="hc-card">
                          <div className="hc-card-title">
                            <h2>{S("Your health history", "صحت کی تاریخ")}</h2>
                            <span className="hc-icon-tile">
                              <Icon name="pulse" />
                            </span>
                          </div>
                          <p className="hc-caption">
                            {S(
                              "Recorded observations, not a health score",
                              "درج شدہ پیمائشیں، صحت کا اسکور نہیں",
                            )}
                          </p>
                          <VitalChart
                            records={records.filter(
                              (r) =>
                                r.published &&
                                r.patient_id === state.patient.id,
                            )}
                            S={S}
                          />
                          <div className="hc-inline-stats">
                            <span>
                              <b>{latest?.data.vitals.temperature ?? "—"}°C</b>
                              {S("Temperature", "درجہ حرارت")}
                            </span>
                            <span>
                              <b>{records.filter((r) => r.published).length}</b>
                              {S("Published visits", "شائع شدہ ملاقاتیں")}
                            </span>
                          </div>
                        </section>
                        <section className="hc-card hc-care-plan">
                          <div className="hc-card-title">
                            <h2>{S("Follow-up plan", "فالو اپ پلان")}</h2>
                            <Icon name="records" />
                          </div>
                          <span className="hc-eyebrow">
                            {S("NEXT REVIEW", "اگلا جائزہ")}
                          </span>
                          <h3>
                            {latest?.data.follow_up
                              ? dateLabel(
                                  `${latest.data.follow_up}T12:00:00+05:00`,
                                  lang,
                                )
                              : S("Not recorded", "درج نہیں")}
                          </h3>
                          <p>
                            {S(
                              "Your clinician’s published instructions and prescriptions stay with your visit record.",
                              "ڈاکٹر کی شائع شدہ ہدایات اور نسخے ملاقات کے ریکارڈ کے ساتھ ہیں۔",
                            )}
                          </p>
                          <button
                            className="hc-btn secondary"
                            onClick={() => changeTab("records")}
                          >
                            {S("Open health records", "طبی ریکارڈ کھولیں")}
                            <Icon name="arrow" />
                          </button>
                        </section>
                      </div>
                      <div className="hc-two-grid">
                        <section className="hc-card">
                          <div className="hc-card-title">
                            <h2>
                              {S(
                                "Latest visit summary",
                                "آخری ملاقات کا خلاصہ",
                              )}
                            </h2>
                            <span className="hc-pill">
                              {S("Clinician entered", "ڈاکٹر کا درج کردہ")}
                            </span>
                          </div>
                          <h3>
                            {latest?.data.title ??
                              S(
                                "No published visits yet",
                                "ابھی کوئی شائع شدہ ملاقات نہیں",
                              )}
                          </h3>
                          <div className="hc-tags">
                            {latest?.data.diagnoses.map((d) => (
                              <span key={d}>{d}</span>
                            ))}
                          </div>
                          <p className="hc-caption">{latest?.data.notes}</p>
                        </section>
                        <section className="hc-card">
                          <div className="hc-card-title">
                            <h2>
                              {S("Allergies & prescriptions", "الرجی اور نسخے")}
                            </h2>
                            <Icon name="shield" />
                          </div>
                          <p>
                            <b>{S("Allergies: ", "الرجی: ")}</b>
                            {state.patient.allergies.join(", ") ||
                              S("Not recorded", "درج نہیں")}
                          </p>
                          {latest?.data.prescriptions.map((p) => (
                            <p className="hc-prescription" key={p}>
                              {p}
                            </p>
                          ))}
                        </section>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="hc-kpis">
                        {[
                          [
                            todays.filter(
                              (a) =>
                                !["cancelled", "no_show"].includes(a.status),
                            ).length,
                            S("Today’s visits", "آج کی ملاقاتیں"),
                            "calendar",
                          ],
                          [
                            queue.length,
                            S(
                              "Waiting / in consultation",
                              "منتظر / زیر ملاقات",
                            ),
                            "queue",
                          ],
                          [
                            state.conversations.filter(
                              (c) => c.handoff || c.staff_mode,
                            ).length,
                            S("Need a staff reply", "عملے کے جواب کے منتظر"),
                            "messages",
                          ],
                          [
                            todays.filter((a) =>
                              ["cancelled", "no_show"].includes(a.status),
                            ).length,
                            S("Cancelled / no-show", "منسوخ / غیر حاضر"),
                            "appointments",
                          ],
                        ].map(([n, l, i]) => (
                          <section className="hc-card hc-kpi" key={String(l)}>
                            <span className="hc-icon-tile">
                              <Icon name={String(i)} />
                            </span>
                            <b>{n}</b>
                            <p>{l}</p>
                          </section>
                        ))}
                      </div>
                      <div className="hc-two-grid wide">
                        <section className="hc-card">
                          <div className="hc-card-title">
                            <h2>
                              {S(
                                "Upcoming appointments",
                                "آنے والی اپائنٹمنٹس",
                              )}
                            </h2>
                            <button
                              className="hc-link"
                              onClick={() => changeTab("calendar")}
                            >
                              {S("Open schedule", "شیڈول کھولیں")}
                            </button>
                          </div>
                          <AppointmentList
                            appointments={appointments
                              .filter(
                                (a) =>
                                  ![
                                    "cancelled",
                                    "no_show",
                                    "completed",
                                  ].includes(a.status),
                              )
                              .slice(0, 5)}
                            state={state}
                            lang={lang}
                            S={S}
                            staff
                            busy={busy}
                            onStatus={status}
                            onReschedule={(a) =>
                              setBooking({
                                appointment: a,
                                doctorId: a.doctor_id,
                                patientId: a.patient_id,
                              })
                            }
                            onRecord={
                              role === "doctor" ? showClinical : undefined
                            }
                            onCall={setCall}
                          />
                        </section>
                        <section className="hc-card">
                          <div className="hc-card-title">
                            <h2>{S("Clinic activity", "کلینک کی سرگرمی")}</h2>
                            <span className="hc-live" />
                          </div>
                          <div className="hc-activity">
                            {state.activity.length ? (
                              state.activity.slice(0, 7).map((e, i) => (
                                <div key={`${e.at}-${i}`}>
                                  <span className="hc-activity-dot" />
                                  <div>
                                    <b>{activityLabel(e.kind, S)}</b>
                                    <p>
                                      {dateLabel(e.at, lang)} ·{" "}
                                      {timeLabel(e.at, lang)}
                                    </p>
                                  </div>
                                </div>
                              ))
                            ) : (
                              <p className="hc-caption">
                                {S(
                                  "Bookings, published records and simulated reminders will appear here.",
                                  "بکنگ، شائع شدہ ریکارڈ اور نمونہ یاد دہانیاں یہاں آئیں گی۔",
                                )}
                              </p>
                            )}
                          </div>
                          <div className="hc-outcomes">
                            <p>{S("Booked through", "بکنگ کا ذریعہ")}</p>
                            {["chat", "portal", "reception", "sample"].map(
                              (source) => (
                                <div key={source}>
                                  <span>{source}</span>
                                  <b>
                                    {
                                      appointments.filter(
                                        (a) => a.source === source,
                                      ).length
                                    }
                                  </b>
                                </div>
                              ),
                            )}
                            <div>
                              <span>
                                {S("Completed visits", "مکمل ملاقاتیں")}
                              </span>
                              <b>
                                {
                                  appointments.filter(
                                    (a) => a.status === "completed",
                                  ).length
                                }
                              </b>
                            </div>
                          </div>
                        </section>
                      </div>
                      <section className="hc-card">
                        <div className="hc-card-title">
                          <h2>
                            {S(
                              "Reminders & follow-ups",
                              "یاد دہانیاں اور فالو اپ",
                            )}
                          </h2>
                          <span className="hc-pill">
                            {S("Simulation only", "صرف نمونہ")}
                          </span>
                        </div>
                        <p className="hc-caption">
                          {S(
                            "Reminder previews are scheduled one day and two hours before a visit. Use the buttons to log a simulated send, without contacting anyone.",
                            "نمونہ یاد دہانی ملاقات سے ایک دن اور دو گھنٹے پہلے ہے۔ بٹن صرف نمونہ سرگرمی درج کرتا ہے۔",
                          )}
                        </p>
                        <div className="hc-reminders">
                          {future.slice(0, 3).map((a) => (
                            <div key={a.id}>
                              <span>
                                <b>
                                  {
                                    state.patients.find(
                                      (p) => p.id === a.patient_id,
                                    )?.name
                                  }
                                </b>
                                <small>
                                  {S("Reminder preview", "نمونہ یاد دہانی")}:{" "}
                                  {dateLabel(
                                    new Date(
                                      new Date(a.starts_at).getTime() -
                                        86400000,
                                    ).toISOString(),
                                    lang,
                                  )}{" "}
                                  ·{" "}
                                  {timeLabel(
                                    new Date(
                                      new Date(a.starts_at).getTime() - 7200000,
                                    ).toISOString(),
                                    lang,
                                  )}
                                </small>
                              </span>
                              <button
                                className="hc-btn secondary"
                                disabled={busy}
                                onClick={() =>
                                  act({
                                    action: "reminder",
                                    patientId: a.patient_id,
                                  })
                                }
                              >
                                {S("Simulate reminder", "نمونہ یاد دہانی")}
                              </button>
                            </div>
                          ))}
                        </div>
                        <button
                          className="hc-link"
                          disabled={busy}
                          onClick={() =>
                            act({
                              action: "reminder",
                              patientId: selectedPatient?.id,
                              followUp: true,
                            })
                          }
                        >
                          {S(
                            "Simulate follow-up for selected patient",
                            "منتخب مریض کا نمونہ فالو اپ",
                          )}
                        </button>
                      </section>
                    </>
                  )}
                </>
              )}
              {tab === "doctors" && (
                <DoctorDirectory
                  state={state}
                  S={S}
                  onBook={(id) => setBooking({ doctorId: id })}
                />
              )}
              {tab === "appointments" && (
                <section className="hc-card">
                  <AppointmentList
                    appointments={appointments}
                    state={state}
                    lang={lang}
                    S={S}
                    onBook={() => setBooking({})}
                    busy={busy}
                    onCancel={(a) => status(a, "cancelled")}
                    onReschedule={(a) =>
                      setBooking({ appointment: a, doctorId: a.doctor_id })
                    }
                    onCall={setCall}
                  />
                </section>
              )}
              {tab === "calendar" && (
                <CalendarView
                  state={state}
                  doctorId={role === "doctor" ? doctorId : undefined}
                  S={S}
                  lang={lang}
                  onSelect={(a) =>
                    setBooking({
                      appointment: a,
                      doctorId: a.doctor_id,
                      patientId: a.patient_id,
                    })
                  }
                  onRecord={role === "doctor" ? showClinical : undefined}
                />
              )}
              {tab === "queue" && (
                <section className="hc-card">
                  <div className="hc-card-title">
                    <h2>{S("Today’s waiting room", "آج کا انتظار گاہ")}</h2>
                    <span className="hc-pill">
                      {S("Live demo", "لائیو ڈیمو")}
                    </span>
                  </div>
                  <AppointmentList
                    appointments={[
                      ...queue,
                      ...todays.filter((a) => a.status === "confirmed"),
                    ]}
                    state={state}
                    lang={lang}
                    S={S}
                    staff
                    busy={busy}
                    onStatus={status}
                    onCall={setCall}
                  />
                </section>
              )}
              {tab === "records" && (
                <>
                  <div className="hc-section-toolbar">
                    {role === "doctor" && (
                      <>
                        <select
                          value={patientId}
                          aria-label={S("Select patient", "مریض منتخب کریں")}
                          onChange={(e) => setPatientId(e.target.value)}
                        >
                          {state.patients.map((p) => (
                            <option key={p.id} value={p.id}>
                              {p.name}
                            </option>
                          ))}
                        </select>
                        <button
                          className="hc-btn"
                          onClick={() => setClinical({ patientId })}
                        >
                          <Icon name="plus" />
                          {S("Create visit record", "ملاقات کا ریکارڈ بنائیں")}
                        </button>
                      </>
                    )}
                  </div>
                  <RecordList
                    records={records.filter(
                      (r) =>
                        r.patient_id === (own ? state.patient.id : patientId),
                    )}
                    state={state}
                    lang={lang}
                    S={S}
                    onEdit={
                      role === "doctor"
                        ? (r) =>
                            setClinical({ patientId: r.patient_id, record: r })
                        : undefined
                    }
                  />
                </>
              )}
              {tab === "messages" && (
                <div className="hc-message-layout">
                  <section className="hc-card hc-patient-chat">
                    <ChatWindow
                      slug={slug}
                      token={token}
                      name={name}
                      lang={lang}
                      prompts={
                        lang === "ur"
                          ? [
                              "ڈاکٹر کی اپائنٹمنٹ بک کرنی ہے",
                              "میری رپورٹ کہاں ہے؟",
                            ]
                          : [
                              "Book a doctor appointment",
                              "Where are my reports?",
                            ]
                      }
                      healthcare
                    />
                  </section>
                  <aside className="hc-card">
                    <h2>{S("Here to help", "مدد کے لیے حاضر")}</h2>
                    <p className="hc-caption">
                      {S(
                        "Ask about sample doctors, availability or your booking. Clinical questions go to staff.",
                        "نمونہ ڈاکٹر، اوقات یا بکنگ کے بارے میں پوچھیں۔ طبی سوالات عملے کو منتقل ہوتے ہیں۔",
                      )}
                    </p>
                    <button
                      className="hc-btn secondary"
                      onClick={() => setBooking({})}
                    >
                      {S("Open booking calendar", "بکنگ کیلنڈر کھولیں")}
                    </button>
                  </aside>
                </div>
              )}
              {tab === "inbox" && (
                <Inbox state={state} S={S} lang={lang} run={run} busy={busy} />
              )}
              {tab === "patients" && (
                <div className="hc-patients-layout">
                  <PatientList
                    patients={filteredPatients}
                    selected={patientId}
                    onSelect={setPatientId}
                    search={search}
                    onSearch={setSearch}
                    S={S}
                  />
                  <div>
                    <section className="hc-card hc-patient-header">
                      <Avatar name={selectedPatient?.name ?? "Patient"} />
                      <div>
                        <h2>{selectedPatient?.name}</h2>
                        <p>
                          {S("Fictional patient", "فرضی مریض")} ·{" "}
                          {selectedPatient?.age ?? "—"} {S("years", "سال")}
                        </p>
                        <p>
                          {S("Allergies", "الرجی")}:{" "}
                          {selectedPatient?.allergies.join(", ") ||
                            S("Not recorded", "درج نہیں")}
                        </p>
                      </div>
                      {role === "doctor" ? (
                        <button
                          className="hc-btn"
                          onClick={() => setClinical({ patientId })}
                        >
                          {S("New visit record", "نیا ملاقات ریکارڈ")}
                        </button>
                      ) : (
                        <button
                          className="hc-btn"
                          onClick={() => setBooking({ patientId })}
                        >
                          {S("Book visit", "ملاقات بک کریں")}
                        </button>
                      )}
                    </section>
                    <RecordList
                      records={records.filter(
                        (r) => r.patient_id === patientId,
                      )}
                      state={state}
                      lang={lang}
                      S={S}
                      onEdit={
                        role === "doctor"
                          ? (r) =>
                              setClinical({
                                patientId: r.patient_id,
                                record: r,
                              })
                          : undefined
                      }
                    />
                  </div>
                </div>
              )}
              {tab === "schedules" && (
                <ScheduleEditor
                  state={state}
                  S={S}
                  lang={lang}
                  run={run}
                  busy={busy}
                />
              )}
            </>
          )}
          <footer className="hc-footer">
            {S(
              "Built by NexusPoint · Synthetic medical data · Demo role switching is for presentation, not patient authentication.",
              "نیکسس پوائنٹ کا تیار کردہ۔ فرضی طبی معلومات۔ کردار کی تبدیلی صرف نمائش کے لیے ہے، مریض کی تصدیق نہیں۔",
            )}
          </footer>
        </main>
      </div>
      {booking && state && (
        <BookingDialog
          state={state}
          initial={booking}
          credentials={{ slug, t: token, visitor, role }}
          S={S}
          lang={lang}
          run={run}
          busy={busy}
          onClose={() => setBooking(null)}
        />
      )}
      {call && state && (
        <CallDialog
          appointment={call}
          state={state}
          S={S}
          onClose={() => setCall(null)}
          onComplete={
            role === "doctor"
              ? () => {
                  status(call, "completed");
                  setCall(null);
                }
              : undefined
          }
        />
      )}
      {clinical && state && (
        <ClinicalDialog
          state={state}
          initial={clinical}
          doctorId={doctorId}
          S={S}
          run={run}
          busy={busy}
          onClose={() => setClinical(null)}
        />
      )}
      {profile && (
        <Modal
          small
          title={S("Use a fictional name", "فرضی نام استعمال کریں")}
          onClose={() => setProfile(false)}
        >
          <p>
            {S(
              "This is an outreach demo. Keep real patient information out of it.",
              "یہ ڈیمو ہے۔ اصل مریض کی معلومات درج نہ کریں۔",
            )}
          </p>
          <form
            onSubmit={async (e) => {
              e.preventDefault();
              const f = new FormData(e.currentTarget);
              try {
                await run({ action: "profile", name: f.get("name") });
                setProfile(false);
              } catch {}
            }}
          >
            <label>
              {S("Sample name", "نمونہ نام")}
              <input
                name="name"
                required
                maxLength={80}
                defaultValue={state?.patient.name}
              />
            </label>
            <div className="hc-modal-actions">
              <button
                type="button"
                className="hc-btn secondary"
                onClick={() => setProfile(false)}
              >
                {S("Close", "بند کریں")}
              </button>
              <button className="hc-btn" disabled={busy}>
                {S("Save", "محفوظ کریں")}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
function VitalChart({
  records,
  S,
}: {
  records: ClinicalRecord[];
  S: Translator;
}) {
  const points = records
    .slice(0, 6)
    .reverse()
    .filter((r) => r.data.vitals.heart_rate !== null);
  const coordinates = points.map(
    (r, i) =>
      `${30 + i * (260 / Math.max(1, points.length - 1))},${120 - ((r.data.vitals.heart_rate ?? 70) - 50) * 1.2}`,
  );
  return (
    <div className="hc-chart">
      <svg
        viewBox="0 0 320 160"
        role="img"
        aria-label={S(
          "Recorded sample heart rate over past visits",
          "نمونہ ملاقاتوں میں دل کی درج شدہ دھڑکن",
        )}
      >
        <path
          d="M20 30H300M20 75H300M20 120H300"
          stroke="currentColor"
          opacity=".1"
        />
        <text x="2" y="32">
          125
        </text>
        <text x="2" y="77">
          90
        </text>
        <text x="2" y="122">
          50
        </text>
        {points.length > 1 && (
          <>
            <polygon
              points={`30,140 ${coordinates.join(" ")} 290,140`}
              fill="var(--hc-teal)"
              opacity=".1"
            />
            <polyline
              points={coordinates.join(" ")}
              fill="none"
              stroke="var(--hc-teal)"
              strokeWidth="3"
            />
          </>
        )}
        {coordinates.map((c, i) => (
          <circle
            key={i}
            cx={c.split(",")[0]}
            cy={c.split(",")[1]}
            r="5"
            fill="var(--hc-teal)"
          />
        ))}
        {points.map((r, i) => (
          <text
            key={r.id}
            x={30 + i * (260 / Math.max(1, points.length - 1))}
            y="157"
            textAnchor="middle"
          >
            {localDate(r.visit_at).slice(5)}
          </text>
        ))}
      </svg>
      <span>
        {points.length === 1
          ? S(
              "One recorded reading. More visits will show a trend.",
              "ایک پیمائش درج ہے۔ مزید ملاقاتوں سے رجحان ظاہر ہو گا۔",
            )
          : S("Heart rate · bpm", "دل کی دھڑکن")}
      </span>
    </div>
  );
}
function activityLabel(kind: string, S: Translator) {
  const labels: Record<string, [string, string]> = {
    booking: ["Appointment booked", "اپائنٹمنٹ بک ہوئی"],
    reschedule: ["Appointment rescheduled", "اپائنٹمنٹ کا وقت بدلا"],
    record_published: ["Visit record published", "ملاقات کا ریکارڈ شائع ہوا"],
    simulated_reminder: ["Reminder simulated", "نمونہ یاد دہانی"],
    simulated_follow_up: ["Follow-up simulated", "نمونہ فالو اپ"],
    checked_in: ["Patient checked in", "مریض پہنچ گیا"],
    in_consultation: ["Consultation started", "ملاقات شروع ہوئی"],
    completed: ["Consultation completed", "ملاقات مکمل ہوئی"],
    cancelled: ["Appointment cancelled", "اپائنٹمنٹ منسوخ"],
    no_show: ["Patient marked absent", "مریض غیر حاضر"],
  };
  return labels[kind] ? S(...labels[kind]) : kind;
}

export type Mode = "in_person" | "phone" | "video";
export type Status =
  | "confirmed"
  | "checked_in"
  | "in_consultation"
  | "completed"
  | "cancelled"
  | "no_show";
export type Schedule = { day: number; start: string; end: string }[];
export type Doctor = {
  id: string;
  slug: string;
  name: string;
  specialty: string;
  bio: string;
  modes: Mode[];
  schedule: Schedule;
  active: boolean;
};
export type Patient = {
  id: string;
  slug: string;
  visitor: string;
  name: string;
  age: number | null;
  allergies: string[];
  created_at: string;
};
export type Appointment = {
  id: string;
  slug: string;
  patient_id: string;
  doctor_id: string;
  starts_at: string;
  ends_at: string;
  mode: Mode;
  status: Status;
  source: string;
  reason: string;
  request_id: string;
  queue_number: number | null;
  created_at: string;
};
export type Block = {
  id: string;
  slug: string;
  doctor_id: string;
  starts_at: string;
  ends_at: string;
  reason: string;
  active: boolean;
};
export type RecordData = {
  title: string;
  diagnoses: string[];
  notes: string;
  prescriptions: string[];
  tests: { name: string; value: string; unit: string; range: string }[];
  vitals: {
    systolic: number | null;
    diastolic: number | null;
    heart_rate: number | null;
    temperature: number | null;
    oxygen: number | null;
  };
  follow_up: string;
};
export type ClinicalRecord = {
  id: string;
  slug: string;
  patient_id: string;
  doctor_id: string;
  appointment_id: string | null;
  visit_at: string;
  published: boolean;
  data: RecordData;
  created_at: string;
  updated_at: string;
};
export type Choice = {
  kind: "doctor" | "slot" | "mode" | "cancel" | "reschedule" | "food_item" | "food_mode" | "food_confirm" | "food_clear" | "table_party" | "table_time" | "table_confirm" | "school_student" | "school_program" | "school_visit" | "school_time" | "school_confirm";
  value: string;
  label: string;
};
export type ClinicConversation = {
  id: string;
  visitor: string;
  channel: string;
  summary: string | null;
  handoff: boolean;
  staff_mode: boolean;
  assigned_to: string | null;
  last_at: string;
  messages: {
    role: string;
    content: string;
    at: string;
    source: string | null;
    cards?: Choice[] | null;
  }[];
};
export type HealthcareState = {
  doctors: Doctor[];
  patients: Patient[];
  patient: Patient;
  appointments: Appointment[];
  records: ClinicalRecord[];
  blocks: Block[];
  conversations: ClinicConversation[];
  activity: { kind: string; at: string; detail: Record<string, unknown> }[];
  server_time: string;
  expires_at: string;
};
export const emptyRecord = (): RecordData => ({
  title: "Consultation summary",
  diagnoses: [],
  notes: "",
  prescriptions: [],
  tests: [],
  vitals: {
    systolic: null,
    diastolic: null,
    heart_rate: null,
    temperature: null,
    oxygen: null,
  },
  follow_up: "",
});

export function localDate(at: string | Date = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Karachi",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(at));
}
export function dayAfter(date: string, days = 1) {
  return new Date(
    new Date(`${date}T12:00:00+05:00`).getTime() + days * 86400000,
  )
    .toISOString()
    .slice(0, 10);
}
export function timeLabel(at: string, lang = "en") {
  return new Date(at).toLocaleTimeString(lang === "ur" ? "ur-PK" : "en-US", {
    timeZone: "Asia/Karachi",
    hour: "numeric",
    minute: "2-digit",
  });
}
export function dateLabel(at: string, lang = "en") {
  return new Date(at).toLocaleDateString(lang === "ur" ? "ur-PK" : "en-GB", {
    timeZone: "Asia/Karachi",
    weekday: "short",
    day: "numeric",
    month: "short",
  });
}

export function availableSlots(
  doctor: Doctor,
  date: string,
  appointments: Appointment[],
  blocks: Block[],
  expires: string,
  now = new Date(),
): string[] {
  if (!doctor.active) return [];
  if (
    !/^\d{4}-\d{2}-\d{2}$/.test(date) ||
    date < localDate(now) ||
    date > dayAfter(localDate(now), 13)
  )
    return [];
  const weekday = new Date(`${date}T12:00:00+05:00`).getUTCDay();
  const slots: string[] = [];
  for (const s of doctor.schedule.filter((s) => s.day === weekday)) {
    let start = new Date(`${date}T${s.start}:00+05:00`).getTime();
    const end = new Date(`${date}T${s.end}:00+05:00`).getTime();
    start = Math.ceil(start / 1800000) * 1800000;
    for (; start + 1800000 <= end; start += 1800000) {
      if (
        start <= now.getTime() ||
        start + 1800000 > new Date(expires).getTime()
      )
        continue;
      if (
        appointments.some(
          (a) =>
            a.doctor_id === doctor.id &&
            !["cancelled", "no_show"].includes(a.status) &&
            new Date(a.starts_at).getTime() === start,
        )
      )
        continue;
      if (
        blocks.some(
          (b) =>
            b.active &&
            b.doctor_id === doctor.id &&
            new Date(b.starts_at).getTime() < start + 1800000 &&
            new Date(b.ends_at).getTime() > start,
        )
      )
        continue;
      slots.push(new Date(start).toISOString());
    }
  }
  return [...new Set(slots)].sort();
}

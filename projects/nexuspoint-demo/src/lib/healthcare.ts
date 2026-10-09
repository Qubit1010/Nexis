import { randomUUID } from "node:crypto";
import { rest, type Business, type Conversation, type Message } from "./db.ts";
import {
  availableSlots,
  dayAfter,
  emptyRecord,
  localDate,
  type Appointment,
  type Block,
  type ClinicalRecord,
  type Doctor,
  type HealthcareState,
  type Patient,
  type RecordData,
  type Schedule,
} from "./healthcare-types.ts";

const q = (slug: string) => `slug=eq.${encodeURIComponent(slug)}`;
const stamp = () => new Date().toISOString();
export async function rpc<T>(name: string, body: unknown): Promise<T> {
  return (await rest("POST", `rpc/${name}`, body)) as unknown as T;
}

export function scheduleFromFacts(b: Business): Schedule {
  const names = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ];
  const result: Schedule = [];
  const clock = (h: string, m: string | undefined, ap: string) =>
    `${String((+h % 12) + (ap.toUpperCase() === "PM" ? 12 : 0)).padStart(2, "0")}:${m ?? "00"}`;
  for (const h of b.profile.facts.hours) {
    if (/closed/i.test(h.hours)) continue;
    const match = h.hours.match(
      /(\d{1,2})(?::(\d{2}))?\s*(AM|PM)\s*(?:to|–|-)\s*(\d{1,2})(?::(\d{2}))?\s*(AM|PM)/i,
    );
    const day = names.indexOf(h.day);
    if (day < 0) continue;
    if (match)
      result.push({
        day,
        start: clock(match[1], match[2], match[3]),
        end: clock(match[4], match[5], match[6]),
      });
    else if (/24/i.test(h.hours))
      result.push({ day, start: "09:00", end: "17:00" });
  }
  // Unknown listing hours remain explicitly illustrative in the demo.
  if (
    b.profile.facts.hours.length &&
    b.profile.facts.hours.every((h) => /closed/i.test(h.hours))
  )
    return [];
  return result.length
    ? result
    : [1, 2, 3, 4, 5, 6].map((day) => ({ day, start: "09:00", end: "16:00" }));
}

const isDerm = (b: Business) =>
  !/dent/i.test(b.profile.facts.category ?? b.name) &&
  /skin|derma|cosmet|laser|allerg/i.test(`${b.profile.facts.category ?? ""} ${b.name}`);

export function sampleRecord(dental: boolean, offset = 0, derm = false): RecordData {
  return {
    ...emptyRecord(),
    title: dental
      ? "Dental assessment · sample"
      : derm
        ? "Skin consultation · sample"
        : "General consultation · sample",
    diagnoses: dental
      ? ["Dental plaque buildup (sample)"]
      : derm
        ? ["Mild acne vulgaris (sample)"]
        : ["Seasonal allergic rhinitis (sample)"],
    notes:
      "Fictional demonstration record entered by the sample clinician. Follow-up arranged. This is not medical advice or a real patient record.",
    prescriptions: [
      "Sample prescription entry. No medicine or dosage is prescribed in this demo.",
    ],
    tests: dental || derm
      ? [
          {
            name: derm ? "Skin examination" : "Dental examination",
            value: "Sample completed",
            unit: "",
            range: "Clinician assessment",
          },
        ]
      : [
          {
            name: "Hemoglobin",
            value: "13.8",
            unit: "g/dL",
            range: "Sample lab reference: 12–16",
          },
        ],
    vitals: {
      systolic: 118 + offset * 2,
      diastolic: 76 + offset,
      heart_rate: 72 + offset * 3,
      temperature: 36.7,
      oxygen: 98,
    },
    follow_up: dayAfter(localDate(), 5),
  };
}

export async function ensureHealthcare(b: Business) {
  if (
    (await rest("GET", `demo_healthcare_seed?${q(b.slug)}&select=slug&limit=1`))
      .length
  )
    return;
  const dental = /dent/i.test(b.profile.facts.category ?? b.name);
  const derm = isDerm(b);
  const specialties = dental
    ? ["General dentistry", "Orthodontics", "Restorative dentistry"]
    : derm
      ? ["Dermatology", "Cosmetology and laser", "Hair and scalp", "Allergy"]
      : ["General medicine", "Cardiology", "Pediatrics", "Gynecology"];
  const names = [
    "Dr. Sara Ahmed",
    "Dr. Hamza Khan",
    "Dr. Nadia Baloch",
    "Dr. Mariam Ali",
  ];
  const doctors: Doctor[] = specialties.map((specialty, i) => ({
    id: `${b.slug}-doctor-${i + 1}`,
    slug: b.slug,
    name: names[i],
    specialty,
    bio: "Fictional consultant profile for this demonstration. Clinic credentials and services would be confirmed before a real launch.",
    modes: ["in_person", "phone", "video"],
    schedule: scheduleFromFacts(b),
    active: true,
  }));
  const patients: Patient[] = [
    "Ayesha Khan",
    "Bilal Ahmed",
    "Zainab Baloch",
  ].map((name, i) => ({
    id: randomUUID(),
    slug: b.slug,
    visitor: `sample-${i}`,
    name,
    age: 28 + i * 8,
    allergies: i === 0 ? ["Dust (sample)"] : [],
    created_at: stamp(),
  }));
  const records: ClinicalRecord[] = patients.flatMap((p) =>
    [0, 1].map((i) => ({
      id: randomUUID(),
      slug: b.slug,
      patient_id: p.id,
      doctor_id: doctors[0].id,
      appointment_id: null,
      visit_at: new Date(Date.now() - (7 + i * 14) * 86400000).toISOString(),
      published: true,
      data: sampleRecord(dental, i, derm),
      created_at: stamp(),
      updated_at: stamp(),
    })),
  );
  const appointments: Appointment[] = [];
  for (let i = 0; i < patients.length; i++) {
    let start: string | undefined;
    for (let offset = 0; offset < 14 && !start; offset++)
      start = availableSlots(
        doctors[i % doctors.length],
        dayAfter(localDate(), offset),
        appointments,
        [],
        b.expires_at,
      )[i];
    if (start)
      appointments.push({
        id: randomUUID(),
        slug: b.slug,
        patient_id: patients[i].id,
        doctor_id: doctors[i % doctors.length].id,
        starts_at: start,
        ends_at: new Date(new Date(start).getTime() + 1800000).toISOString(),
        mode: i === 1 ? "video" : "in_person",
        status: "confirmed",
        source: "sample",
        reason: "Sample follow-up consultation",
        request_id: `seed-${i}`,
        queue_number: null,
        created_at: stamp(),
      });
  }
  await rpc("demo_seed_healthcare", {
    p_slug: b.slug,
    p_seed: { doctors, patients, records, appointments },
  });
}

export async function ensurePatient(
  b: Business,
  visitor: string,
): Promise<Patient> {
  const path = `demo_patients?${q(b.slug)}&visitor=eq.${encodeURIComponent(visitor)}&limit=1`;
  let p = (await rest<Patient>("GET", path))[0];
  if (!p) {
    await rest(
      "POST",
      "demo_patients?on_conflict=slug,visitor",
      {
        slug: b.slug,
        visitor,
        name: "Demo patient",
        age: 29,
        allergies: ["Dust (sample)"],
      },
      "resolution=ignore-duplicates,return=minimal",
    );
    p = (await rest<Patient>("GET", path))[0];
    // One unique record per visitor and visit date prevents simultaneous first loads duplicating samples.
    const doctor = (
      await rest<Doctor>(
        "GET",
        `demo_doctors?${q(b.slug)}&order=id.asc&limit=1`,
      )
    )[0];
    if (doctor) {
      const recordId = p.id; // patient UUID is unique and valid as the initial record's UUID
      await rest(
        "POST",
        "demo_clinical_records?on_conflict=id",
        {
          id: recordId,
          slug: b.slug,
          patient_id: p.id,
          doctor_id: doctor.id,
          visit_at: new Date(Date.now() - 7 * 86400000).toISOString(),
          published: true,
          data: sampleRecord(/dent/i.test(b.profile.facts.category ?? b.name), 0, isDerm(b)),
        },
        "resolution=ignore-duplicates,return=minimal",
      );
    }
  }
  return p;
}

export async function healthcareState(
  b: Business,
  visitor: string,
  role: string,
): Promise<HealthcareState> {
  await ensureHealthcare(b);
  const patient = await ensurePatient(b, visitor);
  const own = role === "patient";
  const results = await Promise.all([
    rest<Doctor>("GET", `demo_doctors?${q(b.slug)}&order=id.asc`),
    rest<Patient>(
      "GET",
      `demo_patients?${q(b.slug)}${own ? `&id=eq.${patient.id}` : ""}&order=created_at.desc&limit=200`,
    ),
    rest<Appointment>(
      "GET",
      `demo_appointments?${q(b.slug)}${own ? `&patient_id=eq.${patient.id}` : ""}&order=starts_at.asc&limit=500`,
    ),
    rest<ClinicalRecord>(
      "GET",
      `demo_clinical_records?${q(b.slug)}${own ? `&patient_id=eq.${patient.id}&published=eq.true` : ""}&order=visit_at.desc&limit=200`,
    ),
    rest<Block>("GET", `demo_schedule_blocks?${q(b.slug)}&active=eq.true`),
    rest<Conversation>(
      "GET",
      `demo_conversations?${q(b.slug)}${own ? `&visitor=eq.${encodeURIComponent(visitor)}&channel=eq.web` : ""}&order=last_at.desc&limit=100`,
    ),
  ]);
  const [doctors, patients, appointments, records, blocks, convs] = results;
  const ids = convs.map((c) => c.id);
  const messages = ids.length
    ? await rest<Message>(
        "GET",
        `demo_messages?conversation_id=in.(${ids.join(",")})&order=id.desc&limit=3000`,
      )
    : [];
  const activity = own
    ? []
    : await rest<{ kind: string; at: string; detail: Record<string, unknown> }>(
        "GET",
        `demo_events?${q(b.slug)}&kind=in.(booking,reschedule,record_published,simulated_reminder,simulated_follow_up,checked_in,in_consultation,completed,cancelled,no_show)&order=at.desc&limit=30`,
      );
  return {
    doctors,
    patients,
    patient,
    appointments,
    records,
    blocks,
    activity,
    conversations: convs.map((c) => ({
      ...c,
      staff_mode: c.staff_mode ?? false,
      assigned_to: c.assigned_to ?? null,
      messages: messages.filter((m) => m.conversation_id === c.id).reverse(),
    })),
    server_time: stamp(),
    expires_at: b.expires_at,
  };
}

export async function availability(b: Business, doctor: Doctor, date: string) {
  const [appointments, blocks] = await Promise.all([
    rest<Appointment>(
      "GET",
      `demo_appointments?${q(b.slug)}&doctor_id=eq.${encodeURIComponent(doctor.id)}&starts_at=gte.${encodeURIComponent(`${date}T00:00:00+05:00`)}&starts_at=lt.${encodeURIComponent(`${dayAfter(date)}T00:00:00+05:00`)}`,
    ),
    rest<Block>(
      "GET",
      `demo_schedule_blocks?${q(b.slug)}&doctor_id=eq.${encodeURIComponent(doctor.id)}&active=eq.true`,
    ),
  ]);
  return availableSlots(doctor, date, appointments, blocks, b.expires_at);
}

export async function book(
  b: Business,
  patientId: string,
  doctorId: string,
  start: string,
  mode: string,
  source: string,
  reason: string,
  requestId: string,
) {
  const rows = await rpc<Appointment[]>("demo_book_appointment", {
    p_slug: b.slug,
    p_patient: patientId,
    p_doctor: doctorId,
    p_start: start,
    p_mode: mode,
    p_source: source,
    p_reason: reason,
    p_request: requestId,
  });
  return rows[0];
}

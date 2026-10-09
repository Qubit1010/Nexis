import { NextResponse } from "next/server";
import {
  authorised,
  expired,
  getBusiness,
  logEvent,
  rest,
  type Conversation,
} from "@/lib/db";
import {
  availability,
  book,
  ensureHealthcare,
  ensurePatient,
  healthcareState,
  rpc,
  scheduleFromFacts,
} from "@/lib/healthcare";
import type {
  Appointment,
  ClinicalRecord,
  Doctor,
  Patient,
  RecordData,
  Schedule,
} from "@/lib/healthcare-types";

export const dynamic = "force-dynamic";
const response = (data: unknown, status = 200) =>
  NextResponse.json(data, { status, headers: { "Cache-Control": "no-store" } });
const str = (value: unknown, max = 200) =>
  typeof value === "string" ? value.trim().slice(0, max) : "";
const uuid = (s: string) =>
  /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i.test(s);
const fail = (message: string): never => {
  throw new Error(`INVALID: ${message}`);
};
function error(e: unknown) {
  const message =
    e instanceof Error ? e.message : "Connection problem. Please try again.";
  const conflict = message.includes("CONFLICT:");
  const invalid = message.includes("INVALID:");
  const detail = message.match(/(?:CONFLICT|INVALID): ([^"\\]+)/)?.[1];
  return response(
    {
      error:
        detail ??
        "The clinic could not complete this request. Please try again.",
    },
    conflict ? 409 : invalid ? 400 : 500,
  );
}
async function access(slug: string, t: string, visitor: string, role: string) {
  const b = await getBusiness(slug);
  if (!authorised(b, t) || b.sector !== "healthcare") return null;
  if (expired(b)) throw new Error("INVALID: This demo has expired");
  if (
    !/^[a-zA-Z0-9_-]{8,64}$/.test(visitor) ||
    !["patient", "clinic", "doctor"].includes(role)
  )
    fail("Invalid demo session");
  return b;
}
export async function GET(req: Request) {
  try {
    const u = new URL(req.url),
      p = u.searchParams;
    const b = await access(
      p.get("slug") ?? "",
      p.get("t") ?? "",
      p.get("visitor") ?? "",
      p.get("role") ?? "patient",
    );
    if (!b) return response({ error: "Not found" }, 404);
    if (p.has("doctorId")) {
      await ensureHealthcare(b);
      const doctor = (
        await rest<Doctor>(
          "GET",
          `demo_doctors?slug=eq.${encodeURIComponent(b.slug)}&id=eq.${encodeURIComponent(p.get("doctorId") ?? "")}&limit=1`,
        )
      )[0];
      const date = p.get("date") ?? "";
      if (
        !doctor ||
        !/^\d{4}-\d{2}-\d{2}$/.test(date) ||
        Number.isNaN(Date.parse(`${date}T12:00:00+05:00`))
      )
        fail("Choose a doctor and valid date");
      return response({ slots: await availability(b, doctor, date) });
    }
    return response(
      await healthcareState(b, p.get("visitor")!, p.get("role") ?? "patient"),
    );
  } catch (e) {
    return error(e);
  }
}

export async function POST(req: Request) {
  try {
    const input = (await req.json()) as Record<string, unknown>;
    const slug = str(input.slug),
      visitor = str(input.visitor, 64),
      role = str(input.role) || "patient";
    const b = await access(slug, str(input.t), visitor, role);
    if (!b) return response({ error: "Not found" }, 404);
    await ensureHealthcare(b);
    const self = await ensurePatient(b, visitor),
      action = str(input.action);
    const scoped = `slug=eq.${encodeURIComponent(b.slug)}`;
    const staff = () => {
      if (role === "patient")
        fail("Switch to a staff demo view for this action");
    };
    const patientId =
      role === "patient" ? self.id : str(input.patientId) || self.id;
    if (!uuid(patientId)) fail("Invalid patient");
    if (
      !(
        await rest<Patient>(
          "GET",
          `demo_patients?${scoped}&id=eq.${patientId}&limit=1`,
        )
      )[0]
    )
      fail("Unknown patient");
    let result: unknown = { ok: true };
    if (action === "book") {
      const requestId = str(input.requestId, 100);
      if (!requestId) fail("Booking request identifier required");
      const start = str(input.start);
      if (!Number.isFinite(Date.parse(start))) fail("Invalid appointment time");
      result = await book(
        b,
        patientId,
        str(input.doctorId),
        start,
        str(input.mode),
        role === "patient" ? "portal" : "reception",
        str(input.reason, 500),
        requestId,
      );
      await logEvent(b.slug, "booking", {
        source: role === "patient" ? "portal" : "reception",
      });
    } else if (action === "appointment") {
      const id = str(input.id);
      if (!uuid(id)) fail("Invalid appointment");
      const a = (
        await rest<Appointment>(
          "GET",
          `demo_appointments?${scoped}&id=eq.${id}&limit=1`,
        )
      )[0];
      if (!a || (role === "patient" && a.patient_id !== self.id))
        return response({ error: "Not found" }, 404);
      const status = str(input.status),
        start = str(input.start);
      if (
        role === "patient" &&
        ((status !== "cancelled" && !start) || a.status !== "confirmed")
      )
        fail("Patients can reschedule or cancel confirmed bookings");
      if (start && !Number.isFinite(Date.parse(start)))
        fail("Invalid appointment time");
      result = (
        await rpc<Appointment[]>("demo_change_appointment", {
          p_slug: b.slug,
          p_id: id,
          p_status: status || a.status,
          p_start: start || null,
          p_doctor: str(input.doctorId) || null,
          p_mode: str(input.mode) || null,
        })
      )[0];
      await logEvent(b.slug, start ? "reschedule" : status, {
        appointment_id: id,
      });
    } else if (action === "schedule") {
      staff();
      let schedule: Schedule | null = null;
      if (input.schedule !== undefined) {
        if (!Array.isArray(input.schedule) || input.schedule.length > 7)
          fail("Invalid weekly schedule");
        schedule = input.schedule as Schedule;
        if (
          schedule.some(
            (s) =>
              !Number.isInteger(s.day) ||
              s.day < 0 ||
              s.day > 6 ||
              !/^([01]\d|2[0-3]):(00|30)$/.test(s.start) ||
              !/^([01]\d|2[0-3]):(00|30)$/.test(s.end) ||
              s.start >= s.end,
          ) ||
          new Set(schedule.map((s) => s.day)).size !== schedule.length
        )
          fail("Use one 30-minute-aligned schedule per day");
        const opening = scheduleFromFacts(b);
        if (
          schedule.some(
            (s) =>
              !opening.some(
                (h) => h.day === s.day && s.start >= h.start && s.end <= h.end,
              ),
          )
        )
          fail("Doctor hours must stay within the clinic demo opening hours");
      }
      const start = str(input.start),
        end = str(input.end),
        remove = str(input.remove);
      if (
        !schedule &&
        !remove &&
        (!Number.isFinite(Date.parse(start)) ||
          !Number.isFinite(Date.parse(end)))
      )
        fail("Choose a valid unavailable period");
      if (remove && !uuid(remove)) fail("Invalid unavailable period");
      await rpc("demo_change_schedule", {
        p_slug: b.slug,
        p_doctor: str(input.doctorId),
        p_schedule: schedule,
        p_start: start || null,
        p_end: end || null,
        p_reason: str(input.reason) || "Unavailable",
        p_remove: remove || null,
      });
    } else if (action === "record") {
      if (role !== "doctor")
        fail("Use the doctor workspace to edit clinical records");
      const doctorId = str(input.doctorId);
      if (
        !(
          await rest<Doctor>(
            "GET",
            `demo_doctors?${scoped}&id=eq.${encodeURIComponent(doctorId)}&limit=1`,
          )
        )[0]
      )
        fail("Unknown doctor");
      const data = input.data as RecordData;
      if (
        !data ||
        typeof data !== "object" ||
        !str(data.title) ||
        typeof data.notes !== "string" ||
        data.notes.length > 5000 ||
        ![data.diagnoses, data.prescriptions, data.tests].every(Array.isArray)
      )
        fail("Incomplete clinical record");
      if (
        data.diagnoses.length > 20 ||
        data.prescriptions.length > 20 ||
        data.tests.length > 30 ||
        data.diagnoses.some((x) => typeof x !== "string" || x.length > 1000) ||
        data.prescriptions.some(
          (x) => typeof x !== "string" || x.length > 1000,
        ) ||
        data.tests.some(
          (x) =>
            !x ||
            [x.name, x.value, x.unit, x.range].some(
              (v) => typeof v !== "string" || v.length > 300,
            ),
        )
      )
        fail("Invalid record fields");
      if (
        !data.vitals ||
        ["systolic", "diastolic", "heart_rate", "temperature", "oxygen"].some(
          (k) => {
            const n = data.vitals[k as keyof typeof data.vitals];
            return (
              n !== null &&
              (typeof n !== "number" ||
                !Number.isFinite(n) ||
                n < 0 ||
                n > 1000)
            );
          },
        )
      )
        fail("Invalid vital readings");
      if (data.follow_up && !/^\d{4}-\d{2}-\d{2}$/.test(data.follow_up))
        fail("Invalid follow-up date");
      const appointmentId = str(input.appointmentId);
      if (appointmentId) {
        if (!uuid(appointmentId)) fail("Invalid appointment");
        const a = (
          await rest<Appointment>(
            "GET",
            `demo_appointments?${scoped}&id=eq.${appointmentId}&patient_id=eq.${patientId}&doctor_id=eq.${encodeURIComponent(doctorId)}&limit=1`,
          )
        )[0];
        if (!a)
          fail(
            "Record and appointment must belong to the same patient and doctor",
          );
      }
      const id = str(input.id);
      const patch = {
        slug: b.slug,
        patient_id: patientId,
        doctor_id: doctorId,
        appointment_id: appointmentId || null,
        visit_at: str(input.visitAt) || new Date().toISOString(),
        published: input.published === true,
        data,
        updated_at: new Date().toISOString(),
      };
      if (!Number.isFinite(Date.parse(patch.visit_at)))
        fail("Invalid visit date");
      if (id) {
        if (!uuid(id)) fail("Invalid record");
        const old = (
          await rest<ClinicalRecord>(
            "GET",
            `demo_clinical_records?${scoped}&id=eq.${id}&patient_id=eq.${patientId}&doctor_id=eq.${encodeURIComponent(doctorId)}&limit=1`,
          )
        )[0];
        if (!old) return response({ error: "Not found" }, 404);
        if (old.published)
          fail("Published records are final. Create a new visit record");
        result = (
          await rest(
            "PATCH",
            `demo_clinical_records?${scoped}&id=eq.${id}&published=eq.false`,
            patch,
            "return=representation",
          )
        )[0];
      } else
        result = (
          await rest(
            "POST",
            "demo_clinical_records",
            patch,
            "return=representation",
          )
        )[0];
      if (patch.published)
        await logEvent(b.slug, "record_published", { patient_id: patientId });
    } else if (action === "conversation") {
      staff();
      const id = str(input.id);
      if (!uuid(id)) fail("Invalid conversation");
      const c = (
        await rest<Conversation>(
          "GET",
          `demo_conversations?${scoped}&id=eq.${id}&limit=1`,
        )
      )[0];
      if (!c) return response({ error: "Not found" }, 404);
      const text = str(input.text, 2000);
      if (text) {
        if (!c.staff_mode) fail("Take over this conversation before replying");
        await rest(
          "POST",
          "demo_messages",
          {
            conversation_id: id,
            role: "business",
            content: text,
            source: "staff",
            latency_ms: null,
          },
          "return=minimal",
        );
      }
      const patch: Record<string, unknown> = {
        last_at: new Date().toISOString(),
      };
      if (typeof input.staffMode === "boolean") {
        patch.staff_mode = input.staffMode;
        patch.handoff = input.staffMode;
      }
      if (input.assignedTo !== undefined)
        patch.assigned_to = str(input.assignedTo, 80) || null;
      await rest(
        "PATCH",
        `demo_conversations?${scoped}&id=eq.${id}`,
        patch,
        "return=minimal",
      );
    } else if (action === "reminder") {
      staff();
      await logEvent(
        b.slug,
        input.followUp === true ? "simulated_follow_up" : "simulated_reminder",
        { patient_id: patientId, simulated: true },
      );
    } else if (action === "profile") {
      const name = str(input.name, 80);
      if (!name) fail("Enter a fictional patient name");
      await rest(
        "PATCH",
        `demo_patients?${scoped}&id=eq.${patientId}`,
        { name },
        "return=minimal",
      );
    } else fail("Unknown clinic action");
    return response({ result });
  } catch (e) {
    return error(e);
  }
}

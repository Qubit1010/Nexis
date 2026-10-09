import { test } from "node:test";
import assert from "node:assert/strict";
import {
  availableSlots,
  localDate,
  dayAfter,
  type Doctor,
  type Appointment,
  type Block,
} from "../src/lib/healthcare-types.ts";
const doctor: Doctor = {
  id: "doctor-1",
  slug: "test",
  name: "Sample doctor",
  specialty: "General medicine",
  bio: "Sample",
  modes: ["in_person"],
  schedule: [{ day: 5, start: "09:00", end: "11:00" }],
  active: true,
};
const now = new Date("2026-10-02T03:00:00Z"),
  expires = "2026-10-15T00:00:00Z";
const slots = (apps: Appointment[] = [], blocks: Block[] = []) =>
  availableSlots(doctor, "2026-10-02", apps, blocks, expires, now);
test("Pakistan date changes five hours ahead of UTC", () =>
  assert.equal(localDate("2026-10-01T20:00:00Z"), "2026-10-02"));
test("calendar day arithmetic survives month boundaries", () =>
  assert.equal(dayAfter("2026-10-31"), "2026-11-01"));
test("availability uses local working hours and 30-minute intervals", () =>
  assert.deepEqual(slots(), [
    "2026-10-02T04:00:00.000Z",
    "2026-10-02T04:30:00.000Z",
    "2026-10-02T05:00:00.000Z",
    "2026-10-02T05:30:00.000Z",
  ]));
test("a conflicting reservation is excluded but a cancelled booking frees its slot", () => {
  const a = {
    doctor_id: doctor.id,
    starts_at: "2026-10-02T04:00:00Z",
    status: "confirmed",
  } as Appointment;
  assert.equal(slots([a]).length, 3);
  assert.equal(slots([{ ...a, status: "cancelled" }]).length, 4);
});
test("another doctor's booking does not remove this doctor's time", () =>
  assert.equal(
    slots([
      {
        doctor_id: "another",
        starts_at: "2026-10-02T04:00:00Z",
        status: "confirmed",
      } as Appointment,
    ]).length,
    4,
  ));
test("blocked periods exclude every overlapping slot", () => {
  const b = {
    doctor_id: doctor.id,
    active: true,
    starts_at: "2026-10-02T04:15:00Z",
    ends_at: "2026-10-02T05:00:00Z",
  } as Block;
  assert.deepEqual(slots([], [b]), [
    "2026-10-02T05:00:00.000Z",
    "2026-10-02T05:30:00.000Z",
  ]);
});
test("only future slots that finish before expiry are offered", () =>
  assert.deepEqual(
    availableSlots(
      doctor,
      "2026-10-02",
      [],
      [],
      "2026-10-02T05:30:00Z",
      new Date("2026-10-02T04:00:00Z"),
    ),
    ["2026-10-02T04:30:00.000Z", "2026-10-02T05:00:00.000Z"],
  ));
test("closed days and days outside the 14-day horizon offer no slots", () => {
  assert.deepEqual(
    availableSlots(doctor, "2026-10-03", [], [], expires, now),
    [],
  );
  assert.deepEqual(
    availableSlots(doctor, "2026-10-16", [], [], "2026-11-01T00:00:00Z", now),
    [],
  );
});
test("inactive doctors cannot offer appointments", () =>
  assert.deepEqual(
    availableSlots(
      { ...doctor, active: false },
      "2026-10-02",
      [],
      [],
      expires,
      now,
    ),
    [],
  ));

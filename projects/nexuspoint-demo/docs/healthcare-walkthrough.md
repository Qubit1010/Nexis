# Connected clinic walkthrough

All doctors, schedules and clinical records are fictional samples. Bookings, staff replies and record
publication persist in the demo database. There is no live telemedicine or outbound messaging service.
Demo role switching is for sales presentations; it is not authentication for real medical records.

## Five-minute owner demonstration

1. Open the prospect hub and start with the Google review findings. For Saleem, connect waiting-area
   crowding to scheduled arrivals and the reception queue. Do not imply the demo fixes clinical quality.
2. Open **Patient portal**. Choose a fictional patient name using the avatar. Show the latest visit,
   allergies, vital readings and follow-up summary. Recorded values are not an AI health score.
3. In **Messages**, ask to book an appointment. Select a sample doctor, consultation mode and stored
   slot. The confirmation appears only after the database reserves it. Alternatively use **Find a doctor**.
4. Switch to **Admin / reception**. Show the booking in the calendar and inbox. Select **Take over chat**,
   send a sample reply, and switch to the patient view to see it arrive in the original conversation.
5. In the reception overview, check in a booking for today and show its queue token. For future visits,
   explain that check-in opens on the appointment day. Rescheduling and cancellations update availability.
6. Switch to **Doctor view**, choose the appointment's consultant and start the sample consultation.
   Phone/video bookings have a simulated waiting room and call screen. The controls use no devices.
7. Create a fictional visit note from the appointment, save a draft, then publish it. Drafts stay in staff
   views; publishing makes the diagnoses, notes, prescriptions and test results visible to that patient.
8. Switch back to **Patient view**, open **Health records**, then **View report** and **Print / save PDF**.
9. Finish with the operational outcome: one appointment and one linked record across patient, reception
   and doctor workflows. Reminders are previews and simulated events, never messages to real people.

## Preparation and reset

- Choose only fictional data. Each browser visitor gets a linked sample patient; the clinic staff views
  share the same business calendar. A second phone has its own patient and conversation.
- The first request seeds specialty-appropriate doctors, sample patients and reports. Schedules follow
  parseable listing hours; unknown hours use explicitly illustrative Monday–Saturday, 9 am–4 pm.
- All appointment times use Asia/Karachi. Slots last 30 minutes, finish before demo expiry and fall
  within a 14-day booking window. Sunday is closed in the Saleem sample schedule.
- After a meeting, run `python scripts/reset_demo.py <slug>`. Healthcare data and conversation transcripts
  are saved in `demo_healthcare_archives` before the live walkthrough is cleared. Outreach events remain.
- Aleem's `/admin` control room is separate from each prospect's `/d/<slug>/clinic` operations panel.

## Validation

`npm test` covers assistant rules and timezone/availability behavior. `python tests/healthcare_eval.py
http://localhost:4400 --ui` checks the connected API and browser layouts in an isolated fictional clinic,
then archives that test activity. It never resets a real prospect.

For a protected Vercel preview, run `python tests/healthcare_eval.py <preview-url> --vercel` from the
linked demo project. This uses the signed-in Vercel CLI. `--ui-only` runs the focused browser walkthrough.

Release checks on 2 October 2026 passed: 25 unit tests, 55 preview API integration checks and 27 focused
browser checks. Additional checks covered keyboard focus and connection recovery, dental examples,
cross-business record isolation, reset archives and food/education regression. Both English and Urdu
landing-page previews passed, with published pricing amounts unchanged. Next.js production compilation
and TypeScript checks succeeded.

Real patient use requires a separate rollout with verified doctors and schedules, identity and staff
access controls, private records, live integrations and operational procedures.

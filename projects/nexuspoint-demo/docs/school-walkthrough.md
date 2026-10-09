# Campusflow education outreach walkthrough

Use the three workspace links in an education prospect's private report. They share the prospect
token, expiry and this browser's persistent demo-family visitor ID. The college preview uses
illustrative FSc classes; school prospects use sample school classes. None are verified operational
records for the named business.

## Meeting flow

1. Open the parent portal. Switch between the two linked fictional children. Show recorded
   attendance, published homework, results, fees and printable reports. Unrecorded dates and marks
   remain unknown, rather than being treated as absences or zeroes.
2. In the teacher workspace, choose the child's sample class teacher. Record today's attendance.
   Save a homework draft and show that parents cannot see it. Explicitly publish it.
3. Return to the parent portal. Submit a fictional homework response. Review it as the teacher,
   then show the feedback in the parent portal.
4. Create an assessment with a few recorded marks. Leave missing marks blank. Save the draft,
   then explicitly publish it. Print the student's report card and choose Save as PDF.
5. Submit a simulated fee payment reference. The invoice stays unpaid until the office verifies
   the reference. Show the pending review in the office, verify it and print the sample receipt
   from the parent portal. Rejected references can be submitted again with a new retry identifier.
6. Ask the assistant for sample fees, attendance or results. It offers only this family's linked
   children and answers from stored records. It never verifies payment from a chat claim.
7. Start an admissions enquiry in chat, supply a fictional applicant name and choose a programme.
   Book an available campus slot, confirm it and show the enquiry and visit in the office.
8. Show day/week office calendars, rescheduling, cancellation, arrival and completion. Block an
   available interval; an interval with a confirmed visit must first be cleared by rescheduling.
9. Submit a leave request as the parent and review it as the office. Leave approval does not
   automatically invent an attendance record.
10. Publish an announcement. In the office inbox, assign a conversation and take over.
    Assistant replies pause until staff return the conversation to automation. Both sides retain
    the transcript after refresh.

## Boundaries

Students, teachers, fees, classes, marks, admissions decisions and office availability are synthetic.
Role switching is a meeting tool, not real student or staff authentication. Payments, notices and
reminders are simulated. No money or outbound messages move. Public landing pages describe the
workflow without private prospect links; published agency package prices stay unchanged.

## Architecture

- Additive school tables and a service-role-only RPC in sql/school_schema.sql. RLS is enabled with
  no public policies. Server APIs validate prospect token, expiry, sector and visitor on every call.
- Families are unique per business and visitor. Parent reads and writes are scoped to linked
  children. Teacher reads and mutations are scoped to the selected illustrative teacher's classes.
  Grades are filtered server-side before the parent response is returned.
- Each mutation takes a business advisory transaction lock. Campus visit ranges have a database
  exclusion constraint; timetable class and teacher ranges have separate overlap constraints.
  Rescheduling is atomic. Cancellation releases capacity.
- Retry identifiers preserve the original result and reject changed payloads or different
  visitors, roles or actions. The pending payment index prevents concurrent duplicate claims.
- Homework, assessments and notices save as drafts. Publication is an explicit action. Editing
  published content returns it to draft. Only published academic records appear to parents.
- Campus visits use 30-minute slots over the next 14 PKT dates and finish before preview expiry.
  The college seed preserves a morning/afternoon split with a lunch gap.
- Active workspaces poll every two seconds while visible, with overlapping refreshes suppressed.
  Forms retain their contents on errors; error states offer retry.
- Reset archives education tables, conversation state and transcripts before clearing active
  walkthrough data. Outreach analytics stay intact. The next visit reseeds synthetic examples.

## Validation

Run npm test, npx tsc --noEmit and npm run build. The additional suites are:

- python tests/school_eval.py http://localhost:4400
- python tests/school_browser.py http://localhost:4400
- python tests/school_eval.py PREVIEW_URL --vercel
- python tests/school_smoke.py https://nexuspoint-demo.vercel.app

Integration fixtures are isolated from real prospect activity and archived afterwards. Browser
checks cover teacher publication, homework feedback, fee verification, campus visits, printable
reports, keyboard modal controls, connection errors, desktop layouts, both themes and Urdu RTL.
Healthcare and restaurant regression suites verify the shared assistant still works.

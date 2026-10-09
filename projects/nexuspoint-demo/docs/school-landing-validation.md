# School landing validation, 2026-10-02

## Local verification

- 35 assistant, healthcare, restaurant and school unit tests passed.
- TypeScript `npx tsc --noEmit` and the Next production build passed.
- 34 school landing checks passed: token and sector isolation, expiry before
  seeding, scoped class IDs, no student/academic/fee payload or credentials,
  parent/admissions/visit entries, safe Maps links, Urdu and iframe navigation,
  edited stored classes, independent academy reuse, empty classes and missing facts.
- 26 healthcare landing checks and 31 restaurant landing checks passed, including
  existing customer, restaurant, kitchen and sector report routes.
- Browser validation covered 1440px desktop and 390px mobile, both themes,
  English/Urdu RTL, program category filtering, empty search, keyboard program
  details and FAQ, mobile menu with Escape, image loading and no horizontal overflow.
- Selecting the second college program opened the enquiry form with the correct
  class preselected. An unknown program ID produced only this school's class
  options. Closing the form kept it closed through active polling.
- Campus visit entry opened the existing 30-minute PKT planner with stored split
  session times. Confirmation stayed disabled until a slot was selected. Closing
  the planner kept it closed through polling. Navigation did not submit a visit.
- The report's mobile iframe measured 390px. Its visit CTA navigated the parent
  frame to the parent portal and opened the planner. No recursive nested workspace.
- Browser console had no landing errors during local validation.

QA fixtures are retained expired. Existing real prospect data was not reset.
Standard synthetic families are created by school seeding; the landing does not
create or link a visitor family. Families are linked only inside the existing
parent portal or assistant. No real application, payment or outbound message occurred.

## Release verification

Preview: https://nexuspoint-demo-ibnswd9x7-qubit1010s-projects.vercel.app
Deployment: dpl_FS6UacRbcFztZFuK6EFbd7sroh4C

The preview uses the existing Vercel protection. HTML and route checks run through
the authenticated CLI with `--vercel`. Browser interaction checks ran locally;
the released page is also checked in the browser after production deployment.

All 34 school, 26 healthcare and 31 restaurant landing checks passed on the protected preview.

Production: https://nexuspoint-demo.vercel.app
Deployment: dpl_FGthRwsTqPjiSJUQrBVoqBDirNLD

- All 34 school landing checks passed against the production alias.
- Production smoke checks passed for the Saleem clinic landing, Usmania restaurant
  landing and Tameer-E-Nau report with the new school website preview.
- Live browser verification confirmed the campus visit link opens the parent
  portal's PKT planner, including its split-session availability and disabled
  confirmation before a time is selected. No visit was submitted.
- The released 1440px English light layout and 390px Urdu dark layout loaded both
  images and had no horizontal overflow. Mobile headings, links, buttons and
  fields had no clipped bounds. No browser console errors were recorded.
- Screenshots: `tests/qa/school-landing-hero.jpg` and
  `tests/qa/school-landing-mobile-urdu.jpg`. The browser was restored to English,
  light theme and the default viewport after testing.

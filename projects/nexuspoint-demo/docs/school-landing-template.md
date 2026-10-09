# School and academy landing template

Education prospects share one reusable landing page at `/d/<slug>/website?t=<token>`.
This is one page, with section anchors. It connects to the existing Campusflow demo
instead of creating a separate website or a second admissions service.

The school report's Website section embeds this page and offers desktop/mobile
preview sizes and a full-page link. Add `lang=ur` for Urdu and `embed=1` for an iframe.
Embedded workflow links navigate the parent frame; section links stay inside the page.

## Design

Blue, ivory and warm orange, clear academic typography, an illustrated crest,
rounded learning photography, searchable program cards with expandable details,
learning features, an interactive parent portal preview, admissions steps,
researched Google review excerpts, campus directions and listed hours, FAQs and a
closing enquiry CTA. Light and dark palettes have independent tokens.
Mobile navigation, keyboard disclosure controls, skip link, visible focus states,
Urdu RTL and reduced motion preferences are supported.

Design research used [Krisnandika's private school landing page](https://dribbble.com/shots/26129565-private-school-landing-page-design)
for approachable typography and photography and [Nebula Onspace's High School Portal](https://dribbble.com/shots/22119684-High-School-Portal-Landing-Page)
for the academic section hierarchy and a clear first step. The implementation and
assets are original, with no copied school branding, partner logos or claimed metrics.
See [school-imagery.md](school-imagery.md) for the generated asset provenance and prompts.

## Business data and privacy

- Name, institution category, address, listed hours, rating and review count come
  from the stored prospect profile. Missing address, hours and reviews get explicit states.
- Category adapts the institution label for colleges, academies and schools.
- Programs come from this business's stored sample class directory, selecting only
  `id,name`. They are explicitly illustrative, not verified real course offerings.
- Program search is local to that scoped directory. Categories are derived from its
  names. Empty and unavailable directories offer an office handoff without invented classes.
- Review cards contain actual researched excerpts, labeled as reviewer opinions.
  The page does not invent pass rates, accreditation, rankings, staff credentials or fees.
- The route checks the prospect token, sector and expiry before seeding or querying.
  It never loads a family's students, assessment marks, attendance, invoices or drafts.
- School initialization may create the standard fictional sample seed. Rendering
  this page does not link a web visitor to a family or submit an enquiry or visit.
- External links use safe HTTPS Google Maps URLs with `noopener noreferrer` and the
  page uses `no-referrer`. A malformed stored URL falls back to an encoded Maps search.
- Shared private preview `noindex,nofollow`, server-only credentials and website view
  events are preserved. Embedded loads do not double count `website_view`.

## Connected walkthrough

1. Open a school's report, then Website. Try both preview widths or open the full page.
2. Filter/search programs, expand a program and select **Enquire about this program**.
   The parent portal opens Admissions with a sample enquiry form and the matching
   business-owned class preselected. Use fictional information and submit to the office.
3. **Plan a campus visit** opens the existing availability planner. It uses the same
   atomic, idempotent reservation service as chat and the office, including PKT,
   split hours, 30-minute slots, 14-day horizon and expiry. No booking happens on navigation.
4. Close either form. Refresh polling does not reopen it. A fresh navigation/reload
   with the entry query opens it once again. Unknown or foreign program IDs never
   populate a class from another institution; the select contains this school's classes.
5. Open Homework, Results, Fees or Timetable from the landing preview cards. These
   enter the correct parent portal section using the same persistent visitor family.
6. In the school office, show the submitted enquiry or reserved visit. Continue the
   existing [Campusflow walkthrough](school-walkthrough.md).

Entry query parameters are restricted to parent mode: `visit=1` opens the visit planner,
`enquire=1` opens the enquiry form, and `program=<class-id>` optionally preselects a
validated class. If both actions are supplied, the visit planner takes precedence.
These are UI entry hints, not admission approval, payment or authentication.

## Validation

Run `npm test`, `npx tsc --noEmit`, `npm run build` and
`python tests/school_landing_checks.py <base-url>`. Add `--vercel` for a protected
Vercel preview. Regression suites: `tests/landing_checks.py` and
`tests/restaurant_landing_checks.py`. QA profiles are isolated and retained expired.
Browser checks use the Codex browser, covering desktop/mobile, EN/Urdu, both themes,
keyboard navigation, program preselection, close persistence and iframe handoff.

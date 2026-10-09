# Healthcare landing page template

Open **Your website** in a healthcare prospect's report. The embedded preview can
switch between desktop and mobile widths. **Open full preview** opens the same
single-page template at `/d/<slug>/website?t=<prospect-token>`.

This is one landing page for clinic, hospital and dental outreach. Navigation
scrolls to sections. Patient functions remain in the existing connected demo.

## Design and content

- Photo hero, editorial headings, teal/ivory palette, dark theme and Urdu RTL.
- Clinic introduction, sample services, patient portal preview, consultant cards,
  visit process, selected researched review excerpts, location, hours, FAQ and CTA.
- Business name, address, neighborhood, accessibility details, hours, Google
  rating and review count come from the stored researched profile.
- General and dental copy use the same layout. Sample services come from
  `profile.services_sample`. Consultant cards use active business-scoped
  `demo_doctors`, with no patient or clinical record query.
- Hero image is AI-generated illustrative photography. Consultant artwork is
  illustrative SVG, never presented as staff photography. There are no invented
  credentials, awards, treatment claims, statistics or reviewer identities.
- Missing ratings, reviews and accessibility details are omitted. Missing hours,
  address, services or consultant data show clear alternatives.
- Listing details are dated using the prospect creation date. Quotes are
  verbatim selected excerpts from the stored research, with a link to all reviews.

## Connected actions

- Booking buttons open the existing booking dialog in patient appointments.
- Each consultant's availability action opens the existing booking dialog with
  that consultant selected. The patient workspace checks the ID against its own
  active doctors before opening. Reservation rules are unchanged.
- Assistant buttons use the existing web chat and visitor history.
- Record and message links open their patient portal tabs.
- Directions open the prospect's Google Maps listing.
- English/Urdu links preserve the prospect token and selected language. Theme is
  stored separately as `np-website-theme`, defaulting to light.

## Access and analytics

The route checks business existence, prospect token, sector and expiry before
loading consultant data or seeding. Credentials stay server-side. Invalid
tokens and unsupported sectors return 404. Valid food prospects now use the
restaurant template on the same route; education prospects use the school and
academy template. Expired links show only the expiry message.
The page inherits noindex/nofollow and adds no-referrer. Embedded outbound
workspace actions navigate the parent frame. Full previews record
`website_view`; embedded views do not inflate that event.

## Walkthrough

1. Open a healthcare report, go to **Your website**, try both preview widths.
2. Open the full preview and navigate its sections.
3. Open a consultant's availability. The booking dialog selects the same doctor.
4. Close the dialog, return to the landing page and try records or the assistant.
5. Change language and theme; review the mobile menu and expandable FAQ.
6. Open a dental prospect. Names, hours, services, rating and consultants change
   while the layout stays the same.

Validation: `npm test`, `npx tsc --noEmit`, `npm run build`,
`python tests/landing_checks.py <base-url>` (add `--vercel` for protected previews).
Browser checks cover responsive layouts, theme contrast, Urdu, section links,
mobile navigation, FAQ keyboard operation, doctor preselection and hub iframe.

This outreach release remains a private template. Real clinic services,
credentials, staff photos and contact details are confirmed before public use.

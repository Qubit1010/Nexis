# Restaurant landing validation, 2026-10-02

Released to the existing `nexuspoint-demo.vercel.app` domain.

- Preview: `nexuspoint-demo-bal3qptrv-qubit1010s-projects.vercel.app`,
  deployment `dpl_Di4ZVgQtLhMZcoQMtKrKLz2cu8wa`.
- Production: `nexuspoint-demo-fvq6t8usx-qubit1010s-projects.vercel.app`,
  deployment `dpl_2KSUhben6aq61uENjatDTnZduMHZ`.
- Local TypeScript and production build passed. Preview and production cloud
  builds also passed.
- 35 assistant/healthcare/restaurant/school unit checks passed.
- 31 restaurant landing checks passed locally, on the protected preview
  through Vercel CLI authentication, and on the live domain.
- 26 healthcare landing/regression checks passed on all three targets.
- Isolated QA profiles and their activity are retained and expired. Existing
  prospect orders, reservations and records were not reset.

Browser checks used the Codex in-app browser. Local checks covered desktop,
390px mobile, light/dark, English/Urdu RTL, category filters, search, no matches,
show all dishes, section navigation, mobile navigation, keyboard FAQ,
accessible control names, image loading and horizontal overflow.

The report iframe measured 1094px in desktop preview and 390px in mobile
preview. Its reservation link navigated the parent frame into the guest booking
dialog. Closing the dialog stayed closed after further refreshes. A dish link
filtered the ordering workspace to the same stored menu item with an empty
basket.

Live browser smoke checks confirmed dish preselection, reservation entry and
closing, image loading, mobile Urdu/dark mode, no horizontal overflow and no
browser console errors. Dark hero CTA contrast measured 10.03:1 for the
primary action and 15.41:1 for the outlined action.

Screenshots are local ignored QA artifacts:

- `tests/qa/restaurant-landing-hero.jpg`, live desktop 1440 × 1000.
- `tests/qa/restaurant-landing-mobile-urdu.jpg`, live mobile Urdu/dark 390 × 844.

Protected preview browser access remained behind Vercel protection; its
deployed content and access rules were checked through authenticated HTTP.
Visual and interaction checks ran locally and on the live release. Calls,
payments, orders, delivery and table service remain simulated demo workflows.

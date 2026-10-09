# Restaurant landing page template

Open **Your website** in a food prospect's report. Desktop/mobile preview and
**Open full preview** use the same private route:
`/d/<slug>/website?t=<prospect-token>`.

This is one reusable landing page. Its navigation scrolls to sections; orders,
tables, messages and receipts stay in the existing Tableflow workspaces.

## Design and content

- Cream, charcoal, olive and saffron, editorial serif headings, original food
  photography, dark mode and English/Urdu with RTL.
- Food hero, searchable category menu, sharing section, ordering/reservation/
  assistant choices, researched review excerpts, address, hours, FAQ and CTA.
- Business name, neighborhood, address, hours, Google rating and review count
  come from the stored prospect profile. Reviews are selected original excerpts,
  linked to the listing and dated with the listing snapshot.
- The menu comes from business-scoped `demo_menu_items`, including stored
  prices and sold-out states. Fictional menu, prices, servings and photography
  are labeled. There are no invented awards, staff identities or discounts.
- Missing review data is omitted or linked to the listing. Missing hours,
  empty menu and a failed menu fetch have explicit states. No fallback menu is
  invented when a previously seeded menu is empty or unavailable.
- Images are illustrative, not the restaurant's actual dishes or venue.
  They live in `public/restaurant/`. See `restaurant-imagery.md`.

## Connected actions

- Book a table opens the existing guest reservation dialog via
  `/customer?tab=reservations&reserve=1`. The dialog opens once after its scoped
  state loads; closing it does not reopen it on two-second polling.
- Choose a dish opens the ordering menu with `item=<stored-menu-id>`. The menu
  validates this ID against its own business menu and filters to the matching
  dish. It does not add anything to a basket or submit an order automatically.
  Unknown or another business's IDs are ignored.
- Ordering, prices at checkout, reservations, capacity, atomic collision
  protection and retry identifiers use the existing service.
- Assistant links open guest messages with the same browser visitor identity.
  Staff takeover and persisted history remain shared.
- Directions use the prospect's Google Maps listing. The visual map on the
  page is decorative and explicitly identified as an illustration.
- All workspace links preserve business token and language. In the embedded
  preview they navigate the parent frame. Maps links use no referrer.
- Theme preference is `np-website-theme`, shared with the healthcare template.
  Its colors are isolated from the outreach report and restaurant workspaces.

## Access and analytics

The website route allows healthcare and food businesses and validates token and
expiry before loading sector data or seeding. Only the fields needed by this
restaurant page are passed to its browser component. No orders, customers,
table bookings, messages or credentials are queried or sent by the page.
Education keeps its existing preview. Invalid/cross-business tokens return 404;
expired previews display the expiry notice and do not seed operating data.

The route inherits noindex/nofollow and sets no-referrer. Full previews log
`website_view`; embedded previews do not add this event. Existing outreach
analytics and public prices are preserved.

## Walkthrough and validation

1. Open Usmania's report and **Your website**, then try desktop/mobile widths.
2. Open the full page; explore categories, search, show all dishes and FAQ.
3. Choose a dish and verify the guest menu filters to it. Add items and use the
   existing sample checkout if demonstrating the kitchen workflow.
4. Return and book a table. Select party/date/time using stored availability.
   Close the form and verify it stays closed while the workspace refreshes.
5. Open the assistant, directions and order history.
6. Check mobile, English/Urdu and both themes.

Checks:

```sh
npm test
npx tsc --noEmit
npm run build
python tests/restaurant_landing_checks.py <base-url>
python tests/landing_checks.py <base-url>
```

Append `--vercel` to either Python command for a protected preview. The food
checks use isolated, retained QA profiles for missing data, changed price,
sold-out items, empty menu, business isolation and expiry. Existing prospects
are never reset. Browser validation covers desktop/mobile, filtering, search,
keyboard FAQ, themes, RTL, preview widths, dish selection and reservation entry.

Real menus, prices, delivery terms, contact details and photography are approved
by each restaurant before public use. This release remains a private outreach
landing template with simulated operating workflows.

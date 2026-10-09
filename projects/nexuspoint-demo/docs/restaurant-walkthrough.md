# Restaurant outreach walkthrough

Tableflow extends each food prospect's existing private review report. Open the workspace cards from that report. All routes require its token and expiry:

- /d/[slug]/customer: menu, saved basket, pickup/delivery/dine-in checkout, order history and printable receipts, table bookings, assistant messages.
- /d/[slug]/restaurant: live orders, tables, reservations and waitlist, conversation takeover, guests, sample prices/availability and settings.
- /d/[slug]/kitchen: accepted, preparing and ready tickets, elapsed time, quantities, spice preferences and notes.

The owner's /admin remains separate. Role switching is for fictional outreach presentations. It is not real staff or customer authentication.

## Ten-minute meeting

1. Start with the prospect's Google Maps review report. Connect slow service and order accuracy findings to the workflow. Do not claim the software alone fixes food safety or staffing.
2. Open Customer, choose Menu, add karahi and naan. Adjust quantities, spice preference and fictional notes. Review pickup/delivery/dine-in checkout. Explain that prices are synthetic.
3. Place a sample order. View its receipt and use Print / save PDF. Switch to Manager. The same ticket number, items and total appear. Accept it.
4. Switch to Kitchen. Start preparing, then mark ready. Return to Manager to complete pickup, or mark delivery out for delivery and then complete. Record a simulated payment.
5. Return to Customer orders to see the status. Old receipts retain their prices when the manager changes menu prices.
6. Reserve a table for a family. Show it in Manager reservations and the table board. Reschedule, seat guests on the same PKT day, then complete and release the table. Blocking a booked table or changing conflicting hours is refused.
7. Open Customer messages and request the sample menu. Select dishes, pickup and confirmation. The shared service persists a demo order. Request a table and confirm a suggested slot.
8. In Manager inbox, assign Front desk, take over and send a staff reply. Further customer messages receive no automated response until Return to assistant is selected.
9. Mark a dish sold out or pause intake. Checkout refuses unavailable orders while existing tickets stay visible. Add a waiting party and simulate a notification.
10. Tie the demonstration to the agency bundle in the original report. Agency prices have not changed.

## Defaults and boundaries

- Business-scoped persistent Supabase data; credentials stay server-side. APIs check token, expiry and ownership on every read/write.
- Orders use server-calculated prices, immutable line snapshots, atomic transitions and retry identifiers. Uncertain requests can be retried with the same payload.
- Table reservations last 90 minutes, start every 30 minutes over 14 PKT days, and end before expiry. Illustrative daily hours default to noon through midnight. Database exclusion constraints and a business lock prevent overlaps. Rescheduling and cancellation release capacity atomically.
- Visible views poll every two seconds. The visitor ID and basket persist locally; conversations, orders and reservations link to the same database customer.
- All dishes, prices, ingredients, tables, guests, estimates, payments and notices are synthetic. Staff must verify real ingredients and allergen requirements.
- Real authentication, delivery integrations, payment gateways, taxes/POS/BRA certification, printers, loyalty and outbound WhatsApp remain outside this outreach release.
- Transaction replies use stored menus and table availability. Unknown requests and allergy questions go to staff. General factual questions retain the provider fallback.

## Validation and reset

Apply migrations with python scripts/setup_db.py. Run npm test, npx tsc --noEmit, npm run build, python tests/restaurant_eval.py http://localhost:4400 --ui, and python tests/restaurant_eval.py PREVIEW_URL --vercel.

Integration tests create isolated fictional restaurants and check retries, concurrency, price snapshots, kitchen and delivery transitions, availability, table overlaps, rescheduling, cancellation, hours, timezone, ownership, expiry, chat booking and takeover. Browser checks cover all workspace tabs, both themes, mobile Urdu RTL and modal keyboard handling.

Before a meeting, python scripts/reset_demo.py FOOD_SLUG archives operating data, conversations and messages. The next visit creates fresh samples. Outreach events are preserved. Do not reset the real prospect just for QA.

# NexusPoint Prospect Demo Kit

A private, per-prospect demo: the owner's own business, already running on NexusPoint. Live at
`https://nexuspoint-demo.vercel.app/d/<slug>?t=<token>` (unlisted, noindex, expires after 14 days).

| Surface | What it shows | Sells |
|---|---|---|
| Health score | Google listing, website, photos, rating, reply rate | Google + website |
| Review X-ray | Their last 80 reviews grouped into complaints and praise, with counts and verbatim quotes | AI + data |
| Assistant | A WhatsApp-style assistant with their facts, in Urdu, Roman Urdu or English | AI automation |
| Dashboard | Their conversations live: summaries, bookings/orders, staff hand-offs | Dashboards |
| Website | A draft site from their listing + 2 posts in Urdu and English | Web + marketing |
| Numbers | PKR ROI calculator against the Growth bundle | The close |
| Plan | Recommended bundle, pilot offer, YES button to Aleem's WhatsApp | The close |

## Make a demo

```
python projects/quetta-local-market/scripts/make_demo.py "<maps link | placeId | name>" --reset
python projects/nexuspoint-demo/scripts/snapshot.py <slug>          # offline copy
python projects/nexuspoint-demo/scripts/reset_demo.py <slug>        # clear chats before a meeting
```

Meeting script: `docs/demo-script.md`. WhatsApp number setup: `docs/whatsapp-setup.md`.

## How it works

- `make_demo.py` reads the place from the Quetta Google Maps scan and fetches the newest 80 reviews
  (Apify). An LLM groups the themes; counts, star mix and reply rate are computed from the data, and every
  quote is checked word for word against the reviews. It writes to Supabase (`demo_*` tables, Tokyo
  region) and renders the Health Check PDFs.
- The brain (`src/lib/brain.ts`) is a port of Sixty Second Responder's: facts only, one question at a
  time, prices and anything unknown go to staff, honest bot disclosure, emergencies go to Rescue 1122.
  - Provider chain: Anthropic → Claude via OpenRouter → OpenAI → a scripted sector brain, so a customer
    is never unanswered.
- Vercel functions run in Tokyo (`hnd1`) next to the database.
- Measured on production: median 3.3s, p95 4.8s per reply, 0 rule failures across 36 adversarial
  test messages (`tests/chat_eval.py`).

## Tests

Healthcare now has connected patient, reception and doctor workspaces at `/d/<slug>/patient`,
`/d/<slug>/clinic` and `/d/<slug>/doctor`, with the same prospect token. Start from the links in the hub.
Booking chat and calendars share atomic reservations; clinical drafts publish to the linked patient.
All medical data and doctors are fictional. See `docs/healthcare-walkthrough.md` for the meeting flow.

Healthcare's **Your website** section now previews a complete single-page landing template.
Open `/d/<slug>/website?t=<prospect-token>` for the full responsive page. Business details come
from the researched profile; active sample consultant cards connect to the patient booking flow.
See `docs/healthcare-landing-template.md` for reuse, access controls and the walkthrough.

Food prospects now have connected customer, manager and kitchen workspaces at `/d/<slug>/customer`,
`/d/<slug>/restaurant` and `/d/<slug>/kitchen`. Orders share server-calculated price snapshots and
atomic state changes; table reservations use database overlap protection. Menus, prices, tables,
guests, payments and notices are synthetic. See `docs/restaurant-walkthrough.md`.

Food prospects also have a complete one-page restaurant landing template in **Your website**,
at `/d/<slug>/website?t=<prospect-token>`. Its menu uses stored dishes, prices and availability;
dish links select the matching ordering item and booking links open the existing table form.
See `docs/restaurant-landing-template.md` for reuse and `docs/restaurant-imagery.md` for assets.
Run `python tests/restaurant_landing_checks.py <base-url>` for scoped landing checks.

Run `python tests/restaurant_eval.py http://localhost:4400 --ui` for isolated integration and browser
checks, or substitute a preview URL with `--vercel` for protected preview APIs. Restaurant resets
archive activity and preserve outreach events.

Education prospects now have connected parent, school office and teacher workspaces at
/d/<slug>/parent, /d/<slug>/school and /d/<slug>/teacher. Teachers publish homework and assessments;
parents see their linked fictional children, submit responses and request fee verification.
Admissions chat uses the same atomic campus booking calendar as the office. All academic data,
fees and payments are synthetic. See docs/school-walkthrough.md for the presentation flow.

Education's Website section now embeds a reusable school, college and academy landing
page at `/d/<slug>/website?t=<token>`. It reads the business profile and scoped sample
classes, with searchable programs, enquiry preselection, campus visit booking and
parent portal entry points. Supports Urdu, both themes and desktop/mobile preview.
See docs/school-landing-template.md and docs/school-imagery.md. Run
`python tests/school_landing_checks.py <base-url> [--vercel]` for access and data isolation checks.

Run python tests/school_eval.py http://localhost:4400 for transaction and privacy checks, and
python tests/school_browser.py http://localhost:4400 for the connected browser walkthrough.
Protected preview API tests accept --vercel. Education resets archive activity and retain analytics.

```
npm test                                            # assistant + healthcare + restaurant + school (35 tests)
python tests/healthcare_eval.py http://localhost:4400 --ui # isolated clinic integration + browser checks
python tests/healthcare_eval.py <preview-url> --vercel    # protected preview API checks using Vercel auth
python tests/chat_eval.py https://nexuspoint-demo.vercel.app   # live rules + latency
python tests/qa_hub.py https://nexuspoint-demo.vercel.app      # screenshots + overflow
```

## Env (Vercel production)

`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, `DEMO_BASE_URL`,
`ADMIN_TOKEN`. Add `ANTHROPIC_API_KEY` back once the account has credit. Phase 2 adds the `WHATSAPP_*`
vars.

## Public checkout setup

The approved pricing file `src/data/bundles.json` is private and excluded from Git.
For a fresh checkout, copy `src/data/bundles.example.json` to `src/data/bundles.json`
before `npm install` and `npm run build`. The example has zero prices and placeholder
terms, so configure the real private file before using a prospect demo. On the agency
checkout, `python scripts/sync_bundles.py` regenerates it from the private Quetta kit.
Prospect records, access tokens, environment variables and captured sessions remain local.

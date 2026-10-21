# Real estate outreach walkthrough

Leadline extends each property prospect's private review report. It is built for agencies, developers, builders and property managers. Open the workspace cards from that report. All routes require its token and expiry:

- /d/[slug]/buyer: sample listings, the buyer's own enquiry and its qualification, site visits (book, move, cancel), and the WhatsApp-style assistant.
- /d/[slug]/agents: the lead pipeline (new, qualified, visit booked, negotiating, won, lost) with the assistant summary, source, first-reply time and assigned agent on every card; site visits by day; conversation takeover; listing status.
- /d/[slug]/manager: where leads come from, median first reply, share answered within five minutes, visit rate, slowest replies, next visits, agent load and availability, site-visit hours.
- /d/[slug]/website: a one-page project and listings site. Its lead form writes a real lead into the same pipeline; Visit buttons open the buyer portal's booking.

Role switching is for fictional outreach presentations. It is not real staff or buyer authentication.

## Ten-minute meeting

1. Start with the review report. If replies to reviews are low, connect that to speed to lead: buyers in Dubai and the UK message at night and the first agency to answer usually gets the visit. Do not promise a sales uplift.
2. Open Buyer, then Assistant. Send "10 marla plot chahiye DHA ya Gulberg mein, budget 2.5 crore". The assistant answers in Roman Urdu and asks one missing question at a time (timeline, then whether the buyer is in Pakistan or overseas), with quick replies.
3. Once qualified it shows only stored sample listings within budget, labelled as sample demand. Pick one, pick a concrete time, confirm. The visit is saved by the database, not by the model.
4. Switch to Agent pipeline. The same buyer sits in Visit booked with the assistant summary ("Overseas buyer (UAE) wants a 10 marla plot ... Site visit ... with Bilal Ahmed"), the source and a first reply measured in seconds. Open the card: qualification grid, history, notes, reassignment and stage moves.
5. Back in the assistant ask "Is the society NOC approved?" or "Final price kya hai, discount milega?". Both go to an agent with no number in the reply. In Conversations, take over and reply as the agent; the assistant stays silent until handed back.
6. Open Your website from the report. Send the enquiry form with a sample name. Show the new Website form lead in the pipeline a few seconds later.
7. Switch to Manager view. Walk through sources and response times: phone and referral leads answered in hours, assistant and form leads in seconds. Mark an agent unavailable to show visits route to the others; an agent with booked visits cannot be switched off.
8. Close on the Growth bundle in the report. Islamabad prospects see Islamabad prices.

## Defaults and boundaries

- Business-scoped Supabase tables prefixed demo_re_ and one function, demo_re_action. Every write takes a per-business advisory lock. Site visits also carry a per-agent exclusion constraint, so two buyers can never hold the same agent at the same hour; the integration test fires four simultaneous bookings at one hour with three agents and exactly three succeed.
- Visits are one hour, on the hour, 10:00 to 18:00 PKT by default, every day for 14 days and before expiry. A slot is free while any active agent is free. Booking keeps a lead's existing agent when possible, otherwise picks the least loaded free agent. Retry identifiers make bookings and enquiries safe to resend.
- Pipeline moves are validated in the database and mirrored in src/lib/real-estate-types.ts: lost needs a reason, won is final, lost can reopen to new, and visit booked requires a confirmed visit. Cancelling the only visit returns the lead to qualified.
- The chat flow is deterministic (src/lib/real-estate-chat.ts). It parses budget in crore and lakh, society or sector, marla, kanal or square feet, timeline and overseas country in English, Roman Urdu and Urdu. It never invents a price: listings come from the stored samples and anything above 120% of the stated budget is never shown. Legal, NOC, transfer, possession, tax, discount and payment-plan questions go to an agent. Hours, directions and bot questions fall through to the shared brain with the property honesty rules; emergencies still go to Rescue 1122 first.
- Lead summaries are built only from what the buyer said. First reply is the time from the enquiry arriving to the first answer.
- Listings, prices, agents, buyers and the sample pipeline history are synthetic. Islamabad and Rawalpindi demos get DHA, Bahria, Gulberg, B-17, E-11 and Top City samples; other cities get a Quetta set. No phone line, WhatsApp number, ad account, Zameen or Facebook connection exists in this release.

## City

A demo's city comes from profile.city (written by make_demo), then a recognised Maps city, then the address, then Quetta. The assistant prompt, today's date line, sector copy ({city} in sectors.json), landing pages and footers use it. Islamabad and Rawalpindi demos read the islamabad price list in src/data/bundles.json; everything else reads quetta.

## Make, validate, reset

    python projects/islamabad-local-market/scripts/make_demo.py "<maps link | placeId | name>" [--sector real-estate] [--no-pdf]
    python scripts/setup_db.py sql/real_estate_schema.sql     # additive tables + function
    npm test                                                   # includes tests/real-estate.test.ts
    python tests/real_estate_eval.py http://localhost:4400     # 48 API, concurrency and chat-rule checks
    python scripts/reset_demo.py PROPERTY_SLUG                 # archive activity before a meeting

The eval creates an isolated fictional Islamabad office, then archives it and expires it. Do not reset a real prospect just for QA.

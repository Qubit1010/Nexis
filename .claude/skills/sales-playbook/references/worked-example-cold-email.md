# Worked Example — Cold Email to Closed Client

> A full end-to-end walkthrough of one cold-email prospect: 4-email sequence → reply → live conversation → booked call → 30-min Ops Teardown discovery call → signed contract. Uses the cold-email benchmarks and bans from `frameworks/opener-archetypes.md` + `references/what-not-to-do.md`, the live conversation flow (`scripts/live-conversation-playbook.md`), the discovery script (`scripts/discovery-call-script.md`), and real proof-bank entries (`offer/proof-bank.md` — Andrey).
>
> Companion to `worked-example-linkedin.md` and `worked-example-instagram.md`. The cold layer differs by channel; the discovery call and close are identical.
>
> **Note:** This shows the *playbook-aligned* version of the 4-email cadence. The live templates in `cold-outreach/scripts/send_sequence.py` currently drift from this (see "Flag for Aleem" at the bottom) — not yet fixed as of this writing.

---

## The Prospect

**David Okafor** — Operations Lead at **Talentbridge**, a 14-person recruiting/staffing firm (Austin). No social trigger (this is email, working from scraped firmographic + a website signal). Pain inferred from their careers page + service pages: manual candidate pipeline updates and weekly client status reports. Maps to **Andrey** (lead routing + client reporting automation).

Cold email has the lowest baseline of the three channels (**1.7% reply on generic templates**, Sopro/Mailforge), so the whole game is: specificity, named peer, sub-120 words, and a deliverable-anchored ask.

---

## STAGE 1 — The 4-Email Sequence (Day 0 / +3 / +7 / +14)

**Email 1 (Day 0) — Quick question.** Subject lowercase + curiosity. Under 120 words, named peer, no-oriented ask, no em-dash, no formal sign-off.

> **Subject:** quick question about Talentbridge
>
> David,
>
> Recruiting firms at Talentbridge's size usually hit a wall where candidate pipeline updates and weekly client reports eat a full day a week, manually.
>
> Built the fix for Andrey, an agency operator with the same scattered-tools setup. Lead routing + client reporting wired together, took 10+ hrs/week off his team.
>
> I do a free Ops Teardown for a few firms a week. I map your stack and show you the first thing I'd automate, sent as a short Loom. You keep it either way.
>
> Would it be a bad idea to send a 3-question link so I know where to look?
>
> Aleem, NexusPoint

No reply. **Email 2 (Day +3) — Proof, no ask.** Subject as a reply thread.

> **Subject:** re: Talentbridge
>
> David,
>
> Concrete example since it's relevant to where you are. The Andrey build pulled candidate and client data from four tools into one auto-generated weekly report. Friday status updates went from a half-day of copy-paste to zero.
>
> Not pitching. Figured it was worth sharing given Talentbridge's headcount.
>
> Still happy to run the same teardown if you're open to it.
>
> Aleem

**Email 3 (Day +7) — Specific signal + Loom offer.**

> **Subject:** the talentbridge careers page
>
> David,
>
> Saw you're hiring 3 recruiters right now. Adding headcount usually means the manual reporting load scales with it, not down, because every new recruiter is another pipeline to track by hand.
>
> If useful, I'll record a 5-min Loom showing exactly what I'd automate first for a firm your size. No call required to get it.
>
> Want me to send it?
>
> Aleem

David replies:

> A Loom would be useful. We are definitely feeling the reporting load. What does something like this cost?

*Price question — don't quote. Route to the live playbook. Email 4 ("should I close your file?") never fires because he replied.*

---

## STAGE 2 — The Middle Conversation (over email, live playbook)

Email tempo is slower than DMs, but the phases are identical. Reply same day.

**Phase 1 — deliver the Loom + qualify + deflect price:**

> Sending the Loom over today. On cost, it depends on what you'd actually need, which is why I don't quote blind. Quick one first: is it just the weekly client reporting that's manual, or is the candidate pipeline tracking by hand too?

> Both honestly. Recruiters update a shared sheet, I stitch it into client reports every Friday. Takes me most of the day.

**Phase 2 — label, then leave it:**

> Sounds like Friday has basically become a data-entry day instead of an ops day for you.

> Pretty much. And it gets worse every time we add a recruiter.

**Phase 3 — deepen / quantify:**

> If you had to put a number on it, how many hours a week across you and the team goes into pipeline updates plus the Friday report?

> Me, half a day. The recruiters, maybe 2-3 hours each. Call it 12-15 hours total.

> And with the 3 new hires coming, where does that land you?

> Worse. That's part of why I replied honestly.

**Phase 4 — proof reinforced (he already pulled at Email 3):**

> Right, this is the exact Andrey build. Four tools into one auto-report, 10+ hrs/week back. The Loom I just sent is a slice of it. Ports cleanly to a recruiting pipeline.

**Phase 6 — anchored call ask, two times:**

> Easier to show than type. Want a 20-min Ops Teardown? I screen-share your stack and tell you the exact first thing I'd automate, you decide if it's worth building. Tuesday 2pm or Thursday 11am Central?

> Thursday 11am.

Booked. **Send the 5-question pre-call form** with the calendar invite.

---

## STAGE 3 — The Discovery Call (same 30-min Ops Teardown)

Identical 4-Act script. The content fills in around recruiting-ops pain.

- **Act I — UFC:** same frame, price anchored "$2k to $6k depending on scope," two no-oriented questions.
- **Act II — Pain Funnel (8 questions):** surfaces the Friday report has eaten his Fridays for ~2 years, he tried a shared Airtable that recruiters stopped updating, and on cost he lands on it himself:

> between my Fridays and recruiters not selling while they do data entry, probably $6k+ a month in lost productivity

*Label:* "so every Friday this runs, it's a recruiter's worth of selling time going into spreadsheets."

- **Act III — Need-Payoff + Mistake ABC (peer-matched to Andrey):**

> the mistake I see ops leads make is they buy another tool, like the Airtable, and expect the team to change their behavior to feed it. they never do. we map how your recruiters actually work first, then automate around that so nobody has to change a habit. that's why Andrey's reporting held instead of getting abandoned like your Airtable.

*(Pre-kills "we tried Airtable and the team didn't adopt it.")*

- **Act IV — Close:** 3-step plan → double tie-down → price tied to his $6k/mo number, two tiers (DWY $2k / DFY $5,500, live in 14 days) → silence → risk reversal (14 days or don't pay; 5+ hrs/week back in 30 days or refund) → no-oriented close:

> would it be a bad idea to kick off Monday?

> No, let's do it.

---

## STAGE 4 — Same-Day Send-Through

> **Subject:** Your recruiting-ops build plan + start date

Contract + 1-page plan + both guarantees + Monday start + signature link, within 2 hours. He signs. **Closed.** → `client-onboarding-workflow`.

---

## Cold email vs DM channels — what changed

| Dimension | LinkedIn / Instagram | Cold Email (David) |
|---|---|---|
| Baseline reply rate | 24-32% (IG) / ~39% positive (LI note) | **1.7%** generic — specificity is everything |
| Trigger source | Their posts/reels | Website signal (careers page, service pages) |
| Cadence | DM 2/3/4 over ~2 wks | **4 emails: Day 0 / +3 / +7 / +14** |
| Personalization signal | Recent content | Firmographic + inferred pain, confirmed Email 3 |
| Reply tempo | Minutes (speed-to-lead critical) | Hours/same-day is fine |
| Email 4 | n/a | "should I close your file?" — no-oriented breakup (skipped here, he replied) |
| **Discovery call** | **Identical 4-Act script** | **Identical 4-Act script** |

---

## Flag for Aleem (worth fixing in the pipeline later)

The live templates in `cold-outreach/scripts/send_sequence.py` drift from the playbook:
- Email 1 opens with "It looks like" — a burned literal opener per `references/what-not-to-do.md`
- No named peer (uses generic "a 12-person company") — the single biggest lever per the proof bank
- Formal sign-off "Aleem\nNexusPoint | AI Automation & Web Systems"

Fix: rewrite the four `send_sequence.py` templates to the playbook-aligned versions above (named-peer + no-oriented asks + Andrey/Steve/Mikey merge). Not done yet — Aleem will handle when he's back to sending email.

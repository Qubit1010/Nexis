# When to Ask for the Call

**Ask by the 5th-6th prospect reply, at the latest.** This is the number the system is built
around (`ASK_BY = 6` in the dashboard's draft prompt, same rule in `live-conversation-playbook.md`
Advance Triggers) — pinned to real data, not a guess.

## The data

SetSmart's study of 828,761 DM conversations (5.6M messages, 391 businesses, Instagram +
WhatsApp, July 2024 - March 2026) is the largest public dataset on this. Booked-call rate by
conversation depth:

| Prospect replies so far | Booked-call rate |
|---|---|
| 1-2 | 0.07% |
| 2-5 | 1.67% |
| **5-10** | **11.25%** |
| 10-20 | 28.87% |
| 20+ | 34.13% (plateau) |

The inflection point sits right around 5-6 replies. Before that, asking converts at
rounding-error rates — too early, no trust built yet. Past ~20 replies the curve flattens: if
they haven't booked by then, more back-and-forth stops helping.

## Two caveats

1. **Don't wait for exchange 6 if a buying signal fires earlier.** Longer replies, a question
   back, price/timeline questions, "how does it work," a proof request — any of these should
   jump straight to the ask regardless of exchange count. Already wired into the Advance
   Triggers (`live-conversation-playbook.md`).
2. **This is DM-specific, not the whole relationship.** High-ticket deals overall ($3-10K range)
   tend to close across 5-12 touchpoints over ~3 weeks once follow-ups and re-engagement are
   counted. "Ask by 6" governs a single live conversation, not the total sales cycle.

## How this is enforced in the system

The moment either trigger fires (6 replies with no ask yet, or an earlier buying signal), the
drafted reply is forced to include the anchored Ops Teardown call ask. That's the loop-killer
behind the Supabase conversation memory + Advance Triggers build
(see [[project-sales-playbook-memory-upgrade]]).

## Source

Full citations and the rest of the ask-timing research: `references/research-synthesis.md`,
section **Q7: Buying Signals + When to Ask for the Call**.

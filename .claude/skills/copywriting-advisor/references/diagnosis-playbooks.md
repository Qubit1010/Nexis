# Diagnosis playbooks

Load this in diagnose mode. The job is to find the **root cause**, not to list everything that
could be improved. A diagnosis that returns twelve findings has not diagnosed anything.

---

## The five root causes

Almost every "our copy isn't working" traces to one of these. They are ordered by how often
they are the real answer, which is roughly the inverse of how often they get blamed.

| # | Root cause | Tell | Fix owner |
|---|---|---|---|
| 1 | **The offer is wrong** | Traffic is fine, engagement is fine, nobody buys. Competitors with worse copy convert better | `strategic-foundation` / `proposal-generator` |
| 2 | **No proof** | Every claim is an adjective. No numbers, no names, no demonstrations | `copy-conversion` Phase 6, but the client has to supply the raw material |
| 3 | **Unclear what it is** | A visitor cannot say what the company does after five seconds | `copy-conversion` build |
| 4 | **Wrong reader / message mismatch** | The ad promises one thing, the page delivers another. Bounce concentrated by source | `copy-conversion` + whoever owns the ad |
| 5 | **Voice drift** | Every page sounds like a different company. Usually several writers, no spec | `brand-voice` first, then `copy-conversion` |

**The diagnostic question that separates 1 from 2-5:** would a well-known competitor selling
the identical thing convert this traffic? If yes, it is a copy problem. If no, it is an offer
problem and no rewrite will fix it. Say so early - it is the finding clients least want and
most need.

---

## Symptom → cause → route

| Symptom | Most likely cause | Check first | Route |
|---|---|---|---|
| "Traffic but no conversions" | Offer, or message mismatch | Does traffic source match page promise? | `copy-conversion` audit; escalate to offer if clean |
| "Our copy is all features" | Missing benefit ladder — **but check construal level first**, features may be right for a near-term concrete purchase `[C]` [s41] | Purchase timeframe and concreteness | `copy-conversion` |
| "Nobody reads it" | Almost never true as stated. Attention is front-loaded, not absent `[C]` [s259] | Is the load-bearing message in the top screenful? | `copy-conversion` |
| "It sounds generic" | Specificity failure. Adjectives standing in for proof | Can any claim be falsified? | `copy-conversion` Phase 6 |
| "Every page sounds different" | No voice spec, multiple writers | Does `14-brand-voice.md` exist? | `brand-voice` |
| "Our A/B test won then stopped working" | Optional stopping / underpowered test `[C]` [s271], `[P]` [s302] | Sample size, stopping rule | Explain; do not re-test blindly |
| "Emails get opened but no clicks" | Subject writes a cheque the body does not cash. Also: open rate is unreliable post-2021 | Click-to-open, not open rate | `copy-conversion` |
| "Open rates collapsed in 2021-22" | Apple MPP changed what an open measures | When did it change, and for which clients | Explain; switch the metric |
| "Competitor's copy is better" | Usually proof and specificity, not craft | Compare proof inventories, not prose | `copy-conversion` audit |
| "Urgency stopped working" | Reactance, or the deadline was never real `[C]` [s125] | Is the constraint genuine? | `copy-conversion` + `what-not-to-do.md` Part 2 |
| "Returns went up after the new page" | Pressure nudges raise purchases **and** returns `[C]` [s127] | What changed at checkout | `copy-conversion` |
| "We're not cited by AI" | Not a copy problem in the first instance | Retrievability, entity resolution | `seo-authority-ai` |
| "Our blog doesn't rank" | Article structure, not conversion copy | — | `blog-writer` / `seo-onpage` |

---

## The five-second test

Before any other diagnosis. Read the hero, look away, answer aloud:

1. What does this company do?
2. Who is it for?
3. What am I meant to do next?

Any unanswerable → root cause 3, and nothing below the fold matters until it is fixed.
Everything downstream is written for a reader who got past this.

---

## Audit triage: what to fix first

Rank by leverage, not by severity.

1. **The hero.** Most-read, cheapest to change `[C]` [s259].
2. **The primary CTA and its surrounding copy.** Everything upstream exists to get here. Try
   headline-verbatim repetition on the button `[C]` [s2].
3. **The weakest unsupported claim.** The one a sceptical reader stops on.

Then stop. Rewriting everything at audit stage turns an audit into an unbilled rebuild.

---

## When the diagnosis is "nothing is wrong with the copy"

This is a legitimate and underused finding. It applies when:

- The offer is uncompetitive (root cause 1).
- Traffic is mismatched: the copy is fine for the right reader who is not arriving.
- The volume is too low to know anything. If the page gets a few hundred visits a month, the
  conversion difference the client is worried about is noise `[P]` [s302][s305].

Say it plainly and redirect the budget. Copy work sold as a fix for an offer problem fails,
and it fails in a way that gets blamed on the copy.

---

## Rebrand-adjacent and voice-adjacent questions

If the ask is really about how the brand should sound rather than what a page should say, this
is `brand-voice` territory and the diagnosis is that the copy problem is downstream of a
missing voice spec. Do not write a voice guide inside a copy diagnosis - route it, and note
that copy written before the spec exists will need revisiting.

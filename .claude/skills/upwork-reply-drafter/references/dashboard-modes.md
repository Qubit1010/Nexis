# Dashboard Modes — how Situation and Job Type actually work

Mechanics reference for `projects/upwork-reply-dashboard`. `situations.md` documents the playbook content (goals, moves, research citations); this documents what the UI toggles actually change at runtime.

## The 4 Situations

Each picks a different playbook from `situations.md` and reshapes both the prompt and the form itself — not just a label swap.

| Situation | What it's for | Default stage | Objection/negotiation brain? | Goal presets |
|---|---|---|---|---|
| **Pre-hire** | Answering a client's questions or price/scope pushback before they hire | `pre_hire` | Yes | win the hire · hold my rate · clarify scope · move to a contract |
| **Active project** | Mid-project: status updates, feedback, scope-creep requests | `active` | Yes | contain scope · handle feedback · push to next milestone · unblock the work |
| **Closeout** | Delivery wrap-up + the 5-star review ask | `delivered` | No | land the 5-star review · open a retainer · confirm delivery |
| **Reactivation** | Re-opening a dormant past client | `reactivation` | No | reopen with a reason · offer an Ops Teardown · keep it warm |

Two things change per situation:

1. **Which frameworks load into the prompt.** `loadsObjectionBrain()` (`projects/upwork-reply-dashboard/src/app/api/draft/route.ts`) only pulls in `objection-psychology.md`, `objection-riffs.md`, and the Hormozi value equation for **Pre-hire** and **Active project** — the two situations where a client might push back on price or scope. Closeout and Reactivation skip that brain entirely, since there's nothing to negotiate and loading it risks a defensive-sounding reply where none is needed.
2. **The form itself changes.** Reactivation makes "Client's latest message" optional — the placeholder explains that reactivation opens a *cold* thread from the profile + a past outcome, not a reply to something the client said (`src/app/page.tsx`).

Voss calibrated questions and the banned-phrase/AI-tell filter (`what-not-to-do.md`) load for **all four** situations — those apply regardless of what's being replied to.

## The 3 Job Types

Job type does not swap files — the same brain loads regardless of selection. It only injects a label into the prompt (`JOBTYPE_LABEL` in `route.ts`) that steers positioning tone and which result from the bank gets pulled:

- **AI Services** — "agentic automation, the premium wedge." Leans on the AI results (email triage, lead-gen pipeline).
- **Marketing Automation** — workflows/CRM/lead-ops framing. Leans on the e-commerce/CRM automation results.
- **Web Dev** — React/Next/Webflow build framing. The only job type where portfolio links (tradinghunters.com etc.) are allowed to surface, inheriting the rule from `upwork-proposal-generator` that web links undercut AI positioning elsewhere.

**Summary:** Situation changes the actual conversational strategy and which parts of the brain load. Job type tunes the flavor of proof and positioning within whatever situation is selected.

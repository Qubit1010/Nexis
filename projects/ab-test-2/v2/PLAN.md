# Reply Drafter — Plan

Local tool that drafts replies to inbound client enquiries in Aleem's voice, lets him edit
and rate each draft, and tells him whether his prompt edits are actually making the drafting
better or worse.

Built with `nexis-builder-v2` in `--auto` mode (planning gate skipped by flag).

## The real problem

The first two asks are easy. The third one, "am I getting better or worse", is the whole
project, and the obvious implementation of it is wrong.

The obvious implementation is a thumbs-up counter that trends over time. It lies, for two
reasons:

1. **Confounded inputs.** Prompt v1 was rated on last week's enquiries, v2 on this week's.
   If this week's enquiries are easier, v2 looks better and the prompt had nothing to do
   with it. You are measuring your inbox, not your prompt.
2. **Tiny samples.** Eight ratings on v1 and six on v2 cannot separate a real improvement
   from a coin flip, but a percentage rendered to one decimal place looks authoritative.

So the measurement layer is built around those two failures rather than around a counter.

## Approach

**Prompt versions are immutable records.** Editing the prompt never mutates a row, it
creates a new version. Every draft stores the `prompt_version_id` that produced it, so
attribution is permanent and cannot drift.

**Two signals per draft, not one:**

- *Verdict* (good / bad) — the explicit judgement. Cheap but coarse and subject to mood.
- *Edit ratio* — word-level Levenshtein between the draft served and the text finally
  kept, normalised 0..1. This is revealed preference. It is free, it is continuous, and it
  is much harder to fool yourself with than a thumbs-up. 0.0 means shipped untouched.

**Two comparison surfaces:**

- *Live scoreboard* — rolls up real reviewed drafts per version. Honest about what it is:
  confounded by which enquiries happened to arrive.
- *Bench runs* — a fixed, saved set of enquiries flagged `in_bench`. Running the bench
  against a prompt version drafts every one of them, so version A and version B are
  compared on byte-identical inputs. This is the surface that actually answers the
  question. Bench rating has a blind toggle so the version label is hidden while judging.

**Statistics that refuse to overclaim.** Every approval rate carries a Wilson 95% score
interval. A head-to-head returns `better` / `worse` only when the two intervals do not
overlap; otherwise `no detectable difference`. Under 5 reviews on either side it returns
`not enough data` and declines to render a winner. Displaying "62.5% vs 58.3%" as though
it means something, on n=8, is the failure mode this is built to avoid.

## Stack

Node 24.14.0, **zero runtime dependencies**, no build step.

| Choice | Why |
|---|---|
| Node stdlib only (`node:http`, `node:sqlite`, `node:test`) | The brief says local, and fully runnable and testable without an API key. Zero deps means `npm install` cannot fail, there is no native compile (`better-sqlite3` needs a Windows toolchain), no lockfile drift, no supply chain. Everything needed is already in the installed runtime. |
| SQLite via `node:sqlite` | The product is longitudinal comparison across versions. That is `GROUP BY` work and it has to survive restarts. A JSON file is fine at version 1 and the wrong call by version 5. Verified available unflagged on this runtime. |
| Native TypeScript type stripping | Types on the data model, zero build step. Verified `node file.ts` runs on 24.14.0. Constrains to erasable syntax: no enums, no parameter properties, `import type` for type-only imports. |
| Vanilla HTML/CSS/JS frontend | Three screens on localhost. React plus Vite would add a build and a `node_modules` for that. Hand-written CSS also makes the visual direction easier to hit than overriding a framework's defaults. |
| Provider adapter, mock by default | The load-bearing decision for "testable without a key". No key present, the deterministic mock drafts. Key present, live Claude. |

Ports: web 3300, API 4300, both bound to 127.0.0.1. One process starts both.

## Model

`claude-sonnet-5`. $2 per million input tokens, $10 per million output tokens. Both the ID
and the prices read live from `platform.claude.com` on 2026-09-01, not from memory — the
pricing page carries a note that Sonnet 5's introductory $2/$10 became the standard price
rather than rising to $3/$15 on 2026-09-01, which is today, so this specifically needed
checking.

Sent with `output_config: { effort: "low" }`. Also verified live: effort is nested under
`output_config`, not a top-level field, and the docs recommend `low` for latency-sensitive
non-coding chat work, which is exactly what drafting a short email is. Header
`anthropic-version: 2023-06-01`, confirmed current.

Opus 5 is 2.5x the price for a task that is tone-matching, not reasoning. Haiku 4.5 is half
the price but this is client-facing copy where voice is the entire product.

## The mock provider

A mock that returns a constant string would make the measurement feature untestable, since
every prompt version would score identically. So the mock is **deterministic and
prompt-sensitive**: it seeds from a hash of the system prompt plus the enquiry, and it
reads directives out of the system prompt (brevity, warmth, asking a discovery question,
naming a price, signing off) and changes its output accordingly. Bench runs across
different prompt versions therefore produce genuinely different drafts, and the whole
scoreboard, comparison and bench pipeline can be exercised with no key at all.

Every draft row stores its `provider`. The scoreboard flags any version whose stats mix
mock and live drafts, so an offline demo can never be mistaken for a real measurement.

Token counts and cost are recorded **only** from a real API response. Mock drafts store
null tokens and null cost rather than an invented estimate.

## Security baseline

Localhost tool, so the controls that matter are the ones against hostile input, not auth:
bind 127.0.0.1 explicitly (never 0.0.0.0); every SQL statement prepared and parameterised;
64KB request body cap; type, length and enum validation on every field of every endpoint;
path-traversal-safe static serving; API key read from env only, never logged, never
returned, `/api/health` exposes a boolean and nothing else. Enquiry bodies arrive from
email and are treated as hostile: the frontend renders all user text via `textContent`,
never `innerHTML`.

## Design direction

"Quiet instrument." Warm paper ground, near-black ink, one ochre accent, a serif for
display type against a system sans for UI, hairline rules instead of card-and-shadow,
generous whitespace. Deliberately not a default-framework dashboard. Light and dark both.

## Deliberately not building

- No email ingestion (IMAP/Gmail). Enquiries are pasted. The brief says "reads an inbound
  enquiry", and a connector is a separate project with its own auth story.
- No sending. It drafts, the user copies. Nothing here should be able to email a client.
- No auth, no multi-user. Single local user, and adding login to a 127.0.0.1 tool is theatre.
- No LLM-as-judge auto-scoring. The signal being measured is *this user's* taste, and a
  model judging its own output would launder that away.
- No streaming responses. A draft is a few hundred tokens.
- No migration framework. `CREATE TABLE IF NOT EXISTS` at boot is right at this size.

---

## What changed during the build

Recorded because the plan is the only bookkeeping file here.

**Three defects the review and the tests actually caught, all fixed:**

1. **NUL truncation.** SQLite stores TEXT as a C string, so an enquiry body containing a
   NUL byte was silently stored as only the text before it, with no error anywhere. Found
   by a hostile-input test. Fixed with `stripNul` at the validation boundary, which turns
   unbounded silent data loss into one removed control character.
2. **`safeResolve` decided nothing.** It normalised before stripping leading separators, so
   `normalize` clamped `..` at the root and the containment check never got to reject
   anything. Not exploitable as written, but the security property was accidental rather
   than enforced. Reordered so containment is what decides.
3. **The entrypoint was never executed by any test.** 114 tests passed while `npm start`
   was broken by a syntax error in `src/main.ts`, because every suite imported modules
   directly and none booted the app. Caught by running it, not by the suite. Added
   `test/smoke.test.ts`, which spawns the real entrypoint and drives it over HTTP.

**Smaller corrections:** POST endpoints that update rather than create now return 200
instead of 201; the web server got the same loopback Host check as the API, since a proxied
request reaches the API with the Host rewritten and a GET carries no Origin to fall back on;
the offline drafter's brevity mode produced a near-empty draft and now produces a short one.

**Added beyond the plan:** `scripts/demo.ts`, which builds a demo database so the scoreboard
can be seen populated without an hour of clicking. Its ratings are synthetic and it says so
on every run, and it writes to its own file so it cannot contaminate the real database.

**Verified rather than assumed:** foreign keys are genuinely enforced (`PRAGMA foreign_keys`
returns 1 and an orphan insert is rejected); all four routes render in Chromium with no
console errors in light and dark; the full loop, including the edit ratio, was driven by
clicking in a real browser.

**Final state:** 116 tests, all passing. Runs with no API key.

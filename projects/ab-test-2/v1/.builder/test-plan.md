---
project: ReplyLab
phase: 5 (test design)
shape: testing trophy
runner: vitest
---

# Test Plan — ReplyLab

## Shape: trophy

Integration-heavy. The value in this app is in the seams: an HTTP request reaching a service,
reaching SQLite, and coming back with the right attribution. Most of the risk lives there, not
in individual functions. So the bulk of the suite drives the real Express app over real HTTP
against a real (in-memory) SQLite database, with a thin unit layer under the two pieces of
genuine logic: the Wilson interval and the edit distance.

No E2E browser suite. There is one user, on one machine, and the UI is thin over the API. A
Playwright install would cost more than it would catch at this tier. Named here so it is a
decision, not an oversight.

## Priority order, mapped to what actually hurts if it breaks

There is no auth and no money path in this app, so the standard top two priorities do not apply.
The equivalent "expensive when wrong" list here is:

1. **Attribution.** A draft must be permanently tied to the prompt version that produced it. If
   this breaks, every number on the scoreboard silently becomes a lie, and nothing in the UI
   would look wrong. This is the single most important thing to test.
2. **Immutability of the generated text.** Editing must never overwrite what the model wrote,
   because that text is the baseline the edit-distance signal is measured against.
3. **Statistical honesty.** A 1-of-1 version must not report a confident 100%. The Wilson
   interval and the minimum-sample flag are tested directly, including the degenerate cases at
   0 and 1 where the naive interval collapses.
4. **The no-key path.** `selectProvider` must choose the stub when no key is present, and the
   stub must be deterministic, or the integration tests cannot assert on content.
5. **The core loop.** Create an enquiry, draft, edit, rate, change the prompt, re-draft, and see
   the scoreboard reflect all of it.
6. **Boundary validation.** Bad bodies and bad ids get a 400 with the contract's error shape,
   not a 500.

## What is deliberately not tested

- **The live Anthropic call.** There is no API key in this environment, so no test executes a
  real request. `draftWithClient` is tested through a fake client that reproduces the SDK's
  response shape, which covers the response handling, the refusal branch, and error mapping.
  It does **not** prove the request parameters are accepted by the live API. That is stated in
  the completion report as an unverified path rather than papered over with a passing test.
- React components. No jsdom, no Testing Library. The UI is thin, and asserting on it at this
  tier would mostly test React.
- SQLite itself, and Express's routing.

## Running it

```
npm test        # vitest run
npm run typecheck
```

Tests use `:memory:` databases, so they leave nothing behind and do not touch `data/`.

# Test Strategy — the Test Design phase (Phase 5)

The goal is coverage of the paths that would actually hurt if they broke, not a coverage-percentage badge. Right-sized to the complexity tier. Write the plan to `.builder/test-plan.md`, wire the runner, write the tests.

## Pick the shape: trophy vs pyramid

Read the blueprint's best-practices checklist first; it usually names the intended shape. If not, choose from the app's nature:

- **Testing trophy** (integration-heavy) — the default for most web apps and anything with a UI + API + DB. The bulk of value is in integration tests that exercise real seams (route -> handler -> service -> DB). Thin unit layer for pure logic, a few end-to-end tests for the critical journeys, static analysis (types + lint) as the base.
- **Testing pyramid** (unit-heavy) — for logic-dense systems: libraries, algorithms, data pipelines, financial calculation engines. Many fast unit tests, fewer integration, fewest E2E.

State which shape and why in `test-plan.md`.

## What to test first (priority order)

Test the things that are expensive when they fail, in this order:

1. **Auth + authorization.** Can an unauthenticated user reach protected data? Can one user read/write another's data? If the blueprint uses row-level security or roles, test that a wrong role is denied. This is the most common real breach.
2. **Money paths.** Any payment, payout, billing, or balance flow. Correct amounts computed server-side, webhook signature verification, idempotency (a replayed webhook does not double-charge), failure/refund/dispute handling. Use the provider's test mode and test accounts.
3. **The core loop.** The one journey the product exists for (in a marketplace: discover -> propose -> pay -> get paid; in a tracker: log -> view analytics). If this breaks, the product is down.
4. **Data integrity.** Constraints that matter: uniqueness, required relationships, cascade behavior, computed/denormalized fields staying correct.
5. **Non-trivial logic.** Anything with branching or math: date/time handling, parsing, aggregation, pricing, state machines. Unit-test these directly.

Do not spend the budget on trivial CRUD getters/setters or framework behavior. Test your logic, not the framework's.

## Scale to tier

- **Simple:** smoke tests of the core flow + static analysis (types, lint). A handful of tests.
- **Standard:** integration tests for auth + the primary journey + any money path, unit tests for the non-trivial logic, static analysis. One or two E2E happy paths if there is a UI.
- **Complex:** the above plus authz/RLS matrix tests, webhook/idempotency tests, edge/failure cases on the money path, and E2E across the main roles.

## Runner setup (per stack, from the blueprint)

Wire the ecosystem-standard runner. Do not introduce a testing stack foreign to the blueprint's choices.

- **TS/JS:** Vitest (or Jest) for unit/integration, Playwright for E2E, Testing Library for components.
- **Python:** pytest (+ httpx/requests for API, Playwright for E2E).
- **Other:** the ecosystem default (Go `testing`, etc.).

Include: how to run the suite (`npm test` / `pytest`), any test DB / fixtures / env needed, and how it plugs into the review phase (code-reviewer runs this suite in Phase 6).

## Output: test-plan.md

Use `templates/test-plan.md`. It records the chosen shape, the runner, the prioritized coverage list (mapped to the flows above), what is deliberately not tested (and why), and how to run it. The tests themselves live in the project's test directory per the ecosystem convention.

## Honesty

If a flow cannot be meaningfully tested in the MVP (e.g. a third-party sandbox is unavailable), say so in `test-plan.md` and note what a real test would need. Do not write a hollow test that asserts nothing to inflate the count.

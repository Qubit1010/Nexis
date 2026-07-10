# Pipeline — the run manual

This is the phase-by-phase orchestration for `nexis-builder`. It plays the role the `Nexus-Fullstack-Developer` CLAUDE.md played, upgraded: no house stack, a design phase, a test phase, a polish pass, and research-grounded execution.

Read `artifact-conventions.md` alongside this. `status.md` is the source of truth for where a run is.

---

## Before Phase 0 — bootstrap

1. **Classify the input:**
   - A blueprint (a path such as `references/athllo-mvp-blueprint.md`, or pasted blueprint text) -> ingest directly as Phase 0.
   - A raw brief, idea, or client/Upwork post -> Phase 0 runs `developer-advisor` to produce the blueprint.
   - Too vague to build -> ask for the core requirement (what it does, for whom, the one non-negotiable) before scaffolding. Do not invent a whole app.
2. **Derive the project name** (short, PascalCase).
3. **Choose the output directory.** Default `projects/<ProjectName>/`. Client/confidential build -> an external or gitignored path. Confirm in one line if not the default.
4. **Scaffold the bus:** create `<output>/.builder/` and write `status.md` with `phase: blueprint`, `started`/`updated` timestamps, `complexity: pending`. See `artifact-conventions.md` for the exact frontmatter.
5. All subsequent paths are relative to the project directory.

---

## Phase 0 — Blueprint (worker: developer-advisor)

**Goal:** a problem-first blueprint whose stack is derived from the problem, not a default.

- **If a blueprint was provided:** copy it verbatim to `.builder/blueprint.md` (add frontmatter: `source`, `received`). Do not re-derive or "improve" the stack. Trust the advisor's decision.
- **If not:** invoke `developer-advisor` in Project Architect mode with the brief. Let it run its intake (it may ask the user the smallest high-leverage question set) and produce the blueprint. Save the result to `.builder/blueprint.md`.
- **Extract into `status.md`:** the headline stack (frontend / backend / data / auth / hosting), the platform (web/mobile/both), and any hard constraints. These are read, never overridden, downstream.

**Transition:** `status.md` -> `blueprint: COMPLETE`, `architecture: STARTED`.

**Do not:** substitute a familiar stack, add a database the blueprint did not call for, or "upgrade" the choices. If the blueprint is missing a load-bearing decision, go back to `developer-advisor` for it (do not fill it with a default).

---

## Phase 1 — Architecture spec (worker: senior-architect)

**Goal:** turn the blueprint into a buildable, unambiguous spec using `templates/architecture-doc.md`.

- Score complexity (simple / standard / complex) on the 5 dimensions (data, auth, UI, integrations, scale). This tier drives depth everywhere downstream.
- Fill the architecture doc: overview, complexity, **tech stack copied from the blueprint** (rationale references the blueprint's reasoning, not a house preference), project structure, DB schema (standard/complex), the full **API contract** (Section 6, the frontend/backend handshake), frontend breakdown, backend breakdown, env vars, implementation order.
- On any implementation detail that is version-sensitive or not obvious (a payment flow, an auth pattern, a realtime approach), escalate per `research-during-build.md` before committing it to the spec. Cite what you find in `decisions.md`.
- Write `.builder/architecture.md` and start `.builder/decisions.md`.

**Transition:** `architecture: COMPLETE (complexity: <tier>)`, `design: STARTED`.

**Immutability:** once written, `architecture.md` is not edited by later phases. If a later phase must change it, log the reason in `decisions.md` and note it in the review report.

---

## Phase 2 — Design direction (workers: ui-ux-pro-max + taste-skill + ui-design-system)

**Goal:** a product-specific visual system so the UI does not look AI-generated. This is the anti-slop phase. Follow `design-standards.md`.

- Read the blueprint + architecture for the product's personality, audience, and platform.
- Use `ui-ux-pro-max` for the design intelligence (style, palette, type pairing, layout, a11y, component patterns). Use `taste-skill` when a specific aesthetic is wanted or the default risks looking generic (brutalist, minimalist, luxury, motion-heavy). Use `ui-design-system` to lock tokens (color scale, spacing, radius, shadow, motion) for clean dev handoff.
- Write `.builder/design-system.md` (see `templates/design-system.md`): chosen aesthetic + why it fits, palette with roles, type system, spacing/radius/shadow tokens, motion language, key component treatments, and 1-2 signature UI moments.

**HUMAN CHECKPOINT.** Present the direction concisely and ask go / adjust. Do not proceed to Phase 3 on an unapproved direction. Skip only if `--auto`.

**Transition (after approval):** `design: COMPLETE`, `frontend: STARTED`.

---

## Phase 3 — Frontend (worker: senior-frontend)

**Goal:** build the UI against both the API contract and the approved design system.

- Scaffold per the blueprint's framework (whatever it is: Next.js, Vite+React, SvelteKit, Expo, etc. — never assume).
- Implement the design tokens from `design-system.md` first (theme, globals), then build components and pages from the architecture's component hierarchy (Section 7).
- Build a typed API client matching the contract (Section 6). Wire routing and state.
- Enforce `design-standards.md`: responsive, accessible (focus states, contrast, touch targets, reduced-motion), premium polish (real empty/loading/error states, no placeholder lorem left in).
- Verify the frontend builds cleanly before finishing (`build` / typecheck for the chosen toolchain).

**Transition:** `frontend: COMPLETE`, `backend: STARTED`.

---

## Phase 4 — Backend (worker: senior-backend)

**Goal:** implement every endpoint in the contract, plus schema and middleware.

- Scaffold the server per the blueprint (framework, ORM, DB, auth all from the blueprint).
- Build the schema/migrations (Section 5), the middleware stack (auth, validation, error wrapper, security headers), and every endpoint in Section 6 using a clean layering (routes -> handlers -> services).
- Enforce the security baseline from `code-standards.md`: validate all input, verify webhook signatures, idempotency on payment mutations, no secrets in source, least-privilege data access (RLS if the blueprint uses it).
- Create `.env.example` with every required variable. Verify the server starts and typechecks.
- On a version-sensitive integration (payments, auth provider, third-party API), escalate per `research-during-build.md`.

**Transition:** `backend: COMPLETE`, `test-design: STARTED`.

---

## Phase 5 — Test design (worker: references/test-strategy.md)

**Goal:** a right-sized test suite that covers the paths that matter, not coverage theater.

- Read the blueprint's best-practices checklist for the intended approach (trophy vs pyramid) and the highest-risk flows.
- Write `.builder/test-plan.md` (see `templates/test-plan.md`): the strategy, the runner, and the prioritized list of what to test (auth, payments/money paths, the core loop, RLS/authz).
- Wire the runner and write the critical-path tests. Scale to tier: simple gets smoke tests of the core flow; standard/complex gets integration tests of auth + the money path + the primary journey, plus unit tests for non-trivial logic.

**Transition:** `test-design: COMPLETE`, `review: STARTED`.

---

## Phase 6 — Review + polish (workers: code-reviewer, then ponytail/impeccable)

**Goal:** verify it works and matches the spec, then tighten quality.

**Review (code-reviewer):**
- Verify every endpoint in Section 6 is implemented on BOTH backend and frontend, with matching field names/types/URLs.
- Run typecheck + build (both sides) and the test suite from Phase 5.
- Check the security baseline and completeness against architecture Sections 7-8.
- Write `.builder/review-report.md` (see `templates/review-report.md`).
- **Fix-loop (one pass):** if `status: fail`, apply critical fixes directly, re-verify once, update the report. If still failing -> `status: blocked`.

**Polish (ponytail / impeccable), only if review is not blocked:**
- Run a YAGNI/quality pass: remove dead code and speculative abstractions, collapse duplication, prefer stdlib/native/existing-dependency over new code, tighten names. Do not add features or change behavior. Re-run typecheck + tests after polishing to confirm nothing broke.

**Transition:** `review: COMPLETE (status: pass|blocked)`.

---

## Phase 7 — Completion (this skill)

**If review passed:**
- Set `status.md` phase to `complete`.
- Report to the user: project name, the stack (as built), how to run it (install, env setup, dev/build commands), test status, and the notable calls from `decisions.md`.
- Note the natural next steps: deploy (per the blueprint's hosting choice), or hand the pitch to `proposal-generator`.

**If blocked:**
- Set phase to `blocked`, present the remaining issues from `review-report.md`, ask the user for guidance. Do not silently ship a broken build.

---

## Status transitions (quick reference)

```
blueprint -> architecture -> design -> [CHECKPOINT] -> frontend -> backend -> test-design -> review -> (fix-loop?) -> polish -> complete
                                                                                                       └-> blocked (needs user)
```

Every arrow is a `status.md` append. On resume, read the last entry and continue from the next phase. Never restart a `COMPLETE` phase.

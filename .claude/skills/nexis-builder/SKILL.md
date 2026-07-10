---
name: nexis-builder
description: >
  The implementation counterpart to developer-advisor. Takes a build blueprint (from developer-advisor), a raw project brief, or an Upwork/client post, and autonomously builds a complete, production-ready project by orchestrating specialized skills in sequence: developer-advisor (blueprint) -> senior-architect (spec) -> ui-ux-pro-max/taste-skill (design direction) -> senior-frontend + senior-backend (build) -> test design -> code-reviewer + ponytail/impeccable (review and polish). It inherits developer-advisor's doctrine: PROBLEM-FIRST, NO HOUSE STACK. The stack comes from the blueprint, never a default. It stays research-grounded during the build by escalating to developer-advisor's three-tier resolution (local refs -> NotebookLM -> Exa live) for "how do I best implement X in 2026" questions. Communicates through a .builder/ artifact bus, scales to project complexity, and is resume-safe. Runs autonomously with ONE human checkpoint at the UI/UX design direction (the anti-slop gate). Use whenever Aleem wants a project actually BUILT, not just planned. Triggers: "build this project", "build this app", "implement this blueprint", "turn this blueprint into code", "scaffold and build X", "build me a <app>", "code this up", "build the MVP", pasted brief or Upwork post + "build it", "run the builder", or after developer-advisor produces a blueprint and Aleem says "now build it". This is the EXECUTION layer; developer-advisor is the DECISION layer that precedes it.
argument-hint: [blueprint path, project brief, or "build <idea>"]
---

# Nexis Builder

The build engine. Advisor plans, Builder builds. It takes what `developer-advisor` decided (or derives it first) and produces a complete, running project: architecture spec, a premium non-generic UI, frontend, backend, tests, and a reviewed, polished codebase. The stack is whatever the problem needs. There is no house stack.

## What this is (read once)

`nexis-builder` orchestrates a pipeline of existing skills, communicating through a `.builder/` artifact bus inside the target project directory. It is the implementation half of a two-skill flow:

- **`developer-advisor` = the DECISION layer.** What to build, which architecture and stack, how the pieces connect. Produces the blueprint. Stops there.
- **`nexis-builder` = the EXECUTION layer.** Takes the blueprint and builds the actual project. Starts there.

Phase 0 is the seam between them. Either skill can run alone: advisor for a plan with no build, builder on an existing blueprint (or a raw brief, in which case it calls advisor internally first).

Doctrine (inherited from `developer-advisor`, non-negotiable):
- **Problem first, stack second. There is NO house stack.** The stack is read from the blueprint, which derived it from the problem. This pipeline injects no defaults. It exists precisely because the old `Nexus-Fullstack-Developer` pipeline hardcoded React+Vite+Express, which is the bias we removed. If there is no blueprint, get one from `developer-advisor`. Never fall back to a fixed stack.
- **Premium, not AI slop.** A dedicated design-direction phase (ui-ux-pro-max + taste-skill + ui-design-system) sets a product-specific visual system before any UI is built, gated by one human checkpoint. Generic-looking output is a failure, not an acceptable default.
- **Research-grounded execution.** When an implementation detail is non-trivial or version-sensitive ("current best way to wire Stripe Connect", "RSC data-fetching pattern in 2026"), escalate to `developer-advisor`'s three-tier resolution (`references/research-during-build.md`) instead of guessing from memory.
- **Simplest thing that ships.** YAGNI. Scale the output to the complexity tier. A landing page is not a SaaS.

## Clean split with sibling skills (important)

- **nexis-builder owns:** orchestration. Sequencing the phases, managing the `.builder/` artifact bus, the design checkpoint, the review fix-loop, resume logic, and the final handoff.
- **The phase workers (invoked by this skill, not re-implemented here):**
  - `developer-advisor` — Phase 0, the blueprint (problem-first stack decision).
  - `senior-architect` — Phase 1, the buildable architecture spec.
  - `ui-ux-pro-max` + `taste-skill` + `ui-design-system` — Phase 2, the design direction.
  - `senior-frontend` / `senior-backend` — Phases 3-4, the build.
  - `code-reviewer` — Phase 6, contract/security/build verification + one fix-loop.
  - `ponytail` / `impeccable` — Phase 6, the quality/polish pass.
- **Hands off entirely to:** `ai-use-case-generator` / `proposal-generator` / `sales-playbook` for the client pitch; `claude-advisor` for Claude-product questions. This skill builds software, it does not pitch or sell.

## Context to Load First

1. `references/pipeline.md` — the phase-by-phase orchestration detail (always load; this is the run manual).
2. `references/artifact-conventions.md` — the `.builder/` bus format and rules.

Then load the phase-specific reference when you reach that phase: `code-standards.md` (all build phases), `design-standards.md` (Phase 2), `test-strategy.md` (Phase 5), `research-during-build.md` (any phase, on a hard implementation question). Templates live in `templates/`.

---

## The Pipeline

| Phase | Worker(s) | Reads | Writes | Purpose |
|------|-----------|-------|--------|---------|
| **0 Blueprint** | `developer-advisor` | user input / existing blueprint | `.builder/blueprint.md` | Get the problem-first stack + architecture. Ingest an existing blueprint, or derive one. The seam with the advisor. |
| **1 Architecture** | `senior-architect` | `blueprint.md` | `.builder/architecture.md`, `.builder/decisions.md` | Turn the blueprint into a buildable spec: complexity tier, full API contract, DB schema, structure, implementation order. Stack from the blueprint, no defaults. |
| **2 Design direction** | `ui-ux-pro-max` + `taste-skill` + `ui-design-system` | `blueprint.md`, `architecture.md` | `.builder/design-system.md` | Product-specific visual system (style, palette, type, spacing, motion, components, a11y). **HUMAN CHECKPOINT.** |
| **3 Frontend** | `senior-frontend` | `architecture.md`, `design-system.md` | frontend source | Build the UI against the contract and the design system. Premium, responsive, accessible. |
| **4 Backend** | `senior-backend` | `architecture.md` | backend source | Build the API, schema, middleware. Security baseline enforced. |
| **5 Test design** | `references/test-strategy.md` | `blueprint.md`, `architecture.md` | `.builder/test-plan.md` + tests | Trophy vs pyramid, critical-path tests (auth, payments, core flow), wire the runner. |
| **6 Review + polish** | `code-reviewer`, then `ponytail`/`impeccable` | all source + `architecture.md` | `.builder/review-report.md` | Verify contract both sides, security, build. One fix-loop. Then a YAGNI/quality polish pass. |
| **7 Completion** | this skill | `status.md` | `status.md` | Report how to run, notable decisions, test status. |

Full inputs/outputs, section references, and transitions are in `references/pipeline.md`.

---

## How to Start

When the user asks to build something:

1. **Determine the input type.** Existing blueprint (a path like `references/athllo-mvp-blueprint.md`, or pasted blueprint text) -> ingest it as Phase 0. Raw brief or idea -> run `developer-advisor` first to produce the blueprint. Too vague to build ("make something cool") -> ask for the core requirement before starting.
2. **Derive a project name** (short, PascalCase: `Athllo`, `TaskFlow`, `LedgerLite`).
3. **Pick the output directory.** Default `projects/<ProjectName>/`. If the user names a path, or it is a confidential client build, use that instead. Confirm the location in one line before scaffolding if it is not the default.
4. **Create the project directory + `.builder/`** and write `.builder/status.md` (see `artifact-conventions.md`). All subsequent paths are relative to `<ProjectName>/`.
5. **Run the phases in order** per `references/pipeline.md`, updating `status.md` at every transition. Pause only at the Phase-2 design checkpoint (unless `--auto`).

## The Design Checkpoint (the anti-slop gate)

After Phase 2 writes `design-system.md`, STOP and present the direction to the user: the chosen aesthetic and why it fits the product, the palette, the type system, the motion/interaction feel, and 1-2 signature UI moments. Ask for a go / adjust. Do not build the frontend on an unapproved direction. This one gate is where "premium, not generic" is won. Skip it only if invoked with `--auto`.

## Autonomy Rules

1. **Do not ask for confirmation between phases** except the Phase-2 design checkpoint.
2. **Do not pick a stack.** It comes from the blueprint. If you are reaching for a default, stop and re-read Phase 0.
3. **Stop for the user only if:** requirements are too vague to build (Phase 0), or the review is still failing after the one fix-loop (Phase 6, status `blocked`).
4. **`status.md` is the source of truth.** Update it at every transition.
5. **Scale to the complexity tier.** The architect's tier (simple/standard/complex) drives depth downstream.
6. **`--auto`** skips the design checkpoint for a fully autonomous run.

## Resume Support

If a run is interrupted, read `.builder/status.md` to find the current phase and resume from there. Never restart a completed phase. Artifacts are append-only; `architecture.md` is immutable once written.

---

## Writing / Quality Rules

- All generated code follows `references/code-standards.md` (stack-agnostic: it adapts to whatever the blueprint chose).
- All UI meets `references/design-standards.md` (accessibility, responsive, premium bar).
- Security baseline is not optional: input validation, no secrets in source, parameterized queries, verified webhooks, least-privilege auth. See `code-standards.md`.
- On any non-trivial or version-sensitive implementation call, consult `references/research-during-build.md` before writing code from memory.
- Log every deviation from the blueprint or any non-obvious choice to `.builder/decisions.md`.

## Edge Cases

| Scenario | Action |
|----------|--------|
| No blueprint, only an idea | Run `developer-advisor` (Project Architect) first to produce `blueprint.md`, then proceed. |
| Blueprint exists (path or pasted) | Ingest as Phase 0 verbatim. Do not re-derive the stack. |
| Requirements too vague to build | Ask for the core requirement (what it must do, for whom) before scaffolding. Do not guess a whole app. |
| Tempted to use a default stack | Stop. The stack is in the blueprint. If it is not, the blueprint is incomplete, go back to Phase 0. |
| Implementation detail is version-sensitive or unfamiliar | Escalate via `references/research-during-build.md` (advisor refs -> NotebookLM -> Exa live). Flag anything net-new as fresh. |
| Design direction feels generic | Re-run Phase 2 with `taste-skill` for a stronger aesthetic before the checkpoint. Generic is a fail. |
| Review still failing after one fix-loop | Mark `status: blocked`, surface the remaining issues, ask the user for guidance. |
| Client / confidential build | Target an external or gitignored output path, not `projects/`. Confirm the path first. |
| User asks for the client pitch / proposal | Hand off to `proposal-generator` / `ai-use-case-generator`. This skill builds, it does not sell. |

## Reference Map

```
references/
├── pipeline.md              # RUN MANUAL: phase-by-phase orchestration, inputs/outputs, transitions, fix-loop, resume
├── artifact-conventions.md  # the .builder/ bus: artifacts, frontmatter, append-only, status.md, immutability
├── code-standards.md        # stack-agnostic code standards + security baseline (all build phases)
├── design-standards.md      # Phase 2 anti-slop bar: ui-ux-pro-max/taste/ui-design-system usage + a11y/responsive/premium checklist + checkpoint format
├── test-strategy.md         # Phase 5: trophy vs pyramid, critical-path coverage, runner setup per stack
└── research-during-build.md # escalation to developer-advisor's 3-tier resolution for implementation questions
templates/
├── architecture-doc.md      # Phase 1 output (stack rows from the blueprint, NOT defaults)
├── design-system.md         # Phase 2 output
├── test-plan.md             # Phase 5 output
└── review-report.md         # Phase 6 output
```

Sibling skills: **developer-advisor** (Phase 0 decision layer, the planner this pairs with), **senior-architect / senior-frontend / senior-backend / code-reviewer** (phase workers), **ui-ux-pro-max / taste-skill / ui-design-system** (design phase), **ponytail / impeccable** (polish), **proposal-generator / ai-use-case-generator / sales-playbook** (the client pitch, not this skill's job).

## Note on Google Docs

This skill builds code, not documents. There is no Google Docs export. The blueprint (a developer-advisor deliverable) can be exported by that skill; the running project is the deliverable here.

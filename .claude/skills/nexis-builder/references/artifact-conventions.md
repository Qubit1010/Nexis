# Artifact Conventions — the `.builder/` bus

The `.builder/` directory is the communication bus between pipeline phases. It lives inside the target project directory, self-contained, so multiple builds never collide.

```
projects/Athllo/                 # (or a client/external path)
├── .builder/                    # pipeline artifacts for THIS project
│   ├── blueprint.md             # Phase 0 (from developer-advisor)
│   ├── architecture.md          # Phase 1 (from senior-architect) — IMMUTABLE
│   ├── design-system.md         # Phase 2 (from ui-ux-pro-max/taste/ui-design-system)
│   ├── test-plan.md             # Phase 5
│   ├── review-report.md         # Phase 6 (from code-reviewer)
│   ├── decisions.md             # append-only decision log
│   └── status.md                # pipeline state — SOURCE OF TRUTH
├── <source code>                # the actual project, structure per architecture.md
└── ...
```

All source code, configs, dependencies, and `.builder/` artifacts stay inside the project directory. Nothing leaks to the repo root.

## Format

Every artifact is markdown with YAML frontmatter:

```markdown
---
key: value
---

# Content
```

## Artifacts

### blueprint.md
Written by: Phase 0 (developer-advisor output, or an ingested existing blueprint).
Read by: senior-architect, and every later phase that needs to know the stack or the best-practices checklist.
The problem-first plan. The stack here is authoritative and is never overridden downstream.

### status.md
Written by: every phase (append on start + complete).
Read by: every phase, and the orchestrator on resume. **The source of truth for pipeline state.**

```yaml
---
project: Athllo
phase: blueprint|architecture|design|frontend|backend|test-design|review|polish|complete|blocked
started: 2026-07-10T10:00:00Z
updated: 2026-07-10T10:30:00Z
complexity: pending|simple|standard|complex
stack: "Next.js + Supabase + Stripe Connect"   # copied from the blueprint once known
output_dir: projects/Athllo
---
# Pipeline Status
## Phase History
- [2026-07-10T10:00:00Z] blueprint: STARTED
- [2026-07-10T10:12:00Z] blueprint: COMPLETE
- [2026-07-10T10:12:00Z] architecture: STARTED
```

### architecture.md
Written by: senior-architect (Phase 1).
Read by: senior-frontend, senior-backend, test design, code-reviewer.
The central buildable spec. Numbered sections (1-11) that downstream phases reference by number. Uses `templates/architecture-doc.md`. **Immutable** once written (see rules).

### design-system.md
Written by: Phase 2.
Read by: senior-frontend (Phase 3).
The product-specific visual system and tokens. Uses `templates/design-system.md`. This is what keeps the UI from looking generic.

### test-plan.md
Written by: Phase 5.
Read by: code-reviewer (runs the suite), the user.
The test strategy + prioritized coverage. Uses `templates/test-plan.md`.

### review-report.md
Written by: code-reviewer (Phase 6).
Read by: the orchestrator, the user.
Contract verification, completeness, security, build/test results, fix log. Uses `templates/review-report.md`.

### decisions.md
Written by: any phase, append-only.
Read by: all phases, the user.
Each entry:
```
[YYYY-MM-DD] DECISION: <what> | REASONING: <why> | CONTEXT: <constraint / phase>
```
Used whenever a phase makes a non-obvious call, deviates from the blueprint, or acts on a research escalation.

## Rules

1. **Never delete artifacts.** Only append or create.
2. **Frontmatter is machine-readable.** Phases parse it for state and context.
3. **`status.md` is the source of truth.** Check it before doing anything, especially on resume.
4. **`architecture.md` is immutable** after Phase 1 writes it. A later phase that genuinely must change it logs why in `decisions.md` and flags it in `review-report.md`. Do not silently edit.
5. **The stack in `blueprint.md` is authoritative.** No phase substitutes its own stack preference. There is no house stack.
6. **Timestamps are ISO 8601.**
7. **Resume-safe:** on interruption, the last `status.md` entry tells you where to continue. Never restart a `COMPLETE` phase.

---
name: nexis-builder-v2
description: "Builds a complete, running project end to end from a plan or a raw idea: discovery and planning if needed, then code, tests, review and fixes, in one pass by one agent. This is the deliberate lean A/B counterpart to nexis-builder (v1): no .builder artifact bus, no phase manual, and no delegation to senior-frontend, senior-backend, senior-architect, ui-ux-pro-max, code-reviewer or ponytail, so the two can be compared honestly on the same brief. Say 'nexis-builder-v2', 'build this with v2', 'v2 build', 'compare v1 and v2'. For the standard orchestrated pipeline use nexis-builder."
argument-hint: [PLAN.md path, pasted plan, or "build <idea>"] [--auto]
---

# Nexis Builder v2

Plan or idea in, a project that actually runs out. One agent carries the whole flow:
discovery and research, architecture and planning, coding, testing, reviewing.

Deliberately thin: no phase manual, no artifact bus, no standards files, no templates,
no sub-skills. You know how to build software, so build it.

## Input

- **A plan** (a `PLAN.md` path or pasted text): take it as-is. Do not re-derive the stack.
- **A raw idea or brief:** do the discovery, research and planning yourself first. Do not
  call `developer-advisor-v2` to get it. Ask the smallest set of questions that would
  change the build, batched into one round.
- **Too vague to build:** ask what it must do and for whom first. Never guess an app.

Default output is `projects/<Name>/`. For a client or confidential build, confirm the
path in one line first.

## The one gate

Write the plan to `PLAN.md` in the project directory, then stop and present it: the
approach, the stack, the design direction, and what you are deliberately not building.
Wait for a go or an adjust.

The only interruption in the run. A wrong plan caught here costs one message; caught
after the build it costs a rebuild. `--auto` skips the gate.

`PLAN.md` is the only bookkeeping file. Keep it current if the build diverges, so a long
run survives a compaction. No status file, no decisions log, no other scaffolding.

## Then build it

After the go, run to completion without stopping: code, tests, review, fix, report. How
you sequence frontend against backend, the design direction, what deserves a test, and
what the review looks for are yours to decide.

**Non-negotiables:**

- **The stack comes from the plan.** If you catch yourself reaching for a default,
  re-read the plan.
- **It has to actually run.** Install the dependencies, start it, exercise the main flow,
  run the tests. A project you never executed is not finished, and reporting it as
  finished is the worst failure available here.
- **Security is not optional.** Validate input, parameterize queries, real auth checks on
  real endpoints, no secrets in source.
- **Premium, not generic.** Default-framework-looking UI is a failure, not an acceptable
  outcome. Decide a visual direction that fits this specific product and commit to it.
- **Verify version-sensitive details live** rather than writing them from memory: current
  API shapes, framework versions, config formats.
- **Simplest thing that ships.** Scale everything to the actual project.

**Review means reviewing.** When the code is written, read it as if someone else wrote it
and you have to sign off. Check the frontend against the backend contract, check the
error paths, check the security baseline, run the build and the tests. Fix what is wrong
and re-verify. Loop until it passes, or until you are genuinely stuck, and say clearly
which of the two happened.

**Do the work yourself.** Do not invoke `nexis-builder`, `senior-architect`,
`senior-frontend`, `senior-backend`, `ui-ux-pro-max`, `code-reviewer`, `ponytail`, or any
other skill, and do not fan out to subagents. One agent, whole pipeline. That is the
experiment; delegating defeats it.

## Finish

Report briefly: how to run it, notable decisions and deviations from the plan,
test status, anything left undone. Be accurate about what you verified versus what you
assumed. No emojis, no em dashes in body text.

---
name: ask-matt
description: Ask which skill or flow fits your situation. A router over the user-invoked skills in this repo.
disable-model-invocation: true
---

# Ask Matt

You don't remember every skill, so ask.

A **flow** is a path through the skills. Most paths run along one **main flow**, and two **on-ramps** merge onto it. Everything else is standalone.

## The main flow: idea → ship

The route most work travels. You have an idea and want it built.

1. **`/grill-with-docs`** — sharpen the idea by interview. Start here when you **have a codebase**: it's stateful, retaining what it learns in `CONTEXT.md` and ADRs. (No codebase? Use `/grill-me` — see Standalone.)
2. **Branch — can you settle every question in conversation?** If a question needs a runnable answer (state, business logic, a UI you have to see), detour through a prototype, bridged by **`/handoff`** in both directions (see Crossing sessions):
   - **`/handoff`** out, then open a fresh session against that file,
   - **`/prototype`** to answer the question with throwaway code,
   - **`/handoff`** back what you learned, and reference it from the original idea thread.
3. **Branch — is this a multi-session build?**
   - **Yes** → **`/to-prd`** (turn the thread into a PRD) → **`/to-issues`** (split the PRD into independently-grabbable issues). Because the issues are independent, **clear context between each one**: start a fresh session per issue and kick off **`/implement`** by passing it the PRD and the single issue to work on.
   - **No** → **`/implement`** right here, in the same context window.

### Context hygiene

Keep steps 1–3 in **one unbroken context window** — don't compact or clear until after `/to-issues` — so the grilling, PRD, and issues all build on the same thinking. Each `/implement` then starts fresh, working from the issue.

The limit on this is the **[smart zone](https://www.aihero.dev/ai-coding-dictionary/smart-zone)**: the window (~120k tokens on state-of-the-art models) within which the model still reasons sharply. If a session approaches it before `/to-issues`, don't push on degraded — `/handoff` and continue in a fresh thread.

## On-ramps

A starting situation that generates work, then merges onto the main flow.

- **Bugs and requests piling up** → **`/triage`**. It moves issues through triage roles and produces agent-ready issues, which **`/implement`** later picks up.

  Triage is only for issues **you didn't create** — bug reports, incoming feature requests, anything that arrives raw. Issues that `/to-issues` produced are already agent-ready, so **don't triage them**.

## Codebase health

Not feature work — upkeep.

- **`/improve-codebase-architecture`** — run whenever you have a spare moment to keep the codebase good for agents to operate in. It surfaces deepening opportunities; picking one _generates an idea_ you can take into the main flow at `/grill-with-docs`.

## Crossing sessions

- **`/handoff`** — when a thread is full or you need to branch off (e.g. into a `/prototype` session), this compacts the conversation into a markdown file. You don't continue in place — you **open a new session and reference that file** to carry the context across. It's the bridge between context windows, in either direction. Use it when you want a **fresh session** but need the **current conversation preserved**.
- **`/compact`** (built-in) — stay in the **same conversation**, letting the earlier turns be summarized. Use it at **intentional breaks between phases**, when you don't mind losing the verbatim history. Don't compact mid-phase — the agent can lose its way. `/handoff` forks; `/compact` continues.

## Standalone

Off the main flow entirely.

- **`/grill-me`** — the same relentless interview as `/grill-with-docs`, but for when you have **no codebase**. Stateless: it saves nothing locally, builds no `CONTEXT.md`. Reach for it to sharpen any plan or design that doesn't live in a repo.
- **`/teach`** — learn a concept over multiple sessions, using the current directory as a stateful workspace.
- **`/writing-great-skills`** — reference for writing and editing skills well.

## Debugging & quality

- **`/diagnosing-bugs`** — structured diagnosis loop for hard bugs and performance regressions. Use when something is broken, throwing, or slow. Runs before you write any fix.
- **`/tdd`** — test-driven development: red → green → refactor. Use when building features or fixing bugs test-first.
- **`/review`** — code review over a diff or file set. Use before merging.
- **`/qa`** — interactive QA session where you report bugs conversationally and the agent files GitHub issues.
- **`/request-refactor-plan`** — interview-driven refactor plan filed as a GitHub issue; produces safe, incremental commit steps.
- **`/resolving-merge-conflicts`** — use when an in-progress git merge or rebase has conflicts.
- **`/git-guardrails-claude-code`** — add Claude Code hooks to block dangerous git commands (push, reset --hard, clean, branch -D) before they run.
- **`/setup-pre-commit`** — add Husky pre-commit hooks with lint-staged (Prettier), type-check, and tests.

## Architecture & design vocabulary

- **`/codebase-design`** — shared vocabulary for designing deep modules; use when designing or improving a module's interface, or finding deepening opportunities.
- **`/domain-modeling`** — build and sharpen the project's domain model and ubiquitous language; record architectural decisions.
- **`/ubiquitous-language`** — pin down domain terminology for the project.
- **`/decision-mapping`** — map out the decisions inside a plan before committing to one.
- **`/design-an-interface`** — generate multiple radically different interface designs for a module using parallel sub-agents. Use when you want to compare module shapes before picking one.

## Writing & articles

- **`/writing-fragments`** — mining session: surfaces raw fragments (claims, vignettes, sharp sentences, half-thoughts) and appends them to a document as raw material.
- **`/writing-beats`** — shape raw material into an article beat by beat, choose-your-own-adventure style.
- **`/writing-shape`** — take a pile of notes or a rough draft and shape it into a publishable article through a conversational session.
- **`/edit-article`** — edit an existing article for clarity, flow, and structure.

## Specialised workflows

- **`/migrate-to-shoehorn`** — migrate test files from `as` type assertions to `@total-typescript/shoehorn`.
- **`/scaffold-exercises`** — create exercise directory structures with sections, problems, solutions, and explainers.
- **`/obsidian-vault`** — search, create, and manage notes in an Obsidian vault with wikilinks and index notes.

## Precondition

**`/setup-matt-pocock-skills`** — run before your first engineering flow to configure the issue tracker, triage labels, and doc layout the other skills assume. Custom issue trackers also work.

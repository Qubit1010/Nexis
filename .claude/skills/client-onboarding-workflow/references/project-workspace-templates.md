# Project Workspace Templates

Reference for the **local project workspace** generated per client in Phase 2 of this
skill. This is the internal, strategic command center for actually running an engagement,
separate from the client-facing Drive kit produced in Phase 1.

The workspace lives in the gitignored, confidential `client-projects/<client-slug>/`
folder at the repo root. Nothing here is shared with the client. Two files in particular
(`05-bottlenecks.md`, `06-improvements.md`) are internal-only and must never be pushed to
the client Drive.

## When this runs

Standalone, decoupled from signing day. Aleem invokes it when he is ready to start
running the project: after onboarding, after the kickoff call, or whenever he wants the
project board set up. It is not auto-run during the Phase 1 onboarding flow.

## The `<client-slug>` rule

Lowercase, hyphenated, no special characters. Strip ampersands and punctuation.

- "Belle & Perry" -> `belle-perry`
- "Acme Co." -> `acme-co`
- "FintechCo" -> `fintechco`

The slug is the folder name under `client-projects/`. Reuse the existing folder if one is
already there (a client can have one workspace across multiple projects).

## File layout

```
client-projects/<client-slug>/
  README.md            hub: at-a-glance status, links to the Drive kit + the 6 docs, last-updated
  01-overview.md       who the client is, what they do, engagement type, relationship dynamics
  02-what-they-want.md requirements, goals, phases, deliverables, success metrics, scope boundaries
  03-my-role-rules.md  Aleem's role + responsibilities, the client's principles, comms, constraints, Aleem's own rules
  04-task-board.md     local task board by status (In progress / Next / Backlog / Done), tagged by stage
  05-bottlenecks.md    the client's operational bottlenecks (what Aleem is hired to fix) + project risks/blockers (INTERNAL)
  06-improvements.md   value-add ideas, expansion/upsell paths to pitch as the relationship grows (INTERNAL)
```

## Authoring rules

- **Ground every claim in the source docs.** The onboarding guide, proposal, and call
  transcript are the truth. Do not invent facts about the client, their team, their tools,
  or their goals.
- **Mark unknowns, do not guess.** If a fact is not in the docs, write
  `TBD - confirm on kickoff` rather than inventing it. This is especially important for
  names, dates, tools, and pricing.
- **House style.** No em dashes (use commas or periods), no emojis, direct and specific
  voice. Same rules as the rest of the agency's written output. See Memory
  `feedback_google_docs_encoding.md`.
- **Keep the internal files internal.** `05-bottlenecks.md` and `06-improvements.md` are
  Aleem's private strategic read on the account. They never get copied to the client Drive
  or pasted into a client-facing doc.
- **Write for a working session, not a report.** These files are meant to be opened and
  updated mid-project. Lead with what matters, keep sections scannable, prefer bullets and
  short tables over prose.
- **Seed the task board from the Phase 1 checklist** when it exists, so the local board and
  the shared Sheet start aligned. After that, the local board is the day-to-day working
  layer Aleem updates; the Sheet stays as the shared/client artifact.

---

## File skeletons

Each skeleton below is a starting structure. Adapt headings to the actual engagement, drop
sections that do not apply, and add ones that do. Replace every `<...>` prompt with
synthesized content from the docs, or `TBD - confirm on kickoff` if unknown.

### README.md (the hub)

```markdown
# <Client Name> - Project Workspace

**Status:** <one line: current phase + immediate next action>
**Engagement:** <role / project type, e.g. "AI Systems Developer, transcript-to-content pipeline">
**Started:** <YYYY-MM-DD or TBD>

## Drive kit (client-facing)
- Project folder: <client_folder_url>
- Onboarding doc: <onboarding_doc_url>
- Checklist sheet: <checklist_sheet_url>

## Workspace docs (internal)
- [Overview](01-overview.md) - who they are
- [What they want](02-what-they-want.md) - requirements and goals
- [My role and rules](03-my-role-rules.md) - how I operate on this account
- [Task board](04-task-board.md) - live working board
- [Bottlenecks](05-bottlenecks.md) - what I'm hired to fix (internal)
- [Improvements](06-improvements.md) - expansion ideas (internal)

Last updated: <YYYY-MM-DD>
```

The Drive kit URLs come from the Phase 1 orchestrator output. If Phase 1 has not run for
this client, leave the three Drive links as `TBD - run onboarding kit` and say so in the
report.

### 01-overview.md

```markdown
# Overview - <Client Name>

## Who they are
<What the company does, the market and niche they operate in.>

## Team and structure
<Key people and roles relevant to the engagement. Who Aleem reports to. Who he works
alongside. Mark anyone unknown as TBD.>

## Engagement type
<One-off project vs ongoing partnership. Modular vs full build. Any stated long-term
intent, e.g. co-building or expanding scope later.>

## Relationship dynamics
<How they like to work, what they value, tone of the relationship, anything from the call
transcript that signals how to manage the account.>
```

### 02-what-they-want.md

```markdown
# What They Want - <Client Name>

## The core ask
<In one or two sentences: the outcome they are paying for.>

## Phases / roadmap
<If the work is phased, list each phase with its scope. Phase 1 first, in detail.>

## Deliverables
<Concrete things being produced. Bullets.>

## Success metrics
<How they will judge whether this worked. Pulled from the docs, not assumed.>

## Scope boundaries
<What is explicitly in scope and what is not. The line that prevents scope creep.>
```

### 03-my-role-rules.md

```markdown
# My Role and Rules - <Client Name>

## My role
<Aleem's title and what he owns on this engagement. Who he reports to.>

## My responsibilities
<The specific things Aleem is accountable for. Bullets.>

## The client's working principles
<Any stated values or operating principles the client expects the work to follow.>

## Communication
<Primary channel, meeting cadence, response-time expectation, point of contact.>

## Hard constraints
<Real limits to design around: platform/tooling differences, timezone overlap, contract or
platform rules, access dependencies. These shape every build decision.>

## My own working rules
<Aleem's self-imposed rules for running this account well, given the constraints above.
E.g. favor cloud/platform-independent builds, document as you go, protect Phase 1 scope.>
```

### 04-task-board.md

```markdown
# Task Board - <Client Name>

Local working board. Move tasks between sections as they progress. The shared checklist
Sheet is the client-facing mirror; this is the private working layer.

## In progress
- [ ] <task> _(stage: <Discovery/Workflow Map/Build/Test/Handoff>)_

## Next
- [ ] <task> _(stage: ...)_

## Backlog
- [ ] <task> _(stage: ...)_

## Done
- [x] <task> _(stage: ...)_

Last updated: <YYYY-MM-DD>
```

Seed the sections from the Phase 1 checklist stages and current reality: what is genuinely
underway goes in In progress, the immediate next actions in Next, everything else in
Backlog, and anything already completed (e.g. the onboarding kit) in Done.

### 05-bottlenecks.md (INTERNAL)

```markdown
# Bottlenecks and Risks - <Client Name>  (internal only)

## Client's operational bottlenecks
<The actual pain Aleem is hired to fix. The slow, manual, or inconsistent steps in their
current process. This is the problem definition that the build should target.>

## Project risks and blockers
<What could derail delivery: tooling friction, async timezone, scope creep, dependencies on
access or sample data, single points of failure. For each, a one-line mitigation if known.>
```

### 06-improvements.md (INTERNAL)

```markdown
# Improvements and Expansion - <Client Name>  (internal only)

## Value-add ideas
<Things Aleem can bring that the client has not asked for yet but would benefit from.
Ground these in capabilities Aleem already has, e.g. existing skills or systems to adapt.>

## Expansion and upsell paths
<Where this engagement can grow: later phases, retainers, additional systems, a longer-term
operating-system play. What to pitch and when.>
```

---

## Report format (after writing the workspace)

```
**Project workspace ready: <Client Name>**

Wrote `client-projects/<client-slug>/`:
- README.md (hub)
- 01-overview.md
- 02-what-they-want.md
- 03-my-role-rules.md
- 04-task-board.md
- 05-bottlenecks.md (internal)
- 06-improvements.md (internal)

This folder is gitignored and confidential. Bottlenecks and improvements are internal-only,
never pushed to the client Drive.
```

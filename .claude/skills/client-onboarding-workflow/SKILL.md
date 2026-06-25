---
name: client-onboarding-workflow
description: >
  Two phases for running a NexusPoint client. PHASE 1 (Onboarding Kit): spin up a complete
  onboarding kit when a deal is signed: a Drive folder structure, an onboarding Google Doc,
  a project checklist Google Sheet tailored to the project type, and a Gmail draft of the
  welcome email (saved as draft, not sent). Reads a prior proposal or discovery doc to
  pre-fill the kit, or takes inline intake when no doc exists. PHASE 2 (Project Workspace):
  a standalone step that processes the client's source docs into a confidential local
  project command center under `client-projects/<client-slug>/` (overview, what they want,
  Aleem's role and rules, a live task board, the client's bottlenecks, and improvement ideas).

  Use this skill whenever Aleem says or implies "we just closed [client]", "onboard
  [client]", "set up onboarding for [client]", "kick off the [project]", "we signed
  [client]", "client onboarding", "create the project kit", "spin up the folder for
  [client]", or pastes a proposal Doc URL with words like "onboard them", "set them up",
  "let's get them going". Also trigger when Aleem references a closed deal moving into
  delivery, even if he doesn't use the word "onboarding". Lean toward triggering when in
  doubt: this is the post-close workflow and Aleem won't always name it.

  For PHASE 2 specifically, also trigger on "build the project workspace for [client]",
  "set up the project board for [client]", "process the [client] docs into a workspace",
  "make a project command center for [client]", or "turn these client docs into a workspace".

  Don't trigger for: prospect research before a deal closes (use discovery-call-prep),
  proposal writing (use proposal-generator), or onboarding existing clients into a
  separate engagement (ask first).
argument-hint: "[proposal doc URL or client name + project type]"
---

# Client Onboarding Workflow

You set up the full kit a NexusPoint client needs on day 1: Drive folders, an onboarding
Doc, a project checklist Sheet, and a welcome email draft. The goal is to remove the
manual setup that happens between "deal signed" and "kickoff call" so Aleem can spend
his time closing the next deal instead of clicking through Drive.

## Why this matters

Onboarding sets the client's first impression of NexusPoint as an organized agency, not
a freelancer. A folder structure, a clear doc, and a thoughtful welcome email signal
"this is a real operation." Skipping it costs trust early and creates downstream chaos.

## Context to load

Read these before generating any artifacts:
- `references/checklist-templates.md` — checklist stages by project type, owner defaults
- `references/welcome-email-voice.md` — voice rules and example emails (no em dashes,
  no emojis, under 200 words, 5-beat structure)
- `context/team.md` — for owner assignments in the timeline table
- `context/work.md` — for service categories that map to project types
- `references/project-workspace-templates.md` — Phase 2 only: the local workspace spec

Also recall: Memory `feedback_google_docs_encoding.md` — never use em dashes in any
Doc/Sheet content (use commas or periods).

## Two phases

This skill has two phases that run independently:

- **Phase 1: Onboarding Kit** — the day-1 client-facing kit (Drive folders, onboarding Doc,
  checklist Sheet, welcome email draft). Runs when a deal is signed.
- **Phase 2: Project Workspace** — a standalone, internal command center for running the
  engagement, written to the confidential local `client-projects/<client-slug>/` folder.
  Runs when Aleem is ready to start managing the project, decoupled from signing day.

Route to the phase the request implies. "Onboard [client]" / "we signed [client]" is
Phase 1. "Build the project workspace / project board for [client]", "process the [client]
docs into a workspace" is Phase 2. If both are wanted, run Phase 1 first so its Drive URLs
can be linked from the Phase 2 README.

## Phase 1: Onboarding Kit

### Step 1: Resolve input

**If Aleem pasted a Google Doc URL or ID** (proposal, discovery prep, scope doc):
1. Run `python .claude/skills/client-onboarding-workflow/scripts/extract_proposal.py "<url_or_id>"` to pull the doc text.
2. From the returned text, extract these fields:
   - `client_name` (required)
   - `industry`
   - `contact_name`
   - `contact_email` (required)
   - `project_type` — match to one of: web-design, full-stack, ai-automation, cms,
     custom-saas, data-analysis (use the closest fit)
   - `project_name` — short name for the project (e.g., "Acme website rebuild")
   - `scope_summary` — 2-3 sentences
   - `deliverables` — bulleted list
   - `timeline_weeks` — total project duration
   - `start_date` — if specified
   - `price` — if specified
3. If `client_name`, `contact_email`, or `project_type` is missing or ambiguous, ask
   Aleem to confirm or fill in. Don't guess on these three.

**If no doc was provided**, ask 4-5 targeted questions to fill the same fields:

> "Quick intake. I need:
> 1. Client + contact name
> 2. Contact email
> 3. Project type (web design / full-stack / AI automation / CMS / SaaS / data)
> 4. One-line scope and any specific deliverables
> 5. Timeline and start date if known"

Don't proceed without `client_name`, `contact_email`, `project_type`. Everything else
has reasonable defaults.

### Step 2: Build the doc spec

Construct the onboarding doc as JSON sections (same schema as proposal-generator):

```json
{
  "title": "[Client] -- Onboarding",
  "sections": [
    {"heading": "Project overview", "level": 1, "body": "..."},
    {"heading": "Scope summary", "level": 1, "bullets": ["...", "..."]},
    {"heading": "Timeline", "level": 1, "table": {
      "headers": ["Phase", "Owner", "Start", "End"],
      "rows": [["...", "...", "...", "..."]]
    }},
    {"heading": "Communication", "level": 1, "bullets": ["...", "..."]},
    {"heading": "What we need from you", "level": 1, "bullets": ["...", "..."]},
    {"heading": "Next steps", "level": 1, "body": "..."}
  ]
}
```

Section guidance:

1. **Project overview** — One paragraph synthesized from the source doc. What we're
   building, why it matters to them. Concrete, not generic.
2. **Scope summary** — Bulleted deliverables. Pulled directly from the proposal scope.
3. **Timeline** — Table. Phase / Owner / Start / End. Use the project-type checklist
   stages (Discovery, Design, Build, QA, Launch — or whatever the template specifies)
   as the phases. Owner defaults from `references/checklist-templates.md`. Leave Start
   / End blank if no specific dates were committed; otherwise compute from `start_date`
   and `timeline_weeks`.
4. **Communication** — Bullets covering: primary channel (default WhatsApp + email),
   weekly check-in cadence (default Friday async update), response time commitment
   (default within 24h on weekdays), point of contact (Aleem unless otherwise scoped).
5. **What we need from you** — Project-type-specific access/asset list. Reference the
   checklist template's Discovery stage for hints. Tailor to the actual scope.
6. **Next steps** — One paragraph: kickoff call ask, first milestone, link to the
   checklist sheet. The link goes in here as plain URL text.

Write everything in NexusPoint's voice: confident, direct, specific. No fluff. No em
dashes. No emojis.

### Step 3: Build the checklist spec

Pick the matching template from `references/checklist-templates.md`. Adapt:
- Inject 2-4 scope-specific rows under the Build stage (based on actual deliverables)
- Drop generic rows that don't apply
- Set Owner using the project-type defaults
- Status = "Not started" for every row
- Due and Notes blank

Build the checklist JSON:

```json
{
  "title": "[Client] -- Project Checklist",
  "headers": ["Stage", "Task", "Owner", "Due", "Status", "Notes"],
  "rows": [
    ["Discovery", "Kickoff call (60 min)", "Aleem", "", "Not started", ""],
    ...
  ]
}
```

### Step 4: Write the welcome email

Follow `references/welcome-email-voice.md`. Hard requirements:
- Under 200 words
- No em dashes, no emojis
- 5 beats: opening (mirror something specific) → what's set up → what we need →
  kickoff call ask → signoff
- Include placeholders for the three URLs (folder, doc, sheet) — the orchestrator
  doesn't substitute them, so write the actual URLs into the body after step 5
  produces them. Build the body in two passes if needed.

For the first pass, write the email with placeholder strings `[FOLDER_URL]`,
`[DOC_URL]`, `[SHEET_URL]`. After step 5 returns real URLs, do a string replacement
before assembling the final spec.

### Step 5: Pipe the spec to the orchestrator

Assemble the full spec:

```json
{
  "client_name": "...",
  "project_name": "...",
  "contact_name": "...",
  "contact_email": "...",
  "doc": { ... },
  "checklist": { ... },
  "email": { "subject": "...", "body": "..." }
}
```

Pipe it:

```bash
echo '<full_spec_json>' | python .claude/skills/client-onboarding-workflow/scripts/create_onboarding.py
```

The script:
1. Finds or creates `NexusPoint Clients` parent folder
2. Creates `[Client]` subfolder under it
3. Creates the 5 standard subfolders (`01-Onboarding` through `05-Invoices`)
4. Creates the onboarding Doc inside `01-Onboarding`
5. Creates the checklist Sheet inside `01-Onboarding`
6. Creates a Gmail draft to `contact_email` with the subject and body provided

It returns:

```json
{
  "status": "ok",
  "client_folder_url": "...",
  "subfolders": {"01-Onboarding": "...", ...},
  "onboarding_doc_url": "...",
  "checklist_sheet_url": "...",
  "draft_id": "..."
}
```

### Step 6: Backfill URLs into the email if you used placeholders

If the body had `[FOLDER_URL]`, `[DOC_URL]`, `[SHEET_URL]` placeholders, do a second
pass: rewrite the email body with real URLs, then update the draft. The simplest path
is to just call the orchestrator twice — once with placeholders to get real URLs, then
again with the substituted body. That works because folder/doc/sheet creation is
find-or-create-style and won't duplicate.

Cleaner alternative: in the model layer, run create_onboarding.py first with an empty
email body, then call `gws gmail users drafts update` separately with the populated
body. If you do that, the orchestrator will return `draft_id` from the first call and
you can update it.

For most cases just run twice — it's fast and idempotent.

### Step 7: Report to Aleem

Single concise message in this format:

```
**Onboarded: [Client]**

- Folder: [client_folder_url]
- Onboarding doc: [onboarding_doc_url]
- Checklist: [checklist_sheet_url]
- Welcome email: saved as Gmail draft to [contact_email]

Review the draft in Gmail before sending. The kit is in `NexusPoint Clients / [Client]`.
```

No editorializing, no recap of what was in the proposal. Aleem already knows.

## Phase 2: Project Workspace (standalone)

A standalone phase that turns the client's source docs into a confidential local project
command center: the strategic layer Aleem actually runs the engagement from. It is separate
from the Phase 1 Drive kit and runs on its own trigger, not automatically after onboarding.

Output is a multi-file markdown workspace in `client-projects/<client-slug>/`, which is
gitignored and confidential. Two of the files (bottlenecks, improvements) are internal-only
and never get pushed to the client Drive. No new script is needed: you author these local
files directly.

Read `references/project-workspace-templates.md` first. It holds the file layout, the
per-file skeletons, the authoring rules, the `<client-slug>` rule, and the README hub format.

### Step 1: Resolve client and locate source docs

Identify the client and find their source material. Sources, in order of preference:
1. A Google Doc URL or ID Aleem points to (proposal, onboarding guide, call transcript).
2. The client's Drive folder (often under `NexusPoint Clients / [Client]`, or a docs folder
   Aleem names). Locate the relevant docs inside it.

Pull each doc's text with `python .claude/skills/client-onboarding-workflow/scripts/extract_proposal.py "<url_or_id>"`.
If you cannot find or read the source docs, ask Aleem where they are before proceeding.
Do not fabricate the workspace from nothing.

### Step 2: Compute the slug and create the folder

Compute `<client-slug>` per the rule in the templates reference ("Belle & Perry" ->
`belle-perry`). Create `client-projects/<client-slug>/` if it does not exist. Reuse it if it
does.

### Step 3: Author the workspace files

Write README.md plus the six `0X-*.md` files using the skeletons in
`references/project-workspace-templates.md`, synthesizing everything from the source docs.

- Ground every claim in the docs. Mark anything not in the docs as `TBD - confirm on kickoff`.
- House style: no em dashes, no emojis, direct and specific.
- Seed `04-task-board.md` from the Phase 1 checklist stages and current reality (kit done,
  kickoff/access pending, etc.).
- In README.md, link the Drive kit URLs from the Phase 1 orchestrator output. If Phase 1 has
  not run for this client, set those three links to `TBD - run onboarding kit` and note it.
- Keep `05-bottlenecks.md` and `06-improvements.md` internal. Never copy them to the client
  Drive.

### Step 4: Report

Use the report format at the bottom of `references/project-workspace-templates.md`: list the
files written, note the folder is gitignored and confidential, and that bottlenecks and
improvements are internal-only.

## Phase 3: Task Progress (mark done + guide next step)

A lightweight, standalone operation that keeps the local task board and the Drive checklist
Sheet in sync whenever a task is completed, and tells Aleem what to do next.

Trigger phrases: "we finished [task]", "mark [task] done", "we had the [meeting/call/session]
and [outcome]", "we got [access/asset]", "done with [task]", "what's my next task for [client]".

### How it runs

**Step 1: Identify what is done.**
Parse Aleem's message to understand which task(s) have been completed. Match against tasks
in `client-projects/<client-slug>/04-task-board.md` — fuzzy-match on keywords
("kickoff call" matches "Schedule and run the kickoff call", "Slack access" matches
"Get Slack access and channel invites", etc.).

**Step 2: Update the local task board.**
In `04-task-board.md`:
- Move each completed task from its current section to the `## Done` section.
- Change `- [ ]` to `- [x]` on each completed task.
- If the task was the only item in `## In progress`, promote the first item in `## Next`
  to `## In progress`.
- Update `Last updated: YYYY-MM-DD` to today.

**Step 3: Update the Drive checklist Sheet.**
Read the checklist spreadsheet ID from the README.md Drive kit links (the `checklist_sheet_url`
line). Row numbers: the Sheet header is row 1, tasks start at row 2. Match the task name
to the correct row and update column E (Status) to `"Done"` using:
```
gws sheets spreadsheets values batchUpdate \
  --params '{"spreadsheetId":"<ID>"}' \
  --json '{"valueInputOption":"USER_ENTERED","data":[{"range":"Sheet1!E<ROW>","values":[["Done"]]}]}'
```
If the sheet ID is unknown, ask Aleem for the spreadsheet URL before updating.

Also update the README.md **Status** line to reflect the new current state.

**Step 4: Identify and surface the next task.**
Look at `## In progress` after the update. If it has items, the first one is the active task.
If `## In progress` is empty, the first item in `## Next` is what should be started now.

Report in this format:

```
**[Client] task update**

Done:
- [x] Kickoff call (60 min)
- [x] Get Slack access and channel invites

Next up: Collect 3-5 real sample transcripts (stage: Discovery)
[One sentence on what this involves and why it unblocks the rest of Discovery]
```

Keep the guidance sentence concrete: what to collect, who to ask, or what specifically to do,
based on what the skill already knows about the client from the workspace docs.

## Edge cases

- **No proposal doc + sparse intake** ("we signed Acme"): Ask the 5 intake questions
  before doing anything. Don't generate placeholder content.
- **Source doc is a discovery-call-prep brief, not a proposal**: Same flow. The brief
  has enough to extract client, contact, scope direction. Mark `price` and
  `timeline_weeks` as missing if not present, then ask Aleem to confirm.
- **Gmail draft fails** (auth issue, scope missing): The script returns `draft_error`
  in the output. Surface this to Aleem and ask if he wants you to output the email body
  in chat so he can paste it manually.
- **Drive permission errors**: Same approach — surface the error, suggest re-auth via
  `gws auth`.
- **Client name has special characters** (e.g., "Acme & Co", apostrophes): The folder
  search uses `name='...'` queries — escape single quotes by doubling them in the query
  if needed. The orchestrator doesn't currently auto-escape, so warn Aleem if the name
  has unusual characters and offer a sanitized version.
- **Existing folder with the same client name**: The find-or-create logic reuses it.
  This is correct behavior — multiple projects for the same client should land under
  one parent. Subfolders also reuse, so re-running won't create duplicates.
- **Aleem asks to skip the email step**: Just don't include `email` and skip step 4.
  But the orchestrator currently requires the email field; pass an empty subject/body
  and tell Aleem the draft will be empty.

## Quality bar

**Phase 1**, before reporting back, verify:
- The onboarding doc has all 6 sections
- The checklist has at least 10 rows for web/full-stack/SaaS, at least 8 for CMS/AI/data
- The email is under 200 words, has no em dashes, no emojis, no "I hope this finds you
  well", and references something specific from the proposal
- The "What we need from you" section has 3-6 concrete items, not 10+ (overwhelming)
- All four URLs are real and load

**Phase 2**, before reporting back, verify:
- `client-projects/<client-slug>/` contains README.md plus the six `0X-*.md` files, all
  non-empty
- Every claim is grounded in the source docs. Unknowns read `TBD - confirm on kickoff`, not
  invented facts
- No em dashes, no emojis anywhere in the files
- `client-projects/` is gitignored, and nothing from `05-bottlenecks.md` /
  `06-improvements.md` is copied to the client Drive

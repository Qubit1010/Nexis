---
name: client-onboarding-workflow
description: >
  Spin up a complete client onboarding kit when a NexusPoint deal is signed: a Drive folder
  structure, an onboarding Google Doc, a project checklist Google Sheet tailored to the
  project type, and a Gmail draft of the welcome email (saved as draft, not sent). Reads a
  prior proposal or discovery doc to pre-fill the kit, or takes inline intake when no doc
  exists.

  Use this skill whenever Aleem says or implies "we just closed [client]", "onboard
  [client]", "set up onboarding for [client]", "kick off the [project]", "we signed
  [client]", "client onboarding", "create the project kit", "spin up the folder for
  [client]", or pastes a proposal Doc URL with words like "onboard them", "set them up",
  "let's get them going". Also trigger when Aleem references a closed deal moving into
  delivery, even if he doesn't use the word "onboarding". Lean toward triggering when in
  doubt: this is the post-close workflow and Aleem won't always name it.

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

Also recall: Memory `feedback_google_docs_encoding.md` — never use em dashes in any
Doc/Sheet content (use commas or periods).

## Workflow

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

Before reporting back, verify:
- The onboarding doc has all 6 sections
- The checklist has at least 10 rows for web/full-stack/SaaS, at least 8 for CMS/AI/data
- The email is under 200 words, has no em dashes, no emojis, no "I hope this finds you
  well", and references something specific from the proposal
- The "What we need from you" section has 3-6 concrete items, not 10+ (overwhelming)
- All four URLs are real and load

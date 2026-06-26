---
name: meeting-insights
description: >
  Transforms a meeting, call, or conversation transcript into a structured markdown file
  of insights saved to docs/meetings/. Use this skill whenever the user pastes any block
  of conversation text (with or without speaker labels), shares a file path to a transcript,
  or links a Google Doc with call notes — and wants it turned into anything organized:
  action items, key points, a summary, client notes, or takeaways. Trigger on intent, not
  exact wording. "Process this", "log this call", "notes from my call with X", "what came
  out of that meeting", "extract the action items", "summarize what we said", or pasting a
  transcript alongside any request to do something with it — all trigger this skill. Covers
  discovery calls, sales calls, internal team reviews, vendor calls, onboarding calls, and
  rough jotted notes. When in doubt, trigger it.
argument-hint: "[paste transcript, file path, or Google Doc URL] [optional: meeting name]"
---

# Meeting Insights

Turns a raw meeting transcript into a clean, structured markdown file saved under
`docs/meetings/`. Output is scannable in under two minutes — only what was said
and decided, nothing padded.

---

## Step 1 — Load the Transcript

Determine the input type from the user's message:

**Inline paste:** Transcript text is in the message directly. Use it as-is.

**File path:** A local path was provided (e.g., `transcripts/acme-call.txt`).
Read the file before proceeding.

**Google Doc URL or ID:** A Google Docs URL was provided. Read the document via the
Google Docs MCP tool. If the MCP tool is unavailable, ask the user to paste the text.

**Nothing provided:** Ask for the transcript before doing anything else.

---

## Step 2 — Extract Metadata

Pull these fields from the transcript or the user's message:

| Field | Source | If missing |
|---|---|---|
| Meeting name / topic | User's message or transcript header | Ask one question: "What should I call this meeting?" — nothing else |
| Date | User's message, transcript header, or file name | Use today's date |
| Attendees | Transcript speaker labels | List whoever spoke; mark as "unknown" if labels are absent |
| Client / Project | User's message or transcript context | Omit the field if not determinable |
| Duration | Transcript timestamps or user's message | Omit the field entirely |

Only ask one clarifying question if something critical is missing. Never ask about
more than one thing at a time.

---

## Step 3 — Derive the Output Filename

Format: `YYYY-MM-DD-<slug>.md`

- Date = meeting date (today if unknown)
- Slug = meeting name: lowercase, hyphens for spaces, strip special characters
- Examples: `2026-06-26-acme-discovery-call.md`, `2026-06-26-team-sprint-review.md`
- If a file already exists at that path, warn the user and ask: "A file already exists
  at that path. Overwrite, or use a different name?"

---

## Step 4 — Analyze and Extract

Read the full transcript carefully. Extract each section defined in
`references/output-template.md`.

Rules (and why they matter):
- **Only include what is actually in the transcript.** Never infer, assume, or invent.
  The output is a record someone will act on — invented items cause real confusion.
- **Skip sections with no content.** If no decisions were made, omit that section
  entirely. An empty section header adds noise and makes the reader wonder if something
  was missed. Never write "None" or leave a blank section.
- **Preserve specificity.** "We need this by Friday the 20th" stays exactly that,
  not "soon." Specific dates and names are the most actionable parts of any transcript.
- **Action items:** include owner and deadline when stated. If only one was stated,
  include it and mark the other as `unspecified`. Without an owner, tasks vanish.
  Without a deadline, they just drift. Do not drop an action item because one field
  is missing — include it with what was said.
- **Quotes are allowed for decisions** where the exact phrasing matters (e.g., a
  commitment made by a client).
- **General Notes is the catch-all.** Anything worth capturing that does not fit
  another section goes here — tone, context, red flags, background info shared. If
  nothing is left over, omit this section too.

---

## Step 5 — Write the File

Follow `references/output-template.md` exactly for structure and formatting.

Write to: `docs/meetings/<filename>`

Create `docs/meetings/` if it does not exist.

After writing, confirm:
```
Meeting insights saved: docs/meetings/<filename>
Sections captured: [comma-separated list]
Sections omitted: [comma-separated list, or "none"]
```

One brief note at the end if something was unclear in the transcript and may have
affected extraction quality. Otherwise nothing else.

---

## Input Examples

**Inline transcript:**
> Process this transcript: [large block of text with speaker labels]

**Rough notes:**
> Meeting notes from the Acme call: [bullet points or stream of consciousness]
Treat as the transcript.

**File path:**
> Extract insights from transcripts/acme-onboarding.txt

**Google Doc URL:**
> Pull the notes from this doc: https://docs.google.com/document/d/[id]

**Minimal context with transcript:**
> Here's the call with Belle and Perry from yesterday: [transcript]
Use "belle-perry" and yesterday's date for the filename.

---

## Quality Check Before Saving

- [ ] Filename follows `YYYY-MM-DD-<slug>.md`
- [ ] Metadata block has date and attendees at minimum
- [ ] Every action item has an owner or explicitly marks it unspecified
- [ ] No section present with empty content
- [ ] Present sections follow the template order
- [ ] No invented details
- [ ] No em dashes, no emojis

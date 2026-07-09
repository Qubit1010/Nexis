---
name: post-creator
description: >-
  End-to-end post creation from the Weekly Posting Schedule sheet. Takes a schedule row
  (topic + description + content mode + pillars + design templates), finds 8-12 sources
  with Exa, loads them into a NotebookLM notebook and queries it for a detailed Formal
  source summary and a Simplified one, writes the finished LinkedIn/Instagram post in
  Aleem's voice using the content-engine rules, saves everything to a Google Doc, fills
  the row's LinkedIn infographic + Instagram carousel templates into paste-ready Gemini
  image prompts, and writes the Doc link back into the row's Final Video/Post cell. Use
  this skill whenever Aleem says "run the post creator", "create the post for
  [topic/row]", "process my schedule", "next post", "make the post + image prompts for
  [row]", "generate this week's content", "turn the schedule row into a post", "automate
  my posting schedule", or names a topic that lives in the Weekly Posting Schedule. Also
  use it when he asks to research + write + log a scheduled post in one go — even if he
  doesn't say "post creator". One row at a time, with a review checkpoint before anything
  is saved.
---

# Post Creator

Connects the previously disconnected pipeline — Exa for source discovery, NotebookLM
for synthesis (matching Aleem's existing habit: sources in, detailed response out),
content-engine generation, carousel + linkedin-infographics image prompts, and the
Weekly Posting Schedule sheet — into one flow. One schedule row in, one reviewed
package out: finished post + Google Doc + Gemini image prompts + the Doc link written
back into the row.

**Scope:** text-based rows only. `Post Type = Reel` rows are skipped — that's the
`reel-creator` skill's job. Image *generation* stays manual (Aleem pastes the emitted
prompts into his Gemini Gems).

## Setup notes (read once per session)

- Python is NOT on PATH. Use the full path and UTF-8:
  `$env:PYTHONIOENCODING="utf-8"` + `C:\Users\Aleem\AppData\Local\Programs\Python\Python313\python.exe`.
- Exa, gws, and NotebookLM calls need real network — run those commands with sandbox
  disabled (`dangerouslyDisableSandbox: true`); api.exa.ai DNS fails inside the sandbox.
- If gws returns `invalid_grant` / auth errors: tell Aleem to run `gws auth login`
  (account `hassanaleem86@gmail.com`) and stop until he confirms. Never drive the browser.
- If `notebooklm` returns "Authentication expired": follow the re-auth flow in
  `.claude/skills/notebooklm/SKILL.md` and stop until Aleem confirms he's signed in.
  Run `notebooklm.exe` via PowerShell, not Bash (Python isn't on the Bash PATH).
- All scripts below live in this skill's `scripts/` folder unless another path is given.

## The flow (one row at a time)

### 1. Pick the row

- "next post" / "process my schedule" → `python scripts/schedule.py next`
- A named topic → `python scripts/schedule.py find --topic "<name>"`
- A row number → `python scripts/schedule.py get --row <N>`

The JSON gives you everything: topic, description, reference, platform, format,
`content_mode_key`, `pillars` (canonical keys), and `templates` (parsed LinkedIn +
Instagram numbers). Field semantics and the full vocab tables are in
`references/column-map.md` — read it if a value looks odd.

Guards, in order:
- `templates.errors` non-empty → show the error and ask Aleem which existing template
  to use. Don't substitute silently.
- `post_type` contains Reel → say it's a reel-creator row and pick the next row instead.
- `final_post` already filled → the row is done; confirm before overwriting anything.

### 2. Research (Exa finds sources)

```
python scripts/research.py --topic "<topic>" --description "<description>" \
    [--reference "<url-from-Reference-column>"] -o <scratchpad>/pack-<row>.json
```

Writes a source pack: the Reference URL's full text (when present) + 8-12 deep-search
sources with summaries, highlights, and full text for the top 6. If it comes back with
fewer than ~5 usable sources, retry once with a rephrased query (the topic alone, or the
description alone) before telling Aleem the topic is thin. This step only gathers URLs —
NotebookLM does the actual reading and synthesis in step 3.

### 3. Synthesize via NotebookLM (Formal + Simplified)

This mirrors Aleem's manual habit: sources go into NotebookLM, then you ask it for a
detailed response. NotebookLM fetches and embeds the full page for each source (richer
than Exa's scraped text), so route synthesis through it rather than writing summaries
from the Exa pack directly. Uses the `notebooklm` skill's CLI — see that skill's SKILL.md
for the exe path and re-auth flow if a command fails with "Authentication expired".

```powershell
$nlm = "C:\Users\Aleem\AppData\Local\Programs\Python\Python313\Scripts\notebooklm.exe"
& $nlm create "<Topic>"                        # note the returned notebook_id
& $nlm use <notebook_id>
& $nlm source add "<url 1>"                     # one call per source from the Exa pack
& $nlm source add "<url 2>"
...
& $nlm source list --json                       # wait until every source shows status "ready"
```

Then ask two questions in the same conversation (the second reuses context from the first):

```powershell
& $nlm ask "Give me a detailed, comprehensive response synthesizing all the sources on: <topic + description>. Include specific numbers, dates, architecture details, and named production users where the sources give them." --json
& $nlm ask "Rewrite that as a simplified, plain-language summary anyone can scan in under a minute. No jargon, no dense paragraphs, short lines. This will be used to write social media content, so keep it scannable and concrete with the real numbers." --json
```

The first `answer` is the **Formal Source** (feeds post generation — it typically surfaces
concrete facts Exa's raw scrape missed, since NotebookLM processes the whole page).
The second `answer` is the **Simplified Source** (feeds the image prompts). Keep both
verbatim for the Doc's Source / Source_S sections — don't re-summarize NotebookLM's output.

### 4. Generate the post(s) (in-session)

Read, if not already in context:
- `.claude/skills/content-engine/references/voice-principles.md` — voice + the 7 pillar definitions
- `.claude/skills/content-engine/references/platform-formats.md` — per-platform format specs

Then write the post for each active platform (`Platform = All` → LinkedIn and Instagram,
else just the named one), honoring:
- the row's **format** (Text Post / Carousel caption / Article / Newsletter),
- the row's **content mode** (news / opinion / story / tutorial),
- the row's **pillars** — enforce exactly the selected ones; if the cell was blank,
  use the mode's defaults from `references/column-map.md`,
- the **Formal Source** (from NotebookLM, step 3) as source material: extract what's
  useful, make it Aleem's own, never summarize the summary.

Voice guardrails that override everything: no emojis, no em dashes in body text,
no "As an AI", no agency-pitch tone — this is Aleem's personal brand feed.

### 5. Checkpoint (the one review gate)

Show Aleem: both NotebookLM summaries, the post(s), and what will happen next (Doc title,
the target row/cell, which image templates will be filled). Wait for his OK. This gate
replaces the carousel/infographic skills' internal approval gates — don't re-ask later.

### 6. Save the Google Doc (six real tabs)

Google Docs API *does* support creating tabs — `addDocumentTab` in `batchUpdate` (this
isn't in any gws help text; verified live 2026-07-08). `save_content.py` was extended to
use it: pass a `"tabs"` array instead of `"sections"` and it creates one real, independently
clickable tab per entry via `addDocumentTab` + `updateDocumentTabProperties`, in order.
Use Aleem's exact tab names: `LinkedIn` / `LinkedIn - Infographics Prompt` / `Instagram`
/ `Instagram - Carousel Prompt` / `Source` / `Source_S`. Don't put a redundant heading
inside each tab's content — the tab title already labels it (matches his reference docs,
which start the post text immediately with no heading).

Write the payload to a scratchpad JSON file, then pipe it to content-engine's saver
(creates the Doc in the "Nexis Content" Drive folder and returns `doc_url`).
Pipe with the **Bash tool** — PowerShell 5.1 re-encodes pipes with a UTF-8 BOM, which
save_content.py rejects. Also **avoid `&` in the Doc title** — it breaks the gws command
line on Windows (use "and" instead):

```bash
cat <payload>.json | python .claude/skills/content-engine/scripts/save_content.py
```

Payload shape: `{"title": "<Topic> - <Date>", "tabs": [{"title": "<tab name>", "sections": [{"body": "...", "bullets": [...]}]}, ...]}`
— one tab per name above: LinkedIn post, LinkedIn image prompt, Instagram post, Instagram
image prompt set, Formal Source (verbatim from NotebookLM), Simplified Source (verbatim).
Build the image-prompt tabs (step 7) before this call so you save once.

### 7. Fill the image prompts

Follow `references/image-prompt-fill.md`. In short: read the row's template
`input-prompt.md` from `.claude/skills/linkedin-infographics/references/LinkedIn-Template-<N>/`
and/or `.claude/skills/carousel/references/Instagram-Template-<N>/`, map the
**Simplified Source** (from NotebookLM, step 3) into the placeholders, and emit the
paste-ready prompt(s) — LinkedIn = exactly one prompt; Instagram = CONTEXT → COVER →
BODY× → CTA blocks. Include them in the Doc payload AND print them in chat in code blocks.

### 8. Write back to the sheet

```
python scripts/schedule.py write --row <N> --doc-url "<doc_url>" --status Draft
```

Confirm the cell it wrote (`final_post_cell` in the output). Then tell Aleem what's
left for him: paste the image prompts into the matching Gem (named in the template's
`gem.md`), review the Doc, publish.

### 9. Next row

Offer to continue: `schedule.py next` again. Same flow, same checkpoint. Don't batch
without being asked — if Aleem says "do the whole week", process rows sequentially
but still pause at each step-5 checkpoint unless he explicitly waives it.

## Failure honesty

Every step reports what actually happened. If the Doc save fails, the sheet write-back
must not run (a row pointing at a dead link is worse than an empty cell). If Exa returns
junk sources, say so instead of padding the summary. If a template number doesn't exist
on disk, ask — the inventories are in `references/column-map.md`.

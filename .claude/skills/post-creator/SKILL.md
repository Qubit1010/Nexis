---
name: post-creator
description: >-
  End-to-end post creation from the Weekly Posting Schedule sheet. Takes a schedule row
  (topic + description + content mode + pillars + design templates), finds 8-12 sources
  via the research skill's multi-engine deep search, loads them into a NotebookLM notebook
  and queries it for a detailed Formal source summary and a Simplified one, writes the finished
  LinkedIn/Instagram post in
  Aleem's voice using the content-engine rules, drafts a companion Instagram Shorts/Reels
  teaser sequence via the shorts-creator template, saves everything to a Google Doc, fills
  the row's LinkedIn infographic + Instagram carousel + Shorts templates into paste-ready
  Gemini image prompts, and writes the Doc link back into the row's Final Video/Post cell. Use
  this skill whenever Aleem says "run the post creator", "create the post for
  [topic/row]", "process my schedule", "next post", "make the post + image prompts for
  [row]", "generate this week's content", "turn the schedule row into a post", "automate
  my posting schedule", or names a topic that lives in the Weekly Posting Schedule. Also
  use it when he asks to research + write + log a scheduled post in one go — even if he
  doesn't say "post creator". One row at a time, with a review checkpoint before anything
  is saved.
---

# Post Creator

Connects the previously disconnected pipeline — the research skill for source discovery,
NotebookLM for synthesis (matching Aleem's existing habit: sources in, detailed response
out), content-engine generation, carousel + linkedin-infographics + shorts-creator image
prompts, and the Weekly Posting Schedule sheet — into one flow. One schedule row in, one
reviewed package out: finished post + Google Doc + Gemini image prompts (LinkedIn +
Instagram + Shorts) + the Doc link written back into the row.

**Scope:** text-based rows only. `Post Type = Reel` rows are skipped — that's the
`reel-creator` skill's job. Image *generation* stays manual (Aleem pastes the emitted
prompts into his Gemini Gems). Every processed row also gets a companion Shorts/Reels
teaser prompt set (`Instagram-Short-Template-1`, the only shorts-creator template so far) —
that generation is prompts-only too, same as the other image templates. No video is
rendered here.

## Setup notes (read once per session)

- Python is NOT on PATH. Use the full path and UTF-8:
  `$env:PYTHONIOENCODING="utf-8"` + `$env:LOCALAPPDATA\Programs\Python\Python312\python.exe`.
- Research (Exa/Tavily/Serper/Jina), gws, and NotebookLM calls need real network — run
  those commands with sandbox disabled (`dangerouslyDisableSandbox: true`); api.exa.ai
  DNS fails inside the sandbox.
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
`content_mode_key`, `ingredients` and `topical_pillars` (the Pillars cell split
across its two axes, plus `pillars_unrecognized` for anything matching neither),
and `templates` (parsed LinkedIn +
Instagram numbers). Field semantics and the full vocab tables are in
`references/column-map.md` — read it if a value looks odd.

Guards, in order:
- `templates.errors` non-empty → show the error and ask Aleem which existing template
  to use. Don't substitute silently.
- `post_type` contains Reel → say it's a reel-creator row and pick the next row instead.
- `final_post` already filled → the row is done; confirm before overwriting anything.

### 1b. Gate the row before spending research on it

Three questions against `agency/personal-brand-content-engine.md`, run **before** step 2.
Researching a level-2 topic only produces a well-researched level-2 post, and research is
the expensive step.

1. **Ladder check.** Is the row a tool announcement, a news relay, a neutral tutorial, or an
   "N ways to" listicle? Those are ladder levels 1-4, which `agency/personal-brand-voice.md`
   marks FORBIDDEN. **75 of the 197 themed rows already published failed this**, so treat it
   as a real filter, not a formality.
2. **First-person check.** Can this row carry a first-person claim with a real number or a
   named moment in its first two lines? That single variable separates the strongest posts in
   the log from the weakest. If the honest answer is no, the topic is not his to write yet.
3. **Pillar check.** Which of the 4 topical pillars in `agency/personal-brand-pillars.md` does
   it serve? Founder Journey and Young Builder sit at roughly zero across 199 rows, and both
   are Conversion-intent.

**A failing row gets rescued, not written and not silently skipped.** Propose the rescue and
get Aleem's call before continuing. Most rows rescue on the same move: add what happened when
*he* used the thing, and what he got wrong first. "Here is what OmniVoice does" fails; "I
replaced my voiceover step with OmniVoice and the first three takes were unusable, here is
what I had misconfigured" passes, on the same topic and the same research.

If `Content Mode` or `Pillars` is blank, decide the values here. They get written back in
step 8 along with the Doc URL, so the decision has to be made before the row is processed,
not after. `Pillars` takes the **4 topical pillars**, not the 7 ingredients; `schedule.py`
rejects an ingredient label on that column rather than writing it, because a cell filled
with the wrong axis looks filled while leaving the mix unmeasurable.

### 2. Research (the research skill finds sources)

```
python scripts/research.py --topic "<topic>" --description "<description>" \
    [--reference "<url-from-Reference-column>"] -o <scratchpad>/pack-<row>.json
```

This delegates to `.claude/skills/research/scripts/research.py` in deep mode (Exa +
Tavily + Serper + Jina, fused and ranked by cross-source agreement) instead of Exa alone.
Writes a source pack: the Reference URL's full text (when present) + up to 12 fused
sources with snippets, the engines that agreed on each URL, and full text for the top
ones. If it comes back with fewer than ~5 usable sources, retry once with a rephrased
query (the topic alone, or the description alone) before telling Aleem the topic is thin.
This step only gathers URLs — NotebookLM does the actual reading and synthesis in step 3.

### 3. Synthesize via NotebookLM (Formal + Simplified)

This mirrors Aleem's manual habit: sources go into NotebookLM, then you ask it for a
detailed response. NotebookLM fetches and embeds the full page for each source (richer
than Exa's scraped text), so route synthesis through it rather than writing summaries
from the Exa pack directly. Uses the `notebooklm` skill's CLI — see that skill's SKILL.md
for the exe path and re-auth flow if a command fails with "Authentication expired".

```powershell
$nlm = "$env:LOCALAPPDATA\Programs\Python\Python312\Scripts\notebooklm.exe"
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
- `agency/personal-brand-content-engine.md` — **the spec.** Hook patterns P1-P6 with the post
  that proves each one, the format set, the copywriting rules, and the target pillar mix
- `agency/personal-brand-voice.md` — voice, and the 7 Unswappable **ingredients** every piece must contain
- `agency/personal-brand-pillars.md` — the 4 **topical pillars** a piece is about. These are a different axis from the ingredients above; do not substitute one for the other
- `.claude/skills/content-engine/references/platform-formats.md` — per-platform format specs

Then write the post for each active platform (`Platform = All` → LinkedIn and Instagram,
else just the named one), honoring:
- the row's **format** (Text Post / Carousel caption / Article / Newsletter),
- the row's **content mode** (news / opinion / story / tutorial),
- the row's **topical pillar** from step 1b, which is what the piece is about,
- the **ingredients** to weave in: the row's own if the cell named any, otherwise the
  content mode's defaults in `references/column-map.md`. At least two, always,
- the **Formal Source** (from NotebookLM, step 3) as source material: extract what's
  useful, make it Aleem's own, never summarize the summary.

**Write for a business reader, not an engineer.** Plain language beats precise jargon:
"the budget you set for the answer" not `max_tokens`, "steps" not "tool calls", "it
refuses" not "returns a 400". Keep every real number — the specificity rule still holds.
Technical detail belongs in the infographic, where a reader who wants it is already
leaning in.

**When the row's Reference names one of Aleem's own skills, the post must say how he
uses it.** A reference like `Content-Engine-Skill`, `Weekly Business Review skill`, or
`claude advisor` is not just a citation, it is the lived-experience anchor (Pillar 1):
he built the thing and runs it. Name it and show it working ("I run it through a content
engine I built, which takes the anchor and produces the platform versions"). Never
reduce it to a passive mention. If the reference is a skill used only to *source* the
post rather than as its subject (e.g. `research-skill` on a news row), skip it — that's
plumbing, not story.

Voice guardrails that override everything: no emojis, no em dashes in body text,
no "As an AI", no agency-pitch tone — this is Aleem's personal brand feed.

Also draft the companion **Shorts/Reels teaser copy** (shorts-creator's Step 2, light —
no fresh research): eyebrow label, cover headline + subtitle, 1-2 content frame lines,
and CTA text, derived from the **Simplified Source** (step 3) and the row's description.
It's a teaser, not the post repeated — keep every line short and punchy. Shorts always
carry NexusPoint branding (logo, dark diagonal-stripe motif) even though the post above
is personal-brand voice — that's shorts-creator's own deliberate, scoped exception to the
no-agency-mention rule, and it still applies here.

### 5. Checkpoint (the one review gate)

Show Aleem: both NotebookLM summaries, the post(s), the drafted Shorts copy (eyebrow /
headline / subtitle / content line(s) / CTA), and what will happen next (Doc title, the
target row/cell, which image templates will be filled). Wait for his OK. This gate
replaces the carousel/infographic/shorts-creator skills' internal approval gates — don't
re-ask later.

### 6. Save the Google Doc (seven real tabs)

Google Docs API *does* support creating tabs — `addDocumentTab` in `batchUpdate` (this
isn't in any gws help text; verified live 2026-07-08). `save_content.py` was extended to
use it: pass a `"tabs"` array instead of `"sections"` and it creates one real, independently
clickable tab per entry via `addDocumentTab` + `updateDocumentTabProperties`, in order.
Use Aleem's exact tab names: `LinkedIn` / `LinkedIn - Infographics Prompt` / `Instagram`
/ `Instagram - Carousel Prompt` / `Shorts - Image Prompt` / `Source` / `Source_S`. Don't
put a redundant heading inside each tab's content — the tab title already labels it
(matches his reference docs, which start the post text immediately with no heading).

Write the payload to a scratchpad JSON file, then pipe it to content-engine's saver
(creates the Doc in the "Nexis Content" Drive folder and returns `doc_url`).
Pipe with the **Bash tool** — PowerShell 5.1 re-encodes pipes with a UTF-8 BOM, which
save_content.py rejects. Also **avoid `&` in the Doc title** — it breaks the gws command
line on Windows (use "and" instead):

```bash
cat <payload>.json | python tools/gdocs/save_content.py
```

Payload shape: `{"title": "<Topic> - <Date>", "tabs": [{"title": "<tab name>", "sections": [{"body": "...", "bullets": [...]}]}, ...]}`
— one tab per name above: LinkedIn post, LinkedIn image prompt, Instagram post, Instagram
image prompt set, Shorts image prompt set, Formal Source (verbatim from NotebookLM),
Simplified Source (verbatim). Build the image-prompt tabs (step 7) before this call so
you save once.

### 7. Fill the image prompts

Follow `references/image-prompt-fill.md`. In short: read the row's template
`input-prompt.md` from `.claude/skills/linkedin-infographics/references/LinkedIn-Template-<N>/`,
`.claude/skills/carousel/references/Instagram-Template-<N>/`, and
`.claude/skills/shorts-creator/references/Instagram-Short-Template-1/input-prompt.md`,
map the **Simplified Source** (from NotebookLM, step 3) and the approved Shorts copy
(step 4) into the placeholders, and emit the paste-ready prompts — LinkedIn = exactly one
prompt; Instagram = CONTEXT → COVER → BODY× → CTA blocks; Shorts = CONTEXT → COVER →
CONTENT× (1-2) → CTA blocks, 1080x1920 (9:16). Include them all in the Doc payload AND
print them in chat in code blocks.

### 8. Write back to the sheet

```
python scripts/schedule.py write --row <N> --doc-url "<doc_url>" --status Draft \
    [--pillars "Founder Journey"] [--content-mode "Personal Story"]
```

Pass `--pillars` and `--content-mode` whenever step 1b had to decide them, so the row
carries the classification the mix is measured from. Both are validated before anything
is written, so a bad label fails the whole write instead of half-filling the row.

Confirm the cells it wrote (`final_post_cell`, and `pillars_cell` / `content_mode_cell`
when those were passed). Then tell Aleem what's
left for him: paste the image prompts into the matching Gem (named in the template's
`gem.md`), review the Doc, publish.

### 9. Next row

Offer to continue: `schedule.py next` again. Same flow, same checkpoint. Don't batch
without being asked — if Aleem says "do the whole week", process rows sequentially
but still pause at each step-5 checkpoint unless he explicitly waives it.

## Failure honesty

Every step reports what actually happened. If the Doc save fails, the sheet write-back
must not run (a row pointing at a dead link is worse than an empty cell). If research
returns junk sources, say so instead of padding the summary. If a template number doesn't
exist on disk, ask — the inventories are in `references/column-map.md`.

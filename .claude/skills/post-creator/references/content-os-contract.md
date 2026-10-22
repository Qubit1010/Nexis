# post-creator under Content OS

Content OS (`projects/content-os/`) runs this skill headless, one LinkedIn post per run. Its
prompt names a run folder and passes the schedule row as a JSON brief instead of a sheet row.
When a prompt says it comes from Content OS, follow this file wherever it differs from SKILL.md.

| SKILL.md step | Under Content OS |
|---|---|
| Setup (Python 3.12 path, gws auth, NotebookLM re-auth) | Use `python` on PATH. Never call gws. NotebookLM is not installed on this machine. |
| 1. Pick the row | Skipped. The brief in `input.json` is the row. |
| 1b. Gate | Run it. A failing row is **rescued by you**, not escalated: write the rescued angle, set `gate` honestly, and explain the rescue in `notes_for_reviewer`. Use `status: "blocked"` only when the rescue needs a fact only Aleem has (what happened when he used the thing). |
| 2. Research | Run `scripts/research.py` with `-o <run folder>/pack.json`. |
| 3. NotebookLM | Replaced: write `source-formal.md` and `source-simple.md` yourself from the pack, same intent (formal = detailed with every real number; simple = scannable). |
| 4. Generate | LinkedIn only unless the brief says otherwise. No Instagram version, no Shorts copy. `post.md` is the exact paste text. |
| 5. Checkpoint | Skipped. The Content OS review screen is the checkpoint. |
| 6. Save the Doc | Skipped. Content OS exports a Doc on request. |
| 7. Image prompts | LinkedIn infographic only, to `infographic-prompt.md` (the prompt alone; concept notes go in `meta.infographic`). Do not append linkedin-infographic-studio's `concept-ledger.md` or save to a scratchpad; put the ledger row in `notes_for_reviewer`. |
| 8. Write back to the sheet | Skipped. Content OS owns the schedule and mirrors it to the sheet. |

Finish by writing `output.json` exactly as the appended Content OS contract describes.

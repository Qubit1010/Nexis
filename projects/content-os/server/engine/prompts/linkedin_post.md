Use the **post-creator** skill (`.claude/skills/post-creator/SKILL.md`) to write one LinkedIn post,
following its Content OS contract in `.claude/skills/post-creator/references/content-os-contract.md`.

Run folder: `{{RUN_DIR}}`
Item brief (also saved as `{{RUN_DIR}}/input.json`):

```json
{{INPUT_JSON}}
```

Do, in order:

1. Step 1b gate (ladder, first-person, pillar) against the brief. Decide Content Mode and the
   topical Pillar if the brief leaves them blank or the pillar is not one of the 4 topical
   pillars (imported rows often hold ingredient labels such as "Practical Stakes" there).
   Imported briefs can have fields swapped: treat any URL in `description` as the reference.
2. Step 2 research: `python .claude/skills/post-creator/scripts/research.py --topic "..." --description "..." [--reference "..."] -o "{{RUN_DIR}}/pack.json"`.
   Retry once with a rephrased query if fewer than about 5 usable sources come back.
3. Step 3 synthesis without NotebookLM: write `source-formal.md` and `source-simple.md` in the run
   folder from the pack.
4. Step 4: write the LinkedIn post only (no Instagram version, no Shorts copy) to `post.md`. Plain
   text exactly as it will be pasted into LinkedIn: no markdown headings, no bold, under 3,000
   characters, short paragraphs.
5. Step 7, LinkedIn only: the infographic prompt via linkedin-infographic-studio's headless mode
   (or the numbered template if the brief names one) to `infographic-prompt.md`. That file holds
   only the paste-ready prompt (it is linted as a whole); put the concept line, runner-up concepts
   and colour mode in `meta.infographic` instead.

`meta` must include: `hook` (the first two lines), `char_count`, `pillar`, `content_mode`,
`ingredients` (array), `hashtags` (array, may be empty).
`files.extra`: `infographic-prompt.md`, `source-formal.md`, `source-simple.md`.

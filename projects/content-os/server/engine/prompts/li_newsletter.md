Use the **linkedin-newsletter** skill (`.claude/skills/linkedin-newsletter/SKILL.md`) to write one
issue, following its Content OS contract in
`.claude/skills/linkedin-newsletter/references/content-os-contract.md`.

Edition: **{{EDITION}}** ({{CHANNEL_NAME}}).
{{EDITION_RULES}}

Run folder: `{{RUN_DIR}}`
Item brief (also saved as `{{RUN_DIR}}/input.json`):

```json
{{INPUT_JSON}}
```

Source: {{SOURCE_LINE}}

Write the issue to `issue.md` in the run folder, following
`.claude/skills/linkedin-newsletter/references/issue-format.md` (it must end with the
`<!-- end issue -->` marker, with the publishing notes below it). Then run the checker and fix every
failure:

```
python .claude/skills/linkedin-newsletter/scripts/check_issue.py "{{RUN_DIR}}/issue.md" --edition {{EDITION}}{{SOURCE_URL_ARG}}
```

Do not convert to a Doc, upload anything, or append to the issue log.

`files.main` is `issue.md`. `meta` must include: `issue_title`, `word_count`, `share_text` (the
short text for sharing the issue as a post), `cover_note` (what the cover image should show),
`check_passed` (boolean from the checker).

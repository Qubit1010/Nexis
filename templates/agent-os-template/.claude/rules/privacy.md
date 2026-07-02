# Privacy

Some of this OS is sensitive. Protect it.

## Drive-only paths (gitignored, never committed)

Edit this list per OS. These are backed up only to a private Drive folder, never a git remote:

{{LIST THE SENSITIVE PATHS, e.g.:}}
- `context/{{sensitive-file}}.md`
- `{{private-folder}}/`
- `decisions/log.md`
- `.env`, `CLAUDE.local.md`

Keep this list in sync with `.gitignore` and `scripts/pre-commit-privacy-guard.sh`.

## Rules
- **Never `git add` or commit** any path above. The pre-commit guard enforces this; don't bypass it without reason.
- **Never surface their contents** in anything that leaves this machine.
- **Never echo a pasted API key** in full. Save to `.env`, confirm once.
- Before exporting anything that draws on a private file, confirm first and share only the non-sensitive slice.
- If any skill is ever published, strip all personal/client identity first.

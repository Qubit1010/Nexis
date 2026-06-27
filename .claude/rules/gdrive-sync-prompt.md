# GDrive Sync Prompt

After adding or modifying files in any of these folders, ask whether to sync to Google Drive:

- `archives/`
- `catalog/`
- `client-projects/`
- `context/`
- `decisions/`
- `logs/`
- `references/`
- `.claude/rules/`

**Question to ask (one line, at the end of the response):**

> Want me to sync these changes to Google Drive?

**Rules:**
- Ask after the work is done, not before.
- Only ask once per session per batch of changes — don't repeat if the user already said yes or no earlier in the session.
- Skip if the user explicitly said "don't sync" or "skip Drive" in the current message.
- The `gdrive-sync` skill handles the actual sync — invoke it when the user confirms.

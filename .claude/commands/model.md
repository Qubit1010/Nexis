---
description: Switch the active model config (glm / open-models / default) and apply it to .claude/settings.local.json
argument-hint: glm | open-models | default | (empty to show current)
allowed-tools: Bash
---

Switch the active Claude Code model configuration.

## What to do

1. Read the argument: `$ARGUMENTS`. Strip whitespace. If empty, set `target=""` (meaning "show status only").
2. Run the switcher script from the project root, passing the argument through:

   - If a target was given: `powershell -NoProfile -ExecutionPolicy Bypass -File .claude/switch-model.ps1 <target>`
   - If no target: `powershell -NoProfile -ExecutionPolicy Bypass -File .claude/switch-model.ps1`

3. Report the script's output verbatim to the user. Do not paraphrase — the script already prints the active model, available configs, and the restart reminder.
4. If the user gave a target that isn't one of the available configs, the script will say so — relay that and stop. Do not guess or create new configs.
5. Remind the user once at the end: **restart Claude Code (or reload the window) for the new model env vars to take effect**, since settings.local.json is read only at startup.

## Notes

- This command does NOT restart anything itself — it only merges the chosen config's env keys into the active `.claude/settings.local.json`.
- Permissions, additionalDirectories, and all non-model env vars (API keys, etc.) are always preserved.
- Stored configs live in `.claude/<name>/settings.local.json`. The active file is always `.claude/settings.local.json`.
- Never edit `settings.local.json` directly here — always go through the script so the source-of-truth copies in `.claude/<name>/` stay in sync.

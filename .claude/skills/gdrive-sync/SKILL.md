---
name: gdrive-sync
description: >
  Syncs Nexis private/gitignored folders to Google Drive as a permanent backup,
  with two-way awareness: pushes local changes up, detects Drive-only or Drive-newer
  files, and asks before pulling them down. Invoke whenever the user says anything
  like: "sync to Drive", "back up to Drive", "push context to Drive", "sync
  client-projects", "back up my decisions", "check Drive for new files", "gdrive
  sync", "set up Drive sync", "set up weekly sync", "is there anything on Drive
  I'm missing", "pull from Drive", "what's new on Drive", "gdrive sync setup".
  Also invoke after the user adds files to archives/, catalog/, client-projects/,
  context/, decisions/, logs/, or references/ and the gdrive-sync-prompt rule fires.
---

# GDrive Sync

Two-way sync between Nexis private folders and **Work / Nexis Business Context** on Google Drive.

## Synced folders

| Local | Drive |
|-------|-------|
| `archives/` | Nexis Business Context/archives/ |
| `catalog/` | Nexis Business Context/catalog/ |
| `client-projects/` | Nexis Business Context/client-projects/ |
| `context/` | Nexis Business Context/context/ |
| `decisions/` | Nexis Business Context/decisions/ |
| `docs/` | Nexis Business Context/docs/ |
| `logs/` | Nexis Business Context/logs/ |
| `references/` | Nexis Business Context/references/ |
| `.claude/rules/` | Nexis Business Context/.claude/rules/ |

Drive is a **permanent backup** — files are never deleted from Drive, even if removed locally.

---

## Modes

| Mode | Command | When to use |
|------|---------|-------------|
| Push all | `python sync.py --push` | Default — upload new/changed local files |
| Push one folder | `python sync.py --push --folder context` | After touching a specific folder |
| Check (two-way) | `python sync.py --check` | Scan Drive for files missing/newer locally |
| Full two-way | `python sync.py --push --check` | Comprehensive sync + pull review |
| Dry run | `python sync.py --push --dry-run` | Preview without uploading |
| Setup | `python sync.py --setup` | First-time: creates Drive folder structure |

All commands run from: `.claude/skills/gdrive-sync/scripts/`

---

## First-time setup

Run once to create the Drive folder structure:

```powershell
cd .claude/skills/gdrive-sync/scripts
python sync.py --setup
```

This creates `Work / Nexis Business Context / {folder}` on Drive and saves folder IDs to `folder_ids.json`. Requires `gws auth login` to be authenticated first.

If `folder_ids.json` doesn't exist yet, always run `--setup` before any push or check.

---

## Auth

The script reuses the existing GWS OAuth token — no separate login needed as long as `gws auth login` has been run. It checks these locations in order:

1. `%APPDATA%\gws\token.json`
2. `~\.gws\token.json`
3. `~\.config\gws\token.json`
4. `.claude/skills/gdrive-sync/scripts/gdrive_token.json` (standalone fallback)

If all fail: tell the user to run `gws auth login` and retry.

---

## Weekly scheduled sync

To set up a weekly auto-push via Windows Task Scheduler, run:

```powershell
python sync.py --schedule-weekly
```

This registers a Task Scheduler job (`NexisGDriveSync`) that runs every Sunday at 9am and pushes all folders to Drive silently. To remove it: `python sync.py --unschedule`.

---

## Claude's decision flow

When this skill triggers:

1. **Check if setup is done** — does `scripts/folder_ids.json` exist?
   - No → run `python sync.py --setup` first, then proceed
   - Yes → proceed

2. **Determine intent**:
   - "sync", "push", "back up" → run `--push` (all folders unless user specified one)
   - "check", "what's on Drive", "pull", "anything new" → run `--check`
   - "full sync" / "two-way" → run `--push --check`
   - "weekly sync", "schedule" → run `--schedule-weekly`
   - "setup" → run `--setup`

3. **Run the command** via PowerShell from `scripts/`:
   ```powershell
   cd .claude/skills/gdrive-sync/scripts; python sync.py --push
   ```

4. **Report the output** — always state the result explicitly, don't just show the command:
   - Push: parse the script stdout and say "Synced X files (Y new, Z updated, W skipped)". If the command hasn't run yet, say "Running push — will report counts once complete."
   - Check: List any Drive-only or Drive-newer files explicitly, then ask "Want me to pull these locally?"
   - Schedule: Confirm "NexisGDriveSync task registered — runs every Sunday at 9am. Use `python sync.py --unschedule` to remove it."
   - If pull requested: run `python sync.py --pull --files "path1,path2"`

5. **On auth error**: tell the user to run `gws auth login`, wait for confirmation, then retry.

---

## Requirements

```
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv
```

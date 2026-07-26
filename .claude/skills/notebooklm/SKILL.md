---
name: notebooklm
description: Complete API for Google NotebookLM - full programmatic access including features not in the web UI. Create notebooks, add sources, generate all artifact types, download in multiple formats. Activates on explicit /notebooklm or intent like "create a podcast about X", "list my notebooks", "add this URL to NotebookLM", "generate a quiz from my research", "summarize these documents", "create flashcards for studying", "generate a report", "make a mind map", "add these sources to NotebookLM", "turn this into an audio overview"
---

# NotebookLM Skill

Full programmatic access to Google NotebookLM via the `notebooklm-py` CLI (v0.7.1). Installed system-wide on this machine.

## Setup (Already Done)

- **CLI:** `$env:LOCALAPPDATA\Programs\Python\Python312\Scripts\notebooklm.exe`
- **Auth:** `$env:USERPROFILE\.notebooklm\profiles\default\storage_state.json`
- **Invoke via PowerShell:** `& "$env:LOCALAPPDATA\Programs\Python\Python312\Scripts\notebooklm.exe" <command>`

Always run notebooklm commands via PowerShell, not Bash (Python is not on the Bash PATH).

## Re-Authentication (When Session Expires)

`notebooklm list` will fail with "Authentication expired". `scripts/relogin.py` handles it.

**Step 1** — Open the browser. This MUST be a background task (`run_in_background: true`);
a foreground call is torn down when it returns and kills the browser with it:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -u `
  .claude\skills\notebooklm\scripts\relogin.py open
```

Tell user: "A Chromium window is open at notebooklm.google.com. Sign in and tell me when
you're on the homepage." Note the window title is **Google Chrome for Testing** — signing
into their normal Chrome does nothing, since this profile is isolated.

**Step 2** — Once the user confirms, close the browser and capture the session. The
sign-in persists in the profile on disk, so capture is a separate run:

```powershell
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.CommandLine -like "*relogin.py*" } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Start-Sleep -Seconds 3
Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" |
  Where-Object { $_.CommandLine -like "*notebooklm*browser_profile*" } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Start-Sleep -Seconds 3
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -u `
  .claude\skills\notebooklm\scripts\relogin.py capture
```

Both kills are needed: the browser must release the profile lock before `capture` can
reopen it.

**Step 3** — Verify:

```powershell
$out = & "$env:LOCALAPPDATA\Programs\Python\Python312\Scripts\notebooklm.exe" list --json
"exit=$LASTEXITCODE"; ($out | ConvertFrom-Json).Count
```

Use `--json` to check. The plain `list` renders a table but exits 255 through PowerShell
(native-stderr quirk), which reads as a failure when it isn't.

**Do not** verify sign-in by watching the URL from inside the open browser. NotebookLM
redirects through several hostnames and can settle on a Gemini-branded title, so a naive
`"notebooklm.google.com" in url` check misses a completed login. Ask the user instead.

## Autonomy Rules

**Run automatically (no confirmation):**
- `auth check` — diagnose auth
- `list` — list notebooks
- `use <id>` — set context
- `status` — show context
- `source list` — list sources
- `source add` — add sources
- `artifact list` — list artifacts
- `ask "..."` — chat (without --save-as-note)
- `history` — read-only
- `create` — create notebook
- `language list/get/set`

**Ask before running:**
- `delete` — destructive
- `generate *` — long-running, may hit rate limits
- `download *` — writes to filesystem
- `ask "..." --save-as-note` — writes a note
- `history --save` — writes a note
- `artifact wait` / `source wait` (in main conversation — long-running)

## Quick Reference

| Task | Command |
|------|---------|
| List notebooks | `notebooklm list` |
| Create notebook | `notebooklm create "Title"` |
| Set context | `notebooklm use <notebook_id>` |
| Show context | `notebooklm status` |
| Add URL source | `notebooklm source add "https://..."` |
| Add YouTube | `notebooklm source add "https://youtube.com/..."` |
| Add local file | `notebooklm source add ./file.pdf` |
| List sources | `notebooklm source list` |
| Web research (fast) | `notebooklm source add-research "query"` |
| Web research (deep) | `notebooklm source add-research "query" --mode deep --no-wait` |
| Chat | `notebooklm ask "question"` |
| Chat + save as note | `notebooklm ask "question" --save-as-note` |
| Show history | `notebooklm history` |
| Generate podcast | `notebooklm generate audio "instructions"` |
| Generate video | `notebooklm generate video "instructions"` |
| Generate report | `notebooklm generate report --format briefing-doc` |
| Generate quiz | `notebooklm generate quiz` |
| Generate flashcards | `notebooklm generate flashcards` |
| Generate mind map | `notebooklm generate mind-map` |
| Generate infographic | `notebooklm generate infographic` |
| Generate slide deck | `notebooklm generate slide-deck` |
| Check artifact status | `notebooklm artifact list` |
| Download audio | `notebooklm download audio ./output.mp3` |
| Download video | `notebooklm download video ./output.mp4` |
| Download report | `notebooklm download report ./report.md` |
| Download quiz (JSON) | `notebooklm download quiz quiz.json` |
| Download flashcards | `notebooklm download flashcards cards.json` |
| Download mind map | `notebooklm download mind-map ./map.json` |
| Download slides (PDF) | `notebooklm download slide-deck ./slides.pdf` |
| Download slides (PPTX) | `notebooklm download slide-deck ./slides.pptx --format pptx` |
| Check auth | `notebooklm auth check` |
| List languages | `notebooklm language list` |
| Set language | `notebooklm language set en` |

## Generation Types

All generate commands support `-s <source_id>` (specific sources), `--language`, `--json`, `--retry N`.

| Type | Format options | Download |
|------|---------------|----------|
| Podcast | `deep-dive`, `brief`, `critique`, `debate` | .mp3 |
| Video | `explainer`, `brief` | .mp4 |
| Report | `briefing-doc`, `study-guide`, `blog-post`, `custom` | .md |
| Quiz | `--difficulty easy/medium/hard` | .json / .md |
| Flashcards | `--difficulty easy/medium/hard` | .json / .md |
| Infographic | `--orientation landscape/portrait/square` | .png |
| Slide Deck | `detailed`, `presenter` | .pdf / .pptx |
| Mind Map | *(sync, instant)* | .json |

## Common Workflows

### Research to Podcast
1. `notebooklm create "Research: [topic]"`
2. `notebooklm source add "https://..."` for each source
3. Wait: check `notebooklm source list --json` until all status=ready
4. `notebooklm generate audio "Focus on [angle]"` (confirm first)
5. Note the artifact ID returned
6. `notebooklm artifact list` to check status later
7. `notebooklm download audio ./podcast.mp3` when complete

### Document/Video Analysis
1. `notebooklm create "Analysis: [project]"`
2. `notebooklm source add ./doc.pdf` or YouTube URL
3. `notebooklm ask "Summarize the key points"`

### Quick Quiz from Sources
1. Set context: `notebooklm use <id>`
2. `notebooklm generate quiz --difficulty medium`
3. `notebooklm download quiz quiz.md --format markdown`

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| "Authentication expired" | Session stale | Run re-auth workflow above |
| "No notebook context" | Context not set | `notebooklm use <id>` |
| Rate limiting / GENERATION_FAILED | Google throttle | Wait 5-10 min, retry |
| Download fails | Generation not complete | Check `artifact list` status |

## Processing Times

| Operation | Typical time |
|-----------|-------------|
| Source processing | 30s – 2 min |
| Mind map / report | Instant – 2 min |
| Quiz / flashcards | 5 – 15 min |
| Podcast (audio) | 10 – 20 min |
| Video | 15 – 45 min |

For long-running generations: start with `--json`, capture the artifact ID, and tell the user to check back. Don't block the conversation waiting.

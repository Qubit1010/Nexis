# Setup & troubleshooting

`scripts/preflight.mjs` automates this; read here when preflight reports a problem or you're
setting up on a new machine.

## The dedicated CDP Chrome (the important gotcha)

The script attaches `playwright-cli` to a Chrome exposing a CDP endpoint on `:9222`. The
**non-obvious trap**: Chrome's in-browser toggle at `chrome://inspect/#remote-debugging`
("Allow remote debugging for this browser instance") exposes a **WebSocket-only** endpoint
with no `/json` discovery API. Playwright connects to the WS but then **hangs enumerating
contexts and times out** — so that toggle does NOT work here.

You must start Chrome with the real launch flag:

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --remote-debugging-port=9222 `
  --user-data-dir="C:\Users\Aleem\fb-automation-profile" `
  --no-first-run --no-default-browser-check https://www.facebook.com
```

Why a **dedicated** `--user-data-dir` (not the main profile): you can't attach to your normal
Chrome without restarting it (closing all your windows), and a separate profile keeps the
automation away from your day-to-day browsing. It persists, so you log into Facebook in it
**once**. Verify CDP is live: open <http://localhost:9222/json/version> — it should return
JSON (`{"Browser":"Chrome/…"}`). `preflight.mjs` launches this for you if `:9222` is down.

Override the profile path with `--profile` or `FB_AUTOMATION_PROFILE`.

## gws (Google Workspace CLI) auth

The script reads/writes the sheet via `gws`. Check with `gws auth status` (`token_valid:
true`). If the refresh token is expired/revoked you'll see `401 / Token has been expired or
revoked` — re-auth interactively:

```bash
gws auth login            # prints an OAuth URL; open it, sign in as hassanaleem86@gmail.com,
                          # approve all scopes. A localhost listener catches the redirect.
```

Then confirm: `gws sheets +read --spreadsheet <id> --range "Sheet1!A1:A3"`.

## Facebook checkpoints

A fresh dedicated profile logging into Facebook may trigger a "Someone tried to log in" /
approve-login checkpoint (same machine/IP keeps risk low). Approve it once; the session then
persists in the profile. If Facebook starts showing security challenges mid-run, stop, slow
down (raise `--delay-min/--delay-max`), and reduce `--limit`.

## Common failures

| Symptom | Cause | Fix |
|---|---|---|
| attach hangs ~30s then "Timeout exceeded" | using the `chrome://inspect` toggle, not the launch flag | start Chrome with `--remote-debugging-port` (preflight does this) |
| `/json/version` → 404 | same toggle issue (WS-only endpoint) | same as above |
| `401 Failed to get token` on sheet read | gws token expired | `gws auth login` |
| many rows "NEEDS REVIEW (author: …)" | posts not fully rendered, or heavy obfuscation | raise the settle wait; confirm you're logged in; spot-check a post by hand |
| resolver returns `### Error … setTimeout is not defined` | used `setTimeout` in run-code context | use `page.waitForTimeout(ms)` |
| writes nothing on a fresh sheet | `Profile URL` column already filled, or column A not post links | check column A is `/groups/.../posts/...`; use `--start-row` |

## Rate limiting

Defaults: ≤15–20 posts/run, 3–8s randomized between posts, real logged-in session. These
exist to stay under Facebook's automation detection — don't strip them. For a big backlog,
run several small batches across the day rather than one large run.

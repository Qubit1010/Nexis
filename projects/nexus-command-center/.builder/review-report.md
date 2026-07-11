---
project: NexusCommandCenter
phase: review
created: 2026-07-10T20:15:00Z
verdict: PASS
---

# Review Report — NexusCommandCenter

## Contract verification (architecture.md §6, both sides)

| Check | Result |
|---|---|
| GET /api/graph serves scanner output; 404 GRAPH_MISSING when absent | PASS (live curl + code path) |
| GET /api/vitals: counts, last_sync (real brain-sync.log line), last_vault_commit (real git), spend | PASS (live curl showed real data) |
| GET /api/commands: id/label/description only — prompts never reach the client | PASS (tested) |
| POST /api/command: 400 UNCONFIRMED / 400 UNKNOWN_COMMAND / 202 / 409 / 423 | PASS (tested) |
| GET /api/command/status + POST /api/command/ack | PASS (tested) |
| Frontend api.ts types match server responses field-for-field | PASS (typecheck + live render) |
| Server binds 127.0.0.1 only | PASS (index.ts hostname) |

## Guardrails (blueprint §5 hard requirements, tested)

1. Preset-only: prompt text never from/to client — **tested**
2. Mutex: concurrent POST → 409 — **tested** (fake CLI)
3. Scoped spawn: cwd=runs/workspace, generated settings file, stdin prompt (nothing user-controlled in argv) — code-reviewed
4. Allowlist Read/Glob/Grep/Write(./**), deny Bash/WebFetch/secret patterns + PreToolUse hook-guard — **hook tested** (blocks .env, .ssh, client-projects, Bash, destructive patterns; allows normal reads)
5. 5-min timeout → `taskkill /T /F` child tree — code-reviewed (Windows path)
6. $0.50 ceiling → 423 lock until /ack — **tested**
7. Results → `<vault>/raw/command-center/`, audit → runs/log.jsonl — **tested** (temp vault)

## Fix-loop findings (all fixed)

1. `HttpError` used TS parameter properties — crashes Node strip-only mode → explicit fields.
2. `finish()` could fire twice ('error' + 'close' on failed spawn) → `finished` guard.
3. Failed spawn could emit unhandled stdin EPIPE → swallow handler.
4. Tests polluted the real `runs/log.jsonl` (vitals showed fake spend) → `NCC_RUNS_DIR` seam + temp dirs.
5. Hono `app.request` return type mismatch in test helper → `Promise.resolve` wrap.
6. Vault graphify islands scattered as disconnected dust → union-find component anchoring to `vault:__hub__` + root bridge.

## Evidence

- `npx tsc --noEmit` — clean.
- `npm test` — node:test 5/5 pass + `scanner selftest: OK`.
- `vite build` — clean (405 kB bundle, 131 kB gz).
- Live smoke: all 6 routes + SPA over 127.0.0.1:4400 with real data (256 nodes / 303 edges).
- Headless visual QA (gstack browse): zero console errors; screenshot confirms HUD chrome, vitals, single connected constellation, legend chips, deck presets. `C:/Users/qubit/AppData/Local/Temp/ncc-shot3.png`.

## Ponytail notes

- No react-query, no SSE, no DB, no state lib beyond one zustand store — YAGNI held.
- Sigma.js WebGL remains the documented >3k-node upgrade path only.
- Known ceilings marked in code (`ponytail:` comments): type-based coloring, member-link hubs.

## Not done (deliberate)

- Playwright UI-interaction suite (node click → panel) — manual visual QA covered the render path; add if the UI grows.
- Live `claude -p` run from the deck — wiring is fully tested against the fake CLI; first real click costs money and is Aleem's to fire.
- Aurora/graph perf profiling at >1k nodes — current n=256, budget documented.

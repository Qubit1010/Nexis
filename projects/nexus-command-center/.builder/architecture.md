---
project: NexusCommandCenter
complexity: standard
tech_stack:
  frontend: "Vite 6 + React 19 + TypeScript SPA, react-force-graph-2d, zustand, Tailwind v4 + brand CSS custom props"
  backend: "Hono on Node 20+ (serves SPA + API), child_process spawn of claude CLI"
  database: "none — filesystem (data/system-graph.json, runs/log.jsonl)"
  auth: "none — binds 127.0.0.1 only"
  hosting: "localhost (npm start)"
created: 2026-07-10T15:55:00Z
source_blueprint: .builder/blueprint.md
---

# NexusCommandCenter — Architecture Spec

## 1. Overview

A local, branded command center for the Nexis agency OS: one screen rendering the whole system (skills, projects, rules, context, decisions, second-brain wiki) as an interactive force-directed knowledge graph, with vitals, a searchable catalog, and a guarded command deck that fires headless `claude -p` runs. Single user (Aleem), Windows, localhost; doubles as a client showcase.

## 2. Complexity Assessment

| Dimension | Score (1-5) | Rationale |
|-----------|-------------|-----------|
| Data | 2 | No DB; static JSON + JSONL, but a non-trivial 3-source merge in the scanner |
| Auth | 1 | None; 127.0.0.1 bind is the boundary |
| UI | 4 | Canvas graph centerpiece, 5 panel systems, brand-premium polish, motion |
| Integrations | 3 | claude CLI spawn w/ guardrails, vault git, 3 heterogeneous data sources |
| Scale | 1 | One user, one machine |
| **Total** | **11** | **Tier: standard** |

## 3. Tech Stack (from the blueprint — authoritative)

| Layer | Choice | Rationale (traces to blueprint) |
|-------|--------|---------------------------------|
| Build/dev | Vite 6 + React 19 + TS | SPA-first for a canvas-heavy single screen; no SSR tax (blueprint §3) |
| Graph render | react-force-graph-2d | Canvas 2D 60fps at target scale; brandable via Canvas2D; Sigma.js = documented >3k upgrade path, not v1 (blueprint §3, Exa-cited) |
| State | zustand | Shared selection/filter/deck state; re-render control next to canvas |
| Styling | Tailwind v4 + CSS custom props | Brand tokens once as custom props; HUD speed (blueprint §3) |
| Server | Hono on Node 20+ | 4 tiny routes + static serve; TS-first (blueprint §3) |
| Scanner | Python 3.12 stdlib | Matches Nexis tooling; regex frontmatter, no deps (blueprint §3) |
| Database | none | Filesystem is the database (blueprint what-not-to-do #1... §3) |
| AI layer | direct `claude -p` spawn | One call per button; CLI holds auth (blueprint §3) |
| Hosting | localhost | Local-first requirement |

## 4. Project Structure

```
nexus-command-center/
├── .builder/                    # pipeline artifacts
├── blueprint.md                 # advisor original (kept)
├── package.json                 # one package: client + server scripts
├── vite.config.ts               # dev proxy /api -> :4400
├── tailwind.config / CSS        # Tailwind v4 (CSS-first config)
├── index.html
├── public/fonts/                # QuicheSans + Urbanist (copied from brand-assets)
├── src/                         # React SPA
│   ├── main.tsx / App.tsx
│   ├── theme.css                # brand tokens as CSS custom props + @font-face
│   ├── store.ts                 # zustand
│   ├── api.ts                   # typed client for the contract below
│   └── components/
│       ├── AuroraBackground.tsx # rAF canvas: blobs + particles (reduced-motion aware)
│       ├── HudShell.tsx         # layout chrome: top bar, docks
│       ├── GraphCanvas.tsx      # react-force-graph-2d + custom node painting
│       ├── LegendFilters.tsx    # community/type chips -> filters
│       ├── SidePanel.tsx        # selected node detail
│       ├── CatalogDrawer.tsx    # searchable object list
│       ├── VitalsBar.tsx        # counts, last sync, spend
│       └── CommandDeck.tsx      # presets, confirm modal, live status
├── server/
│   ├── index.ts                 # Hono app: static dist/ + /api, binds 127.0.0.1
│   ├── routes.ts                # route handlers
│   ├── spawn.ts                 # runClaude(): mutex, timeout+kill, cost parse, logging
│   ├── vitals.ts                # cheap fs reads
│   └── config.ts                # paths, ceiling, port (env overrides)
├── commands.json                # command-deck presets (code-reviewed config)
├── runs/                        # gitignored: workspace/, log.jsonl, claude-settings.json
│   └── claude-settings.json     # PreToolUse hook + allowlist for spawned runs
├── scripts/
│   ├── build_system_graph.py    # the scanner (stdlib only)
│   └── test_build_system_graph.py  # pytest
└── data/system-graph.json       # scanner output (gitignored, regenerable)
```

## 5. Data Contracts (no DB — file schemas are the schema)

### data/system-graph.json (scanner output)
```jsonc
{
  "meta": { "generated_at": "ISO", "counts": { "skills": 0, "projects": 0, "wiki": 0, "decisions": 0, "nodes": 0, "edges": 0 } },
  "nodes": [ { "id": "nexis:skill/brain-sync", "label": "Brain Sync", "type": "skill|project|rule|context|decision-cluster|wiki|raw|community|asset", "group": "str|int", "summary": "1-3 sentences", "source_file": "abs or repo-rel path", "size": 1 } ],
  "links": [ { "source": "id", "target": "id", "relation": "str", "weight": 1 } ]
}
```
- id namespaces: `nexis:` (repo scan), `vault:` (Graphify import), `ua:` (understand-anything). Dedup on id; cross-links per blueprint §4.
- decisions: cluster node per month (`nexis:decisions/2026-07`), entries listed in `summary`/panel, never one node per entry.

### runs/log.jsonl (append-only audit)
`{ "ts": "ISO", "run_id": "str", "label": "str", "cost_usd": 0.0, "duration_ms": 0, "result_file": "path|null", "exit": "ok|timeout|error|killed" }`

### commands.json (presets — the ONLY commands the deck can run)
`[ { "id": "slug", "label": "str", "description": "str", "prompt": "str", "output": "vault-raw" } ]`

## 6. API Contract

All JSON. Server binds `127.0.0.1:4400`. Error shape: `{ "error": "msg", "code": "MACHINE_CODE" }`.

| Method | Path | Request | Response 200 | Errors |
|--------|------|---------|--------------|--------|
| GET | /api/graph | — | system-graph.json passthrough | 404 `GRAPH_MISSING` (scanner never ran) |
| GET | /api/vitals | — | `{ counts, last_sync: {ts, line}\|null, last_vault_commit: {ts, message}\|null, command_spend: {total_usd, runs}, graph_generated_at }` | — |
| GET | /api/commands | — | `{ commands: [{id,label,description}] }` (prompts not exposed to UI) | — |
| POST | /api/command | `{ "id": "slug", "confirm": true }` | 202 `{ run_id, label, started }` | 400 `UNKNOWN_COMMAND` / `UNCONFIRMED`; 409 `RUN_IN_PROGRESS`; 423 `CEILING_LOCKED` |
| GET | /api/command/status | — | `{ running: bool, current: {run_id,label,started}\|null, last: {run_id,label,cost_usd,duration_ms,exit,result_file,over_ceiling}\|null, locked: bool }` | — |
| POST | /api/command/ack | `{}` | 200 `{ locked: false }` (acknowledges an over-ceiling run, unlocks the deck) | — |

UI polls `/api/command/status` every 2s while `running` (simplest live status; SSE deliberately skipped — decisions.md).

### POST /api/command guardrails (hard requirements, tested)
1. Preset-only: `id` must exist in commands.json; prompt text never comes from the client.
2. Mutex: one child ever; concurrent POST -> 409. No fan-out.
3. Spawn: `claude -p "<prompt>" --output-format json --max-turns 15 --settings runs/claude-settings.json` with `cwd = runs/workspace/`, full .cmd path resolution on Windows.
4. `runs/claude-settings.json`: PreToolUse hook blocking `.env`/credential/key reads + destructive Bash; tool allowlist Read/Glob/Grep/Write (scoped), **no Bash**.
5. Wall-clock timeout 5 min -> kill child tree (`taskkill /PID <pid> /T /F`), exit `timeout`.
6. Parse `total_cost_usd` from result JSON; if > ceiling ($0.50 default), set `locked=true` (423 until /ack).
7. Result markdown saved to `<vault>/raw/command-center/<ts>-<label>.md`; every run appended to runs/log.jsonl.

## 7. Frontend Breakdown

Single route `/`. Component hierarchy:
```
App
├── AuroraBackground        (z-0, rAF canvas, pauses on prefers-reduced-motion)
└── HudShell                (z-10 chrome grid)
    ├── TopBar: logo + wordmark, VitalsBar, catalog + deck toggles
    ├── GraphCanvas         (fills viewport; custom nodeCanvasObject: brand-glow dots,
    │                        community colors, labels above zoom threshold; click -> select;
    │                        cooldownTicks throttled after settle)
    ├── LegendFilters       (bottom-left chips; toggle type/community visibility)
    ├── SidePanel           (right slide-in: label, type badge, summary, source path,
    │                        vscode:// link, neighbor list -> click to navigate)
    ├── CatalogDrawer       (left slide-in: fuzzy search over nodes; click -> focus + select)
    └── CommandDeck         (bottom dock: preset buttons; confirm modal shows prompt label +
                             ceiling; running spinner + live status; last-run result + cost;
                             ceiling-lock banner with Acknowledge)
```
State: one zustand store `{ graph, selectedId, filters, deck: {running, last, locked} }`. Data fetch: plain typed `fetch` in api.ts on mount; vitals refresh 30s; status poll 2s while running (no react-query — 4 endpoints, YAGNI).

Design system: implement `.builder/design-system.md` tokens first (theme.css), then components.

Key libraries: react-force-graph-2d, zustand, tailwindcss v4. Nothing else without a decisions.md entry.

## 8. Backend Breakdown

- **routes.ts:** thin handlers -> services. Static serve `dist/` (prod) at `/`.
- **spawn.ts:** `runClaude(preset)` — the only stateful module: module-level mutex + current-run record, spawn/timeout/kill, result parse, vault write, log append, ceiling lock.
- **vitals.ts:** reads graph meta, tails `logs/brain-sync.log` (Nexis), `git -C <vault> log -1 --format=%cI|%s`, sums log.jsonl.
- **config.ts:** resolved paths (NEXIS_ROOT = repo root two levels up from project; VAULT = env `OBSIDIAN_VAULT_PATH` or default), PORT 4400, CEILING 0.50, CLAUDE_BIN.
- Middleware: Hono logger (dev), JSON error wrapper mapping thrown `{code,status}` to the error shape. No auth middleware (localhost bind).

## 9. Environment Variables (all optional — sane defaults in config.ts)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| PORT | API/serve port | 4400 | No |
| OBSIDIAN_VAULT_PATH | vault root | C:\Users\qubit\OneDrive\Documents\agency-brain | No |
| COMMAND_COST_CEILING_USD | per-run ceiling | 0.50 | No |
| CLAUDE_BIN | claude CLI path | claude (PATH resolve) | No |

No secrets anywhere. `.env.example` documents the four.

## 10. Implementation Order

1. **M0 scaffold:** package.json (dev = concurrently vite + tsx server), Tailwind v4, theme.css tokens + fonts, HudShell + TopBar static, AuroraBackground stub (flat gradient). *Demoable: branded empty cockpit.*
2. **M1 graph:** scanner + pytest -> data/system-graph.json; /api/graph; GraphCanvas + LegendFilters with community colors + glow. *Demoable: the living system graph.*
3. **M2 panels:** SidePanel, CatalogDrawer, /api/vitals + VitalsBar.
4. **M3 deck:** commands.json (3 starter presets), runs/claude-settings.json, spawn.ts + guardrail tests, CommandDeck UI + confirm + status poll + ack.
5. **M4 polish:** full aurora (blobs + particles), motion (panel slide, settle easing), HUD chrome detail, showcase pass.

## 11. Scaling Considerations

Not applicable (standard tier, single user). The only perf budget: 60fps pan/zoom at 1k nodes — enforced by canvas hygiene (label zoom threshold, cooldownTicks, no per-frame allocation in nodeCanvasObject).

# Nexus Command Center

One screen for the whole Nexis agency OS: every skill, project, rule, context file, decision cluster, and second-brain wiki page rendered as a living force-directed knowledge graph — plus system vitals and a guarded command deck that fires headless `claude -p` runs whose outputs land in the vault.

Built by nexis-builder from `blueprint.md` (developer-advisor). Pipeline artifacts in `.builder/`.

## Run

```bash
npm install
npm run scan       # builds data/system-graph.json (Python 3.12, stdlib only)
npm run dev        # Vite on 5173 (proxies /api) + API on 4400
```

Production-style (one process, one port):

```bash
npm run build
npm start          # http://127.0.0.1:4400
```

Regenerate the graph any time with `npm run scan` (idempotent; also safe to wire into the weekly NexisBrainSync task).

## Stack

Vite + React 19 + TS SPA · react-force-graph-2d (canvas) · zustand · Tailwind v4 + NexusPoint brand tokens · Hono on Node (24+, runs TS natively) · Python stdlib scanner · no DB — the filesystem is the database.

## Command deck guardrails (architecture.md §6)

- **Preset-only**: the deck can only run entries from `commands.json`; prompt text never comes from (or goes to) the browser.
- **Scoped spawn**: `claude -p` runs in `runs/workspace/` with `runs/claude-settings.json` — tool allowlist Read/Glob/Grep/Write(./**), **no Bash**, secret-path deny rules, plus a PreToolUse hook (`server/hook-guard.mjs`) as a second layer.
- **Mutex**: one run at a time (409), no fan-out.
- **Timeout**: 5 min wall clock, then the child tree is killed.
- **Cost ceiling**: runs costing over `$0.50` lock the deck (423) until acknowledged in the UI.
- **Audit**: every run appends to `runs/log.jsonl`; results save to `<vault>/raw/command-center/`.

## Environment (all optional — defaults in `server/config.ts`)

| Var | Default |
|---|---|
| `PORT` | 4400 |
| `OBSIDIAN_VAULT_PATH` | `C:\Users\qubit\OneDrive\Documents\agency-brain` |
| `COMMAND_COST_CEILING_USD` | 0.50 |
| `CLAUDE_BIN` | `claude` (resolved via `where.exe`) |

## Tests

```bash
npm test           # node:test (guard hook + API contract + mutex/ceiling, fake CLI) + Python scanner selftest
npm run typecheck
```

## Data sources (scanner merge)

1. Nexis repo: `.claude/skills/*/SKILL.md`, `projects/*`, `.claude/rules/*.md`, `context/*.md`, `decisions/log.md` (month clusters)
2. Vault Graphify graph (`<vault>/graphify-out/graph.json`), namespaced `vault:`
3. `.understand-anything` edges remapped onto scanned nodes (best effort)
4. Cross-links: context mirrors, brain-sync → vault, skill → project mentions

# Nexus Command Center — Build Blueprint

*developer-advisor blueprint, 2026-07-10. Consumer: nexis-builder. Target: `projects/nexus-command-center/`.*

## 1. Problem statement

Aleem runs NexusPoint from the Nexis Claude Code repo (40+ skills, 13+ projects, rules, context, decisions) plus the live-connected agency-brain vault (Graphify graph, 150 nodes/38 communities, auto-rebuilds on commit). Nothing shows the whole system in one place or lets him drive it from one screen. Build a local, branded command center: a large interactive force-directed knowledge graph of everything, plus system vitals, a browsable catalog, and a guarded command deck that fires headless `claude -p` runs. Single user, local Windows machine, doubles as a client showcase so visual polish is a requirement, not a nicety.

## 2. Recommended architecture

**A local client-server monolith in one process: a static React SPA served by a small Node API server, fed by a Python scanner that pre-computes the graph.**

- The centerpiece is a long-lived canvas scene with client-side physics. There is no SEO, no auth, no multi-user routing — server-side rendering machinery (Next.js et al.) adds hydration complexity that fights a persistent canvas and provides nothing here. The scoreboard's "dashboard -> Next.js" row is conditioned on authed multi-page products; this is a single-screen local cockpit, so the condition does not trigger.
- Data is pre-computed to static JSON by a scanner script, not queried live. The graph only changes when the repo/vault changes; computing it per-request is wasted work. This mirrors how Graphify already works (build artifact + viewer).
- The only dynamic surface is 3 small API routes (graph, vitals, command). One process serves both SPA and API — no CORS, one port, one `npm start`.
- **Condition that would change this:** if the command center ever goes multi-user/remote (team dashboards), revisit with auth + a real backend. Not v1.

## 3. Stack table

| Layer | Choice | Why |
|---|---|---|
| Build/dev | **Vite 6 + React 19 + TypeScript** | SPA-first tooling for a canvas-heavy single screen; instant HMR; no SSR framework tax. React for ecosystem + the graph lib's first-class React bindings. TS end-to-end with the API. |
| Graph rendering | **react-force-graph (2D canvas mode)** | The decisive constraint is smooth 100s-2k nodes with brandable visuals. Canvas 2D holds 60fps well past this scale ("10,000 nodes... 60fps" — starlog.is on vasturiano/force-graph); d3-force physics gives the alive drift/settle feel; custom node painting via plain Canvas2D (shadowBlur = the brand glow) is far cheaper to style than WebGL shaders. *Fresh Exa sources (2026-07-10), not the locked corpus: starlog.is/articles/data-knowledge/vasturiano-force-graph/, pkgpulse.com 2026 graph-lib guide, github.com/vasturiano/react-force-graph.* |
| Graph upgrade path (named, not built) | Sigma.js v3 + graphology (WebGL) | If the merged graph ever exceeds ~3k nodes and canvas frame rate drops, port the renderer only — data layer stays node-link JSON either way (dgraph's ratel made exactly this canvas->sigma migration for scale). Do not start here; WebGL styling costs more for zero benefit at current n. |
| State | **zustand** | Selected-node / filter / panel state shared across graph, side panel, catalog, deck; re-render control matters next to a canvas. Tiny, no boilerplate. |
| Styling | **Tailwind CSS v4 + CSS custom properties for brand tokens** | Fastest route to a polished dark HUD; tokens (`--np-blue`, `--np-charcoal`, fog/hairline/glow) defined once as CSS custom props so the brand is not smeared through utility classes. QuicheSans + Urbanist via `@font-face` from `brand-assets/fonts/` (copy into `public/fonts/`). |
| API server | **Hono on Node 20+** | 3 routes + static serving; Hono is tiny, TS-first, zero-config on Windows. Express would also do; Hono wins on TS ergonomics at identical simplicity. |
| Scanner | **Python 3.12, stdlib only** (`scripts/build_system_graph.py`) | Repo-side data tooling matches every other Nexis skill (all Python); frontmatter is simple enough for regex, no YAML dep. Also invocable by the weekly `NexisBrainSync` task later. |
| Database | **None — the filesystem is the database** | All data is static JSON + repo files. Adding a DB here is what-not-to-do #1. |
| AI layer | **Direct `claude -p` child process** (no SDK, no framework) | One headless call per button matches the scoreboard's "1 call -> direct" row; the CLI already holds auth. Spawn per run, never concurrent. |
| Hosting | **localhost only** (`npm start`; optional Windows shortcut) | Local-first requirement. No deploy target in v1. |

## 4. Data model sketch

**`data/system-graph.json`** (scanner output, the app's single graph source):

- `nodes[]`: `{ id, label, type, group, summary, source_file, size }`
  - `type`: `skill | project | rule | context | decision-cluster | wiki | raw | community | asset`
  - `id` namespaced by origin: `nexis:skill/brain-sync`, `vault:offer-and-positioning`, `ua:<file-id>`
  - `group`: community/cluster for coloring (vault nodes keep Graphify's `community`; Nexis nodes cluster by type)
  - `size`: degree-scaled for node radius
- `links[]`: `{ source, target, relation, weight }`
- `meta`: `{ generated_at, counts: {skills, projects, wiki, decisions, nodes, edges} }`

**Merge sources (scanner):**
1. Nexis scan: `.claude/skills/*/SKILL.md` frontmatter (name + description), `projects/*/` (README first line), `.claude/rules/*.md`, `context/*.md`, `decisions/log.md` (count + one cluster node per month, not one node per entry).
2. Vault Graphify `graphify-out/graph.json` (NetworkX node-link: `label/file_type/source_file/community`; links `relation/weight/confidence_score`) — imported as-is under the `vault:` namespace.
3. `.understand-anything/tmp/ua-graph-0-full.json` edges over the Nexis OS core, where they connect nodes that survived 1 (best effort; skip malformed batches).
4. Cross-links: `nexis:context/*` <-> `vault:context` mirrors (brain-sync contract), `nexis:skill/brain-sync` -> vault root, skills -> projects they mention (regex over SKILL.md).

**`runs/log.jsonl`** (command deck audit): one line per run `{ ts, prompt_label, cost_usd, duration_ms, result_file, exit }`.

## 5. How the pieces connect

- `scripts/build_system_graph.py` -> writes `data/system-graph.json`. Run manually, on server start if file missing, and (later) from the weekly task.
- Hono serves: `GET /` (built SPA), `GET /api/graph` (the JSON), `GET /api/vitals` (cheap fs reads: counts from graph meta, `logs/brain-sync.log` tail for last sync, vault `git log -1` for last commit, sum of `runs/log.jsonl` cost), `POST /api/command`.
- `POST /api/command` — the guarded headless runner:
  - **Preset commands only** (defined in `commands.json`: label, prompt, output target). No free-text prompt in v1 — buttons, not a shell.
  - Server-level **mutex**: one child process ever; concurrent clicks get 409.
  - Spawn `claude -p "<prompt>" --output-format json` with: `cwd` = a **scoped runs workspace** (`runs/workspace/`), `--settings` pointing at `runs/claude-settings.json` containing a **PreToolUse hook that blocks** `.env`/credential/key-file reads and destructive Bash patterns, a **tool allowlist** (Read/Glob/Grep/Write scoped; **no Bash** for v1 presets), and `--max-turns` cap.
  - Hard wall-clock timeout (kill child), parse `total_cost_usd` from the result JSON, refuse further runs if the last run exceeded the per-click ceiling (default $0.50) until acknowledged in UI.
  - UI: confirm dialog before spawn (shows prompt + ceiling), live status, result saved to the vault (`raw/command-center/<ts>-<label>.md`) so outputs enter the second brain's intake flow, and appended to `runs/log.jsonl`.
- Graph interaction: click node -> zustand `selected` -> side panel renders summary + source path + "open in editor" (`vscode://file/` link). Community color legend doubles as filter chips.
- Brand background: re-implement `BrandBackground.tsx`'s aurora blobs + particles as a plain `requestAnimationFrame` canvas layer behind the graph (visual reference only, no Remotion imports).

## 6. Best-practices checklist (this build)

- **Tests where the risk lives (trophy, minimal):** scanner merge/dedup gets a real pytest (fixture trees -> assert node/link counts, namespacing, no dupes); the command route gets guardrail tests (blocked pattern actually blocks, mutex 409s, ceiling refusal). UI gets a Playwright smoke (graph renders, node click opens panel) only if cheap.
- **Security:** the PreToolUse hook + allowlist are non-negotiable and tested; API binds to `127.0.0.1` only; no secrets in the SPA bundle; `runs/workspace/` gitignored.
- **Performance:** target 60fps pan/zoom at 1k nodes (throttle physics `cooldownTicks` after settle); lazy-render labels above a zoom threshold — standard canvas-graph hygiene.
- **A11y baseline:** the catalog + panels are keyboard-navigable and readable (the canvas itself is exempt); WCAG AA contrast for text on charcoal.
- **No CI needed** (local tool) — a `npm test` + `pytest` pair runnable locally is enough.

## 7. Build milestones

- **M0 — Scaffold:** Vite+React+TS+Tailwind+Hono monorepo layout, brand tokens + fonts wired, dark HUD shell with logo. *Demoable: branded empty cockpit.*
- **M1 — Data + graph:** scanner v1 (Nexis + vault sources), `/api/graph`, force-graph rendering with community colors + brand glow. *Demoable: the whole system visible as a living graph.* (The slice that matters — land it early.)
- **M2 — Panels:** node side panel, catalog (searchable skill/project list from the same JSON), vitals bar.
- **M3 — Command deck:** presets + guarded `/api/command` + runs log + vault output. Guardrail tests pass.
- **M4 — Polish:** aurora background, motion (settle animation, panel transitions), HUD chrome, client-showcase pass.

Each milestone: spec -> plan -> build -> review (agentic loop). M1 before M2 because the graph is the product; panels decorate it.

## 8. Risks and what-not-to-do

1. **Do not reach for Next.js/SSR by habit** — hydration + a persistent canvas is friction with zero payoff locally. (This was an explicit user correction; it stays corrected.)
2. **Do not start on WebGL** — Sigma/reagraph cost shader-level styling effort for scale we do not have. Threshold documented: port renderer at ~3k+ nodes.
3. **Command deck scope creep** — no free-text prompts, no Bash tool, no concurrent runs, no fan-out in v1. A "just let it run anything" relaxation is how a showcase tool becomes an incident. The ceiling + confirm stays even when it feels slow.
4. **Graph staleness** — the scanner must be one command, idempotent, and wired into the existing weekly heartbeat later; a stale showcase graph quietly kills trust in the whole brain.
5. **Windows spawn quirks** — `claude` resolves via `.cmd` shim; spawn with explicit full path or `shell: true`, and test the kill-on-timeout path actually terminates the child tree (`taskkill /T`).
6. **decisions/log.md as nodes** — one node per decision (~80+) is noise; cluster by month, expandable in the panel.

## 9. Follow-ups

Blueprint is ready for nexis-builder (`projects/nexus-command-center/`, this file is Phase 0 input). Contested-decision deep-dives available on ask: canvas vs WebGL numbers, Hono vs Express, scanner design. Google Doc export available via `scripts/save_blueprint.py`.

*Corpus note: graph-rendering library evidence is from a fresh 2026-07-10 Exa pass (URLs inline above), not the locked 226-source corpus — the corpus is thin on graph-viz. Also: SKILL.md references `tools/exa/exa_client.py`, which does not exist in the skill; the pass used the standard Nexis Exa pattern instead.*

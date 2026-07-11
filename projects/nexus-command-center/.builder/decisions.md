# Decisions — NexusCommandCenter (append-only)

[2026-07-10] DECISION: Ingested existing developer-advisor blueprint verbatim as Phase 0; did not re-derive the stack | REASONING: Blueprint was produced this session by the advisor with a fresh Exa pass on the graph-lib decision; re-running would burn tokens for zero new information | CONTEXT: Phase 0

[2026-07-10] DECISION: senior-architect skill's generic analyzer scripts not run in Phase 1 | REASONING: They analyze existing codebases; no code exists yet. The Phase-1 deliverable is architecture.md per the nexis-builder template, written against the blueprint | CONTEXT: Phase 1

[2026-07-10] DECISION: Command-deck live status via 2s polling of GET /api/command/status, not SSE/WebSocket | REASONING: Localhost single-user; polling is the simplest thing that ships and removes a whole class of connection-management code. Revisit only if runs become long/chatty | CONTEXT: Phase 1, API contract

[2026-07-10] DECISION: Added GET /api/commands and POST /api/command/ack beyond the blueprint's named 3 routes | REASONING: UI needs the preset list without hardcoding it, and the $0.50 ceiling lock needs an explicit acknowledge path; both derive directly from blueprint §5 guardrail requirements | CONTEXT: Phase 1, API contract

[2026-07-10] DECISION: No react-query/SWR; plain typed fetch | REASONING: 4 endpoints, one screen, no cache invalidation problem. YAGNI | CONTEXT: Phase 1, frontend

[2026-07-10] DECISION: Command prompts never sent to or from the browser; UI gets id/label/description only | REASONING: Keeps the preset-only guardrail honest — the client cannot influence what runs | CONTEXT: Phase 1, security

[2026-07-10] DECISION: Phase 2 written directly against the pinned brand instead of invoking ui-ux-pro-max/taste-skill/ui-design-system routers | REASONING: The aesthetic was not open — brand tokens, fonts, motifs, and 5 reference screenshots fix the direction; the routers exist to derive a direction when one is missing. Tokens still locked per ui-design-system conventions in design-system.md | CONTEXT: Phase 2

[2026-07-10] DECISION: Nodes colored by TYPE (skill/project/wiki/…), not by raw community id; legend chips filter by type | REASONING: 38 vault communities would need 38 chips and an illegible legend; type coloring makes graph, legend, and filters one coherent language. Communities still shape layout via links and show in the side panel | CONTEXT: Phase 3, GraphCanvas/palette

[2026-07-10] DECISION: No tsx/nodemon — Node 24 runs the TS server natively (`node --watch server/index.ts`); server imports use explicit .ts extensions, erasable-syntax TS only | REASONING: Native platform feature covers it; two dev-deps deleted | CONTEXT: Phase 4

[2026-07-10] DECISION: Prompt piped to `claude -p` via STDIN, never argv | REASONING: kills all Windows .cmd-shell quoting issues, keeps prompts out of process lists, and leaves argv fully static (no injectable surface) | CONTEXT: Phase 4, spawn.ts

[2026-07-10] DECISION: runs/claude-settings.json is GENERATED at boot by ensureRunFiles(), not checked in | REASONING: it embeds machine-absolute paths (hook script, additionalDirectories); regenerating per boot keeps runs/ fully disposable and correct on any machine | CONTEXT: Phase 4, config.ts

[2026-07-10] DECISION: Guardrails are belt+suspenders: settings allow/deny lists AND the PreToolUse hook-guard | REASONING: blueprint names the hook as a hard requirement; the deny list alone would satisfy function but not the stated contract, and the hook survives allowlist edits | CONTEXT: Phase 4, security

[2026-07-10] DECISION: Deck runs execute with cwd inside the repo (runs/workspace/), so the spawned claude inherits Nexis CLAUDE.md context | REASONING: presets summarize THIS system — the context makes outputs better; token cost stays inside the $0.50 ceiling. Revisit if presets ever get generic | CONTEXT: Phase 4

[2026-07-10] DECISION: Scanner adds synthetic hub nodes (nexis:hub/*, type "community") anchoring each Nexis type | REASONING: skills/rules with no organic edges would float as disconnected dust; hubs give the constellation structure the reference screenshots show. Vault side keeps its real Graphify edges | CONTEXT: Phase 4, scanner

[2026-07-10] DECISION: CLAUDE_BIN_ARGS env seam added to config | REASONING: lets tests run the deck against a fake CLI (node fake-claude.mjs) — deterministic, free, no live claude spawn in CI/tests | CONTEXT: Phase 5

[2026-07-10] DECISION: Vault graphify components union-find-anchored to a synthetic vault:__hub__ ("Agency Brain"), bridged to nexis:hub/nexis | REASONING: visual QA showed disconnected vault islands scattering as dust; anchoring every component makes the graph read as ONE system, which is the product's whole point | CONTEXT: Phase 6, visual QA fix-loop

[2026-07-10] DECISION: No live `claude -p` deck run fired during the build | REASONING: the spawn path is fully covered by the fake-CLI tests; the first real run costs real money and belongs to Aleem's first click | CONTEXT: Phase 6
[2026-07-11] DECISION: pickRunnableBin prefers .cmd/.exe/.bat from where.exe output | REASONING: npm's extensionless sh shim is listed first and is not spawnable on Windows (ENOENT) — the deck had never actually run until this fix | CONTEXT: cockpit expansion, spawn.ts

[2026-07-11] DECISION: Two run profiles (read/act): per-profile settings files, hook-guard argv, max-turns (15/25), timeout (5m/10m), ceiling ($0.50/$1.00) | REASONING: curated skill actions must run their python/gws steps (Bash+Edit) while deck presets stay read-only; a live proposal run measured $0.58, so a single $0.50 ceiling would lock the console after every normal act run | CONTEXT: skill quick-actions

[2026-07-11] DECISION: Headless runs pinned to sonnet via --model (env NCC_RUN_MODEL) | REASONING: the CLI default (opus) billed $1.81 for a decision digest; sonnet is plenty for presets and skill actions | CONTEXT: spawn.ts

[2026-07-11] DECISION: dev script runs the API WITHOUT --watch; SIGINT/exit cleanup kills supervised children | REASONING: mtime churn in this OneDrive tree restarted the API mid-run (a server.test.ts reload 14s into a live proposal run), orphaning the in-flight claude and losing run state — an auto-restarting process cannot supervise children (deck runs + project dev servers). Restart manually after server changes | CONTEXT: package.json, index.ts

[2026-07-11] DECISION: projects.json registry is curated with explicit ports (Next apps 3001-3005, remotion 3010); browser-automation excluded | REASONING: every Next dashboard defaults to :3000 (guaranteed collision); browser-automation is a Playwright test suite, not a launchable server | CONTEXT: projects launcher

[2026-07-11] DECISION: Console = tabbed dock (Deck/Projects/Skills); deck status poll moved to Console; ConfirmModal + RunStatus extracted as shared components | REASONING: three surfaces share one footer, one mutex, and one run-state view — the poll must outlive tab switches | CONTEXT: frontend

## 2026-07-11 — Build 2: Chat with Nexis

- **Chat gets its own third profile ("chat"), the tightest in the console.** The read profile allows Write(./**) for deck output; the locked decision says chat "never edits files", so chat allows exactly Read/Glob/Grep and denies Write/Edit/Bash/Task/WebFetch/WebSearch. hook-guard treats any non-"act" arg as read-equivalent (fail closed).
- **Transport is NDJSON over the POST response body, not SSE.** EventSource only supports GET; fetch + ReadableStream gives the same streaming with one request and no reconnect machinery. The turn is started BEFORE the stream opens so mutex/validation failures (400/404/409/423) return plain JSON statuses.
- **startStreamRun lives in spawn.ts beside startRun**, sharing the module mutex, ceiling lock, timeout, and audit log — chat turns, deck presets, and skill actions are one single-flight system. stream-json parsed line-by-line; deltas preferred, whole-turn text blocks as fallback, result.result as last resort.
- **Session continuity via --resume.** Thread stores the CLI session_id; a session that fails to resume (error + zero output) is dropped so the next turn starts fresh. Live-verified: turn 2 remembered turn 1 AND cost $0.016 vs $0.247 (prompt cache hit on the resumed session).
- **Chat spawns from the Nexis root** (deck/skills use the scratch workspace) so the spawned claude loads CLAUDE.md and answers as Nexis — that is the product.
- **Two new deps, justified:** marked (md -> html) + dompurify (claude can echo file content into replies; sanitize before dangerouslySetInnerHTML). Everything else reused (mutex engine, ConfirmModal-free flow, np-* design system).
- **"killed" added as a first-class exit** (user pressed Stop) distinct from error/timeout; partial answers persist to the thread.

## 2026-07-11 — Build 3: Brain panel + graph-to-cockpit + vitals depth

- **The brain-sync script is the single source of truth for freshness/drift.** `server/brain.ts` shells `sync_vault.py --ingest-status --json` / `--check --json` instead of re-implementing the logic in TS. The script exits 1 for stale/drift while still printing valid JSON, so the exec wrapper recovers the payload from the error's stdout.
- **Staleness detector design (the item-1 automation):** baseline file `wiki/.ingest-state.json` written by `--mark-ingested` (date + SKILL.md-bearing folder set + newest decision date); stale = any new skill OR >5 new decisions OR >14 days. Surfaced in three places: weekly `--maintain` log line, `session-closeout` step 4.5, and the Brain panel badge. Thresholds chosen to avoid alarm fatigue (every session logs decisions; one stray decision is not "overdue").
- **Brain panel is signal + safe check only** (user decision): read-only Brain Pulse preset + local rescan; the real ingest stays Claude-driven in-session because wiki distillation quality needs judgment. No headless ingest button.
- **/api/ops split from /api/vitals** so the 15s top-bar poll stays cheap; ops parses the full audit log on demand (panel open only).
- **Graph rescan is not a claude run:** own module-level in-flight guard (409 SCAN_IN_PROGRESS), independent of the deck mutex — it is a free local script, not a paid headless run. `NCC_SCAN_CMD` JSON-array env is the test seam.
- **Graph -> cockpit mapping is id-based:** `nexis:project/<dir>` -> projects.json id (ids are dir names); `nexis:skill/<folder>` -> skill-actions.json `skill` field (now exposed in the API listing — it is just a folder name, templates stay server-side). Launcher buttons render only where a mapping exists (6 projects, 3 actions — sparse but honest).
- **QA note:** the gstack browse daemon flaked persistently (server died after each command); fell back to playwright-core in the scratchpad driving the cached ms-playwright chromium directly — deterministic, 6/6 steps passed.

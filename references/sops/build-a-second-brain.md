# How to Build a Second Brain (NexusPoint SOP)

A reproducible, step-by-step playbook for building an AI second brain (Obsidian + Karpathy-style
LLM Wiki + Graphify knowledge graph). This is the exact process used to build the NexusPoint
agency brain on 2026-06-20. Reuse it to build a brain for a **client** or a **team member** by
following the same steps and applying the per-scope notes in the last section.

A second brain is a structured folder of markdown that Claude reads, writes, and maintains:
`raw/` (read-only source material) plus `wiki/` (Claude-written, interlinked knowledge) governed
by a lean `CLAUDE.md` schema, visualized in Obsidian, and graphed by Graphify.

---

## 0. Prerequisites (install once per machine)

- **Obsidian** (free) from obsidian.md.
- **Claude Code** CLI: `irm https://claude.ai/install.ps1 | iex` (Windows PowerShell).
- **Python 3.10+** (for the Drive export script).
- **Graphify**: `pip install graphifyy` (PyPI package is `graphifyy`, double-y; the CLI is `graphify`).
- **An LLM API key with credit** (OpenAI / Gemini / Anthropic / DeepSeek / Moonshot). Required for
  the doc semantic pass. This build used the OpenAI key from the Nexis `.env`.
- **Google Workspace access** (`gws` CLI, authenticated) if seeding from Google Drive.

---

## 1. Decide the scope before building

| Scope | Lives where | Seed from | Sensitivity |
|-------|------------|-----------|-------------|
| **Agency** (this build) | `OneDrive/Documents/agency-brain` | Nexis context + agency Drive docs | Internal only |
| **Client** | a per-client vault, e.g. `client-brains/<client>` | the client's briefs, transcripts, brand docs | High - keep client data isolated, never mix clients |
| **Team member** | `team-brains/<name>` | that person's role docs, SOPs they own, project history | Medium - scope to their function |

Decide: what is the brain FOR, whose knowledge goes in, and what must stay out (see Step 6).

---

## 2. Create the vault + folder structure

Pick a location OUTSIDE any working code repo (a brain is knowledge, not code). Create:

```
<brain-name>/
├── CLAUDE.md        # the router/schema Claude reads every prompt (Step 3)
├── context/         # who/what this brain serves (identity, goals, audience)
├── decisions/       # append-only decision log
├── clients/         # one subfolder per client (agency/team brains)
├── raw/             # READ-ONLY intake: exported docs, transcripts, brain dumps
│   ├── ops/         # operational source docs
│   └── research/    # reference/research source docs
├── wiki/            # Claude-built knowledge base (index.md + log.md + [[linked]] pages)
└── skills/          # plain-language SOPs (this file lives here)
```

```bash
mkdir -p <brain-name>/{context,decisions,clients,raw/ops,raw/research,wiki,skills}
```

Seed `wiki/index.md` (a "Pages" catalog) and `wiki/log.md` (append-only ingest log) as empty stubs.

---

## 3. Write CLAUDE.md (the schema / router)

Keep it under ~200 lines: it is read on every prompt, so bloat wastes tokens. It should route, not
contain. Template (adapt the role line per scope):

```markdown
# <Name> Brain (AI Operating System)

You are the executive assistant and operational brain for <who/what>. This vault is the single
source of truth. Read it, maintain it, reason across it. This is a Karpathy-style LLM Wiki: you
read raw material, then write and link summarized knowledge pages yourself.

## Navigation & Routing Rules
- context/  -> identity, goals, audience            (read for strategy questions)
- decisions/ -> append-only decision log            (read before reversing a call)
- clients/  -> one subfolder per client             (client-specific work)
- raw/      -> READ-ONLY intake, never the answer   (source material to ingest)
- wiki/     -> YOUR knowledge base, answer from here (build it as you ingest)
- skills/   -> SOPs as instruction files            (executing a workflow)
wiki/index.md is the catalog. wiki/log.md records what changed each cycle.

## Operating Principles
1. Think before executing. Outline the plan before creating/editing files.
2. Answer from wiki/, not raw/. If the wiki can't answer, ingest the source first.
3. Maintain voice. Follow context/ brand rules for any external-facing output.
4. Surgical edits. Change only what was asked.
5. Cite sources. Every wiki page links back to the raw/ file(s) it came from.
6. Evergreen only. Ingest goals, SOPs, durable knowledge. Never daily noise.

## Ingest Workflow ("I added a source to raw, update the wiki")
Read the new file(s) -> extract entities/concepts -> create/update wiki pages with [[wiki-links]]
-> update wiki/index.md -> append a dated line to wiki/log.md.

## Lint Workflow ("lint the wiki")
Scan for orphaned pages, broken [[links]], stale claims, missing summaries. Report + fix.

## Wiki Page Format
Every page: a one-paragraph summary, a Source: line linking the raw/ file(s), Related: [[links]].

## Memory Health
/compact at ~60% context. /clear near the window limit (knowledge is in files, nothing is lost).
/handoff when switching tasks.

## Boundaries
Live data (CRMs, lead sheets, calendars, finances) is NOT stored here - reach it via MCP tools.
Sensitive data (contracts with PII, keys) stays out of wiki/ summaries.
```

---

## 4. Seed content from local files

Copy durable identity/decision files in directly (they are already good wiki material):

```bash
cp <source>/context/*.md      <brain-name>/context/
cp <source>/decisions/log.md  <brain-name>/decisions/
```

For the agency brain, these came from the Nexis repo (`context/` + `decisions/log.md`).

---

## 5. Seed content from Google Drive (export to markdown)

Google Docs export cleanly to markdown via `gws drive files export` with mimeType `text/markdown`.
Use a small script with a curated manifest so it is repeatable. Reference implementation:
`scripts/export_drive_seed.py` in this vault.

Key points from that script:
- It maps a list of `(name-substring, raw-subfolder, output-filename)` to exported files.
- Look up each doc by a unique, **apostrophe-free** name substring (Drive's `q` syntax breaks on apostrophes).
- Call `gws` through `cmd /c` so the `.cmd` wrapper resolves, and parse JSON from the first `{`
  (gws prints a keyring line first).
- Write files with a Windows path (`C:/Users/...`), not an MSYS `/c/...` path - the bundled Python
  cannot open MSYS paths.

For Google **Sheets** (e.g. portfolios), pull values with `gws sheets spreadsheets values get` and
render a markdown table. Only do this for **evergreen, structured** sheets (see Step 6).

Run it: `python scripts/export_drive_seed.py`

---

## 6. Decide what goes IN vs OUT (the boundary rule)

This is the most important judgment call. A brain compounds in value only if it holds **evergreen**
knowledge. Snapshotting live or sensitive data bloats it and goes stale.

| Put IN (evergreen) | Keep OUT (live / sensitive) |
|--------------------|-----------------------------|
| Identity, offer, positioning, strategy | CRMs, lead lists, outreach sheets |
| Services, SOPs, playbooks | Finances (earnings, expenses, budgets) |
| Delivered project/case-study logs | Content calendars / scraped social data |
| Brand voice, ICP, pricing logic | Anything that changes daily/weekly |
| Reference research (distilled) | Secrets, API keys, contracts with PII |

For OUT data, connect live via the Google Sheets/Drive MCP when a number is actually needed.
If a high-level summary is genuinely useful (e.g. a revenue snapshot), derive a single wiki page on
demand WITHOUT storing the raw sensitive figures.

---

## 7. Build the wiki (first ingest)

Open a terminal in the vault, run `claude`, and instruct it:

> "Read everything in raw/ and build the wiki. Follow the ingest workflow and page format in CLAUDE.md."

Claude distills the raw sources into interlinked `wiki/` pages, updates `wiki/index.md`, and logs the
cycle in `wiki/log.md`. Review the pages. The agency build produced pages like `nexuspoint-overview`,
`offer-and-positioning`, `services-and-difficulty`, `proposals-and-pitches`, `client-projects`, etc.

Going forward: drop any new transcript/doc into `raw/`, then say "update the wiki".

---

## 8. Configure Obsidian

1. Open the vault folder in Obsidian (Open folder as vault).
2. Install the **Terminal** community plugin -> run `claude` inside Obsidian.
3. (Optional) Install the **Obsidian Markdown** Claude skill so Claude writes proper `[[wiki-links]]`.
4. Exclude graphify output from the graph (do this after Step 9): Settings -> Files and links ->
   Excluded files -> add `graphify-out`. Also set the Graph View filter to `-path:graphify-out`.

---

## 9. Build the knowledge graph with Graphify

```bash
# from inside the vault, in a plain terminal
git init                                     # graphify hooks need a git repo
graphify hook install                        # post-commit/checkout auto-rebuild (code only, free)
graphify . --backend openai                  # build the graph (docs need an LLM key)
graphify cluster-only . --backend openai     # name communities + write GRAPH_REPORT.md + graph.html
```

Output lands in `graphify-out/`: `graph.html` (open in a browser), `GRAPH_REPORT.md`, `graph.json`.

**Gotchas learned on the agency build (do these or the graph breaks):**
- **Force the backend.** Graphify auto-picks a backend from any key it finds. If a global
  `ANTHROPIC_API_KEY` is set but out of credit, the build fails. Pass `--backend openai` (or whichever
  key has credit). There is no `graphify-obsidian` command and no bare `--obsidian` build flag in the
  CLI; the build is `graphify .` then `graphify cluster-only .`.
- **Exclude `.obsidian/plugins/`.** Bundled minified plugin JS (e.g. the Terminal plugin's xterm.js)
  otherwise explodes the graph into thousands of noise nodes that bury your docs. Gitignore it; a
  clean docs+code build is dozens of nodes, not thousands.
- **Gitignore `graphify-out/`** and periodically clear the dated `graphify-out/2026-*` backups
  graphify auto-creates on each `cluster-only` run.

`.gitignore` to add:
```
.obsidian/plugins/
.obsidian/workspace.json
graphify-out/
```

---

## 10. Commit

```bash
git add -A && git commit -m "Initialize <name> second brain"
```

---

## 11. Ongoing use & maintenance

- **Add knowledge:** drop a doc/transcript into `raw/`, tell Claude "update the wiki".
- **Health check:** "lint the wiki" to catch orphans, broken links, stale claims.
- **Refresh the graph:** `graphify update .` after edits (code, free) or rerun Step 9 for a full rebuild.
- **Context hygiene:** `/compact` at ~60%, `/clear` near the limit, `/handoff` between tasks.
- **Clean backups:** delete `graphify-out/2026-*` occasionally.

---

## Adapting for a CLIENT or TEAM-MEMBER brain

Same 11 steps, with these changes:

**Client brain**
- Location: a dedicated per-client vault. **Never mix two clients in one vault.**
- `CLAUDE.md` role line: "operational brain for <Client>, owned by NexusPoint."
- Seed `raw/` from: the client's discovery/brief docs, call transcripts, brand guidelines, their
  existing content, deliverables. Pull from the client's Drive folder under `NexusPoint Clients/`.
- IN: brand voice, product/offer, audience, approved messaging, project history, deliverable specs.
- OUT: the client's customer PII, credentials, internal financials. Treat their data as confidential.
- Use case: Claude drafts on-brand content, answers "what did we decide for this client", preps calls.
- This is also productizable - a client second brain can be a paid NexusPoint deliverable.

**Team-member brain**
- Location: `team-brains/<name>`.
- Scope to their function (see `team-and-delegation` in the agency wiki): e.g. a frontend dev's brain
  holds component patterns, the design system, their project history; an ops person's holds the
  bidding SOP and Upwork playbooks.
- Seed `raw/` from: the SOPs they own, their past project notes, role-specific references.
- IN: repeatable workflows, decisions in their domain, reference material they reuse.
- OUT: anything outside their role, agency-wide financials, other people's private data.
- Use case: faster onboarding, a personal assistant that knows their lane, consistent SOP execution.

**General rule:** one brain = one clearly-scoped owner and audience. Smaller, well-scoped brains beat
one giant brain. Each gets its own `CLAUDE.md`, its own Graphify graph, its own Obsidian vault.

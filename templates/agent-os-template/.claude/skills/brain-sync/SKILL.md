---
name: brain-sync
description: Two-way sync between this OS repo and its second-brain Obsidian vault. Check drift, push/pull the scoped subset (context/ + decisions/log.md with lossless union merge), check wiki freshness, and ingest new evergreen knowledge into the vault's wiki/ + CRITICAL_FACTS.md. Use when the user says "sync the brain", "push to the second brain", "pull from the vault", "is the brain up to date", "update the wiki", "ingest this into the brain", or after context/ or decisions/ change in this repo.
---

# Brain Sync

Keeps this OS repo and its second-brain vault in step. Setup: set `OBSIDIAN_VAULT_PATH` to the
vault's absolute path (in `.claude/settings.local.json` env, plus add the vault to
`permissions.additionalDirectories`). The vault is then an additional working directory — read and
write it directly by absolute path. Build the vault itself per `build-a-second-brain.md`.

## The contract (never violate)

| Files | Direction | Rule |
|-------|-----------|------|
| `context/**/*.md` | two-way mirror | Last writer wins; script writes a `.bak` before overwriting |
| `decisions/log.md` | two-way | Append-only **union merge** — lossless, converges both sides in one run |
| `wiki/`, `CRITICAL_FACTS.md` | vault-owned | This repo writes only via **ingest** (distillation), never raw copies |
| `raw/`, `clients/` | vault-only | Never mirrored to this repo |
| Live/sensitive data (CRMs, `.env`, client PII, lead sheets) | off-limits | Never enters the vault |

Deletions are reported, never propagated.

## Modes

All script modes run from the repo root:

```bash
python .claude/skills/brain-sync/scripts/sync_vault.py --check          # drift report, no writes (exit 1 = drift; --json for machines)
python .claude/skills/brain-sync/scripts/sync_vault.py --push           # repo -> vault
python .claude/skills/brain-sync/scripts/sync_vault.py --pull           # vault -> repo
python .claude/skills/brain-sync/scripts/sync_vault.py --push --dry-run
python .claude/skills/brain-sync/scripts/sync_vault.py --maintain       # unattended converge + vault auto-commit (the weekly heartbeat)
python .claude/skills/brain-sync/scripts/sync_vault.py --ingest-status  # wiki staleness (exit 1 = overdue; --json for machines)
python .claude/skills/brain-sync/scripts/sync_vault.py --mark-ingested  # reset the staleness baseline (last ingest step)
python .claude/skills/brain-sync/scripts/sync_vault.py --schedule-weekly  # register the weekly Task Scheduler heartbeat
python .claude/skills/brain-sync/scripts/sync_vault.py --selftest       # built-in convergence check
```

- **Ambiguous ask** ("sync the brain"): run `--check` first, show the report, then push/pull per what's newer. If both sides changed the same `context/` file, show both versions and let the user pick before overwriting.
- `decisions/log.md` needs no direction decision — either command converges both sides losslessly.

## Ingest (Claude-driven, not a script flag)

When evergreen knowledge changed — a new offer, case study, strategic call, positioning shift — after (or instead of) a push:

1. Identify what's new/changed (the push output, or the conversation itself).
2. Follow the vault's own Ingest workflow (vault `CLAUDE.md`): create/update the relevant `wiki/` pages with `[[wiki-links]]`, cite the source, update `wiki/index.md`, append one line to `wiki/log.md`.
3. Refresh `CRITICAL_FACTS.md` (vault root) if a ground-truth fact changed — keep it under ~40 lines, update its "Last updated" date. This file auto-loads into every repo session, so it IS the bridge; stale facts here are worse than missing ones.
4. Skip daily noise (lead lists, ephemeral chatter) — evergreen only.
5. **Reset the staleness baseline:** `python .claude/skills/brain-sync/scripts/sync_vault.py --mark-ingested` (writes `wiki/.ingest-state.json`). Skipping this leaves the detector reporting overdue forever.

**Staleness detector:** `--ingest-status` diffs the current skill set + decision log against that baseline (stale = any new skill, >5 new decisions, or >14 days). Surface it in the weekly `--maintain` log and this repo's session-closeout flow — the mirror staying in sync does NOT mean the wiki is current; they fail independently.

## Maintenance / consolidation (weekly or on ask)

"Maintain the brain" / "consolidate the brain" / the weekly scheduled run:
1. `--check`, resolve any drift.
2. Run the vault's Lint workflow (orphaned pages, broken `[[links]]`, claims contradicted by `decisions/log.md`).
3. Consolidate: merge duplicate wiki pages, fix temporal references ("yesterday" -> a date), prune contradicted facts from `CRITICAL_FACTS.md`.
4. Commit in the vault (`git -C "$OBSIDIAN_VAULT_PATH" add -A && git commit`) — the Graphify post-commit hook rebuilds the knowledge graph.

## Safety

- Never edit or delete past `decisions/log.md` entries — union merge only.
- Never copy raw operational data into the vault.
- If `--check` shows a conflict you can't order confidently (same file, both sides edited), ask — don't guess.

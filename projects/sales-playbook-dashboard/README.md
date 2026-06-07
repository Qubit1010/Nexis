# Sales Playbook Dashboard

One dashboard that drafts **LinkedIn and Instagram** outreach straight from the
NexusPoint `sales-playbook` skill — the single source of truth. It replaces the old
`instagram-dm-dashboard` / `linkedin-dm-dashboard` and the `*-dm-responder` skills,
which drifted from the playbook and produced AI-sounding, Voss-heavy copy.

Why this one sounds human: every generation loads the **opener archetypes** and the
platform's **worked example** into the system prompt (the old dashboards never did),
then filters every message against the playbook's **banned-phrase** list.

## Matrix

| | Cold Opener | Follow-up | Live Reply |
|---|---|---|---|
| **LinkedIn** | Connection note / first DM, archetype rotation, ≤300 chars | DM 2 (Day 4) / DM 3 (Day 9) / DM 4 (Day 16) | Paste a thread → next reply, 6-phase playbook |
| **Instagram** | Touch 1 DM, archetype rotation, ≤400 chars | Touch 2 (Day 3) / Touch 3 (Day 5) / Touch 4 (Day 7-14) | Paste a thread → next reply |

The output panel shows the message plus the move behind it (Archetype, or Phase +
Tactic, + a one-line Why). All sends are manual.

## Run locally

```bash
npm install
# add your key:
#   open .env.local and set ANTHROPIC_API_KEY=sk-ant-...
npm run dev
```

Open http://localhost:3000. Get an Anthropic key at
https://console.anthropic.com/settings/keys. Model: `claude-sonnet-4-6`.

## Keep the playbook in sync

The dashboard reads bundled copies of the playbook from `prompts/sales-playbook/`
(so it can deploy to Vercel, which can't reach `../../.claude/skills/` at runtime).
After you edit the canonical skill at `.claude/skills/sales-playbook/`, refresh the
copies:

```bash
npm run sync-playbook
```

The file list lives in `scripts/sync-playbook.mjs` and must stay in step with the
files `src/app/api/draft/route.ts` loads.

## Deploy to Vercel

```bash
vercel
vercel env add ANTHROPIC_API_KEY production   # paste the key when prompted
vercel --prod
```

`next.config.ts` already traces `prompts/**` into the serverless function, so the
bundled playbook ships with the deployment.

## Layout

```
src/app/
  page.tsx              # platform x mode UI
  api/draft/route.ts    # builds the system prompt from the playbook, calls Claude
prompts/sales-playbook/ # bundled copy of the canonical skill (via sync-playbook)
scripts/
  sync-playbook.mjs     # copies canonical playbook -> prompts/  (npm run sync-playbook)
  sync-playbook.ps1     # PowerShell wrapper
```

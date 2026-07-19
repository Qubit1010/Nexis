# Upwork Reply Drafter Dashboard

Paste an Upwork **client** message and get a sharp, research-backed reply — across the
whole relationship, not just the pitch. It's the delivery-side counterpart to the
`upwork-proposal-generator` (which wins the interview); this drafts everything after the
first client reply.

Drafts straight from the canonical **`upwork-reply-drafter`** skill (the single source of
truth), which is grounded in a cited 2026 corpus on Upwork client communication plus the
`sales-playbook` framework brain (Voss, Hormozi value equation, objection-psychology, the
human-not-AI filter).

## Situations × Job type

| Situation | Goal |
|---|---|
| **Pre-hire** | Answer questions / negotiate price·scope·timeline → win the contract without discounting |
| **Active project** | Status, feedback, scope-change requests → momentum + contain scope + protect JSS |
| **Closeout** | Delivery + the 5-star review ask + retainer opening |
| **Reactivation** | Re-open a dormant past client with a genuine reason + low-friction next step |

Job type (AI Services / Marketing Automation / Web Dev) tunes positioning and which
result to drop. Output shows the reply plus the move behind it (Situation · Move · Why).
All sends are manual.

Why it isn't generic: every situation's moves trace to `references/research-synthesis.md`
(GigRadar's 133K/2M-proposal data, the move-scope-never-rate discipline, JSS + review
mechanics), and every reply is filtered against the banned-phrase / AI-tell list.

## Conversation memory

Saves each client thread + stage + exchange count to a Supabase table
(`upwork_conversations`), so you can pick a conversation back up later. It's a separate
table from the sales-playbook `conversations` (Upwork stages differ). Fails soft: without
Supabase env, drafting still works and the memory panel shows an "off" note.

**One-time setup:** paste `.claude/skills/upwork-reply-drafter/scripts/schema.sql` into the
Supabase SQL Editor.

## Run locally

```bash
npm install
npm run sync-prompts          # bundle the skill brain into ./prompts
# add keys to .env.local:
#   ANTHROPIC_API_KEY=sk-ant-...        (primary; model claude-sonnet-4-6)
#   OPENAI_API_KEY=sk-...               (fallback; gpt-5.2)
#   SUPABASE_URL=...                    (optional — memory)
#   SUPABASE_SERVICE_ROLE_KEY=...       (optional — memory)
npm run dev
```

Open http://localhost:3000.

## Keep the playbook in sync

The dashboard reads bundled copies of the skill from `prompts/` (so it can deploy to
Vercel, which can't reach `../../.claude/skills/` at runtime). After editing the canonical
skill at `.claude/skills/upwork-reply-drafter/` (or the reused `sales-playbook` frameworks),
refresh the copies:

```bash
npm run sync-prompts
```

The file list lives in `scripts/sync-prompts.mjs` and must stay in step with the files
`src/app/api/draft/route.ts` loads.

## Deploy to Vercel

```bash
vercel
vercel env add ANTHROPIC_API_KEY production   # + OPENAI_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
vercel --prod
```

`next.config.ts` traces `prompts/**` into the serverless function, so the bundled brain
ships with the deployment.

## Layout

```
src/app/
  page.tsx                     # Situation × Job-type UI + memory + output
  api/draft/route.ts           # builds the system prompt from the brain, calls Claude → OpenAI
  api/conversations/route.ts   # Supabase memory CRUD (upwork_conversations)
src/lib/db.ts                  # PostgREST client + identity/exchange helpers
prompts/                       # bundled brain (via sync-prompts)
scripts/sync-prompts.mjs       # copies canonical skill + sales-playbook frameworks → prompts/
```

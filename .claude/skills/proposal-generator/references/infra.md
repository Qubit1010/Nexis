# Infrastructure

## How it fits together

```
client opens  https://<base_url>/p/<id>        static page, Vercel (project: nexuspoint-proposals)
   on load    POST /api/event {type: view}     logs a view (skipped with ?internal=1), returns signed state
   on sign    POST /api/event {type: sign}     validates against api/_manifest.js, inserts the signature
                         |
                         v
              Supabase  proposal_events         project jmfbbwxdguvbtflnwmos, service role only (RLS on, no policies)
                         |
                         v
              Resend    email to NOTIFY_EMAIL   first client view, and every signature
```

The function trusts nothing the browser sends except which option was picked and who is signing.
Ids, hashes, prices, option names and expiry all come from `api/_manifest.js`, which `deploy.py`
generates from the same derivation `render.py` used to build the page.

## Where things live

| What | Where | In git? |
|---|---|---|
| Skill, template, site skeleton | `.claude/skills/proposal-generator/` | yes |
| Each proposal (json, html, meta) | `client-projects/<slug>/proposals/<id>/` | no, gitignored, backed up by `gdrive-sync` |
| Brief per client | `client-projects/<slug>/proposals/brief.md` | no |
| Build and deploy dir | `projects/proposals-site/` | only its README and .gitignore. `.vercel/` holds the project link. |
| Site config (project, scope, base_url) | `assets/site-config.json` | yes, holds no secrets |

## One-time setup (done 2026-09-25, repeat only to rebuild)

1. Table: `python .claude/skills/proposal-generator/scripts/setup_db.py` (idempotent, uses `SUPABASE_DB_URL`).
2. First deploy links the project: `deploy.py` runs `vercel link --yes --project nexuspoint-proposals`
   in `projects/proposals-site/` when `.vercel/project.json` is missing.
3. Environment variables on the Vercel project, production:
   `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and for alerts `RESEND_API_KEY` + `NOTIFY_EMAIL`.
   Add with `vercel env add <NAME> production --scope qubit1010s-projects` from `projects/proposals-site/`,
   value on stdin. A new env var takes effect on the next deploy.
4. Put the production URL in `assets/site-config.json` as `base_url` (no trailing slash).

**Resend without a verified domain** sends only from `onboarding@resend.dev` and only to the email
the Resend account was created with. That is why alerts go to Aleem and nothing is emailed to the
client. Verifying a domain in Resend would allow a signed-copy email to the client later.

## What "deployed" means

`deploy.py` reports success only when every approved page is live at `<base_url>/p/<id>` with
the approved content hash in it and the noindex meta, and `/api/event` health returns
`supabase: ok` with the right proposal count. Anything short of that exits with ABORT and says why.

`POST /api/event {"type": "health"}` is safe to call any time. It writes nothing and returns
`{ok, proposals, supabase, email}`.

## Privacy

- Ids are `<company-slug>-<10 hex chars>`, 40 bits of randomness. Nothing lists proposals: the
  root page is a stub, there is no directory listing, and the manifest is bundled into the function
  rather than served.
- `noindex` in both the meta tag and the `X-Robots-Tag` header, `robots.txt` disallows everything,
  and `Referrer-Policy: no-referrer` keeps the URL out of Payoneer's and Google Fonts' logs.
- Anyone holding the link can see the page and, once signed, the signer's name, email and signature.
  Treat the link like the document itself.

## Failure modes

| Symptom | Cause | What happens |
|---|---|---|
| Supabase down during signing | network or project paused | the client sees "nothing was recorded, try again", never a false "signed" |
| Client signs an outdated tab after a redeploy | hash mismatch | rejected with "reload to see the latest version" |
| Two signatures race | unique index on `(proposal_id) where event_type = 'sign'` | the second gets the first's record back, shown as already signed |
| Signed proposal edited locally | hash differs from the signed one | `deploy.py` refuses to deploy anything |
| Supabase unreachable at deploy time | the signed-proposal guard cannot run | `deploy.py` refuses rather than deploying blind |
| Resend key missing or wrong | alerts not configured | signing still works; health shows `email: not_configured`; function logs the Resend error |
| `vercel` not found | npm shim not on PATH | `deploy.py` aborts; it resolves the shim with `shutil.which`, since a bare `"vercel"` fails in Python on Windows |

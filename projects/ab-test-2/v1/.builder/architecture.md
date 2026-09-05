---
project: ReplyLab
complexity: standard
stack: "Node 24 (native TS) + Express 5 + node:sqlite + React 19/Vite 7 + @anthropic-ai/sdk"
written: 2026-09-01
status: immutable
---

# Architecture — ReplyLab

## 1. Overview

A local workbench for drafting replies to inbound client enquiries and measuring whether the
drafting prompt is improving. One machine, one user, no auth, no network dependency except the
optional Anthropic API call.

Two processes in dev: Vite on **3200** (UI), Express on **4200** (API + SQLite). Vite proxies
`/api` to 4200, so the browser only ever talks to one origin and there is no CORS surface.

## 2. Complexity tier

**Standard.** Scored on the five dimensions:

| Dimension | Score | Note |
|---|---|---|
| Data | Medium | Three related tables, an append-only version table, and a non-trivial aggregate query |
| Auth | None | Single local user, no accounts. This is what keeps the tier out of "complex" |
| UI | Medium | Four views, real async state, an editable surface, a chart |
| Integrations | Low | One outbound API, behind an interface, optional |
| Scale | Trivial | Single user, local file DB |

Consequence downstream: integration tests over the real HTTP server for the core loop and the
measurement path, unit tests for the statistics; no E2E browser suite, no load work.

## 3. Tech stack

Copied from `blueprint.md` section 3. Not re-derived here. The rationale for each row lives in the
blueprint; this document does not get to change any of it.

## 4. Project structure

```
projects/ab-test-2/v1/
├── server/
│   ├── index.ts         entry: load config, open db, build app, listen on 4200
│   ├── app.ts           express app factory — takes deps, returns app (this is what tests drive)
│   ├── config.ts        project-local .env loading + provider selection inputs
│   ├── db.ts            node:sqlite open, schema DDL, seed of prompt version 1
│   ├── schemas.ts       zod request schemas
│   ├── routes.ts        all HTTP handlers, thin — they validate, call a service, shape a response
│   ├── drafter.ts       service: enquiry + active prompt version -> provider -> persisted draft
│   ├── scoreboard.ts    service: per-version aggregation, Wilson interval, edit-distance stats
│   ├── text.ts          word-level Levenshtein + keep-ratio
│   ├── pricing.ts       model id + per-token prices as data, and the cost estimator
│   └── providers.ts     DraftProvider interface, AnthropicProvider, StubProvider, selector
├── src/                 frontend
│   ├── main.tsx
│   ├── App.tsx
│   ├── api.ts           typed fetch client, mirrors section 6 exactly
│   ├── types.ts         shared response types
│   ├── styles.css       design tokens + all component styles
│   └── components/
│       ├── EnquiryList.tsx
│       ├── NewEnquiry.tsx
│       ├── DraftPane.tsx
│       ├── PromptPanel.tsx
│       └── Scoreboard.tsx
├── tests/
│   ├── api.test.ts          integration, real server over fetch
│   ├── scoreboard.test.ts   unit, Wilson + aggregation
│   ├── text.test.ts         unit, edit distance
│   └── providers.test.ts    unit, stub determinism + no-key selection
├── scripts/seed-demo.ts     opt-in demo data
├── index.html
├── vite.config.ts
├── tsconfig.json
├── package.json
└── .env.example
```

## 5. Database schema

SQLite, one file at `data/replylab.db` (gitignored). `PRAGMA foreign_keys = ON`.

```sql
CREATE TABLE prompt_versions (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  version       INTEGER NOT NULL UNIQUE,      -- 1, 2, 3 ... human-facing
  label         TEXT    NOT NULL,
  system_prompt TEXT    NOT NULL,
  created_at    TEXT    NOT NULL,
  is_active     INTEGER NOT NULL DEFAULT 0    -- exactly one row is 1
);

CREATE TABLE enquiries (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  subject    TEXT NOT NULL,
  body       TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE drafts (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  enquiry_id        INTEGER NOT NULL REFERENCES enquiries(id)       ON DELETE CASCADE,
  prompt_version_id INTEGER NOT NULL REFERENCES prompt_versions(id) ON DELETE RESTRICT,
  provider          TEXT    NOT NULL,   -- 'anthropic' | 'stub'
  model             TEXT    NOT NULL,
  generated_text    TEXT    NOT NULL,   -- immutable, what the model produced
  edited_text       TEXT,               -- null until the user edits
  rating            TEXT,               -- 'good' | 'bad' | null
  edit_distance     INTEGER,            -- word-level, generated vs edited
  edit_base_words   INTEGER,            -- denominator for keep-ratio
  input_tokens      INTEGER,
  output_tokens     INTEGER,
  latency_ms        INTEGER,
  created_at        TEXT NOT NULL,
  rated_at          TEXT
);
```

Two invariants the code enforces and the tests check:

1. `generated_text` is **never overwritten**. Editing writes `edited_text`. Losing the original
   would destroy the edit-distance signal.
2. `prompt_versions` rows are **never updated except `is_active`**. Changing prompt text always
   inserts a new version.

## 6. API contract

Base `/api`. All responses JSON. Errors are `{ "error": { "code": string, "message": string, "details"?: unknown } }`
with an appropriate status. All ids are integers.

| # | Method | Path | Request body | 2xx response |
|---|---|---|---|---|
| 1 | GET | `/api/health` | — | `{ ok: true, provider: "anthropic"\|"stub", model: string, hasApiKey: boolean, pricing: { inputPerMTok: number, outputPerMTok: number, source: string } }` |
| 2 | GET | `/api/enquiries` | — | `EnquirySummary[]` — `{ id, subject, bodyPreview, createdAt, draftCount, latestRating }` |
| 3 | POST | `/api/enquiries` | `{ subject: string(1..300), body: string(1..20000) }` | `201` `Enquiry` |
| 4 | GET | `/api/enquiries/:id` | — | `{ enquiry: Enquiry, drafts: Draft[] }` (drafts newest first) |
| 5 | POST | `/api/enquiries/:id/drafts` | — | `201` `Draft` — generates using the **active** prompt version |
| 6 | PATCH | `/api/drafts/:id` | `{ editedText?: string, rating?: "good"\|"bad"\|null }` (at least one key) | `Draft` |
| 7 | GET | `/api/prompts` | — | `PromptVersion[]` newest first |
| 8 | POST | `/api/prompts` | `{ systemPrompt: string(1..20000), label?: string(1..120) }` | `201` `PromptVersion` — new version, activated |
| 9 | POST | `/api/prompts/:id/activate` | — | `PromptVersion` |
| 10 | GET | `/api/stats` | — | `{ versions: VersionStat[], totals: Totals }` |

`Draft`:
```ts
{ id, enquiryId, promptVersionId, promptVersion, provider, model,
  generatedText, editedText, rating, editDistance, editBaseWords, keepRatio,
  inputTokens, outputTokens, latencyMs, costUsd, createdAt, ratedAt }
```

`VersionStat` (the measurement payload):
```ts
{ promptVersionId, version, label, createdAt, isActive,
  drafts, rated, good, bad, goodRate,          // goodRate null when rated === 0
  wilsonLow, wilsonHigh,                        // 95%, null when rated === 0
  enoughData,                                   // rated >= MIN_SAMPLE (5)
  editedCount, medianKeepRatio,                 // second signal
  avgLatencyMs, totalCostUsd }
```

`Totals`: `{ enquiries, drafts, rated, versions, minSample }`.

**Error codes:** `validation_error` (400), `not_found` (404), `provider_error` (502),
`internal_error` (500).

## 7. Frontend breakdown

Single page, three regions, plus a scoreboard view toggled in the header.

- `App` — owns the fetch of health/enquiries/prompts/stats and the selected enquiry id. One
  refresh function passed down; no state library needed at this size.
- `EnquiryList` — left rail. Shows subject, a body preview, draft count, and a rating dot.
- `NewEnquiry` — paste subject + body. Collapses into the rail when an enquiry is selected.
- `DraftPane` — the centre. The enquiry rendered as received, then the draft: read view, an
  edit mode with a textarea, good/bad buttons, and a metadata strip (version, provider, model,
  tokens, latency, cost). "Draft reply" / "Re-draft with v{n}" action.
- `PromptPanel` — the current prompt version's text, editable; saving creates a new version.
  Lists prior versions with an activate (roll back) action.
- `Scoreboard` — one row per prompt version: good-rate bar with a Wilson whisker, the counts, the
  keep-ratio, and an explicit "not enough data" state under the minimum sample.

Every async surface has loading, empty, error, and success states. Errors render next to the
control that caused them.

## 8. Backend breakdown

Layering: `routes.ts` (validate + shape) -> `drafter.ts` / `scoreboard.ts` (logic) -> `db.ts`
(prepared statements). No SQL in routes, no HTTP types in services.

- `providers.ts` exports `DraftProvider = { name, model, draft(input): Promise<DraftResult> }`.
  `selectProvider(config)` returns `AnthropicProvider` when a key is present, `StubProvider`
  otherwise. This one function is what makes the no-key requirement hold.
- `AnthropicProvider` calls `client.messages.create` with `model: claude-opus-5`,
  `thinking: { type: "adaptive" }`, `output_config: { effort: "medium" }`, no `budget_tokens`,
  no prefill. It maps SDK errors to a `provider_error`.
- `StubProvider` derives a deterministic reply from a hash of (system prompt + subject + body) so
  the same inputs always produce the same draft, which is what makes the integration tests stable.
  Its output is prefixed with a visible stub marker.
- Middleware: `express.json({ limit: '1mb' })`, a zod validation helper, and a terminal error
  handler that maps `AppError` to the contract's error shape and anything else to a 500 with the
  detail logged, not returned.

## 9. Environment variables

| Var | Required | Default | Purpose |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | No | unset | When absent the app runs on the stub provider. This is the requirement, not a fallback hack |
| `PORT` | No | `4200` | API port |
| `REPLYLAB_DB` | No | `data/replylab.db` | DB path. Tests point this at a temp file |
| `REPLYLAB_MODEL` | No | `claude-opus-5` | Escape hatch only. Default comes from `pricing.ts` |

Loaded from `./.env` **in this directory only**. The parent repo's `.env` is deliberately not on
the search path.

## 10. Implementation order

1. `pricing.ts`, `text.ts`, `providers.ts` — pure, no I/O, testable immediately
2. `db.ts` schema + seed
3. `scoreboard.ts`
4. `drafter.ts`, `schemas.ts`, `routes.ts`, `app.ts`, `index.ts`
5. Frontend tokens, then components
6. Tests
7. Review, fix, polish

## 11. Known limits (recorded, not hidden)

- Ratings across versions are **observational, not an experiment**. Different versions may have
  been rated on different enquiries. The scoreboard shows counts and intervals so the user can see
  when a comparison is thin, but it does not control for enquiry mix. A replay harness would; see
  the completion report for why that was left out.
- `node:sqlite` emits an ExperimentalWarning on Node 24. Suppressed in the npm scripts.
- No token counting before the call, so `costUsd` is computed from the response `usage` and is
  therefore null for stub drafts.

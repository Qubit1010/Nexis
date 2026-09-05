---
source: derived from the user brief (no existing blueprint supplied)
received: 2026-09-01
mode: problem-first (developer-advisor doctrine applied inline)
---

# Blueprint — ReplyLab

## 1. The problem, stated plainly

Three requirements, only one of which is a "reply drafter":

1. **Draft.** Given an inbound enquiry (subject + body), produce a reply in the user's voice.
2. **Review.** Show the draft, let the user edit it, let the user mark it good or bad.
3. **Measure.** Tell the user whether drafting is getting **better or worse over time as they change the prompt**.

(3) is the load-bearing requirement and it changes the architecture. It means the prompt is not a
constant in a source file — it is **versioned data**, every draft is **attributed** to the exact
prompt version that produced it, and ratings **aggregate per version**. Without that, ratings are
uninterpretable: you cannot say a prompt got better if you cannot say which prompt wrote what.

Hard constraint: **must run and be fully testable with no API key.** So the model call sits behind
a provider interface with a deterministic offline implementation, selected at runtime.

## 2. What this is NOT

Not a mail client. It does not connect to Gmail/IMAP, does not send anything, has no auth, no
multi-user, no deploy target. Enquiries are pasted in. Single local user, single machine.

## 3. Stack, derived from the problem

| Layer | Choice | Why this, from the problem |
|---|---|---|
| Runtime | Node 24 (native TypeScript) | Node 24 executes `.ts` directly by type-stripping, so no `tsx`, `ts-node`, or build step for the server. Types are required by the code standards; this gets them for zero tooling. |
| Data | `node:sqlite` (Node standard library) | Local single-user, tens-to-thousands of rows, needs durable relational attribution (draft to prompt_version). SQLite is exactly this shape. It is in the standard library on Node 24, so zero dependency and, critically, no native compile step that could fail on Windows. A server DB (Postgres/Supabase) would add an install the problem does not justify; JSON files would lose the relational join the scoreboard is built on. |
| API | Express 5 | ~11 endpoints needing routing, JSON body parsing, and an error middleware. Hand-rolling that on `node:http` is worse code, not less. |
| Validation | zod | The security baseline requires schema validation at the boundary. |
| LLM | `@anthropic-ai/sdk`, model `claude-opus-5` | See section 4. |
| Frontend | React 19 + Vite 7 (TypeScript) | Four interactive views with real async state: enquiry list, draft edit/rate surface, prompt version editor, scoreboard. Vanilla DOM would mean hand-written state sync; this is the ecosystem norm for the shape. Vite proxies `/api` to the backend in dev. |
| Tests | Vitest | The TS/JS ecosystem default. Node's global `fetch` tests the real HTTP server, so no `supertest`. |
| Hosting | None. Local only. | The brief says "runs locally". No Docker, no deploy config. |

**No house stack was applied.** Postgres, Supabase, Next.js, and Tailwind were all considered and
rejected as heavier than the problem.

## 4. The model decision

Provider: Anthropic. The `claude-api` skill was consulted before writing any model string
(mandatory per its trigger rules: LLM-shaped task, no provider named in the brief, and a provider
grep over the target project could not hit because the project did not exist yet).

- **Model ID: `claude-opus-5`.** The skill's instruction is explicit and non-negotiable: use
  `claude-opus-5` unless the user names a different model. The user named none. Never downgrade
  for cost, that is the user's call and not the builder's.
- **Pricing: $5.00 per 1M input tokens, $25.00 per 1M output tokens.** Read from the "Current
  Models" table in the `claude-api` skill, which is marked *cached: 2026-06-24*. It is a cached
  table, not a live lookup.
- API shape per the skill: `thinking: {type: "adaptive"}`, no `budget_tokens` (400 on Opus 5),
  no assistant prefill (400), `output_config.effort` for depth.
- The model ID and both prices are written into the code as data (`server/pricing.ts`) so the app
  can show a per-draft cost estimate rather than the number living only in a doc.

## 5. Measurement design (the core mechanism)

- `prompt_versions` are **append-only and immutable**. "Editing the prompt" creates version N+1.
  A rating can therefore always be traced to the exact text that produced the draft.
- Every `draft` row stores `prompt_version_id`, provider, model, tokens, latency.
- The scoreboard aggregates per version: drafts, rated, good, bad, good-rate.
- **Small-n honesty is a requirement, not a nicety.** A 1-of-1 version is not a 100% prompt. The
  scoreboard computes a 95% **Wilson score interval** and renders it as a whisker, and flags
  versions under a minimum sample as "not enough data". Ranking uses the interval's lower bound.
- **Second signal, no click required: edit distance.** When the user edits a draft, the app stores
  word-level Levenshtein distance from the generated text. "How much did he rewrite it" is a
  quieter but denser quality signal than a thumb, and it is free to collect.
- Re-drafting an enquiry under a newer prompt version is allowed, producing naturally paired
  comparisons on the same input.

## 6. Best-practices checklist

- Test shape: **testing trophy** — integration tests through the real HTTP server against a
  temp-file SQLite DB, thin unit layer for the statistics and edit-distance maths.
- No secrets in source; `.env.example` only; project-local env loading that must not inherit the
  parent repo's `.env`.
- Provider selection is explicit and surfaced in the UI, so a stub draft is never mistaken for a
  real one.

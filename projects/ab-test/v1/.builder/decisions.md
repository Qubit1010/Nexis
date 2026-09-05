---
project: LeadQ
append_only: true
---

# Decision Log

[2026-08-31] DECISION: SQLite via the Node 24 built-in `node:sqlite`, not Postgres and not better-sqlite3. | REASONING: The blueprint's hard constraint is "runs locally, one user". Postgres would make a solo operator install and run a server for a few hundred rows; better-sqlite3 is a native module that has to compile on Windows. `node:sqlite` is in the runtime, so the data layer costs zero dependencies and has no build step that can fail. Verified working (DatabaseSync, prepare, run, all) before adoption. | CONTEXT: Phase 0/1. Deviates from the scoreboard's "Postgres is the relational default", which assumes a multi-user server app. Tradeoff accepted: the module prints an ExperimentalWarning in Node 24, and it rules out Vercel serverless as a deploy target. Isolated behind lib/db.ts so the swap is one file.

[2026-08-31] DECISION: No ORM. Hand-written parameterized SQL in two repository modules. | REASONING: Eleven queries total. Drizzle or Prisma would add a dependency, a schema DSL, a codegen step and a migration runner to replace under 100 lines of SQL. The security requirement is parameterized statements, which prepared statements satisfy directly. | CONTEXT: Phase 1, code-standards "a few lines beats a new dependency".

[2026-08-31] DECISION: One Next.js process serving both the UI and the API. No separate backend on :4000. | REASONING: Seven endpoints, one user, one deployable. A second process would add CORS, a second deploy target, duplicated types and a network hop for zero benefit. Splitting later is a directory move because all SQL is already behind lib/ repositories. | CONTEXT: Phase 1. The run instruction offered port 4000 "for any backend"; there is deliberately no backend process, so :3000 is the only port used.

[2026-08-31] DECISION: REST route handlers instead of React Server Actions for every mutation. | REASONING: Server Actions are the more idiomatic Next choice for a form, but they cannot be invoked in a test without a Next request context. An explicit HTTP contract is directly testable, is verifiable by the review phase against architecture section 6, and survives a future frontend/backend split. | CONTEXT: Phase 1. Cost: slightly more client-side fetch code than Server Actions would need.

[2026-08-31] DECISION: `requireAdmin()` reads the session cookie from the `Request` object, not from `next/headers`. | REASONING: `cookies()` throws outside a Next request scope, which would make every admin route handler untestable without mocking the framework. Reading `req.headers.get('cookie')` keeps handlers as pure `(Request) => Response` functions. `next/headers` is still used in the dashboard layout, which is not under test. | CONTEXT: Phase 1, testability.

[2026-08-31] DECISION: Auth is re-checked inside every admin route handler, not only in the dashboard layout. | REASONING: The layout gate protects pages, not the API. A missed gate on an API route is the exact failure mode code-standards calls out ("authz on every mutation"). Two independent checks, neither relying on the other. | CONTEXT: Phase 1/4 security baseline.

[2026-08-31] DECISION: Plain CSS with CSS Modules and hand-authored tokens, no Tailwind, no component library. | REASONING: Next ships CSS Modules. A utility framework would add a dependency and a config surface in exchange for a more template-looking result, and this pipeline has an explicit anti-generic bar. Full control over the token system was worth more here than utility velocity. | CONTEXT: Phase 1/2.

[2026-08-31] DECISION: System font stacks with a mono face for all numerals, instead of a webfont. | REASONING: `next/font/google` fetches at build time, which makes `next build` fail without network and slows every cold build. The design register (a precise instrument panel) is carried by type scale, weight contrast, negative tracking and tabular numerals rather than by a distinctive face, so the constraint costs little. | CONTEXT: Phase 2. Honest tradeoff: this is the one place the design is more constrained than it would be with a licensed face.

[2026-08-31] DECISION: Scores, bands and breakdowns are denormalized onto the lead row and recomputed for every lead when the rule set is saved. | REASONING: The dashboard sorts by score, which should be a SQL ORDER BY rather than an in-memory sort of recomputed values. The cost is a consistency obligation, discharged by making `rescoreAll()` run in the same transaction as `replaceRules()`. | CONTEXT: Phase 1. At hundreds of rows a full rescore is instant; at 100k rows it would need a job.

[2026-08-31] DECISION: The rules engine is additive with stacking tiers, and shows its work. | REASONING: A rule set where "budget >= 10k" and "budget >= 5k" both fire is surprising if hidden. Rather than build range operators or rule precedence, every lead stores which rules fired and what each contributed, and the dashboard shows it. Transparency was cheaper and more useful than a cleverer engine. | CONTEXT: Phase 1.

[2026-08-31] DECISION: The public POST response does not include the computed score. | REASONING: The score is internal qualification. Returning it would leak the rule set's shape to anyone who can probe the form. | CONTEXT: Phase 4.

[2026-09-01] DECISION: Dashboard and rules pages read via the repositories server-side instead of fetching their own HTTP endpoints. | REASONING: A server component fetching its own API over localhost on first paint is a wasted round trip. The endpoints still exist, are still authorized, and carry every client-side mutation and refresh, so the contract is real rather than decorative. | CONTEXT: Phase 3/6. Logged because it is a visible deviation from a literal reading of architecture section 6.

[2026-09-01] DECISION: No jsdom, no Testing Library, no Playwright. | REASONING: The route handlers are testable directly as (Request) => Response, which covers the real seams. Component rendering tests would add a dependency and a second runner to cover three presentational screens for one user. The cost is that the client-side sort/filter in triage.tsx is genuinely untested, which is recorded in test-plan.md section 3 rather than hidden. | CONTEXT: Phase 5.

[2026-09-01] DECISION: The error summary box uses a hairline border, not a coloured left tab. | REASONING: The design hook flagged the 3px side border as the standard AI-generated-UI tell, and it contradicted this system's own rule that surfaces separate with hairlines rather than slabs. Now matches the field-level error language (mono "/" marker). | CONTEXT: Phase 6 review, design fix 3.

[2026-09-01] DECISION: Removed --shadow-pop, --copper-wash, --slate-wash, --r-md, --z-menu and --z-dialog from the token set. | REASONING: Tokens for components this product does not have. The scoring receipt was built as an inline expanded row rather than the floating popover design-system.md anticipated, so the elevation token had no user. Speculative tokens are the CSS version of speculative abstraction. | CONTEXT: Phase 6 polish. Noted as design-system drift in review-report.md.

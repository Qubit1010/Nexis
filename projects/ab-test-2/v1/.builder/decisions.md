# Decision Log (append-only)

[2026-09-01] DECISION: Ran the Phase 0 blueprint derivation inline instead of spawning `developer-advisor` as a subagent | REASONING: The brief is small and fully specified; the doctrine that matters (problem-first, no house stack) is applied directly and recorded in blueprint.md section 3. Spawning a cold agent to re-derive a three-requirement brief costs more than it returns | CONTEXT: Phase 0, --auto run

[2026-09-01] DECISION: Consulted the `claude-api` skill before writing any model ID or price | REASONING: Its trigger rules mandate it for an LLM-shaped task with no provider named, and the provider grep over the target project could not hit because the project did not exist yet. Model IDs and pricing must never come from memory | CONTEXT: Phase 0

[2026-09-01] DECISION: `node:sqlite` (stdlib) over `better-sqlite3` | REASONING: Zero dependency and no native compile step, which is the main install-failure mode on Windows. Cost: Node prints an ExperimentalWarning, suppressed with `--disable-warning=ExperimentalWarning` in the npm scripts | CONTEXT: Phase 1, stack

[2026-09-01] DECISION: Node 24 native TypeScript type-stripping for the server; no bundler and no `tsx` | REASONING: Verified `node file.ts` runs directly on Node 24.14.0 with no flag. Removes a dependency and a build step. Cost: server code must use erasable syntax only, so no enums and no parameter properties | CONTEXT: Phase 1, tooling

[2026-09-01] DECISION: Prompt versions are immutable and append-only | REASONING: This is what makes the "getting better or worse" question answerable. A mutable prompt row would silently re-attribute old ratings to new text | CONTEXT: Phase 1, data model

[2026-09-01] DECISION: The scoreboard reports a 95% Wilson score interval and a minimum-sample flag, not a bare good-rate | REASONING: With n of 1 to 5 a raw percentage is noise. Presenting it unqualified would actively mislead the one decision this app exists to support | CONTEXT: Phase 1, measurement

[2026-09-01] DECISION: Project-local `.env` loading only; the parent repo's `.env` is never read | REASONING: The repo root `.env` contains a real ANTHROPIC_API_KEY. Inheriting it would have made the no-key requirement untestable and would silently spend money | CONTEXT: Phase 4, config

[2026-09-01] DECISION: Word-level Levenshtein rather than character-level for edit distance | REASONING: Cheaper (drafts are ~200-400 words, not ~2000 characters) and the number means something a human can act on, namely how many words were rewritten | CONTEXT: Phase 4, scoreboard

[2026-09-01] DECISION: Demo data is an opt-in script (`npm run seed:demo`), never seeded automatically | REASONING: The scoreboard needs rated history to be visible at all, but auto-seeding fabricated ratings into the user's real database would corrupt the measurement the app exists to provide. Opt-in and clearly labelled is the honest version | CONTEXT: Phase 5

[2026-09-01] DECISION: Committed to a single deliberate light "correspondence" theme plus a dark-scheme token override, rather than a themed design system | REASONING: The app is a local single-user instrument. The design budget goes into the two surfaces that carry the product, the letter-like drafting pane and the version scoreboard, rather than into breadth | CONTEXT: Phase 2, design

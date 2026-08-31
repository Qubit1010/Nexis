# Research corpus pipeline (for research-backed skills)

The mechanics for building a cited corpus with NotebookLM. Moved here 2026-08-31 from
`.claude/rules/research-backed-skills.md`, which was carrying exact CLI invocations into
context on every turn for a workflow that runs a handful of times a year. **The principle
still lives in that rule; this is only the how.**

Run via PowerShell with the full exe path. Paths and login are in the
`reference-notebooklm-setup` memory.

## The passes

1. **One notebook per topic:** `notebooklm create "<Topic> <Year>"`.
2. **Several deep research passes,** importing cited sources:
   `source add-research "<focused query>" --mode deep --no-wait`
   then `research wait --import-all --cited-only --timeout 1800`.
   Batch the passes in a background script.
3. **Synthesize with citations:** one `ask "<question>" --json` per sub-topic. The JSON returns
   `answer` (with inline `[n]`) plus a `references[]` array mapping `citation_number ->
   source_id`. That mapping is the traceability.
4. **Build the audit trail** in the skill's `_research/`: a deduped `sources.json` (global index
   plus `uuid_to_index`) and the raw `q*.json` answers.

## Gotchas

- `Out-File -Encoding utf8` writes a BOM. Parse the JSON with `utf-8-sig`, not `utf-8`.
- **There is an undocumented ~100-source-per-notebook cap on this account.** When it is hit,
  imports fail with a generic RPC error that looks exactly like an auth failure. Check for the
  cap and for duplicate URLs *before* concluding auth is broken. `seo-advisor` had to split its
  320-source corpus across 6 notebooks for this reason.
- **Never run a destructive command (`source clean`, `delete`) without asking first**, even
  mid-debugging, even when the notebook looks obviously full of duplicates. It silently drops
  source UUIDs that existing `[n]` citations point at. This has already broken 5 live citation
  links once.

## If NotebookLM is down

Do not let an outage stall the research-first standard. Fall back to a direct Exa full-text
pass (`exa-py`), with the same citation rigor: save the raw sources and build the same
`sources.json` audit trail, then synthesize from that. Importing the same sources into
NotebookLM later is optional and is not required to unblock the skill.

## Keeping a corpus fresh

Notebooks persist in the Google account, so a corpus can be refreshed with a new deep pass when
benchmarks age. Offer a quarterly refresh. The live fallback
(`references/notebook-live-query.md` in each research-backed skill) only surfaces detail already
inside the locked corpus; genuinely new sources need a fresh pass.

# Research-Backed Skills

When building a new **advice or knowledge skill** (one that gives strategy, benchmarks, or "best practice"), do the research FIRST. Don't ship opinions as fact. Does NOT apply to pure execution skills that just move data.

## Principle
Every load-bearing claim or number traces to a real, current source. Named frameworks are allowed where research validates them, labeled as such. No source for a number = say so, never invent.

## Method
1. Discover sources with Exa (semantic search).
2. Optionally ingest into a NotebookLM notebook for a live fallback.
3. Build `_research/sources.json` (cited index) + `references/research-synthesis.md` (inline `[n]` citations + honest "Not in sources" flags).
4. Lead with the evidence, then the tactic.
5. Wire `references/notebook-live-query.md`: when local refs don't answer, query the notebook, then append the cited answer back.

Reference implementations: the research-backed skills in this OS once built.

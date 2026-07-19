# Live Query Fallback

When `research-synthesis.md` + `situations.md` + `upwork-mechanics.md` don't confidently answer a specific Upwork-communication question (a benchmark, an objection nuance, a policy detail), **research it live before guessing** — don't invent a number or a "best practice."

## How

1. **Primary — the `research` skill / Exa** (NotebookLM auth was expired 2026-07-14, so this is the working tier). Run a light/medium research pass on the specific question, or directly:
   ```
   python tools/exa/exa_client.py answer "<the specific Upwork question>" --model exa
   ```
   Prefer 2025-2026 sources; keep the same citation rigor.
2. **Optional — NotebookLM.** If its auth is restored, create/reuse an "Upwork Client Communication 2026" notebook and `ask --json` (see `reference-notebooklm-setup` memory for the exe path + login + `utf-8-sig` BOM gotcha).

## Then

- Present the cited answer.
- **Append it to `research-synthesis.md` under "Live Query Additions"** with its source URL, so it's reusable and the corpus stays current without re-running the whole pipeline.
- Re-run `_research/gather.py` only when the whole corpus needs a refresh (benchmarks age); a single new question uses this fallback.

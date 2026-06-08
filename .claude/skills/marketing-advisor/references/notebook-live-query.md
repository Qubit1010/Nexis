# Live NotebookLM Fallback (Ask the Marketing Notebook)

**Purpose:** When a marketing question isn't answered by the loaded reference files or `research-synthesis.md`, don't say "I don't know" - query the live **Marketing 2026** NotebookLM notebook (the same 234-source corpus the synthesis was built from) and check for a relevant answer. Then append the result to `research-synthesis.md` (its "Live Query Additions" section) so the corpus grows and the next identical question is answered instantly from disk.

This keeps the skill current without re-running the whole research pipeline.

---

## When to trigger

Run the live fallback when ALL of these are true:
1. The user asked a specific marketing question (LinkedIn/IG/email/content/ICP/offer/ads/martech, or a 2026 benchmark/tactic).
2. After loading the relevant reference file(s) + scanning `research-synthesis.md`, you **don't have a confident, specific answer**.
3. It's a knowledge question (not a "write the copy" request - that goes to sales-playbook).

Do NOT run it for things already well covered (check `channel-benchmarks.md` + the matching playbook first - most questions are already answered there).

---

## The operation

**Notebook:** `Marketing 2026 - What Works (NexusPoint)`
**Notebook ID:** `0cde1fba-0e93-4068-8d2a-6519e3f40ac0`
**CLI (run via PowerShell, full path):** `C:\Users\qubit\AppData\Local\Programs\Python\Python312\Scripts\notebooklm.exe`

Ask the notebook (use `--json` to get citations; `-n` pins the notebook so context is right):

```powershell
& "C:\Users\qubit\AppData\Local\Programs\Python\Python312\Scripts\notebooklm.exe" `
  ask "<the user's question, phrased to pull specifics and numbers>" `
  --json -n 0cde1fba-0e93-4068-8d2a-6519e3f40ac0
```

Phrase the question to extract specifics: add "Give specific 2026 numbers, formatting, and tactics, and cite sources." Write the JSON to a temp file if it's large, then read it (note: `Out-File -Encoding utf8` writes a BOM, so if you parse it in Python use `utf-8-sig`).

The JSON returns:
- `answer` - prose with inline `[n]` citations (already contains the specifics).
- `references[]` - each `{citation_number, source_id, cited_text}`. Resolve `source_id` -> global index/URL via `_research/sources.json` (`uuid_to_index` + `sources`).

If the answer is empty or unhelpful, the corpus genuinely doesn't cover it - say so and offer a fresh `deep-research` run or a new NotebookLM research pass (see the rebuild process), rather than guessing.

---

## Decision flow (every knowledge question)

1. **Load** the mode's reference file(s) + `channel-benchmarks.md`. Answer if covered.
2. **Scan** `research-synthesis.md` (the right Q section) for the specific number/tactic. Answer if found.
3. **Miss? Run the live query** above against the notebook.
4. **Present** the answer, leading with the specific number/tactic, citing sources (resolve `[n]` to titles/URLs via `sources.json` when the user wants the source).
5. **Log it** in `research-synthesis.md`, under the **"Live Query Additions"** section at the bottom (append a dated entry tagged to the relevant Q section). That file is the single growing source of truth, so the next identical question is answered from it in step 2 - no re-query.
6. **Honesty:** a live answer can surface sources NOT in our original 234. If a stat is net-new (its `source_id` isn't in `sources.json`), say it came from a fresh notebook query, not the locked corpus. Never invent a number.

---

## Auth / troubleshooting

- If the CLI errors with "Authentication expired", run `notebooklm login` (opens a browser; auto-saves on Google sign-in as hassanaleem86@gmail.com). See the [[reference-notebooklm-setup]] memory for paths.
- Run from PowerShell, not Bash (Python isn't on the Bash PATH here).
- `ask` continues the last conversation by default; that's fine. Use `--new -y` only if context bleed is a problem.

---

## Where findings get saved

Live-query results are appended to **`research-synthesis.md` -> "Live Query Additions"** (a dated section at the bottom of the master synthesis), NOT here. Keeping everything in one file means step 2 of the decision flow (scan `research-synthesis.md`) catches it next time, so you never re-query the same question.

Format per entry: `### [YYYY-MM-DD] (Q# - Topic) <question>` then the answer's key specifics in bullets, then a Source line noting it came from the notebook and which Q-section sources back it.

# Live NotebookLM Fallback (Ask the Sales Notebook)

**Purpose:** When a sales question isn't answered by the playbook's framework/script/reference files or `references/research-synthesis.md`, don't guess - query the live **NexusPoint Sales Playbook Research** NotebookLM notebook (the same corpus the synthesis was built from) and check for a relevant answer. Then append the result to `references/research-synthesis.md` (its "Live Query Additions" section) so the corpus grows and the next identical question is answered instantly from disk.

This keeps the playbook current without re-running the whole research pipeline. (Mirrors the marketing-advisor skill's live fallback.)

---

## When to trigger

Run the live fallback when ALL of these are true:
1. The user asked a specific sales KNOWLEDGE question (openers, reply/connection rates, objection handling, closing, discovery-call structure, cold-outreach timing, a benchmark or a "what does the research say about X").
2. After checking the relevant framework/script file + scanning `references/research-synthesis.md` (Q1 Openers, Q2 LinkedIn, Q3 Instagram, Q4 Closing, Q5 Objections, Q6 Human-vs-AI, Q7 Ask Timing, Q8 Facebook, Q9 Stalled Threads), you **don't have a confident, specific answer**.
3. It's a knowledge question - NOT "write me the DM/script" (that's generated from the archetypes + scripts as usual).

Do NOT run it for things already covered (check the frameworks/scripts + research-synthesis.md first - most asks are already answered there).

---

## The operation

**Notebook:** `NexusPoint Sales Playbook Research`
**Notebook ID:** `f5ad3db7-87ee-4e2d-b674-3f977e797bb2`
**CLI (run via PowerShell, full path):** `C:\Users\qubit\AppData\Local\Programs\Python\Python312\Scripts\notebooklm.exe`

Ask the notebook (use `--json` for citations; `-n` pins the notebook):

```powershell
& "C:\Users\qubit\AppData\Local\Programs\Python\Python312\Scripts\notebooklm.exe" `
  ask "<the user's question, phrased to pull specifics and numbers>" `
  --json -n f5ad3db7-87ee-4e2d-b674-3f977e797bb2
```

Phrase the question to extract specifics ("Give specific numbers, scripts, and tactics, and cite sources."). Write large JSON to a temp file, then read it (note: `Out-File -Encoding utf8` writes a BOM - parse with `utf-8-sig` in Python).

The JSON returns `answer` (prose with inline `[n]` citations) and `references[]` (`{citation_number, source_id, cited_text}`). Resolve `source_id` -> title/URL via `_research/sources.json` (match the `id` field of each source).

If the answer is empty or unhelpful, the corpus genuinely doesn't cover it - say so and offer a fresh `deep-research` run or a new NotebookLM research pass, rather than guessing.

---

## Decision flow (every sales knowledge question)

1. **Check** the relevant framework/script file (`opener-archetypes.md`, `objection-riffs.md`, `discovery-call-script.md`, etc.). Answer if covered.
2. **Scan** `references/research-synthesis.md` (the right Q section) for the specific number/tactic. Answer if found.
3. **Miss? Run the live query** above against the notebook.
4. **Present** the answer, leading with the specific tactic/number, citing sources (resolve `[n]` via `_research/sources.json` when the user wants the source).
5. **Log it** in `references/research-synthesis.md`, under the **"Live Query Additions"** section at the bottom (append a dated entry tagged to the relevant Q section). That file is the single growing source of truth, so step 2 catches it next time - no re-query.
6. **Honesty:** never invent a number. If a stat is net-new (its `source_id` isn't in `_research/sources.json`), say it came from a fresh notebook query, not the locked corpus.

---

## Auth / troubleshooting

- If the CLI errors with "Authentication expired", run `notebooklm login` (opens a browser; auto-saves on Google sign-in as hassanaleem86@gmail.com). See the [[reference-notebooklm-setup]] memory for paths. NotebookLM sessions expire often - expect to re-login periodically.
- **Resolved 2026-07-04:** 22 of the 34 curated Q6-Q9 URLs are now in the notebook (12 fail consistently with `RPCError rpc_code=9` across three attempts - bot-blocked or JS-rendered pages, not an auth issue). `_research/sources.json` resolves 192/210 Q1-Q9 citation instances; 5 unique source UUIDs (Q1 citations 9,10,12,13,14,16,26 and Q3 citations 5,6,9,11,12,17,24,30,32,34) no longer resolve because a `source clean` dedup pass removed them - the underlying claims in `research-synthesis.md` are still valid prose, just without a live-resolvable URL in the index.
- Run from PowerShell, not Bash (Python isn't on the Bash PATH here).
- `ask` continues the last conversation by default; that's fine. Use `--new -y` only if context bleed is a problem.

---

## Where findings get saved

Live-query results are appended to **`references/research-synthesis.md` -> "Live Query Additions"** (a dated section at the bottom of the master synthesis), NOT here. Keeping everything in one file means step 2 of the decision flow catches it next time, so you never re-query the same question.

Format per entry: `### [YYYY-MM-DD] (Q# - Topic) <question>` then the answer's key specifics in bullets, then a Source line noting it came from the notebook and which Q-section sources back it.

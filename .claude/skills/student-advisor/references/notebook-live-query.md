# Live NotebookLM Fallback (Ask the Student-Success Notebook)

**Purpose:** When an advice question isn't answered by the loaded reference files or
`research-synthesis.md`, don't guess and don't answer from stale memory — query the live
**Student Success & Learning Science 2026** NotebookLM notebook (the same cited corpus the synthesis
was built from) and check for a current, sourced answer. Then append the result to
`research-synthesis.md` (its "Live Query Additions" section) so the corpus grows and the next
identical question is answered instantly from disk.

This matters most for the **time-sensitive** parts of the advice half: AI/CS job market, salaries,
scholarship deadlines and amounts, study-abroad visa/PR rules, and program requirements. The
learning-science material (retrieval practice, spacing, etc.) is stable and almost always already in
the references, so it rarely needs a live query.

This is for the **advice half only**. The tutor half (roadmaps, learn-anything) is generative — for
current sources there, hand off to `deep-research` / `assignment-research`, not this notebook.

---

## When to trigger

Run the live fallback when ALL of these are true:
1. The user asked a specific advice question (a number, a benchmark, a scholarship detail, a job-market
   fact, a program requirement, a "is X still true / what's the current figure").
2. After loading the relevant reference file(s) + scanning `research-synthesis.md`, you **don't have a
   confident, specific, current answer**.
3. It's a knowledge question (not a tutor/roadmap request, and not "save this to Google Docs").

Do NOT run it for things already covered (check the matching playbook + the right Q section of
`research-synthesis.md` first). Do run it before falling back to memory on anything date-, price-,
deadline-, or market-sensitive, since those age fast.

---

## The operation

**Notebook:** `Student Advisor - Curated Sources 2026` (built from Exa-curated, hand-vetted sources)
**Notebook ID:** `ffcd6d51-673d-4308-9400-c01976e3a849`
**CLI (run via PowerShell, full path):** `C:\Users\Aleem\AppData\Local\Programs\Python\Python313\Scripts\notebooklm.exe`
(If that path moves, the build script `_research/build_corpus.py` resolves the exe via `find_exe()`.)

Ask the notebook (use `--json` to get citations; `-n` pins the notebook):

```powershell
& "C:\Users\Aleem\AppData\Local\Programs\Python\Python313\Scripts\notebooklm.exe" `
  ask "<the user's question, phrased to pull specifics and numbers>" `
  --json -n ffcd6d51-673d-4308-9400-c01976e3a849
```

Phrase the question to extract specifics: add "Give specific numbers, named programs/techniques,
effect sizes where relevant, and cite sources." If the output is large, write it to a temp file and
read it (note: `Out-File -Encoding utf8` writes a BOM, so parse JSON with `utf-8-sig`).

The JSON returns:
- `answer` — prose with inline `[n]` citations (already contains the specifics).
- `references[]` — each `{citation_number, source_id, cited_text}`. Resolve `source_id` to a global
  index/URL via `_research/sources.json` (`uuid_to_index` + `sources`).

If the answer is empty or unhelpful, the corpus genuinely doesn't cover it — say so, and offer a
fresh deep-research pass (`python _research/build_corpus.py research <q_key>` to add sources, then
`synthesize`), rather than guessing.

---

## Decision flow (every advice knowledge question)

1. **Load** the mode's reference file(s). Answer if covered.
2. **Scan** `research-synthesis.md` (the right Q section) for the specific number/fact. Answer if found.
3. **Miss? Run the live query** above against the notebook.
4. **Present** the answer, leading with the specific number/fact, citing sources (resolve `[n]` to
   titles/URLs via `sources.json` when the user wants the source).
5. **Log it** in `research-synthesis.md`, under the **"Live Query Additions"** section at the bottom
   (a dated entry tagged to the relevant Q section). That file is the single growing source of truth,
   so the next identical question is answered from it in step 2 — no re-query.
6. **Honesty:** a live answer can surface sources NOT in the original corpus. If a fact is net-new
   (its `source_id` isn't in `sources.json`), say it came from a fresh notebook query, not the locked
   corpus. Never invent a number, deadline, program name, or salary figure.

---

## Auth / troubleshooting

- If the CLI errors with "Authentication expired" / token-fetch fails, run `notebooklm login` (opens
  a browser; sign in to the Google account that owns the notebook). The static `auth check` can pass
  while the live token fetch (`auth check --test`) fails — trust `--test`.
- Run from PowerShell, not Bash (Python isn't on the Bash PATH here).
- `ask` continues the last conversation by default; that's usually fine. If topic bleed shows up,
  start the question with a clear topic re-statement.

---

## Where findings get saved

Live-query results are appended to **`research-synthesis.md` -> "Live Query Additions"** (a dated
section at the bottom of the master synthesis), NOT here. Keeping everything in one file means step 2
of the decision flow (scan `research-synthesis.md`) catches it next time, so you never re-query the
same question.

Format per entry: `### [YYYY-MM-DD] (Q# - Topic) <question>` then the answer's key specifics in
bullets, then a Source line noting it came from the notebook and which Q-section sources back it.

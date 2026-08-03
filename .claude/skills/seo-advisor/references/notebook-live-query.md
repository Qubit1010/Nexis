# Live Query Fallback - the SEO notebook

**Purpose:** do not guess, and do not answer a specific SEO question from stale training
memory. When the local references plus `research-synthesis.md` do not answer it, query the
live NotebookLM notebook, present the cited answer, then **append the finding back into
`research-synthesis.md`** so the corpus grows and the next identical question is answered
from disk.

This matters more in SEO than in most domains. Thresholds move (Core Web Vitals metrics
have been replaced twice), Google ships and retires ranking systems, and AI-search
behavior is changing quarterly. The notebook is built on 2026 web sources, so it can carry
detail that postdates the model's training cutoff.

## When to trigger

All three must be true:

1. It is a specific factual question (a threshold, a percentage, a tool behavior, a
   platform's citation behavior, a schema type, a bot name).
2. After loading the mode reference and scanning `research-synthesis.md`, you do not have
   a confident, current answer.
3. It is a knowledge question, not a build task.

Do NOT trigger for: opinion or judgment calls, anything the loaded references already
answer, writing tasks, or questions about Aleem's own site that need data rather than
research.

## The operation

The corpus is **split across six notebooks**, because this account's NotebookLM plan
caps a notebook at 100 sources and the corpus is 320. Pick the notebook by topic. If a
topic notebook comes back thin, ask **A_core** as well: it holds 100 sources spanning
all fourteen research passes and often has the cross-topic angle.

| Ask about | Notebook | ID |
|---|---|---|
| How search works, keyword research, on-page | **B_foundations** | `ee2af5a6-cdd5-4c0d-9b5d-39ea0352423b` |
| Technical SEO, Core Web Vitals, schema | **C_technical** | `458c5c68-ebfd-49a9-87ec-745f4e1ff087` |
| Backlinks, digital PR, local SEO, GBP | **D_authority_local** | `f3729c57-b836-4bd5-9a52-43fa3fc8b434` |
| AEO/GEO, AI Overviews, entity SEO, AI crawlers, llms.txt | **E_ai_search** | `d761d412-69dc-4e62-9a62-7d1b69c220ae` |
| Measurement, GSC/GA4, tools, pricing, selling SEO | **F_measure_business** | `d6b96514-4e96-4476-8604-1f83ec2e48a0` |
| Anything cross-topic, or a thin answer above | **A_core** (mixed) | `c863f492-08a3-472e-93f0-a871a9f60c55` |

The live map is `_research/.notebook_ids.json`, and every source in
`_research/sources.json` carries a `notebook` field saying which one holds it.

**CLI:** `C:\Users\qubit\AppData\Local\Programs\Python\Python312\Scripts\notebooklm.exe`

Run from PowerShell, not Bash (Python is not on the Bash PATH):

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\Scripts\notebooklm.exe" ask "<question>" --json -n <NOTEBOOK_ID_FROM_TABLE>
```

**Phrase the question to pull specifics:** append *"Give specific 2026 numbers,
thresholds, and tool names, and cite sources. If the sources disagree or the evidence is
only a vendor's own study, say so."* That last clause matters here: most SEO sources are
selling something.

**Encoding:** the CLI emits UTF-8 with a BOM. Parse with `utf-8-sig`. Writing the question
to a temp file first avoids PowerShell quoting problems on long questions.

**Response shape:** `answer` (with inline `[n]`) plus `references[]`, each carrying
`source_id` and `citation_number`. Resolve `source_id` through
`_research/sources.json` -> `uuid_to_index` -> `sources[index-1]` for the title and URL.

## Decision flow (every knowledge question)

1. Load `seo-scoreboard.md` plus the mode reference.
2. Scan `research-synthesis.md`, including the **Live Query Additions** section at the
   bottom. Prior live findings live there, so a question asked once is never re-queried.
3. Still a miss? Run the live query.
4. Present the answer, leading with the number, and **state the tier**: is the citation
   Google documentation, peer-reviewed work, or a vendor blog? Resolve the source and say
   which. Never present a vendor's self-reported statistic as established fact.
5. **Log it** in `research-synthesis.md` under "Live Query Additions" using the format
   below.
6. Honesty: if a returned `source_id` is not in `sources.json`, it is net-new. Flag it as
   outside the locked corpus.

## Append format

```markdown
### [YYYY-MM-DD] (Q# - Topic) <the question, verbatim>

- key specific, with its number
- key specific, with its number
- Tier: [confirmed] / [practitioner] - <what the citation actually is>
- Source: live query to the SEO Complete Guide 2026 (NexusPoint) notebook
  (N citations, within the locked corpus / net-new).
```

## Auth and troubleshooting

- Re-auth: `python .claude/skills/notebooklm/scripts/relogin.py open` as a **background**
  task, sign in to the "Google Chrome for Testing" window, then `relogin.py capture`.
- Trust `list --json` to verify auth. Plain `list` renders a table but exits 255 through
  PowerShell, which reads as a failure and is not one.
- `ask` continues the previous conversation by default. Add `--new -y` if context bleeds
  between unrelated questions.
- **Import failures that look like auth failures are usually the source cap.** This
  account caps at **100 sources per notebook** (Plus tier). Past that, every add returns
  `RPCError rpc_code=9` and lands as an `error`-status entry with a null url, which is
  indistinguishable from an auth failure. Check `source list --json` and count
  `status == "ready"` before concluding auth broke. This is why the corpus is split
  across six notebooks in the first place.
- **`rpc_code=9` does not reliably mean failure.** Some adds return it and still land
  server-side. Never blind-retry an add; verify against the live URL list instead, or
  you will create duplicates that burn slots against the cap.
- **Never run `source clean` or `delete` without asking Aleem first.** It silently drops
  source UUIDs that existing `[sN]` citations resolve through.

## Where findings get saved

Into `research-synthesis.md` under "Live Query Additions". **Not** into this file. Step 2
of the decision flow reads that section, so a logged finding is found before the next
query is ever run. Then re-run `python _research/build_corpus.py verify` if you introduced
new `[sN]` markers, to confirm they resolve.

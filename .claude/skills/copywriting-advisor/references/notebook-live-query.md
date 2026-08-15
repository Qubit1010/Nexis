# Live query fallback

When `research-synthesis.md` and the other references do not answer a specific question, **do
not guess and do not interpolate from a nearby number.** Run a fresh pass, cite it, and append
it so the next person inherits the answer.

**Two tiers, and this skill has both.**

The corpus was *gathered* through the Exa lane (the sanctioned fallback in
`.claude/rules/research-backed-skills.md`), because when the passes ran the `notebooklm-py`
CLI was not installed on this machine at all. It has since been **installed, authenticated
and loaded**: on 2026-08-15 all 314 sources were mirrored into two NotebookLM notebooks, so
the ask-the-corpus tier is live.

### The notebooks

**364 of 422 sources are mirrored** (97% of the 375 that NotebookLM can actually fetch; 47 are
recorded as `known_unfetchable` in the state file and skipped by design rather than retried).
IDs live in `_research/notebooklm-state.json` - read them from there, never hardcode:

| Notebook | Sources | Ask it about |
|---|---|---|
| **Craft & Examples** | 66 | **Technique only.** Teardowns, swipe files, microcopy galleries, per-platform ad copy, worked examples |
| **Persuasion Evidence** (+ II, + III) | 223 | Headlines, CTAs, landing pages, framing, social proof, scarcity, fluency, length, VoC, benefits/features, emotion, reading behaviour |
| **AI Search, Law & Folklore** | 75 | AEO/GEO, platform formats, folklore provenance, email, experiment validity, FTC endorsement law |

**The craft notebook is a physical quarantine, not just a filing choice.** Anything it returns
is `[K]`: it may inform how to write something and how a platform formats it, and it may never
be quoted as evidence that something works. If you need to know whether a claim is *true*,
you are in the wrong notebook.

The persuasion set is split across three because the per-notebook cap on this account is
**~136**, not the 300 the Pro tier implies. Roman-numeral continuations are created
automatically on overflow.

Re-run or top up with `python _research/push_to_notebooklm.py` (resume-safe, skips what is
already there, craft pushes first) and check with `--status`.

**If it aborts saying the session expired:** run `notebooklm login`, then re-run. The script
detects auth death explicitly rather than mistaking it for a full notebook, which it used to
do - and which cost two spurious notebooks out of an account that is near its creation limit.

### Tier 1 - ask the notebook

Fastest when the question is "what does the corpus already say". Pick the notebook by
subject from the table above.

```powershell
& "$env:APPDATA\Python\Python314\Scripts\notebooklm.exe" ask "<question>" -n <id> --json
```

The JSON carries the answer plus a references array, which is the traceability. **Never run
`source clean` or `delete` on these notebooks without asking Aleem first** - per the rules,
it can silently drop UUIDs that existing citations depend on.

### Tier 2 - fresh research

Use when the notebook does not know, which is the case for anything outside the 20 passes.

---

## Procedure

**1. Run the query.** UNSANDBOXED.

```bash
python .claude/skills/research/scripts/research.py \
  --query "<the specific question> 2026" --depth medium --json
```

Use `--depth deep` when the answer will become a load-bearing claim in a client deliverable,
or when you need the provenance of a statistic rather than the statistic itself.

**2. Tier what comes back**, by the same rule `gather.py` applies:

- **`[C]`**: peer-reviewed journal, primary regulatory text, or original empirical usability
  research with published method.
- **`[P]`**: everything else, including any vendor benchmark however large the sample.

If the only sources are vendors selling the thing the number flatters, the honest answer is
"no independent evidence", not the vendor number with a caveat.

**3. Answer** in the standard shape: what the claim says → what the evidence shows → what to
say instead. Give the tier.

**4. Append it to the corpus.** Two steps, both required:

- Add a bullet under a **`## Live Query Additions`** heading at the end of
  `research-synthesis.md`, dated, with the URL inline since it has no `[sN]` yet.
- If it is a recurring question, add the source properly:

```bash
# add a pass to QUERIES in gather.py, then
python .claude/skills/copywriting-advisor/_research/gather.py run q21_<topic>
python .claude/skills/copywriting-advisor/_research/gather.py extract
python .claude/skills/copywriting-advisor/_research/gather.py verify
```

`extract` preserves existing indices, so adding sources never repoints an existing `[sN]`.

---

## Questions the corpus is known to be weak on

Expect to run live for these, and say the corpus is thin rather than implying coverage:

| Topic | Why it is thin |
|---|---|
| **Email benchmarks of any kind** | q4 returned 0 confirmed, remedial q17 recovered 1. Nearly all email evidence here is vendor-published |
| **Apple MPP mechanics** | No confirmed technical source retrieved. Explain the mechanism, do not cite a figure |
| **Platform character limits** | 0 confirmed by nature. **Always** verify against platform documentation and date it - do not live-query a blog instead |
| **Checkout and form specifics** | Baymard did not retrieve. `[s87]` and the NN/g set are what exists |
| **Countdown timer / dark pattern rules** | No timer-specific regulation retrieved. General deception principle only `[C]` [s288] |
| **Binet and Field** | Did not retrieve. Do not cite their figures from memory |
| **Non-US advertising law** | Corpus is US-centric apart from `[C]` [s286] |

---

## What never justifies a live query

- Getting a number the client wants to hear. If the corpus says a claim is unsourced, a fresh
  search that surfaces the same unsourced claim on a different blog does not make it sourced.
- Replacing a refusal with a softer answer. Re-running a query until it agrees is the failure
  mode this whole skill exists to prevent.

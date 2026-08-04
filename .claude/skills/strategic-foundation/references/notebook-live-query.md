# Live Query Fallback

When `foundation-scoreboard.md` and `research-synthesis.md` do not answer a specific
question, research it before guessing. Then write the finding back so the corpus improves.

**Never fill an evidence gap with a plausible number.** The gaps in `research-synthesis.md`
are real and were left deliberately. Saying "I do not have a sourced figure for that" is a
correct answer here.

---

## Tier 1 — The local corpus

Check first, in this order:
1. `foundation-scoreboard.md` for the number.
2. The relevant `research-synthesis.md` section (Q1-Q8) for the evidence and caveats.
3. `what-not-to-do.md` in case the question is one we deliberately refuse.
4. The **Live Query Additions** section at the bottom of `research-synthesis.md`, in case a
   previous session already answered it.

## Tier 2 — Self-research via the `research` skill (the working live tier)

Run the sibling skill on the gap:

```
python .claude/skills/research/scripts/research.py --query "<gap question>" --depth deep --save
```

Use `--depth medium` for a quick factual check, `--depth deep` when the answer will go into
a client deliverable. Deep mode saves a cited report to `research/YYYY-MM-DD-<slug>.md`.

Phrase the query for the register you want. This corpus was built after learning that broad,
popular phrasing returns explainer and consultancy content, while asking for
"empirical", "meta-analysis", "peer-reviewed" or naming the academic construct returns a
different and better source set. Six of the fifteen passes behind this skill were remedial
for exactly that reason.

## Tier 3 — NotebookLM

Not wired for this skill. That account's auth has been dead since 2026-07-14, which is why
the corpus was built through the `research` skill instead, per the fallback clause in
`.claude/rules/research-backed-skills.md`. If auth is restored, importing
`_research/sources.json` is optional and not required to keep this skill working.

---

## Writing the finding back

A live answer that stays in the chat is wasted. After presenting it:

1. Append to **Live Query Additions** at the bottom of `research-synthesis.md`:

```markdown
### <question> — <YYYY-MM-DD>
**Finding:** <the answer, number first>
**Tier:** confirmed | practitioner
**Sources:** <urls, or [sN] once extracted>
**Caveat:** <what it does not cover>
```

2. If the finding will be cited repeatedly, add the pass to `_research/gather.py` under
   `QUERIES`, run it, and re-extract so the sources get stable `[sN]` indices:

```
python .claude/skills/strategic-foundation/_research/gather.py run <pass_key>
python .claude/skills/strategic-foundation/_research/gather.py extract
python .claude/skills/strategic-foundation/_research/gather.py verify
```

`extract` preserves existing indices and appends new ones, so citations already written in
`references/` never repoint. **Always run `verify` before trusting a citation after a refresh.**

3. If the finding contradicts something in the scoreboard or the synthesis, update both, and
   note the change rather than silently overwriting. If it kills a claim, move it to
   `what-not-to-do.md`.

---

## Refreshing the whole corpus

Benchmarks age. To rebuild:

```
python .claude/skills/strategic-foundation/_research/gather.py run      # skips completed passes
python .claude/skills/strategic-foundation/_research/gather.py extract
python .claude/skills/strategic-foundation/_research/gather.py verify
```

Delete `passes/<key>.json` to force a specific pass to re-run. Deleting `sources.json`
rebuilds indices from scratch, which is **only safe if nothing in `references/` cites `[sN]`
yet**. After the first citation is written, never delete it.

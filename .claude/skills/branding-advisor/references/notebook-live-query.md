# Live Query Fallback

When `brand-scoreboard.md` and `research-synthesis.md` do not answer a specific question,
research it before guessing. Then write the finding back so the corpus improves.

**Never fill an evidence gap with a plausible number.** The gaps in `research-synthesis.md`
are real and were left deliberately. Saying "I do not have a sourced figure for that" is a
correct answer here, and on this topic it is more often the correct answer than on any other
subject in this repo.

Branding attracts invented statistics the way no other marketing subject does. A number that
sounds authoritative and appears in a hundred agency decks is the *most* likely kind of claim
to have no primary source at all. Treat familiarity as a warning sign, not as corroboration.

---

## Tier 1 — The local corpus

Check first, in this order:

1. `brand-scoreboard.md` for the number.
2. The relevant `research-synthesis.md` section (Q1-Q14) for the evidence and caveats.
3. `what-not-to-do.md`, in case the question is one we deliberately refuse. Check this
   **before** researching a suspicious statistic: several of the most-requested branding
   numbers are already documented there as unsourced.
4. The **Live Query Additions** section at the bottom of `research-synthesis.md`, in case a
   previous session already answered it.

## Tier 2 — Self-research via the `research` skill (the working live tier)

Run the sibling skill on the gap:

```
python .claude/skills/research/scripts/research.py --query "<gap question>" --depth deep --save
```

Use `--depth medium` for a quick factual check, `--depth deep` when the answer will go into a
client deliverable. Deep mode saves a cited report to `research/YYYY-MM-DD-<slug>.md`.

Phrase the query for the register you want. Broad, popular phrasing on a branding topic
returns agency explainers and listicles, because that is what dominates these keywords
commercially. Asking for "empirical", "meta-analysis", "peer-reviewed", "experiment", or
naming the academic construct ("brand personality scale", "narrative transportation",
"distinctive brand assets") returns a different and better source set.

### Tracing a suspicious statistic

When the question is "is this number real", do not search the claim in its popular form.
Searching "color increases brand recognition by 80%" returns the hundred pages that repeat
it, which reads as overwhelming confirmation and is worthless.

Instead:

1. Search for the **underlying construct** in academic register ("color effects on brand
   recognition experiment", "typeface personality empirical study").
2. Search for the claim **plus** a provenance word: `"80%" color recognition original study
   source`, or the same claim with "myth", "debunk", "no source".
3. If a specific study is named anywhere, go find that study and read what it actually
   measured. Popular restatements routinely change the population, the outcome variable, and
   the effect size.

If no primary source exists, that is a finding. Record it in `what-not-to-do.md` Tier 1 with
what the trace turned up, so the next session does not repeat the search.

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
**Tier:** confirmed | practitioner | no primary source found
**Sources:** <urls, or [sN] once extracted>
**Caveat:** <what it does not cover>
```

`no primary source found` is a first-class outcome here, not a failed search. Record it with
the same care as a positive finding.

2. If the finding will be cited repeatedly, add the pass to `_research/gather.py` under
   `QUERIES`, run it, and re-extract so the sources get stable `[sN]` indices:

```
python .claude/skills/branding-advisor/_research/gather.py run <pass_key>
python .claude/skills/branding-advisor/_research/gather.py extract
python .claude/skills/branding-advisor/_research/gather.py verify
```

`extract` preserves existing indices and appends new ones, so citations already written in
`references/` never repoint. **Always run `verify` before trusting a citation after a
refresh.** `verify` checks this skill's `references/` *and* all three spokes', since they
cite back to this corpus and have none of their own.

3. If the finding contradicts something in the scoreboard or the synthesis, update both, and
   note the change rather than silently overwriting. If it kills a claim, move it to
   `what-not-to-do.md`.

---

## Refreshing the whole corpus

Benchmarks age, and branding's practitioner tier ages faster than its academic tier. To
rebuild:

```
python .claude/skills/branding-advisor/_research/gather.py run      # skips completed passes
python .claude/skills/branding-advisor/_research/gather.py extract
python .claude/skills/branding-advisor/_research/gather.py verify
```

Delete `passes/<key>.json` to force a specific pass to re-run. Deleting `sources.json`
rebuilds indices from scratch, which is **only safe if nothing in any `references/` folder
cites `[sN]` yet**. After the first citation is written, never delete it.

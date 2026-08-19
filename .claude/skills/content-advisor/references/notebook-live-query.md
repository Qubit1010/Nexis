# Live query — what to do when the corpus is silent

The corpus is 560 sources across 28 passes. It will still miss things: anything
version-specific, anything that changed after 2026-08-15, and the areas listed as honest
weaknesses in `research-synthesis.md`.

**Never fill a gap with a plausible number.** Run the ladder below, then append what you find.

---

## Current state of the tiers

| Tier | Status | Use |
|---|---|---|
| **1. The corpus** | Live | `research-synthesis.md`, then `what-not-to-do.md` / `content-scoreboard.md` / the `format-specs/` |
| **2. Platform documentation** | Live | For anything a platform defines. See below |
| **3. NotebookLM** | Live (mirrored 2026-08-15) | Asking the gathered corpus in natural language |
| **4. Fresh research via the `research` skill** | Live | Anything the corpus genuinely misses |

## The notebooks

Mirrored by `_research/push_to_notebooklm.py`; ids in `_research/notebooklm-state.json`.
Five logical buckets, eight actual notebooks - four overflowed a **II** continuation at the
100-source cap. Query the base and its continuation together when a bucket has one.

| Notebook | Holds | Ask it |
|---|---|---|
| **Content 2026 - Platform Specs** | the 9 `[P*]` first-party docs | What a platform requires or defines. **Never** whether something works |
| **Content 2026 - Craft & Examples** (+ II) | the 140 `[K]` craft sources | How to make something, what good looks like, per-platform convention. **Never** a factual claim |
| **Content 2026 - Format & Attention Evidence** (+ II) | multimedia learning, attention, visual perception, podcast/live/newsletter consumption | How long, what structure, does showing a face help |
| **Content 2026 - Diffusion & Audience Evidence** (+ II) | cascades, seeding, UGC, source credibility, decay | Why content spreads, who to seed, who the audience trusts |
| **Content 2026 - Strategy, Measurement & AI** | firm-generated content, frequency, incrementality, AI content, folklore, metric definitions | Does it work, can we prove it, is that number real |

**The two quarantine notebooks are physical, not just logical.** Craft and Platform Specs are
separate notebooks precisely so a teardown or a spec page cannot be returned as evidence by a
notebook you are asking an evidence question of. **Route your question to the right notebook**
rather than asking all eight, or the quarantine buys nothing.

**Coverage: 464 of 560 sources mirrored (83%), across 8 notebooks.** Verified by listing each
notebook, not from the push log.

**The remaining 96 are unfetchable by NotebookLM, and the profile is entirely predictable:**
ScienceDirect 30, Springer 27, Wiley 5, Nature 3 - academic publisher abstract pages behind
paywalls, plus a few dead practitioner links. All 102 failing URLs are now recorded in
`notebooklm-state.json` under `known_unfetchable`, so a re-run skips them at plan time rather
than re-adding error stubs that consume real notebook slots.

**This costs nothing in the skill.** `[sN]` resolves against `sources.json`, never against
NotebookLM, so a paywalled source is still fully cited and traceable in
`research-synthesis.md`. It simply cannot be queried conversationally. Note the shape of the
gap, though: the missing 96 skew **confirmed-tier**, because paywalled journals are exactly
what fails. **The notebooks under-represent the strongest evidence, so never treat a notebook
miss as evidence of absence** - check the synthesis before concluding the corpus is silent.

**The real per-notebook cap on this account is 100, not the ~136 the copywriting run
estimated.** Every full notebook here stopped at exactly 100, which is why four buckets have a
**II** continuation. There is no API for "full": the script detects it by 6 consecutive add
failures and then overflows, so a burst of `rpc_code=9` in the log is normal operation rather
than an error.

**Re-running the push is safe.** It reads back what each notebook already holds and skips it.
It never calls `source clean` or `source delete`; per
`.claude/rules/research-backed-skills.md` those need Aleem's explicit approval, because they
can silently drop UUIDs that existing citations depend on.

**If auth expires** (`Authentication expired or invalid`), run `notebooklm login`. On this
machine it is usually a no-op click, because the browser profile at
`~/.notebooklm/profiles/default/browser_profile` keeps the Google session alive and only the
derived `storage_state.json` goes stale. **The non-interactive `--browser-cookies` path does
not work here**: it needs `rookiepy`, which has no wheel for Python 3.14 and cannot build
without a Rust toolchain, and `pip install "notebooklm-py[cookies]"` exits 0 while installing
nothing.

---

## Tier 2 — platform documentation, for anything a platform defines

Aspect ratios, durations, character limits, truncation points, what counts as a view. These
change quarterly and the research literature does not carry them `[C]` [s1].

The corpus holds nine first-party docs `[P*]`: YouTube view metrics [s426][s427] and formatting
specs [s428], Instagram content publishing and media requirements [s429][s430][s432][s433],
TikTok's posting API [s431], and LinkedIn video specs [s434].

**Always re-check on the day you use it and record the date in the deliverable.** A figure from
this corpus is a starting point, not an answer, and `[P*]` is authoritative for what a platform
*requires or defines* - never evidence that anything *works*.

---

## Tier 4 — fresh research, when the notebooks miss too

Match the register to the question. This is the whole point of the two-register split, and
getting it wrong is what produced a corpus with two YouTube sources elsewhere in this repo.

**An evidence question** - does X work, how large is the effect, is this real:

```bash
python .claude/skills/research/scripts/research.py \
  --query "<question>" --mode scientific --depth deep --num 15
```

**A craft or platform question** - how do I structure X, what does good look like, what is the
current spec:

```bash
python .claude/skills/research/scripts/research.py \
  --query "<question>" --mode practical --depth deep
```

**A provenance question** - where did this number come from:

```bash
python .claude/skills/research/scripts/research.py \
  --query "<claim> original source methodology" --mode general --depth deep
```

Runs **UNSANDBOXED**. `--mode practical` is the only mode that runs Serper, and therefore the
only one that reaches YouTube and the platform help centres.

---

## Procedure

1. **Confirm the corpus is actually silent.** Check `research-synthesis.md` for the relevant Q,
   then `what-not-to-do.md` - a surprising number of "missing" answers are refusals.
2. **Ask the right notebook** (Tier 3), routing by the table above.
3. **If it misses, run the right register** from Tier 4.
4. **Tier what comes back** by the same rules the corpus uses. A vendor blog is `[P]` however
   confident it sounds; a platform help page is `[P*]`; a teardown is `[K]` and cannot support a
   claim.
5. **Present the answer with its tier**, and flag that it is net-new rather than from the locked
   corpus.
6. **Append it** to `research-synthesis.md` under "Live Query Additions" with the date, the
   query, the finding and the tier, so the next person does not re-buy it.
7. **If it is load-bearing and recurs**, add a pass to `_research/gather.py` and re-run. `run` is
   resume-safe and `extract` is index-stable, so a refresh appends without repointing any
   existing `[sN]`.

---

## Questions the corpus is known to be weak on

Go straight to Tier 4 for these rather than searching the synthesis twice:

- **Podcast audience sizes and format preferences** - vendor-published throughout. Only
  listening motivations are peer-reviewed `[C]` [s36]
- **Webinar practice** - no literature under that name
- **Memes** - almost no direct evidence
- **Thought leadership programmes** - the construct with evidence is source credibility
- **Per-platform view thresholds and any current spec** - Tier 2, not Tier 4
- **The 95-5 rule** - real, from the LinkedIn B2B Institute and Ehrenberg-Bass, and simply
  absent here. Cite it from its actual source
- **Whether refreshing content restores traffic** - the model implies it, nothing tests it

---

## What never justifies a live query

- A number you could get from platform documentation. That is Tier 2, and it is authoritative.
- A claim the corpus already **refuses**. Re-searching until something agrees is how folklore
  gets laundered, and `what-not-to-do.md` exists to stop exactly that.
- A benchmark a client wants for a deck when the honest answer is that no comparable benchmark
  exists. Say it does not exist.

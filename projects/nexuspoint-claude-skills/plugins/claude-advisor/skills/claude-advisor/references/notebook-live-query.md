# Live Fallback (Optional) - Keeping Answers Current

**Purpose:** When a Claude question isn't answered by the loaded reference files or `research-synthesis.md`, don't guess and don't answer from stale memory. Verify against a current, cited source first, then record what you find so the next identical question is answered instantly from disk.

This matters more for this skill than most: Claude's products move fast (new models, Cowork updates, new Claude Code features). The static corpus in `references/` reflects a 2026 research pass with honesty flags on anything version- or price-sensitive. Treat those flags seriously.

---

## When to trigger

Run the fallback when ALL of these are true:
1. The user asked a specific Claude question (a model spec, a price, a Claude Code/Cowork feature, a plan limit, an ecosystem tool, a benchmark, "is X possible").
2. After loading the relevant reference file(s) + scanning `research-synthesis.md`, you **don't have a confident, specific, current answer**.
3. It's a knowledge question (not "write me the guide" - that's `guide` mode using `scripts/save_guide.py`).

Do NOT run it for things already well covered (check `surface-comparison.md` + the matching reference first - most questions are already answered there).

---

## Two ways to verify

**Option A - Web/docs check (no setup):** verify the specific spec/price/feature against current official sources (the Anthropic docs, the Claude pricing page, the changelog) using whatever web tools are available, then present the answer with the source named. This is the zero-config default.

**Option B - Bring your own NotebookLM notebook (optional, advanced):** the original corpus was built in NotebookLM. If you want the same "ask a cited research notebook" workflow this skill was designed around, create your own:

1. In NotebookLM, create a notebook (e.g. "Claude - Complete Guide 2026").
2. Run a few deep web-research passes on Claude's surfaces, models, pricing, Claude Code, and Cowork, importing the cited sources.
3. Query it when the static refs miss, and append the cited finding back into `research-synthesis.md` under "Live Query Additions".

Any NotebookLM access works. This step is entirely optional. The static `references/` corpus stands on its own.

---

## Decision flow (every knowledge question)

1. **Load** the mode's reference file(s) + `surface-comparison.md`. Answer if covered.
2. **Scan** `research-synthesis.md` (the right Q section) for the specific number/tactic. Answer if found.
3. **Miss?** Verify via Option A (or B), leading with the specific number/tactic and naming the source.
4. **Log it** in `research-synthesis.md`, under the **"Live Query Additions"** section at the bottom (append a dated entry tagged to the relevant Q section), so the next identical question is answered from it in step 2.
5. **Honesty:** if a stat is net-new (not in the locked corpus), say so. Never invent a number, model name, price, or feature.

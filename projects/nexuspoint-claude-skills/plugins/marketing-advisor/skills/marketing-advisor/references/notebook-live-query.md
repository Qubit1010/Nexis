# Live Fallback (Optional) - Keeping Numbers Current

**Purpose:** When a marketing question isn't answered by the loaded reference files or `research-synthesis.md`, don't guess and don't quote a stale stat. Verify against a current, cited source first, then record what you find so the next identical question is answered instantly from disk.

The static corpus in `references/` reflects a 2026 research pass (234 sources) with honesty flags on anything that ages fast. Benchmarks drift, so prefer a fresh check over training memory on specific numbers.

---

## When to trigger

Run the fallback when ALL of these are true:
1. The user asked a specific marketing question (a benchmark, a rate, a deliverability number, a pricing figure, "is X still working").
2. After loading the relevant reference file(s) + scanning `research-synthesis.md`, you **don't have a confident, specific 2026 number**.
3. It's a knowledge question (not "write me the plan" - that's a normal output using `scripts/save_marketing_plan.py`).

Do NOT run it for things already covered (check `channel-benchmarks.md` + the matching playbook first - most numbers are already there).

---

## Two ways to verify

**Option A - Web/source check (no setup):** verify the specific benchmark against a current, citable 2026 source (a reputable industry report, the platform's own data, a recent study) using whatever web tools are available, then present the number with the source named. This is the zero-config default.

**Option B - Bring your own NotebookLM notebook (optional, advanced):** the original corpus was built in NotebookLM. If you want the same "ask a cited research notebook" workflow this skill was designed around, create your own:

1. In NotebookLM, create a notebook (e.g. "Marketing 2026").
2. Run a few deep web-research passes on the channels you care about (LinkedIn, email, Reels, paid, pricing), importing the cited sources.
3. Query it when the static refs miss, and append the cited finding back into `research-synthesis.md` under "Live Query Additions".

Any NotebookLM access works. This step is entirely optional. The static `references/` corpus stands on its own.

---

## Decision flow (every knowledge question)

1. **Load** the mode's playbook(s) + `channel-benchmarks.md`. Answer if covered.
2. **Scan** `research-synthesis.md` (the right Q section) for the specific number. Answer if found.
3. **Miss?** Verify via Option A (or B), leading with the number and naming the source.
4. **Log it** in `research-synthesis.md`, under the **"Live Query Additions"** section at the bottom (append a dated entry tagged to the relevant Q section), so the next identical question is answered from it in step 2.
5. **Honesty:** if a stat is net-new (not in the locked corpus), say so. If there's genuinely no 2026 number, say "I don't have a benchmark for that" - never invent or extrapolate.

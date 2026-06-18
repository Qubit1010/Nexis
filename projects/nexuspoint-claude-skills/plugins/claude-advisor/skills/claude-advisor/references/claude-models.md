# Claude Models 2026 - Lineup, Pricing, and Which to Use When

**Source basis:** `research-synthesis.md` Q1/Q7/Q8 (237-source NotebookLM synthesis). `[sN]` -> `_research/sources.json`. **Honesty rule:** prices/versions move fast - confirm via the live notebook before quoting to a client. Don't invent a benchmark.

**Plain-English framing for a business reader:** A large language model is a system trained on huge amounts of text to predict and generate language; in practice it reads your instructions + context and produces useful text, code, or actions. Claude is Anthropic's family of these models, tuned to be helpful, honest, and safe. The key 2026 insight: treat Claude as a **tiered system and route by task**, not one model [s34, s86].

---

## The 2026 lineup (API list price, per million tokens)

| Model | Input | Output | Context | Use it for |
|-------|-------|--------|---------|-----------|
| **Haiku 4.5** | $1 | $5 | 200K | High-volume/simple: classification, extraction, routing, summarization, sub-agents [s78, s79] |
| **Sonnet 4.6** | $3 | $15 | **1M (standard rate)** | The default for ~80% of work: coding, PR review, content, chatbots, doc analysis [s92, s98, s99] |
| **Opus 4.8** | $5 | $25 | 1M (≤128K out) | Hardest 10-15%: multi-file refactors, deep reasoning, audits, long unattended agents [s86, s89] |
| **Fable 5** | $10 | $50 | - | Multi-day autonomous projects with self-validation [s71, s76] *(newest; corroborate)* |

Notes: Opus has a **Fast Mode** ($10/$50) for ~2.5x faster output [s86]. Sonnet 4.6 removed the long-context surcharge that 4.5 had - full 1M at standard rates [s92]. Opus tier is ~67% cheaper than earlier generations [s20, s92]. Opus 4.6 and 4.7 remain active at the same price as 4.8 [s92].

**Benchmarks worth citing:** Sonnet 4.6 ~79.6% SWE-bench Verified, 72.5% OSWorld; Opus ~80.8% Verified, Claude Code 64.3% SWE-bench Pro / 87.6% Verified [s98, s99, s110]. Claude's standout business trait is **epistemic honesty**: ~36% hallucination rate on long-form factuality vs GPT-5.5's 86% - why legal/finance/compliance teams pick it [s110].

---

## Which model when (the rule of thumb)

- **Haiku 4.5** - the answer is cheap to fix and you need speed/scale. Routers, bulk extraction, first-pass triage [s34, s79].
- **Sonnet 4.6** - your **default**. Near-Opus quality at 1/5 the output price; using Opus for standard dev is wasted money [s86, s99].
- **Opus 4.8** - only when output quality changes the business result: hardest reasoning, big refactors, zero-tolerance-for-error tasks [s48, s86].
- **Fable 5** - long-horizon autonomous projects that run for hours/days with minimal check-ins [s71].

**The 70/20/10 routing default:** 70% Haiku, 20% Sonnet, 10% Opus for automated workloads - a single architectural choice that saves thousands/month [s156, s183]. For interactive/coding work, many teams instead run Sonnet 4.6 as the 70-80% default and reserve Opus for 10-15% [s183].

---

## Cost levers (every model)

1. **Prompt caching** - cache static prefixes (system prompt, tool defs, reference docs). Cache **reads cost 10% of base input** ($3 -> $0.30/M on Sonnet 4.6). Cache writes carry a 1.25x (5-min) or 2.0x (1-hr) premium [s182, s92, s183].
2. **Batch API** - flat **50% off** input + output for async jobs that can finish within 24h [s54, s182].
3. **Routing** - 70/20/10 (above).
4. Stacking caching + batch can cut input token costs by up to **~95%** [s156].

For exact request parameters, SDK code, token counting, and model IDs, hand off to the **claude-api** skill.

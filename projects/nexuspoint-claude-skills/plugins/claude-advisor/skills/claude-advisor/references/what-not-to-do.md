# What Not To Do - Misconceptions, Anti-Patterns, Real Limits (2026)

**Source basis:** `research-synthesis.md` Q1/Q3/Q4/Q7 (237-source NotebookLM synthesis). `[sN]` -> `_research/sources.json`. Use this to avoid steering yourself or a client wrong. **Honesty rule:** if you're unsure a limit still holds, verify against current docs before stating it.

---

## Misconceptions to correct

- **"Just use Opus for everything."** Wrong and expensive. Sonnet 4.6 nearly matches Opus on coding (79.6% vs ~80.8% Verified) at 1/5 the output price; default to Sonnet, reserve Opus for the hardest 10-15% [s86, s99].
- **"Claude is one product."** It's one engine behind many doors (chat, Code, Cowork, API). Recommending the wrong door is the most common mistake - match it to who runs the task and how much autonomy it needs [s111].
- **"Claude Code and Cowork are the same."** Code = developers in a terminal/IDE outputting software; Cowork = non-technical operators on the desktop outputting business deliverables [s111, s194].
- **"Open rate / message count is the limit."** 2026 plans run on a token-based "conversation budget," not fixed message counts, and limits flex with demand [s193].
- **"More context is always better."** Claude Code sessions over ~120K tokens drift; stuffing context degrades focus. Curate context, use subagents + `/compact` [s33].

---

## Anti-patterns (operational)

- **Running unattended automation on a Pro/Max/Team subscription.** Violates Anthropic's ToS and risks account suspension - automation belongs on the **API** [s183, s219].
- **Bulk-installing plugins from awesome-lists.** Context bloat kills sessions. Run a lean 5-plugin stack; install the rest on demand [s32, s29].
- **Naive multi-agent fan-out without a budget.** A 50-agent run is ~50x tokens; a $50 job can become $2,500. Cap concurrency, route models 70/20/10 [s86, s156].
- **Paying list price for repeated prompts.** Not using prompt caching (10% reads) + Batch (50%) leaves up to ~95% input savings on the table [s156, s183].
- **Letting verbose shell output flood context.** Filter it (Context Mode plugin) or it derails the agent [s33].
- **Running code-simplifier on every edit.** Burns tokens; run it once pre-PR [s33].

---

## Real limits + risks (don't oversell to clients)

- **Cowork needs a live desktop:** the machine must stay awake, online, app open - sleep pauses scheduled/active tasks [s145, s146].
- **Cowork audit gap:** activity isn't yet in the Claude Compliance API - a blocker for strictly regulated workflows; no cross-session memory unless inside a Project [s145, s199].
- **Prompt injection:** "Act without asking" + web access (or Claude in Chrome) can be hijacked by a malicious page/document. Keep ask-before-acting for sensitive work [s195, s199].
- **Autonomy without guardrails:** Claude Code can over-engineer, touch unrelated files, or expose credentials without git discipline + `PreToolUse` hooks [s33, s69].
- **No native image/video generation** in Claude (unlike ChatGPT's Sora/DALL-E) - don't promise it [s110].
- **Hallucination still exists:** Claude's ~36% long-form factuality error rate is best-in-class but not zero - keep a human review on high-stakes legal/finance output [s110].

---

## Honesty defaults for this skill

- Quote a model name, price, limit, or feature only if it's in the references or the live notebook. If it isn't, say so and offer to query.
- Flag any net-new fact that came from a live query (vs the locked 237-source corpus).
- Customer ROI numbers are *published case-study results*, never a NexusPoint guarantee - frame them that way to prospects.
- For exact API params -> **claude-api** skill. For exhaustive Claude Code mechanics -> **claude-code-guide** agent. Don't guess these from memory.

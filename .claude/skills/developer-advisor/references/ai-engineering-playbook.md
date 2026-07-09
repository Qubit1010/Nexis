# AI / LLM Engineering Playbook

**Source basis:** `research-synthesis.md` Q5 (sources `[s104]`–`[s130]`). Load for RAG/agent/LLM-app architecture questions and the AI layer of a blueprint.

## First principle
**Simple, composable patterns beat complex frameworks** — Anthropic's own finding across dozens of teams [s125]. Escalate only as the problem demands:
`single well-prompted call → + retrieval (RAG) → agentic RAG → multi-agent`. Don't skip ahead.

## RAG vs Agents
- **RAG** — ground answers in a knowledge base; cuts hallucination, adds domain knowledge [s108][s127]. For "answer over documents."
- **Agentic RAG** (2026 production default for complex/messy data) — the agent decides when/what/whether to retrieve; patterns: iterative retrieval, query decomposition, hypothesis-driven, cross-corpus triangulation, evidence-weighted synthesis [s106][s107].
- **Agents** — for multi-step execution + tool use + reasoning loops beyond retrieval [s108].

## The agent stack ≠ the LLM stack
An agent needs state across steps, protocol-governed tools (MCP), persistent memory, reasoning loops, real-time guardrails — ~7 distinct layers [s110][s112]. Even 1M-token windows fill up; add memory (vector + graph stores) once agents run long/across sessions [s109].

## Framework vs direct SDK (the key call)
- **2–3 tools, linear flow → skip the framework.** Direct SDK: OpenAI Agents SDK, Anthropic SDK, or Vercel AI SDK `generateText` + `maxSteps` [s118].
- **Linear RAG pipeline → LangChain (LCEL)** — fast, huge ecosystem [s119].
- **Stateful, branching, human-in-loop → LangGraph** — earns its complexity for state, not logic [s117][s119]. (One team rewrote 4/12 projects LangChain→LangGraph when state became the bottleneck; LangGraph debugging still worse than a custom loop [s119].)
- **Choosing too early** = abstraction tax on every debug/upgrade; **too late** = rebuilding state mgmt under pressure [s115]. A real 2026 movement goes back to **direct API calls** in production [s117]. Pydantic AI for type safety; CrewAI for role-based teams [s117][s121].

## Non-negotiables in production
- **Structured outputs:** program-consumed data must be JSON validated against a schema; write the schema before the prompt; never regex JSON from prose [s113].
- **Evals = the only reliable way to improve** an LLM app: eval-driven development, scoped task-specific tests at every stage, log everything [s126].
- **Context engineering:** smallest set of high-signal tokens; tools are the agent/environment contract [s130] (see `agentic-coding-playbook.md`).

## Checklist for an AI blueprint
- [ ] Chose the lowest rung that solves it (prompt < RAG < agentic < multi-agent).
- [ ] Retrieval design if RAG (chunking, embeddings, pgvector).
- [ ] Framework-vs-SDK decision justified by tool count + state.
- [ ] Structured outputs + eval plan named.
- [ ] Provider chosen (Claude-first for Aleem) + cost/latency budget.

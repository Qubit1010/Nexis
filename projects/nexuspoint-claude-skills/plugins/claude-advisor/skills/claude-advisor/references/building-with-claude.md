# Building with the Claude API (2026)

**Source basis:** `research-synthesis.md` Q7 (237-source NotebookLM synthesis). `[sN]` -> `_research/sources.json`. **Honesty rule:** API params/headers/prices change - confirm via the live notebook, and for exact request shapes, model IDs, and SDK code, hand off to the **claude-api** skill (this file is the strategic layer, not the API reference).

**Headline:** 2026 building means **stateful agentic systems** via the **Agent SDK + MCP + cost engineering**, not thin chat wrappers [s183].

---

## Build with the Agent SDK + tools

- **Agent SDK** (Python/TS) wraps the Claude Code runtime: state management, filesystem tracking, no hand-written tool loop [s10, s183].
- **Subagents for isolation** - a coordinator spawns a restricted-toolset subagent, gets a concise summary back, discards its context (prevents bloat) [s183, s196].
- **Lifecycle hooks for governance** - `PreToolUse` / `PostToolUse` / `SessionStart` to scrub PII before the model, or block dangerous commands [s10, s183].
- **Server vs client tools** - client-executed tools for your local business logic; server-executed tools (`web_search`, `code_execution`, `web_fetch`) run in Anthropic's sandbox, cutting your loop code + latency [s157].
- **Mind the tool tax** - equipping tools adds system-prompt overhead: ~290 input tokens for `auto` tool choice on Opus 4.8, ~410 if you force `any`/`tool` [s182, s183].

---

## Standardize integrations with MCP

- MCP solves the N×M integration problem over JSON-RPC [s183].
- **Direct API MCP connector** - connect to remote MCP servers from the Messages API via the `"anthropic-beta": "mcp-client-2025-11-20"` header; pass `mcp_servers` + expose tools via `mcp_toolset` [s171].
- **"Code Mode"** - instead of loading a server's full schemas + pushing big datasets through the LLM, let Claude write a short local script to query/filter and return only the summary. Anthropic measured a large-data task dropping from ~150,000 -> ~2,000 tokens (**98.7%**) [s117, s183].

---

## Cost optimization (2026 numbers)

Base list price/MTok: Opus 4.8 $5/$25, Sonnet 4.6 $3/$15, Haiku 4.5 $1/$5 - all 1M context at standard rates [s183, s193].
- **Prompt caching** - split static prefix (system, tool defs, docs) from variable suffix; cache reads cost **10% of base** ($0.50/M Opus, $0.30/M Sonnet); writes 1.25x (5-min) / 2.0x (1-hr) [s183].
- **Batch API** - flat **50% off** for async ≤24h jobs; stacking with caching can cut input costs up to **95%** [s156, s183].
- **70/20/10 routing** - 70% Haiku, 20% Sonnet, 10% Opus [s156, s183].

---

## Build-vs-buy (the decision that actually matters)

**Use Claude products** (Pro/Max/Team/Enterprise, Code, Cowork) when:
- A human is in the loop typing/reviewing/steering [s183].
- A developer works in an IDE/terminal (Code) or a non-technical user needs desktop autonomy (Cowork) [s111].
- You're arbitraging heavy individual cost: a full-day coder can burn ~$3,650/mo in raw API; **Max 20x ($200)** or **Team Premium (~$125-150)** is far cheaper, flat-rate [s59, s183].

**Build on the API** when:
- **Unattended automation** / backend services / embedding into your platform. Running automated unattended scripts on a Pro/Max/Team subscription **violates Anthropic's ToS** and risks suspension [s183, s219].
- **Customer-facing apps** needing white-label control, system-prompt control, granular rate limits [s219].
- **ZDR + fine-grained auditing** - Zero Data Retention and OpenTelemetry tool-call observability dictate API (or Bedrock/Vertex gateways) [s69, s183].

**Mature pattern (hybrid):** buy governed Team/Enterprise seats for staff (chat + Code + Cowork at subsidized rates) **and** build foundational automated workflows on the API with the Agent SDK + MCP [s70, s183].

For exact endpoints, request/response schemas, streaming, token counting, and current model IDs -> **claude-api** skill.

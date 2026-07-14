# Service Selection — which engine, when

Lead with the pick. Full evidence + citations in `research-synthesis.md` Q5-Q6. Verify pricing
before quoting it to anyone — this category re-prices constantly [93][95].

## The one mental model: two layers
- **Search** (query → ranked passages): **Exa, Tavily, Serper**. "What does the web say about X."
- **Extraction** (known URL → clean page): **Jina Reader** (`jina_client.read`), Exa `get_contents`.
  "Pull this page into clean markdown." Most deep research needs both. [92]

## Pick by job

| Job | Use | Why |
|---|---|---|
| Fast answer to a general question | **Tavily** (`include_answer`) or Exa `answer` | RAG-shaped, returns an answer-ready blob [94][95] |
| Broad topical / semantic discovery | **Exa** `type=neural` | embeddings find meaning-similar pages keyword misses [85][86] |
| Exact name / quote / known string | **Exa** `type=keyword` or **Serper** `"exact"` | precision over semantics [85][90] |
| People / founders / companies (dorks) | **Serper** | real Google SERP + knowledge graph; dorks work verbatim [79][94] |
| Academic / scientific | **Exa** `category="research paper"` | indexes papers; pair with Tavily [87] |
| Cheap web/news links at volume | **Serper** (~$1/1k, ~$0.30 at scale) | cheapest; but no page content/synthesis [93][94] |
| Read a specific URL → markdown | **Jina Reader** (free-ish) or Exa contents | extraction layer, not search [92] |
| Single-engine agentic deep dive | **Exa** `research()` (`--single --services exa`) | multi-step search+synthesis in one call |
| Let OpenAI search + write | `--single --services openai` | absorbed deep-research path (gpt-5 web search) |

## Depth → default service set (what the orchestrator auto-picks)
- **light** = 1 fast service + its answer (general→Tavily, scientific→Exa, entity→Serper).
- **medium** = 2-3 services fused (general→Exa+Tavily+Serper). The everyday default.
- **deep** = all relevant services + content extraction + OpenAI synthesis, saved to `research/`.

## Cost cheat (list, 2026 — VERIFY [93])
Serper ~$1/1k (→$0.30 at scale) · Firecrawl ~$0.85/1k · Brave ~$5 · Perplexity ~$5 · Exa ~$7 ·
Tavily ~$8. Agents fan 80-240 searches/task; routing per class beats defaulting to one premium
engine by up to ~8.2× [93]. Translation: don't run `deep` (all engines + LLM) for a question `light`
answers.

## Cross-check rule
When accuracy matters, prefer **medium/deep fusion** over one engine: a URL returned by 2-3 engines
outranks a single-engine hit (cheap triangulation) [1][10]. Force it with the default `--fuse`.

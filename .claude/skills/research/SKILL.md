---
name: research
description: >
  The single research + web-search front door. Combines four search services (Exa neural,
  Tavily, Serper/Google, Jina) at three depths — light (fast answer), medium (2-3 engines
  fused + ranked), deep (all engines + content extraction + a cited, saved report) — and cross-
  checks them so you get the best fused result, or deep single-service research on demand. Handles
  three task shapes: general-topic research, finding a specific person/company/founder (entity mode,
  Google-dork + LinkedIn X-ray + email discovery), and scientific/academic research. Grounded in a
  research-first corpus of 108 cited 2026 sources (references/research-synthesis.md) on research
  methodology, Google-dork query crafting, people/company OSINT, SERP-vs-neural-vs-extraction service
  selection, and answer verification. FIRST routes free-tool / API / software / service lookups to the
  scout skills (api-scout, free-tool-scout, free-for-dev-scout, selfhosted-scout) and only researches
  live if their catalogs miss. Use whenever Aleem says "research X", "deep/medium/light research",
  "search X across sources", "find info on X", "look up X", "who is X", "find the founder/CEO of X",
  "find [company]'s [people/email/tech stack]", "cross-check this across Exa and Tavily", "combine the
  search engines", "research this scientifically / find papers on X", or asks to find a free tool/API
  (it checks the scouts first). Supersedes the old deep-research skill. Hands off free-tool catalogs
  to the scout skills, university coursework to assignment-research, content research to post-creator,
  and marketing/sales strategy to marketing-advisor/sales-playbook.
argument-hint: [topic, person/company, or research question]
---

# Research — multi-service search + research engine

The one entry point for "go find this out." It routes tool lookups to the scouts, and for everything
else runs a real research pass: combine Exa / Tavily / Serper / Jina, dedupe + rank by cross-source
agreement, extract and synthesize into a cited answer or report. Problem-first: pick the depth, mode,
and engines that fit the question — don't default to the most expensive pass.

## Built research-first
Every technique below traces to a 2026 source in `references/research-synthesis.md` (108 sources,
`_research/sources.json`). Cite only sources the engine actually returns; never invent a citation
(LLMs hallucinate plausible ones — 50+ were found across 300 ICLR 2026 submissions). If the sources
don't cover something, say so.

## Layer 0 — route free-tool / API / software lookups to the scouts FIRST
If the ask is "a free/open tool, API, software, or service for X," check the pre-built scout catalogs
before spending any live-research effort — they're instant and free:

| Ask is about… | Route to |
|---|---|
| a developer / public **API** | `api-scout` |
| a free **business/SaaS tool** (marketing, CRM, productivity, AI, finance) | `free-tool-scout` |
| a **free hosted tier** of a cloud/dev service (hosting, CI, DB, auth, email) | `free-for-dev-scout` |
| **self-hosted / open-source** software to run yourself | `selfhosted-scout` |

- Auto-pick by the query. If it's genuinely ambiguous which scout fits, **ask Aleem which to check**.
- If the scout catalog returns nothing useful, **fall through** to a live research pass here
  (medium/deep) to find it on the open web.
- Anything that is NOT a tool/API/service lookup skips Layer 0 entirely.

## Context to load first (max 3 refs per invocation)
- Always consult `references/service-selection.md` (which engine/depth for this ask).
- Entity/people/company asks → also `references/people-and-company-finding.md`.
- Query-building / dork questions → `references/query-craft.md`.
- "How should I research this" / credibility → `references/research-methodology.md`.
- Deep evidence or a cited claim in doubt → `references/research-synthesis.md`.

## Mode & depth detection

| The ask | mode | depth (default) |
|---|---|---|
| Free tool/API/software/service | — | **Layer 0 → scout**, then fall through |
| General topic, quick fact | general | light |
| General topic, real answer | general | medium |
| Market/competitor/strategic deep dive | general | deep |
| Find a person/founder/decision-maker; company profile/email/tech-stack | entity | medium or deep |
| Scientific/academic, papers, evidence | scientific | medium or deep |
| "cross-check across engines" / "combine the searches" | (any) | medium/deep, `--fuse` |
| "deep research with just Exa" / "only Serper" | (any) | `--single --services <x>` |

`--mode auto` also detects entity (founder/CEO/email…) and scientific (study/meta-analysis/paper…)
from the query if you don't set it.

## Workflow
1. **Classify.** Tool lookup → Layer 0. Else pick mode (general/entity/scientific) + depth.
2. **Run the engine** (unsandboxed — `api.exa.ai` fails when sandboxed):
   ```
   python .claude/skills/research/scripts/research.py --query "<q>" --depth <light|medium|deep> [--mode entity|scientific] [--single --services exa|openai|serper] [--save]
   ```
   Defaults: `--mode auto`, `--depth medium`, all-relevant engines fused, synthesis on for deep.
3. **Read the output** — it already fuses, dedupes, ranks by cross-source agreement, and (deep)
   writes a cited report. Deep auto-saves to `research/YYYY-MM-DD-<slug>.md`.
4. **Present**, leading with the finding + URL. For entity mode, include a confidence line and flag
   same-name ambiguity. Keep the model's claims tied to returned sources.
5. **Gap?** If a specific technique question isn't covered by the refs, use the live-query fallback
   (`references/notebook-live-query.md`) — research the gap and append it to the synthesis.

## Single-service deep backends
- `--single --services exa --depth deep` → Exa agentic `research()` (multi-step, one call).
- `--single --services openai --depth deep` → OpenAI does its own web search + writes (the absorbed
  deep-research path, gpt-5).
- `--single --services serper` → raw Google SERP / dorks only.

## Writing rules
- No emojis. No em dashes in body text (use commas/periods) — headings may use them.
- Lead with the answer/benchmark, then the evidence and the URL.
- Be honest about gaps and disagreement between sources. Verify before asserting.
- Don't quote this category's pricing/vendor facts as fixed — verify (it re-prices constantly).

## Reference map
```
research/
├── SKILL.md
├── scripts/
│   ├── research.py         orchestrator (depth/mode/services routing, parallel, fuse, save)
│   ├── exa_adapter.py      wraps tools/exa/exa_client.py (search/answer/contents/agentic research)
│   ├── tavily_client.py    Tavily search (+ bundled answer)
│   ├── serper_client.py    Serper Google SERP (+ knowledge graph / PAA) — dorks
│   ├── jina_client.py      s.jina.ai search + r.jina.ai reader (URL -> markdown)
│   ├── fuse.py             normalize-URL dedupe + cross-source ranking (self-check in __main__)
│   ├── synthesize.py       OpenAI report writer (from results) + OpenAI-native web research
│   ├── _env.py / _http.py  shared key loader + stdlib HTTP
├── references/
│   ├── service-selection.md          which engine/depth (default load)
│   ├── query-craft.md                operators + keyword formatting
│   ├── people-and-company-finding.md entity-mode OSINT recipes
│   ├── research-methodology.md       the light/medium/deep method + credibility
│   ├── research-synthesis.md         cited master (Q1-Q6) + Live Query Additions
│   ├── what-not-to-do.md             sourced kill list
│   └── notebook-live-query.md        live fallback (self-research; NotebookLM optional)
└── _research/                        audit trail: gather.py, sources.json (108), exa/q*.json
```
Keys used (all in repo `.env`): `EXA_API_KEY`, `TAVILY_API_KEY`, `SERPER_API_KEY`, `JINA_AI_API_KEY`,
`OPENAI_API_KEY`.

"""OpenAI synthesis: turn fused search results into a structured, cited report.

Two paths:
- synthesize(): writes a report FROM the results we already gathered (no extra web search).
- openai_web_research(): the OpenAI-native web-search path (absorbed from the old deep-research
  skill) — a single-service deep backend when the caller wants OpenAI to do its own searching.
Models mirror the proven deep-research config: gpt-5 (deep) / gpt-4.1-mini (lighter).
"""
from __future__ import annotations

import sys

from _env import get_key

SYSTEM = (
    "You are a rigorous research analyst. Produce thorough, accurate, well-structured research. "
    "Cite sources inline as [n] matching the numbered Sources list you are given. "
    "Never invent facts, numbers, or URLs. If the sources do not cover something, say so plainly."
)

_STRUCTURE = {
    "general": (
        "## Summary\n2-3 sentence overview.\n\n## Key Findings\nNumbered, each with [n] citations.\n\n"
        "## Detail\nDeeper analysis, cross-referencing sources.\n\n## Gaps / Caveats\nWhat the sources "
        "disagree on or don't cover."
    ),
    "entity": (
        "## Who / What\nThe person or company in one line.\n\n## Identity & Role\nName, title, "
        "affiliation, with [n].\n\n## Company / Context\n\n## Links & Contact\nCanonical profile URLs "
        "(LinkedIn, site) with [n].\n\n## Confidence\nHow sure, and any ambiguity between similarly "
        "named entities."
    ),
    "scientific": (
        "## Summary\n\n## Key Findings\nEach tied to a specific study/source [n]; include effect sizes "
        "or numbers only if stated in the source.\n\n## Evidence Quality\nStudy types, consensus vs "
        "contested.\n\n## Open Questions"
    ),
}


def format_sources(results: list[dict], limit: int = 20) -> str:
    lines = []
    for i, r in enumerate(results[:limit], 1):
        body = (r.get("text") or r.get("snippet") or "").strip().replace("\n", " ")
        srcs = ",".join(r.get("sources", []) or [r.get("source", "")])
        lines.append(f"[{i}] {r.get('title','(untitled)')} — {r.get('url','')} ({srcs})\n    {body[:400]}")
    return "\n".join(lines)


def _model_for(depth: str) -> str:
    return "gpt-5" if depth == "deep" else "gpt-4.1-mini"


def _responses_create(client, model, system, user, tools=None):
    kwargs = {"model": model, "instructions": system, "input": user}
    if tools:
        kwargs["tools"] = tools
    try:
        return client.responses.create(**kwargs).output_text
    except Exception as e:  # noqa: BLE001 - fall back off gpt-5 like the old deep-research did
        if model == "gpt-5" and "model" in str(e).lower():
            print(f"Note: falling back to gpt-4.1-mini ({e})", file=sys.stderr)
            kwargs["model"] = "gpt-4.1-mini"
            return client.responses.create(**kwargs).output_text
        raise


def synthesize(query: str, results: list[dict], *, mode: str = "general",
               depth: str = "deep", context: str = "") -> str:
    """Write a cited report from already-gathered results."""
    from openai import OpenAI

    client = OpenAI(api_key=get_key("OPENAI_API_KEY"))
    structure = _STRUCTURE.get(mode, _STRUCTURE["general"])
    sources_block = format_sources(results)
    ctx = f"\n\nBusiness context (use only if relevant):\n{context}\n" if context else ""
    user = (
        f"Research question:\n{query}\n{ctx}\n"
        f"You have these sources (cite them as [n]):\n\n{sources_block}\n\n"
        f"Write the report with this structure:\n\n{structure}\n\n"
        "End with a '## Sources' section listing each [n] as 'title - url'. "
        "Base every claim on the sources above; do not add outside facts."
    )
    return _responses_create(client, _model_for(depth), SYSTEM, user)


def openai_web_research(query: str, *, depth: str = "deep", context: str = "") -> str:
    """OpenAI does its own web search (absorbed deep-research path) — a single-service deep backend."""
    from openai import OpenAI

    client = OpenAI(api_key=get_key("OPENAI_API_KEY"))
    ctx = f"\n\nBusiness context:\n{context}\n" if context else ""
    user = (
        f"Research this thoroughly and cite sources with URLs:\n\n{query}{ctx}\n\n"
        "Structure: ## Summary, ## Key Findings, ## Detail, ## Recommendations, ## Sources. "
        "Cross-reference multiple recent, authoritative sources."
    )
    size = "high" if depth == "deep" else "low"
    tools = [{"type": "web_search_preview", "search_context_size": size}]
    return _responses_create(client, _model_for(depth), SYSTEM, user, tools=tools)


if __name__ == "__main__":  # smoke test (needs OPENAI_API_KEY)
    demo = [{"title": "Milvus", "url": "https://milvus.io", "snippet": "open-source vector DB", "sources": ["exa"]},
            {"title": "Weaviate", "url": "https://weaviate.io", "snippet": "vector search engine", "sources": ["tavily", "exa"]}]
    print(synthesize("top open-source vector databases", demo, mode="general", depth="quick")[:600])

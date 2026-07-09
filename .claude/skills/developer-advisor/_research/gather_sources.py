#!/usr/bin/env python3
"""Curate high-quality developer-advisor sources with Exa, save md + json, emit a URL list.

Same pipeline as student-advisor: curated Exa search across multiple angles per topic
(evidence/deep, practitioner guides, video explainers) instead of NotebookLM auto-research.
Output feeds a clean NotebookLM import.

Run (sandbox must be disabled for network):
    python .claude/skills/developer-advisor/_research/gather_sources.py

Writes to _research/exa/:
    <key>.json          full results per topic
    <key>.md            readable per-topic source list (title, url, date, snippet)
    all_sources.json    combined, deduped, topic-tagged
    urls.txt            one URL per line (for NotebookLM import)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Make the shared Exa client importable (repo root is 4 parents up from this file).
HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parents[4]
sys.path.insert(0, str(REPO_ROOT))

from tools.exa.exa_client import get_client, search  # noqa: E402

OUT_DIR = HERE.parent / "exa"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Per-topic search angles. Each angle: (query, kwargs). Dev content dates fast, so deep
# angles carry a recency floor; practitioner angles stay open for evergreen classics.
DEEP = dict(type="deep", highlights=True, start_published_date="2024-06-01")
PRACTICAL = dict(type="auto", highlights=True)
VIDEO = dict(type="auto", highlights=False, include_domains=["youtube.com"], num_results=3)

TOPICS: dict[str, dict] = {
    "q1_architecture": {
        "title": "Software architecture patterns & system design",
        "angles": [
            ("software architecture patterns 2026 modular monolith vs microservices event-driven serverless when to choose",
             dict(num_results=10, **DEEP)),
            ("system design fundamentals clean architecture domain-driven design practical guide for web applications",
             dict(num_results=8, **PRACTICAL)),
            ("software architecture explained monolith microservices system design",
             dict(**VIDEO)),
        ],
    },
    "q2_frontend": {
        "title": "Frontend & web frameworks (2026)",
        "angles": [
            ("choosing a frontend framework 2026 Next.js React server components Astro Svelte comparison rendering SSR SSG",
             dict(num_results=10, **DEEP)),
            ("modern web development best practices React Next.js App Router Tailwind performance accessibility guide",
             dict(num_results=8, **PRACTICAL)),
            ("which JavaScript framework to choose 2026 Next.js Astro Svelte comparison",
             dict(**VIDEO)),
        ],
    },
    "q3_backend": {
        "title": "Backend frameworks & API design",
        "angles": [
            ("backend framework comparison 2026 Node.js Bun FastAPI Django Go REST vs GraphQL vs tRPC when to use",
             dict(num_results=10, **DEEP)),
            ("API design best practices REST versioning pagination error handling authentication patterns guide",
             dict(num_results=8, **PRACTICAL)),
            ("REST vs GraphQL vs tRPC API design backend framework comparison",
             dict(**VIDEO)),
        ],
    },
    "q4_database": {
        "title": "Databases & the data layer",
        "angles": [
            ("choosing a database 2026 Postgres serverless Neon Supabase SQLite Turso MongoDB vector database pgvector comparison",
             dict(num_results=10, **DEEP)),
            ("Drizzle vs Prisma ORM comparison database schema design caching Redis best practices guide",
             dict(num_results=8, **PRACTICAL)),
            ("which database to choose Postgres Supabase MongoDB explained",
             dict(**VIDEO)),
        ],
    },
    "q5_ai_engineering": {
        "title": "AI/LLM application engineering",
        "angles": [
            ("building LLM applications 2026 RAG vs agents architecture evals structured outputs best practices production",
             dict(num_results=10, **DEEP)),
            ("LangChain LangGraph vs direct API SDK agent frameworks when to use RAG pipeline design guide",
             dict(num_results=8, **PRACTICAL)),
            ("how to build AI agents RAG LLM apps architecture explained",
             dict(**VIDEO)),
        ],
    },
    "q6_agentic_coding": {
        "title": "Agentic coding & AI-assisted engineering",
        "angles": [
            ("AI coding agents best practices 2026 Claude Code context engineering spec-driven development workflows",
             dict(num_results=10, **DEEP)),
            ("how to get the best results from AI coding assistants CLAUDE.md planning subagents code review guide",
             dict(num_results=8, **PRACTICAL)),
            ("Claude Code workflow tips agentic coding best practices",
             dict(**VIDEO)),
        ],
    },
    "q7_mobile": {
        "title": "Mobile development (2026)",
        "angles": [
            ("React Native Expo vs Flutter vs native 2026 comparison cross-platform mobile development when to choose",
             dict(num_results=8, **DEEP)),
            ("PWA vs native app when do you need a mobile app web-first strategy guide",
             dict(num_results=6, **PRACTICAL)),
            ("React Native vs Flutter 2026 which to choose",
             dict(**VIDEO)),
        ],
    },
    "q8_practices": {
        "title": "Engineering best practices (testing, CI/CD, security, quality)",
        "angles": [
            ("software engineering best practices 2026 testing strategy CI/CD DORA metrics code review security OWASP",
             dict(num_results=10, **DEEP)),
            ("practical testing strategy unit integration e2e test pyramid git workflow trunk based development guide",
             dict(num_results=8, **PRACTICAL)),
            ("testing strategy CI/CD pipeline explained software engineering",
             dict(**VIDEO)),
        ],
    },
    "q9_hosting": {
        "title": "Hosting, deployment & infrastructure",
        "angles": [
            ("where to deploy web app 2026 Vercel Cloudflare Railway Fly.io AWS comparison cost scaling serverless vs containers",
             dict(num_results=10, **DEEP)),
            ("deployment platform pricing comparison indie SaaS hosting costs edge functions cold starts guide",
             dict(num_results=8, **PRACTICAL)),
            ("Vercel vs Cloudflare vs Railway vs AWS where to host 2026",
             dict(**VIDEO)),
        ],
    },
}


def _norm_url(u: str) -> str:
    return (u or "").split("#")[0].rstrip("/").lower()


def gather():
    client = get_client()
    combined: list[dict] = []
    seen_global: set[str] = set()

    for key, spec in TOPICS.items():
        topic_results: list[dict] = []
        seen_topic: set[str] = set()
        for query, kwargs in spec["angles"]:
            try:
                res = search(query, client=client, **kwargs)
            except Exception as e:  # noqa: BLE001
                print(f"  [warn] {key} angle failed: {e}", flush=True)
                continue
            for r in res["results"]:
                nu = _norm_url(r["url"])
                if not nu or nu in seen_topic:
                    continue
                seen_topic.add(nu)
                topic_results.append(r)
        # Write per-topic JSON
        (OUT_DIR / f"{key}.json").write_text(
            json.dumps({"topic": spec["title"], "key": key, "count": len(topic_results),
                        "results": topic_results}, indent=2, ensure_ascii=False),
            encoding="utf-8")
        # Write per-topic MD
        lines = [f"# {spec['title']}", "", f"_{len(topic_results)} curated sources via Exa_", ""]
        for i, r in enumerate(topic_results, 1):
            date = (r.get("published_date") or "")[:10]
            meta = " | ".join(x for x in [date, r.get("author") or ""] if x)
            lines.append(f"## {i}. {r.get('title') or '(untitled)'}")
            lines.append(f"<{r['url']}>")
            if meta:
                lines.append(f"*{meta}*")
            hi = r.get("highlights") or []
            if hi:
                snippet = " ".join(hi[0].split())[:500]
                lines.append("")
                lines.append(f"> {snippet}")
            lines.append("")
        (OUT_DIR / f"{key}.md").write_text("\n".join(lines), encoding="utf-8")

        # Add to global combined (dedupe across topics)
        for r in topic_results:
            nu = _norm_url(r["url"])
            if nu in seen_global:
                continue
            seen_global.add(nu)
            combined.append({**r, "topic_key": key, "topic": spec["title"]})

        print(f"  {key}: {len(topic_results)} sources", flush=True)

    # Combined outputs
    (OUT_DIR / "all_sources.json").write_text(
        json.dumps({"total": len(combined), "sources": combined}, indent=2, ensure_ascii=False),
        encoding="utf-8")
    (OUT_DIR / "urls.txt").write_text(
        "\n".join(s["url"] for s in combined) + "\n", encoding="utf-8")

    print(f"\nTOTAL unique curated sources: {len(combined)}")
    print(f"Wrote per-topic md/json + all_sources.json + urls.txt to {OUT_DIR}")


if __name__ == "__main__":
    gather()

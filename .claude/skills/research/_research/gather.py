#!/usr/bin/env python3
"""Research-first gather: Exa full-text passes for the 6 research-technique questions.

Produces the citation audit trail the research-backed rule requires:
  _research/exa/<qkey>.json   raw per-question sources (title, url, text, score)
  _research/sources.json      global deduped index; inline [n] in research-synthesis.md == index

Run:  python .claude/skills/research/_research/gather.py
Rerun-safe: overwrites the JSON each time. Needs EXA_API_KEY (unsandboxed for api.exa.ai).
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))
from tools.exa.exa_client import search  # noqa: E402

QUESTIONS: dict[str, list[str]] = {
    "q1_methodology": [
        "how to research any topic effectively methodology framework 2026",
        "source triangulation evaluating source credibility CRAAP lateral reading",
        "systematic research process steps from question to synthesis",
    ],
    "q2_query_craft": [
        "google advanced search operators dorking cheat sheet complete list",
        "how to formulate effective search queries keyword techniques",
        "boolean search operators site intitle inurl filetype AROUND exact phrase",
    ],
    "q3_finding_people": [
        "how to find someone linkedin profile google x-ray search OSINT",
        "find company founder CEO decision maker contact email techniques",
        "email address permutation pattern finding verification tools",
    ],
    "q4_finding_companies": [
        "how to research a company OSINT tech stack hiring signals",
        "company research tools crunchbase linkedin x-ray funding data",
        "identify company website technology stack builtwith wappalyzer",
    ],
    "q5_serp_extraction": [
        "SERP API vs neural search vs web scraping when to use each",
        "extract structured data from google search results serper serpapi",
        "exa neural search vs keyword search semantic retrieval comparison",
    ],
    "q6_service_optimization": [
        "best AI search API Exa Tavily Serper Jina comparison 2026",
        "reduce hallucination verify AI research answers citation grounding",
        "optimize search relevance ranking result quality techniques",
    ],
}


def norm(url: str) -> str:
    try:
        p = urlparse(url)
        return (p.netloc.lower().removeprefix("www.") + p.path.rstrip("/")).lower()
    except ValueError:
        return url.lower()


def main() -> int:
    exa_dir = HERE / "exa"
    exa_dir.mkdir(parents=True, exist_ok=True)
    global_sources: list[dict] = []
    seen: dict[str, int] = {}

    for qkey, queries in QUESTIONS.items():
        q_sources: list[dict] = []
        for query in queries:
            try:
                data = search(query, num_results=6, type="auto", text=True, highlights=True)
            except Exception as e:  # noqa: BLE001
                print(f"[warn] {qkey}: {query!r} failed: {e}", file=sys.stderr)
                continue
            for r in data.get("results", []):
                url = r.get("url") or ""
                if not url:
                    continue
                rec = {
                    "title": r.get("title") or "",
                    "url": url,
                    "published_date": r.get("published_date"),
                    "score": r.get("score"),
                    "text": (r.get("text") or "")[:2600],
                    "query": query,
                }
                q_sources.append(rec)
                key = norm(url)
                if key not in seen:
                    idx = len(global_sources) + 1
                    seen[key] = idx
                    global_sources.append({"index": idx, "title": rec["title"],
                                           "url": url, "q": qkey, "origin": "exa"})
        (exa_dir / f"{qkey}.json").write_text(
            json.dumps({"question": qkey, "queries": queries, "sources": q_sources},
                       indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"{qkey}: {len(q_sources)} raw sources")

    (HERE / "sources.json").write_text(
        json.dumps({"origin": "exa", "generated": date.today().isoformat(),
                    "note": "inline [n] in research-synthesis.md resolves to sources[index-1]",
                    "total": len(global_sources), "sources": global_sources},
                   indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"total deduped sources: {len(global_sources)} -> sources.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())

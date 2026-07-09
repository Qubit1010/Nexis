#!/usr/bin/env python3
"""Booster pass: add authoritative/canonical sources for the dev topics.

The first gather pass pulls broad practitioner + video sources. This pass pins
include_domains to canonical engineering sources (framework docs, vendor eng blogs,
Fowler/ThoughtWorks, Anthropic engineering, OWASP, DORA) so the corpus is anchored on
primary references, then merges into the existing per-topic files and rebuilds the
combined all_sources.json + urls.txt.

Run (sandbox disabled):
    python .claude/skills/developer-advisor/_research/boost_sources.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parents[4]
sys.path.insert(0, str(REPO_ROOT))
from tools.exa.exa_client import get_client, search  # noqa: E402

OUT_DIR = HERE.parent / "exa"

TOPIC_TITLES = {
    "q1_architecture": "Software architecture patterns & system design",
    "q2_frontend": "Frontend & web frameworks (2026)",
    "q3_backend": "Backend frameworks & API design",
    "q4_database": "Databases & the data layer",
    "q5_ai_engineering": "AI/LLM application engineering",
    "q6_agentic_coding": "Agentic coding & AI-assisted engineering",
    "q7_mobile": "Mobile development (2026)",
    "q8_practices": "Engineering best practices (testing, CI/CD, security, quality)",
    "q9_hosting": "Hosting, deployment & infrastructure",
}

# Targeted, authoritative angles. include_domains pins canonical / primary sources.
BOOST = {
    "q1_architecture": [
        ("architecture patterns microservices monolith tradeoffs when to use",
         dict(num_results=5, type="deep",
              include_domains=["martinfowler.com", "thoughtworks.com", "aws.amazon.com",
                               "microservices.io", "learn.microsoft.com"])),
    ],
    "q2_frontend": [
        ("rendering strategies server components SSR SSG streaming best practices",
         dict(num_results=5, type="deep",
              include_domains=["nextjs.org", "react.dev", "astro.build", "web.dev",
                               "vercel.com"])),
        ("state of JS frontend framework trends survey",
         dict(num_results=3, type="auto",
              include_domains=["stateofjs.com", "2024.stateofjs.com"])),
    ],
    "q3_backend": [
        ("API design guidelines REST versioning idempotency pagination auth",
         dict(num_results=5, type="deep",
              include_domains=["stripe.com", "cloud.google.com", "learn.microsoft.com",
                               "fastapi.tiangolo.com", "trpc.io"])),
    ],
    "q4_database": [
        ("Postgres index design schema modeling scaling best practices",
         dict(num_results=5, type="deep",
              include_domains=["neon.tech", "supabase.com", "planetscale.com",
                               "orm.drizzle.team", "use-the-index-luke.com"])),
    ],
    "q5_ai_engineering": [
        ("building effective agents RAG evals production LLM best practices",
         dict(num_results=6, type="deep",
              include_domains=["anthropic.com", "openai.com", "docs.anthropic.com",
                               "python.langchain.com", "huggingface.co"])),
    ],
    "q6_agentic_coding": [
        ("Claude Code best practices agentic coding CLAUDE.md context engineering",
         dict(num_results=6, type="deep",
              include_domains=["anthropic.com", "docs.anthropic.com", "github.blog",
                               "simonwillison.net"])),
    ],
    "q7_mobile": [
        ("Expo React Native production guidance new architecture",
         dict(num_results=4, type="auto",
              include_domains=["expo.dev", "reactnative.dev", "docs.flutter.dev"])),
    ],
    "q8_practices": [
        ("DORA metrics software delivery performance testing CI/CD security",
         dict(num_results=6, type="deep",
              include_domains=["dora.dev", "cloud.google.com", "owasp.org",
                               "martinfowler.com", "google.github.io"])),
    ],
    "q9_hosting": [
        ("serverless vs containers edge deployment platform tradeoffs pricing",
         dict(num_results=5, type="deep",
              include_domains=["vercel.com", "developers.cloudflare.com", "fly.io",
                               "railway.app", "aws.amazon.com"])),
    ],
}


def _norm_url(u: str) -> str:
    return (u or "").split("#")[0].rstrip("/").lower()


def main():
    client = get_client()
    for key, angles in BOOST.items():
        path = OUT_DIR / f"{key}.json"
        if not path.exists():
            print(f"  [skip] {key}: no gather file yet", flush=True)
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        results = data["results"]
        seen = {_norm_url(r["url"]) for r in results}
        added = 0
        for query, kwargs in angles:
            try:
                res = search(query, client=client, highlights=True, **kwargs)
            except Exception as e:  # noqa: BLE001
                print(f"  [warn] {key} boost failed: {e}", flush=True)
                continue
            for r in res["results"]:
                nu = _norm_url(r["url"])
                if not nu or nu in seen:
                    continue
                seen.add(nu)
                results.append(r)
                added += 1
        data["count"] = len(results)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        # rewrite md
        lines = [f"# {data['topic']}", "", f"_{len(results)} curated sources via Exa_", ""]
        for i, r in enumerate(results, 1):
            date = (r.get("published_date") or "")[:10]
            meta = " | ".join(x for x in [date, r.get("author") or ""] if x)
            lines.append(f"## {i}. {r.get('title') or '(untitled)'}")
            lines.append(f"<{r['url']}>")
            if meta:
                lines.append(f"*{meta}*")
            hi = r.get("highlights") or []
            if hi:
                lines.append("")
                lines.append(f"> {' '.join(hi[0].split())[:500]}")
            lines.append("")
        (OUT_DIR / f"{key}.md").write_text("\n".join(lines), encoding="utf-8")
        print(f"  {key}: +{added} authoritative sources (now {len(results)})", flush=True)

    # Rebuild combined from all 9 per-topic files
    combined, seen_global = [], set()
    for key in TOPIC_TITLES:
        p = OUT_DIR / f"{key}.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        for r in d["results"]:
            nu = _norm_url(r["url"])
            if nu in seen_global:
                continue
            seen_global.add(nu)
            combined.append({**r, "topic_key": key, "topic": d["topic"]})
    (OUT_DIR / "all_sources.json").write_text(
        json.dumps({"total": len(combined), "sources": combined}, indent=2, ensure_ascii=False),
        encoding="utf-8")
    (OUT_DIR / "urls.txt").write_text("\n".join(s["url"] for s in combined) + "\n", encoding="utf-8")
    print(f"\nTOTAL unique curated sources: {len(combined)}")


if __name__ == "__main__":
    main()

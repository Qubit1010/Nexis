#!/usr/bin/env python3
"""Curate high-quality student-advisor sources with Exa, save md + json, emit a URL list.

Replaces NotebookLM's auto-research (which pulled weak sources) with curated Exa search across
multiple angles per topic: academic/evidence, specialist sites/practitioner guides, and
video/explainer. Output feeds a clean NotebookLM import.

Run (sandbox must be disabled for network):
    python .claude/skills/student-advisor/_research/gather_sources.py

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

# Per-topic search angles. Each angle: (query, kwargs). Categories/recency tuned per topic so we
# pull from different platforms and the strongest source type for each.
EVERGREEN = dict(type="deep", highlights=True)          # evidence-heavy, quality over latency
PRACTICAL = dict(type="auto", highlights=True)          # specialist sites / guides
VIDEO = dict(type="auto", highlights=False, include_domains=["youtube.com"], num_results=4)

TOPICS: dict[str, dict] = {
    "q1_learning_science": {
        "title": "Learning Science (how learning works)",
        "angles": [
            ("meta-analysis effective learning techniques retrieval practice spaced repetition interleaving effect size",
             dict(category="research paper", num_results=12, **EVERGREEN)),
            ("evidence-based study strategies that actually work cognitive science learning",
             dict(num_results=10, **PRACTICAL)),
            ("retrieval practice spaced repetition explained study techniques",
             dict(**VIDEO)),
        ],
    },
    "q2_note_taking": {
        "title": "Note-taking & active reading",
        "angles": [
            ("note-taking methods effectiveness research handwriting vs laptop Cornell method study",
             dict(category="research paper", num_results=10, **EVERGREEN)),
            ("best note-taking system for students Cornell mapping Feynman active reading SQ3R guide",
             dict(num_results=10, **PRACTICAL)),
            ("how to take notes in lectures Cornell method Feynman technique",
             dict(**VIDEO)),
        ],
    },
    "q3_exam_prep": {
        "title": "Exam preparation & test anxiety",
        "angles": [
            ("practice testing distributed practice cramming exam performance research test anxiety sleep",
             dict(category="research paper", num_results=10, **EVERGREEN)),
            ("how to study for exams effectively revision plan practice tests reduce test anxiety guide",
             dict(num_results=10, **PRACTICAL)),
            ("how to study for exams practice testing revision strategy",
             dict(**VIDEO)),
        ],
    },
    "q4_retention_motivation": {
        "title": "Retention, motivation & procrastination",
        "angles": [
            ("forgetting curve spaced retrieval long-term retention self-determination theory intrinsic motivation research",
             dict(category="research paper", num_results=10, **EVERGREEN)),
            ("how to stay motivated as a student build interest in boring subject beat procrastination habit formation",
             dict(num_results=10, **PRACTICAL)),
            ("how to get motivated to study beat procrastination intrinsic motivation",
             dict(**VIDEO)),
        ],
    },
    "q5_ai_careers": {
        "title": "AI/CS careers (2026)",
        "angles": [
            ("AI machine learning career paths 2026 ML engineer data scientist AI engineer MLOps job market skills salary",
             dict(num_results=12, type="deep", highlights=True, start_published_date="2025-01-01")),
            ("what to learn to become an AI engineer in 2026 roadmap in-demand skills",
             dict(num_results=8, **PRACTICAL)),
            ("AI engineer career path 2026 skills what to learn",
             dict(**VIDEO)),
        ],
    },
    "q6_grad_school": {
        "title": "Master's / grad school planning",
        "angles": [
            ("masters vs PhD computer science AI is a masters worth it graduate school application statement of purpose 2026",
             dict(num_results=10, type="deep", highlights=True, start_published_date="2024-01-01")),
            ("how to apply to grad school CS AI statement of purpose letters of recommendation timeline guide",
             dict(num_results=8, **PRACTICAL)),
            ("how to apply to grad school computer science statement of purpose",
             dict(**VIDEO)),
        ],
    },
    "q7_scholarships": {
        "title": "Fully funded scholarships",
        "angles": [
            ("fully funded scholarships international students 2026 Fulbright Chevening DAAD Erasmus Mundus Commonwealth MEXT eligibility deadlines",
             dict(num_results=12, type="deep", highlights=True, start_published_date="2024-06-01")),
            ("how to win a fully funded scholarship application strategy international students Pakistan guide",
             dict(num_results=8, **PRACTICAL)),
            ("how to win fully funded scholarship Fulbright Chevening DAAD tips",
             dict(**VIDEO)),
        ],
    },
    "q8_study_abroad": {
        "title": "Best countries to study abroad",
        "angles": [
            ("best countries to study abroad 2026 international students cost post study work visa PR Germany Canada UK Australia Netherlands",
             dict(num_results=12, type="deep", highlights=True, start_published_date="2024-06-01")),
            ("compare study abroad destinations tuition living cost post-study work visa for international students guide",
             dict(num_results=8, **PRACTICAL)),
            ("best country to study abroad for international students 2026 comparison",
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

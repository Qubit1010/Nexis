#!/usr/bin/env python3
"""Booster pass: add authoritative/official sources for the careers/scholarships/study-abroad topics.

The first gather pass got gold-standard peer-reviewed sources for the learning-science topics, but
the time-sensitive topics (q5-q8) leaned on SEO/aggregator blogs. This pass targets official program
sites and authoritative reports via include_domains, then merges into the existing per-topic files
and rebuilds the combined all_sources.json + urls.txt.

Run (sandbox disabled):
    python .claude/skills/student-advisor/_research/boost_sources.py
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
    "q1_learning_science": "Learning Science (how learning works)",
    "q2_note_taking": "Note-taking & active reading",
    "q3_exam_prep": "Exam preparation & test anxiety",
    "q4_retention_motivation": "Retention, motivation & procrastination",
    "q5_ai_careers": "AI/CS careers (2026)",
    "q6_grad_school": "Master's / grad school planning",
    "q7_scholarships": "Fully funded scholarships",
    "q8_study_abroad": "Best countries to study abroad",
}

# Targeted, authoritative angles. include_domains pins official / high-authority sources.
BOOST = {
    "q5_ai_careers": [
        ("AI jobs and skills demand outlook 2026 report",
         dict(num_results=6, type="deep",
              include_domains=["hai.stanford.edu", "weforum.org", "bls.gov", "github.blog",
                               "oecd.org", "mckinsey.com"])),
        ("machine learning engineer career roadmap skills",
         dict(num_results=4, type="auto",
              include_domains=["dataquest.io", "deeplearning.ai", "towardsdatascience.com"])),
    ],
    "q6_grad_school": [
        ("master's vs PhD computer science is graduate school worth it advice",
         dict(num_results=6, type="deep",
              include_domains=["cs.cmu.edu", "gradschool.cornell.edu", "mit.edu", "stanford.edu",
                               "80000hours.org", "matt.might.net"])),
    ],
    "q7_scholarships": [
        ("Fulbright foreign student program eligibility how to apply",
         dict(num_results=3, type="auto",
              include_domains=["foreign.fulbrightonline.org", "cies.org", "eca.state.gov"])),
        ("Chevening scholarship eligibility application",
         dict(num_results=2, type="auto", include_domains=["chevening.org"])),
        ("DAAD scholarships for international students Germany",
         dict(num_results=3, type="auto", include_domains=["daad.de", "study-in-germany.de"])),
        ("Erasmus Mundus joint masters scholarship apply",
         dict(num_results=3, type="auto",
              include_domains=["erasmus-plus.ec.europa.eu", "eacea.ec.europa.eu"])),
        ("Commonwealth scholarship and MEXT scholarship for international students",
         dict(num_results=3, type="auto",
              include_domains=["cscuk.fcdo.gov.uk", "studyinjapan.go.jp", "mext.go.jp"])),
    ],
    "q8_study_abroad": [
        ("study in Germany / Canada / Australia post study work visa for international students official",
         dict(num_results=6, type="deep",
              include_domains=["study-in-germany.de", "canada.ca", "studyaustralia.gov.au",
                               "gov.uk", "studyinholland.nl", "educationinireland.com"])),
    ],
}


def _norm_url(u: str) -> str:
    return (u or "").split("#")[0].rstrip("/").lower()


def main():
    client = get_client()
    for key, angles in BOOST.items():
        path = OUT_DIR / f"{key}.json"
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

    # Rebuild combined from all 8 per-topic files
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

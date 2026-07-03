#!/usr/bin/env python3
"""Gather Exa research on social-media writing craft for the podcast-repurposer skill.

Writes one combined JSON to references/social-writing-research-2026.json.
Run with the sandbox disabled (api.exa.ai DNS fails sandboxed).
"""

import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
sys.path.insert(0, str(REPO_ROOT))

from tools.exa.exa_client import get_client, search  # noqa: E402

OUT = HERE.parent / "references" / "social-writing-research-2026.json"

QUERIES = [
    ("linkedin_hooks_dwell", "How to write LinkedIn post hooks and optimize for dwell time engagement 2026"),
    ("instagram_captions_saves", "Instagram caption writing best practices for saves and shares engagement"),
    ("facebook_post_engagement", "Facebook post writing best practices for organic engagement and comments"),
    ("comment_cta_design", "How to write call-to-action questions that drive comments on social media posts"),
    ("hook_formulas", "Short-form content hook formulas that stop the scroll copywriting"),
    ("social_copy_formatting", "Social media copywriting formatting best practices line breaks lists readability"),
]


def main():
    client = get_client()
    seen = set()
    out = {"generated": str(date.today()), "skill": "podcast-repurposer", "queries": []}

    for key, query in QUERIES:
        print(f"[{key}] {query}")
        data = search(query, client=client, num_results=8, type="auto",
                      highlights=True, summary=True, text=False)
        results = []
        for r in data["results"]:
            url = (r.get("url") or "").rstrip("/").lower()
            if url in seen:
                continue
            seen.add(url)
            results.append(r)
        print(f"  -> {len(results)} new results")
        out["queries"].append({"topic": key, "query": query, "results": results})

    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    total = sum(len(q["results"]) for q in out["queries"])
    print(f"Wrote {OUT} ({total} unique results)")


if __name__ == "__main__":
    main()

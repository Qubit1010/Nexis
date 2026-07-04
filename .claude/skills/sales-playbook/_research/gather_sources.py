#!/usr/bin/env python3
"""Curate Q6-Q9 sales-playbook sources with Exa (human-vs-AI copy, DM-to-meeting
conversion, Facebook outreach, stalled-thread cadence). Mirrors the
student-advisor gather script.

Run: python .claude/skills/sales-playbook/_research/gather_sources.py

Writes to _research/exa/:
    <key>.json          full results per topic
    <key>.md            readable per-topic source list
    all_sources.json    combined, deduped, topic-tagged
    urls.txt            one URL per line (for NotebookLM import)
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
OUT_DIR.mkdir(parents=True, exist_ok=True)

RECENT = dict(type="auto", highlights=True, text=False, start_published_date="2024-09-01")

TOPICS: dict[str, dict] = {
    "q6_human_vs_ai": {
        "title": "Sounding human vs AI-generated in outreach",
        "angles": [
            ("how to write cold DMs and cold emails that don't sound AI generated in 2026", dict(num_results=8, **RECENT)),
            ("telltale signs of AI-written outreach messages buyers ignore em dash chatgpt phrases", dict(num_results=8, **RECENT)),
            ("writing outreach that sounds human authentic voice AI era practitioner guide", dict(num_results=6, **RECENT)),
        ],
    },
    "q7_advance_to_call": {
        "title": "Buying signals + advancing a DM thread to a booked call",
        "angles": [
            ("buying signals in a LinkedIn DM conversation when to ask for the meeting", dict(num_results=8, **RECENT)),
            ("Instagram DM sales conversation how to book a call conversion", dict(num_results=8, **RECENT)),
            ("social selling how many messages before asking for a call data readiness signals", dict(num_results=6, **RECENT)),
        ],
    },
    "q8_facebook": {
        "title": "Facebook Messenger / group outreach for B2B services",
        "angles": [
            ("Facebook Messenger cold outreach B2B best practices message requests", dict(num_results=8, **RECENT)),
            ("Facebook group lead generation DM outreach etiquette founders clients", dict(num_results=8, **RECENT)),
            ("Facebook DM sales scripts book calls service business", dict(num_results=6, **RECENT)),
        ],
    },
    "q9_stalled_threads": {
        "title": "Warm-thread follow-up cadence + stall recovery",
        "angles": [
            ("follow-up cadence warm DM thread prospect stalled how many attempts before moving on", dict(num_results=8, **RECENT)),
            ("re-engage prospect who stopped replying DM without being pushy scripts", dict(num_results=8, **RECENT)),
            ("sales conversation stuck in rapport loop force advancement to meeting", dict(num_results=6, **RECENT)),
        ],
    },
}


def main() -> None:
    client = get_client()
    all_sources: dict[str, dict] = {}

    for key, topic in TOPICS.items():
        results = []
        for query, kwargs in topic["angles"]:
            print(f"[{key}] {query}")
            try:
                res = search(query, client=client, **kwargs)
                results.extend(res["results"])
            except Exception as e:  # noqa: BLE001 - keep gathering other angles
                print(f"  FAILED: {e}")

        (OUT_DIR / f"{key}.json").write_text(
            json.dumps({"title": topic["title"], "results": results}, indent=2, ensure_ascii=False),
            encoding="utf-8")

        lines = [f"# {topic['title']}\n"]
        for r in results:
            lines.append(f"- [{r.get('title') or r['url']}]({r['url']}) "
                         f"({r.get('published_date') or 'n.d.'})")
            for h in (r.get("highlights") or [])[:1]:
                lines.append(f"  > {h.strip()[:300]}")
        (OUT_DIR / f"{key}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

        for r in results:
            url = r["url"].split("?")[0].rstrip("/")
            entry = all_sources.setdefault(url, {**r, "topics": []})
            if key not in entry["topics"]:
                entry["topics"].append(key)
        print(f"[{key}] {len(results)} results")

    (OUT_DIR / "all_sources.json").write_text(
        json.dumps(list(all_sources.values()), indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT_DIR / "urls.txt").write_text("\n".join(all_sources) + "\n", encoding="utf-8")
    print(f"\n{len(all_sources)} unique sources -> {OUT_DIR}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the upwork-advisor research corpus with Exa (cited).

NotebookLM-first is the standard (research-backed-skills.md), but NotebookLM auth
was flagged expired (2026-07-14), so this uses the sanctioned Exa fallback with the
same citation rigor: one cited `answer()` per sub-question (Q1-Q8) plus one `search()`
per question to widen the source pool, then a deduped global `sources.json` index.

Scope note: these eight questions deliberately AVOID the eight already covered by
`upwork-reply-drafter/_research/` (reply craft, rate negotiation, scope creep,
JSS-comms, review asks, retention messaging, red flags, sound-human). This corpus is
the STRATEGY layer: profile, search/ranking, job selection, connects economics,
proposal strategy, rates/positioning, badge thresholds, 2026 platform outlook.

Run: python .claude/skills/upwork-advisor/_research/gather.py

Writes to _research/:
    q1..q8.json      per-question {question, answer, citations, extra_sources}
    sources.json     global deduped index: url -> {index, title, date, topics[]}
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parents[4]
sys.path.insert(0, str(REPO_ROOT))

from tools.exa.exa_client import get_client, answer, search  # noqa: E402

OUT_DIR = HERE.parent
# Platform mechanics (connect pricing, Boost, badge thresholds) change fast.
# Stale numbers here are worse than no numbers, so keep the window tight.
RECENT = "2025-01-01"

# Each: (key, cited-answer question, supplementary search query)
QUESTIONS: list[tuple[str, str, str]] = [
    ("q1_profile",
     "How should a freelancer optimize their Upwork profile in 2026 to win more work? Cover the "
     "profile title, the first two lines of the overview (the part shown before 'more'), specialized "
     "profiles, portfolio pieces, profile photo, intro video, and skills/tags. What specifically "
     "moves search visibility versus what only affects clients who already clicked?",
     "Upwork profile optimization 2026 title overview specialized profiles portfolio that wins clients"),
    ("q2_search_algorithm",
     "How does Upwork's search and matching algorithm rank freelancers in 2026, and how do freelancers "
     "get found by clients? Cover the known ranking signals, profile completeness, keywords and skills, "
     "activity/responsiveness, JSS and badges as ranking inputs, and how Upwork's talent matching or "
     "invite system surfaces freelancers to clients.",
     "how Upwork search algorithm ranks freelancers get found by clients invites 2026"),
    ("q3_job_selection",
     "How do successful Upwork freelancers find and select the right jobs to bid on? Cover search "
     "filters and saved searches, how to read a job post for quality, how to vet the CLIENT before "
     "spending connects (hire rate, payment verified, average hourly paid, review history), and the "
     "red flags in a job post that mean skip it.",
     "how to vet Upwork client before applying job post red flags hire rate payment verified filters"),
    ("q4_connects_boost",
     "How does the Upwork connects economy and Boosted Proposals bidding work in 2026, and what is the "
     "actual ROI? Cover the cost of connects, how many connects a proposal costs, how Boost bidding "
     "works, when boosting pays off versus wastes money, and how many proposals per week successful "
     "freelancers send.",
     "Upwork connects cost boosted proposals bidding worth it ROI how many proposals 2026"),
    ("q5_proposal_strategy",
     "At a portfolio level, what separates Upwork freelancers with high proposal win rates from low "
     "ones in 2026? Cover benchmark reply rates and hire rates per proposal, ideal proposal length, "
     "the importance of the first two lines shown in the client's preview, response speed after a job "
     "is posted, and how many proposals it typically takes to land a contract.",
     "Upwork proposal win rate benchmark statistics how many proposals to get hired reply rate 2026"),
    ("q6_rates_positioning",
     "How do Upwork freelancers raise their rates, niche down, and move upmarket to better clients? "
     "Cover specializing versus generalizing, positioning as a specialist, when and how to raise rates "
     "with new and existing clients, hourly versus fixed-price strategy, and how top earners position "
     "themselves differently from commodity freelancers.",
     "Upwork raise rates niche down specialist positioning move upmarket higher paying clients"),
    ("q7_badges_thresholds",
     "What are the exact qualification requirements and thresholds for Upwork's freelancer badges and "
     "status levels in 2026: Rising Talent, Top Rated, Top Rated Plus, and Expert-Vetted? Cover the "
     "JSS threshold, earnings requirements, account age, activity requirements, and what benefits each "
     "level actually unlocks.",
     "Upwork Top Rated Plus Rising Talent Expert Vetted requirements qualifications benefits 2026"),
    ("q8_platform_strategy_2026",
     "What is the state of Upwork as a platform for freelancers in 2026, and what is the winning "
     "long-term strategy? Cover AI's effect on demand and competition, market saturation, Upwork's own "
     "AI features and how they change the game, whether Upwork is still worth it, and how top "
     "freelancers build a stable client portfolio and long-term retainers on the platform.",
     "is Upwork still worth it 2026 AI impact freelancing competition saturation long term strategy"),
]


def main() -> None:
    client = get_client()
    sources: dict[str, dict] = {}

    def register(url: str, title: str | None, date: str | None, topic: str) -> None:
        clean = (url or "").split("?")[0].rstrip("/")
        if not clean:
            return
        entry = sources.setdefault(
            clean, {"index": 0, "title": title, "published_date": date, "topics": []})
        if topic not in entry["topics"]:
            entry["topics"].append(topic)
        if not entry.get("title") and title:
            entry["title"] = title

    for key, question, search_q in QUESTIONS:
        print(f"[{key}] answering...", flush=True)
        rec: dict = {"question": question}
        try:
            ans = answer(question, text=False, model="exa", client=client)
            rec["answer"] = ans.get("answer")
            rec["citations"] = ans.get("citations", [])
            for c in rec["citations"]:
                register(c.get("url", ""), c.get("title"), c.get("published_date"), key)
        except Exception as e:  # noqa: BLE001
            print(f"  answer FAILED: {e}")
            rec["answer"] = None
            rec["citations"] = []

        print(f"[{key}] searching...", flush=True)
        try:
            res = search(search_q, num_results=8, type="auto", highlights=True,
                         text=False, start_published_date=RECENT, client=client)
            rec["extra_sources"] = res["results"]
            for r in res["results"]:
                register(r.get("url", ""), r.get("title"), r.get("published_date"), key)
        except Exception as e:  # noqa: BLE001
            print(f"  search FAILED: {e}")
            rec["extra_sources"] = []

        (OUT_DIR / f"{key}.json").write_text(
            json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
        n_cit = len(rec.get("citations") or [])
        n_src = len(rec.get("extra_sources") or [])
        print(f"[{key}] {n_cit} citations + {n_src} search sources")
        time.sleep(1)  # be polite to the API

    # Freeze a stable global index (sorted by first-seen order via insertion).
    for i, entry in enumerate(sources.values(), start=1):
        entry["index"] = i
    (OUT_DIR / "sources.json").write_text(
        json.dumps({"count": len(sources), "sources": sources}, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(f"\n{len(sources)} unique sources -> {OUT_DIR / 'sources.json'}")


if __name__ == "__main__":
    main()

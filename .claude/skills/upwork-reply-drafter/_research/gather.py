#!/usr/bin/env python3
"""Build the upwork-reply-drafter research corpus with Exa (cited).

NotebookLM-first is the standard (research-backed-skills.md), but NotebookLM auth
was flagged expired (2026-07-14), so this uses the sanctioned Exa fallback with the
same citation rigor: one cited `answer()` per sub-question (Q1-Q8) plus one `search()`
per question to widen the source pool, then a deduped global `sources.json` index.

Run: python .claude/skills/upwork-reply-drafter/_research/gather.py

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
RECENT = "2024-06-01"  # published-after window: keep it current

# Each: (key, cited-answer question, supplementary search query)
QUESTIONS: list[tuple[str, str, str]] = [
    ("q1_reply_craft",
     "On Upwork, after a client replies to a freelancer's proposal with questions or interest, "
     "what makes the freelancer's reply convert to a hire versus get ghosted? Cover response time, "
     "message structure, specificity, and the most common first-reply mistakes in 2025-2026.",
     "Upwork how to respond to client message after proposal to get hired 2026"),
    ("q2_negotiation",
     "How do top-rated Upwork freelancers negotiate rate, scope, and timeline with clients without "
     "discounting their price? Cover anchoring, value framing, responding to 'can you do it cheaper' "
     "or a low budget, and holding your rate professionally.",
     "Upwork freelancer negotiate rate without discounting hold price client wants cheaper"),
    ("q3_scope_creep",
     "What is the professional best practice for handling scope creep and out-of-scope change requests "
     "from clients on Upwork without damaging the relationship or the review? Cover change-order framing, "
     "exactly what to say, and milestone/contract mechanics.",
     "Upwork handling scope creep client change request out of scope politely 2026"),
    ("q4_jss",
     "How does Upwork's Job Success Score (JSS) work in 2026, and how does a freelancer's client "
     "communication and contract handling protect or hurt it? Cover public and private feedback, "
     "disputes, contracts closed with no feedback, and long-term client relationships.",
     "Upwork Job Success Score JSS how it works protect improve 2026"),
    ("q5_reviews",
     "What is the best practice for asking an Upwork client for a 5-star review, including timing and "
     "wording, and what drives positive public and private feedback? How do top freelancers request "
     "reviews and feedback without seeming pushy?",
     "Upwork how to ask client for 5 star review feedback timing wording"),
    ("q6_retention",
     "How do freelancers convert one-off Upwork jobs into repeat work and retainers, and how do they "
     "re-engage or reactivate past clients? Cover retention tactics, offering ongoing support or "
     "maintenance, and the message that reopens a dormant client relationship.",
     "Upwork turn one-time client into repeat retainer re-engage past client message"),
    ("q7_trust_redflags",
     "What communication norms build client trust on Upwork (response time, professionalism, proactive "
     "updates, expectation-setting), and what client red flags should a freelancer watch for? Cover "
     "cadence, tone, and the signals of a problem client in 2025-2026.",
     "Upwork client communication best practices build trust red flags bad client signs"),
    ("q8_sound_human",
     "In 2026, how can a freelancer write Upwork client messages that sound human and personal rather "
     "than AI-generated or templated? What tells do clients pattern-match, and how do you avoid "
     "generic-sounding replies while staying professional?",
     "messages that don't sound AI generated ChatGPT tells human writing 2026"),
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

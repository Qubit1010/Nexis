"""Research for the post-creator skill: topic -> source pack JSON.

Delegates topic search to the research skill's multi-engine orchestrator (Exa +
Tavily + Serper + Jina, deep mode: fused across engines, ranked by cross-source
agreement, full text pulled for the top sources) instead of a standalone Exa-only
pass. The row's Reference URL (if any) is still fetched directly via Exa
get_contents, since that's a known page to read, not something to search for.

Output is a "source pack" JSON that Claude condenses in-session into the
Formal + Simplified source summaries. This script only gathers — it never
writes prose, so there is nothing to hallucinate. NotebookLM does the actual
reading and synthesis in step 3.

Run unsandboxed (dangerouslyDisableSandbox: true) — api.exa.ai / Tavily /
Serper / Jina all need real network.

CLI:
    python research.py --topic "GLM 5.2 as the new open-weights" \
        [--description "..."] [--reference https://...] [--num 12] [-o pack.json]
"""

import argparse
import io
import json
import sys
from pathlib import Path

# .claude/skills/post-creator/scripts/research.py -> repo root is 4 parents up.
_REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / ".claude" / "skills" / "research" / "scripts"))

from tools.exa.exa_client import get_client, get_contents  # noqa: E402
import research as research_engine  # noqa: E402

TEXT_CAP = 4000


def _trim(txt, cap=TEXT_CAP):
    if not txt:
        return None
    txt = txt.strip()
    return txt[:cap] + ("..." if len(txt) > cap else "")


def build_pack(topic, description="", reference=None, num=12):
    pack = {"topic": topic, "description": description, "reference": None,
            "sources": [], "errors": []}

    # 1. Seed: the row's Reference URL, fetched directly (not a search).
    if reference:
        try:
            ref = get_contents([reference], text=True, client=get_client())
            for r in ref.get("results", []):
                pack["reference"] = {
                    "title": r.get("title"), "url": r.get("url"),
                    "text": _trim(r.get("text"), TEXT_CAP * 2),  # the primary source gets more room
                }
        except Exception as e:  # noqa: BLE001 - a dead reference URL shouldn't kill the run
            pack["errors"].append(f"reference fetch failed: {e}")

    # 2. Search: the research skill, deep mode (all engines, fused, top sources
    #    enriched with full text). No LLM synthesis here — NotebookLM does that.
    query = f"{topic}. {description}".strip().rstrip(".")
    try:
        result = research_engine.run(query, depth="deep", mode="general", services=[],
                                      single=False, do_synth=False, num=num, context="")
    except Exception as e:  # noqa: BLE001
        pack["errors"].append(f"research failed: {e}")
        return pack

    seen = {reference.rstrip("/").lower()} if reference else set()
    for r in result.get("results", [])[:num]:
        url = (r.get("url") or "").rstrip("/").lower()
        if not url or url in seen:
            continue
        seen.add(url)
        pack["sources"].append({
            "title": r.get("title"), "url": r.get("url"),
            "published_date": r.get("published_date"),
            "summary": r.get("snippet"),
            "engines": r.get("sources", []),  # which search engines agreed on this URL
            "text": _trim(r.get("text")),
        })

    pack["num_sources"] = len(pack["sources"])
    return pack


def main():
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Build a research-skill source pack for a schedule topic.")
    ap.add_argument("--topic", required=True)
    ap.add_argument("--description", default="")
    ap.add_argument("--reference", default=None, help="Optional URL from the row's Reference column.")
    ap.add_argument("--num", type=int, default=12)
    ap.add_argument("-o", "--output", default=None)
    args = ap.parse_args()

    pack = build_pack(args.topic, args.description, args.reference, args.num)
    text = json.dumps(pack, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Wrote {pack.get('num_sources', 0)} source(s) to {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()

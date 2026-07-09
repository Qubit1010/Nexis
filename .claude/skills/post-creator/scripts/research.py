"""Exa research for the post-creator skill: topic -> source pack JSON.

Replaces the manual NotebookLM step. Given a topic (+ optional description and
reference URL), it:
  1. Seeds with the reference URL's cleaned contents when one is given.
  2. Runs an Exa deep search for the 8-12 best sources.
  3. Pulls full text for the top few so the synthesis has real substance.

Output is a "source pack" JSON that Claude condenses in-session into the
Formal + Simplified source summaries. This script only gathers — it never
writes prose, so there is nothing to hallucinate.

Reuses tools/exa/exa_client.py (EXA_API_KEY from repo .env; run unsandboxed —
api.exa.ai DNS fails in the sandbox).

CLI:
    python research.py --topic "GLM 5.2 as the new open-weights" \
        [--description "..."] [--reference https://...] [--num 12] [-o pack.json]
"""

import argparse
import io
import json
import sys
from pathlib import Path

# tools/exa lives at the repo root; walk up from this file to find it.
_REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO_ROOT))

from tools.exa.exa_client import get_client, get_contents, search  # noqa: E402

# Full text of a page can be huge; cap what we carry into the pack so the
# in-session synthesis stays sharp instead of drowning in one source.
TEXT_CAP = 4000
FULLTEXT_TOP_N = 6


def _trim(txt, cap=TEXT_CAP):
    if not txt:
        return None
    txt = txt.strip()
    return txt[:cap] + ("..." if len(txt) > cap else "")


def build_pack(topic, description="", reference=None, num=12):
    client = get_client()
    pack = {"topic": topic, "description": description, "reference": None,
            "sources": [], "errors": []}

    # 1. Seed: the row's Reference URL, fetched directly.
    if reference:
        try:
            ref = get_contents([reference], text=True, client=client)
            for r in ref.get("results", []):
                pack["reference"] = {
                    "title": r.get("title"), "url": r.get("url"),
                    "text": _trim(r.get("text"), TEXT_CAP * 2),  # the primary source gets more room
                }
        except Exception as e:  # noqa: BLE001 - a dead reference URL shouldn't kill the run
            pack["errors"].append(f"reference fetch failed: {e}")

    # 2. Search: deep neural search with highlights for citability.
    query = f"{topic}. {description}".strip().rstrip(".")
    try:
        res = search(query, num_results=num, type="deep", text=False,
                     highlights=True, summary=True, client=client)
    except Exception as e:  # noqa: BLE001
        pack["errors"].append(f"search failed: {e}")
        return pack

    seen = set()
    if reference:
        seen.add(reference.rstrip("/").lower())
    for r in res.get("results", []):
        url = (r.get("url") or "").rstrip("/").lower()
        if not url or url in seen:
            continue
        seen.add(url)
        pack["sources"].append({
            "title": r.get("title"), "url": r.get("url"),
            "published_date": r.get("published_date"), "author": r.get("author"),
            "summary": r.get("summary"),
            "highlights": (r.get("highlights") or [])[:3],
            "text": None,
        })

    # 3. Full text for the top few, so the synthesis has real substance.
    top = pack["sources"][:FULLTEXT_TOP_N]
    if top:
        try:
            full = get_contents([s["url"] for s in top], text=True, client=client)
            by_url = {(r.get("url") or "").rstrip("/").lower(): r.get("text")
                      for r in full.get("results", [])}
            for s in top:
                s["text"] = _trim(by_url.get(s["url"].rstrip("/").lower()))
        except Exception as e:  # noqa: BLE001
            pack["errors"].append(f"contents fetch failed: {e}")

    pack["num_sources"] = len(pack["sources"])
    return pack


def main():
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Build an Exa source pack for a schedule topic.")
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

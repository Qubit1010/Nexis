#!/usr/bin/env python3
"""
Live Exa search for api-scout.
Fallback for APIs not in the public-apis catalog, or to check for newer/niche options.

Usage:
    python .claude/skills/api-scout/scripts/search_api.py --query "sports scores api"
    python .claude/skills/api-scout/scripts/search_api.py --query "AI image generation api" --category "Machine Learning"
    python .claude/skills/api-scout/scripts/search_api.py --query "crypto price api" --num 5
"""
from __future__ import annotations

import sys
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from tools.exa.exa_client import search  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description="Search Exa for free/public APIs on demand.")
    p.add_argument("--query", required=True, help="Search query")
    p.add_argument("--category", default=None, help="Optional category label for display")
    p.add_argument("--num", type=int, default=8, help="Number of results (default: 8)")
    args = p.parse_args()

    query = args.query
    if "api" not in query.lower():
        query = f"{query} api"
    if "free" not in query.lower():
        query = f"free {query}"

    print(f"Searching: {query!r}\n", flush=True)

    data = search(
        query,
        num_results=args.num,
        type="neural",
        text=False,
        highlights=True,
        summary=False,
    )

    results = data.get("results", [])
    if not results:
        print("No results found.")
        return

    print(f"Found {len(results)} results:\n")
    for i, r in enumerate(results, 1):
        title = r.get("title") or "Unknown"
        url = r.get("url", "")
        highlights = r.get("highlights") or []
        snippet = highlights[0][:220] if highlights else ""

        print(f"{i}. **{title}**")
        print(f"   URL: {url}")
        if args.category:
            print(f"   Category: {args.category}")
        if snippet:
            print(f"   About: {snippet}")
        print()


if __name__ == "__main__":
    main()

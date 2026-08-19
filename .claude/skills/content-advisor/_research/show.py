#!/usr/bin/env python3
"""Print a pass's report alongside its sources, with [sN] indices already resolved.

    python show.py q1_firm_generated_content_effects [--report] [--max 40]

Written for the synthesis-writing step: the pass `report` names sources by title and URL,
but references/research-synthesis.md has to cite them as [sN]. This prints both side by
side so a claim can be traced to an index without hand-matching URLs.

Tiers are printed as the tags the synthesis uses: C confirmed, K craft, P practitioner,
P* first-party platform documentation.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Windows consoles default to cp1252 and the reports contain non-breaking hyphens and
# smart quotes, which raise UnicodeEncodeError mid-print and truncate the output.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
TAG = {"confirmed": "C", "craft": "K", "practitioner": "P"}


def main(argv):
    key = argv[0]
    want_report = "--report" in argv
    mx = int(argv[argv.index("--max") + 1]) if "--max" in argv else 40

    srcs = json.loads((HERE / "sources.json").read_text(encoding="utf-8"))["sources"]
    mine = [s for s in srcs if key in (s.get("topics") or [])]
    mine.sort(key=lambda s: ({"confirmed": 0, "practitioner": 1, "craft": 2}[s["tier"]], s["index"]))

    print(f"### {key}  ({len(mine)} sources in corpus)\n")
    for s in mine[:mx]:
        tag = "P*" if s.get("first_party") else TAG[s["tier"]]
        multi = "" if len(s["topics"]) == 1 else f"  +{len(s['topics'])-1}pass"
        print(f"[s{s['index']}] {tag:2} {(s['title'] or '')[:96]}{multi}")
        print(f"        {s['url'][:110]}")

    if want_report:
        data = json.loads((HERE / "passes" / f"{key}.json").read_text(encoding="utf-8"))
        rep = data.get("report") or data.get("answer") or ""
        print("\n--- report ---\n")
        print(rep)


if __name__ == "__main__":
    main(sys.argv[1:])

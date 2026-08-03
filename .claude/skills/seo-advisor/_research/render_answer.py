#!/usr/bin/env python3
"""Render a synthesis answer with its citations resolved to global [sN] indices.

    python render_answer.py q5_core_web_vitals          # topic-notebook answer
    python render_answer.py q5_core_web_vitals --core    # the A_core cross-check
    python render_answer.py q5_core_web_vitals --sources # just the cited source list

NotebookLM numbers citations locally per answer ([1], [3-6], [10, 12]) and exposes the
mapping in `references[]` as citation_number -> source_id. `sources.json` maps
source_id -> our stable global index. This script composes the two so the synthesis can
be written with [sN] markers that `build_corpus.py verify` can actually check.

Two things worth knowing:
  * NotebookLM emits RANGES ("[3-6]"), not just comma lists. Expanding them is required
    or most citations silently resolve to nothing.
  * A citation whose source_id is absent from sources.json is net-new (it came from a
    notebook source we never indexed). Those render as [?uuid] rather than being
    dropped, so they are visible instead of silently swallowed.
"""
import json
import re
import sys
from pathlib import Path

RESEARCH_DIR = Path(__file__).resolve().parent


def _load(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def resolve(key, core=False):
    sj = _load(RESEARCH_DIR / "sources.json")
    uuid_to_index = sj["uuid_to_index"]
    by_index = {s["index"]: s for s in sj["sources"]}

    path = RESEARCH_DIR / f"{key}{'__core' if core else ''}.json"
    if not path.exists():
        raise SystemExit(f"missing {path.name}")
    data = _load(path)

    # local citation number -> global index (or None if net-new)
    local = {}
    for r in data.get("references", []):
        n = r.get("citation_number")
        sid = r.get("source_id")
        if n is None:
            continue
        local[n] = uuid_to_index.get(sid)

    def sub(m):
        body = m.group(1)
        nums = []
        for part in body.split(","):
            part = part.strip()
            rng = re.fullmatch(r"(\d+)\s*[-–]\s*(\d+)", part)
            if rng:                       # NotebookLM range form, e.g. [3-6]
                nums.extend(range(int(rng.group(1)), int(rng.group(2)) + 1))
            elif part.isdigit():
                nums.append(int(part))
            else:
                return m.group(0)         # not a citation, leave alone
        out, unknown = [], False
        for n in nums:
            gi = local.get(n)
            if gi:
                out.append(f"s{gi}")
            else:
                unknown = True
        if not out:
            return "[?]" if unknown else m.group(0)
        # dedupe, keep order
        seen, uniq = set(), []
        for x in out:
            if x not in seen:
                seen.add(x)
                uniq.append(x)
        return "[" + ", ".join(uniq) + ("+?]" if unknown else "]")

    answer = re.sub(r"\[([\d\s,–-]+)\]", sub, data.get("answer", ""))

    cited = sorted({gi for gi in local.values() if gi})
    return answer, cited, by_index, len(local)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    key = sys.argv[1]
    core = "--core" in sys.argv
    answer, cited, by_index, nrefs = resolve(key, core)

    if "--sources" in sys.argv:
        print(f"# {key}{'__core' if core else ''}: {len(cited)} distinct sources "
              f"({nrefs} citations)\n")
        for gi in cited:
            s = by_index[gi]
            tier = "CONFIRMED" if s["tier"] == "confirmed" else "practitioner"
            print(f"[s{gi}] ({tier}) {s['title'][:70]}")
            print(f"       {s['url'][:110]}")
    else:
        print(answer)
        print(f"\n---\n{len(cited)} distinct sources cited: "
              f"{', '.join('s'+str(i) for i in cited[:40])}"
              f"{' ...' if len(cited) > 40 else ''}")

#!/usr/bin/env python3
"""Build _research/sources.json: the global source index that resolves the
inline [n] citations in references/research-synthesis.md.

Two citation systems feed it:
  Q1-Q5  NotebookLM ask outputs (references carry source_id UUIDs). Resolving
         UUIDs to titles/URLs needs `notebooklm source list`; when auth is
         down they are indexed as unresolved and a re-run completes them.
  Q6-Q9  Exa-direct outputs (references carry url + title). Always resolvable.

Run: python .claude/skills/sales-playbook/_research/build_sources_index.py
Prints "resolved X/Y source_ids" as its own check.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOTEBOOK_ID = "f5ad3db7-87ee-4e2d-b674-3f977e797bb2"
NOTEBOOKLM = r"C:\Users\qubit\AppData\Local\Programs\Python\Python312\Scripts\notebooklm.exe"

Q_FILES = {
    "Q1": "q1_openers.json", "Q2": "q2_linkedin.json", "Q3": "q3_instagram.json",
    "Q4": "q4_closing.json", "Q5": "q5_objections.json",
    "Q6": "q6_human.json", "Q7": "q7_advance.json",
    "Q8": "q8_facebook.json", "Q9": "q9_cadence.json",
}


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8-sig"))


def notebook_sources() -> dict[str, dict]:
    """source_id -> {title, url} from the live notebook; {} if auth is down."""
    try:
        out = subprocess.run(
            [NOTEBOOKLM, "source", "list", "-n", NOTEBOOK_ID, "--json"],
            capture_output=True, text=True, timeout=120,
            encoding="utf-8", errors="replace")
        data = json.loads(out.stdout)
        items = data if isinstance(data, list) else data.get("sources", [])
        return {s.get("id") or s.get("source_id"): {"title": s.get("title", ""), "url": s.get("url", "")}
                for s in items if (s.get("id") or s.get("source_id"))}
    except Exception as e:  # noqa: BLE001 - auth down / CLI missing is expected
        print(f"notebooklm source list unavailable ({type(e).__name__}); Q1-Q5 UUIDs left unresolved")
        return {}


def main() -> None:
    nb = notebook_sources()
    sources: list[dict] = []
    uuid_to_index: dict[str, int] = {}
    url_to_index: dict[str, int] = {}
    total = resolved = 0

    def add(entry: dict) -> int:
        sources.append({"index": len(sources), **entry})
        return len(sources) - 1

    for q, fname in Q_FILES.items():
        path = HERE / fname
        if not path.exists():
            print(f"{q}: {fname} missing, skipped")
            continue
        for ref in load(path).get("references", []):
            total += 1
            sid, url = ref.get("source_id"), (ref.get("url") or "").rstrip("/")
            if sid:
                if sid not in uuid_to_index:
                    meta = nb.get(sid)
                    uuid_to_index[sid] = add({
                        "source_id": sid, "origin": "notebooklm", "q": q,
                        "title": (meta or {}).get("title", ""),
                        "url": (meta or {}).get("url", ""),
                        "resolved": bool(meta)})
                if sources[uuid_to_index[sid]]["resolved"]:
                    resolved += 1
            elif url:
                if url not in url_to_index:
                    url_to_index[url] = add({
                        "origin": "exa", "q": q, "title": ref.get("title", ""),
                        "url": url, "resolved": True})
                resolved += 1

    out = HERE / "sources.json"
    out.write_text(json.dumps(
        {"notebook_id": NOTEBOOK_ID, "sources": sources, "uuid_to_index": uuid_to_index},
        indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"resolved {resolved}/{total} source_ids -> {out} "
          f"({len(sources)} unique sources; unresolved fill in after notebooklm re-login)")


if __name__ == "__main__":
    main()

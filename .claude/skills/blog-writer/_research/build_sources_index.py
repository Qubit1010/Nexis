#!/usr/bin/env python3
"""Build the blog-writer research audit trail from the deep-research passes.

Reads q1..q5 JSON (research.py --json output), dedupes every result by
normalized URL into a global source index, and writes:
  - sources.json   : {sources:[{index,origin,q,title,url,date,resolved}], url_to_index}
  - reports.md     : the 5 synthesized cited reports concatenated (for writing the synthesis)

Exa-lane build (NotebookLM auth expired) - mirrors sales-playbook Q10-Q12 /
developer-advisor. Parse with utf-8-sig (redirected stdout may carry a BOM).
"""
import json
import glob
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

HERE = Path(__file__).resolve().parent


def norm_url(u: str) -> str:
    if not u:
        return ""
    try:
        s = urlsplit(u.strip())
        netloc = s.netloc.lower().replace("www.", "")
        path = s.path.rstrip("/")
        return urlunsplit((s.scheme.lower() or "https", netloc, path, "", "")).lower()
    except Exception:
        return u.strip().lower()


def main():
    files = sorted(glob.glob(str(HERE / "q*.json")))
    sources = []
    url_to_index = {}
    reports = []

    for f in files:
        d = json.load(open(f, encoding="utf-8-sig"))
        qid = Path(f).stem  # e.g. q1_blog_seo
        qlabel = qid.split("_")[0].upper()  # Q1
        report = d.get("report") or ""
        reports.append(f"\n\n{'='*80}\n# {qlabel} :: {qid}\nQUERY: {d.get('query','')}\n{'='*80}\n\n{report}\n")

        for r in d.get("results", []):
            url = r.get("url", "")
            key = norm_url(url)
            if not key or key in url_to_index:
                continue
            idx = len(sources)
            url_to_index[key] = idx
            origin = ",".join(r.get("sources", [])) or "exa"
            sources.append({
                "index": idx,
                "origin": origin,
                "q": qlabel,
                "title": (r.get("title") or "").strip()[:200],
                "url": url,
                "date": r.get("published_date") or "",
                "score": round(float(r.get("best_score") or 0), 4),
                "resolved": bool(url),
            })

    out = {
        "notebook_id": None,
        "corpus": "blog-writer 2026 (Exa/Serper/Jina deep passes; Tavily quota-capped)",
        "built": "2026-07-21",
        "n_sources": len(sources),
        "sources": sources,
        "url_to_index": url_to_index,
    }
    (HERE / "sources.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    (HERE / "reports.md").write_text("".join(reports), encoding="utf-8")
    print(f"sources.json: {len(sources)} unique sources")
    print(f"reports.md: {sum(len(x) for x in reports)} chars")
    # quick per-Q source counts
    from collections import Counter
    c = Counter(s["q"] for s in sources)
    for q in sorted(c):
        print(f"  {q}: {c[q]} sources")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Fetch full text of the curated Q6-Q9 URLs with Exa get_contents so the
synthesis can cite exact numbers, not just search highlights.

Run: python .claude/skills/sales-playbook/_research/fetch_contents.py

Writes to _research/exa/contents/: one .txt per URL (slugged filename) plus
contents_index.json mapping url -> file.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parents[4]
sys.path.insert(0, str(REPO_ROOT))

from tools.exa.exa_client import get_client, get_contents  # noqa: E402

OUT_DIR = HERE.parent / "exa" / "contents"
OUT_DIR.mkdir(parents=True, exist_ok=True)

URLS = [
    u.strip()
    for u in (HERE.parent / "exa" / "curated_urls.txt").read_text(encoding="utf-8").splitlines()
    if u.strip()
]


def slug(url: str) -> str:
    s = re.sub(r"^https?://(www\.)?", "", url).rstrip("/")
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:80]


def main() -> None:
    client = get_client()
    index: dict[str, str] = {}
    # batches of 10 keep each request small enough to not time out
    for i in range(0, len(URLS), 10):
        batch = URLS[i : i + 10]
        try:
            res = get_contents(batch, client=client, text={"max_characters": 20000})
        except Exception as e:  # noqa: BLE001 - keep fetching other batches
            print(f"batch {i // 10 + 1} FAILED: {e}")
            continue
        for r in res.get("results", []):
            url, text = r.get("url", ""), (r.get("text") or "").strip()
            if not url or not text:
                print(f"  EMPTY {url}")
                continue
            fname = slug(url) + ".txt"
            (OUT_DIR / fname).write_text(
                f"{r.get('title') or ''}\n{url}\n{r.get('published_date') or 'n.d.'}\n\n{text}",
                encoding="utf-8")
            index[url] = fname
            print(f"  ok {url} ({len(text)} chars)")
    (OUT_DIR / "contents_index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n{len(index)}/{len(URLS)} fetched -> {OUT_DIR}")


if __name__ == "__main__":
    main()

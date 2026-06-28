#!/usr/bin/env python3
"""Import the Exa-curated URLs into the clean NotebookLM notebook, one source at a time.

Reads _research/exa/urls.txt and adds each URL via the notebooklm CLI (auto-detects url vs youtube).
Logs success/failure per URL and is resume-safe: it skips URLs already present in the notebook.

Run (sandbox disabled):
    python .claude/skills/student-advisor/_research/import_to_notebooklm.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

NOTEBOOK_ID = "ffcd6d51-673d-4308-9400-c01976e3a849"
HERE = Path(__file__).resolve()
URLS = HERE.parent / "exa" / "urls.txt"
LOG = HERE.parent / "import-log.txt"


def find_exe() -> str:
    for c in [
        Path(r"C:\Users\Aleem\AppData\Local\Programs\Python\Python313\Scripts\notebooklm.exe"),
        Path(r"C:\Users\qubit\AppData\Local\Programs\Python\Python312\Scripts\notebooklm.exe"),
    ]:
        if c.exists():
            return str(c)
    w = shutil.which("notebooklm")
    if w:
        return w
    raise SystemExit("notebooklm.exe not found")


EXE = find_exe()


def log(msg: str):
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def existing_urls() -> set[str]:
    try:
        r = subprocess.run([EXE, "source", "list", "-n", NOTEBOOK_ID, "--json"],
                           capture_output=True, text=True, encoding="utf-8-sig",
                           errors="replace", timeout=120)
        data = json.loads(r.stdout or "{}")
        srcs = data.get("sources") or []
        return {(s.get("url") or "").rstrip("/").lower() for s in srcs if s.get("url")}
    except Exception:  # noqa: BLE001
        return set()


def main():
    urls = [u.strip() for u in URLS.read_text(encoding="utf-8").splitlines() if u.strip()]
    have = existing_urls()
    log(f"=== IMPORT START notebook={NOTEBOOK_ID} total={len(urls)} already={len(have)} ===")
    ok = fail = skip = 0
    for i, url in enumerate(urls, 1):
        if url.rstrip("/").lower() in have:
            skip += 1
            continue
        try:
            r = subprocess.run([EXE, "source", "add", url, "-n", NOTEBOOK_ID, "--json"],
                               capture_output=True, text=True, encoding="utf-8-sig",
                               errors="replace", timeout=180)
            if r.returncode == 0:
                ok += 1
                log(f"[{i}/{len(urls)}] OK {url}")
            else:
                fail += 1
                err = (r.stderr or r.stdout or "").strip().replace("\n", " ")[:160]
                log(f"[{i}/{len(urls)}] FAIL rc={r.returncode} {url} :: {err}")
        except Exception as e:  # noqa: BLE001
            fail += 1
            log(f"[{i}/{len(urls)}] ERROR {url} :: {e}")
        time.sleep(1.2)  # pace to avoid rate limits
    log(f"=== IMPORT DONE ok={ok} fail={fail} skip={skip} ===")


if __name__ == "__main__":
    main()

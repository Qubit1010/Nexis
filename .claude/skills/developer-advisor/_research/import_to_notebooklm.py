#!/usr/bin/env python3
"""Import the Exa-curated URLs into the clean NotebookLM notebook, one source at a time.

Reads _research/exa/urls.txt and adds each URL via the notebooklm CLI.
Resume-safe and self-healing:
  - Skips YouTube URLs entirely (NotebookLM can't ingest them without transcript data;
    they stay in the on-disk citation corpus, just not the notebook).
  - Only treats sources that are actually `ready` as "already present" — so a prior
    `error` entry does NOT block a retry.
  - Paces conservatively to avoid the throttle wall that errors out bulk adds.

Phases:
    import   (default) - add missing non-YouTube URLs.
    clean              - delete every source currently in `error` status.
    status             - print ready/error counts and exit.

Run (sandbox disabled):
    python .claude/skills/developer-advisor/_research/import_to_notebooklm.py clean
    python .claude/skills/developer-advisor/_research/import_to_notebooklm.py import
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

NOTEBOOK_ID = "5c8257d3-cdb3-469e-8d8c-da500a99ea14"
HERE = Path(__file__).resolve()
URLS = HERE.parent / "exa" / "urls.txt"
LOG = HERE.parent / "import-log.txt"
PACE_SECONDS = 3.0  # gentler than before; bulk adds get throttled/errored under ~2s


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


def is_youtube(url: str) -> bool:
    u = url.lower()
    return "youtube.com" in u or "youtu.be" in u


def log(msg: str):
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def list_sources() -> list[dict]:
    try:
        r = subprocess.run([EXE, "source", "list", "-n", NOTEBOOK_ID, "--json"],
                           capture_output=True, text=True, encoding="utf-8-sig",
                           errors="replace", timeout=120)
        data = json.loads(r.stdout or "{}")
        return data.get("sources") or []
    except Exception:  # noqa: BLE001
        return []


def ready_urls() -> set[str]:
    """URLs that are actually processed (status ready). Error entries are NOT counted,
    so a re-run retries them."""
    return {(s.get("url") or "").rstrip("/").lower()
            for s in list_sources()
            if s.get("url") and str(s.get("status", "")).lower() == "ready"}


def clean_errors():
    """Delete every source currently in error status (the red entries)."""
    srcs = list_sources()
    errored = [s for s in srcs if str(s.get("status", "")).lower() == "error"]
    log(f"=== CLEAN START errors={len(errored)} of {len(srcs)} ===")
    deleted = failed = 0
    for i, s in enumerate(errored, 1):
        sid = s.get("id")
        if not sid:
            continue
        try:
            r = subprocess.run([EXE, "source", "delete", sid, "-n", NOTEBOOK_ID, "--yes"],
                               capture_output=True, text=True, encoding="utf-8-sig",
                               errors="replace", timeout=90)
            if r.returncode == 0:
                deleted += 1
            else:
                # retry without --yes flag variant differences
                r2 = subprocess.run([EXE, "source", "delete", sid, "-n", NOTEBOOK_ID],
                                    capture_output=True, text=True, encoding="utf-8-sig",
                                    errors="replace", timeout=90, input="y\n")
                if r2.returncode == 0:
                    deleted += 1
                else:
                    failed += 1
                    log(f"  [{i}/{len(errored)}] DELETE FAIL {sid} :: {(r.stderr or r.stdout or '').strip()[:120]}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            log(f"  [{i}/{len(errored)}] DELETE ERROR {sid} :: {e}")
        time.sleep(0.6)
    log(f"=== CLEAN DONE deleted={deleted} failed={failed} ===")


def do_import():
    all_urls = [u.strip() for u in URLS.read_text(encoding="utf-8").splitlines() if u.strip()]
    urls = [u for u in all_urls if not is_youtube(u)]
    skipped_yt = len(all_urls) - len(urls)
    have = ready_urls()
    log(f"=== IMPORT START notebook={NOTEBOOK_ID} total={len(urls)} (skipped {skipped_yt} youtube) ready={len(have)} pace={PACE_SECONDS}s ===")
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
        time.sleep(PACE_SECONDS)
    log(f"=== IMPORT DONE ok={ok} fail={fail} skip={skip} ===")
    # A failed `source add` leaves a red error placeholder in the notebook. Auto-clean
    # that debris so a quota-blocked run never leaves the notebook littered.
    if fail:
        clean_errors()
        if ok == 0:
            log("NOTE: 0 adds succeeded - NotebookLM daily source-add quota is likely exhausted. "
                "Re-run `import` after it resets (~24h) to fill the remaining topics.")


def status():
    srcs = list_sources()
    ready = sum(1 for s in srcs if str(s.get("status", "")).lower() == "ready")
    error = sum(1 for s in srcs if str(s.get("status", "")).lower() == "error")
    other = len(srcs) - ready - error
    print(f"notebook={NOTEBOOK_ID} total={len(srcs)} ready={ready} error={error} other={other}")


if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "import"
    if phase == "clean":
        clean_errors()
    elif phase == "import":
        do_import()
    elif phase == "status":
        status()
    elif phase == "clean-and-import":
        clean_errors()
        time.sleep(2)
        do_import()
    else:
        raise SystemExit(f"Unknown phase: {phase} (use import | clean | status | clean-and-import)")

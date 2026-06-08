#!/usr/bin/env python3
"""
research_notebooklm.py - NotebookLM-backed research for the content engine.

Research is scoped STRICTLY to the topic: it does a fresh web-research pass into a
clean notebook, so the returned sources are about the topic, not a static corpus.

Two modes:
  --topic "..." [--depth light|medium|deep]
        Mode A: fresh web research on the topic, return the imported sources +
        the notebook id (so the constrained ask can target the same notebook).

  --topic "..." --notebook <id> --sources "id1,id2"
        Mode B: ask the notebook constrained to the selected sources, return prose.

Output: JSON to stdout (always exit 0 so the Node caller can JSON.parse).
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

NOTEBOOK_TITLE = "Content Engine Research"
NOTEBOOK_URL_PREFIX = "https://notebooklm.google.com/notebook/"

# NotebookLM's "deep" research mode is currently server-flaky (START_DEEP_RESEARCH /
# IMPORT_RESEARCH RPC failures). "fast" mode is reliable. So light + medium both use fast,
# and medium runs an extra angled pass into the same notebook (server-side dedup) to gather
# more sources. "deep" keeps deep mode for manual/best-effort use only.
#
# depth -> {mode, query suffixes (one research pass each), max sources returned, per-phase timeout}
DEPTH_CONFIG = {
    "light": {
        "mode": "fast",
        "suffixes": [""],
        "cap": 12,
        "timeout": 300,
    },
    "medium": {
        "mode": "fast",
        "suffixes": ["", " - latest 2026 developments, case studies, and advanced techniques"],
        "cap": 25,
        "timeout": 300,
    },
    "deep": {
        "mode": "deep",
        "suffixes": [""],
        "cap": 120,
        "timeout": 1500,
    },
}


def find_notebooklm_exe():
    python_dir = Path(sys.executable).parent
    candidates = [
        python_dir / "notebooklm.exe",
        python_dir / "Scripts" / "notebooklm.exe",
        python_dir.parent / "Scripts" / "notebooklm.exe",
    ]
    for c in candidates:
        if c.exists():
            return c
    on_path = shutil.which("notebooklm")
    return Path(on_path) if on_path else None


def run_nlm(exe, args, timeout=120, parse=True):
    """Run a notebooklm command. Returns parsed JSON (or raw stdout if parse=False)."""
    cmd = [str(exe)] + args
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8-sig",
        timeout=timeout,
    )
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        raise RuntimeError(f"notebooklm exited {result.returncode}: {stderr}")
    stdout = (result.stdout or "").strip()
    if not parse:
        return stdout
    if not stdout:
        raise RuntimeError("notebooklm returned empty output")
    return json.loads(stdout)


def error_out(msg):
    print(json.dumps({"available": False, "error": msg}))
    sys.exit(0)


def reset_research_notebook(exe):
    """Delete any prior research notebooks, create a fresh clean one. Returns its id."""
    try:
        listing = run_nlm(exe, ["list", "--json"], timeout=60)
        for nb in listing.get("notebooks", []):
            if nb.get("title") == NOTEBOOK_TITLE and nb.get("id"):
                try:
                    run_nlm(exe, ["delete", "-n", nb["id"], "-y", "--json"], timeout=60)
                except Exception:
                    pass  # best-effort cleanup; don't fail the run
    except Exception:
        pass  # if listing fails, just create a new one

    created = run_nlm(exe, ["create", NOTEBOOK_TITLE, "--json"], timeout=60)
    nb_id = created.get("notebook", {}).get("id")
    if not nb_id:
        raise RuntimeError("could not create research notebook")
    return nb_id


def mode_sources(exe, topic, depth):
    cfg = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["medium"])
    mode = cfg["mode"]
    suffixes = cfg["suffixes"]
    cap = cfg["cap"]
    research_timeout = cfg["timeout"]

    notebook_id = reset_research_notebook(exe)

    # Fresh web research scoped to the topic. NotebookLM's research/import RPCs are flaky and
    # can exit non-zero even after most sources imported fine, so each pass is best-effort: we
    # don't fail the run here. The source-list read-back below is authoritative. Medium runs
    # multiple angled passes into the same notebook (server-side dedup) to gather more sources.
    research_error = None
    for suffix in suffixes:
        query = (topic + suffix).strip()
        try:
            run_nlm(
                exe,
                [
                    "source", "add-research", query,
                    "--from", "web",
                    "--mode", mode,
                    "--import-all",
                    "--cited-only",
                    "-n", notebook_id,
                    "--timeout", str(research_timeout),
                    "--json",
                ],
                timeout=research_timeout + 120,
            )
        except Exception as e:
            research_error = str(e)  # keep the last error; only fatal if nothing lands

    # Read back whatever sources actually landed (id + title + url + status).
    listing = run_nlm(exe, ["source", "list", "-n", notebook_id, "--json"], timeout=120)
    raw_sources = listing.get("sources", [])

    # Only treat the research error as fatal if nothing imported at all.
    if not raw_sources and research_error:
        error_out(f"Research import failed and no sources were added: {research_error}")

    sources = []
    for s in raw_sources:
        if s.get("status") and s.get("status") != "ready":
            continue
        sid = s.get("id")
        if not sid:
            continue
        sources.append({
            "id": sid,
            "title": s.get("title", "") or "Untitled source",
            "url": s.get("url", ""),
        })

    sources = sources[:cap]

    print(json.dumps({
        "available": True,
        "topic": topic,
        "notebook_id": notebook_id,
        "notebook_url": NOTEBOOK_URL_PREFIX + notebook_id,
        "sources": sources,
    }))


def mode_ask(exe, topic, notebook_id, source_ids):
    question = (
        f"{topic}. "
        "Provide a comprehensive, detailed synthesis covering the key facts, statistics, "
        "practical steps, and real-world examples found in these sources. Write in flowing prose."
    )
    cmd = ["ask", question, "--json", "-n", notebook_id]
    for sid in source_ids:
        cmd.extend(["-s", sid])

    response = run_nlm(exe, cmd, timeout=180)
    answer = response.get("answer", "")
    if not answer:
        error_out("No answer returned from NotebookLM")
    print(json.dumps({"available": True, "answer": answer}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--depth", default="medium", choices=["light", "medium", "deep"])
    parser.add_argument("--notebook", default="")
    parser.add_argument("--sources", default="")
    args = parser.parse_args()

    topic = args.topic.strip()
    source_ids = [s.strip() for s in args.sources.split(",") if s.strip()] if args.sources else []

    exe = find_notebooklm_exe()
    if not exe:
        error_out("notebooklm not found - run: pip install notebooklm-py && notebooklm login")

    try:
        if source_ids:
            if not args.notebook:
                error_out("--notebook is required when --sources is set")
            mode_ask(exe, topic, args.notebook.strip(), source_ids)
        else:
            mode_sources(exe, topic, args.depth)
    except subprocess.TimeoutExpired:
        error_out("NotebookLM research timed out. Try a lighter depth or a narrower topic.")
    except Exception as e:
        error_out(str(e))


if __name__ == "__main__":
    main()

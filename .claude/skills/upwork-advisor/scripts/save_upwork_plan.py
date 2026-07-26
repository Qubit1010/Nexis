#!/usr/bin/env python3
"""Save an Upwork plan (profile rewrite, 90-day plan, rate-raise plan) as a Google Doc.

Thin wrapper. The actual JSON -> Google Doc writer lives in the student-advisor skill
and is already generic: it takes a plan on stdin and picks its Drive folder from an
env var. Rather than copy ~150 lines of gws plumbing (which would drift), this just
points that script at an "Upwork Advisor" folder and hands stdin straight through.

Usage:
    echo '{"title":"...","sections":[...]}' | python save_upwork_plan.py
    cat plan.json | python save_upwork_plan.py

Override the Drive folder with UPWORK_DOCS_FOLDER.

Output (stdout): {"status": "ok", "doc_url": "...", "doc_id": "..."}

Plan JSON shape:
    {
      "title": "Upwork Profile Rewrite - AI Automation Positioning",
      "sections": [
        {"heading": "...", "level": 1, "body": "..."},
        {"heading": "...", "level": 2, "bullets": ["...", "..."]},
        {"heading": "...", "level": 2,
         "table": {"headers": ["...", "..."], "rows": [["...", "..."]]}}
      ]
    }

Use plain hyphens, not em dashes, and avoid exotic unicode: Google Docs mangles it
(see the `feedback_google_docs_encoding` memory).
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
SKILLS_DIR = HERE.parents[2]
WRITER = SKILLS_DIR / "student-advisor" / "scripts" / "save_student_plan.py"


def main() -> int:
    if not WRITER.exists():
        print(
            f'{{"status": "error", "error": "writer script not found at {WRITER}"}}',
            file=sys.stderr,
        )
        return 1

    env = dict(os.environ)
    # The writer reads its target folder from STUDENT_DOCS_FOLDER, and its folder-id
    # cache path from PLAN_FOLDER_CACHE. Give it ours so the two skills don't fight
    # over one cache file.
    env["STUDENT_DOCS_FOLDER"] = env.get("UPWORK_DOCS_FOLDER", "Upwork Advisor")
    env["PLAN_FOLDER_CACHE"] = str(HERE.parents[1] / ".folder_id")

    # Pass stdin/stdout straight through so the wrapper is transparent.
    return subprocess.run([sys.executable, str(WRITER)], env=env).returncode


if __name__ == "__main__":
    raise SystemExit(main())

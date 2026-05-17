#!/usr/bin/env python3
"""
Wrap `npm run build`, capture exit code + tail of output, and classify common
errors into actionable categories.

Usage:
    python verify_build.py <app-dir>

Exit code 0 = build passed.
Non-zero = build failed (or classification produced auto-fix suggestions).
"""

import json
import re
import subprocess
import sys
from pathlib import Path


# Known error patterns → fix description
KNOWN_PATTERNS = [
    {
        "id": "css-import-order",
        "pattern": r"@import rules must precede all rules aside from @charset",
        "fix": "Move font @import statements ABOVE `@import \"tailwindcss\"` in src/app/globals.css",
    },
    {
        "id": "client-component-handler",
        "pattern": r"Event handlers cannot be passed to Client Component props",
        "fix": "Add `\"use client\";` as the first line of the component file containing onClick/onChange/etc",
    },
    {
        "id": "module-not-found",
        "pattern": r"Module not found:.*Can't resolve '@/lib/content'",
        "fix": "Create src/lib/content.ts (the @/lib/content import expects a file at src/lib/content.ts)",
    },
    {
        "id": "tsx-syntax",
        "pattern": r"Syntax error|Unexpected token",
        "fix": "TSX syntax error — re-check JSX braces, unclosed tags, or stray characters",
    },
    {
        "id": "image-fill-no-sizes",
        "pattern": r'Image with src ".*" has "fill" but is missing "sizes" prop',
        "fix": "WARNING ONLY (not a blocker): add sizes prop to <Image fill /> for perf",
        "warning_only": True,
    },
    {
        "id": "image-modified-dim",
        "pattern": r"has either width or height modified, but not the other",
        "fix": "WARNING ONLY: set explicit width AND height (or one + 'auto') on <Image>",
        "warning_only": True,
    },
]


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit("Usage: verify_build.py <app-dir>")

    app_dir = Path(sys.argv[1]).resolve()
    if not (app_dir / "package.json").exists():
        sys.exit(f"No package.json in {app_dir}")

    print(f"Building {app_dir} ...", flush=True)
    # Use npm via shell on Windows so it picks up npm.cmd
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=str(app_dir),
        capture_output=True,
        text=True,
        shell=(sys.platform == "win32"),
        timeout=300,
    )

    out = (result.stdout or "") + "\n" + (result.stderr or "")
    tail = "\n".join(out.splitlines()[-80:])

    matches = []
    for known in KNOWN_PATTERNS:
        if re.search(known["pattern"], out, re.IGNORECASE):
            matches.append(known)

    blocking = [m for m in matches if not m.get("warning_only")]
    warnings = [m for m in matches if m.get("warning_only")]

    report = {
        "app": str(app_dir),
        "exit_code": result.returncode,
        "passed": result.returncode == 0,
        "matched_known_errors": [m["id"] for m in blocking],
        "warnings": [m["id"] for m in warnings],
        "fixes": [m["fix"] for m in matches],
        "tail": tail,
    }
    print(json.dumps(report, indent=2))

    if result.returncode != 0:
        print("\n--- BUILD FAILED ---")
        if blocking:
            print("Auto-fix suggestions:")
            for m in blocking:
                print(f"  • [{m['id']}] {m['fix']}")
        else:
            print("(no known patterns matched — read the tail above)")
        sys.exit(result.returncode)
    else:
        print("\nBuild passed.")
        if warnings:
            print("Warnings (not blocking):")
            for m in warnings:
                print(f"  • [{m['id']}] {m['fix']}")


if __name__ == "__main__":
    main()

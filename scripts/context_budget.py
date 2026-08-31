"""Measure what loads into context on every single turn, before the user types anything.

This is the ablation instrument. Boris Cherny's method for trimming a harness is to delete,
use it, and restore only what demonstrably breaks - which only works if "how much is loaded"
is a number you can re-read after each change rather than a feeling. Run it before a trim,
run it after, and diff.

Counts the four things that are genuinely always-on:
  1. CLAUDE.md + CLAUDE.local.md, and every file they pull in with an `@path` import
  2. .claude/rules/*.md          (loaded wholesale, every turn)
  3. the auto-memory MEMORY.md index
  4. the `description:` frontmatter of every SKILL.md (metadata is always in context;
     the body is not, and is deliberately excluded)

Usage:
    python scripts/context_budget.py              # summary table
    python scripts/context_budget.py --detail     # every file, largest first
    python scripts/context_budget.py --json       # machine-readable, for diffing runs
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MEMORY_INDEX = (
    Path.home() / ".claude" / "projects"
    / "c--Users-qubit-OneDrive-Documents-Automations-Nexis" / "memory" / "MEMORY.md"
)

# Rough and deliberately crude. The point is to compare two runs of this script, not to
# predict a tokenizer. ~4 chars/token is close enough for English prose and stays stable.
CHARS_PER_TOKEN = 4

_IMPORT = re.compile(r"^\s*[-*]?\s*@(\S+)", re.M)
_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---", re.S)
_DESCRIPTION = re.compile(r"^description:\s*(.*?)(?=\n[a-zA-Z_-]+:|\Z)", re.S | re.M)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _resolve(raw: str) -> Path:
    """An @import is either repo-relative or an absolute path (the agency-brain bridge)."""
    p = Path(raw)
    return p if p.is_absolute() else REPO / raw


def collect_imports(entry_points: list[Path]) -> list[tuple[str, int]]:
    """Follow @imports transitively so a nested import cannot hide from the count."""
    seen: set[Path] = set()
    out: list[tuple[str, int]] = []
    queue = list(entry_points)
    while queue:
        path = queue.pop(0)
        resolved = path.resolve() if path.exists() else path
        if resolved in seen:
            continue
        seen.add(resolved)
        text = _read(path)
        if not text and not path.exists():
            out.append((f"{path}  [MISSING]", 0))
            continue
        try:
            label = str(path.relative_to(REPO))
        except ValueError:
            label = str(path)
        out.append((label, len(text)))
        queue.extend(_resolve(m) for m in _IMPORT.findall(text))
    return out


def collect_skill_descriptions() -> list[tuple[str, int]]:
    rows = []
    for skill_md in sorted(REPO.glob(".claude/skills/*/SKILL.md")):
        fm = _FRONTMATTER.search(_read(skill_md))
        if not fm:
            continue
        desc = _DESCRIPTION.search(fm.group(1))
        if desc:
            rows.append((skill_md.parent.name, len(desc.group(1).strip())))
    return rows


def build_report() -> dict:
    groups = {
        "CLAUDE.md + @imports": collect_imports(
            [REPO / "CLAUDE.md", REPO / "CLAUDE.local.md"]
        ),
        ".claude/rules/": [
            (str(p.relative_to(REPO)), len(_read(p)))
            for p in sorted(REPO.glob(".claude/rules/*.md"))
        ],
        "MEMORY.md index": [("MEMORY.md", len(_read(MEMORY_INDEX)))],
        "skill descriptions": collect_skill_descriptions(),
    }
    return {
        "groups": {k: [{"name": n, "chars": c} for n, c in v] for k, v in groups.items()},
        "totals": {k: sum(c for _, c in v) for k, v in groups.items()},
        "total_chars": sum(sum(c for _, c in v) for v in groups.values()),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--detail", action="store_true", help="list every file, largest first")
    ap.add_argument("--json", action="store_true", help="emit JSON for diffing two runs")
    args = ap.parse_args()

    report = build_report()
    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    total = report["total_chars"]
    print(f"{'ALWAYS-LOADED COMPONENT':<28} {'chars':>10} {'~tokens':>9} {'share':>7}")
    print("-" * 58)
    for name, chars in sorted(report["totals"].items(), key=lambda kv: -kv[1]):
        share = f"{100 * chars / total:.0f}%" if total else "-"
        print(f"{name:<28} {chars:>10,} {chars // CHARS_PER_TOKEN:>9,} {share:>7}")
    print("-" * 58)
    print(f"{'TOTAL, every turn':<28} {total:>10,} {total // CHARS_PER_TOKEN:>9,}")

    if args.detail:
        for group, rows in report["groups"].items():
            print(f"\n--- {group} ---")
            for row in sorted(rows, key=lambda r: -r["chars"]):
                print(f"{row['chars']:>8,}  {row['name']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Append a drafted comment-run's markdown file to the running Google Sheet log.

Separate from fetch_posts.py on purpose: the sheet should hold the FINISHED batch (drafted
comments and all), not the raw fetch. This runs after Claude has filled in every
**Comment draft:** slot and done the batch review, so it parses the same markdown file a human
would read and mirrors it into the sheet as a durable, searchable log across days -- the local
.md files are easy to lose track of, a sheet is not.

Usage:
    python save_to_sheet.py                       # today's file
    python save_to_sheet.py --date 2026-07-30      # a specific day
    python save_to_sheet.py --file path/to/x.md    # explicit path
    python save_to_sheet.py --sheet <id>           # override LINKEDIN_COMMENT_SHEET_ID
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]  # scripts/ -> linkedin-commenter/ -> skills/ -> .claude/ -> repo
sys.path.insert(0, str(REPO / ".claude" / "skills" / "web-scraper" / "scripts"))
sys.path.insert(0, str(REPO / ".claude" / "skills" / "leads-to-crm" / "scripts"))

from _env import load_env  # noqa: E402
import sheets  # noqa: E402

load_env()

OUT_DIR = REPO / "docs" / "linkedin-comments"
TAB = "Log"
HEADER = ["Date", "#", "Author", "Age", "Likes", "Comments", "Shares", "Score",
          "Post URL", "Post preview", "Comment draft", "Status", "Posted"]

# Blocks are split on the "## " heading marker rather than matched as one regex. A single
# end-to-end pattern needs to know exactly how many blank lines separate the comment text from
# the closing "---", and that count depends on how much of the placeholder Claude's Edit calls
# happened to overwrite -- it is not reliably one blank line. Splitting first and using DOTALL
# on the remainder sidesteps counting newlines entirely.
_HEADER = re.compile(r"^(\d+)\.\s*(.+)$", re.M)
_META = re.compile(
    r"(\d+)h.*?(\d+)\s*likes\s*/\s*(\d+)\s*comments(?:\s*/\s*(\d+)\s*shares)?.*?score\s*([\d.]+)"
    r".*?\[open the post\]\(([^)]+)\)"
)
_DRAFT = re.compile(r"\*\*Comment draft:\*\*\s*(.*?)(?:\n---|\Z)", re.S)


def parse_file(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    rows = []
    for block in re.split(r"^## ", text, flags=re.M)[1:]:
        head = _HEADER.match(block)
        meta = _META.search(block)
        draft = _DRAFT.search(block)
        if not (head and meta and draft):
            continue  # a block that doesn't match the expected shape is skipped, not fatal

        rank, author = head.groups()
        age, likes, comments, shares, score, url = meta.groups()

        quote_lines = [ln[1:].strip() for ln in block.splitlines() if ln.startswith(">")]
        preview = " ".join(ln for ln in quote_lines if ln)

        comment = draft.group(1).strip()
        skipped = comment.startswith("_skipped")
        status = "skipped" if skipped else ("drafted" if comment else "empty")
        if skipped:
            comment = comment.strip("_").removeprefix("skipped:").strip()

        rows.append({
            "rank": rank, "author": author.strip(), "age": f"{age}h",
            "likes": likes, "comments": comments, "shares": shares or "0", "score": score,
            "url": url, "preview": preview[:200], "comment": comment,
            "status": status,
        })
    return rows


def ensure_tab(sheet_id: str, tab: str) -> None:
    """Create the Log tab with a header row if it doesn't exist yet."""
    meta = sheets.get_metadata(sheet_id)
    titles = [sh["properties"]["title"] for sh in meta.get("sheets", [])]
    if tab in titles:
        return
    sheets.batch_update(sheet_id, [{"addSheet": {"properties": {"title": tab}}}])
    sheets.update_range(sheet_id, f"{tab}!A1", [HEADER])


def already_logged(sheet_id: str, tab: str, run_date: str) -> bool:
    """True if this date's Column A already has rows. Re-running the same day's file would
    otherwise duplicate every row, since append_rows has no way to know a prior run happened."""
    values = sheets.read_values(sheet_id, tab)
    return any(row and row[0] == run_date for row in values[1:])


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--date", default=date.today().isoformat())
    p.add_argument("--file", type=Path, default=None)
    p.add_argument("--sheet", default=os.environ.get("LINKEDIN_COMMENT_SHEET_ID", ""))
    p.add_argument("--force", action="store_true", help="append again even if this date is already logged")
    args = p.parse_args()

    path = args.file or (OUT_DIR / f"{args.date}.md")
    if not path.exists():
        sys.exit(f"No file at {path}. Run fetch_posts.py and draft the comments first.")
    if not args.sheet:
        sys.exit("No sheet id. Set LINKEDIN_COMMENT_SHEET_ID in .env or pass --sheet.")

    rows = parse_file(path)
    if not rows:
        sys.exit(f"Parsed 0 posts from {path}. Has the file's format changed?")

    run_date = path.stem  # the YYYY-MM-DD the file is named for, not necessarily today
    ensure_tab(args.sheet, TAB)
    if not args.force and already_logged(args.sheet, TAB, run_date):
        sys.exit(f"{run_date} is already in the Log tab. Pass --force to append a second copy.")

    values = [[run_date, r["rank"], r["author"], r["age"], r["likes"], r["comments"], r["shares"],
               r["score"], r["url"], r["preview"], r["comment"], r["status"], ""] for r in rows]
    if not sheets.append_rows(args.sheet, TAB, values):
        sys.exit("Append failed, see error above.")

    drafted = sum(1 for r in rows if r["status"] == "drafted")
    skipped = sum(1 for r in rows if r["status"] == "skipped")
    print(f"[sheet] appended {len(rows)} rows ({drafted} drafted, {skipped} skipped) -> "
          f"https://docs.google.com/spreadsheets/d/{args.sheet}")


if __name__ == "__main__":
    main()

"""Mechanical checks for a Notes from the Workbench issue.

    python check_issue.py <issue.md> [--source-url https://aleemuh.com/blog/<slug>]

Checks only the part above `<!-- end issue -->`. Exits 1 on any failure, so a caller cannot
mistake a failed check for a pass. Always prints the word count first: no word count in the
output means the check did not run.
"""

import argparse
import re
import sys

BANNED = [r"nexus\s*-?\s*point", r"\bbsai\b", r"\biqra\b", r"\buniversity\b", r"\bsemester\b"]
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]")
PLACEHOLDER = re.compile(r"\[(?:[^\]]*\b(?:TODO|TBD|placeholder|insert|X+)\b[^\]]*)\]", re.I)
CTA = re.compile(r"https://aleemuh\.com/(newsletter|contact)\b")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--source-url")
    args = ap.parse_args()

    text = open(args.path, encoding="utf-8").read()
    if "<!-- end issue -->" not in text:
        print("FAIL: no '<!-- end issue -->' marker, cannot tell the issue from the notes")
        return 1
    issue = text.split("<!-- end issue -->")[0]

    lines = issue.strip().splitlines()
    if not lines or not lines[0].startswith("# "):
        print("FAIL: first line must be the '# ' title")
        return 1
    body = "\n".join(lines[1:])
    prose = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", body)  # link text only
    words = len(re.findall(r"[A-Za-z0-9']+", prose))
    print(f"checked: {words} words in the issue body")

    fails, warns = [], []
    if "—" in issue or "–" in issue:
        fails.append("em or en dash present (use commas or periods)")
    for pat in BANNED:
        m = re.search(pat, issue, re.I)
        if m:
            fails.append(f"banned personal-brand term: '{m.group(0)}'")
    if EMOJI.search(issue):
        fails.append("emoji present")
    if PLACEHOLDER.search(issue):
        fails.append(f"unfilled placeholder: {PLACEHOLDER.search(issue).group(0)}")
    ctas = {m.group(1) for m in CTA.finditer(issue)}
    if len(ctas) != 1:
        fails.append(f"need exactly one CTA destination (/newsletter or /contact), found {sorted(ctas) or 'none'}")
    if args.source_url and args.source_url.rstrip("/") not in issue:
        fails.append(f"backlink to {args.source_url} missing")
    if "## The short version" not in issue:
        warns.append("no '## The short version' takeaways section")
    if not 350 <= words <= 750:
        warns.append(f"body is {words} words, house range is 400-600")

    for w in warns:
        print(f"WARN: {w}")
    for f in fails:
        print(f"FAIL: {f}")
    print("PASS" if not fails else f"{len(fails)} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

"""Brand + proof lint over rendered HTML in build/ (agency/16-brand-guidelines.md §5-7, verified proof list).

Flags: em dashes in body text, banned vocabulary, unverified proof claims. Competitor company names
(e.g. "Quetech Solutions") are allowed because they are proper nouns. Exit 1 if anything is flagged.
"""
import re
import sys
from pathlib import Path

BUILD = Path(__file__).resolve().parents[1] / "build"
BANNED = [r"\bseamless", r"\brobust\b", r"cutting[- ]edge", r"best[- ]in[- ]class", r"\bunlock", r"\bempower",
          r"\bsupercharge", r"\brevolutioni[sz]e", r"game[- ]changing", r"\bjourney\b", r"\bpassionate\b",
          r"\bdedicated\b", r"\bup to\b", r"\bagentic\b", r"\bRAG\b", r"LangChain", r"vector database", r"\bbypass",
          r"\bleverage\b(?!\.)", r"\bsynerg"]
PROPER_SOLUTIONS = re.compile(r"(Quetech|UXPro|Nizi|Ali Techno|Soft Innovative|Tijarah|Infotechno|Noor Software|"
                              r"Icon Pro Digital|360 Marketing|Prismatic|Tecveq)[^<]{0,20}Solutions", re.I)
UNVERIFIED = [r"90\+ ?clients", r"70% manual", r"95% (response )?accuracy", r"mvmt", r"bulletproof\.com"]


def text_of(html: str) -> str:
    html = re.sub(r"(?is)<(style|script|svg)[^>]*>.*?</\1>", " ", html)
    html = re.sub(r'(?is)<div[^>]*data-lint="skip"[^>]*>.*?</ul></div>', " ", html)  # instructional "never say" lists
    html = re.sub(r"https?://\S+", " ", html)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def main() -> int:
    problems = 0
    for f in sorted(BUILD.glob("*.html")):
        t = text_of(f.read_text(encoding="utf-8"))
        t_no_names = PROPER_SOLUTIONS.sub("", t)
        hits = []
        if "—" in t:
            hits.append(f"em dash x{t.count(chr(0x2014))}")
        for pat in BANNED:
            for m in re.finditer(pat, t_no_names, re.I):
                ctx = t_no_names[max(0, m.start() - 30): m.end() + 30]
                if "We build leverage" in ctx or "We build leverage" in t_no_names[m.start() - 20: m.end() + 5]:
                    continue
                hits.append(f"banned '{m.group(0)}': ...{ctx}...")
        if re.search(r"\bsolutions\b", t_no_names, re.I):
            for m in re.finditer(r"\bsolutions\b", t_no_names, re.I):
                hits.append(f"'solutions': ...{t_no_names[max(0, m.start() - 40): m.end() + 10]}...")
        for pat in UNVERIFIED:
            if re.search(pat, t, re.I):
                hits.append(f"UNVERIFIED claim '{pat}'")
        if hits:
            problems += len(hits)
            print(f"\n{f.name}")
            for h in hits:
                print("  -", h)
    print(f"\n{problems} issue(s)" if problems else "lint clean")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

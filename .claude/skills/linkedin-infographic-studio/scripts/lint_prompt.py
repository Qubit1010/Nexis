"""Pre-emit checks for image prompts written by linkedin-infographic-studio and
instagram-carousel-studio.

Usage:
    python lint_prompt.py check <prompt-file> --mode brand|anchored|colourful
    python lint_prompt.py set <slides-file> --mode brand|anchored|colourful [--slide-words 40] [--max-slides 7]
    python lint_prompt.py contrast "#FFFFFF" "#02A1E1"

`check` lints one prompt. `set` lints a carousel: slides separated by lines starting with
"### SLIDE", each slide checked on its own, plus three series checks: the opening style
paragraph is identical on every slide, no slide introduces a hex absent from that style
paragraph, and the slide count is within --max-slides (default Instagram's 20).

Both exit 0 on pass, 1 on a failed check, 2 when the check could not run at all (empty
prompt, unreadable palette file). The last line always says which, so "did not run" can
never be mistaken for "passed".

`contrast` prints the WCAG contrast ratio of a text colour on a fill, with the verdict
for body text (4.5:1) and for large headline text (3:1).
"""

import argparse
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[4]
PERSONAL_PALETTE = REPO / "agency" / "personal-brand-visual-identity.md"
BRAND_GROUND = "#000000"
BRAND_ACCENT = "#02A1E1"
RETIRED = {"#475569"}

# House heuristics, not benchmarks. No source measures how many rendered words current
# image models keep accurate, so these only warn.
WORD_WARN = 260
SLIDE_WORD_WARN = 40
MAX_SLIDES = 20        # Instagram's carousel limit
SLIDE_WARN = 12        # completion drops beyond roughly this, per content-advisor [K]

NEGATIVE = re.compile(
    r"\b(no|not|without|avoid|avoiding|don't|do not|never|none|nothing|exclude|excluding)\b",
    re.I)
FILLER = re.compile(
    r"\b(4k|8k|masterpiece|high quality|highest quality|beautiful|stunning|ultra[- ]detailed|"
    r"award[- ]winning|trending on)\b", re.I)
PIXELS = re.compile(r"\b\d{3,4}\s*[x×]\s*\d{3,4}\b|\b\d{2,4}\s*px\b", re.I)
FLAGS = re.compile(r"(?<![\w-])--[a-z]{1,10}\b", re.I)
MODEL_NAMES = re.compile(r"\b(nano banana|gpt-image|gpt image|dall-?e|midjourney|imagen|flux)\b", re.I)
AGENCY = re.compile(r"\b(nexus\s?point|iqra|university)\b", re.I)
RATIO = re.compile(r"\b(1:1|4:5|3:4|2:3|9:16|16:9)\b")
RATIO_WORD = re.compile(r"\b(portrait|square|vertical|landscape|wide)\b", re.I)
HEX = re.compile(r"#[0-9A-Fa-f]{6}\b")
QUOTED = re.compile(r"\"([^\"]*)\"|“([^”]*)”")
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]")
SLIDE_SPLIT = re.compile(r"^###\s*SLIDE\b.*$", re.I | re.M)


class DidNotRun(Exception):
    pass


def brand_hexes():
    """Hexes in the palette tables of sections 1 and 2 of the personal identity file."""
    try:
        text = PERSONAL_PALETTE.read_text(encoding="utf-8-sig")
    except OSError as e:
        raise DidNotRun(f"cannot read {PERSONAL_PALETTE}: {e}")
    allowed, section = set(), None
    for line in text.splitlines():
        m = re.match(r"##\s+(\d+)\.", line)
        if m:
            section = int(m.group(1))
            continue
        if section in (1, 2) and line.startswith("|"):
            cells = [c.strip() for c in line.split("|")]
            if len(cells) > 2:
                allowed.update(h.upper() for h in HEX.findall(cells[2]))
    if not allowed:
        raise DidNotRun(f"parsed zero hexes from {PERSONAL_PALETTE}; the file layout changed")
    return allowed


def strip_quoted(text):
    return QUOTED.sub(" ", text)


def quoted_words(text):
    return sum(len((a or b).split()) for a, b in QUOTED.findall(text))


def hexes_in(text):
    return {h.upper() for h in HEX.findall(text)}


def run_checks(prompt, mode, word_warn):
    """Return [(status, name, detail)] for one prompt."""
    if len(prompt.strip()) < 200:
        raise DidNotRun(f"prompt is {len(prompt.strip())} characters, too short to be a real prompt")
    results = []
    unquoted = strip_quoted(prompt)

    hits = sorted({m.group(0).lower() for m in NEGATIVE.finditer(unquoted)})
    results.append(("FAIL" if hits else "PASS", "positive framing",
                    f"negative words outside quoted text: {hits}" if hits else "none found"))

    dashes = prompt.count("—")
    results.append(("FAIL" if dashes else "PASS", "no em dashes",
                    f"{dashes} em dash(es)" if dashes else "none"))

    emojis = EMOJI.findall(prompt)
    results.append(("FAIL" if emojis else "PASS", "no emojis",
                    f"{len(emojis)} found" if emojis else "none"))

    bad = PIXELS.findall(prompt) + FLAGS.findall(prompt) + sorted(
        {m.lower() for m in MODEL_NAMES.findall(prompt)})
    results.append(("FAIL" if bad else "PASS", "universal (no pixels, flags, model names)",
                    f"found {bad}" if bad else "clean"))

    ok_ratio = bool(RATIO.search(prompt)) and bool(RATIO_WORD.search(prompt))
    results.append(("PASS" if ok_ratio else "FAIL", "ratio stated in words",
                    "found" if ok_ratio else "need e.g. 'vertical 4:5 portrait'"))

    filler = sorted({m.lower() for m in FILLER.findall(unquoted)})
    results.append(("FAIL" if filler else "PASS", "no filler adjectives",
                    f"found {filler}" if filler else "none"))

    agency = sorted({m.lower() for m in AGENCY.findall(prompt)})
    results.append(("FAIL" if agency else "PASS", "personal brand (no agency or university)",
                    f"found {agency}" if agency else "clean"))

    hexes = hexes_in(prompt)
    retired = hexes & RETIRED
    results.append(("FAIL" if retired else "PASS", "no retired hex",
                    f"found {sorted(retired)}" if retired else "clean"))
    results.append(("PASS" if hexes else "FAIL", "palette named in hex",
                    f"{len(hexes)} hexes" if hexes else "no hex values in the prompt"))

    if mode in ("brand", "anchored"):
        allowed = brand_hexes()
        missing = [h for h in (BRAND_GROUND, BRAND_ACCENT) if h not in hexes]
        results.append(("FAIL" if missing else "PASS", f"{mode}: brand ground and accent present",
                        f"missing {missing}" if missing else "both present"))
        if mode == "brand":
            off = sorted(hexes - allowed)
            results.append(("FAIL" if off else "PASS", "brand: every hex from the personal palette",
                            f"off-palette {off}" if off else f"all in {len(allowed)}-token palette"))

    words = quoted_words(prompt)
    results.append(("WARN" if words > word_warn else "PASS", "text budget",
                    f"{words} quoted words (house heuristic warns above {word_warn})"))
    return results


def report(results):
    for status, name, detail in results:
        print(f"[{status}] {name}: {detail}")
    fails = [r for r in results if r[0] == "FAIL"]
    if fails:
        print(f"LINT FAIL ({len(fails)} of {len(results)} checks failed)")
        return 1
    print(f"LINT PASS ({len(results)} checks ran)")
    return 0


def read(path):
    p = Path(path)
    if not p.exists():
        raise DidNotRun(f"{path} does not exist")
    return p.read_text(encoding="utf-8-sig")


def check(path, mode):
    try:
        return report(run_checks(read(path), mode, WORD_WARN))
    except DidNotRun as e:
        print(f"ERROR: {e}")
        print("LINT DID NOT RUN")
        return 2


def first_paragraph(text):
    return re.split(r"\n\s*\n", text.strip(), maxsplit=1)[0].strip()


def check_set(path, mode, slide_words, max_slides=MAX_SLIDES):
    try:
        text = read(path)
        slides = [s for s in SLIDE_SPLIT.split(text)[1:] if s.strip()]
        if len(slides) < 2:
            raise DidNotRun(f"found {len(slides)} slide(s); separate slides with lines "
                            f"starting '### SLIDE'")
        results = []
        for i, s in enumerate(slides, 1):
            for status, name, detail in run_checks(s, mode, slide_words):
                results.append((status, f"slide {i}: {name}", detail))
    except DidNotRun as e:
        print(f"ERROR: {e}")
        print("LINT DID NOT RUN")
        return 2

    n = len(slides)
    status = "FAIL" if n > max_slides else ("WARN" if n > SLIDE_WARN else "PASS")
    results.append((status, "series: slide count",
                    f"{n} slides (max {max_slides}"
                    + (f"; warns above {SLIDE_WARN})" if max_slides > SLIDE_WARN else ")")))

    styles = [first_paragraph(s) for s in slides]
    base = styles[0]
    differ = [i for i, st in enumerate(styles, 1) if st != base]
    if len(base) < 300:
        results.append(("FAIL", "series: style block present",
                        f"slide 1 opens with {len(base)} characters; the shared style paragraph "
                        f"should lead every slide"))
    else:
        results.append(("PASS", "series: style block present", f"{len(base)} characters"))
    results.append(("FAIL" if differ else "PASS", "series: style block identical on every slide",
                    f"differs on slides {differ}" if differ else f"identical across {n} slides"))

    palette = hexes_in(base)
    strays = {i: sorted(hexes_in(s) - palette) for i, s in enumerate(slides, 1)}
    strays = {i: h for i, h in strays.items() if h}
    results.append(("FAIL" if strays else "PASS", "series: every hex declared in the style block",
                    f"undeclared {strays}" if strays else f"{len(palette)} hexes, all declared"))
    return report(results)


def luminance(hex_):
    h = hex_.lstrip("#")
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    for h in (a, b):
        if not re.fullmatch(r"#?[0-9A-Fa-f]{6}", h):
            print(f"ERROR: {h} is not a 6-digit hex")
            return 2
    la, lb = luminance(a), luminance(b)
    ratio = (max(la, lb) + 0.05) / (min(la, lb) + 0.05)
    body = "PASS" if ratio >= 4.5 else "FAIL"
    large = "PASS" if ratio >= 3.0 else "FAIL"
    print(f"{a} on {b}: {ratio:.2f}:1  body text {body} (4.5)  large headline {large} (3.0)")
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("file")
    c.add_argument("--mode", required=True, choices=["brand", "anchored", "colourful"])
    s = sub.add_parser("set")
    s.add_argument("file")
    s.add_argument("--mode", required=True, choices=["brand", "anchored", "colourful"])
    s.add_argument("--slide-words", type=int, default=SLIDE_WORD_WARN)
    s.add_argument("--max-slides", type=int, default=MAX_SLIDES)
    k = sub.add_parser("contrast")
    k.add_argument("text")
    k.add_argument("fill")
    args = ap.parse_args()
    if args.cmd == "check":
        sys.exit(check(args.file, args.mode))
    if args.cmd == "set":
        sys.exit(check_set(args.file, args.mode, args.slide_words, args.max_slides))
    sys.exit(contrast(args.text, args.fill))


if __name__ == "__main__":
    main()

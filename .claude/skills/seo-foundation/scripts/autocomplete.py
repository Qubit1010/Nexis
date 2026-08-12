"""Google Autocomplete harvesting - the free half of keyword discovery.

Google's suggest endpoint is undocumented but public, needs no key, and returns what real
people actually type. That makes it the best free source of long-tail phrasing there is,
and the reason this skill can do real keyword discovery without a paid tool.

Measured 2026-08-06: 8 sequential calls in 5.5s, 10 suggestions each, 80 unique, no
blocking. It is still alive. But it is undocumented, so treat a failure as "this endpoint
changed" rather than "there are no keywords" - `--selftest` exists to tell those apart.

Three expansion patterns, which is what makes this better than typing a seed into a box:
  alphabet  "<seed> a".."<seed> z"   catches the long tail Google has demand data for
  prefix    "how <seed>", "best <seed>"  catches intent-bearing phrasings
  question  who/what/why/when/where/which/how  catches the AEO question layer
"""
from __future__ import annotations

import argparse
import json
import string
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ENDPOINT = "https://suggestqueries.google.com/complete/search"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

# Prefixes chosen to pull one bucket each: commercial investigation, transactional, and the
# comparison shape that so reliably signals a decision is being made.
PREFIXES = ["best", "top", "cheap", "affordable", "professional", "local",
            "how to choose", "alternatives to"]
SUFFIXES = ["vs", "or", "near me", "cost", "price", "review", "for small business"]
QUESTIONS = ["how", "what", "why", "when", "where", "which", "who", "is", "does", "can"]


def suggest(query: str, *, gl: str = "us", hl: str = "en", timeout: int = 15) -> list[str]:
    """One autocomplete call. Returns [] on failure rather than raising, so one dead query
    in a 200-call sweep does not sink the batch."""
    url = f"{ENDPOINT}?client=firefox&hl={hl}&gl={gl}&q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode("utf-8", errors="replace")
        parsed = json.loads(body)
        return [s for s in parsed[1] if isinstance(s, str)] if len(parsed) > 1 else []
    except (urllib.error.URLError, json.JSONDecodeError, IndexError, OSError):
        return []


def expand(seed: str, *, gl: str = "us", hl: str = "en", modes: tuple[str, ...] = ("alphabet", "prefix", "question"),
           delay: float = 0.3, progress: bool = True) -> dict[str, list[str]]:
    """Expand one seed across the requested patterns. Returns {pattern: [suggestions]}.

    Sleeps between calls on purpose. The endpoint is a courtesy, not a product, and
    hammering it is how it gets closed.
    """
    out: dict[str, list[str]] = {}
    plan: list[tuple[str, str]] = []

    if "alphabet" in modes:
        plan += [("alphabet", f"{seed} {c}") for c in string.ascii_lowercase]
    if "prefix" in modes:
        plan += [("prefix", f"{p} {seed}") for p in PREFIXES]
        plan += [("prefix", f"{seed} {s}") for s in SUFFIXES]
    if "question" in modes:
        plan += [("question", f"{q} {seed}") for q in QUESTIONS]

    failures = 0
    for i, (pattern, q) in enumerate(plan, 1):
        res = suggest(q, gl=gl, hl=hl)
        if not res:
            failures += 1
        out.setdefault(pattern, []).extend(res)
        if progress and i % 20 == 0:
            print(f"  [autocomplete] {i}/{len(plan)} calls", file=sys.stderr)
        time.sleep(delay)

    # A total wipeout means the endpoint changed, not that the seed has no demand. Say so.
    if failures == len(plan) and plan:
        print(f"  [autocomplete] WARNING: all {failures} calls returned nothing. "
              f"The undocumented endpoint may have changed - verify with --selftest.",
              file=sys.stderr)

    for k in out:
        out[k] = sorted(set(out[k]))
    return out


def expand_many(seeds: list[str], **kw) -> list[dict]:
    """Flatten several seeds into candidate rows ready for the Query|Source|Notes sheet."""
    rows, seen = [], set()
    for seed in seeds:
        for pattern, suggestions in expand(seed, **kw).items():
            for s in suggestions:
                key = s.strip().lower()
                if key and key not in seen:
                    seen.add(key)
                    rows.append({"query": s.strip(), "source": "autocomplete",
                                 "notes": f"{pattern} expansion of '{seed}'"})
    return rows


def _selftest() -> int:
    print("1. single call...")
    res = suggest("best crm for")
    if not res:
        print("   FAIL: endpoint returned nothing. It is undocumented and may have changed.")
        print("   Check manually: https://suggestqueries.google.com/complete/search?client=firefox&q=test")
        return 1
    print(f"   PASS: {len(res)} suggestions, e.g. {res[:3]}")

    print("2. alphabet expansion (6 letters, checking for rate limiting)...")
    got, t0 = set(), time.time()
    for c in "abcdef":
        s = suggest(f"crm software {c}")
        if not s:
            print(f"   FAIL: letter '{c}' returned nothing - possible rate limit")
            return 1
        got.update(s)
        time.sleep(0.3)
    print(f"   PASS: 6 calls in {time.time() - t0:.1f}s, {len(got)} unique suggestions, no blocking")

    print("3. question expansion...")
    qs = suggest("how to choose a crm")
    print(f"   {'PASS' if qs else 'WARN'}: {len(qs)} suggestions")

    print("\nRESULT: PASS - the endpoint is alive")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Harvest Google Autocomplete suggestions.")
    ap.add_argument("seed", nargs="?", help="seed keyword to expand")
    ap.add_argument("--gl", default="us"); ap.add_argument("--hl", default="en")
    ap.add_argument("--modes", default="alphabet,prefix,question",
                    help="comma-separated: alphabet, prefix, question")
    ap.add_argument("--json", action="store_true", help="emit candidate rows as JSON")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()
    if not args.seed:
        ap.error("seed required (or use --selftest)")

    modes = tuple(m.strip() for m in args.modes.split(",") if m.strip())
    if args.json:
        print(json.dumps(expand_many([args.seed], gl=args.gl, hl=args.hl, modes=modes),
                         ensure_ascii=False, indent=2))
    else:
        res = expand(args.seed, gl=args.gl, hl=args.hl, modes=modes)
        total = 0
        for pattern, suggestions in res.items():
            print(f"\n## {pattern} ({len(suggestions)})")
            for s in suggestions:
                print(f"  {s}")
            total += len(suggestions)
        print(f"\n{total} unique suggestions from '{args.seed}'", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

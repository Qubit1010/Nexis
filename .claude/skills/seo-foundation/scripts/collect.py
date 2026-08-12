"""Candidate collection and SERP-competitor discovery - the mechanical discovery layers.

`course/06` collects candidates across six layers. Three of them are mechanical and belong
in a script; three need judgment and belong to Claude:

  mechanical, here          judgment, Claude does it in-session
  ------------------------  ----------------------------------------
  autocomplete expansion    L1 reading the persona's question list
  PAA harvesting            L3 mining community phrasing (via `research`)
  related-search harvesting L4 reading competitor vocabulary (via `web-scraper`)
                            L6 AI fan-out / inverse prompting

L5 (paid keyword tools) is deliberately absent. There is no free volume API in 2026, and
`course/07` argues volume is the wrong sort key anyway - two tools disagree by up to 30x
and keyword difficulty is a vendor invention with no counterpart at Google.

The governing rule of this phase is **collect, do not judge**. Target 200+ raw candidates.
Only exact duplicates are dropped here; near-variants survive on purpose, because deciding
that "seo audit" and "seo site audit" are the same thing is the clustering step's job and
it makes that call from SERP evidence rather than from how similar the strings look.

Two subcommands:
  expand       seeds -> candidate rows (Query | Source | Notes)
  competitors  seeds -> the domains that actually own page one
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import autocomplete  # noqa: E402
import serp  # noqa: E402
from serp_features import PLATFORM_DOMAINS, UGC_DOMAINS, domain_of  # noqa: E402

# Aggregators and marketplaces rank for commercial queries everywhere but are not
# competitors you displace with a better page. `course/06` layer 4 and the aruntastic
# competitor-discovery method both say to exclude them and look for dedicated niche sites.
EXCLUDE_FROM_COMPETITORS = PLATFORM_DOMAINS | UGC_DOMAINS | {
    "forbes.com", "businessnewsdaily.com", "techradar.com", "pcmag.com", "cnet.com",
    "nerdwallet.com", "investopedia.com", "hubspot.com", "zapier.com", "shopify.com",
    "wix.com", "squarespace.com", "godaddy.com", "clutch.co", "goodfirms.co",
    "expertise.com", "thumbtack.com", "angi.com", "houzz.com", "bbb.org", "indeed.com",
}


def _rows(queries, source, note_fn):
    return [{"query": q, "source": source, "notes": note_fn(q)} for q in queries]


def expand(seeds: list[str], *, gl: str = "us", hl: str = "en",
           modes: tuple[str, ...] = ("alphabet", "prefix", "question"),
           skip_serp: bool = False) -> dict:
    """Run the mechanical layers over each seed."""
    rows: list[dict] = []

    print(f"[collect] autocomplete over {len(seeds)} seed(s)...", file=sys.stderr)
    rows += autocomplete.expand_many(seeds, gl=gl, hl=hl, modes=modes)

    if not skip_serp:
        print(f"[collect] SERP harvest (PAA + related) over {len(seeds)} seed(s)...", file=sys.stderr)
        serps = serp.fetch_many(seeds, gl=gl, hl=hl)
        for seed, data in serps.items():
            paa = [p.get("question", "") for p in (data.get("peopleAlsoAsk") or []) if p.get("question")]
            rel = [r.get("query", "") for r in (data.get("relatedSearches") or []) if r.get("query")]
            rows += _rows(paa, "paa", lambda q, s=seed: f"People Also Ask on '{s}'")
            rows += _rows(rel, "related", lambda q, s=seed: f"Related search on '{s}'")

    # Exact-duplicate collapse only. Near-variants are kept - see the module docstring.
    seen, deduped = set(), []
    for r in rows:
        key = r["query"].strip().lower()
        if key and key not in seen:
            seen.add(key)
            deduped.append(r)

    by_source = Counter(r["source"] for r in deduped)
    return {
        "seeds": seeds,
        "candidates": deduped,
        "count": len(deduped),
        "by_source": dict(by_source),
        "target_note": (
            f"{len(deduped)} candidates collected. course/06 targets 200+ before judging. "
            + ("Below target - add seeds, or bring in the judgment layers (persona questions, "
               "community mining, competitor vocabulary, AI fan-out)."
               if len(deduped) < 200 else "At target.")),
    }


def competitors(seeds: list[str], *, gl: str = "us", hl: str = "en",
                top: int = 5, business_competitors: list[str] | None = None) -> dict:
    """Who actually owns page one for these seeds.

    This is the aruntastic procedure, which the seo-advisor corpus does not cover: run 3-5
    seed searches, count the domains that recur across the organic results, drop the
    aggregators and platforms, keep the dedicated niche sites.

    It reconciles against the business competitor list when one is supplied, because the
    two sets routinely differ. The sites beating a client in search are often not the
    companies they think of as rivals, and that gap is a finding worth writing down.
    """
    if len(seeds) < 3:
        print(f"[collect] WARNING: {len(seeds)} seed(s). The method calls for 3-5 so a domain "
              f"has to recur to count as a competitor.", file=sys.stderr)

    serps = serp.fetch_many(seeds, gl=gl, hl=hl)
    appearances: Counter = Counter()
    queries_owned: dict[str, list[str]] = defaultdict(list)
    best_position: dict[str, int] = {}
    excluded: Counter = Counter()

    for q, data in serps.items():
        for r in (data.get("organic") or [])[:10]:
            d = domain_of(r.get("link", ""))
            if not d:
                continue
            if any(d == x or d.endswith("." + x) or x in d for x in EXCLUDE_FROM_COMPETITORS):
                excluded[d] += 1
                continue
            appearances[d] += 1
            queries_owned[d].append(q)
            pos = r.get("position", 99)
            best_position[d] = min(best_position.get(d, 99), pos)

    biz = {b.strip().lower().replace("www.", "") for b in (business_competitors or []) if b.strip()}
    ranked = []
    for d, n in appearances.most_common(top * 4):
        ranked.append({
            "domain": d,
            "appearances": n,
            "queries_owned": sorted(set(queries_owned[d])),
            "best_position": best_position.get(d),
            "recurring": n > 1,
            "also_a_business_competitor": any(b in d or d in b for b in biz) if biz else None,
        })

    search_only = [r["domain"] for r in ranked[:top] if r["also_a_business_competitor"] is False]
    matched = {r["domain"] for r in ranked if r["also_a_business_competitor"]}
    business_only = sorted(b for b in biz if not any(b in m or m in b for m in matched))

    return {
        "seeds": seeds,
        "search_competitors": ranked[:top],
        "runners_up": ranked[top:top + 5],
        "excluded_aggregators": [d for d, _ in excluded.most_common(10)],
        "reconciliation": {
            "business_competitors_supplied": sorted(biz) or None,
            "search_only_not_on_the_business_list": search_only or None,
            "business_only_absent_from_page_one": business_only or None,
            "note": ("Search competitors and business competitors are different sets. "
                     "Domains in the first list are beating this client in search without "
                     "necessarily competing with them commercially; names in the second are "
                     "commercial rivals who are invisible in these SERPs. Both are findings."),
        },
        "method_note": (
            f"{len([r for r in ranked[:top] if r['recurring']])} of the top {min(top, len(ranked))} "
            "recur across more than one seed. A domain appearing on a single seed is weak "
            "evidence - the method wants domains that show up consistently."),
    }


def _read_lines(path: str) -> list[str]:
    return [l.strip() for l in Path(path).read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.startswith("#")]


def main() -> int:
    ap = argparse.ArgumentParser(description="Collect keyword candidates / discover SERP competitors.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("expand", help="seeds -> candidate keyword rows")
    e.add_argument("--seeds", help="comma-separated seeds")
    e.add_argument("--seeds-file", help="text file, one seed per line")
    e.add_argument("--modes", default="alphabet,prefix,question")
    e.add_argument("--skip-serp", action="store_true", help="autocomplete only, spend no credits")

    c = sub.add_parser("competitors", help="seeds -> domains that own page one")
    c.add_argument("--seeds", help="comma-separated seeds")
    c.add_argument("--seeds-file")
    c.add_argument("--top", type=int, default=5)
    c.add_argument("--business-competitors", help="comma-separated, from the strategic foundation")

    for p in (e, c):
        p.add_argument("--gl", default="us"); p.add_argument("--hl", default="en")
        p.add_argument("--out", help="write JSON here")

    args = ap.parse_args()
    seeds = _read_lines(args.seeds_file) if getattr(args, "seeds_file", None) else \
        [s.strip() for s in (args.seeds or "").split(",") if s.strip()]
    if not seeds:
        ap.error("--seeds or --seeds-file required")

    if args.cmd == "expand":
        result = expand(seeds, gl=args.gl, hl=args.hl,
                        modes=tuple(m.strip() for m in args.modes.split(",") if m.strip()),
                        skip_serp=args.skip_serp)
        summary = f"{result['count']} candidates from {len(seeds)} seed(s): {result['by_source']}"
    else:
        bc = [b.strip() for b in (args.business_competitors or "").split(",") if b.strip()]
        result = competitors(seeds, gl=args.gl, hl=args.hl, top=args.top, business_competitors=bc)
        summary = f"{len(result['search_competitors'])} search competitors from {len(seeds)} seed(s)"

    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
        print(f"{summary} -> {args.out}")
    else:
        print(payload)
    print(f"\n{serp.cost_report()}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

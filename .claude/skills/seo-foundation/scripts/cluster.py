"""SERP-overlap clustering - group keywords by what Google actually returns.

The rule from `course/08` is "cluster by shared SERP outcome, not by shared wording",
because Google's own results are a better judge of intent than our intuition about
language. "seo audit" and "seo site audit" return the same page one, so they are one page.
"seo audit" and "seo audit tool" do not, so they are two. The words are closer in the
second pair and the intents are further apart, which is exactly why wording-based grouping
fails.

The course prescribes SERP-checking only 15-25 uncertain pairs, because it assumes you are
doing this by hand. We already hold every SERP from the difficulty read, so we compare all
pairs at zero additional cost. That is a strict improvement on the taught method, not a
shortcut around it.

**Complete linkage, not single-linkage.** Single-linkage chains: A matches B, B matches C,
so A and C land together even when they share nothing. That silently merges two intents
into one page, which is the exact failure the whole method exists to prevent. Anchoring
every member to a pivot is not enough either - two members can each overlap the pivot and
still share nothing with each other (the `--selftest` fixture is exactly this case). So a
query joins a cluster only if it clears the threshold against *every* member already in it.

That errs toward splitting, on purpose. A wrong split leaves a small cluster a human can
merge in seconds. A wrong merge silently gives one page two intents, which is invisible
until the page fails to rank for either.

The script proposes. Claude names the clusters and overrides the borderline calls, which
are surfaced deliberately rather than buried.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import serp  # noqa: E402
from serp_features import domain_of  # noqa: E402

# 3 shared URLs in a top 10 is the practitioner-standard threshold for "same intent".
# Lower it and unrelated queries merge; raise it and genuine clusters fragment.
DEFAULT_THRESHOLD = 3


def overlap(a: list[str], b: list[str]) -> int:
    """Shared URLs between two SERPs. Whole URLs, not domains: two different pages on the
    same big publisher are not evidence of shared intent, they are evidence of a big
    publisher."""
    return len(set(a) & set(b))


def build(queries: list[str], serps: dict[str, dict], *, threshold: int = DEFAULT_THRESHOLD,
          top_n: int = 10) -> dict:
    url_sets = {q: serp.urls_of(serps[q], top_n) for q in queries if q in serps}
    usable = [q for q in queries if url_sets.get(q)]
    dropped = [q for q in queries if q not in usable]

    pairs: dict[tuple[str, str], int] = {}
    for i, a in enumerate(usable):
        for b in usable[i + 1:]:
            n = overlap(url_sets[a], url_sets[b])
            if n:
                pairs[(a, b)] = n

    # Connectivity = how many other queries this one shares a SERP with. The most connected
    # query is the most central expression of its intent, which makes it the natural pivot
    # and the natural primary query.
    connectivity = {q: 0 for q in usable}
    for (a, b), n in pairs.items():
        if n >= threshold:
            connectivity[a] += 1
            connectivity[b] += 1

    def linked(a: str, b: str) -> int:
        return pairs.get((a, b), pairs.get((b, a), 0))

    assigned: set[str] = set()
    clusters: list[dict] = []
    for pivot in sorted(usable, key=lambda q: (-connectivity[q], q)):
        if pivot in assigned:
            continue
        members = [pivot]
        assigned.add(pivot)
        for other in sorted(usable, key=lambda q: (-connectivity[q], q)):
            if other in assigned:
                continue
            # Complete linkage: must clear the threshold against every existing member,
            # not just the pivot. See the module docstring for why the pivot alone is not
            # sufficient.
            if all(linked(m, other) >= threshold for m in members):
                members.append(other)
                assigned.add(other)
        clusters.append({
            "primary_query": pivot,
            "secondary_queries": members[1:],
            "size": len(members),
            "shared_urls_with_primary": {m: linked(pivot, m) for m in members[1:]},
            "serp_signature": url_sets[pivot][:5],
        })

    # Pairs one URL away from the threshold in either direction. These are the calls the
    # method says a human should make, and they are the only ones worth a human's time.
    borderline = sorted(
        [{"query_a": a, "query_b": b, "shared_urls": n,
          "same_cluster": any(a in [c["primary_query"], *c["secondary_queries"]] and
                              b in [c["primary_query"], *c["secondary_queries"]]
                              for c in clusters)}
         for (a, b), n in pairs.items() if threshold - 1 <= n <= threshold],
        key=lambda d: -d["shared_urls"])

    singletons = [c["primary_query"] for c in clusters if c["size"] == 1]
    return {
        "threshold": threshold,
        "queries_in": len(queries),
        "queries_clustered": len(usable),
        "queries_dropped_no_serp": dropped,
        "cluster_count": len(clusters),
        "singleton_count": len(singletons),
        "clusters": sorted(clusters, key=lambda c: -c["size"]),
        "borderline_pairs": borderline[:40],
        "review_note": (
            f"{len(borderline)} borderline pair(s) sit within one URL of the threshold. "
            "Those are the judgment calls - read them before accepting the grouping. "
            f"{len(singletons)} singleton(s) may be genuinely distinct intents or may just "
            "be under-collected."),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Cluster keywords by SERP overlap.")
    ap.add_argument("--file", required=True, help="text file, one query per line")
    ap.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD,
                    help=f"shared top-10 URLs required to merge (default {DEFAULT_THRESHOLD})")
    ap.add_argument("--top-n", type=int, default=10)
    ap.add_argument("--gl", default="us"); ap.add_argument("--hl", default="en")
    ap.add_argument("--out", help="write JSON here")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()

    queries = [l.strip() for l in Path(args.file).read_text(encoding="utf-8").splitlines() if l.strip()]
    serps = serp.fetch_many(queries, gl=args.gl, hl=args.hl)
    result = build(queries, serps, threshold=args.threshold, top_n=args.top_n)

    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
        print(f"{result['cluster_count']} clusters from {result['queries_clustered']} queries "
              f"-> {args.out}")
    else:
        print(payload)
    print(f"\n{serp.cost_report()}", file=sys.stderr)
    return 0


def _selftest() -> int:
    """Fixture-based: no network, checks the two failures that matter - that genuinely
    overlapping queries merge, and that single-linkage chaining does NOT happen."""
    fixture = {
        # A and B share 5 URLs -> one cluster.
        "seo audit":       {"organic": [{"link": f"https://x{i}.com/a"} for i in range(10)]},
        "seo site audit":  {"organic": [{"link": f"https://x{i}.com/a"} for i in range(5)] +
                                       [{"link": f"https://y{i}.com/b"} for i in range(5)]},
        # C shares 3 with B but 0 with A. Single-linkage would wrongly chain C onto A.
        "seo audit tool":  {"organic": [{"link": f"https://y{i}.com/b"} for i in range(3)] +
                                       [{"link": f"https://z{i}.com/c"} for i in range(7)]},
        # D shares nothing -> its own cluster.
        "plumber near me": {"organic": [{"link": f"https://p{i}.com/d"} for i in range(10)]},
    }
    qs = list(fixture)
    res = build(qs, fixture, threshold=3)
    ok = True

    def cluster_of(q):
        for c in res["clusters"]:
            if q in [c["primary_query"], *c["secondary_queries"]]:
                return c["primary_query"]
        return None

    print("1. overlapping queries merge...")
    if cluster_of("seo audit") == cluster_of("seo site audit"):
        print("   PASS: 'seo audit' + 'seo site audit' share 5 URLs -> same cluster")
    else:
        print("   FAIL: they should be one cluster"); ok = False

    print("2. no single-linkage chaining...")
    if cluster_of("seo audit tool") != cluster_of("seo audit"):
        print("   PASS: 'seo audit tool' shares 0 URLs with 'seo audit', kept separate")
    else:
        print("   FAIL: chained through the middle query - hard clustering is broken"); ok = False

    print("3. unrelated query isolated...")
    if res["clusters"] and cluster_of("plumber near me") == "plumber near me":
        print("   PASS: 'plumber near me' is its own cluster")
    else:
        print("   FAIL: unrelated query absorbed"); ok = False

    print("4. every query assigned exactly once...")
    seen = [q for c in res["clusters"] for q in [c["primary_query"], *c["secondary_queries"]]]
    if sorted(seen) == sorted(qs):
        print(f"   PASS: {len(seen)} queries across {res['cluster_count']} clusters, no dupes")
    else:
        print(f"   FAIL: assignment mismatch {sorted(seen)} vs {sorted(qs)}"); ok = False

    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

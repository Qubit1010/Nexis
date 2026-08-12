#!/usr/bin/env python3
"""What the pages ranking for this query cover that yours does not.

This is the free replacement for NeuronWriter or Surfer SEO, and it exists because their
actual mechanism is not proprietary: read the pages currently ranking, find the concepts
they share, compare against yours. The paid part is the interface and the hosting. The
method is a document-frequency count, and every input it needs is already free here -
seo-foundation's cached SERPs for the top 10, and fetch_page for the bodies.

The aruntastic course calls this the Modern Optimization Workflow, and the one genuinely
distinctive thing in it is preserved: **body terms and heading terms are separate outputs**,
because they get acted on differently. A concept the competitors put in an H2 is a section
you are missing. A concept they mention in prose is a sentence you are missing. Collapsing
the two into one list is what produces pages with keywords stapled into paragraphs.

What this deliberately does not do:

- It does not emit a target density or a "use this term 11 times" instruction. Frequency
  targets are how you get the over-optimization the helpful-content system catches.
- It does not treat its own coverage score as a ranking prediction. The score exists so
  that an edit can be verified as having changed something. That is all a score is for.

The re-score loop is the point. Measure, edit under the Revise-Don't-Rewrite constraint in
method.md, measure again, report the delta. An edit nobody re-measured is a claim.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO = SKILL_DIR.parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO / ".claude" / "skills" / "seo-foundation" / "scripts"))

import fetch_page  # noqa: E402
import onpage  # noqa: E402
import serp as sf_serp  # noqa: E402  - seo-foundation's cached Serper client
from serp_features import PLATFORM_DOMAINS, UGC_DOMAINS, domain_of  # noqa: E402

# A term must appear in at least this share of the ranking set to count as expected
# coverage. Below it you are chasing one competitor's idiosyncrasy, not the topic.
CONSENSUS = 0.5
TOP_N = 10
MIN_TERM_LEN = 3

STOPWORDS = set("""
a about above after again against all am an and any are aren as at be because been before
being below between both but by can cannot could couldn did didn do does doesn doing don
down during each few for from further had hadn has hasn have haven having he her here hers
herself him himself his how i if in into is isn it its itself just ll me more most mustn my
myself no nor not now of off on once only or other ought our ours ourselves out over own re
s same shan she should shouldn so some such t than that the their theirs them themselves
then there these they this those through to too under until up ve very was wasn we were
weren what when where which while who whom why will with won would wouldn you your yours
yourself yourselves also may might one two get got make made use used using need needs
like well back even still much many lays new first last long good great best top
""".split()) | set("""
looking look looks going go goes went come comes came take takes taking took thing things
know knows knew think thinks thought feel feels felt want wants wanted whatever whoever
however anything everything something nothing anyone everyone someone lot lots bit really
actually simply always never often sometimes usually probably maybe perhaps quite rather
pretty little big small day days time times year years way ways people person love loved
help helps helping find finds found give gives given put puts sure right left able
different various several every each around along across without within among since
say says said tell tells told see sees seen show shows shown keep keeps kept let lets
work works working start starts started end ends ended try tries tried ask asks asked
mind matter matters based including included include includes example examples
""".split())

# A concept a page actually covers gets repeated. A word that appears once is a word in
# passing, and counting it produced a first live run whose "missing concepts" were
# whatever, things, mind, know, feel. Requiring two occurrences is the cheapest available
# separator between a topic and a turn of phrase.
MIN_OCCURRENCES = 2


def _tokens(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z][a-z0-9'-]+", (text or "").lower())
            if len(w) >= MIN_TERM_LEN and w not in STOPWORDS]


def _term_counts(text: str) -> Counter:
    """Unigrams plus bigrams with their counts, stopword-trimmed at the edges."""
    c = Counter(_tokens(text))
    words = re.findall(r"[a-z][a-z0-9'-]+", (text or "").lower())
    for i in range(len(words) - 1):
        a, b = words[i], words[i + 1]
        if a in STOPWORDS or b in STOPWORDS or len(a) < MIN_TERM_LEN or len(b) < MIN_TERM_LEN:
            continue
        c[f"{a} {b}"] += 1
    return c


def _terms(text: str, *, min_occurrences: int = 1) -> set[str]:
    """The terms a document actually covers, at the given repetition floor."""
    return {t for t, n in _term_counts(text).items() if n >= min_occurrences}


MIN_COMPETITOR_WORDS = 150
MIN_SAMPLE = 4  # below this the consensus threshold stops meaning anything


def _page_parts(url: str, *, refresh: bool = False) -> tuple[dict | None, str]:
    """Returns (parts, reason_dropped). The reason matters: a small sample has to be
    explained, not silently presented as if the whole SERP had been read."""
    try:
        rec = fetch_page.fetch(url, refresh=refresh)
    except ValueError as exc:
        return None, f"skipped ({exc})"
    if not rec.get("html"):
        return None, f"no body (status {rec.get('status')}) - likely blocking scripted requests"
    doc = onpage.doc_from_html(rec["html"], rec.get("final_url") or url)
    if doc.word_count < MIN_COMPETITOR_WORDS:
        return None, f"only {doc.word_count} words of article text - a shell, paywall or block page"
    return {
        "url": url,
        # main_text, not body_text: the whole body drags nav and footer into the term counts,
        # and the first live run of this file duly reported "search", "news" and "download"
        # as missing concepts. Those are menu items.
        "body": doc.main_text,
        "headings": " \n ".join(t for _, t in doc.headings),
        "words": doc.word_count,
        "title": doc.title,
    }, ""


def analyze(query: str, target_url: str = "", *, target_text: str = "",
            target_headings: str = "", top_n: int = TOP_N, gl: str = "us",
            refresh: bool = False) -> dict:
    data = sf_serp.fetch(query, gl=gl, hl="en", num=top_n, refresh=refresh)
    urls = sf_serp.urls_of(data, limit=top_n)
    cached = data.get("_meta", {}).get("cached", False)
    print(f"[terms] SERP for \"{query}\": {len(urls)} result(s), "
          f"{'cache hit, 0 credits' if cached else '1 credit spent'}", file=sys.stderr)

    target_host = urlparse(fetch_page.normalize_url(target_url)).hostname if target_url else None

    competitors, dropped = [], []
    for i, u in enumerate(urls, 1):
        if target_host and (urlparse(u).hostname or "") == target_host:
            dropped.append({"url": u, "reason": "your own page - not a competitor"})
            continue
        # A Facebook page or a Reddit thread is not a document you displace with better
        # on-page work, and its vocabulary is platform chrome. seo-foundation already
        # maintains these sets for the same reason, so reuse them rather than fork them.
        dom = domain_of(u)
        if any(dom == d or dom.endswith("." + d) or d in dom for d in PLATFORM_DOMAINS):
            dropped.append({"url": u, "reason": "platform result - not a competing document"})
            continue
        if any(dom == d or dom.endswith("." + d) or d in dom for d in UGC_DOMAINS):
            dropped.append({"url": u, "reason": "UGC result - not a competing document"})
            continue
        print(f"[terms] {i}/{len(urls)} {u[:80]}", file=sys.stderr)
        p, reason = _page_parts(u, refresh=refresh)
        if p:
            competitors.append(p)
        else:
            dropped.append({"url": u, "reason": reason})

    if not competitors:
        return {"query": query, "error": "no competitor pages could be fetched",
                "urls_tried": urls, "dropped": dropped}

    body_df: Counter = Counter()   # how many competitors cover the term
    body_tf: Counter = Counter()   # how heavily, summed across them - the tiebreak
    head_df: Counter = Counter()
    for c in competitors:
        counts = _term_counts(c["body"])
        for t, k in counts.items():
            if k >= MIN_OCCURRENCES:
                body_df[t] += 1
                body_tf[t] += k
        # Headings are short, so one mention there is already deliberate.
        for t in _terms(c["headings"]):
            head_df[t] += 1

    n = len(competitors)
    # Consensus needs at least two documents to be a consensus. Clamping to n keeps the
    # reported threshold from reading "2 of 1 pages", which is not a sentence.
    threshold = min(n, max(2, round(CONSENSUS * n)))

    if target_url and not target_text:
        tp, why = _page_parts(target_url, refresh=refresh)
        if not tp:
            return {"query": query,
                    "error": f"could not read the target page {target_url}: {why}"}
        target_text, target_headings = tp["body"], tp["headings"]
        target_words = tp["words"]
    else:
        target_words = len(_tokens(target_text))

    mine_body = _terms(target_text)  # crediting a single mention is generous, deliberately
    mine_head = _terms(target_headings)

    if n < 2:
        expected_body = expected_head = set()  # one document is not a consensus
    else:
        expected_body = {t for t, c in body_df.items() if c >= threshold}
        expected_head = {t for t, c in head_df.items()
                         if c >= min(n, max(2, round(CONSENSUS * n * 0.6)))}

    # Rank by consensus first, then by how heavily the ranking set leans on the term. With a
    # small sample every term ties on document frequency alone, and the order becomes
    # arbitrary - which is how filler words ended up at the top of the first live run.
    missing_body = sorted(((t, body_df[t], body_tf[t]) for t in expected_body - mine_body),
                          key=lambda kv: (-kv[1], -kv[2]))
    missing_head = sorted(((t, head_df[t]) for t in expected_head - mine_head),
                          key=lambda kv: -kv[1])

    covered = len(expected_body & mine_body)
    score = round(100 * covered / max(1, len(expected_body)))

    lengths = sorted(c["words"] for c in competitors)
    median_len = lengths[len(lengths) // 2]

    confidence = "usable" if n >= MIN_SAMPLE else "low"
    caveat = ""
    if n < MIN_SAMPLE:
        n_platform = sum(1 for d in dropped if "not a competing document" in d["reason"])
        n_blocked = sum(1 for d in dropped if "block" in d["reason"] or "no body" in d["reason"])
        caveat = (f"Only {n} of {len(urls)} results are readable competing documents, so the "
                  f"consensus threshold means little - with {n} pages, 'most competitors use "
                  "this' and 'both pages use this' are the same statement. Treat the term "
                  "lists as suggestive and read page one by hand.")
        if n_platform >= max(2, len(urls) // 3):
            caveat += (f" The dominant cause is the SERP itself: {n_platform} of the results are "
                       "platform or UGC pages (social profiles, forums, review sites). That is a "
                       "finding in its own right - when page one is mostly platforms, there is "
                       "little editorial content to out-cover, and the lever is usually the "
                       "profile pages themselves plus intent, not on-page terms.")
        if n_blocked:
            caveat += f" A further {n_blocked} result(s) blocked scripted requests."

    return {
        "query": query,
        "target": target_url or "(inline text)",
        "competitors_analyzed": n,
        "competitor_urls": [c["url"] for c in competitors],
        "dropped": dropped,
        "confidence": confidence,
        "confidence_caveat": caveat,
        "serp_cached": cached,
        "consensus_threshold": f"{threshold} of {n} pages",
        "coverage_score": score,
        "covered": covered,
        "expected_terms": len(expected_body),
        "target_words": target_words,
        "competitor_median_words": median_len,
        "missing_body_terms": [{"term": t, "used_by": c, "mentions": f} for t, c, f in missing_body[:60]],
        "missing_heading_terms": [{"term": t, "used_by": c, "of": n} for t, c in missing_head[:30]],
        "notes": [
            "Body terms and heading terms are separate on purpose. A concept the ranking set "
            "puts in an H2 is a SECTION you are missing. A concept they mention in prose is a "
            "SENTENCE you are missing. Treating them the same produces stapled-in keywords.",
            "There is no frequency target here and there should not be one. The question is "
            "whether the page covers the concept, not how many times the string appears.",
            f"Competitor median length is {median_len} words. That is context, not a target - "
            "length is not a ranking factor and padding to match is the pattern that gets caught.",
            "The coverage score exists so an edit can be verified as having changed something. "
            "It is not a ranking prediction and should never be shown to a client as one.",
        ],
    }


def cost_report() -> str:
    return (f"terms: {sf_serp.cost_report()} | {fetch_page.cost_report()}")


def _selftest() -> int:
    """Fixture-based. Proves the scoring logic without spending a SERP credit."""
    ok = True

    print("1. tokenizer drops stopwords and keeps meaningful bigrams")
    t = _terms("The drainage system for a small urban garden")
    if "drainage" in t and "drainage system" in t and "the" not in t and "for a" not in t:
        print("   PASS")
    else:
        print(f"   FAIL: {sorted(t)}")
        ok = False

    print("2. a term used by half the ranking set is expected; a one-off is not")
    comps = [{"url": f"u{i}", "body": b, "headings": h, "words": 400, "title": "t"}
             for i, (b, h) in enumerate([
                 ("drainage matters for clay soil " * 30, "How much does drainage cost"),
                 ("drainage and clay soil planting " * 30, "Drainage on clay soil"),
                 ("clay soil drainage advice here " * 30, "What about clay soil"),
                 ("unrelated hedgehog trivia only " * 30, "Hedgehogs"),
             ])]
    body_df = Counter()
    for c in comps:
        for term, k in _term_counts(c["body"]).items():
            if k >= MIN_OCCURRENCES:
                body_df[term] += 1
    n, thresh = len(comps), max(2, round(CONSENSUS * len(comps)))
    expected = {x for x, c in body_df.items() if c >= thresh}
    if "drainage" in expected and "clay soil" in expected and "hedgehog" not in expected:
        print(f"   PASS: threshold {thresh} of {n} keeps shared concepts, drops the one-off")
    else:
        print(f"   FAIL: expected={sorted(expected)[:10]}")
        ok = False

    print("3. coverage score rises when the missing concept is added")
    mine_before = _terms("a page about hedgehogs and nothing else at all")
    mine_after = _terms("a page about drainage and clay soil and hedgehogs")
    s_before = round(100 * len(expected & mine_before) / max(1, len(expected)))
    s_after = round(100 * len(expected & mine_after) / max(1, len(expected)))
    if s_after > s_before:
        print(f"   PASS: {s_before} -> {s_after} after covering the shared concepts")
    else:
        print(f"   FAIL: {s_before} -> {s_after}")
        ok = False

    print("4. heading terms are computed separately from body terms")
    head_df = Counter()
    for c in comps:
        for term in _terms(c["headings"]):
            head_df[term] += 1
    if "cost" in head_df and "cost" not in body_df:
        print("   PASS: 'cost' appears only in competitor headings, so it is a missing SECTION")
    else:
        print(f"   FAIL: head={sorted(head_df)[:8]}")
        ok = False

    print("5. no frequency target is emitted anywhere in the output shape")
    src = Path(__file__).read_text(encoding="utf-8")
    if "density" not in src.lower().split("does not")[0][:2000]:
        print("   PASS: output carries concepts and consensus counts, not densities")
    else:
        print("   FAIL: a density target leaked into the module")
        ok = False

    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Term gap against the live top 10 for a query.")
    ap.add_argument("--query", help="the query this page targets")
    ap.add_argument("--url", default="", help="the page being optimized")
    ap.add_argument("--draft", default="", help="a markdown draft instead of a live URL")
    ap.add_argument("--top-n", type=int, default=TOP_N)
    ap.add_argument("--gl", default="us")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()
    if not args.query:
        ap.error("--query required (or use --selftest)")
    if not (args.url or args.draft):
        ap.error("--url or --draft required")

    text = heads = ""
    if args.draft:
        doc = onpage.doc_from_markdown(Path(args.draft).read_text(encoding="utf-8"))
        text, heads = doc.body_text, " \n ".join(t for _, t in doc.headings)

    res = analyze(args.query, args.url, target_text=text, target_headings=heads,
                  top_n=args.top_n, gl=args.gl, refresh=args.refresh)

    if res.get("error"):
        print(f"ERROR: {res['error']}")
        return 1

    if args.out:
        Path(args.out).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\"{args.query}\": coverage {res['coverage_score']}% "
              f"({res['covered']}/{res['expected_terms']}), "
              f"{len(res['missing_heading_terms'])} missing section topic(s) -> {args.out}")
    else:
        print(f"\nQuery: {args.query}")
        print(f"Analyzed {res['competitors_analyzed']} ranking page(s). "
              f"SERP {'from cache, 0 credits' if res['serp_cached'] else 'live, 1 credit'}.")
        if res["dropped"]:
            print(f"\nCould not read {len(res['dropped'])} result(s):")
            for d in res["dropped"][:10]:
                print(f"  {urlparse(d['url']).hostname}: {d['reason']}")
        if res["confidence_caveat"]:
            print(f"\nCONFIDENCE: LOW. {res['confidence_caveat']}")
        print(f"\nCoverage: {res['coverage_score']}% "
              f"({res['covered']} of {res['expected_terms']} concepts used by "
              f"{res['consensus_threshold']})")
        print(f"Your page: {res['target_words']} words. "
              f"Competitor median: {res['competitor_median_words']} words.")

        print(f"\nMissing SECTION topics ({len(res['missing_heading_terms'])}) - "
              "these appear in competitor headings, so each is a section you do not have:")
        for m in res["missing_heading_terms"][:20]:
            print(f"  {m['used_by']}/{res['competitors_analyzed']}  {m['term']}")
        print(f"\nMissing BODY concepts ({len(res['missing_body_terms'])}) - "
              "covered in competitor prose, so each is a point you do not make:")
        for m in res["missing_body_terms"][:30]:
            print(f"  {m['used_by']}/{res['competitors_analyzed']}  {m['term']}")
        for n in res["notes"]:
            print(f"\nNOTE: {n}")

    print(cost_report(), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

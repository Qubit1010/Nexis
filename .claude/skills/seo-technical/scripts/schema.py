#!/usr/bin/env python3
"""Structured data checks for course/30, run against the same crawl graph.

Separate from technical.py for one reason: schema is the area where the gap between vendor
marketing and evidence is widest in all of SEO, and it needs its own voice rather than
another six rows in a registry of sixty.

What the corpus actually establishes, and what this script therefore refuses to say:

  Google's position is that structured data is NOT a direct ranking factor, and their May
  2026 AI-search guidance says it is not required to appear in AI Overviews `[confirmed]`.
  Vendors selling schema tools report 71% of ChatGPT-cited pages carrying it and up to 3.2x
  more citations `[practitioner, correlational, self-interested]`. Ahrefs tested 1,885 pages
  and SearchAtlas tested coverage against citation rate; both were designed to detect
  causation and both found none `[practitioner, causal design]`.

  So this script never reports schema as a ranking or citation opportunity. It reports two
  things: rich-result eligibility, and entity clarity - the `@id` graph that course/40
  builds on. Anything else would be repeating a tool company's brochure.

The deprecations get the same treatment. FAQPage lost its Google rich result on 7 May 2026
and HowTo has been effectively dead since 2023, but both are still consumed by ChatGPT,
Perplexity and Bing Copilot. So a page carrying them is `review` with the nuance attached,
never `fail` - "delete your FAQ markup" is the wrong reaction and this script will not
produce it.

No HTTP requests. crawl.py already parsed every JSON-LD block, including the ones that
failed to parse, which are recorded rather than dropped.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import crawl  # noqa: E402
from technical import _ev, _live, _row, _verdict  # noqa: E402

# The roughly 14 types Google actively renders an enhancement for, plus the four other
# active ones. course/30 [practitioner]. Schema.org has 800+ classes; this is the set that
# produces anything visible.
RICH_RESULT_TYPES = {
    "Article", "NewsArticle", "BlogPosting", "BreadcrumbList", "Product", "ProductGroup",
    "Recipe", "Event", "LocalBusiness", "JobPosting", "VideoObject", "Organization",
    "SpeakableSpecification", "MerchantReturnPolicy", "OfferShippingDetails",
    "MemberProgram", "ItemList", "ProfilePage", "DiscussionForumPosting", "QAPage",
    "Dataset", "Course", "SoftwareApplication", "Book", "Movie", "Review", "Person",
}

# Retired, with why and what to do. The value is never "remove it" unless it is actually
# harmful - see the FAQPage and HowTo note in the module docstring.
DEPRECATED = {
    "FAQPage": ("Google rich result sunset entirely 7 May 2026, including the former health "
                "and government exceptions. Still consumed by ChatGPT, Perplexity and Bing "
                "Copilot - leave the markup, stop expecting Google output."),
    "HowTo": ("Effectively dead on desktop since 2023, near-zero payoff. Still read by "
              "non-Google engines - same treatment as FAQPage."),
    "ClaimReview": ("Restricted to verified fact-checkers in the June 2025 sweep. Produces "
                    "nothing for anyone else."),
    "EstimatedSalary": "Phased out in the June 2025 sweep.",
    "LearningVideo": "Phased out in the June 2025 sweep.",
    "SpecialAnnouncement": "Phased out in the June 2025 sweep.",
    "VehicleListing": "Phased out in the June 2025 sweep.",
    "BookAction": "Book Actions phased out in the June 2025 sweep.",
}

# WebSite + potentialAction/SearchAction was the sitelinks searchbox, sunset late 2024.
SEARCHBOX_SUNSET = "Sitelinks Searchbox sunset late 2024. The markup now does nothing."

ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2})?(\.\d+)?(Z|[+-]\d{2}:?\d{2})?)?$")
ISO_DURATION = re.compile(r"^P(?!$)(\d+Y)?(\d+M)?(\d+W)?(\d+D)?(T(?!$)(\d+H)?(\d+M)?(\d+(\.\d+)?S)?)?$")
DATE_FIELDS = ("datePublished", "dateModified", "dateCreated", "startDate", "endDate",
               "uploadDate", "validFrom", "priceValidUntil", "expires")
DURATION_FIELDS = ("cookTime", "prepTime", "totalTime", "duration", "timeRequired")
URL_FIELDS = ("url", "@id", "logo", "image", "contentUrl", "thumbnailUrl", "sameAs")

BREADCRUMB_COVERAGE = 0.8   # course/30: "sitewide"


# --------------------------------------------------------------------------- walking

def walk(blocks) -> list[dict]:
    """Every dict node in a page's JSON-LD, flattened, including @graph members.

    Schema is nested by design - an Article carries a Person as its author and an
    Organization as its publisher. A check that only looked at top-level @type would miss
    most of the markup on any correctly built page.
    """
    out, stack = [], list(blocks or [])
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            out.append(node)
            stack += [v for v in node.values() if isinstance(v, (dict, list))]
        elif isinstance(node, list):
            stack += node
    return out


def types_of(node: dict) -> list[str]:
    t = node.get("@type")
    if isinstance(t, str):
        return [t.rsplit("/", 1)[-1]]
    if isinstance(t, list):
        return [str(x).rsplit("/", 1)[-1] for x in t]
    return []


def _page_types(p: dict) -> set[str]:
    return {t for n in walk(p.get("jsonld")) for t in types_of(n)}


def _broken(p: dict) -> list[dict]:
    return [b for b in (p.get("jsonld") or []) if isinstance(b, dict) and "__parse_error__" in b]


def _as_list(v) -> list:
    return v if isinstance(v, list) else [] if v is None else [v]


# --------------------------------------------------------------------------- checks

def check_schema(g: dict) -> list[dict]:
    A = "Structured data"
    pages = _live(g.get("pages") or {})
    origin = (g.get("origin") or "").rstrip("/")
    home = crawl.normalize_url(origin + "/")
    out: list[dict] = []
    if not pages:
        return [_row("schema.present", A, "no HTML pages in the graph", "n/a", "unknown",
                     "course/30", "Nothing to check. Crawl the site first.")]

    # --- presence and format
    with_jsonld = {u: p for u, p in pages.items() if p.get("jsonld")}
    microdata_only = [u for u, p in pages.items()
                      if not p.get("jsonld") and p.get("microdata_types")]
    none_at_all = [u for u, p in pages.items()
                   if not p.get("jsonld") and not p.get("microdata_types")]

    out.append(_row("schema.present", A,
                    f"{len(with_jsonld)} of {len(pages)} page(s) carry JSON-LD",
                    "structured data on pages that qualify for a rich result",
                    "review" if none_at_all else "pass", "course/30", _ev(none_at_all) or
                    "Not every page needs markup. Missing schema is only a finding on a page "
                    "with a type that earns something."))

    out.append(_row("schema.jsonld_format", A,
                    f"{len(microdata_only)} page(s) use microdata or RDFa with no JSON-LD",
                    "JSON-LD, Google's recommended format",
                    "review" if microdata_only else "pass", "course/30 [confirmed]",
                    _ev(microdata_only) or "JSON-LD keeps markup separate from content and is "
                                           "easiest to maintain."))

    broken = [f"{u}: {b['__parse_error__']}" for u, p in pages.items() for b in _broken(p)]
    out.append(_row("schema.parses", A, f"{len(broken)} block(s) are not valid JSON",
                    "every JSON-LD block parses", _verdict(broken), "course/30", _ev(broken) or
                    "A block that does not parse is invisible to every consumer. Usually a "
                    "template variable that rendered empty or an unescaped quote."))

    all_types = Counter(t for p in pages.values() for t in _page_types(p))

    # --- Organization: the entity anchor
    home_page = pages.get(home) or pages.get(crawl.normalize_url(origin))
    org_nodes = [n for p in pages.values() for n in walk(p.get("jsonld"))
                 if {"Organization", "LocalBusiness"} & set(types_of(n))
                 or any(t.endswith("Business") or t.endswith("Store") for t in types_of(n))]
    if home_page is None:
        out.append(_row("schema.organization", A, "homepage not in the crawl",
                        "Organization on the homepage", "unknown", "course/30",
                        "Crawl the homepage to check this."))
    else:
        home_org = [n for n in walk(home_page.get("jsonld"))
                    if {"Organization", "LocalBusiness"} & set(types_of(n))
                    or any(t.endswith("Business") for t in types_of(n))]
        out.append(_row("schema.organization", A,
                        f"{len(home_org)} Organization/LocalBusiness node(s) on the homepage",
                        "one, as the entity anchor", _verdict([] if home_org else ["missing"]),
                        "course/30 -> course/40",
                        "This is the highest-value, lowest-effort markup on any business site "
                        "and it is what entity work in course/40 builds on."
                        if not home_org else _ev(sorted({t for n in home_org for t in types_of(n)}))))

    same_as = sorted({s for n in org_nodes for s in _as_list(n.get("sameAs")) if isinstance(s, str)})
    out.append(_row("schema.organization_sameas", A, f"{len(same_as)} sameAs profile(s)",
                    "sameAs pointing at the real profiles",
                    _verdict([] if same_as else ["none"]), "course/30 -> course/40",
                    _ev(same_as) or "sameAs is what connects the site to LinkedIn, Crunchbase "
                                    "and the rest, and it is how an engine resolves which "
                                    "'Acme' this is."))

    # --- Breadcrumbs: sitewide, and widely skipped
    crumbed = [u for u, p in pages.items() if "BreadcrumbList" in _page_types(p)]
    ratio = len(crumbed) / len(pages)
    out.append(_row("schema.breadcrumbs", A, f"{len(crumbed)} of {len(pages)} page(s) ({ratio:.0%})",
                    f"sitewide (>{BREADCRUMB_COVERAGE:.0%})",
                    "pass" if ratio >= BREADCRUMB_COVERAGE else "fail", "course/30 [practitioner]",
                    "Machine-readable hierarchy, independent of the prose."
                    if ratio >= BREADCRUMB_COVERAGE
                    else _ev([u for u in pages if u not in crumbed])))

    # --- Article completeness
    article_pages = {u: p for u, p in pages.items()
                     if {"Article", "BlogPosting", "NewsArticle"} & _page_types(p)}
    missing_fields = []
    for u, p in article_pages.items():
        for n in walk(p.get("jsonld")):
            if not {"Article", "BlogPosting", "NewsArticle"} & set(types_of(n)):
                continue
            gaps = [f for f in ("author", "dateModified", "headline") if not n.get(f)]
            if gaps:
                missing_fields.append(f"{u}: missing {', '.join(gaps)}")
    out.append(_row("schema.article_fields", A,
                    f"{len(missing_fields)} of {len(article_pages)} Article node(s) incomplete",
                    "author, headline and an accurate dateModified",
                    _verdict(missing_fields) if article_pages else "pass", "course/30",
                    _ev(missing_fields) or
                    ("No Article markup found." if not article_pages else
                     "dateModified is a real recency signal for Perplexity and AI Overviews. "
                     "Faking it is the same fake-freshness problem as course/19.")))

    # --- Format rules
    bad_dates, bad_urls, bad_durations = [], [], []
    for u, p in pages.items():
        for n in walk(p.get("jsonld")):
            for f in DATE_FIELDS:
                v = n.get(f)
                if isinstance(v, str) and v and not ISO_DATE.match(v.strip()):
                    bad_dates.append(f"{u}: {f}={v!r}")
            for f in DURATION_FIELDS:
                v = n.get(f)
                if isinstance(v, str) and v and not ISO_DURATION.match(v.strip()):
                    bad_durations.append(f"{u}: {f}={v!r}")
            for f in URL_FIELDS:
                for v in _as_list(n.get(f)):
                    if isinstance(v, str) and v and not v.lower().startswith(("http", "urn:", "#")):
                        bad_urls.append(f"{u}: {f}={v!r}")

    out.append(_row("schema.iso_8601", A,
                    f"{len(bad_dates)} date(s) and {len(bad_durations)} duration(s) malformed",
                    "ISO 8601 - 2026-04-18, PT30M", _verdict(bad_dates + bad_durations),
                    "course/30", _ev(bad_dates + bad_durations) or
                    "Named in the course as the most common validation error."))

    out.append(_row("schema.absolute_urls", A, f"{len(bad_urls)} relative URL value(s)",
                    "absolute URLs, always", _verdict(bad_urls), "course/30", _ev(bad_urls)))

    # --- The @id graph: the part that actually matters for entity work
    ided = [n for p in pages.values() for n in walk(p.get("jsonld")) if n.get("@id")]
    entity_nodes = [n for p in pages.values() for n in walk(p.get("jsonld"))
                    if {"Organization", "Person", "LocalBusiness", "Article", "BlogPosting",
                        "WebSite", "WebPage"} & set(types_of(n))]
    out.append(_row("schema.stable_ids", A,
                    f"{len(ided)} node(s) carry @id, out of {len(entity_nodes)} entity node(s)",
                    "stable @id values connecting the entities into one graph",
                    "review" if len(ided) < len(entity_nodes) else "pass", "course/30",
                    "Without @id, each block is an isolated island and nothing links the "
                    "Organization to the Article to the author. This is the part of schema "
                    "that genuinely matters, and it is the part plugins skip."))

    # --- Deprecations, with the nuance
    found_dead = {t: DEPRECATED[t] for t in DEPRECATED if all_types.get(t)}
    searchbox = [u for u, p in pages.items()
                 for n in walk(p.get("jsonld"))
                 if "WebSite" in types_of(n) and n.get("potentialAction")]
    if searchbox:
        found_dead["WebSite/SearchAction"] = SEARCHBOX_SUNSET
    retired_ev = _ev([f"{t} ({all_types.get(t) or len(searchbox)} page(s)): {why}"
                      for t, why in found_dead.items()], 8) if found_dead else \
        "Nothing retired found."
    out.append(_row("schema.retired_types", A, f"{len(found_dead)} retired type(s) in use",
                    "no expectations resting on a retired rich result",
                    "review" if found_dead else "pass", "course/30 [practitioner]", retired_ev))

    # --- Eligibility, stated as eligibility and nothing more
    earning = {t: c for t, c in all_types.items() if t in RICH_RESULT_TYPES}
    inert = {t: c for t, c in all_types.items()
             if t not in RICH_RESULT_TYPES and t not in DEPRECATED}
    out.append(_row("schema.rich_result_eligible", A,
                    f"{len(earning)} type(s) Google renders an enhancement for",
                    "the types that earn something, and no more",
                    "pass" if earning else "review", "course/30 [practitioner]",
                    _ev([f"{t}: {c} page(s)" for t, c in sorted(earning.items())], 10) or
                    "Schema.org has 800+ classes and Google renders roughly 30. None of the "
                    "markup here is in that set."))

    out.append(_row("schema.no_ranking_claim", A,
                    f"{len(inert)} type(s) present that produce no rich result",
                    "implemented for eligibility and entity clarity, never for rankings",
                    "review" if len(inert) > 6 else "pass", "course/30 [confirmed]",
                    _ev([f"{t}: {c}" for t, c in sorted(inert.items())], 10) +
                    "\n\nThese are not errors - supporting types like ImageObject and "
                    "PostalAddress belong inside other nodes. It is a prompt to check nothing "
                    "was added on the belief that more markup ranks better. Google has "
                    "confirmed structured data is not a direct ranking factor, and the two "
                    "causal studies that tested schema against AI citations (Ahrefs, 1,885 "
                    "pages; SearchAtlas) found no meaningful uplift."))

    # --- The spam risk, which needs eyes
    rating_pages = sorted({u for u, p in pages.items()
                           if {"AggregateRating", "Review", "Rating"} & _page_types(p)})
    out.append(_row("schema.matches_visible", A,
                    f"{len(rating_pages)} page(s) mark up a rating or review",
                    "markup matches visible content", "review" if rating_pages else "pass",
                    "course/30", _ev(rating_pages) +
                    ("\n\nMarking up a review score that is not shown on the page is a "
                     "structured data spam violation and carries manual-action risk. The page "
                     "text is not in the crawl graph, so confirm each of these by eye."
                     if rating_pages else
                     "No rating or review markup, so the highest-risk case does not apply. "
                     "Other types still need a visual check.")))

    out.append(_row("schema.validated", A, "not connected",
                    "clean in the Rich Results Test and validator.schema.org",
                    "unknown", "course/30",
                    "This script checks the rules course/30 states. It is not a schema.org "
                    "vocabulary validator and it cannot tell you whether Google will render "
                    "an enhancement - those are two different questions and you want both "
                    "answers.\n"
                    "Manual: validator.schema.org for vocabulary conformance, Google's Rich "
                    "Results Test for whether an enhancement actually renders, and Search "
                    "Console Enhancements for the template-wide picture. Valid markup on one "
                    "page means nothing if the template breaks on 400 others."))
    return out


def analyze(g: dict) -> dict:
    rows = check_schema(g)
    return {
        "origin": g.get("origin"),
        "crawled_at": g.get("crawled_at"),
        "pages_crawled": (g.get("stats") or {}).get("pages_crawled"),
        "counts": {v: sum(1 for r in rows if r["verdict"] == v)
                   for v in ("pass", "fail", "review", "unknown")},
        "checks": rows,
        "not_connected": [
            "Rich Results Test and validator.schema.org: no API. Vocabulary conformance and "
            "render eligibility are checked by hand.",
            "Search Console Enhancements: no credential, so template-wide error counts are "
            "unavailable.",
        ],
        "reading_note": (
            "Schema earns rich results and clarifies entity identity. It is not a ranking "
            "factor (Google, confirmed) and the two causal studies of schema against AI "
            "citations found no uplift. Report it as eligibility, never as a ranking or "
            "citation opportunity."),
    }


# --------------------------------------------------------------------------- selftest

def _selftest() -> int:
    ok = True
    o = "https://e.test"

    def page(url, jsonld=None, **kw):
        base = {"url": url, "status": 200, "content_type": "text/html", "jsonld": jsonld or [],
                "microdata_types": [], "final_url": url, "depth": 1}
        base.update(kw)
        return base

    g = {
        "origin": o, "crawled_at": "x", "stats": {"pages_crawled": 3},
        "pages": {
            f"{o}/": page(f"{o}/", [{"@context": "https://schema.org", "@graph": [
                {"@type": "Organization", "@id": f"{o}/#org", "name": "E",
                 "sameAs": ["https://linkedin.com/company/e"], "logo": "/logo.png"},
                {"@type": "WebSite", "url": o, "potentialAction": {"@type": "SearchAction"}}]}]),
            f"{o}/post": page(f"{o}/post", [
                {"@type": "BlogPosting", "headline": "H", "datePublished": "18/04/2026"},
                {"@type": "FAQPage", "mainEntity": []},
                {"@type": "AggregateRating", "ratingValue": 5}]),
            f"{o}/broken": page(f"{o}/broken",
                                [{"__parse_error__": "Expecting value", "__raw_head__": "{"}]),
        },
    }
    res = analyze(g)
    by = {r["check_id"]: r for r in res["checks"]}

    print("1. the broken fixture fails what it should")
    expect_fail = {
        "schema.parses": "one block is not valid JSON",
        "schema.breadcrumbs": "no BreadcrumbList anywhere",
        "schema.article_fields": "BlogPosting has no author or dateModified",
        "schema.iso_8601": "18/04/2026 is not ISO 8601",
        "schema.absolute_urls": "logo is relative",
    }
    wrong = [(c, by.get(c, {}).get("verdict")) for c in expect_fail
             if by.get(c, {}).get("verdict") != "fail"]
    print(f"   PASS: all {len(expect_fail)} fired" if not wrong else f"   FAIL: {wrong}")
    ok &= not wrong

    print("2. retired types are `review` with the nuance, never `fail`")
    r = by.get("schema.retired_types", {})
    has_nuance = "Still consumed by ChatGPT" in r.get("evidence", "")
    has_searchbox = "Searchbox" in r.get("evidence", "")
    if r.get("verdict") == "review" and has_nuance and has_searchbox:
        print("   PASS: FAQPage flagged, keep-the-markup nuance attached, searchbox caught")
    else:
        print(f"   FAIL: verdict={r.get('verdict')} nuance={has_nuance} searchbox={has_searchbox}")
        ok = False

    print("3. no check asserts a ranking or citation benefit")
    claim = re.compile(r"(improves? rank|boosts? rank|more citations|ranking factor(?! ))", re.I)
    offenders = [r["check_id"] for r in res["checks"]
                 if claim.search(f"{r['observed']} {r['threshold']} {r['evidence']}")
                 and "not a direct ranking factor" not in r["evidence"]
                 and "never for rankings" not in r["threshold"]]
    print("   PASS: no ranking claim anywhere" if not offenders else f"   FAIL: {offenders}")
    ok &= not offenders

    print("4. nested nodes are found, not just top-level @type")
    if "SearchAction" in {t for n in walk(g["pages"][f"{o}/"]["jsonld"]) for t in types_of(n)}:
        print("   PASS: a node nested two levels deep is reachable")
    else:
        print("   FAIL: walk() missed a nested node")
        ok = False

    print("5. Organization and sameAs found through @graph")
    if by["schema.organization"]["verdict"] == "pass" and \
            by["schema.organization_sameas"]["verdict"] == "pass":
        print("   PASS: entity anchor and sameAs both detected inside @graph")
    else:
        print(f"   FAIL: org={by['schema.organization']['verdict']} "
              f"sameas={by['schema.organization_sameas']['verdict']}")
        ok = False

    print("6. the rating spam risk is surfaced for human review")
    r = by.get("schema.matches_visible", {})
    if r.get("verdict") == "review" and "manual-action risk" in r.get("evidence", ""):
        print("   PASS: rating markup named as needing a visual check")
    else:
        print(f"   FAIL: {r.get('verdict')}")
        ok = False

    print("7. ISO 8601 accepts what it should")
    cases = {"2026-04-18": True, "2026-04-18T10:00:00Z": True, "2026-04-18T10:00:00+05:00": True,
             "18/04/2026": False, "2026-4-8": False, "": False}
    bad = [c for c, want in cases.items() if bool(ISO_DATE.match(c)) != want]
    dur = {"PT30M": True, "P1DT2H": True, "30 minutes": False, "P": False}
    bad += [c for c, want in dur.items() if bool(ISO_DURATION.match(c)) != want]
    print("   PASS: dates and durations both validated" if not bad else f"   FAIL: {bad}")
    ok &= not bad

    print(f"\n{res['counts']}")
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# --------------------------------------------------------------------------- cli

def main() -> int:
    ap = argparse.ArgumentParser(description="Structured data checks (course/30) over a crawl graph.")
    ap.add_argument("url", nargs="?")
    ap.add_argument("--graph", help="a graph JSON written by crawl.py --out")
    ap.add_argument("--max-pages", type=int, default=crawl.DEFAULT_MAX_PAGES)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()
    if not args.graph and not args.url:
        ap.error("url or --graph required (or use --selftest)")

    if args.graph:
        g = json.loads(Path(args.graph).read_text(encoding="utf-8"))
    else:
        cached = crawl._cache_path(crawl.origin_of(args.url)).exists() and not args.refresh
        if args.max_pages > crawl.CONFIRM_ABOVE and not args.yes and not cached:
            print(f"This would make up to {args.max_pages} requests. Re-run with --yes.",
                  file=sys.stderr)
            return 2
        g = crawl.crawl(args.url, max_pages=args.max_pages, refresh=args.refresh)

    res = analyze(g)
    if args.out:
        Path(args.out).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        print(args.out, file=sys.stderr)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0

    print(f"\n{res['origin']}  -  {res['pages_crawled']} pages")
    print("  ".join(f"{k}: {v}" for k, v in res["counts"].items()))
    for r in res["checks"]:
        if r["verdict"] == "pass":
            continue
        print(f"\n  [{r['verdict'].upper():7}] {r['check_id']}: {r['observed']}")
        print(f"            want: {r['threshold']}  ({r['source']})")
        for line in (r["evidence"] or "").splitlines()[:5]:
            print(f"            | {line}")
    print(f"\n{res['reading_note']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

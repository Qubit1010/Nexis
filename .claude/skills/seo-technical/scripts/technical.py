#!/usr/bin/env python3
"""The check registry for Tier 3 sections 21 to 25 and 31, run against one crawl graph.

Six areas, in the order course/21 fixes them, and the order is not negotiable because a
failure at a lower layer invalidates the work above it:

    1. Crawlability and robots      course/21
    2. Sitemaps and indexation      course/22
    3. Canonicals and duplicates    course/23
    4. Redirects and status codes   course/24
    5. Site architecture            course/25
    6. International and hreflang   course/31

Rendering (26), performance (27-28), mobile (29) and structured data (30) are the other
three scripts. They read the same graph.

This file makes no HTTP requests. Everything it reports comes from crawl.py's graph, which
is the whole point: one pass over the site answers every check here, and re-running an
audit after a fix costs nothing. If a check needs a fact the graph does not carry, the
answer is to add it to the crawl, not to fetch it here.

The four verdicts are seo-onpage's, deliberately, so the two skills' rows share a shape and
a Sheet schema:

    pass    - measured, clears the threshold
    fail    - measured, does not clear it
    review  - measured, but the verdict needs judgment; evidence attached
    unknown - not measurable from anything available here; reason and manual method attached

`unknown` is load-bearing in this skill more than in any other. Indexation is the subject of
half of Tier 3 and Search Console is the only thing that can report it. There is no
credential for it here, verified. Every indexation check that needs Search Console says so
and gives the manual steps, because a script that reports "indexation looks fine" from a
crawl it did itself is describing its own crawl, not Google's index.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import crawl  # noqa: E402

# Thresholds. Every one is sourced to a course section that carries its own evidence tier -
# do not edit here without editing references/checks.md, or a report will cite a number the
# reference does not hold.
SITEMAP_MAX_URLS = 50_000        # course/22 [confirmed]
SITEMAP_MAX_BYTES = 50 * 1024 * 1024   # course/22 [confirmed]
INDEXED_RATIO_HEALTHY = 0.85     # course/22 [practitioner]
SITEMAP_SPLIT_ABOVE = 500        # course/22 [practitioner] "more than a few hundred URLs"
MAX_DEPTH_COMMERCIAL = 3         # course/25 [practitioner]
DEPTH_NEGLECTED = 5              # course/25 [practitioner]
MAX_REDIRECT_HOPS = 1            # course/24: one hop, not two
ABANDON_HOPS = 5                 # course/24 [practitioner] Googlebot may abandon beyond 5
CRAWL_BUDGET_BINDS = 10_000      # course/21 [practitioner]
NAV_ITEMS_MAX = 7                # course/25 -> course/13 [practitioner] "about seven"
SITEWIDE_LINK_RATIO = 0.8        # a link on 80%+ of pages is navigation, not a body link
SOFT_404_WORDS = 50              # a 200 with less than this reads as an empty template

# ISO 639-1. Present in full because the course's rule is exact - "region alone is not
# valid" - and a shape heuristic cannot tell the language `is` from the region `IS`.
ISO_639_1 = set(
    "aa ab ae af ak am an ar as av ay az ba be bg bh bi bm bn bo br bs ca ce ch co cr cs cu "
    "cv cy da de dv dz ee el en eo es et eu fa ff fi fj fo fr fy ga gd gl gn gu gv ha he hi "
    "ho hr ht hu hy hz ia id ie ig ii ik io is it iu ja jv ka kg ki kj kk kl km kn ko kr ks "
    "ku kv kw ky la lb lg li ln lo lt lu lv mg mh mi mk ml mn mr ms mt my na nb nd ne ng nl "
    "nn no nr nv ny oc oj om or os pa pi pl ps pt qu rm rn ro ru rw sa sc sd se sg si sk sl "
    "sm sn so sq sr ss st su sv sw ta te tg th ti tk tl tn to tr ts tt tw ty ug uk ur uz ve "
    "vi vo wa wo xh yi yo za zh zu".split())

# Region codes people write that ISO 3166-1 does not have. The full 249-code list is not
# carried here; shape plus these catches the trap course/31 actually names (`en-UK`).
BAD_REGIONS = {"UK": "GB", "EL": "GR", "EN": None, "SU": None}

PAGINATION = re.compile(r"(/page/\d+|[?&](page|paged|p)=\d+)", re.I)


# --------------------------------------------------------------------------- helpers

def _row(cid, area, observed, threshold, verdict, source, evidence="") -> dict:
    return {"check_id": cid, "area": area, "observed": observed, "threshold": threshold,
            "verdict": verdict, "source": source, "evidence": evidence}


def _ev(items, n: int = 6) -> str:
    """Evidence, capped. A finding listing 300 URLs is not evidence, it is an export."""
    items = [str(i) for i in items]
    if not items:
        return ""
    head = "\n".join(items[:n])
    return head + (f"\n... and {len(items) - n} more" if len(items) > n else "")


def _verdict(bad: list, *, fail="fail", ok="pass") -> str:
    return fail if bad else ok


def _disallowed_by(url: str, patterns: list[str]) -> str | None:
    """The first robots.txt Disallow pattern matching this URL, or None.

    Supports the two wildcards Google honours: `*` for any run of characters and `$` for
    end-of-URL. Everything else is a literal prefix match, which is the actual spec.
    """
    p = urlparse(url)
    target = p.path + (f"?{p.query}" if p.query else "")
    for pat in patterns:
        if not pat:
            continue
        rx = re.escape(pat).replace(r"\*", ".*")
        rx = rx[:-2] + "$" if rx.endswith(r"\$") else rx
        try:
            if re.match(rx, target):
                return pat
        except re.error:
            continue
    return None


def _live(pages: dict) -> dict:
    """Pages that returned 200 with HTML. The population every content-level check is about."""
    return {u: p for u, p in pages.items()
            if p.get("status") == 200 and (p.get("content_type") or "").startswith("text/html")}


def _has_noindex(p: dict) -> bool:
    d = f"{p.get('meta_robots') or ''},{p.get('x_robots_tag') or ''}".lower()
    return "noindex" in d or bool(re.search(r"\bnone\b", d))


# --------------------------------------------------------------------------- 21. robots

def check_robots(g: dict) -> list[dict]:
    A = "Crawlability and robots"
    rb = g.get("robots") or {}
    pages = g.get("pages") or {}
    out: list[dict] = []
    status = rb.get("status")

    # The catastrophic one gets its own row so it can never be buried in a list of nine.
    out.append(_row(
        "robots.not_5xx", A,
        f"HTTP {status}", "must not be 5xx",
        "fail" if rb.get("is_5xx") else "pass", "course/21 [confirmed]",
        "A 5xx on robots.txt makes Googlebot stop crawling the entire site until it "
        "resolves. This is the highest-risk small file on the site." if rb.get("is_5xx")
        else "A 404 here is fine and is read as 'crawl everything'."))

    out.append(_row(
        "robots.reachable", A, f"HTTP {status}", "200, or 404",
        "pass" if status in (200, 404) else "fail", "course/21", rb.get("url", "")))

    out.append(_row(
        "robots.disallow_all", A,
        "Googlebot is blocked from /" if rb.get("disallow_all") else "Googlebot may fetch /",
        "the site must not block its own crawlers",
        "fail" if rb.get("disallow_all") else "pass", "course/21",
        "Usually a staging rule left in production." if rb.get("disallow_all")
        else "Checked against the grouped user-agent blocks, so a rule scoped to one bot "
             "is not read as a site-wide block."))

    blocked = rb.get("blocks_css_or_js") or []
    out.append(_row(
        "robots.css_js_open", A,
        f"{len(blocked)} rule(s) block CSS or JS" if blocked else "CSS and JS crawlable",
        "never block CSS or JavaScript",
        _verdict(blocked), "course/21 [practitioner]",
        _ev(blocked) or "Google needs both to render the page as a user sees it."))

    out.append(_row(
        "robots.sitemap_directive", A,
        f"{len(rb.get('sitemaps') or [])} Sitemap: line(s)", "at least one",
        "pass" if rb.get("has_sitemap_directive") else "fail", "course/21",
        _ev(rb.get("sitemaps") or [])))

    # The disallow + noindex conflict. Direction depends on whether this crawl obeyed robots.
    disallows = rb.get("disallows") or []
    skipped = g.get("skipped_by_robots") or []
    respected = (g.get("_meta") or {}).get("respected_robots", True)
    if not disallows:
        out.append(_row("robots.noindex_conflict", A, "no Disallow rules for *",
                        "never both Disallow and noindex the same URL", "pass", "course/21",
                        "The conflict cannot exist without a Disallow rule."))
    elif respected:
        out.append(_row(
            "robots.noindex_conflict", A,
            f"{len(skipped)} URL(s) hit a Disallow rule and were not fetched" if skipped else
            f"{len(disallows)} Disallow rule(s), none matched a URL this crawl reached",
            "never both Disallow and noindex the same URL", "review", "course/21 [confirmed]",
            (_ev(skipped) + "\n\n" if skipped else _ev(disallows) + "\n\n") +
            "A disallowed URL is never fetched, so a noindex on it is never read, and the URL "
            "can stay indexed as a bare link indefinitely. This crawl obeyed the disallow, so "
            "their noindex state is unknown. Confirm with: crawl.py <url> --ignore-robots "
            "--refresh, then re-run this check."))
    else:
        conflicted = [u for u, p in pages.items()
                      if _has_noindex(p) and _disallowed_by(u, disallows)]
        out.append(_row(
            "robots.noindex_conflict", A,
            f"{len(conflicted)} URL(s) are both disallowed and noindex",
            "never both Disallow and noindex the same URL",
            _verdict(conflicted), "course/21 [confirmed]",
            _ev(conflicted) or "Checked directly: this crawl ignored robots.txt."))

    declared = rb.get("ai_policy_declared") or {}
    missing = [b for b in crawl.AI_BOTS if b not in declared]
    diverges = [f"{b}: declared {declared[b]}, 2026 default {crawl.AI_BOTS[b]}"
                for b in declared if declared[b] != crawl.AI_BOTS[b]]
    out.append(_row(
        "robots.ai_policy", A,
        f"{len(declared)} of {len(crawl.AI_BOTS)} AI agents named explicitly",
        "a deliberate policy: block trainers, allow retrievers that send referrals",
        "review", "course/21 [practitioner] -> course/40",
        (_ev(diverges) + "\n" if diverges else "") +
        (f"Not named: {', '.join(missing)}\n" if missing else "") +
        "This is a business decision, not a defect. Blocking indiscriminately opts the site "
        "out of AI answers while trying to opt out of training. robots.txt is voluntary; "
        "real enforcement is WAF or server-level."))

    out.append(_row(
        "robots.no_deprecated_agents", A,
        "anthropic-ai present" if rb.get("mentions_deprecated_anthropic_ai") else "none found",
        "no deprecated agent names",
        "fail" if rb.get("mentions_deprecated_anthropic_ai") else "pass",
        "course/21 [practitioner]",
        "`anthropic-ai` is a deprecated legacy agent. Including it in a 2026 configuration "
        "produces broken instructions - the live agents are ClaudeBot and Claude-SearchBot."))

    # Crawl budget: the thing beginners worry about most and that matters least.
    known = max(len(pages), len(g.get("sitemap_urls_submitted") or []))
    capped = (g.get("stats") or {}).get("hit_cap")
    if capped:
        out.append(_row(
            "crawl.budget_binding", A, f"at least {known} pages (crawl hit its cap)",
            f"binds above ~{CRAWL_BUDGET_BINDS:,} pages", "review", "course/21 [practitioner]",
            "The crawl stopped at its cap, so the page count is a floor, not a total. Raise "
            "--max-pages or read the true count from Search Console's Pages report before "
            "concluding anything about crawl budget."))
    else:
        binding = known >= CRAWL_BUDGET_BINDS
        out.append(_row(
            "crawl.budget_binding", A, f"{known} pages",
            f"binds above ~{CRAWL_BUDGET_BINDS:,} pages",
            "review" if binding else "pass", "course/21 [practitioner]",
            "Crawl budget is a real constraint at this size; check Search Console Settings "
            "-> Crawl stats." if binding else
            "Below the threshold, so crawl budget is not this site's problem. Uncrawled "
            "pages here are an architecture, linking or quality problem instead."))
    return out


# --------------------------------------------------------------------------- 22. sitemaps

def check_sitemaps(g: dict) -> list[dict]:
    A = "Sitemaps and indexation"
    files = g.get("sitemap_files") or []
    submitted = g.get("sitemap_urls_submitted") or []
    pages = g.get("pages") or {}
    out: list[dict] = []

    out.append(_row("sitemap.found", A, f"{len(files)} sitemap file(s), {len(submitted)} URL(s)",
                    "at least one reachable sitemap",
                    _verdict([] if files else ["none"]), "course/22",
                    _ev([f["url"] for f in files])))
    if not files:
        return out

    dead = [f"{f['url']} -> HTTP {f['status']}" for f in files if f["status"] != 200]
    out.append(_row("sitemap.fetches", A, f"{len(dead)} of {len(files)} not 200", "every file 200",
                    _verdict(dead), "course/22", _ev(dead)))

    broken = [f"{f['url']}: {f['error']}" for f in files if f.get("error")]
    out.append(_row("sitemap.parses", A, f"{len(broken)} parse error(s)", "valid XML",
                    _verdict(broken), "course/22", _ev(broken)))

    over = [f"{f['url']}: {len(f['urls']):,} URLs" for f in files if len(f["urls"]) > SITEMAP_MAX_URLS]
    over += [f"{f['url']}: {f['bytes'] / 1e6:.1f}MB" for f in files if f["bytes"] > SITEMAP_MAX_BYTES]
    out.append(_row("sitemap.limits", A, f"{len(over)} file(s) over a hard limit",
                    f"{SITEMAP_MAX_URLS:,} URLs and 50MB per file",
                    _verdict(over), "course/22 [confirmed]",
                    _ev(over) or "Beyond either limit, split with a sitemap index file."))

    # The contents rules, checkable only against the URLs this crawl actually reached.
    reached = [u for u in submitted if u in pages]
    coverage = f"{len(reached)} of {len(submitted)} submitted URL(s) were crawled"

    non200 = [f"{u} -> HTTP {pages[u]['status']}" for u in reached if pages[u]["status"] != 200]
    out.append(_row("sitemap.only_200", A, f"{len(non200)} non-200 in the sitemap",
                    "only 200-status URLs", _verdict(non200), "course/22",
                    _ev(non200) or coverage))

    redirected = [f"{u} -> {pages[u]['final_url']}" for u in reached
                  if pages[u].get("redirect_chain")]
    out.append(_row("sitemap.no_redirects", A, f"{len(redirected)} redirecting URL(s)",
                    "no redirects in the sitemap", _verdict(redirected), "course/22",
                    _ev(redirected) or coverage))

    noindexed = [u for u in reached if _has_noindex(pages[u])]
    out.append(_row("sitemap.only_indexable", A, f"{len(noindexed)} noindexed URL(s)",
                    "no noindexed URLs", _verdict(noindexed), "course/22",
                    _ev(noindexed) or coverage))

    cross = [f"{u} -> canonical {pages[u]['canonical']}" for u in reached
             if pages[u].get("canonical")
             and crawl.normalize_url(pages[u]["canonical"]) != crawl.normalize_url(u)]
    out.append(_row("sitemap.only_canonical", A, f"{len(cross)} canonicalized elsewhere",
                    "only self-canonical URLs", _verdict(cross), "course/22",
                    _ev(cross) or coverage))

    dis = g.get("sitemap_urls_disallowed") or []
    out.append(_row("sitemap.not_disallowed", A, f"{len(dis)} disallowed by robots.txt",
                    "nothing in the sitemap is Disallowed", _verdict(dis), "course/22",
                    _ev(dis) or "The sitemap says 'index this' and robots.txt says 'never "
                                "fetch this'. One of the two is wrong."))

    # lastmod. A count cannot see the bad pattern; the distinct dates can.
    with_lm = sum(f["lastmods"] for f in files)
    dates = sorted({d for f in files for d in (f.get("lastmod_dates") or [])})
    if not with_lm:
        out.append(_row("sitemap.lastmod", A, "no lastmod values", "accurate lastmod",
                        "review", "course/22 [practitioner]",
                        "Google uses lastmod as a recrawl hint. Absent is better than wrong, "
                        "but accurate is better than absent."))
    elif len(dates) == 1 and len(submitted) > 5:
        out.append(_row("sitemap.lastmod", A, f"all {with_lm} URLs share lastmod {dates[0]}",
                        "lastmod reflects real change dates", "fail", "course/22 [practitioner]",
                        "One date across the whole sitemap is the recognised bad pattern: it "
                        "is generated, not observed, and it destroys the value of the hint."))
    else:
        out.append(_row("sitemap.lastmod", A,
                        f"{with_lm} URL(s) with lastmod across {len(dates)} distinct date(s)",
                        "lastmod reflects real change dates", "pass", "course/22 [practitioner]",
                        _ev(dates[:4])))

    big = [f"{f['url']}: {len(f['urls'])} URLs" for f in files
           if not f["is_index"] and len(f["urls"]) > SITEMAP_SPLIT_ABOVE]
    has_index = any(f["is_index"] for f in files)
    out.append(_row("sitemap.split_by_type", A,
                    f"{len(files)} file(s), index present" if has_index else "single flat file",
                    f"split by content type above ~{SITEMAP_SPLIT_ABOVE} URLs",
                    "review" if big and not has_index else "pass", "course/22 [practitioner]",
                    _ev(big) or "Splitting costs nothing and turns the Search Console Pages "
                                "report into a localised diagnosis."))

    subs = set(submitted)
    missing = [u for u, p in _live(pages).items()
               if u not in subs and p.get("indexable") and not p.get("redirect_chain")]
    out.append(_row("sitemap.covers_indexable", A,
                    f"{len(missing)} indexable crawled page(s) not submitted",
                    "every page you want indexed is in the sitemap",
                    "review" if missing else "pass", "course/22", _ev(missing)))

    out.append(_row(
        "index.ratio", A, "not connected", f"above {INDEXED_RATIO_HEALTHY:.0%} indexed-to-submitted",
        "unknown", "course/22 [practitioner]",
        "Only Search Console can report what Google actually indexed, and no Search Console "
        "credential exists here (gws exposes no Search Console service - verified). A crawl "
        "reports what this crawler fetched, which is not the same question.\n"
        "Manual: Search Console -> Pages. Record indexed vs submitted, then the counts for "
        "'Crawled - currently not indexed' (a quality rejection) and 'Discovered - currently "
        "not indexed' (a crawl-reach problem). They look adjacent and share no fixes."))
    return out


# --------------------------------------------------------------------------- 23. canonicals

def check_canonicals(g: dict) -> list[dict]:
    A = "Canonicals and duplicates"
    pages = g.get("pages") or {}
    live = _live(pages)
    origin = g.get("origin") or ""
    home = crawl.normalize_url(origin.rstrip("/") + "/")
    out: list[dict] = []

    missing = [u for u, p in live.items() if not p.get("canonical")]
    out.append(_row("canonical.present", A, f"{len(missing)} of {len(live)} pages without one",
                    "a self-referencing canonical on every indexable page",
                    _verdict(missing), "course/23", _ev(missing)))

    relative = [f"{u} -> {p['canonical_raw']}" for u, p in live.items()
                if p.get("canonical_raw") and not p["canonical_raw"].lower().startswith("http")]
    out.append(_row("canonical.absolute", A, f"{len(relative)} relative canonical(s)",
                    "absolute URLs only", _verdict(relative), "course/23", _ev(relative)))

    multi = [f"{u}: {p['canonical_count']} tags" for u, p in live.items()
             if (p.get("canonical_count") or 0) > 1]
    out.append(_row("canonical.single", A, f"{len(multi)} page(s) with more than one",
                    "exactly one canonical per page", _verdict(multi), "course/23",
                    _ev(multi) or "Multiple canonical tags make Google ignore all of them. "
                                  "Usually a plugin conflict."))

    self_ref = [u for u, p in live.items()
                if p.get("canonical") and crawl.normalize_url(p["canonical"]) == crawl.normalize_url(u)]
    cross = {u: p["canonical"] for u, p in live.items()
             if p.get("canonical") and crawl.normalize_url(p["canonical"]) != crawl.normalize_url(u)}
    out.append(_row("canonical.self_referencing", A,
                    f"{len(self_ref)} self-referencing, {len(cross)} pointing elsewhere",
                    "self-referencing by default", "review" if cross else "pass", "course/23",
                    _ev([f"{u} -> {c}" for u, c in cross.items()]) or
                    "Pointing elsewhere is legitimate when the pages really are duplicates. "
                    "Each one below needs a reason."))

    to_home = [f"{u} -> {c}" for u, c in cross.items() if crawl.normalize_url(c) == home]
    out.append(_row("canonical.not_homepage", A, f"{len(to_home)} page(s) canonicalized to /",
                    "nothing canonicalizes to the homepage except the homepage",
                    _verdict(to_home), "course/23", _ev(to_home) or
                    "Canonicalizing the site to its homepage tells Google the rest of the "
                    "site does not exist. Common and destructive."))

    bad_target = []
    for u, c in cross.items():
        t = pages.get(crawl.normalize_url(c))
        if t is None:
            continue
        if t.get("status") != 200:
            bad_target.append(f"{u} -> {c} (HTTP {t['status']})")
        elif t.get("redirect_chain"):
            bad_target.append(f"{u} -> {c} (redirects to {t['final_url']})")
    out.append(_row("canonical.target_200", A, f"{len(bad_target)} pointing at a non-200",
                    "canonical targets return 200, not a redirect and not a 404",
                    _verdict(bad_target), "course/23", _ev(bad_target)))

    contradiction = [u for u, p in live.items() if p.get("canonical") and _has_noindex(p)]
    out.append(_row("canonical.noindex_conflict", A,
                    f"{len(contradiction)} page(s) carry both", "canonical or noindex, not both",
                    _verdict(contradiction), "course/23", _ev(contradiction) or
                    "One says 'index this other page instead', the other says 'index "
                    "nothing'. Pick one."))

    linked_to_variant = []
    for u, p in live.items():
        for tgt in p.get("internal_outlinks") or []:
            c = cross.get(crawl.normalize_url(tgt))
            if c:
                linked_to_variant.append(f"{u} links to {tgt}, which canonicalizes to {c}")
    out.append(_row("canonical.links_agree", A, f"{len(linked_to_variant)} internal link(s) "
                    "point at a canonicalized variant",
                    "internal links point at canonical URLs directly",
                    "review" if linked_to_variant else "pass", "course/23 [practitioner]",
                    _ev(linked_to_variant) or
                    "Contradicting your own canonical with your internal linking weakens it."))

    # Host and protocol variants. Four unresolved homepages is the default state of the web.
    probe = g.get("origin_probe") or {}
    resolves = probe.get("resolves_to") or []
    variants = probe.get("variants") or {}
    if not variants:
        out.append(_row("dupe.host_variants", A, "not probed",
                        "http, https, www and non-www all resolve to one version",
                        "unknown", "course/23",
                        "This graph predates the origin probe. Re-crawl with --refresh."))
    else:
        detail = [f"{u} -> HTTP {v['status']} {v['final_url']}" for u, v in variants.items()]
        out.append(_row("dupe.host_variants", A,
                        f"{len(resolves)} distinct destination(s) across 4 variants",
                        "all four resolve to one version",
                        "pass" if len(resolves) == 1 else "fail", "course/23", _ev(detail, 8)))

    slash_dupes = []
    for u in live:
        alt = u[:-1] if u.endswith("/") else u + "/"
        if alt in live and u < alt:
            slash_dupes.append(f"{u}  and  {alt}")
    out.append(_row("dupe.trailing_slash", A, f"{len(slash_dupes)} URL pair(s) served both ways",
                    "one form only", _verdict(slash_dupes), "course/23", _ev(slash_dupes)))

    titles = defaultdict(list)
    for u, p in live.items():
        if p.get("title") and p.get("indexable"):
            titles[p["title"].strip().lower()].append(u)
    dupe_titles = {t: us for t, us in titles.items() if len(us) > 1}
    out.append(_row("dupe.titles", A, f"{len(dupe_titles)} title(s) shared by 2+ indexable pages",
                    "distinct titles", "review" if dupe_titles else "pass", "course/23",
                    _ev([f"{t!r}: {', '.join(us[:3])}" for t, us in dupe_titles.items()]) or
                    "Pages differing only by a place name are a content problem wearing a "
                    "technical costume - see course/35, not a canonical."))

    params = [u for u, p in live.items() if "?" in u and p.get("indexable")]
    out.append(_row("dupe.parameter_urls", A, f"{len(params)} indexable URL(s) with parameters",
                    "parameter variants canonicalize to the clean URL",
                    "review" if params else "pass", "course/23", _ev(params)))

    out.append(_row(
        "canonical.google_selected", A, "not connected",
        "Google's selected canonical matches the declared one", "unknown", "course/23 [confirmed]",
        "The canonical tag is a hint, not a directive, and only Search Console URL Inspection "
        "shows 'Google-selected canonical' against 'User-declared canonical'. No credential "
        "exists here.\nManual: URL Inspection on the five most important pages; note any "
        "disagreement. The fix is always to make every signal agree - tag, internal links, "
        "sitemap inclusion and redirects all pointing the same way."))
    return out


# --------------------------------------------------------------------------- 24. redirects

def check_redirects(g: dict) -> list[dict]:
    A = "Redirects and status codes"
    pages = g.get("pages") or {}
    origin = g.get("origin") or ""
    home = crawl.normalize_url(origin.rstrip("/") + "/")
    out: list[dict] = []

    by_class = Counter()
    for p in pages.values():
        s = p.get("status") or 0
        by_class[f"{s // 100}xx" if s else "error"] += 1
    non200 = [f"{u} -> HTTP {p['status']}" for u, p in pages.items() if p.get("status") != 200]
    out.append(_row("status.inventory", A,
                    ", ".join(f"{k}: {v}" for k, v in sorted(by_class.items())),
                    "everything indexable returns 200",
                    "review" if non200 else "pass", "course/24", _ev(non200) or
                    "Every crawled URL returned 200. Nothing to triage."))

    server_errors = [f"{u} -> HTTP {p['status']}" for u, p in pages.items()
                     if 500 <= (p.get("status") or 0) < 600]
    out.append(_row("status.no_5xx", A, f"{len(server_errors)} server error(s)",
                    "no 5xx anywhere", _verdict(server_errors), "course/24", _ev(server_errors)))

    unreachable = [f"{u}: {p['error']}" for u, p in pages.items() if p.get("error")]
    out.append(_row("status.reachable", A, f"{len(unreachable)} URL(s) failed to fetch",
                    "every URL responds", _verdict(unreachable), "course/24", _ev(unreachable)))

    chains, long_chains, loops, temporary, to_home = [], [], [], [], []
    for u, p in pages.items():
        hops = p.get("redirect_chain") or []
        if not hops:
            continue
        trail = " -> ".join([h["url"] for h in hops] + [p.get("final_url") or ""])
        if len(hops) > MAX_REDIRECT_HOPS:
            chains.append(f"{len(hops)} hops: {trail}")
        if len(hops) >= ABANDON_HOPS:
            long_chains.append(f"{len(hops)} hops: {trail}")
        seen = [h["url"] for h in hops] + [p.get("final_url") or ""]
        if len(seen) != len(set(seen)):
            loops.append(trail)
        temp = [h["status"] for h in hops if h["status"] in (302, 303, 307)]
        if temp:
            temporary.append(f"HTTP {temp[0]}: {trail}")
        if crawl.normalize_url(p.get("final_url") or "") == home and crawl.normalize_url(u) != home:
            to_home.append(trail)

    out.append(_row("redirect.single_hop", A, f"{len(chains)} chain(s) longer than one hop",
                    "one redirect, not two", _verdict(chains), "course/24 [practitioner]",
                    _ev(chains) or "Each hop adds 100-500ms and leaks signal. Flatten to one, "
                                   "then repoint internal links at the destination."))

    out.append(_row("redirect.under_abandon_limit", A, f"{len(long_chains)} chain(s) at {ABANDON_HOPS}+ hops",
                    f"fewer than {ABANDON_HOPS} hops", _verdict(long_chains),
                    "course/24 [practitioner]",
                    _ev(long_chains) or "Googlebot may abandon chains beyond five hops "
                                        "entirely, so the destination never gets crawled."))

    out.append(_row("redirect.no_loops", A, f"{len(loops)} loop(s)", "none",
                    _verdict(loops), "course/24", _ev(loops) or
                    "A loop makes the page permanently unreachable. Always a bug, always urgent."))

    out.append(_row("redirect.permanent", A, f"{len(temporary)} temporary redirect(s)",
                    "301 for anything permanent", _verdict(temporary), "course/24", _ev(temporary) or
                    "A 302 tells Google to keep the old URL indexed, so ranking signals stay "
                    "with the URL you retired. Usually a framework default, not a decision."))

    out.append(_row("redirect.not_to_homepage", A, f"{len(to_home)} redirect(s) land on /",
                    "redirect to the closest equivalent page", _verdict(to_home),
                    "course/24 [practitioner]", _ev(to_home) or
                    "A redirect to an irrelevant page is treated as a soft 404, so the signal "
                    "you were preserving is lost anyway."))

    redirecting = {u for u, p in pages.items() if p.get("redirect_chain")}
    stale_links = []
    for u, p in pages.items():
        for tgt in p.get("internal_outlinks") or []:
            if crawl.normalize_url(tgt) in redirecting:
                stale_links.append(f"{u} -> {tgt}")
    out.append(_row("redirect.links_are_final", A, f"{len(stale_links)} internal link(s) hit a redirect",
                    "internal links point at final destinations",
                    "review" if stale_links else "pass", "course/24", _ev(stale_links) or
                    "A redirect should be a fallback for external links, not a routine "
                    "internal hop."))

    dead_links = []
    for u, p in pages.items():
        for tgt in p.get("internal_outlinks") or []:
            t = pages.get(crawl.normalize_url(tgt))
            if t is not None and (t.get("status") or 0) >= 400:
                dead_links.append(f"{u} -> {tgt} (HTTP {t['status']})")
    out.append(_row("status.no_broken_links", A, f"{len(dead_links)} internal link(s) to 4xx/5xx",
                    "no internal links to dead URLs", _verdict(dead_links), "course/24",
                    _ev(dead_links)))

    probe = (g.get("origin_probe") or {}).get("missing_url_probe") or {}
    if not probe:
        out.append(_row("status.404_is_404", A, "not probed", "a missing URL returns 404 or 410",
                        "unknown", "course/24",
                        "This graph predates the origin probe. Re-crawl with --refresh."))
    else:
        st = probe.get("status")
        out.append(_row("status.404_is_404", A, f"a URL that cannot exist returns HTTP {st}",
                        "404 or 410", "pass" if st in (404, 410) else "fail", "course/24",
                        f"Probed {probe.get('url')}\n" +
                        ("A 200 here is a soft 404 template: it wastes crawl budget and "
                         "clutters the index." if st == 200 else
                         "Tested with a URL that cannot exist, which is the only way to see "
                         "the real status of the not-found template.")))

    thin = [f"{u} ({p.get('word_count', 0)} words)" for u, p in _live(pages).items()
            if (p.get("word_count") or 0) < SOFT_404_WORDS]
    out.append(_row("status.soft_404_pages", A, f"{len(thin)} page(s) return 200 with under "
                    f"{SOFT_404_WORDS} words", "a 200 has real content",
                    "review" if thin else "pass", "course/24", _ev(thin) or
                    "Word count is a proxy. A genuinely empty template should return a real "
                    "404 or 410; a thin real page is a content problem for seo-onpage."))
    return out


# --------------------------------------------------------------------------- 25. architecture

def check_architecture(g: dict) -> list[dict]:
    A = "Site architecture"
    pages = g.get("pages") or {}
    live = _live(pages)
    out: list[dict] = []

    depths = {u: p.get("depth") for u, p in live.items()}
    reachable = {u: d for u, d in depths.items() if d is not None}
    deep = sorted([f"depth {d}: {u}" for u, d in reachable.items() if d > MAX_DEPTH_COMMERCIAL])
    out.append(_row("depth.within_3_clicks", A,
                    f"{len(deep)} page(s) deeper than {MAX_DEPTH_COMMERCIAL} clicks",
                    f"{MAX_DEPTH_COMMERCIAL} clicks maximum to any commercial page",
                    "review" if deep else "pass", "course/25 [practitioner]",
                    _ev(deep) or "Click depth is the shortest link path, not URL folder depth.\n"
                    "This is `review` not `fail` because nothing here knows which pages are "
                    "commercial. Check the list against the money pages."))

    neglected = sorted([f"depth {d}: {u}" for u, d in reachable.items() if d >= DEPTH_NEGLECTED])
    out.append(_row("depth.not_neglected", A, f"{len(neglected)} page(s) at {DEPTH_NEGLECTED}+ clicks",
                    f"nothing important below {DEPTH_NEGLECTED} clicks",
                    _verdict(neglected), "course/25 [practitioner]", _ev(neglected) or
                    "Pages this deep are crawled less often and receive very little authority."))

    orphans = sorted(u for u, p in live.items()
                     if p.get("depth") is None and p.get("indexable"))
    out.append(_row("arch.no_orphans", A, f"{len(orphans)} indexable page(s) unreachable by link",
                    "every indexable page is reachable from the homepage",
                    _verdict(orphans), "course/25 -> course/16", _ev(orphans) or
                    "Reached from the sitemap but linked from nothing crawled. Zero internal "
                    "links means effectively invisible, and Google may never fetch it at all."))

    # Sitewide links are the navigation, derived rather than parsed: a link present on most
    # pages is in a template. More reliable than trusting a <nav> element to exist, and the
    # set is subtracted below so no check mistakes a big menu for page content.
    counts = Counter(t for p in live.values() for t in set(p.get("internal_outlinks") or []))
    threshold = max(2, int(len(live) * SITEWIDE_LINK_RATIO))
    sitewide = {u for u, c in counts.items() if c >= threshold}
    nav = sorted(sitewide)
    out.append(_row("nav.item_count", A, f"{len(nav)} link(s) appear on {SITEWIDE_LINK_RATIO:.0%}+ of pages",
                    f"about {NAV_ITEMS_MAX} main navigation items",
                    "review" if len(nav) > NAV_ITEMS_MAX else "pass", "course/25 -> course/13",
                    _ev(nav, 12) + ("\n\nThis is every sitewide link, so it includes footer and "
                                    "utility links as well as the main nav. Count the main nav "
                                    "by eye before acting." if len(nav) > NAV_ITEMS_MAX else "")))

    deep_pages = {u: p for u, p in live.items() if (p.get("depth") or 0) >= 2}
    no_crumbs = [u for u, p in deep_pages.items()
                 if not _has_type(p.get("jsonld") or [], "BreadcrumbList")]
    out.append(_row("arch.breadcrumbs", A,
                    f"{len(deep_pages) - len(no_crumbs)} of {len(deep_pages)} deep page(s) "
                    "carry BreadcrumbList",
                    "breadcrumbs on pages below the top level",
                    "review" if no_crumbs else "pass", "course/25 [practitioner] -> course/30",
                    _ev(no_crumbs) or "Described as one of the most under-implemented signals "
                                      "available. schema.py validates the markup itself."))

    params = [u for u in live if "?" in u]
    out.append(_row("arch.faceted_urls", A, f"{len(params)} parameter URL(s) crawled",
                    "facet combinations people actually search for are indexed, the rest are not",
                    "review" if params else "pass", "course/25", _ev(params) or
                    "None found in this crawl. Confirm with site:domain inurl:? - a crawler "
                    "only finds the facet URLs the site links to itself."))

    paged = [u for u in live if PAGINATION.search(u)]
    bad_paged = [f"{u} -> {live[u]['canonical']}" for u in paged
                 if live[u].get("canonical")
                 and crawl.normalize_url(live[u]["canonical"]) != crawl.normalize_url(u)]
    out.append(_row("arch.pagination", A,
                    f"{len(paged)} paginated URL(s), {len(bad_paged)} canonicalized away",
                    "each paginated page carries a self-referencing canonical",
                    _verdict(bad_paged), "course/25", _ev(bad_paged) or
                    "Page 2 is different content from page 1; canonicalizing it to page 1 "
                    "hides everything on it. rel=next/prev is no longer used by Google."))

    # Body links only. Counting every internal link here would flag every page on any site
    # with a large menu - the first live run reported "36 links" on all 25 pages, which was
    # the navigation, not a link list. Same trap seo-onpage documents in _main_content_text.
    hubs = []
    for u, p in live.items():
        body = [t for t in (p.get("internal_outlinks") or []) if t not in sitewide]
        if len(body) >= 10 and (p.get("word_count") or 0) < 300:
            hubs.append(f"{u} ({len(body)} body links, {p.get('word_count', 0)} words)")
    out.append(_row("arch.hub_pages_have_content", A, f"{len(hubs)} link-list page(s)",
                    "category pages get a real introduction and a target cluster",
                    "review" if hubs else "pass", "course/25", _ev(hubs) or
                    "Counted excluding the sitewide navigation. A category page done properly "
                    "is a pillar page; done lazily it is a crawl waypoint that ranks for "
                    "nothing."))
    return out


def _has_type(blocks: list, wanted: str) -> bool:
    """True if any JSON-LD block on the page declares @type `wanted`, at any nesting depth."""
    stack = list(blocks)
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            t = node.get("@type")
            if t == wanted or (isinstance(t, list) and wanted in t):
                return True
            stack += list(node.values())
        elif isinstance(node, list):
            stack += node
    return False


# --------------------------------------------------------------------------- 31. hreflang

def _valid_hreflang(code: str) -> str:
    """"" if valid, else why not. Format is ISO 639-1, optionally -ISO 3166-1 alpha 2."""
    code = (code or "").strip()
    if not code:
        return "empty"
    if code.lower() == "x-default":
        return ""
    parts = code.split("-")
    if len(parts) > 2:
        return f"{code!r} has too many parts"
    lang = parts[0].lower()
    if lang not in ISO_639_1:
        if len(lang) == 2 and parts[0].isupper():
            return f"{code!r} looks like a region without a language, which is invalid"
        return f"{code!r}: {parts[0]!r} is not an ISO 639-1 language code"
    if len(parts) == 2:
        region = parts[1].upper()
        if len(region) != 2 or not region.isalpha():
            return f"{code!r}: {parts[1]!r} is not an ISO 3166-1 alpha-2 region"
        if region in BAD_REGIONS:
            fix = BAD_REGIONS[region]
            return f"{code!r}: {region} is not a valid region code" + (f"; use {fix}" if fix else "")
    return ""


def check_hreflang(g: dict) -> list[dict]:
    A = "International and hreflang"
    pages = g.get("pages") or {}
    live = _live(pages)
    tagged = {u: p["hreflang"] for u, p in live.items() if p.get("hreflang")}
    out: list[dict] = []

    if not tagged:
        return [_row("hreflang.applicable", A, "no hreflang found on any crawled page",
                     "present only if the site genuinely has multiple language or region versions",
                     "pass", "course/31",
                     "Most sites should not have hreflang, and a documented 'not applicable' is "
                     "a legitimate audit finding - it stops someone implementing it later for "
                     "no reason. It becomes applicable only with substantially different "
                     "content per language or market. A single well-executed site usually "
                     "outperforms three thin translated ones.")]

    out.append(_row("hreflang.applicable", A, f"{len(tagged)} of {len(live)} page(s) declare hreflang",
                    "present because the site needs it", "review", "course/31",
                    "Confirm the versions differ in substance - currency, pricing, shipping, "
                    "legal terms - and not just a swapped currency symbol. hreflang is not a "
                    "ranking signal; it shows the right version to the right user."))

    invalid = []
    for u, alts in tagged.items():
        for a in alts:
            why = _valid_hreflang(a.get("lang", ""))
            if why:
                invalid.append(f"{u}: {why}")
    out.append(_row("hreflang.codes_valid", A, f"{len(invalid)} invalid code(s)",
                    "ISO 639-1 language, optional ISO 3166-1 alpha-2 region; region alone invalid",
                    _verdict(invalid), "course/31", _ev(invalid)))

    no_self = [u for u, alts in tagged.items()
               if not any(crawl.normalize_url(a.get("href", "")) == crawl.normalize_url(u)
                          for a in alts)]
    out.append(_row("hreflang.self_referencing", A, f"{len(no_self)} page(s) omit themselves",
                    "every page includes itself in its own set", _verdict(no_self),
                    "course/31", _ev(no_self)))

    no_default = [u for u, alts in tagged.items()
                  if not any((a.get("lang") or "").lower() == "x-default" for a in alts)]
    out.append(_row("hreflang.x_default", A, f"{len(no_default)} page(s) without x-default",
                    "always include x-default", "review" if no_default else "pass",
                    "course/31", _ev(no_default) or
                    "x-default is the fallback for users matching no other version."))

    broken_return, unverifiable = [], []
    for u, alts in tagged.items():
        for a in alts:
            href = crawl.normalize_url(a.get("href", ""))
            if not href or href == crawl.normalize_url(u):
                continue
            other = live.get(href)
            if other is None:
                unverifiable.append(f"{u} -> {href} (not crawled)")
            elif not any(crawl.normalize_url(b.get("href", "")) == crawl.normalize_url(u)
                         for b in other.get("hreflang") or []):
                broken_return.append(f"{u} declares {href}, which does not declare it back")
    out.append(_row("hreflang.return_links", A,
                    f"{len(broken_return)} one-way declaration(s), {len(unverifiable)} unverifiable",
                    "every declaration is bidirectional", _verdict(broken_return), "course/31",
                    _ev(broken_return + unverifiable) or
                    "The most common hreflang failure, and it fails silently: a one-way "
                    "declaration is ignored entirely."))

    bad_targets = []
    for u, alts in tagged.items():
        for a in alts:
            href = crawl.normalize_url(a.get("href", ""))
            t = pages.get(href)
            if t is None:
                continue
            if t.get("status") != 200:
                bad_targets.append(f"{u} -> {href} (HTTP {t['status']})")
            elif t.get("redirect_chain"):
                bad_targets.append(f"{u} -> {href} (redirects)")
            elif _has_noindex(t):
                bad_targets.append(f"{u} -> {href} (noindex)")
    out.append(_row("hreflang.targets_indexable", A, f"{len(bad_targets)} bad target(s)",
                    "hreflang references canonical, indexable, 200-status URLs",
                    _verdict(bad_targets), "course/31", _ev(bad_targets)))

    conflict = []
    for u, alts in tagged.items():
        can = live[u].get("canonical")
        if not can or crawl.normalize_url(can) == crawl.normalize_url(u):
            continue
        if any(crawl.normalize_url(a.get("href", "")) == crawl.normalize_url(can) for a in alts):
            conflict.append(f"{u} canonicalizes to {can}, which it also declares as an alternate")
    out.append(_row("hreflang.canonical_agrees", A, f"{len(conflict)} conflict(s)",
                    "hreflang and canonical do not contradict each other",
                    _verdict(conflict), "course/31", _ev(conflict) or
                    "A page saying 'index me separately for German users' and 'index the "
                    "English one instead' loses: the canonical wins and hreflang is ignored."))
    return out


# --------------------------------------------------------------------------- run

AREAS = {
    "robots": check_robots,
    "sitemaps": check_sitemaps,
    "canonicals": check_canonicals,
    "redirects": check_redirects,
    "architecture": check_architecture,
    "hreflang": check_hreflang,
}


def analyze(g: dict, areas: list[str] | None = None) -> dict:
    names = areas or list(AREAS)
    rows: list[dict] = []
    for name in names:
        rows += AREAS[name](g)

    counts = {v: sum(1 for r in rows if r["verdict"] == v)
              for v in ("pass", "fail", "review", "unknown")}
    stats = g.get("stats") or {}
    return {
        "origin": g.get("origin"),
        "crawled_at": g.get("crawled_at"),
        "pages_crawled": stats.get("pages_crawled"),
        "hit_cap": stats.get("hit_cap"),
        "areas": names,
        "counts": counts,
        "checks": rows,
        "not_connected": [
            "Search Console: indexed-to-submitted ratio, the exclusion reasons behind it "
            "('Crawled - not indexed' vs 'Discovered - not indexed'), Google-selected "
            "canonical, the soft-404 report and Crawl stats are all unavailable. gws exposes "
            "no Search Console service and no credential exists - verified, not assumed. "
            "Half of Tier 3 is an indexation question, so this is the largest gap in the "
            "skill and it is named rather than approximated.",
            "Backlink profile: which URLs carry external links decides redirect mapping "
            "priority during a migration (course/24). No backlink tool is connected.",
        ],
        "reading_note": (
            "Read in tier order, not by count. Sections 21 and 22 come first because a page "
            "that is not crawled or not indexed cannot rank, and no amount of work above that "
            "layer changes it. Fixing schema on a site whose pages are not indexed is "
            "polishing something invisible."
            + (f"\n\nThis crawl hit its {stats.get('cap')}-page cap, so every count here is a "
               "floor, not a total." if stats.get("hit_cap") else "")),
    }


# --------------------------------------------------------------------------- selftest

def _fixture_graph() -> dict:
    """A deliberately broken site, small enough to reason about, with no network involved."""
    def page(url, **kw):
        base = {"url": url, "final_url": url, "status": 200, "bytes": 900, "html_chars": 900,
                "content_type": "text/html", "x_robots_tag": None, "redirect_chain": [],
                "error": None, "title": "T", "h1": ["H"], "meta_robots": None,
                "canonical": url, "canonical_raw": url, "canonical_count": 1, "hreflang": [],
                "jsonld": [], "microdata_types": [], "images": [], "outlinks": [],
                "internal_outlinks": [], "word_count": 400, "has_viewport": True, "lang": "en",
                "depth": 1, "discovered_via": "link", "in_sitemap": True, "indexable": True,
                "not_indexable_because": ""}
        base.update(kw)
        return base

    o = "https://e.test"
    pages = {
        f"{o}/": page(f"{o}/", depth=0, title="Home",
                      internal_outlinks=[f"{o}/a", f"{o}/b", f"{o}/gone", f"{o}/moved"]),
        f"{o}/a": page(f"{o}/a", title="Shared", internal_outlinks=[f"{o}/deep1"]),
        f"{o}/b": page(f"{o}/b", title="Shared", canonical=f"{o}/", canonical_raw="/",
                       meta_robots="noindex"),
        f"{o}/deep1": page(f"{o}/deep1", depth=2, internal_outlinks=[f"{o}/deep2"]),
        f"{o}/deep2": page(f"{o}/deep2", depth=3, internal_outlinks=[f"{o}/deep3"]),
        f"{o}/deep3": page(f"{o}/deep3", depth=4, internal_outlinks=[f"{o}/deep4"]),
        f"{o}/deep4": page(f"{o}/deep4", depth=5),
        f"{o}/orphan": page(f"{o}/orphan", depth=None),
        # A link list with no introduction: the category page that ranks for nothing.
        f"{o}/hub": page(f"{o}/hub", word_count=80,
                         internal_outlinks=[f"{o}/h{i}" for i in range(12)]),
        f"{o}/gone": page(f"{o}/gone", status=404, indexable=False),
        f"{o}/moved": page(f"{o}/moved", final_url=f"{o}/a", status=200,
                           redirect_chain=[{"status": 302, "url": f"{o}/moved"},
                                           {"status": 301, "url": f"{o}/mid"}]),
        f"{o}/de/x": page(f"{o}/de/x", lang="de", hreflang=[
            {"lang": "de", "href": f"{o}/de/x"}, {"lang": "en-UK", "href": f"{o}/a"}]),
    }
    return {
        "graph_version": crawl.GRAPH_VERSION, "origin": o, "seed": f"{o}/",
        "crawled_at": "2026-01-01T00:00:00",
        "robots": {"url": f"{o}/robots.txt", "status": 200, "text": "", "returns_200": True,
                   "is_5xx": False, "disallow_all": False, "disallows": ["/private"],
                   "sitemaps": [], "blocks_css_or_js": ["/assets/app.css"],
                   "has_sitemap_directive": False, "ai_policy_declared": {},
                   "mentions_deprecated_anthropic_ai": True, "crawl_delay": None},
        "origin_probe": {
            "variants": {f"https://e.test/": {"status": 200, "final_url": f"{o}/", "hops": 0,
                                              "error": None},
                         f"https://www.e.test/": {"status": 200, "final_url": "https://www.e.test/",
                                                  "hops": 0, "error": None}},
            "resolves_to": [f"{o}/", "https://www.e.test/"],
            "missing_url_probe": {"url": f"{o}/nope", "status": 200, "words": 12, "error": None}},
        "sitemap_files": [{"url": f"{o}/sitemap.xml", "status": 200, "bytes": 500,
                           "is_index": False,
                           "urls": [f"{o}/", f"{o}/a", f"{o}/b", f"{o}/gone", f"{o}/deep1",
                                    f"{o}/deep2", f"{o}/hub"],
                           "children": [], "error": None, "lastmods": 7,
                           "lastmod_dates": ["2026-01-01"]}],
        "sitemap_urls_submitted": [f"{o}/", f"{o}/a", f"{o}/b", f"{o}/gone", f"{o}/deep1",
                                   f"{o}/deep2", f"{o}/hub"],
        "sitemap_urls_disallowed": [],
        "pages": pages, "skipped_by_robots": [],
        "stats": {"pages_crawled": len(pages), "cap": 300, "hit_cap": False},
        "_meta": {"cached": False, "respected_robots": True},
    }


def _selftest() -> int:
    ok = True
    res = analyze(_fixture_graph())
    by = {r["check_id"]: r for r in res["checks"]}

    print("1. the broken fixture fails exactly the checks it should")
    expect_fail = {
        "robots.css_js_open": "an /assets rule blocks CSS",
        "robots.sitemap_directive": "no Sitemap: line",
        "robots.no_deprecated_agents": "anthropic-ai present",
        "sitemap.only_200": "a 404 is submitted",
        "sitemap.only_indexable": "a noindexed URL is submitted",
        "sitemap.only_canonical": "a cross-canonicalized URL is submitted",
        "sitemap.lastmod": "one date across the whole file",
        "canonical.not_homepage": "/b canonicalizes to /",
        "canonical.noindex_conflict": "/b has both",
        "canonical.absolute": "/b's canonical is relative",
        "dupe.host_variants": "www and non-www both answer 200",
        "redirect.single_hop": "/moved is two hops",
        "redirect.permanent": "the first hop is a 302",
        "status.no_broken_links": "/ links to a 404",
        "status.404_is_404": "the missing-URL probe returned 200",
        "depth.not_neglected": "/deep4 is 5 clicks down",
        "arch.no_orphans": "/orphan is linked from nothing",
        "hreflang.codes_valid": "en-UK is not a valid region",
        "hreflang.return_links": "/a does not declare /de/x back",
    }
    for cid, why in expect_fail.items():
        got = by.get(cid, {}).get("verdict")
        if got != "fail":
            print(f"   FAIL: {cid} = {got}, expected fail ({why})")
            ok = False
    if ok:
        print(f"   PASS: all {len(expect_fail)} expected failures fired")

    print("2. judgment calls stay `review`, never a fabricated pass")
    judgment = ("robots.ai_policy", "depth.within_3_clicks", "dupe.titles",
                "canonical.self_referencing", "arch.hub_pages_have_content")
    wrong = [(c, by.get(c, {}).get("verdict")) for c in judgment
             if by.get(c, {}).get("verdict") != "review"]
    print(f"   PASS: all {len(judgment)} judgment checks report review" if not wrong
          else f"   FAIL: {wrong}")
    ok &= not wrong

    print("3. Search Console gaps report `unknown`, not `pass`")
    gaps = [c for c in ("index.ratio", "canonical.google_selected")
            if by.get(c, {}).get("verdict") != "unknown"
            or "Manual:" not in by.get(c, {}).get("evidence", "")]
    print("   PASS: both indexation gaps are unknown and name the manual steps" if not gaps
          else f"   FAIL: {gaps} must be unknown AND carry a manual method")
    ok &= not gaps

    print("4. a clean site does not manufacture findings")
    clean = _fixture_graph()
    clean["robots"].update(blocks_css_or_js=[], has_sitemap_directive=True,
                           sitemaps=["https://e.test/sitemap.xml"],
                           mentions_deprecated_anthropic_ai=False)
    clean["origin_probe"]["resolves_to"] = ["https://e.test/"]
    clean["origin_probe"]["missing_url_probe"]["status"] = 404
    for u in ("https://e.test/gone", "https://e.test/b"):
        clean["sitemap_urls_submitted"].remove(u)
    clean["sitemap_files"][0]["urls"] = ["https://e.test/"]
    clean["sitemap_files"][0]["lastmod_dates"] = ["2026-01-01", "2026-02-03"]
    del clean["pages"]["https://e.test/moved"]
    del clean["pages"]["https://e.test/orphan"]
    clean["pages"]["https://e.test/"]["internal_outlinks"] = ["https://e.test/a"]
    clean["pages"]["https://e.test/de/x"]["hreflang"] = []
    for u in ("https://e.test/deep3", "https://e.test/deep4"):
        del clean["pages"][u]
    clean["pages"]["https://e.test/deep2"]["internal_outlinks"] = []
    clean["pages"]["https://e.test/b"].update(canonical="https://e.test/b",
                                              canonical_raw="https://e.test/b", meta_robots=None)
    del clean["pages"]["https://e.test/gone"]
    clean["pages"]["https://e.test/"]["internal_outlinks"] = ["https://e.test/a", "https://e.test/b"]
    res2 = analyze(clean)
    fails = [r["check_id"] for r in res2["checks"] if r["verdict"] == "fail"]
    if not fails:
        print("   PASS: zero failures on the repaired fixture")
    else:
        print(f"   FAIL: still failing {fails}")
        ok = False

    print("5. hreflang absent is a pass, not a finding")
    no_i18n = _fixture_graph()
    no_i18n["pages"]["https://e.test/de/x"]["hreflang"] = []
    rows = check_hreflang(no_i18n)
    if len(rows) == 1 and rows[0]["verdict"] == "pass" and "not applicable" in rows[0]["evidence"]:
        print("   PASS: one row, documented not-applicable")
    else:
        print(f"   FAIL: {[(r['check_id'], r['verdict']) for r in rows]}")
        ok = False

    print("6. hreflang code validation")
    cases = {"en": "", "de-AT": "", "x-default": "", "zh-Hant": "bad",
             "AT": "bad", "en-UK": "bad", "xx": "bad", "en-us": ""}
    bad = [c for c, want in cases.items()
           if bool(_valid_hreflang(c)) != (want == "bad")]
    if not bad:
        print("   PASS: region-alone, en-UK and unknown languages all rejected")
    else:
        print(f"   FAIL: {[(c, _valid_hreflang(c)) for c in bad]}")
        ok = False

    print("7. evidence is capped, so a finding stays a finding")
    if _ev([f"u{i}" for i in range(50)]).count("\n") == 6:
        print("   PASS: 6 examples plus a remainder line")
    else:
        print(f"   FAIL: {_ev([f'u{i}' for i in range(50)])!r}")
        ok = False

    print(f"\n{res['counts']}")
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# --------------------------------------------------------------------------- cli

def main() -> int:
    ap = argparse.ArgumentParser(description="Run the Tier 3 check registry over a crawl graph.")
    ap.add_argument("url", nargs="?", help="seed URL (uses the cached crawl when one exists)")
    ap.add_argument("--graph", help="read a graph JSON written by crawl.py --out instead")
    ap.add_argument("--area", action="append", choices=list(AREAS),
                    help="limit to one area (repeatable)")
    ap.add_argument("--max-pages", type=int, default=crawl.DEFAULT_MAX_PAGES)
    ap.add_argument("--refresh", action="store_true", help="recrawl instead of using the cache")
    ap.add_argument("--yes", action="store_true", help="confirm a large crawl")
    ap.add_argument("--json", action="store_true", help="full JSON instead of a text summary")
    ap.add_argument("--verdict", action="append", choices=["pass", "fail", "review", "unknown"],
                    help="only print rows with this verdict (repeatable)")
    ap.add_argument("--out", help="write the result JSON here")
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
            print(f"This would make up to {args.max_pages} requests to "
                  f"{crawl.origin_of(args.url)}. Re-run with --yes, or lower --max-pages.",
                  file=sys.stderr)
            return 2
        g = crawl.crawl(args.url, max_pages=args.max_pages, refresh=args.refresh)

    res = analyze(g, args.area)
    if args.out:
        Path(args.out).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        print(args.out, file=sys.stderr)

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0

    print(f"\n{res['origin']}  -  {res['pages_crawled']} pages crawled {res['crawled_at']}")
    if res["hit_cap"]:
        print("NOTE: the crawl hit its page cap; every count below is a floor, not a total.")
    print("  ".join(f"{k}: {v}" for k, v in res["counts"].items()))
    wanted = args.verdict or ["fail", "review", "unknown"]
    for area in dict.fromkeys(r["area"] for r in res["checks"]):
        rows = [r for r in res["checks"] if r["area"] == area and r["verdict"] in wanted]
        if not rows:
            continue
        print(f"\n== {area}")
        for r in rows:
            print(f"  [{r['verdict'].upper():7}] {r['check_id']}: {r['observed']}")
            print(f"            want: {r['threshold']}  ({r['source']})")
            for line in (r["evidence"] or "").splitlines()[:4]:
                print(f"            | {line}")
    print("\nNot connected:")
    for n in res["not_connected"]:
        print(f"  - {n.splitlines()[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

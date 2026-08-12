"""The free half of the Tier 4 audit: retrievability, entity, extractability, coverage,
mentions, links and local. Every threshold is owned by ../references/checks.md.

Structurally this is seo-technical's technical.py: one script, N areas, one _row() helper,
one JSON out with the same checks[] shape so push_sheet.py --from-results works across both.

Nothing here re-implements a sibling. robots parsing and the AI-bot matrix come from
seo-technical/crawl.py; page HTML from seo-onpage/fetch_page.py; SERPs from
seo-foundation/serp.py (cached, so re-runs cost nothing); schema and raw-vs-rendered are
READ from seo-technical's result JSON and cross-referenced, never recomputed.

The rule that governs every verdict: a check needing judgment returns `review` with the
evidence attached, and a check whose data source is absent returns `unknown` with the manual
route. Neither is ever collapsed into `pass`.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO = SKILL_DIR.parents[2]
for _p in ("seo-technical", "seo-onpage", "seo-foundation", "research", "web-scraper"):
    sys.path.insert(0, str(REPO / ".claude" / "skills" / _p / "scripts"))

RETRIEVAL_BOTS = ("OAI-SearchBot", "ChatGPT-User", "Claude-SearchBot", "PerplexityBot")
TRAINING_BOTS = ("GPTBot", "ClaudeBot", "CCBot")

ANSWER_UNIT_MIN, ANSWER_UNIT_MAX = 134, 167
ANSWER_UNIT_HARD_MAX = 250
ENTITY_DEF_WORDS = 60
MIN_STATISTICS = 3
MIN_PLATFORMS = 4
FRESH_DAYS = 90
LOCAL_REVIEWS_MIN, LOCAL_RATING_MIN = 50, 4.5

CREDENTIAL = re.compile(
    r"\b(CEO|CTO|CFO|COO|founder|co-founder|director|president|chief|head of|VP|vice president|"
    r"professor|Dr\.?|PhD|Ph\.D|MD|attorney|partner|principal|analyst|researcher|scientist|"
    r"engineer|editor|author of|owner|manager|specialist|consultant)\b", re.I)
PROPER_NAME = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z'\-]+){1,2}\b")
BACKREF = re.compile(
    r"^\s*(as (we|i) (discussed|mentioned|saw|noted)|as (mentioned|noted|described|explained) "
    r"(above|earlier|previously)|as above|this (approach|method|process|technique|strategy|way)\b|"
    r"these\b|those\b|it (is|was) (also|therefore|thus)\b|building on (this|that)\b|"
    r"the (former|latter)\b|such (a|an)\b)", re.I)
STAT = re.compile(r"(?<![\w.])(\d[\d,]*\.?\d*)\s*(%|percent|x\b|million|billion|k\b)|"
                  r"\b(\d[\d,]{2,})\b|\b\d+ (?:out )?of \d+\b", re.I)
SOCIAL_HOSTS = ("facebook.", "twitter.", "x.com", "instagram.", "linkedin.", "youtube.",
                "tiktok.", "pinterest.", "t.me", "wa.me", "threads.")
PLATFORM_MAP = {
    "linkedin.com": "LinkedIn", "crunchbase.com": "Crunchbase", "g2.com": "G2",
    "capterra.com": "Capterra", "clutch.co": "Clutch", "wikipedia.org": "Wikipedia",
    "wikidata.org": "Wikidata", "youtube.com": "YouTube", "reddit.com": "Reddit",
    "quora.com": "Quora", "trustpilot.com": "Trustpilot", "yelp.com": "Yelp",
    "glassdoor.com": "Glassdoor", "producthunt.com": "Product Hunt", "github.com": "GitHub",
    "tripadvisor.com": "Tripadvisor", "eventbrite.com": "Eventbrite", "bbb.org": "BBB",
}
STREET_ABBR = {"st": "street", "rd": "road", "ave": "avenue", "blvd": "boulevard",
               "dr": "drive", "ln": "lane", "hwy": "highway", "pkwy": "parkway",
               "ct": "court", "pl": "place", "ste": "suite", "apt": "apartment",
               "n": "north", "s": "south", "e": "east", "w": "west", "rte": "route"}

KG_ENABLE_URL = ("https://console.developers.google.com/apis/api/kgsearch.googleapis.com/"
                 "overview?project=368115608502")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _row(check_id: str, area: str, tier: int, observed, threshold: str, verdict: str,
         source: str, evidence: str = "") -> dict:
    assert verdict in ("pass", "fail", "review", "unknown"), verdict
    return {"check_id": check_id, "area": area, "tier": tier, "observed": observed,
            "threshold": threshold, "verdict": verdict, "source": source, "evidence": evidence}


# ---------------------------------------------------------------- 1. retrievability

def check_crawlers(origin: str) -> list[dict]:
    import crawl
    A, T = "Retrievability", 1
    out = []
    rb = crawl.fetch_robots(origin)
    declared = rb.get("ai_policy_declared") or {}

    blocked_ret = [b for b in RETRIEVAL_BOTS if declared.get(b) == "block"]
    allowed_train = [b for b in TRAINING_BOTS if declared.get(b) == "allow"]

    out.append(_row(
        "ai.policy_inverted", A, T,
        f"retrieval blocked: {blocked_ret or 'none'}; training allowed: {allowed_train or 'none'}",
        "never block retrieval while allowing training", "fail" if (blocked_ret and allowed_train) else "pass",
        "course/40 [practitioner]",
        (f"Blocks {', '.join(blocked_ret)} (how you get CITED) while allowing "
         f"{', '.join(allowed_train)} (training scrape). This forfeits the citations and keeps "
         "the scraping - the most expensive single misconfiguration in this tier."
         if (blocked_ret and allowed_train) else "No inversion detected.")))

    out.append(_row(
        "ai.retrieval_bots_allowed", A, T,
        f"{len(RETRIEVAL_BOTS) - len(blocked_ret)}/{len(RETRIEVAL_BOTS)} allowed",
        "OAI-SearchBot, ChatGPT-User, Claude-SearchBot, PerplexityBot all allowed",
        "fail" if blocked_ret else "pass", "course/40 [practitioner]",
        f"Disallowed: {', '.join(blocked_ret)}. These are the agents that fetch a page in order to "
        "cite it; blocking them removes the site from the answer, not from training."
        if blocked_ret else "No retrieval agent is disallowed."))

    named_train = {b: declared[b] for b in TRAINING_BOTS if b in declared}
    out.append(_row(
        "ai.training_bots_policy", A, T,
        named_train or "no explicit policy",
        "a deliberate decision, either way", "review", "course/40 [practitioner]",
        "A business decision, not a defect. Blocking indiscriminately opts out of AI answers while "
        "trying to opt out of training. The asymmetry that usually decides it: Googlebot crawls "
        "~5 pages per referred visitor; Anthropic's training crawler peaked at 70,900."))

    ge = declared.get("Google-Extended")
    out.append(_row(
        "ai.google_extended_documented", A, T, ge or "not declared",
        "a written decision", "review", "course/40 [practitioner]",
        "Gemini training opt-out. Does NOT affect Search ranking - most people assume it does."))

    dep = bool(rb.get("mentions_deprecated_anthropic_ai"))
    out.append(_row(
        "ai.no_deprecated_agents", A, T, "anthropic-ai present" if dep else "absent",
        "no `anthropic-ai`", "fail" if dep else "pass", "course/40 [practitioner]",
        "`anthropic-ai` is deprecated; the live agents are ClaudeBot and Claude-SearchBot. A config "
        "still citing it is issuing instructions nothing reads." if dep else ""))

    if declared:
        out.append(_row(
            "ai.robots_is_not_enforcement", A, T, f"{len(declared)} agent(s) declared",
            "enforcement is WAF, not robots.txt", "review", "course/40 [practitioner]",
            "robots.txt is a request, not a lock. Real enforcement is WAF or server-level IP rules, "
            "evaluated before robots.txt is ever read."))

    # llms.txt - absent is the pass
    try:
        r = crawl.fetch_raw(origin.rstrip("/") + "/llms.txt")
        present = r.get("status") == 200 and (r.get("bytes") or 0) > 0
        size = r.get("bytes") or 0
    except Exception:  # noqa: BLE001
        present, size = False, 0
    out.append(_row(
        "ai.llms_txt", A, T, f"present ({size} bytes)" if present else "absent",
        "no engine honors it", "review" if present else "pass", "course/40 [practitioner]",
        ("Present. Harmless - leave it, but do not bill for it and do not present it as an AI-search "
         "deliverable. No engine honors llms.txt; Google explicitly ignores it and has compared it to "
         "the keywords meta tag. Adoption is ~10% of domains. Removing it is also billable work with "
         "no benefit, so the correct action is none."
         if present else
         "Correctly absent. No engine honors llms.txt and there is no measured citation benefit.")))

    for cid, what in (("bing.indexed", "presence in Bing's index"),
                      ("bing.sitemap_submitted", "sitemap submitted to Bing")):
        out.append(_row(
            cid, A, T, "not connected", what, "unknown", "course/39 [practitioner]",
            "Needs the client's own free Bing Webmaster Tools account (10 minutes, OAuth). This is "
            "not a nicety: ChatGPT retrieves from Bing's index and ~90% of its citations come from "
            "pages ranked 21+ on Google, so Bing presence is a precondition for being cited there."))
    return out


# ---------------------------------------------------------------- 2. entity

def _wikidata(brand: str) -> list[dict]:
    q = urllib.parse.urlencode({"action": "wbsearchentities", "search": brand, "language": "en",
                                "format": "json", "limit": 5})
    req = urllib.request.Request("https://www.wikidata.org/w/api.php?" + q,
                                 headers={"User-Agent": "nexis-seo-authority-ai/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r).get("search", [])


def _kg(brand: str) -> tuple[list[dict] | None, str]:
    key = os.environ.get("PAGESPEED_API_KE") or os.environ.get("PAGESPEED_API_KEY")
    if not key:
        return None, "no Google API key in .env"
    u = "https://kgsearch.googleapis.com/v1/entities:search?" + urllib.parse.urlencode(
        {"query": brand, "limit": 3, "key": key})
    try:
        with urllib.request.urlopen(u, timeout=20) as r:
            return json.load(r).get("itemListElement", []), ""
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="ignore")[:200]
        if e.code == 403 or "SERVICE_DISABLED" in body:
            return None, f"API disabled on this Google Cloud project. Enable (free, 100k/day): {KG_ENABLE_URL}"
        return None, f"HTTP {e.code}: {body[:120]}"
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {e}"


def check_entity(brand: str, origin: str, schema_results: dict | None) -> list[dict]:
    A, T = "Entity", 2
    out = []

    try:
        hits = _wikidata(brand)
    except Exception as e:  # noqa: BLE001
        hits = None
        out.append(_row("entity.wikidata_qid", A, T, "lookup failed", "a Q-number exists",
                        "unknown", "course/40 [practitioner]", f"{type(e).__name__}: {e}"))
    if hits is not None:
        exact = [h for h in hits if h.get("label", "").strip().lower() == brand.strip().lower()]
        if not hits:
            out.append(_row("entity.wikidata_qid", A, T, "no match", "a Q-number exists", "fail",
                            "course/40 [practitioner]",
                            "No Wikidata entity. Wikidata is the fastest of the four recognition "
                            "paths (Wikidata, schema disambiguation, Knowledge Panel, Wikipedia) and "
                            "the only one that can be created directly."))
        elif exact and hits[0] is exact[0]:
            h = exact[0]
            out.append(_row("entity.wikidata_qid", A, T, f"{h['id']} - {h.get('description','')}",
                            "a Q-number exists and ranks first", "pass", "course/40 [practitioner]",
                            f"{h.get('concepturi','')}"))
        elif exact:
            h, top = exact[0], hits[0]
            out.append(_row("entity.wikidata_qid", A, T, f"{h['id']} (rank {hits.index(h)+1})",
                            "the right entity ranks first", "review", "course/40 [practitioner]",
                            f"An entity exists ({h['id']}, {h.get('description','')}) but "
                            f"'{top.get('label')}' ({top['id']}, {top.get('description','')}) ranks "
                            "above it for this name. Disambiguation risk: a retrieval system "
                            "resolving the name may attach to the wrong entity."))
        else:
            top = hits[0]
            out.append(_row("entity.wikidata_qid", A, T, f"no exact match; closest {top['id']}",
                            "a Q-number for THIS entity", "review", "course/40 [practitioner]",
                            f"Closest is '{top.get('label')}' - {top.get('description','')}. Confirm "
                            "by hand before claiming either presence or absence."))

    items, err = _kg(brand)
    if items is None:
        out.append(_row("entity.kg_recognized", A, T, "not connected", "a KGMID and confidence score",
                        "unknown", "course/40 [practitioner]", err))
    elif items:
        r0 = items[0]["result"]
        out.append(_row("entity.kg_recognized", A, T,
                        f"{r0.get('@id')} score={round(items[0].get('resultScore',0),1)}",
                        "recognised with a KGMID", "pass", "course/40 [practitioner]",
                        r0.get("name", "")))
    else:
        out.append(_row("entity.kg_recognized", A, T, "no match", "recognised with a KGMID", "fail",
                        "course/40 [practitioner]",
                        "Not in Google's Knowledge Graph. Weeks to months to establish, so start now."))

    # sameAs, read from seo-technical's schema output rather than re-derived
    same_as = []
    if schema_results:
        for c in schema_results.get("checks", []):
            if c.get("check_id") == "schema.organization_sameas":
                same_as = re.findall(r"https?://[^\s,\"']+", str(c.get("evidence", "")))
    if not schema_results:
        for cid, th in (("entity.sameas_present", "sameAs on Organization"),
                        ("entity.sameas_resolve", "every sameAs URL returns 200")):
            out.append(_row(cid, A, T, "not measured", th, "unknown",
                            "course/40 -> seo-technical [practitioner]",
                            "Run seo-technical/scripts/schema.py and pass --schema-results. Schema is "
                            "that skill's to own; duplicating it would let the two drift."))
    else:
        out.append(_row("entity.sameas_present", A, T, f"{len(same_as)} sameAs URL(s)",
                        "sameAs on Organization", "pass" if same_as else "fail",
                        "course/40 -> seo-technical [practitioner]",
                        "sameAs is how an Organization is tied to Wikidata, Crunchbase and LinkedIn. "
                        "Without it the entity has no declared identity to resolve against."
                        if not same_as else ", ".join(same_as[:8])))
        if same_as:
            import crawl
            bad = []
            for u in same_as[:12]:
                try:
                    r = crawl.fetch_raw(u)
                    if r.get("status") != 200:
                        bad.append(f"{u} -> {r.get('status')}")
                    elif len(r.get("redirect_chain") or []) > 0 and \
                            urllib.parse.urlparse(r.get("final_url", "")).path.strip("/") == "":
                        bad.append(f"{u} -> redirects to a homepage")
                except Exception as e:  # noqa: BLE001
                    bad.append(f"{u} -> {type(e).__name__}")
            out.append(_row("entity.sameas_resolve", A, T,
                            f"{len(same_as) - len(bad)}/{len(same_as)} resolve",
                            "every sameAs URL returns 200", "fail" if bad else "pass",
                            "course/40 [measured here]",
                            "; ".join(bad) if bad else "All resolve."))
    return out


# ---------------------------------------------------------------- 3. extractability

def _soup(html: str):
    from bs4 import BeautifulSoup
    s = BeautifulSoup(html or "", "html.parser")
    for t in s(["script", "style", "noscript", "template", "svg"]):
        t.decompose()
    return s


def _body(s):
    for sel in ("main", "article", '[role="main"]'):
        n = s.select_one(sel)
        if n:
            return n
    for t in s.find_all(["nav", "header", "footer", "aside"]):
        t.decompose()
    return s.body or s


def _sections(body) -> list[tuple[str, str]]:
    """(heading, text) pairs split on H2/H3."""
    out, cur_h, buf = [], "(intro)", []
    for el in body.find_all(["h1", "h2", "h3", "p", "li", "blockquote", "td"]):
        if el.name in ("h1", "h2", "h3"):
            if buf:
                out.append((cur_h, " ".join(buf).strip()))
            cur_h, buf = el.get_text(" ", strip=True), []
        else:
            t = el.get_text(" ", strip=True)
            if t:
                buf.append(t)
    if buf:
        out.append((cur_h, " ".join(buf).strip()))
    return out


def check_aeo(url: str, html: str, *, primary_query: str = "",
              render_results: dict | None = None) -> list[dict]:
    A, T = "Extractability", 4
    out = []
    s = _soup(html)
    body = _body(s)
    text = body.get_text(" ", strip=True)
    secs = _sections(body)

    # --- Princeton 1: expert quotes (+41%)
    quotes = body.find_all("blockquote")
    qtexts = [q.get_text(" ", strip=True) for q in quotes]
    qtexts += re.findall(r"[“\"]([^”\"]{40,400})[”\"]", text)
    attributed = []
    for q in qtexts:
        window = text[max(0, text.find(q[:40]) - 200): text.find(q[:40]) + len(q) + 200] or q
        if PROPER_NAME.search(window) and CREDENTIAL.search(window):
            attributed.append((PROPER_NAME.search(window).group(0),
                               CREDENTIAL.search(window).group(0)))
    if not qtexts:
        v, ev = "fail", ("No quotation found. The Princeton study measured a +41% citation "
                         "probability lift from adding expert quotes - the largest single effect in "
                         "the only peer-reviewed evidence in this field.")
    elif attributed:
        v, ev = "review", ("Quotation(s) with an apparent attribution: " +
                           "; ".join(f"{n} ({c})" for n, c in attributed[:4]) +
                           ". Confirm the person and credential are real and named, not implied.")
    else:
        v, ev = "review", (f"{len(qtexts)} quotation(s) but no adjacent named person with a "
                           "credential. 'Experts say' is exactly what the study distinguishes from "
                           "an attributable quote.")
    out.append(_row("aeo.expert_quote", A, T, f"{len(qtexts)} quote(s), {len(attributed)} attributed",
                    "1+ quote from a named person with a credential", v,
                    "course/37 [peer-reviewed] +41%", ev))

    # --- Princeton 2: statistics (+30%)
    stats = STAT.findall(text)
    sourced = 0
    for sent in re.split(r"(?<=[.!?])\s+", text):
        if STAT.search(sent) and (re.search(r"\b(according to|per |source:|study|survey|report|"
                                            r"research|data from)\b", sent, re.I)):
            sourced += 1
    n_stats = len(stats)
    if n_stats < MIN_STATISTICS:
        v, ev = "fail", (f"{n_stats} specific number(s); the threshold is {MIN_STATISTICS}. "
                         "Adding statistics measured a +30% citation lift.")
    elif sourced == 0:
        v, ev = "review", (f"{n_stats} numbers, none in a sentence naming a source. Where a number "
                           "came from matters as much as the number - an unsourced figure is not "
                           "safely repeatable by a synthesis engine.")
    else:
        v, ev = "pass", f"{n_stats} numbers, {sourced} in a sentence naming a source."
    out.append(_row("aeo.statistics", A, T, f"{n_stats} numbers, {sourced} sourced",
                    f"{MIN_STATISTICS}+ specific numbers, each sourced", v,
                    "course/37 [peer-reviewed] +30%", ev))

    # --- Princeton 3: inline citations (+30%)
    host = urllib.parse.urlparse(url).netloc.replace("www.", "")
    outbound = []
    for a in body.find_all("a", href=True):
        h = a["href"]
        if not h.startswith("http"):
            continue
        d = urllib.parse.urlparse(h).netloc.replace("www.", "")
        if d and d != host and not any(sh in d for sh in SOCIAL_HOSTS):
            outbound.append(h)
    out.append(_row("aeo.inline_citations", A, T, f"{len(set(outbound))} outbound editorial link(s)",
                    "outbound links to the source of each claim",
                    "fail" if not outbound else "review", "course/37 [peer-reviewed] +30%",
                    ("No outbound editorial links. Inline citation measured a +30% lift. The instinct "
                     "being corrected here is link-equity hoarding: the equity protected is worth "
                     "less than the citation forgone."
                     if not outbound else f"e.g. {', '.join(sorted(set(outbound))[:5])}")))

    # --- structure
    opening = " ".join(text.split()[:ENTITY_DEF_WORDS])
    out.append(_row("aeo.answer_first", A, T, "see evidence",
                    "first sentence states the conclusion", "review", "course/37 [practitioner]",
                    f"Opening {ENTITY_DEF_WORDS} words: \"{opening[:400]}\". A script cannot tell a "
                    "conclusion from a preamble - read it and decide."))
    out.append(_row("aeo.entity_defined_early", A, T, f"{len(text.split())} words on page",
                    f"main entity defined in the first 40-{ENTITY_DEF_WORDS} words", "review",
                    "course/37 [practitioner]", f"Opening: \"{opening[:300]}\""))

    lens = [(h, len(t.split())) for h, t in secs if t]
    too_long = [(h, n) for h, n in lens if n > ANSWER_UNIT_HARD_MAX]
    in_band = [n for _, n in lens if ANSWER_UNIT_MIN <= n <= ANSWER_UNIT_MAX]
    if not lens:
        v, ev = "unknown", "No headed sections found to segment."
    elif too_long:
        v = "fail"
        ev = (f"{len(too_long)} section(s) over {ANSWER_UNIT_HARD_MAX} words, longest "
              f"\"{too_long[0][0][:60]}\" at {max(n for _, n in too_long)}. A unit that long does not "
              "survive extraction as a standalone answer.")
    elif in_band:
        v, ev = "pass", f"{len(in_band)}/{len(lens)} sections in the {ANSWER_UNIT_MIN}-{ANSWER_UNIT_MAX} band."
    else:
        v = "review"
        ev = (f"No section in the {ANSWER_UNIT_MIN}-{ANSWER_UNIT_MAX} word band "
              f"(sizes: {sorted(n for _, n in lens)[:12]}). Under the band a section is a stub, not a "
              "self-contained answer.")
    out.append(_row("aeo.answer_unit_length", A, T, f"{len(lens)} sections",
                    f"{ANSWER_UNIT_MIN}-{ANSWER_UNIT_MAX} words between headings", v,
                    "course/36, 37 [practitioner]", ev))

    backs = [h for h, t in secs if BACKREF.match(t or "")]
    out.append(_row("aeo.unit_standalone", A, T, f"{len(backs)} section(s) open with a back-reference",
                    "no section opens by referring to another", "fail" if backs else "pass",
                    "course/36 [measured here]",
                    (f"Sections opening with a back-reference: {backs[:5]}. Pulled out alone, such a "
                     "section is incoherent, and being pulled out alone is exactly what retrieval does."
                     if backs else "Every section opens self-contained.")))

    heads = [h for h, _ in secs if h != "(intro)"]
    qh = [h for h in heads if h.strip().endswith("?") or
          re.match(r"^(what|why|how|when|where|who|which|is|are|can|do|does|should)\b", h.strip(), re.I)]
    out.append(_row("aeo.question_headings", A, T,
                    f"{len(qh)}/{len(heads)} headings are question-shaped",
                    "one question per heading, phrased as asked", "review",
                    "course/37 [practitioner]",
                    "Headings are strong retrieval anchors; one matching a fan-out sub-query is a "
                    f"direct hit. Question-shaped: {qh[:5]}"))

    tables = body.find_all("table")
    comparative = bool(re.search(r"\b(vs\.?|versus|best|compare|comparison|alternative)\b",
                                 primary_query or "", re.I))
    if tables:
        v, ev = "review", f"{len(tables)} table(s) present. Confirm one is a genuine comparison."
    elif comparative:
        v, ev = "fail", (f"No table, and the target query ({primary_query!r}) is comparative. A "
                         "comparison table is one of the most extractable formats that exists - an "
                         "engine answering 'X vs Y' can lift a well-built one nearly verbatim.")
    else:
        v, ev = "review", "No table. Add one if the topic supports a genuine comparison."
    out.append(_row("aeo.comparison_table", A, T, f"{len(tables)} table(s)",
                    "a comparison table where the topic supports one", v,
                    "course/37 [practitioner]", ev))

    if render_results:
        rr = [c for c in render_results.get("checks", []) if c.get("check_id") == "render.comparison"]
        v = rr[0].get("verdict", "unknown") if rr else "unknown"
        ev = rr[0].get("evidence", "") if rr else "no render.comparison row found"
        out.append(_row("aeo.not_js_dependent", A, T, rr[0].get("observed") if rr else "not measured",
                        "body content present in raw HTML", v,
                        "course/26 -> seo-technical [practitioner]", ev))
    else:
        out.append(_row("aeo.not_js_dependent", A, T, "not measured",
                        "body content present in raw HTML", "unknown",
                        "course/26 -> seo-technical [practitioner]",
                        "Run seo-technical/scripts/render_diff.py and pass --render-results. This is "
                        "the highest-consequence check in the tier and it belongs to a sibling: a "
                        "client-rendered site can rank fine in Google and be structurally invisible to "
                        "ChatGPT and Perplexity."))
    return out


# ---------------------------------------------------------------- 4. coverage

def check_coverage(origin: str, queries: list[str], headings: list[str]) -> list[dict]:
    A, T = "Coverage", 3
    out = []
    if not queries:
        return [_row("coverage.paa_answered", A, T, "no queries supplied",
                     "every PAA question has an answering heading", "unknown",
                     "course/36 [practitioner]",
                     "Pass --queries or a seo-foundation keyword map to enable the fan-out proxy.")]
    import serp
    paa: list[str] = []
    for q in queries[:12]:
        try:
            d = serp.fetch(q)
            paa += [p.get("question", "") for p in (d.get("peopleAlsoAsk") or [])]
        except Exception:  # noqa: BLE001
            continue
    paa = [p for p in dict.fromkeys(paa) if p]
    hl = [h.lower() for h in headings]

    def answered(question: str) -> bool:
        toks = [w for w in re.findall(r"[a-z]{4,}", question.lower())][:6]
        if not toks:
            return False
        return any(sum(t in h for t in toks) >= max(2, len(toks) // 2) for h in hl)

    unanswered = [p for p in paa if not answered(p)]
    covered = len(paa) - len(unanswered)
    ratio = covered / len(paa) if paa else 0
    out.append(_row("coverage.paa_answered", A, T, f"{covered}/{len(paa)} PAA questions answered",
                    "an answering heading for each", "review" if paa else "unknown",
                    "course/36 [measured here]",
                    ("Unanswered - this list is the content queue: " + "; ".join(unanswered[:12]))
                    if unanswered else "Every observed PAA question has a plausible answering heading."))
    out.append(_row("coverage.subquery_ratio", A, T, f"{ratio:.0%} of observed sub-questions",
                    "80%+ topical coverage", "review", "course/36 [practitioner]",
                    "Sites with 80%+ topical coverage of their domain retain 85.4% of AI visibility. "
                    "This is a free proxy from PAA, not the full fan-out: fan-out is 5-11 sub-queries "
                    "typically and is not directly observable."))
    return out


# ---------------------------------------------------------------- 5. mentions

def check_mentions(brand: str, domain: str, *, gl: str = "us", max_pages: int = 25) -> list[dict]:
    A = "Mentions and platforms"
    out, mentions, platforms = [], [], {}
    import serp
    from fetch_page import fetch as fetch_pg

    dom = domain.replace("www.", "").strip("/")
    # course/33 discovery is `"brand" -site:domain`. Two Serper quirks, both verified 2026-08-09:
    # a quoted phrase CONTAINING AN APOSTROPHE is rejected with "Query pattern not allowed for
    # free accounts" (the message blames the plan, but `O'Malley's Pub` unquoted and
    # `"O'Malley's Pub"` quoted both succeed - it is the combination), and `-site:` is not
    # worth spending a pattern allowance on. So: quote only when it is safe to, and drop the
    # client's own host in Python.
    q = f'"{brand}"' if "'" not in brand and '"' not in brand else brand
    try:
        d = serp.fetch(q, gl=gl, num=30)
        results = [r for r in (d.get("organic") or [])
                   if dom not in (r.get("link") or "")]
    except Exception as e:  # noqa: BLE001
        return [_row("mention.unlinked_count", A, 5, "search unavailable",
                     "every unlinked mention reclaimed", "unknown", "course/34 [practitioner]",
                     f"Serper call failed: {type(e).__name__}: {e}. Re-run when the key has "
                     "credit; nothing here is inferred from a failed search.")]

    for r in results[:max_pages]:
        u = r.get("link") or ""
        host = urllib.parse.urlparse(u).netloc.replace("www.", "")
        for k, name in PLATFORM_MAP.items():
            if host.endswith(k):
                platforms.setdefault(name, u)
        try:
            pg = fetch_pg(u)
            html = pg.get("html") or ""
        except Exception:  # noqa: BLE001
            continue
        if not html:
            continue
        linked = bool(re.search(rf'href=["\'][^"\']*{re.escape(dom)}', html, re.I))
        url_text = dom.lower() in _soup(html).get_text(" ", strip=True).lower()
        mentions.append({"url": u, "title": r.get("title", ""), "host": host,
                         "linked": linked, "url_mentioned_unlinked": url_text and not linked,
                         "snippet": (r.get("snippet") or "")[:300]})

    unlinked = [m for m in mentions if not m["linked"]]
    out.append(_row("mention.unlinked_count", A, 5,
                    f"{len(unlinked)} unlinked of {len(mentions)} checked",
                    "every unlinked mention reclaimed", "review", "course/33, 34 [practitioner]",
                    "A work queue, not a defect. Reclamation converts at 30-50%, the highest of any "
                    "link tactic (broken-link building is 5-15%). Ask in three sentences naming the "
                    "exact sentence, never a template. Top: " +
                    "; ".join(m["host"] for m in unlinked[:8])))

    names = sorted(platforms)
    out.append(_row("mention.platform_count", A, 5, f"{len(names)} platform(s): {', '.join(names) or 'none'}",
                    f"{MIN_PLATFORMS}+ third-party platforms",
                    "pass" if len(names) >= MIN_PLATFORMS else "fail",
                    "course/34 [practitioner, single vendor]",
                    "Brands present on four or more third-party platforms are 2.8x more likely to be "
                    "cited by ChatGPT. The own site is the anchor, not one of the four. Shortlist: "
                    "LinkedIn, Crunchbase, G2/Capterra/Clutch, Wikipedia or Wikidata, vetted industry "
                    "directories, YouTube/podcasts, Reddit/Quora."))
    out.append(_row("mention.branded_impressions", A, 5, "not connected",
                    "tracked monthly, same day each month", "unknown", "course/34 [practitioner]",
                    "Search Console: Performance, filter Query contains the brand, 28-day rolling. "
                    "The cheapest honest measure of whether off-page work is doing anything, and no "
                    "credential exists here."))

    # links - the honest tier
    for cid, th in (("link.referring_domains", "baseline the referring-domain count"),
                    ("link.gap_vs_competitor", "domains competitors have and you do not"),
                    ("link.dr_floor", "DR 30+, 1,000+ monthly visits, Toxic Score under 45"),
                    ("link.anchor_distribution", "exact-match anchors under ~20%"),
                    ("link.risky_patterns", "no PBN, reciprocal ring or marketplace footprint")):
        out.append(_row(cid, "Links", 6, "no free source", th, "unknown",
                        "course/32 [practitioner]",
                        "No free backlink index exists. This skill produces a prospect list, never a "
                        "qualified one. Route: Ahrefs Webmaster Tools (free, owned domains only) or "
                        "Search Console > Links for your own profile; a paid tool for competitors."))
    out.append(_row("link.reclamation_queue", "Links", 6, f"{len(unlinked)} candidate(s)",
                    "reclaim before pursuing anything new", "review", "course/33 [practitioner]",
                    "The one link action available without a backlink index, and the highest-converting "
                    "one that exists. Branded mentions correlate with AI Overview citation at r=0.664 "
                    "against r=0.218 for backlinks - roughly 3x - so this is not a consolation prize. "
                    "Correlational, never causal."))
    return out, mentions, platforms  # type: ignore[return-value]


# ---------------------------------------------------------------- 6. local

def normalize_nap(s: str) -> str:
    """Byte-identical is the standard, so normalisation exists to DETECT variants, not bless them."""
    s = (s or "").lower()
    s = re.sub(r"[.,#]", " ", s)
    toks = [STREET_ABBR.get(t, t) for t in s.split()]
    return " ".join(toks).strip()


def check_local(brand: str, *, applicable: bool, city: str = "", gl: str = "us",
                nap_variants: list[str] | None = None) -> list[dict]:
    A, T = "Local", 7
    if not applicable:
        return [_row("local.applicable", A, T, "not applicable", "a location or service area",
                     "pass", "course/35 [practitioner]",
                     "No physical location or service area. Recorded rather than omitted, so nobody "
                     "implements local work later without asking whether it applies.")]
    out = [_row("local.applicable", A, T, "applicable", "a location or service area", "pass",
                "course/35 [practitioner]",
                "Local applies, which promotes this area to tier 2: 46% of all Google searches carry "
                "local intent, and GBP plus reviews is roughly half of map pack weighting.")]

    rating = reviews = None
    cat = ""
    try:
        import serp
        d = serp.fetch(f"{brand} {city}".strip(), gl=gl)
        places = (d.get("places") or []) + ([d["knowledgeGraph"]] if d.get("knowledgeGraph") else [])
        for p in places:
            rating = rating or p.get("rating")
            reviews = reviews or p.get("ratingCount") or p.get("reviews")
            cat = cat or p.get("category") or p.get("type") or ""
    except Exception:  # noqa: BLE001
        pass

    out.append(_row("local.gbp_primary_category", A, T, cat or "not observed",
                    "the most specific accurate option", "review", "course/35 [practitioner]",
                    "The strongest single signal in local SEO and one dropdown to change. "
                    "'Personal Injury Attorney' beats 'Lawyer'. Check this first, every time."))
    out.append(_row("local.reviews_volume", A, T, reviews if reviews is not None else "not observed",
                    f"{LOCAL_REVIEWS_MIN}+ in 12 months",
                    "unknown" if reviews is None else ("pass" if reviews >= LOCAL_REVIEWS_MIN else "fail"),
                    "course/35 [practitioner, single vendor]",
                    "50+ reviews in 12 months reported 3x more likely to appear in AI recommendations."))
    out.append(_row("local.reviews_rating", A, T, rating if rating is not None else "not observed",
                    f"{LOCAL_RATING_MIN}+",
                    "unknown" if rating is None else ("pass" if float(rating) >= LOCAL_RATING_MIN else "fail"),
                    "course/35 [practitioner, single vendor]",
                    "A 4.5+ rating roughly doubles citation frequency in AI recommendations."))
    out.append(_row("local.reviews_velocity", A, T, "not measured", "2-4 new reviews per week",
                    "unknown", "course/35 [practitioner]",
                    "Velocity beats total: 5-15/month sustained over six months is reported to move a "
                    "business 5-10 map pack positions. Needs dated review data."))

    variants = nap_variants or []
    if len(variants) >= 2:
        norm = {normalize_nap(v) for v in variants}
        out.append(_row("local.nap_consistent", A, T, f"{len(variants)} listing(s), {len(norm)} distinct",
                        "byte-identical everywhere", "pass" if len(norm) == 1 else "review",
                        "course/35 [practitioner]",
                        ("Variants: " + " | ".join(variants[:6]) +
                         ". 'St.' vs 'Street', a suite number present in one listing and absent in "
                         "another, or two phone numbers all suppress ranking.")
                        if len(norm) > 1 else "All listings normalise identically."))
    else:
        out.append(_row("local.nap_consistent", A, T, "not measured", "byte-identical everywhere",
                        "unknown", "course/35 [practitioner]",
                        "Pass --nap to compare listings. Fix order: Google Business Profile, Bing "
                        "Places, Apple Maps, Yelp, Facebook, then the aggregators (Data Axle, "
                        "Localeze), then industry directories. Citations are only ~6% of weighting."))
    out.append(_row("local.gbp_completeness", A, T, "not connected",
                    "every field; 1-3 Posts weekly; 8-12 Q&A; 10-25 photos", "unknown",
                    "course/35 [practitioner]",
                    "Needs GBP access. Do not quote the '100+ photos, 520% more calls' figure - it "
                    "traces to vendor research citing Google, not to a Google publication."))
    out.append(_row("local.three_surfaces", A, T, "map pack + local organic only",
                    "map pack, local organic and AI recommendation, separately", "review",
                    "course/35 [practitioner]",
                    "The third surface needs aivis.py. They are different systems and a business can "
                    "win one while losing another."))
    return out


# ---------------------------------------------------------------- orchestrator

def analyze(origin: str, *, brand: str, areas: list[str], pages: list[str],
            primary_query: str = "", queries: list[str] | None = None,
            schema_results: dict | None = None, render_results: dict | None = None,
            local: bool = False, city: str = "", nap: list[str] | None = None,
            gl: str = "us") -> dict:
    import crawl
    from fetch_page import fetch as fetch_pg

    checks: list[dict] = []
    extra: dict = {}
    domain = urllib.parse.urlparse(origin).netloc.replace("www.", "")

    if "crawlers" in areas:
        checks += check_crawlers(origin)
    if "entity" in areas:
        checks += check_entity(brand, origin, schema_results)
    if "aeo" in areas:
        for u in (pages or [origin]):
            try:
                pg = fetch_pg(u)
                rows = check_aeo(u, pg.get("html") or "", primary_query=primary_query,
                                 render_results=render_results)
                for r in rows:
                    r["observed"] = f"[{u}] {r['observed']}"
                checks += rows
            except Exception as e:  # noqa: BLE001
                checks.append(_row("aeo.fetch", "Extractability", 4, f"{u} unreachable",
                                   "page fetchable", "unknown", "course/37",
                                   f"{type(e).__name__}: {e}"))
    if "coverage" in areas:
        heads: list[str] = []
        try:
            g = crawl.crawl(origin, max_pages=40, respect_robots=True)
            for p in g.get("pages", {}).values():
                heads += (p.get("h1") or [])
                heads.append(p.get("title") or "")
        except Exception:  # noqa: BLE001
            pass
        checks += check_coverage(origin, queries or ([primary_query] if primary_query else []), heads)
    if "mentions" in areas:
        res = check_mentions(brand, domain, gl=gl)
        rows, mentions, platforms = res if isinstance(res, tuple) else (res, [], {})
        checks += rows
        extra["mentions"] = mentions
        extra["platforms"] = platforms
    if "local" in areas:
        checks += check_local(brand, applicable=local, city=city, gl=gl, nap_variants=nap)

    counts: dict[str, int] = {}
    for c in checks:
        counts[c["verdict"]] = counts.get(c["verdict"], 0) + 1
    return {"origin": origin, "brand": brand, "generated_at": _now(), "areas": areas,
            "checks": checks, "counts": counts,
            "not_connected": sorted({c["check_id"] for c in checks if c["verdict"] == "unknown"}),
            "reading_note": ("`review` means a judgment call with the evidence attached; `unknown` "
                             "means the data source is absent. Neither is a pass."),
            **extra}


# ---------------------------------------------------------------- selftest

def _selftest() -> None:
    print("authority selftest")

    # 1. Princeton quote detector - the finding a naive implementation flattens
    good = ('<main><h2>Q</h2><blockquote>"Retrieval changed everything about how we publish."'
            '</blockquote><p>said Jane Doe, CTO of Acme.</p></main>')
    r = {c["check_id"]: c for c in check_aeo("https://a.com", good)}
    assert r["aeo.expert_quote"]["verdict"] == "review", r["aeo.expert_quote"]
    assert "Jane Doe" in r["aeo.expert_quote"]["evidence"]
    vague = '<main><h2>Q</h2><p>Experts say retrieval changed everything.</p></main>'
    r2 = {c["check_id"]: c for c in check_aeo("https://a.com", vague)}
    assert r2["aeo.expert_quote"]["verdict"] == "fail", "'experts say' must not pass as a quote"
    print("  ok  expert quote: attributed -> review, 'experts say' -> fail")

    # 2. answer-unit banding
    long_sec = "<main><h2>A</h2><p>" + "word " * 400 + "</p></main>"
    assert {c["check_id"]: c for c in check_aeo("https://a.com", long_sec)}[
        "aeo.answer_unit_length"]["verdict"] == "fail"
    ok_sec = "<main><h2>A</h2><p>" + "word " * 150 + "</p></main>"
    assert {c["check_id"]: c for c in check_aeo("https://a.com", ok_sec)}[
        "aeo.answer_unit_length"]["verdict"] == "pass"
    print(f"  ok  answer units: 400w -> fail, 150w -> pass (band {ANSWER_UNIT_MIN}-{ANSWER_UNIT_MAX})")

    # 3. back-reference detection
    br = "<main><h2>A</h2><p>As we discussed earlier, this approach works.</p></main>"
    assert {c["check_id"]: c for c in check_aeo("https://a.com", br)}[
        "aeo.unit_standalone"]["verdict"] == "fail"
    print("  ok  back-reference opener -> fail")

    # 4. comparison table only fails when the query is comparative
    q = {c["check_id"]: c for c in check_aeo("https://a.com", "<main><p>x</p></main>",
                                             primary_query="best crm vs hubspot")}
    assert q["aeo.comparison_table"]["verdict"] == "fail"
    q2 = {c["check_id"]: c for c in check_aeo("https://a.com", "<main><p>x</p></main>",
                                              primary_query="what is a crm")}
    assert q2["aeo.comparison_table"]["verdict"] == "review"
    print("  ok  comparison table: comparative query -> fail, informational -> review")

    # 5. inline citations ignore nav/social, count editorial
    html = ('<main><p>x <a href="https://ref.org/a">src</a> '
            '<a href="https://facebook.com/me">fb</a> <a href="/int">int</a></p></main>')
    c = {x["check_id"]: x for x in check_aeo("https://a.com", html)}["aeo.inline_citations"]
    assert c["observed"].startswith("1 "), c["observed"]
    print("  ok  inline citations: social and internal excluded")

    # 6. NAP normaliser detects the variant course/35 names
    assert normalize_nap("123 Main St., Suite 4") == normalize_nap("123 Main Street Suite 4")
    assert normalize_nap("123 Main St") != normalize_nap("124 Main St")
    print("  ok  NAP: 'St.' == 'Street', different numbers stay different")

    # 7. not-applicable local is recorded, not omitted
    rows = check_local("X", applicable=False)
    assert len(rows) == 1 and rows[0]["verdict"] == "pass"
    print("  ok  local not applicable -> recorded as pass, not dropped")

    # 8. every row is well-formed
    for row in (check_aeo("https://a.com", good) + check_local("X", applicable=False)):
        assert set(row) >= {"check_id", "area", "tier", "observed", "threshold", "verdict",
                            "source", "evidence"}, row
        assert row["verdict"] in ("pass", "fail", "review", "unknown")
    print("  ok  row shape and verdict vocabulary")
    print("ALL PASS")


def main() -> None:
    ap = argparse.ArgumentParser(description="Tier 4 authority and AI-visibility checks (the free half).")
    ap.add_argument("origin", nargs="?", help="site origin, e.g. https://acme.com")
    ap.add_argument("--brand", default="")
    ap.add_argument("--areas", default="crawlers,entity,aeo,coverage,mentions",
                    help="crawlers,entity,aeo,coverage,mentions,local")
    ap.add_argument("--pages", default="", help="comma separated URLs for the aeo pass")
    ap.add_argument("--primary-query", default="")
    ap.add_argument("--queries", default="", help="comma separated, for the coverage pass")
    ap.add_argument("--schema-results", help="seo-technical schema.py JSON")
    ap.add_argument("--render-results", help="seo-technical render_diff.py JSON")
    ap.add_argument("--local", action="store_true")
    ap.add_argument("--city", default="")
    ap.add_argument("--nap", default="", help="pipe separated listing strings")
    ap.add_argument("--gl", default="us")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        _selftest()
        return
    if not a.origin:
        raise SystemExit("origin required (or --selftest)")
    if not a.brand:
        raise SystemExit("--brand required: entity and mention checks are brand-keyed")

    def _load(p):
        return json.loads(Path(p).read_text(encoding="utf-8")) if p else None

    res = analyze(
        a.origin, brand=a.brand,
        areas=[s.strip() for s in a.areas.split(",") if s.strip()],
        pages=[s.strip() for s in a.pages.split(",") if s.strip()],
        primary_query=a.primary_query,
        queries=[s.strip() for s in a.queries.split(",") if s.strip()],
        schema_results=_load(a.schema_results), render_results=_load(a.render_results),
        local=a.local, city=a.city,
        nap=[s.strip() for s in a.nap.split("|") if s.strip()], gl=a.gl)

    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"wrote {a.out}", file=sys.stderr)
    else:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    print(f"[authority] {res['counts']}", file=sys.stderr)


if __name__ == "__main__":
    main()

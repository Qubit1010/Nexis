#!/usr/bin/env python3
"""Build the strategic-foundation corpus: 8 deep research passes -> a tiered sources.json.

Two subcommands, both idempotent:

    python gather.py run       # the 8 deep passes -> passes/<key>.json  (resume-safe)
    python gather.py extract   # passes/*.json -> a deduped, tiered, capped sources.json
    python gather.py           # run, then extract

Lifted from .claude/skills/seo-advisor/_research/{run_passes,build_corpus}.py and
collapsed into one file. The entire NotebookLM half of build_corpus.py (import,
merge_uuids, synthesize, find_exe) is deleted rather than ported: that account's auth
has been dead since 2026-07-14, so per research-backed-skills.md the corpus is built
straight from the in-repo `research` skill and the live fallback is self-research.

Evidence rules that survived the port, each of which was a real bug in seo-advisor's
first run:
  - no blanket ".gov = confirmed" (it admitted a legislative calendar as a top source)
  - a topic-token guard so an off-topic PDF cannot ride in on a trusted domain
  - a per-domain cap so one consultancy blog cannot dominate the corpus
  - confirmed-tier sources jump the global cap
  - indices are stable across refreshes, so existing [sN] citations never repoint

UNSANDBOXED: api.exa.ai and friends fail when sandboxed.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

RESEARCH_DIR = Path(__file__).resolve().parent
PASSES_DIR = RESEARCH_DIR / "passes"
REPO_ROOT = RESEARCH_DIR.parents[3]
RESEARCH_PY = REPO_ROOT / ".claude" / "skills" / "research" / "scripts" / "research.py"

# Keep the corpus to what 8 passes can honestly support. There is no NotebookLM
# 100-source-per-notebook ceiling to work around here, so this is purely a
# signal-to-noise cap.
SOURCE_CAP = 250
PER_DOMAIN_CAP = 5

# Primary data or peer-reviewed research, versus a consultancy making a case for its
# own methodology. Business strategy is overwhelmingly practitioner-tier and the
# corpus has to preserve that rather than launder McKinsey's blog into evidence.
# Deliberately NOT here: hbr.org (mostly practitioner essays), and any .gov blanket
# rule. Statistical agencies are listed individually because they publish the market
# data this skill's sizing sections depend on.
CONFIRMED_DOMAINS = {
    # peer-reviewed / academic press
    "jstor.org", "sciencedirect.com", "springer.com", "nature.com", "wiley.com",
    "tandfonline.com", "sagepub.com", "journals.sagepub.com", "cambridge.org",
    "oup.com", "academic.oup.com", "informs.org", "pubsonline.informs.org",
    "aeaweb.org", "nber.org", "ssrn.com", "papers.ssrn.com", "arxiv.org",
    "doi.org", "pnas.org", "jstor.com",
    # Added after the q1 pass surfaced a peer-reviewed vision-and-performance study
    # on PMC that would otherwise have been tiered practitioner. Emerald and AoM are
    # the two biggest management-journal publishers and this corpus is management
    # research, so their absence was a real gap.
    "ncbi.nlm.nih.gov", "pmc.ncbi.nlm.nih.gov", "pubmed.ncbi.nlm.nih.gov",
    "emerald.com", "emeraldinsight.com", "aom.org", "journals.aom.org",
    # primary statistical and regulatory data
    "census.gov", "bls.gov", "sba.gov", "federalreserve.gov", "sec.gov",
    "bea.gov", "worldbank.org", "data.worldbank.org", "oecd.org", "imf.org",
    "eurostat.ec.europa.eu", "ec.europa.eu", "ons.gov.uk", "statcan.gc.ca",
    # Research institutes that are themselves the primary source for a framework
    # this corpus leans on. Enumerated, not inferred from the .edu suffix.
    "isc.hbs.edu",
}

# Somebody's opinion with no editorial process. These crowded out primary sources in
# seo-advisor's first extract run. Medium and Substack are here despite carrying real
# strategy writing: neither has an editorial process, and both republish the same
# frameworks the primary sources already cover.
JUNK_DOMAINS = {
    "facebook.com", "linkedin.com", "twitter.com", "x.com", "instagram.com",
    "pinterest.com", "tiktok.com", "quora.com", "medium.com", "reddit.com",
    "youtube.com", "youtu.be", "slideshare.net", "scribd.com", "issuu.com",
    "substack.com", "coursehero.com", "studocu.com",
    # User-generated study cards and cram notes. The q1 pass ranked a Quizlet study
    # guide 10th, above several primary sources.
    "quizlet.com", "chegg.com", "cliffsnotes.com", "bartleby.com",
}

MIRROR_SUFFIXES = (".google.cn", ".google.co.jp", ".google.de", ".google.fr")

# A source has to be plausibly about business strategy. Without this guard a trusted
# statistical domain admits anything it happens to publish, which is how seo-advisor
# ended up ranking a US House legislative schedule as a top-tier source.
TOPIC_TOKENS = (
    "strategy", "strategic", "mission", "vision", "values", "purpose",
    "market", "tam", "sam", "som", "sizing", "segment", "customer", "icp",
    "persona", "jobs-to-be-done", "jobs to be done", "jtbd", "audience",
    "competit", "porter", "five forces", "pestel", "swot", "moat", "differenti",
    "positioning", "value proposition", "uvp", "usp", "brand",
    "business model", "canvas", "revenue", "pricing", "monetiz", "unit economics",
    "margin", "cac", "ltv", "churn", "cohort", "forecast", "financial",
    "cost structure", "runway", "burn", "funding", "fundrais", "valuation",
    "startup", "founder", "smb", "small business", "venture", "growth",
    "product-market fit", "product market fit", "pmf", "go-to-market",
    "business plan", "planning", "okr", "kpi", "benchmark", "industry",
    # Broad catch-alls. The guard exists to reject a document that rode in on a
    # trusted domain while being clearly off-subject (a legislative calendar), not
    # to be a precision filter. Without plain "business" it rejected
    # census.gov/data/business-formation, which is exactly the primary market data
    # the sizing sections depend on.
    "business", "entrepreneur", "commerc", "econom",
)

SUFFIX = (" Give specific numbers, named frameworks, benchmark ranges and concrete "
          "steps, and cite sources. Distinguish peer-reviewed evidence from "
          "consultant opinion. Where the sources disagree, or where a number comes "
          "only from a vendor's own survey, say so explicitly.")

# One deep pass per section of the strategic foundation. Q8 is what review mode runs
# on, so it targets diagnosis and failure modes rather than construction.
QUERIES = {
    "q1_mission_vision_values": (
        "Mission, vision and values statements: whether they measurably affect firm "
        "performance, employee behaviour and decision making, the empirical research "
        "on mission statement effectiveness, what distinguishes a mission from a "
        "vision from a purpose, how to actually write one, and why most corporate "
        "values statements are interchangeable wallpaper that changes nothing."
    ),
    "q2_market_research_sizing": (
        "Market research and market sizing methodology: how to calculate TAM, SAM and "
        "SOM, top-down versus bottom-up sizing, where the input data actually comes "
        "from, primary versus secondary research methods for a small business, the "
        "most common market sizing errors and inflated numbers, and how investors "
        "actually judge a market size claim."
    ),
    "q3_target_customer_icp": (
        "Defining a target customer: ideal customer profile construction, market "
        "segmentation methods, jobs-to-be-done theory and how to run JTBD interviews, "
        "buyer personas and the evidence on whether they work, firmographic versus "
        "behavioural segmentation, and which customer attributes actually predict "
        "retention and fit versus which are demographic decoration."
    ),
    "q4_competitive_industry_analysis": (
        "Competitive and industry analysis frameworks: Porter's Five Forces and its "
        "criticisms, competitive positioning matrices, PESTEL and macro trend "
        "scanning, how to identify indirect and substitute competitors, competitive "
        "intelligence gathering methods, and how to judge whether an industry is "
        "structurally attractive or a value trap."
    ),
    "q5_positioning_uvp": (
        "Positioning and the unique value proposition: April Dunford's positioning "
        "framework, the value proposition canvas, how to find real differentiation "
        "versus claimed differentiation, category design versus competing in an "
        "existing category, how to test a value proposition with customers, and why "
        "most value propositions are undifferentiated feature lists."
    ),
    "q6_business_model_revenue": (
        "Business model and revenue model design: the Business Model Canvas and how to "
        "use it, the taxonomy of revenue models including subscription, transactional, "
        "marketplace, licensing, retainer and productized service, unit economics, "
        "contribution margin, how to choose a pricing model, and how the revenue model "
        "constrains everything else in the business."
    ),
    "q7_financial_forecast": (
        "Financial forecasting for a small business or early stage company: how to "
        "build a bottom-up revenue forecast, cost structure and fixed versus variable "
        "costs, gross margin benchmarks by business model, CAC and LTV benchmarks and "
        "the LTV to CAC ratio, burn rate and runway, how much funding to raise and "
        "when, and the standard errors in startup financial projections."
    ),
    "q8_strategy_diagnosis": (
        "Diagnosing and auditing an existing business strategy: Richard Rumelt's good "
        "strategy bad strategy and the kernel of diagnosis, guiding policy and "
        "coherent action, the hallmarks of bad strategy including fluff and goal "
        "setting mistaken for strategy, strategy audit frameworks and scorecards, why "
        "strategies fail at execution, and the questions that expose a strategy with "
        "no real choices in it."
    ),
    # ---- remedial passes ------------------------------------------------
    # The first extract produced 10 confirmed-tier sources and 9 of them landed in
    # q1. Passes q2, q3, q5, q6, q7 and q8 returned ZERO peer-reviewed sources: the
    # broad queries above retrieve explainer and consultancy content because that is
    # what dominates these keywords commercially. Six of eight sections would then
    # rest entirely on consultant opinion.
    #
    # These re-ask the same six subjects in the register the academic literature
    # actually uses (empirical, meta-analysis, named journals, "evidence"), and
    # deliberately avoid the popular framework names that pull in blog content. Same
    # lesson as seo-advisor's three remedial passes: re-phrasing retrieves a
    # non-overlapping source set rather than more of the same.
    "q9_sizing_forecast_accuracy": (
        "Empirical research on market size estimation and demand forecasting accuracy: "
        "peer-reviewed studies on forecast bias and optimism in new venture revenue "
        "projections, the accuracy of market potential estimates, reference class "
        "forecasting, judgmental forecasting error, and academic evidence on how "
        "entrepreneurs systematically overestimate addressable demand."
    ),
    "q10_segmentation_evidence": (
        "Peer-reviewed marketing science on customer segmentation and targeting: "
        "empirical studies of segmentation validity and stability, evidence on whether "
        "demographic segments predict purchase behaviour, double jeopardy law and the "
        "Ehrenberg-Bass critique of targeting, customer heterogeneity research, and "
        "academic evidence on customer lifetime value based selection."
    ),
    "q11_differentiation_evidence": (
        "Academic research on product differentiation and competitive positioning: "
        "empirical studies on whether differentiation strategy predicts firm "
        "performance, the resource-based view and sustainable competitive advantage "
        "evidence, perceived value and willingness to pay experiments, brand "
        "distinctiveness research, and meta-analyses of generic strategy performance."
    ),
    "q12_business_model_evidence": (
        "Peer-reviewed research on business model design and innovation: empirical "
        "studies linking business model configuration to firm performance, academic "
        "work on revenue model choice and pricing strategy, subscription and recurring "
        "revenue economics research, and evidence on business model change in "
        "established firms."
    ),
    "q13_startup_financial_evidence": (
        "Empirical research on new venture financial performance: peer-reviewed "
        "studies of startup survival rates and failure causes, small business "
        "formation and closure statistics from national statistical agencies, research "
        "on customer acquisition cost and retention economics, cash flow and "
        "undercapitalization as failure predictors, and evidence on venture funding "
        "outcomes."
    ),
    # A 15th pass, added after the second extract. The remedial batch lifted every
    # other section to 5-11 confirmed sources, but competitive/industry analysis was
    # left with exactly one (Porter's own institute), which is the weakest possible
    # evidence base for a section that has to tell a client their industry is or is
    # not worth competing in. The "how much does industry structure actually explain"
    # literature is large and empirical, so this asks for it directly.
    "q15_industry_structure_evidence": (
        "Empirical research on industry structure and firm profitability: studies "
        "decomposing how much variance in firm performance is explained by industry "
        "effects versus firm-specific effects, tests of the validity and limits of "
        "Porter's Five Forces, research on industry attractiveness and profit "
        "persistence, competitive dynamics research, and meta-analyses of the "
        "structure conduct performance paradigm."
    ),
    # ---- persona / audience passes (added 2026-08-05) --------------------
    # The persona capability sits on a genuine tension: Q3 finds demographic
    # segmentation bases are criticized for failing to predict behaviour [s10], while
    # the standard persona template leads with demographics. These two passes test
    # whether the artifact earns its place for CONTENT and SEARCH specifically, which
    # is a different job from segmentation-for-targeting, and gather the evidence on
    # audience language and question mining that the content half actually runs on.
    "q16_persona_effectiveness": (
        "Empirical research on buyer personas and audience research in marketing: "
        "studies testing whether persona use improves marketing or content outcomes, "
        "evidence on persona validity and construction methods, criticism of personas "
        "as fictional and unvalidated, data-driven versus assumption-based personas, "
        "and research on customer insight quality and its effect on campaign "
        "performance."
    ),
    "q17_audience_language_intent": (
        "How audiences phrase problems and questions when searching, and how that "
        "shapes content: search intent classification, question mining from forums and "
        "community sites, voice-of-customer language research, the vocabulary gap "
        "between how businesses describe products and how customers describe problems, "
        "long-tail and conversational query patterns, and how AI answer engines match "
        "a user question to cited sources."
    ),
    "q14_strategy_process_evidence": (
        "Academic research on strategic planning and strategy execution: meta-analyses "
        "of whether formal strategic planning improves firm performance, empirical "
        "studies on strategy implementation failure rates and their causes, research on "
        "goal setting versus strategy, organizational alignment evidence, and studies "
        "of decision quality in strategic choice."
    ),
}

def log(msg, logfile="corpus-run.log"):
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    with open(RESEARCH_DIR / logfile, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def _load(path):
    """Parse a JSON file from disk."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except Exception:  # noqa: BLE001
        return None


_TRACKING = re.compile(r"^(utm_|fbclid|gclid|mc_|ref$|source$)")


def norm_url(u):
    """Normalize for dedup: drop scheme case, www., trailing slash, fragment, tracking."""
    try:
        s = urlsplit(u.strip())
    except Exception:  # noqa: BLE001
        return u.strip().lower()
    host = s.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    q = urlencode([(k, v) for k, v in parse_qsl(s.query) if not _TRACKING.match(k)])
    path = s.path.rstrip("/") or "/"
    return urlunsplit(("https", host, path, q, ""))


def domain_of(u):
    host = urlsplit(u).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def tier_of(u):
    """confirmed = primary data or peer-reviewed; everything else is a consultant or
    vendor making a case, and must be labelled as such.

    No blanket ".gov = confirmed" rule on purpose. seo-advisor used one and promoted a
    US House legislative schedule to top tier. Statistical agencies are enumerated in
    CONFIRMED_DOMAINS instead.
    """
    d = domain_of(u)
    if d in CONFIRMED_DOMAINS or any(d.endswith("." + c) for c in CONFIRMED_DOMAINS):
        return "confirmed"
    return "practitioner"

# There is deliberately no blanket ".edu = confirmed" rule either, for the same
# reason as .gov. The first extract run promoted a University of Phoenix marketing
# article ("How to write vision, values and mission statements") and a Northwestern
# program page to top tier purely on their suffix. A university publishes research,
# course pages and advertising from one domain, so the suffix carries no evidentiary
# signal. Peer review is carried by the enumerated publishers instead.


def is_junk(url, title):
    d = domain_of(url)
    if d in JUNK_DOMAINS or any(d.endswith("." + j) for j in JUNK_DOMAINS):
        return "social/UGC"
    if any(d.endswith(m) for m in MIRROR_SUFFIXES):
        return "localized mirror"
    # Normalize separators to spaces so short tokens match as whole words. Plain
    # substring matching let "hou-SEO-frepresentatives" through in the original; \b
    # would not have helped either, since underscores count as word characters.
    hay = " " + re.sub(r"[^a-z0-9]+", " ", f"{title} {url}".lower()).strip() + " "
    for tok in TOPIC_TOKENS:
        if len(tok) <= 4:
            if f" {tok} " in hay:
                return None
        elif tok in hay:
            return None
    return "off-topic"


# ---------------------------------------------------------------- run

def run_pass(key, query):
    out_path = PASSES_DIR / f"{key}.json"
    if out_path.exists() and out_path.stat().st_size > 2000:
        log(f"SKIP {key} (already have {out_path.stat().st_size} bytes)")
        return
    log(f"START {key}")
    try:
        r = subprocess.run(
            [sys.executable, str(RESEARCH_PY), "--query", query, "--depth", "deep", "--json"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=1800,
        )
    except subprocess.TimeoutExpired:
        log(f"TIMEOUT {key}")
        return
    stdout = (r.stdout or "").strip()
    try:
        data = json.loads(stdout)
    except Exception:  # noqa: BLE001
        log(f"FAIL {key} rc={r.returncode} stdout={stdout[:200]!r} err={(r.stderr or '')[-300:]!r}")
        return
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"DONE {key} rc={r.returncode} results={len(data.get('results', []))} "
        f"report={'yes' if data.get('report') else 'no'}")


def run_all(only=None):
    PASSES_DIR.mkdir(parents=True, exist_ok=True)
    items = {only: QUERIES[only]} if only else QUERIES
    log(f"=== RESEARCH START passes={len(items)} ===")
    for key, q in items.items():
        run_pass(key, q)
    log("=== RESEARCH DONE ===")


# ---------------------------------------------------------------- extract

def extract():
    """passes/*.json -> a deduped, ranked, tiered, capped sources.json."""
    files = sorted(PASSES_DIR.glob("q*.json"))
    if not files:
        raise SystemExit(f"no pass files in {PASSES_DIR} - run `gather.py run` first")

    merged = {}
    for fp in files:
        data = _load(fp)
        if not isinstance(data, dict):
            log(f"WARN unreadable {fp.name}")
            continue
        topic = fp.stem
        for r in data.get("results", []):
            url = (r.get("url") or "").strip()
            if not url.startswith("http"):
                continue
            e = merged.setdefault(norm_url(url), {
                "url": url, "title": r.get("title") or "", "topics": [],
                "engines": set(), "best_score": 0.0,
                "published_date": r.get("published_date"),
            })
            if topic not in e["topics"]:
                e["topics"].append(topic)
            e["engines"].update(r.get("sources") or [])
            e["best_score"] = max(e["best_score"], float(r.get("best_score") or 0))
            if not e["title"] and r.get("title"):
                e["title"] = r["title"]

    total_found = len(merged)

    # 1. Drop junk before ranking.
    kept, dropped = [], {}
    for e in merged.values():
        why = is_junk(e["url"], e["title"])
        if why:
            dropped[why] = dropped.get(why, 0) + 1
            continue
        kept.append(e)
    for why, n in sorted(dropped.items()):
        log(f"  dropped {n} ({why})")

    # 2. Rank by cross-pass agreement, then cross-engine agreement, then score.
    kept.sort(key=lambda e: (-len(e["topics"]), -len(e["engines"]), -e["best_score"]))

    # 3. Cap per domain so no single consultancy blog dominates. Confirmed-tier is
    #    exempt: there is no such thing as too much primary data.
    per_domain, capped, domain_cut = {}, [], 0
    for e in kept:
        d = domain_of(e["url"])
        if tier_of(e["url"]) != "confirmed":
            if per_domain.get(d, 0) >= PER_DOMAIN_CAP:
                domain_cut += 1
                continue
            per_domain[d] = per_domain.get(d, 0) + 1
        capped.append(e)
    if domain_cut:
        log(f"  dropped {domain_cut} (per-domain cap of {PER_DOMAIN_CAP})")

    # 4. Confirmed-tier jumps the global cap. Capping it would cut peer-reviewed
    #    research while keeping vendor blogs that more engines happened to surface,
    #    which is backwards for an evidence corpus.
    confirmed_e = [e for e in capped if tier_of(e["url"]) == "confirmed"]
    practitioner_e = [e for e in capped if tier_of(e["url"]) != "confirmed"]
    room = max(0, SOURCE_CAP - len(confirmed_e))
    if len(practitioner_e) > room:
        log(f"CAP {len(capped)} eligible -> {len(confirmed_e)} confirmed + top {room} practitioner")
    ranked = confirmed_e + practitioner_e[:room]

    # ---- index stability -------------------------------------------------
    # Existing indices are frozen. Renumbering on a refresh would silently repoint
    # every [sN] citation already written in references/ at a different source.
    existing = _load(RESEARCH_DIR / "sources.json") or {}
    locked = existing.get("sources", [])
    locked_urls = {norm_url(s["url"]) for s in locked}
    next_index = max([s["index"] for s in locked], default=0) + 1

    fresh = [e for e in ranked if norm_url(e["url"]) not in locked_urls]
    sources = list(locked)
    for e in fresh:
        sources.append({
            "index": next_index,
            "title": e["title"],
            "url": e["url"],
            "tier": tier_of(e["url"]),
            "topics": e["topics"],
            "engines": sorted(e["engines"]),
            "published_date": e["published_date"],
        })
        next_index += 1
    sources.sort(key=lambda s: s["index"])
    if locked:
        log(f"  preserved {len(locked)} existing indices, added {len(fresh)} new")

    n_conf = sum(1 for s in sources if s["tier"] == "confirmed")
    out = {
        "generated_at": datetime.now().date().isoformat(),
        "method": ("8 deep passes via the in-repo research skill (Exa+Tavily+Serper+Jina "
                   "fused, content-extracted), deduped by normalized URL, junk-filtered, "
                   "per-domain capped, tiered confirmed vs practitioner"),
        "note": "inline [sN] in references/research-synthesis.md resolves to sources[N-1]",
        "total_found": total_found,
        "source_count": len(sources),
        "confirmed": n_conf,
        "practitioner": len(sources) - n_conf,
        "sources": sources,
    }
    (RESEARCH_DIR / "sources.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"extract: {total_found} deduped -> {len(sources)} kept "
        f"({n_conf} confirmed / {len(sources)-n_conf} practitioner)")


def verify():
    """Every [sN] in references/ must resolve to a real source index."""
    sj = _load(RESEARCH_DIR / "sources.json") or {}
    valid = {s["index"] for s in sj.get("sources", [])}
    refs = RESEARCH_DIR.parent / "references"
    bad = 0
    for fp in sorted(refs.glob("*.md")) if refs.exists() else []:
        for n in {int(m) for m in re.findall(r"\[s(\d+)[,\]]", fp.read_text(encoding="utf-8"))}:
            if n not in valid:
                log(f"  BROKEN [s{n}] in {fp.name}")
                bad += 1
    log(f"verify: {len(valid)} sources, {bad} broken citation(s)")
    return bad


def _selftest():
    """The evidence rules are the whole point of this file, so they get a check."""
    assert norm_url("http://WWW.Example.com/a/?utm_source=x#f") == "https://example.com/a"
    assert norm_url("https://example.com") == "https://example.com/"
    assert tier_of("https://www.census.gov/data") == "confirmed"
    assert tier_of("https://hbr.org/2024/strategy") == "practitioner"
    assert tier_of("https://pmc.ncbi.nlm.nih.gov/articles/PMC1/") == "confirmed"
    assert tier_of("https://isc.hbs.edu/strategy/Pages/the-five-forces.aspx") == "confirmed"
    # a .edu suffix is not evidence: this is University of Phoenix marketing copy
    assert tier_of("https://www.phoenix.edu/articles/business/how-to-write.html") == "practitioner"
    assert tier_of("https://msc.northwestern.edu/mission-vs-vision-statements/") == "practitioner"
    # the bug this guard exists for: trusted domain, off-topic document
    assert is_junk("https://census.gov/119_legislative_schedule.pdf", "Legislative Schedule")
    assert is_junk("https://census.gov/data/business-formation", "Business formation") is None
    assert is_junk("https://linkedin.com/pulse/strategy", "Strategy") == "social/UGC"
    # short tokens must match as whole words, not substrings
    assert is_junk("https://example.com/scam-report", "Scam report") == "off-topic"
    print("selftest ok")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "selftest":
        _selftest()
    elif cmd == "run":
        run_all(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "extract":
        extract()
    elif cmd == "verify":
        sys.exit(1 if verify() else 0)
    else:
        run_all()
        extract()

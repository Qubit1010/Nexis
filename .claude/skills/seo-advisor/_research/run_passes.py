#!/usr/bin/env python3
"""Phase 1: run the 11 deep research passes that seed the seo-advisor corpus.

Uses the in-repo `research` skill (Exa + Tavily + Serper + Jina fused, then
content extraction + a cited report). Deep mode auto-saves a markdown report to
`research/YYYY-MM-DD-<slug>.md` at the repo root; we additionally capture the
`--json` payload per pass into `_research/passes/<key>.json` so the full ranked
source list survives for the NotebookLM import step.

Usage (PowerShell, UNSANDBOXED - api.exa.ai fails when sandboxed):
    python run_passes.py            # all remaining passes
    python run_passes.py q7_offpage # one pass by key

Already-completed passes are skipped, so this is safe to re-run after a failure.
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RESEARCH_DIR = Path(__file__).resolve().parent
PASSES_DIR = RESEARCH_DIR / "passes"
REPO_ROOT = RESEARCH_DIR.parents[3]
RESEARCH_PY = REPO_ROOT / ".claude" / "skills" / "research" / "scripts" / "research.py"

# One deep pass each. Phrased to pull current 2026 sources and to target the
# ground blog-writer's 2026-07-21 passes did NOT cover (site-level and
# platform-level, not article-level).
QUERIES = {
    "q1_how_search_works": (
        "How search engines work in 2026: crawling, indexing, and ranking. Google's "
        "ranking systems, how the index is built, how core updates change rankings, "
        "the Helpful Content system, and what Google Search Central officially "
        "documents about ranking factors versus what is speculation."
    ),
    "q2_keyword_research": (
        "Keyword research and search intent in 2026: the end-to-end process, search "
        "volume and keyword difficulty metrics and how reliable they are, keyword "
        "clustering, content gap analysis against competitors, classifying "
        "informational, commercial, navigational and transactional intent, and how "
        "keyword research changes now that AI search fans out queries."
    ),
    "q3_onpage_site_level": (
        "On-page SEO at the site level in 2026: title tags, meta descriptions, "
        "heading hierarchy, URL structure, image optimization, topical authority and "
        "topic clusters across a whole site, internal linking architecture and anchor "
        "text, entity optimization, and E-E-A-T signals. What still measurably moves "
        "rankings versus what is cargo cult."
    ),
    "q4_technical_seo": (
        "Technical SEO in 2026: crawl budget, robots.txt directives, XML sitemaps, "
        "indexation control, canonical tags, redirects and HTTP status codes, HTTPS, "
        "JavaScript SEO and rendering, server-side rendering for crawlers, duplicate "
        "content, site architecture and crawl depth, and mobile-first indexing."
    ),
    "q5_core_web_vitals": (
        "Core Web Vitals and page speed in 2026: the current LCP, INP and CLS "
        "thresholds, how much they actually affect rankings, field data versus lab "
        "data, PageSpeed Insights and CrUX, and the specific engineering fixes that "
        "move each metric."
    ),
    "q6_structured_data": (
        "Structured data and schema markup in 2026: which schema types earn rich "
        "results, JSON-LD implementation, validation and testing tools, Google's "
        "supported structured data features, schema deprecations, and how structured "
        "data affects retrieval and citation by AI search engines."
    ),
    "q7_offpage_backlinks": (
        "Off-page SEO in 2026: backlinks and link building, which link acquisition "
        "tactics still work and which get penalized, digital PR, unlinked brand "
        "mentions, guest posting, HARO and journalist outreach, link quality metrics, "
        "toxic links and disavow, and how much backlinks still matter relative to "
        "brand signals and content quality."
    ),
    "q8_local_seo": (
        "Local SEO in 2026: Google Business Profile optimization, the local map pack "
        "ranking factors, NAP citations and consistency, local reviews and review "
        "velocity, local landing pages, service area businesses, and how AI search "
        "and AI Overviews are changing local discovery."
    ),
    "q9_ai_search_aeo_geo": (
        "AI search optimization in 2026: Answer Engine Optimization and Generative "
        "Engine Optimization at the site level. How Google AI Overviews and AI Mode "
        "select sources, query fan-out, how ChatGPT, Perplexity, Gemini and Claude "
        "differ in what they cite, llms.txt and machine-readable files, entity SEO and "
        "knowledge graphs, AI crawler access, and brand mentions as a visibility lever."
    ),
    "q10_measurement": (
        "SEO measurement and reporting in 2026: Google Search Console setup and the "
        "reports that matter, GA4 for organic traffic, rank tracking accuracy, "
        "measuring AI search visibility and AI referral traffic, AI bot analytics from "
        "server logs, self-reported attribution, traffic forecasting, and what to put "
        "in a monthly SEO report for a client."
    ),
    # q12 and q13 are remedial. The q9 pass returned the fewest results of any pass
    # (24) and its own synthesis explicitly flagged that the retrieved sources did
    # NOT cover llms.txt, entity SEO / knowledge graphs, AI crawler access, or query
    # fan-out - the four most load-bearing 2026 mechanics. Splitting them into
    # narrower, separately-phrased passes retrieves what the broad q9 query missed.
    "q12_ai_crawlers_llmstxt": (
        "llms.txt and AI crawler access in 2026: what the llms.txt standard is and "
        "whether any AI engine actually honors it, how to allow or block GPTBot, "
        "ChatGPT-User, ClaudeBot, anthropic-ai, PerplexityBot, Google-Extended and "
        "CCBot in robots.txt, the tradeoff between blocking AI crawlers and losing AI "
        "visibility, server-side rendering for AI bots, and machine-readable content "
        "formats for LLM consumption."
    ),
    "q13_entity_seo_fanout": (
        "Entity SEO, knowledge graphs and query fan-out in 2026: how Google and LLMs "
        "build entity understanding, the Google Knowledge Graph and Knowledge Panels, "
        "Wikipedia and Wikidata as entity sources, sameAs and Organization schema for "
        "entity disambiguation, how brand mentions without links influence AI citation, "
        "and how query fan-out expands one prompt into many sub-queries and what that "
        "means for content coverage."
    ),
    "q11_tools_and_service": (
        "The SEO tool stack in 2026 and selling SEO as a service: Ahrefs versus Semrush "
        "versus Moz versus free alternatives, crawlers like Screaming Frog, AI "
        "visibility trackers, what agencies charge for SEO retainers and audits, how to "
        "scope an SEO engagement, realistic timelines to results, and what deliverables "
        "clients expect."
    ),
    # q14 is remedial for the same reason q12/q13 were. The q11 pass retrieved the
    # tool-comparison half of its query and returned almost nothing on the commercial
    # half; its own synthesis stated that pricing, scoping frameworks, timelines and
    # deliverables "are not detailed in these sources". Asking about the business of
    # SEO WITHOUT naming any tool retrieves a different, non-overlapping source set.
    "q14_seo_pricing_scoping": (
        "Pricing and selling SEO services in 2026: typical monthly retainer ranges for "
        "small business, mid-market and enterprise SEO, one-off SEO audit pricing, "
        "hourly versus project versus retainer versus performance-based pricing models, "
        "how agencies scope an SEO engagement and write the statement of work, realistic "
        "timelines before a client sees ranking and traffic results, what deliverables "
        "and reporting cadence clients expect, client churn and contract length, and why "
        "guaranteeing rankings is a red flag."
    ),
}


def log(msg):
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    with open(RESEARCH_DIR / "research-run.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


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
    # research.py prints warnings to stderr; the JSON payload is the whole stdout.
    try:
        data = json.loads(stdout)
    except Exception:
        log(f"FAIL {key} rc={r.returncode} stdout={stdout[:200]!r} err={(r.stderr or '')[-300:]!r}")
        return
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    n = len(data.get("results", []))
    log(f"DONE {key} rc={r.returncode} results={n} report={'yes' if data.get('report') else 'no'}")


if __name__ == "__main__":
    PASSES_DIR.mkdir(parents=True, exist_ok=True)
    only = sys.argv[1] if len(sys.argv) > 1 else None
    items = {only: QUERIES[only]} if only else QUERIES
    log(f"=== RESEARCH START passes={len(items)} ===")
    for key, q in items.items():
        run_pass(key, q)
    log("=== RESEARCH DONE ===")

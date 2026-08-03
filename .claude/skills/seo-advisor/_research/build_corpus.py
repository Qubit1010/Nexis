#!/usr/bin/env python3
"""Build (and refresh) the seo-advisor research corpus, per
`.claude/rules/research-backed-skills.md`.

Pipeline (run in order):

    python build_corpus.py extract     # passes/*.json -> deduped sources.json
    python build_corpus.py import      # create notebook + add every URL, merge uuids
    python build_corpus.py synthesize  # ask Q1-Q11 --json -> q*.json
    python build_corpus.py verify      # every [sN] in references/ resolves

Differences from claude-advisor's build_corpus.py, all deliberate:

* Sources come from the in-repo `research` skill (run_passes.py) and are imported
  into NotebookLM BY URL, rather than letting NotebookLM run its own web research.
  That is the flow Aleem asked for, and it makes the corpus reproducible: the exact
  source set is on disk before anything touches NotebookLM.
* sources.json carries BOTH key shapes - `uuid_to_index` (required by the rule) and
  per-source `url` - so citations survive even if the notebook is rebuilt and every
  uuid changes.
* Each source carries `tier` (confirmed vs practitioner) and `topics` (which passes
  surfaced it). SEO's information space is dominated by self-interested vendor
  content, so the synthesis must be able to say which claims rest on primary
  documentation and which rest on a tool vendor's blog.
* `verify` is new. claude-advisor's sources.json was gitignored then purged, leaving
  its [sNN] citations unresolvable; sales-playbook carries 15 dangling ones. This
  phase makes that failure loud instead of silent.

The NotebookLM CLI emits UTF-8 with a BOM, so every parse uses utf-8-sig.
"""
import collections
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

RESEARCH_DIR = Path(__file__).resolve().parent
PASSES_DIR = RESEARCH_DIR / "passes"
SKILL_DIR = RESEARCH_DIR.parent
REFERENCES_DIR = SKILL_DIR / "references"

NOTEBOOK_TITLE = "SEO Complete Guide 2026 (NexusPoint)"
NOTEBOOK_ID_FILE = RESEARCH_DIR / ".notebook_id"          # bucket A (legacy single)
NOTEBOOK_IDS_FILE = RESEARCH_DIR / ".notebook_ids.json"   # bucket -> notebook id

# This account's NotebookLM plan caps a notebook at 100 sources (Plus tier; Pro is
# 300). Discovered the hard way: the first import ran to exactly 100 `ready` and then
# every subsequent add returned `RPCError rpc_code=9` and landed as an `error`-status
# entry with a null url. That error is indistinguishable from an auth failure, which
# is precisely the trap `.claude/rules/research-backed-skills.md` warns about.
#
# So the corpus is partitioned across topic notebooks instead. This is better than a
# workaround: each synthesis question queries a focused corpus rather than one diluted
# with 250 off-topic sources, and the skill's mode routing maps onto the buckets.
NOTEBOOK_SOURCE_CAP = 95   # 5-slot safety margin under the real 100

BUCKETS = {
    "A_core": {
        "title": "SEO 2026 - Core (NexusPoint)",
        "topics": [],   # holds the first 100 imported, mixed topics, already loaded
    },
    "B_foundations": {
        "title": "SEO 2026 - Foundations & Content (NexusPoint)",
        "topics": ["q1_how_search_works", "q2_keyword_research", "q3_onpage_site_level"],
    },
    "C_technical": {
        "title": "SEO 2026 - Technical (NexusPoint)",
        "topics": ["q4_technical_seo", "q5_core_web_vitals", "q6_structured_data"],
    },
    "D_authority_local": {
        "title": "SEO 2026 - Authority & Local (NexusPoint)",
        "topics": ["q7_offpage_backlinks", "q8_local_seo"],
    },
    "E_ai_search": {
        "title": "SEO 2026 - AI Search (NexusPoint)",
        "topics": ["q9_ai_search_aeo_geo", "q12_ai_crawlers_llmstxt",
                   "q13_entity_seo_fanout"],
    },
    "F_measure_business": {
        "title": "SEO 2026 - Measurement & Business (NexusPoint)",
        "topics": ["q10_measurement", "q11_tools_and_service", "q14_seo_pricing_scoping"],
    },
}

# Which notebook answers which synthesis question. A_core is always consulted as a
# fallback because it spans every topic.
TOPIC_TO_BUCKET = {t: b for b, cfg in BUCKETS.items() for t in cfg["topics"]}

# NotebookLM caps sources per notebook by account plan (Standard 50 / Plus 100 /
# Pro 300 / Ultra 600). Hitting the cap fails imports with a generic RPC error that
# reads exactly like an auth failure, so always check the live count before blaming
# auth.
#
# Set to 320 deliberately. The first 284 imported cleanly, and the q12/q13 remedial
# passes (llms.txt, AI crawler control, entity SEO, query fan-out) produced the
# highest-value sources in the corpus for its weakest topic. Better to attempt the
# import and find the real ceiling than to silently drop that material. If the tail
# fails, the failures are logged per-URL and low-value practitioner sources can be
# swapped out by hand.
SOURCE_CAP = 320

# Domains whose claims are primary documentation or peer-reviewed research rather
# than a vendor making a case for its own product. Everything else is [practitioner].
CONFIRMED_DOMAINS = {
    "developers.google.com", "search.google.com", "support.google.com",
    "google.com", "blog.google", "webmasters.googleblog.com",
    "developer.mozilla.org", "web.dev", "chrome.com", "schema.org", "w3.org",
    "arxiv.org", "dl.acm.org", "acm.org", "ieee.org", "springer.com",
    "nature.com", "sciencedirect.com", "bing.com", "blogs.bing.com",
    "microsoft.com", "openai.com", "anthropic.com",
}

# Social, UGC and aggregator hosts. Each is somebody's opinion with no editorial
# process, and they crowded out primary documentation in the first extract run
# (13 linkedin/facebook pages ranked above Google's own ranking-systems guide).
# YouTube is blocked here but the three hand-curated video courses still enter via
# SEED_SOURCES, which bypasses this filter deliberately.
JUNK_DOMAINS = {
    "facebook.com", "linkedin.com", "twitter.com", "x.com", "instagram.com",
    "pinterest.com", "tiktok.com", "quora.com", "medium.com", "reddit.com",
    "youtube.com", "youtu.be", "slideshare.net", "scribd.com", "issuu.com",
}

# Localized mirrors of docs we already have in English. Keeping both would spend
# two of ~285 notebook slots on the same page.
MIRROR_SUFFIXES = (".google.cn", ".google.co.jp", ".google.de", ".google.fr")

# A source has to be plausibly about search. One pass returned a US House
# legislative schedule PDF, which the blanket ".gov = confirmed" rule then promoted
# to the top tier. Cheap guard: the title or the URL must mention something in the
# subject area.
TOPIC_TOKENS = (
    "seo", "search", "serp", "rank", "keyword", "backlink", "link", "crawl",
    "index", "schema", "structured-data", "structured data", "google", "bing",
    "geo", "aeo", "llm", "ai-search", "ai search", "generative", "answer engine",
    "vitals", "pagespeed", "page speed", "organic", "traffic", "content",
    "marketing", "optimiz", "optimis", "e-e-a-t", "eeat", "sitemap", "robots",
    "canonical", "redirect", "hreflang", "analytics", "ahrefs", "semrush", "moz",
    "local", "business profile", "citation", "digital pr", "overview",
)

# No single site should dominate the corpus. The first run gave one small SEO blog
# 13 slots, more than developers.google.com had.
PER_DOMAIN_CAP = 5

# Sources Aleem curated by hand (2026-07-28) before this build, each already its own
# single-source notebook. They are practitioner video courses, not documentation, so
# they carry no evidentiary weight on numbers - but they are course-SHAPED, which is
# exactly what the curriculum needs (the Claude Playbook pulled its teaching sequence
# from a comparable practitioner-YouTube batch). Always tiered [practitioner].
SEED_SOURCES = [
    {"url": "https://www.youtube.com/watch?v=t_Y5kznd2rk",
     "title": "I Spent 2,000 Hours Learning GEO/AEO For This",
     "topics": ["q9_ai_search_aeo_geo"]},
    {"url": "https://www.youtube.com/watch?v=uza9GX0E2mw",
     "title": "AI SEO Course for Beginners: Complete AEO Tutorial",
     "topics": ["q9_ai_search_aeo_geo"]},
    {"url": "https://www.youtube.com/watch?v=xsVTqzratPs",
     "title": "Complete SEO Course for Beginners: Learn to Rank #1 in Google",
     "topics": ["q1_how_search_works"]},
]

SUFFIX = (" Give specific 2026 numbers, tool names, thresholds, and concrete tactics, "
          "and cite sources. Where the sources disagree or the evidence is only a "
          "vendor's own study, say so explicitly.")

ASKS = {
    "q1_how_search_works": "Explain how search engines work in 2026: crawling, indexing, and ranking. What are Google's actual documented ranking systems, how do core updates work and what should a site do after one, and which widely repeated 'ranking factors' are not supported by Google's own documentation?" + SUFFIX,
    "q2_keyword_research": "Lay out the end-to-end keyword research process in 2026: how to find keywords, how reliable search volume and keyword difficulty scores actually are, how to cluster keywords, how to run a content gap analysis, how to classify search intent, and how keyword research changes now that AI search fans a single prompt into many sub-queries." + SUFFIX,
    "q3_onpage_site_level": "Explain on-page SEO across a whole site in 2026: title tags, meta descriptions, headings, URLs, images, topical authority and topic clusters, internal linking architecture and anchor text, entity optimization, and E-E-A-T. Separate what measurably moves rankings from what is cargo cult with no evidence behind it." + SUFFIX,
    "q4_technical_seo": "Explain technical SEO in 2026: crawl budget, robots.txt, XML sitemaps, indexation control, canonical tags, redirects and status codes, HTTPS, JavaScript SEO and rendering, duplicate content, site architecture and crawl depth, and mobile-first indexing. Which technical issues actually cost traffic and in what order should they be fixed?" + SUFFIX,
    "q5_core_web_vitals": "Give the current Core Web Vitals thresholds for 2026 (LCP, INP, CLS), how much they really affect rankings versus how much they are hyped, the difference between field and lab data, and the specific engineering fixes that move each metric." + SUFFIX,
    "q6_structured_data": "Explain structured data and schema markup in 2026: which schema types earn rich results, how to implement JSON-LD, how to validate it, what Google has deprecated, and how structured data affects retrieval and citation by AI search engines." + SUFFIX,
    "q7_offpage_backlinks": "Explain off-page SEO in 2026: which link building tactics still work and which get penalized, digital PR, unlinked brand mentions, guest posting, journalist outreach, how to judge link quality, whether disavow still matters, and how much backlinks matter now relative to brand signals and content quality." + SUFFIX,
    "q8_local_seo": "Explain local SEO in 2026: Google Business Profile optimization, local map pack ranking factors, NAP citations, reviews and review velocity, local landing pages, service area businesses, and how AI search is changing local discovery." + SUFFIX,
    "q9_ai_search_aeo_geo": "Explain AI search optimization at the site level in 2026: how Google AI Overviews and AI Mode select sources, query fan-out, how ChatGPT, Perplexity, Gemini and Claude differ in what they cite, llms.txt and machine-readable files, entity SEO and knowledge graphs, AI crawler access, and brand mentions as a visibility lever. Which of these have real evidence and which are speculation?" + SUFFIX,
    "q10_measurement": "Explain SEO measurement and reporting in 2026: which Google Search Console reports matter, GA4 for organic, how accurate rank tracking is, how to measure AI search visibility and AI referral traffic, AI bot analytics from server logs, self-reported attribution, forecasting, and what belongs in a monthly client SEO report." + SUFFIX,
    "q11_tools_and_service": "Compare the 2026 SEO tool stack (Ahrefs, Semrush, Moz, Screaming Frog, AI visibility trackers, and free alternatives). For each, what it is best at, what it costs, and whether a free alternative is good enough." + SUFFIX,
    "q12_ai_crawlers_llmstxt": "Explain llms.txt and AI crawler control in 2026: what llms.txt is and whether any engine actually honors it, how to allow or block GPTBot, ChatGPT-User, ClaudeBot, anthropic-ai, PerplexityBot, Google-Extended and CCBot, the difference between a training crawler and a search/retrieval crawler, and the visibility cost of blocking them." + SUFFIX,
    "q13_entity_seo_fanout": "Explain entity SEO, knowledge graphs and query fan-out in 2026: how search engines and LLMs build entity understanding, the role of Wikipedia, Wikidata and sameAs schema, how unlinked brand mentions influence AI citation, and how query fan-out expands one prompt into many sub-queries and what that means for how content must be structured." + SUFFIX,
    "q14_seo_pricing_scoping": "Explain the business of selling SEO in 2026: typical retainer ranges by client size, one-off audit pricing, the pricing models (hourly, project, retainer, performance) and when each fits, how to scope an engagement, realistic timelines before a client sees results, expected deliverables and reporting cadence, and why guaranteeing rankings is a red flag." + SUFFIX,
}


def find_exe():
    """Local Python312 path first, then fall through to PATH.

    The developer-advisor and student-advisor copies of this helper list a
    Python313 path that does not exist on this machine, so order matters.
    """
    candidates = [
        Path.home() / "AppData/Local/Programs/Python/Python312/Scripts/notebooklm.exe",
        Path(r"C:\Users\qubit\AppData\Local\Programs\Python\Python312\Scripts\notebooklm.exe"),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    w = shutil.which("notebooklm")
    if w:
        return w
    raise SystemExit("notebooklm.exe not found")


def log(msg, logfile="corpus-run.log"):
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    with open(RESEARCH_DIR / logfile, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run(args, timeout=600):
    return subprocess.run(
        [find_exe()] + args,
        capture_output=True, text=True,
        encoding="utf-8-sig", errors="replace",
        timeout=timeout,
    )


def _load(path):
    """Parse a JSON file from disk."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except Exception:  # noqa: BLE001
        return None


def _loads(text):
    """Parse a JSON string (CLI stdout). Kept separate from _load on purpose:
    passing stdout to _load silently treats it as a filename and returns None,
    which reads as 'the command failed' when it actually succeeded."""
    try:
        return json.loads((text or "").strip().lstrip("﻿"))
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
    """confirmed = primary documentation or peer-reviewed; everything else is a
    vendor or practitioner making a case, and must be labelled as such.

    Note there is deliberately no blanket ".gov = confirmed" rule: the first run
    used one and admitted a US House legislative schedule as a top-tier source.
    """
    d = domain_of(u)
    if d in CONFIRMED_DOMAINS or any(d.endswith("." + c) for c in CONFIRMED_DOMAINS):
        return "confirmed"
    if d.endswith(".edu"):
        return "confirmed"
    return "practitioner"


def is_junk(url, title):
    d = domain_of(url)
    if d in JUNK_DOMAINS or any(d.endswith("." + j) for j in JUNK_DOMAINS):
        return "social/UGC"
    if any(d.endswith(m) for m in MIRROR_SUFFIXES):
        return "localized mirror"
    # Normalize separators to spaces so a short token can be matched as a whole
    # word. Plain substring matching let a US House legislative calendar through:
    # "hou-SEO-frepresentatives". Regex \b would not have saved it either, since
    # \b treats the underscores in "119_legislative_schedule" as word characters.
    hay = " " + re.sub(r"[^a-z0-9]+", " ", f"{title} {url}".lower()).strip() + " "
    for tok in TOPIC_TOKENS:
        if len(tok) <= 4:
            if f" {tok} " in hay:
                return None
        elif tok in hay:
            return None
    return "off-topic"


# ---------------------------------------------------------------- extract

def extract():
    """passes/*.json -> a deduped, ranked, capped sources.json."""
    files = sorted(PASSES_DIR.glob("q*.json"))
    if not files:
        raise SystemExit(f"no pass files in {PASSES_DIR} - run run_passes.py first")

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
            key = norm_url(url)
            e = merged.setdefault(key, {
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

    # 3. Cap per domain so no single blog dominates. Confirmed-tier domains are
    #    exempt: there is no such thing as too much of Google's own documentation.
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

    # 4. Confirmed-tier sources jump the global cap. In the first run the cap cut
    #    developers.google.com pages while keeping vendor blogs that more engines
    #    happened to surface, which is exactly backwards for an evidence corpus.
    confirmed = [e for e in capped if tier_of(e["url"]) == "confirmed"]
    practitioner = [e for e in capped if tier_of(e["url"]) != "confirmed"]
    room = max(0, SOURCE_CAP - len(confirmed))
    if len(practitioner) > room:
        log(f"CAP {len(capped)} eligible -> {len(confirmed)} confirmed + top {room} practitioner")
    ranked = confirmed + practitioner[:room]

    # Hand-curated seeds go in front of the ranked web results and are never capped:
    # they were chosen deliberately, not surfaced by an engine.
    seeds = []
    for s in SEED_SOURCES:
        if norm_url(s["url"]) in {norm_url(e["url"]) for e in ranked}:
            continue
        seeds.append({"url": s["url"], "title": s["title"], "topics": list(s["topics"]),
                      "engines": {"curated"}, "best_score": 1.0, "published_date": None})
    ranked = seeds + ranked

    # ---- index stability -------------------------------------------------
    # Anything already imported into the notebook keeps its index and its uuid
    # forever. Renumbering on a refresh would silently repoint every [sN] citation
    # already written in references/ at a different source, and would throw away the
    # uuid mapping the rule requires. New sources are appended after the highest
    # existing index; they are never interleaved.
    existing = _load(RESEARCH_DIR / "sources.json") or {}
    locked = [s for s in existing.get("sources", []) if s.get("id")]
    locked_urls = {norm_url(s["url"]) for s in locked}
    next_index = max([s["index"] for s in locked], default=0) + 1

    fresh = [e for e in ranked if norm_url(e["url"]) not in locked_urls]
    room = max(0, SOURCE_CAP - len(locked))
    if len(fresh) > room:
        log(f"  {len(locked)} already imported, room for {room} more, "
            f"{len(fresh) - room} cut")
        fresh = fresh[:room]

    sources = list(locked)
    for e in fresh:
        sources.append({
            "index": next_index,
            "id": "",                       # filled by `import`
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

    out = {
        "notebook_id": _read_notebook_id() or "",
        "notebook_title": NOTEBOOK_TITLE,
        "generated_at": datetime.now().date().isoformat(),
        "method": ("11 deep passes via the in-repo research skill (Exa+Tavily+Serper+Jina "
                   "fused, content-extracted), deduped by normalized URL, imported into "
                   "NotebookLM by URL, then per-question ask --json synthesis"),
        "note": "inline [sN] in references/research-synthesis.md resolves to sources[N-1]",
        "total_found": total_found,
        "source_count": len(sources),
        # Carried forward, not rebuilt - see the index-stability note above.
        "uuid_to_index": {s["id"]: s["index"] for s in sources if s.get("id")},
        "sources": sources,
    }
    (RESEARCH_DIR / "sources.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    confirmed = sum(1 for s in sources if s["tier"] == "confirmed")
    log(f"extract: {total_found} deduped -> {len(sources)} kept "
        f"({confirmed} confirmed / {len(sources)-confirmed} practitioner)")


# ---------------------------------------------------------------- import

def _read_notebook_id():
    if NOTEBOOK_ID_FILE.exists():
        return NOTEBOOK_ID_FILE.read_text(encoding="utf-8").strip() or None
    return None


def ensure_notebook():
    nid = _read_notebook_id()
    if nid:
        log(f"import: reusing notebook {nid}")
        return nid
    r = run(["create", NOTEBOOK_TITLE, "--json"], timeout=180)
    data = _loads(r.stdout) or {}
    nid = (data.get("notebook") or {}).get("id")
    if not nid:
        raise SystemExit(f"could not create notebook: rc={r.returncode} "
                         f"out={(r.stdout or '')[:300]} err={(r.stderr or '')[:300]}")
    NOTEBOOK_ID_FILE.write_text(nid, encoding="utf-8")
    log(f"import: created notebook {nid} ({NOTEBOOK_TITLE})")
    return nid


def _read_bucket_ids():
    ids = _load(NOTEBOOK_IDS_FILE) or {}
    legacy = _read_notebook_id()
    if legacy and "A_core" not in ids:
        ids["A_core"] = legacy
    return ids


def ensure_bucket_notebook(bucket, ids):
    if ids.get(bucket):
        return ids[bucket]
    title = BUCKETS[bucket]["title"]
    r = run(["create", title, "--json"], timeout=180)
    data = _loads(r.stdout) or {}
    nid = (data.get("notebook") or {}).get("id")
    if not nid:
        raise SystemExit(f"could not create notebook {title!r}: rc={r.returncode} "
                         f"out={(r.stdout or '')[:200]} err={(r.stderr or '')[:200]}")
    ids[bucket] = nid
    NOTEBOOK_IDS_FILE.write_text(json.dumps(ids, indent=2), encoding="utf-8")
    log(f"created notebook {bucket} = {nid} ({title})")
    return nid


def bucket_of(source):
    """Route a source to a topic notebook by its primary (first-surfacing) pass."""
    for t in source.get("topics", []):
        if t in TOPIC_TO_BUCKET:
            return TOPIC_TO_BUCKET[t]
    return "B_foundations"


def _live_urls(nid):
    """Normalized URLs currently in a notebook, so we never re-add or double-add."""
    r = run(["source", "list", "-n", nid, "--json"], timeout=300)
    raw = _loads(r.stdout)
    live = (raw.get("sources") if isinstance(raw, dict) else raw) or []
    ready = [s for s in live if str(s.get("status")) == "ready"]
    return {norm_url(s["url"]) for s in ready if s.get("url")}, len(live), len(ready)


def import_sources():
    """Import every not-yet-imported source into its topic notebook.

    Resumable and idempotent: sources that already carry an id are skipped, and each
    bucket's live URL set is read before adding so a source is never added twice.

    Note there is deliberately NO blind retry. The previous version retried on a
    non-zero exit, but `rpc_code=9` is returned for adds that actually SUCCEED
    server-side, so the retry produced duplicate sources that then burned slots
    against the 100-source cap. Verification against the live list replaces it.
    """
    sj_path = RESEARCH_DIR / "sources.json"
    sj = _load(sj_path)
    if not sj:
        raise SystemExit("no sources.json - run `extract` first")
    ids = _read_bucket_ids()

    todo = [s for s in sj["sources"] if not s.get("id")]
    if not todo:
        log("import: nothing to do, every source already has an id")
        return
    by_bucket = collections.defaultdict(list)
    for s in todo:
        by_bucket[bucket_of(s)].append(s)
    log(f"import: {len(todo)} sources across {len(by_bucket)} buckets")
    for b, items in sorted(by_bucket.items()):
        log(f"  {b}: {len(items)}")

    for bucket, items in sorted(by_bucket.items()):
        nid = ensure_bucket_notebook(bucket, ids)
        have, total, ready = _live_urls(nid)
        room = NOTEBOOK_SOURCE_CAP - ready
        log(f"=== {bucket} ({nid}) holds {ready} ready, room for {room}, "
            f"{len(items)} queued ===")
        if room <= 0:
            log(f"  SKIP {bucket}: already at cap")
            continue

        added = skipped = failed = 0
        for n, s in enumerate(items, start=1):
            if added >= room:
                log(f"  STOP {bucket} at cap after {added} adds; "
                    f"{len(items) - n + 1} left unimported")
                break
            if norm_url(s["url"]) in have:
                skipped += 1
                continue
            try:
                r = run(["source", "add", s["url"], "-n", nid,
                         "--timeout", "90", "--json"], timeout=180)
            except Exception as e:  # noqa: BLE001
                failed += 1
                log(f"  FAIL {s['url'][:80]} :: {str(e)[:120]}")
                continue
            # rc is unreliable here, so confirm by URL rather than trusting it.
            have.add(norm_url(s["url"]))
            if r.returncode == 0:
                added += 1
            else:
                added += 1   # counted; merge_uuids is the source of truth
                log(f"  rc={r.returncode} on {s['url'][:70]} (verifying at merge)")
            if (n % 20) == 0:
                log(f"  {bucket} progress {n}/{len(items)} added={added} "
                    f"skipped={skipped} failed={failed}")
        log(f"  {bucket} done: added={added} skipped={skipped} failed={failed}")
        merge_uuids(nid, sj, sj_path)
        sj = _load(sj_path)   # reload after merge writes

    log("import: all buckets processed")


def merge_uuids(nid, sj=None, sj_path=None):
    """Snapshot the notebook's source list and map uuids onto our index by URL."""
    sj_path = sj_path or (RESEARCH_DIR / "sources.json")
    sj = sj or _load(sj_path)
    r = run(["source", "list", "-n", nid, "--json"], timeout=300)
    (RESEARCH_DIR / "sources-raw.json").write_text(r.stdout or "", encoding="utf-8")
    raw = _loads(r.stdout)
    live = (raw.get("sources") if isinstance(raw, dict) else raw) or []

    by_url = {norm_url(s.get("url", "")): s for s in live if s.get("url")}
    by_title = {(s.get("title") or "").strip().lower(): s for s in live if s.get("title")}

    matched = 0
    for s in sj["sources"]:
        if s.get("id"):
            continue   # already matched in an earlier bucket; never re-point it
        hit = by_url.get(norm_url(s["url"])) or by_title.get((s["title"] or "").strip().lower())
        if hit and hit.get("id"):
            s["id"] = hit["id"]
            # Record WHICH notebook holds it. With the corpus split across buckets,
            # a bare uuid is not enough to go ask a follow-up question about a source.
            s["notebook"] = nid
            matched += 1
    # Rebuild across every source, not just this notebook's, so the map stays whole.
    sj["uuid_to_index"] = {s["id"]: s["index"] for s in sj["sources"] if s.get("id")}
    sj["notebooks"] = _read_bucket_ids()
    sj["imported_count"] = sum(1 for s in sj["sources"] if s.get("id"))
    sj_path.write_text(json.dumps(sj, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"merge_uuids: {nid[:8]} has {len(live)} sources, newly matched {matched}, "
        f"corpus imported total {sj['imported_count']}/{len(sj['sources'])}")


# ---------------------------------------------------------------- synthesize

def synthesize():
    """Ask each question against BOTH its topic notebook and the mixed core notebook.

    The corpus is split across buckets, so a single notebook only ever holds part of
    the evidence for a question. Asking the topic notebook gets depth; asking A_core
    (which spans all 14 passes) catches anything the partition put elsewhere. The two
    answers are stored side by side and reconciled when writing research-synthesis.md.
    """
    ids = _read_bucket_ids()
    if not ids:
        raise SystemExit("no notebooks - run `import` first")
    log("=== SYNTHESIZE START ===")
    for key, question in ASKS.items():
        bucket = TOPIC_TO_BUCKET.get(key, "B_foundations")
        targets = [(bucket, ids.get(bucket)), ("A_core", ids.get("A_core"))]
        for label, nid in targets:
            if not nid:
                log(f"SKIP {key}@{label}: notebook not created")
                continue
            suffix = "" if label == bucket else "__core"
            out_path = RESEARCH_DIR / f"{key}{suffix}.json"
            if out_path.exists() and out_path.stat().st_size > 1000:
                log(f"SKIP ask {key}@{label} (already have it)")
                continue
            try:
                # --new -y starts a fresh conversation so topics do not bleed.
                r = run(["ask", question, "--json", "-n", nid, "--new", "-y"], timeout=900)
                out_path.write_text(r.stdout or "", encoding="utf-8")
                data = _loads(r.stdout)
                nrefs = len(data.get("references", [])) if isinstance(data, dict) else 0
                alen = len(data.get("answer", "")) if isinstance(data, dict) else 0
                log(f"WROTE {out_path.name} rc={r.returncode} refs={nrefs} chars={alen}")
            except Exception as e:  # noqa: BLE001
                log(f"ERROR ask {key}@{label}: {e}")
    log("=== SYNTHESIZE DONE ===")


# ---------------------------------------------------------------- verify

def verify():
    """Every [sN] cited anywhere in references/ must resolve to a real source.

    Exists because claude-advisor's sources.json was gitignored then purged, which
    silently broke every [sNN] in its synthesis, and sales-playbook carries 15
    dangling citations from a dedup cleanup. Fail loudly instead.
    """
    sj = _load(RESEARCH_DIR / "sources.json")
    if not sj:
        raise SystemExit("no sources.json")
    valid = {s["index"] for s in sj["sources"]}
    pat = re.compile(r"\[s(\d+)(?:\s*,\s*s?(\d+))*\]")
    single = re.compile(r"s(\d+)")

    dangling, cited, files = {}, set(), 0
    for fp in sorted(REFERENCES_DIR.rglob("*.md")):
        text = fp.read_text(encoding="utf-8", errors="replace")
        hits = [int(n) for m in pat.finditer(text) for n in single.findall(m.group(0))]
        if not hits:
            continue
        files += 1
        for n in hits:
            cited.add(n)
            if n not in valid:
                dangling.setdefault(fp.name, set()).add(n)

    print(f"\nsources.json: {len(valid)} sources (max index s{max(valid) if valid else 0})")
    print(f"citations found in {files} reference file(s), {len(cited)} distinct")
    unused = len(valid) - len(cited & valid)
    print(f"uncited sources: {unused}")
    if dangling:
        print("\nDANGLING CITATIONS:")
        for name, ns in sorted(dangling.items()):
            print(f"  {name}: {', '.join('s'+str(n) for n in sorted(ns))}")
        return 1
    print("\nOK - every [sN] resolves.")
    return 0


if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "extract"
    if phase == "extract":
        extract()
    elif phase == "import":
        import_sources()
    elif phase == "merge":
        merge_uuids(_read_notebook_id())
    elif phase == "synthesize":
        synthesize()
    elif phase == "verify":
        sys.exit(verify())
    else:
        raise SystemExit(f"unknown phase: {phase} "
                         "(extract | import | merge | synthesize | verify)")

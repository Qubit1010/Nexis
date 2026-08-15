#!/usr/bin/env python3
"""Build the branding-advisor corpus: 14 deep research passes -> a tiered sources.json.

Two subcommands, both idempotent:

    python gather.py run       # the 14 deep passes -> passes/<key>.json  (resume-safe)
    python gather.py extract   # passes/*.json -> a deduped, tiered, capped sources.json
    python gather.py           # run, then extract

Cloned from .claude/skills/strategic-foundation/_research/gather.py, which was itself
collapsed out of seo-advisor's run_passes.py + build_corpus.py. Same Exa path, same
reason: NotebookLM auth for that account has been dead since 2026-07-14, and
research-backed-skills.md explicitly permits the direct-Exa fallback.

Evidence rules carried over unchanged, each of which was a real bug in an earlier run:
  - no blanket ".gov" or ".edu = confirmed" (a suffix carries no evidentiary signal)
  - a topic-token guard so an off-topic PDF cannot ride in on a trusted domain
  - a per-domain cap so one design agency's blog cannot dominate the corpus
  - confirmed-tier sources jump the global cap
  - indices are stable across refreshes, so existing [sN] citations never repoint

What is different here is the tier list. Branding evidence lives in marketing science
and consumer psychology journals rather than management and economics ones, so
CONFIRMED_DOMAINS is rebuilt around those publishers. This matters more than usual:
branding is the single most folklore-heavy topic this repo covers ("color increases
recognition by 80%", "consistent branding lifts revenue 23%"), and the whole value of
the skill is being able to separate the real findings from the repeated ones.

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

SOURCE_CAP = 280
PER_DOMAIN_CAP = 5

# Peer-reviewed research or primary data, versus a design agency or SaaS vendor making
# a case for its own service. Branding's empirical literature sits in marketing science
# and consumer psychology, so those publishers lead the list.
#
# Deliberately NOT here: hbr.org, fastcompany.com, and every "brand strategy agency"
# blog, however good. Also not here: designers' portfolio sites, which carry no claims
# at all. Also not researchgate.net or academia.edu, which mirror real papers but also
# host unreviewed preprints and slide decks from the same URL space.
CONFIRMED_DOMAINS = {
    # peer-reviewed / academic press
    "jstor.org", "sciencedirect.com", "springer.com", "link.springer.com",
    "nature.com", "wiley.com", "onlinelibrary.wiley.com", "tandfonline.com",
    "sagepub.com", "journals.sagepub.com", "cambridge.org", "oup.com",
    "academic.oup.com", "informs.org", "pubsonline.informs.org", "aeaweb.org",
    "nber.org", "ssrn.com", "papers.ssrn.com", "arxiv.org", "doi.org",
    "pnas.org", "emerald.com", "emeraldinsight.com", "aom.org", "journals.aom.org",
    "ncbi.nlm.nih.gov", "pmc.ncbi.nlm.nih.gov", "pubmed.ncbi.nlm.nih.gov",
    "frontiersin.org", "plos.org", "journals.plos.org", "mdpi.com",
    # Added after a tiering audit of the first extract. Science carried the Mehta &
    # Zhu red/blue cognition experiment and was being tiered practitioner purely
    # because it was not enumerated; ACM carries the HCI legibility and design-system
    # work that q8 and q16 depend on; APS publishes Psychological Science.
    # Deliberately NOT added in the same audit: academia.edu, researchgate.net and
    # citeseerx, which mirror real papers but also host preprints and slide decks, and
    # whose DOI originals are already in this corpus separately.
    "science.org", "dl.acm.org", "psychologicalscience.org",
    # Marketing science and consumer psychology specifically. Branding's primary
    # literature is here, not in the general management journals: the AMA publishes
    # Journal of Marketing and JMR, ACR publishes the Journal of Consumer Research
    # proceedings, and APA carries the perception and categorization work that the
    # color and logo-shape sections rest on.
    "ama.org", "journals.ama.org", "myama.org",
    "psycnet.apa.org", "apa.org",
    "acrwebsite.org",
    "palgrave.com", "link.palgrave.com",
    # Research institutes that are themselves the primary source for a body of work
    # this corpus leans on, enumerated rather than inferred from a suffix.
    # Ehrenberg-Bass is the whole distinctiveness-over-differentiation evidence base
    # and Q11 cannot be written honestly without it; MSI funds and publishes the
    # brand-equity measurement research.
    "marketingscience.info", "msi.org",
    # primary statistical and regulatory data (trademark and registration facts)
    "uspto.gov", "euipo.europa.eu", "wipo.int", "bls.gov", "census.gov",
}

# Somebody's opinion with no editorial process, or an image with no argument at all.
JUNK_DOMAINS = {
    "facebook.com", "linkedin.com", "twitter.com", "x.com", "instagram.com",
    "pinterest.com", "tiktok.com", "quora.com", "medium.com", "reddit.com",
    "youtube.com", "youtu.be", "slideshare.net", "scribd.com", "issuu.com",
    "substack.com", "coursehero.com", "studocu.com",
    "quizlet.com", "chegg.com", "cliffsnotes.com", "bartleby.com",
    # Portfolio and inspiration galleries. These rank extremely well for every logo
    # and visual-identity query and contain no text that could support a claim: the
    # page is the image. They would otherwise flood the q7-q9 passes.
    "behance.net", "dribbble.com", "awwwards.com", "logopond.com",
    "brandsoftheworld.com", "logolounge.com",
}

MIRROR_SUFFIXES = (".google.cn", ".google.co.jp", ".google.de", ".google.fr")

# A source has to be plausibly about branding, brand strategy, or the design and
# language systems that carry a brand. Without this guard a trusted publisher admits
# anything it happens to print, which is how an earlier corpus ranked a legislative
# calendar as a top-tier source.
TOPIC_TOKENS = (
    "brand", "rebrand", "identity", "positioning", "differenti", "distinctive",
    "archetype", "personality", "voice", "tone", "messaging", "tagline", "slogan",
    "story", "storytell", "narrative", "naming", "trademark", "semiotic",
    "logo", "wordmark", "monogram", "iconograph", "visual", "typograph",
    "typeface", "font", "lettering", "legibility", "color", "colour", "palette",
    "design system", "style guide", "guidelines", "packaging", "aesthetic",
    "equity", "awareness", "salience", "recall", "recognition", "recogniz",
    "perception", "attitude", "association", "loyalty", "reputation", "trust",
    "consumer", "customer", "marketing", "advertis", "communicat", "audience",
    "persona", "segment", "positioning", "influenc", "founder", "personal brand",
    "thought leader", "credibility", "authenticity",
    # Broad catch-alls. The guard exists to reject a document that rode in on a
    # trusted publisher while being clearly off-subject, not to be a precision
    # filter. Without plain "design" and "market" it rejects legitimate marketing
    # science indexes and design-research journals whose titles name neither the
    # brand nor the artifact.
    "design", "market", "product", "firm", "business", "commerc",
)

SUFFIX = (" Give specific numbers, named frameworks, effect sizes and concrete steps, "
          "and cite sources. Distinguish peer-reviewed evidence from agency or vendor "
          "opinion. Where a widely repeated statistic has no traceable primary source, "
          "say so explicitly. Where the sources disagree, preserve the disagreement "
          "rather than picking a side.")

# One deep pass per subject the hub has to be able to answer on. q12 is what audit mode
# runs on, so it targets failure modes and risk rather than construction.
QUERIES = {
    "q1_brand_identity_models": (
        "Brand identity models and brand equity frameworks: Aaker's brand identity "
        "planning model, Keller's customer-based brand equity pyramid, Kapferer's brand "
        "identity prism, what empirical support each has, how brand identity differs "
        "from brand image and brand reputation, and criticism of these models as "
        "untestable consultant scaffolding."
    ),
    "q2_brand_positioning": (
        "Brand positioning: how a brand claims a position in the customer's mind, "
        "positioning statement construction, perceptual mapping and its methodology, "
        "category entry points, the relationship between business positioning and brand "
        "positioning, and evidence on whether a clearly positioned brand outperforms an "
        "ambiguously positioned one."
    ),
    "q3_brand_personality_archetypes": (
        "Brand personality and brand archetypes: Jennifer Aaker's brand personality "
        "scale and its five dimensions, the psychometric validity and cross-cultural "
        "replication of that scale, Jungian brand archetypes and whether they have any "
        "empirical basis at all, brand anthropomorphism research, and evidence on "
        "whether brand personality congruence with self-concept predicts preference."
    ),
    "q4_brand_voice_messaging": (
        "Brand voice, tone of voice and messaging architecture: how to define and "
        "document a brand voice, tone-of-voice frameworks and dimensions, message "
        "hierarchies and messaging houses, linguistic research on corporate register "
        "and consumer response, evidence on whether conversational or formal brand "
        "language performs better, and how voice guidelines actually get used by "
        "writers in practice."
    ),
    "q5_brand_story_narrative": (
        "Brand storytelling and narrative: narrative transportation theory and its "
        "experimental evidence, the effect of story-form advertising on persuasion and "
        "recall, StoryBrand and other commercial narrative frameworks, founding-story "
        "authenticity research, and evidence on when narrative outperforms attribute "
        "claims and when it does not."
    ),
    "q6_naming_taglines": (
        "Brand naming and taglines: linguistic research on brand name sound symbolism "
        "and phonetics, descriptive versus suggestive versus arbitrary names, name "
        "memorability and pronounceability studies, trademark availability and "
        "registrability constraints, tagline recall research, and empirical work on "
        "whether a name change affects firm value."
    ),
    "q7_color_in_branding": (
        "Color in branding and marketing: peer-reviewed research on color and brand "
        "perception, Labrecque and Milne on brand color, color-appropriateness and "
        "brand-fit effects, color and arousal or approach-avoidance findings, cultural "
        "variation in color meaning, accessibility and contrast requirements, and the "
        "provenance of widely repeated color statistics such as the claim that color "
        "increases brand recognition by eighty percent."
    ),
    "q8_typography_branding": (
        "Typography in branding: empirical research on typeface personality and "
        "semantic associations, legibility and readability studies, the effect of font "
        "choice on brand perception and on perceived credibility, disfluency effects, "
        "serif versus sans-serif evidence, variable fonts and web font performance, and "
        "font licensing models for commercial brand use."
    ),
    "q9_logo_design_research": (
        "Logo design research: Henderson and Cote on logo design characteristics and "
        "recognition, descriptive versus abstract marks, logo complexity and "
        "naturalness effects, circular versus angular shape and its perceived meaning, "
        "logo redesign and consumer backlash research, evidence on whether a logo "
        "change affects sales or brand attitude, and how logos are actually tested."
    ),
    "q10_brand_guidelines_design_systems": (
        "Brand guidelines and design systems in practice: what a brand guidelines "
        "document contains and how it is structured, the shift from static brand books "
        "to living design systems and design tokens, governance and adoption of design "
        "systems in organizations, evidence on whether guidelines improve consistency "
        "in practice, and why brand guidelines are commonly ignored."
    ),
    "q11_distinctive_assets_consistency": (
        "Distinctive brand assets and mental availability: Byron Sharp and Jenni "
        "Romaniuk's work on distinctive brand assets, the distinctiveness versus "
        "differentiation argument in marketing science, category entry points, double "
        "jeopardy and the empirical generalizations of the Ehrenberg-Bass Institute, "
        "brand consistency research, and critiques of the Ehrenberg-Bass position."
    ),
    "q12_rebrand_risk": (
        "Rebranding risk and timing: empirical studies on rebranding outcomes and "
        "shareholder value, when a rebrand is justified versus cosmetic, corporate name "
        "change event studies, consumer reaction to identity change and brand-heritage "
        "loss, notable rebrand reversals and what caused them, and frameworks for "
        "deciding whether to evolve or replace an identity."
    ),
    "q13_personal_founder_branding": (
        "Personal branding and founder brands: research on personal branding as a "
        "construct, CEO and founder visibility effects on firm reputation and value, "
        "executive social media presence research, thought leadership and expertise "
        "signalling, authenticity and self-presentation research, parasocial "
        "relationships with founders, and the risk concentration of tying a company "
        "brand to one person."
    ),
    "q14_brand_measurement": (
        "Brand measurement: how brand equity is actually measured, brand awareness and "
        "brand salience metrics and the difference between them, unaided versus aided "
        "recall methodology, brand tracking study design and sample requirements, brand "
        "valuation methods and their criticism, share of search as a brand metric, and "
        "what a small business with no research budget can and cannot measure."
    ),
    # ---- remedial passes -------------------------------------------------
    # Same lesson strategic-foundation learned across six remedial passes: the popular
    # phrasing of a subject retrieves whatever dominates it commercially, and
    # re-asking in the register the academic literature actually uses returns a
    # non-overlapping and better source set.
    #
    # q13 was the worst retrieval failure in this corpus. It returned 10 results and
    # all 10 were LinkedIn personal profiles: the engines read "personal branding" and
    # "founder brand" as an instruction to find people who sell personal branding
    # services. Every one was correctly junked, leaving the section with zero sources.
    # The underlying research does exist, but almost none of it uses the phrase
    # "personal branding" - it is filed under CEO celebrity, human brands, executive
    # reputation and endorser credibility. This asks for those constructs by name and
    # deliberately avoids the popular term.
    "q15_founder_ceo_reputation_evidence": (
        "Empirical research on chief executive visibility and firm outcomes: CEO "
        "celebrity and its effects on firm performance and shareholder value, executive "
        "reputation research, human brands and consumer attachment to individuals, "
        "endorser and source credibility studies, self-presentation and impression "
        "management research in organizational settings, parasocial relationship "
        "research, and evidence on key-person concentration risk when a firm's identity "
        "depends on one individual."
    ),
    # q10 came back 4 confirmed against 13 practitioner, the thinnest section here.
    # "Brand guidelines" and "design systems" are practitioner vocabulary; the
    # equivalent academic literature is filed under corporate visual identity and its
    # management, which is a substantial empirical body this pass targets directly.
    "q16_corporate_visual_identity_management": (
        "Empirical research on corporate visual identity and its management: studies on "
        "corporate visual identity consistency and organizational outcomes, the "
        "antecedents of employee adherence to visual identity standards, corporate "
        "identity management research, standardization versus local adaptation of brand "
        "presentation across markets, and evidence on whether documented identity "
        "systems actually produce consistent execution."
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
    """confirmed = peer-reviewed or primary data; everything else is an agency or
    vendor making a case, and must be labelled as such.

    No blanket ".gov" or ".edu" rule on purpose. A university publishes research,
    course pages and advertising from one domain, so the suffix carries no evidentiary
    signal. Peer review is carried by the enumerated publishers instead.
    """
    d = domain_of(u)
    if d in CONFIRMED_DOMAINS or any(d.endswith("." + c) for c in CONFIRMED_DOMAINS):
        return "confirmed"
    return "practitioner"


def is_junk(url, title):
    d = domain_of(url)
    if d in JUNK_DOMAINS or any(d.endswith("." + j) for j in JUNK_DOMAINS):
        return "social/UGC"
    if any(d.endswith(m) for m in MIRROR_SUFFIXES):
        return "localized mirror"
    # Normalize separators to spaces so short tokens match as whole words. Plain
    # substring matching lets "hou-SEO-frepresentatives" through; \b would not help
    # either, since underscores count as word characters.
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

    def _attempt(extra):
        try:
            r = subprocess.run(
                [sys.executable, str(RESEARCH_PY), "--query", query + SUFFIX,
                 "--depth", "deep", "--json", *extra],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=1800,
            )
        except subprocess.TimeoutExpired:
            log(f"TIMEOUT {key}")
            return None, "timeout"
        try:
            return json.loads((r.stdout or "").strip()), None
        except Exception:  # noqa: BLE001
            return None, (f"rc={r.returncode} stdout={(r.stdout or '')[:200]!r} "
                          f"err={(r.stderr or '')[-300:]!r}")

    data, err = _attempt([])
    # The synthesis step calls an LLM; source discovery does not. When only the
    # synthesis fails - an exhausted OpenAI balance returns 429 insufficient_quota and
    # takes the whole run down with it - the pass is still worth having without its
    # report, because sources.json is built from `results` and never from `report`.
    # Retrying without synthesis turns a total pass failure into a missing summary.
    if data is None and err and "timeout" not in err:
        log(f"RETRY {key} without synthesis ({err[:120]})")
        data, err = _attempt(["--no-synth"])
    if data is None:
        log(f"FAIL {key} {err}")
        return
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"DONE {key} results={len(data.get('results', []))} "
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

    # 3. Cap per domain so no single agency blog dominates. Confirmed-tier is exempt:
    #    there is no such thing as too much primary research.
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
        "method": ("14 deep passes via the in-repo research skill (Exa+Tavily+Serper+Jina "
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
    """Every [sN] in this skill's references/ and in every spoke's must resolve.

    The spokes deliberately have no corpus of their own and cite back to this one, so
    a verify that only checked the hub would miss exactly the citations most likely to
    rot: the ones written in a different folder from the sources.json they point at.
    """
    sj = _load(RESEARCH_DIR / "sources.json") or {}
    valid = {s["index"] for s in sj.get("sources", [])}
    skills_dir = RESEARCH_DIR.parents[1]
    ref_dirs = [RESEARCH_DIR.parent / "references"] + [
        skills_dir / spoke / "references"
        for spoke in ("brand-strategy", "brand-voice", "brand-visual")
    ]
    bad = 0
    for refs in ref_dirs:
        if not refs.exists():
            continue
        for fp in sorted(refs.glob("*.md")):
            text = fp.read_text(encoding="utf-8")
            for n in {int(m) for m in re.findall(r"\[s(\d+)[,\]]", text)}:
                if n not in valid:
                    log(f"  BROKEN [s{n}] in {refs.parent.name}/{fp.name}")
                    bad += 1
    log(f"verify: {len(valid)} sources, {bad} broken citation(s)")
    return bad


def _selftest():
    """The evidence rules are the whole point of this file, so they get a check."""
    assert norm_url("http://WWW.Example.com/a/?utm_source=x#f") == "https://example.com/a"
    assert norm_url("https://example.com") == "https://example.com/"
    # marketing science and consumer psychology are this corpus's primary literature
    assert tier_of("https://journals.sagepub.com/doi/10.1509/jmkg.73.6.52") == "confirmed"
    assert tier_of("https://psycnet.apa.org/record/2012-1") == "confirmed"
    assert tier_of("https://www.marketingscience.info/distinctive-assets/") == "confirmed"
    # an agency or vendor making a case for its own service is not evidence
    assert tier_of("https://hbr.org/2024/02/rebranding") == "practitioner"
    assert tier_of("https://www.canva.com/learn/brand-guidelines/") == "practitioner"
    # a .edu suffix is not evidence: this is university marketing copy
    assert tier_of("https://www.phoenix.edu/articles/business/branding.html") == "practitioner"
    # the bug the topic guard exists for: trusted publisher, off-subject document
    assert is_junk("https://census.gov/119_legislative_schedule.pdf", "Legislative Schedule")
    assert is_junk("https://uspto.gov/trademark/basics", "Trademark basics") is None
    # portfolio galleries are images with no claim in them
    assert is_junk("https://dribbble.com/shots/123", "Logo concept") == "social/UGC"
    assert is_junk("https://linkedin.com/pulse/branding", "Branding") == "social/UGC"
    # short tokens must match as whole words, not substrings
    assert is_junk("https://example.com/fontanelle-anatomy", "Fontanelle") == "off-topic"
    assert is_junk("https://example.com/font-licensing", "Font licensing") is None
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

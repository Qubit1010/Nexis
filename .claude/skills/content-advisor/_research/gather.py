#!/usr/bin/env python3
"""Build the content-advisor corpus: 28 deep research passes -> a tiered sources.json.

Subcommands, all idempotent:

    python gather.py run       # the 28 deep passes -> passes/<key>.json  (resume-safe)
    python gather.py extract   # passes/*.json -> a deduped, tiered, capped sources.json
    python gather.py verify    # every [sN] in the hub + spoke references/ resolves
    python gather.py selftest  # the evidence + mode-routing rules, as executable asserts
    python gather.py           # run, then extract

Cloned from copywriting-advisor's, which came from branding-advisor -> strategic-foundation
-> seo-advisor's run_passes.py + build_corpus.py. Gather via Exa/Serper/Tavily/Jina, then
mirror into NotebookLM afterwards for the live-query tier (push_to_notebooklm.py).

Evidence rules carried over unchanged, each of which was a real bug in an earlier run:
  - no blanket ".gov" or ".edu = confirmed" (a suffix carries no evidentiary signal)
  - a topic-token guard so an off-topic PDF cannot ride in on a trusted domain
  - a per-domain cap so one agency blog cannot dominate the corpus
  - confirmed-tier sources jump the global cap
  - indices are stable across refreshes, so existing [sN] citations never repoint


THREE DEFECTS FIXED HERE THAT SILENTLY DAMAGED THE COPYWRITING CORPUS
---------------------------------------------------------------------
1. ONE SUFFIX FOR BOTH REGISTERS. The shared SUFFIX contained the words "peer-reviewed",
   which matches research.py's _SCI_HINT, and detect_mode checks _SCI_HINT before
   _CRAFT_HINT. Measured on copywriting's own 29 queries: 14/29 detect as practical bare,
   0/29 with the suffix attached. So every craft pass ran under `scientific`, which means
   Serper never ran, _craft_queries' site:youtube.com variant never fired, the
   _ACADEMIC_HOSTS exclusion never applied, and Exa ran category="research paper" against
   "show me landing page teardowns". The visible damage: 2 YouTube sources in 494, and a
   craft tier whose top domains include pdfs.semanticscholar.org and theseus.fi, a Finnish
   polytechnic thesis repository. That corpus documents the missing video tier as an
   honest weakness and blames the search engines. It was a config bug.
   FIX: EVIDENCE_SUFFIX / CRAFT_SUFFIX, and _selftest asserts the routing so it cannot
   regress the next time someone edits a suffix.

2. THE TOPIC GUARD DELETED THE SUBJECT. is_junk matched tokens of length <= 4 as whole
   words, but the token list holds truncated stems - blog, writ, post, hook, text, word.
   " blog " does not occur in real prose, so is_junk(title="Blogging in 2026") returned
   "off-topic". For a corpus about blogging, vlogging, memes, reels, shorts and posts that
   deletes the subject matter. FIX: threshold lowered to <= 3, which still catches the bug
   it was written for (seo inside houseofrepresentatives) while letting the stems work as
   the prefixes they were always meant to be.

3. PLATFORM DOCUMENTATION WAS UNREACHABLE. JUNK_DOMAINS holds the apexes, and is_junk
   matches d.endswith("." + j), so help.instagram.com, business.linkedin.com and
   support.tiktok.com were all killed by their apex entry. Copywriting's corpus contains
   zero linkedin.com, facebook.com, x.com, instagram.com and tiktok.com sources; its one
   platform document is support.google.com, which survived only because google.com was
   never junked. For copywriting that cost one pass. Here it is fatal: the primary source
   for what a Reel is, what aspect ratio it takes, what counts as a view and where
   LinkedIn truncates at "see more" is the platform's own documentation, and it changes
   quarterly. FIX: PLATFORM_DOC_HOSTS + PLATFORM_DOC_PATHS, bypassing the junk gate only
   and never the topic guard.


THE TIER LIST
-------------
Content marketing's empirical literature is media and communication research, computational
social science and multimedia learning - not the advertising psychology copywriting leaned
on. CONFIRMED_DOMAINS is rebuilt around those publishers.

Judgment calls, stated outright because they are judgment and not mechanism:

  - pewresearch.org, reutersinstitute.politics.ox.ac.uk and ofcom.org.uk are CONFIRMED,
    on the same grounds as copywriting's nngroup exception and arguably stronger: all three
    run probability or panel-based survey research, publish full methodology, questionnaires
    and weighting, and - unlike NN/g, which sells consulting - have nothing to sell.
    reutersinstitute.politics.ox.ac.uk is enumerated as a FULL HOST. Listing ox.ac.uk would
    confirm an entire university and break the no-blanket-.edu rule this file is built on.

    THE CAVEAT THAT SHIPS WITH THEM: they measure media consumption in a POPULATION. They
    support "X% of US adults regularly get news on TikTok". They do NOT support "video
    posts outperform text posts". A corpus that admits them without this line will launder
    descriptive population statistics into performance claims, which is the exact failure
    the three tiers exist to prevent.

  - statista.com is NOT confirmed, and is named here because it is the single largest
    laundering vector in this field: a paywalled RE-PUBLISHER of vendor numbers, presented
    with the visual grammar of a data source. Nor are thinkwithgoogle.com (Google's ad
    sales in a research costume), nielsen.com and comscore.com (syndicated measurement sold
    to the industry being measured), or edisonresearch.com - the closest call, since
    Infinite Dial uses a probability sample and publishes method, but Edison sells
    syndicated research to the broadcasters and podcast networks who benefit from the
    number. Rejected deliberately, recorded here so nobody promotes it later.

  - Every "State of Content Marketing" report is PRACTITIONER without exception, however
    large the sample: CMI, Semrush, HubSpot, Buffer, Hootsuite, Sprout Social, Wistia,
    Edelman, Backlinko, Chartbeat, Parse.ly, Socialinsider, RivalIQ, Similarweb. They
    measure their own customers or their own client base, publish no method, and sell the
    thing the number flatters.

  - warc.com and baymard.com are DROPPED from the inherited list. warc is a paywalled
    commercial intelligence service that was a questionable confirmed call for copywriting
    and is worse here; baymard is checkout and form usability, irrelevant to content formats.

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

# The skills that cite this corpus. verify() walks these too, because a citation written
# in a different folder from the sources.json it points at is exactly the one most likely
# to rot unnoticed.
#
# Wider than copywriting's 2-tuple on purpose. content-advisor is corpus owner not just for
# its two spokes but for every content execution skill in the repo, all of which currently
# carry ZERO [sN] - they were written before there was a corpus to cite. Enumerating them
# now means verify() covers them the moment the first citation lands; adding them later
# means it silently skips exactly the files most likely to rot.
#
# blog-writer is deliberately excluded from the walk below: it keeps its own 83-source
# AEO/GEO corpus and its own [sN] namespace, so checking it would report every one of its
# 214 valid citations as broken.
SPOKES = (
    "content-strategy", "content-production",
    "content-engine", "post-creator", "shorts-creator", "carousel",
    "reel-creator", "linkedin-infographics", "podcast-repurposer",
    "client-content-creator",
)

# The cap governs how much PRACTITIONER material may accumulate; confirmed, craft and
# first-party platform docs have their own allocations below.
SOURCE_CAP = 560
PER_DOMAIN_CAP = 5
# youtube.com is one domain holding many distinct teardowns, so the standard cap would
# reduce the whole video tier to five videos.
# Widened 2026-08-31 from 16: youtube.com was already at the old cap when q29/q30 (named
# LinkedIn/carousel creator teardowns, YouTube-heavy) were added, which would have silently
# capped out exactly the sources those passes exist to bring in.
CRAFT_DOMAIN_CAP = 24
# Reserved allocation so the craft tier cannot be squeezed out by whichever vendor pages
# happened to rank. 140 rather than copywriting's 90 because this corpus covers 19 formats
# across 8 platforms, and because copywriting's craft tier was never honestly measured -
# 63 of its 75 came in by provenance while the craft passes were misrouted to scientific,
# so that number describes a bug, not a floor.
# Widened 2026-08-31 from 140: the tier was already full when q29/q30 were added, and
# extract() never evicts an already-locked source regardless of rank, so new sources need
# headroom to land rather than being ranked against an already-saturated top-140.
CRAFT_RESERVE = 180
# First-party platform documentation gets its own cap and its own allocation. At
# PER_DOMAIN_CAP = 5 the corpus would hold five support.tiktok.com pages total across 19
# formats, and without a reserved allocation the practitioner slice would eat them.
PLATFORM_DOC_CAP = 12
PLATFORM_DOC_RESERVE = 45

# Peer-reviewed research or primary data, versus an agency or SaaS vendor making a case
# for its own service. Content marketing's empirical literature sits in media and
# communication research, computational social science and multimedia learning, so those
# publishers lead the list.
#
# Deliberately NOT here (see the header for the reasoning on each): statista.com,
# thinkwithgoogle.com, nielsen.com, comscore.com, edisonresearch.com, hbr.org, every
# content-marketing agency blog, every "State of X" vendor report. Also not
# researchgate.net or academia.edu, which mirror real papers but also host unreviewed
# preprints from the same URL space.
CONFIRMED_DOMAINS = {
    # peer-reviewed / academic press
    "jstor.org", "sciencedirect.com", "springer.com", "link.springer.com",
    "nature.com", "wiley.com", "onlinelibrary.wiley.com", "tandfonline.com",
    "sagepub.com", "journals.sagepub.com", "cambridge.org", "oup.com",
    "academic.oup.com", "informs.org", "pubsonline.informs.org", "aeaweb.org",
    "nber.org", "ssrn.com", "papers.ssrn.com", "arxiv.org", "doi.org",
    "pnas.org", "emerald.com", "emeraldinsight.com", "mdpi.com",
    "ncbi.nlm.nih.gov", "pmc.ncbi.nlm.nih.gov", "pubmed.ncbi.nlm.nih.gov",
    "frontiersin.org", "plos.org", "journals.plos.org",
    "science.org", "psychologicalscience.org",
    # Marketing science and consumer psychology. Kept from copywriting because the
    # firm-generated-content, seeding and advertising-elasticity literature lives here.
    "ama.org", "journals.ama.org", "myama.org",
    "psycnet.apa.org", "apa.org", "acrwebsite.org",
    "journalofadvertisingresearch.com",
    "palgrave.com", "link.palgrave.com",
    # Computational social science. This is where the diffusion, cascade, virality and
    # feed-recommender work actually lives, and it is the half copywriting had no need
    # for. ICWSM proceedings are hosted at ojs.aaai.org/index.php/ICWSM - "AAAI/ICWSM"
    # is not a domain, and without this exact host every ICWSM paper tiers practitioner.
    "ojs.aaai.org", "aaai.org", "dl.acm.org", "acm.org", "sigir.org",
    "aclanthology.org", "ieee.org", "ieeexplore.ieee.org",
    "journals.plos.org", "epjdatascience.springeropen.com",
    # Original empirical usability research. Same deliberate exception copywriting made:
    # these ARE the primary data for how people read and scan a page, and they publish
    # method with result. baymard is dropped here - checkout and form usability has no
    # bearing on content formats.
    "nngroup.com",
    # Population-level media consumption, on the same grounds. Probability or panel-based
    # sampling, full published methodology, questionnaires and weighting, and nothing to
    # sell. Read the header caveat before citing any of them: they measure what people
    # consume, never what performs.
    "pewresearch.org", "reutersinstitute.politics.ox.ac.uk", "ofcom.org.uk",
    # Normative standards and primary regulatory text. WCAG is the source for captions,
    # transcripts and alt text; the FTC rules govern sponsored content, creator content
    # and reviews, which is law rather than style.
    "w3.org", "ftc.gov", "asa.org.uk", "bls.gov", "census.gov", "sec.gov",
}

# The craft canon: where practitioners actually teach and demonstrate content production.
#
# Kept deliberately thin. Content marketing has no swipe-file canon comparable to
# copywriting's - there is no reallygoodemails for podcasts - so the PROVENANCE rule in
# tier_of carries this tier, not the allowlist. That is the design, not an oversight.
#
# One warning against reading copywriting's numbers as a precedent: 63 of its 75 craft
# sources came in by provenance, but its craft passes were misrouted to scientific mode,
# so what provenance was actually catching was semanticscholar PDFs and a Finnish thesis
# repository. With the routing fixed, provenance will catch a genuinely different
# population and there is no prior measurement of how large it is. The named hosts below
# exist to give the tier a floor if provenance under-delivers.
#
# These are a SEPARATE tier, never merged into practitioner. A craft source may show how
# to make something; it may never support a factual claim. tier_of() returns "craft" and
# the factcheck mode ignores that tier entirely.
CRAFT_DOMAINS = {
    # named practitioner canon for content and editorial specifically
    "animalz.co", "superpath.co", "marketingexamples.com", "growth.design",
    "everyonehatesmarketers.com", "growthinreverse.com", "newsletteroperator.com",
    "thepublishpress.com", "copyblogger.com", "cxl.com",
    # video and audio craft. NotebookLM ingests YouTube natively via
    # `source add --type youtube`, so a video is transcribed and queryable rather than a
    # dead link - which is the argument for including them at all. This is also the tier
    # copywriting's corpus never got: 2 videos in 494, because Serper never ran.
    "youtube.com", "youtu.be",
}

# Somebody's opinion with no editorial process, or a page with no argument in it.
# Medium, Substack and Reddit stay junked by Aleem's explicit call: highest volume,
# lowest signal, and impossible to tier honestly.
#
# Note the tension this list carries HERE that it did not carry for copywriting: the
# apexes below are this skill's own subject matter. That is what PLATFORM_DOC_HOSTS
# resolves - the feed stays junk, the documentation does not.
JUNK_DOMAINS = {
    "facebook.com", "linkedin.com", "twitter.com", "x.com", "instagram.com",
    "pinterest.com", "tiktok.com", "quora.com", "medium.com", "reddit.com",
    "slideshare.net", "scribd.com", "issuu.com",
    "substack.com", "coursehero.com", "studocu.com",
    "quizlet.com", "chegg.com", "cliffsnotes.com", "bartleby.com",
    # Freelance marketplaces and job boards, which rank for "content writer" and carry
    # service listings rather than evidence.
    "upwork.com", "fiverr.com", "indeed.com", "glassdoor.com", "ziprecruiter.com",
}

# Named-creator primary sources living on an otherwise-junked domain. Added 2026-08-31,
# Aleem's explicit call: q29/q30 exist specifically to find named creators explaining
# their OWN technique, and several of the best instances are the creator's own
# linkedin.com or substack.com post - the same domains JUNK_DOMAINS discards as
# undifferentiated "social/UGC" feed noise. Deliberately an exact-URL allowlist, not a
# domain or name-pattern rule: broadening this to "any post by someone in a name list"
# would readmit exactly the high-volume, low-signal content JUNK_DOMAINS exists to keep
# out. Each entry below is the creator's OWN post about their OWN technique (a
# third-party post merely analyzing a creator, e.g. someone else's teardown hosted as a
# LinkedIn post, does not qualify and is not on this list - that is still "social/UGC").
# Still has to clear the topic-relevance guard below like everything else.
# Raw, not normalized - norm_url() isn't defined until further down this file, and
# is_junk() normalizes both sides at call time instead (see there).
CREATOR_PRIMARY_SOURCE_URLS = (
    "https://justinwelsh.substack.com/p/how-to-write-compelling-long-form",
    "https://www.linkedin.com/posts/justinwelsh_my-strategy-when-i-started-was-pretty-basic-activity-7415011488983203840-7Rmy",
    "https://www.linkedin.com/posts/rachelkarten_i-asked-800-social-media-professionals-what-activity-7480303141582905344-smTt",
    "https://www.linkedin.com/posts/petar-delev-342509177_instagram-carousels-are-outperforming-reels-activity-7475907490027651073-FsfQ",
)

# Craft sources hand-verified as genuinely on-target, guaranteed a slot in CRAFT_RESERVE
# ahead of the score-based ranking. Added 2026-08-31 after discovering WHY q29/q30 (the
# named-creator passes commissioned specifically to fix content-advisor's thin,
# SaaS-blog-only LinkedIn/carousel craft tier) got ranked to the bottom and cut even
# after CRAFT_RESERVE was widened for them: every one of their results came back from
# Exa with best_score=0.0 (confirmed live - Exa's API genuinely does not populate a
# score for type="auto" search, this is not a bug in this repo's adapter code), while
# competing candidates from OTHER, older craft passes came back from Tavily with real
# scores (0.5-0.6). fuse.py's tie-break sorts on that score, so an Exa-only result is
# structurally indistinguishable from a low-quality one under the current ranking,
# regardless of what it actually contains. That is a real gap in the shared research
# pipeline's cross-engine score normalization, worth fixing there for every skill that
# depends on it - out of scope for this file to fix globally, so it is worked around
# locally instead: sources reviewed and confirmed to be a named creator's own technique
# or a real third-party teardown of one (as opposed to another generic scheduling-tool
# listicle from the same pass, which still competes normally and can still lose) are
# pinned here rather than left to a tie-break the ranking signals cannot actually make.
PINNED_CRAFT_URLS = (
    "https://autoposting.ai/blog/justin-welsh",
    "https://www.viralbrain.ai/blog/dan-koes-minimalist-playbook-for-high-agency-posts",
    "https://voicemoat.com/blog/hook-patterns-naval-paul-graham-sahil-bloom",
    "https://justinwelsh.substack.com/p/how-to-write-compelling-long-form",
    "https://www.100mclub.com/p/justin-welsh-grew-to-10m-making-every-post-look-different",
    "https://www.mylance.co/blog/what-actually-works-on-linkedin-895-post-study",
    "https://blog.terabox.com/insights/dan-koe-ai-content-playbook-llm-prompts",
    "https://moderncreator.app/2026-07-25-ash-harris-claude-carousels-cheat-code-viral-instagram-carousels-course",
    "https://moderncreator.app/2026-05-28-duncan-rogoff-ai-automation-how-i-use-claude-code-to-make-insane-instagram-carousels",
    "https://adlibrary.com/posts/carousel-ad-examples-2026",
    "https://www.linkedin.com/posts/rachelkarten_i-asked-800-social-media-professionals-what-activity-7480303141582905344-smTt",
    "https://www.linkedin.com/posts/petar-delev-342509177_instagram-carousels-are-outperforming-reels-activity-7475907490027651073-FsfQ",
)

# First-party platform documentation. The primary source for what a format IS on the
# platform that defines it: aspect ratios, length limits, what counts as a view, where
# the feed truncates, what the ranking system is stated to optimise for. Nothing else
# supplies that, and it changes quarterly, so a corpus that junks it has no floor under
# its format tables.
#
# A HOST allowlist, never an apex. linkedin.com is a feed of posts; business.linkedin.com
# is documentation. The apexes stay junk.
#
# TIERING: these are PRACTITIONER, never confirmed - a platform documenting its own
# product has a commercial interest and publishes no method - but they carry
# "first_party": true in sources.json and render as [P*] in the synthesis, with one rule
# stated once: authoritative for what the platform REQUIRES or DEFINES, quoted with a
# retrieval date, never evidence that anything WORKS.
PLATFORM_DOC_HOSTS = {
    "developers.facebook.com", "engineering.fb.com", "about.fb.com",
    "transparency.meta.com",
    "help.instagram.com", "about.instagram.com", "creators.instagram.com",
    "business.linkedin.com", "engineering.linkedin.com",
    "help.x.com", "developer.x.com", "business.x.com", "blog.x.com",
    "help.twitter.com", "developer.twitter.com", "blog.twitter.com",
    "support.tiktok.com", "ads.tiktok.com", "newsroom.tiktok.com",
    "developers.tiktok.com", "business-api.tiktok.com",
    "help.pinterest.com", "business.pinterest.com", "developers.pinterest.com",
    "businesshelp.snapchat.com", "forbusiness.snapchat.com", "values.snap.com",
    "redditinc.com", "business.reddithelp.com", "support.reddithelp.com",
    "support.substack.com", "on.substack.com",
    "podcasters.spotify.com", "podcasters.apple.com", "newsroom.spotify.com",
    "blog.youtube", "creatoracademy.youtube.com", "support.youtube.com",
    "support.google.com",
}

# Docs living under a PATH on the same apex as the feed. A host allowlist cannot reach
# these, and Meta and LinkedIn put most of their real documentation here.
PLATFORM_DOC_PATHS = (
    ("facebook.com", "/business/help"), ("facebook.com", "/business/ads-guide"),
    ("instagram.com", "/creators"),
    ("linkedin.com", "/help/linkedin"), ("linkedin.com", "/business"),
    ("tiktok.com", "/business"), ("tiktok.com", "/creator-academy"),
    ("x.com", "/en/using-x"),
)


def is_platform_doc(url):
    """First-party platform documentation, by host or by host+path prefix."""
    d = domain_of(url)
    if d in PLATFORM_DOC_HOSTS:
        return True
    path = urlsplit(url).path.lower()
    return any(d == h and path.startswith(p) for h, p in PLATFORM_DOC_PATHS)


MIRROR_SUFFIXES = (".google.cn", ".google.co.jp", ".google.de", ".google.fr")

# A source has to be plausibly about persuasive writing, the psychology under it, or
# how people read it. Without this guard a trusted publisher admits anything it happens
# to print, which is how an earlier corpus ranked a legislative calendar as a top-tier
# source.
TOPIC_TOKENS = (
    # the formats
    "blog", "article", "guide", "case stud", "whitepaper", "white paper", "ebook",
    "e-book", "newsletter", "video", "vlog", "short", "reel", "tiktok", "podcast",
    "audio", "webinar", "livestream", "live stream", "infographic", "meme", "thread",
    "carousel", "post", "caption", "listicle", "explainer", "tutorial", "long-form",
    "long form", "pillar", "lead magnet", "gated", "episode", "transcript", "subtitle",
    "thumbnail", "chapter", "series", "template",
    # the platforms and channels
    "youtube", "instagram", "linkedin", "tiktok", "facebook", "twitter", "threads",
    "pinterest", "snapchat", "reddit", "substack", "spotify", "social media", "social",
    "platform", "feed", "algorithm", "recommend", "channel", "creator", "influencer",
    "publisher", "media", "newsroom", "journalis",
    # the strategy
    "content", "strategy", "calendar", "cadence", "frequenc", "publish", "distribut",
    "amplif", "syndicat", "repurpos", "cluster", "evergreen", "trending", "viral",
    "thought leader", "educational", "promotional", "user generated", "user-generated",
    "ugc", "branded content", "native advertis", "sponsor", "editorial", "seed",
    "share of voice", "owned media", "earned media", "paid media", "brand safety",
    # how it is consumed
    "attention", "engagement", "engage", "retention", "watch time", "dwell", "scroll",
    "skim", "scan", "read", "readab", "legib", "comprehen", "recall", "memor", "learn",
    "cognitive", "dual coding", "multimedia", "narrative", "story", "storytell",
    "transportation", "parasocial", "credibil", "trust", "expertise", "authorit",
    "source", "humor", "humour", "emotion", "arousal", "curios", "novelty", "decay",
    "half-life", "diffus", "contagion", "shar", "transmis", "network", "cascade",
    # the outcome and its measurement
    "conversion", "convert", "click", "click-through", "clickthrough", "view",
    "impression", "reach", "subscrib", "follow", "churn", "unsubscrib", "lead",
    "pipeline", "revenue", "roi", "attribut", "incremental", "lift", "awareness",
    "consideration", "funnel", "journey", "touchpoint", "benchmark", "metric",
    "measur", "analytics", "audience",
    # method
    "experiment", "randomi", "field study", "a/b", "split test", "meta-analy",
    "replicat", "effect size", "sample size", "statistical", "survey", "panel",
    "longitudinal", "causal", "quasi-experiment", "observational", "regression",
    # search era and AI
    "search", "seo", "aeo", "geo", "answer engine", "generative engine", "ai search",
    "ai overview", "citation", "retriev", "rank", "query", "llm", "language model",
    "chatbot", "generative ai", "ai-generated", "ai generated", "synthetic",
    "disclosure", "provenance", "watermark", "detect",
    # accessibility and standards
    "accessib", "wcag", "alt text", "plain language",
    # broad catch-alls. The guard exists to reject a document that rode in on a
    # trusted publisher while being clearly off-subject, not to be a precision filter.
    "consumer", "customer", "market", "brand", "messag", "communicat", "writ", "text",
    "language", "linguistic", "word", "web", "online", "digital", "user", "product",
    "business", "commerc", "b2b", "b2c",
)

# TWO suffixes, not one. See defect 1 in the header: a single suffix containing the words
# "peer-reviewed" matched _SCI_HINT and forced every craft pass into scientific mode, which
# meant Serper never ran and the video tier never existed.
#
# EVIDENCE_SUFFIX must keep its research-register vocabulary; that is what routes it.
EVIDENCE_SUFFIX = (
    " Give specific numbers, named frameworks, effect sizes and concrete steps, and cite "
    "sources. Distinguish peer-reviewed evidence from agency or vendor opinion. Where a "
    "widely repeated statistic has no traceable primary source, say so explicitly. Where "
    "the sources disagree, preserve the disagreement rather than picking a side.")

# CRAFT_SUFFIX contains no _SCI_HINT token (no "study", "paper", "journal", "trial",
# "peer-reviewed", "effect size") and no _PERSON_HINT token. Verified by _selftest.
CRAFT_SUFFIX = (
    " Show concrete worked examples, named brands and creators, current platform "
    "specifications with dates, and step-by-step technique. Prefer teardowns, annotated "
    "breakdowns and practitioner walkthroughs over summaries. Where a widely repeated "
    "number has no traceable origin, say so.")

# One deep pass per subject the hub has to be able to answer on. q16 is what the
# factcheck mode leans on hardest, so it targets provenance and replication directly
# rather than technique.
# 28 deep passes in two registers.
#
# EVIDENCE (q1-q18) ends with EVIDENCE_SUFFIX and routes `scientific`.
# CRAFT    (q19-q28) ends with CRAFT_SUFFIX and routes `practical`.
# _selftest asserts that routing. Do not edit a query without re-running it.
#
# VOCABULARY IS THE WHOLE GAME IN THE EVIDENCE HALF. Five of these subjects have no
# literature under the industry's name for them, and asking in the industry's words
# returns the industry. "Content marketing ROI" retrieves CMI and Demand Metric;
# "firm-generated content" retrieves the econometrics. "Content half-life" retrieves
# Chartbeat; "decay of collective attention" retrieves the PNAS paper it was derived
# from. Copywriting learned this the expensive way - its email pass returned 0 confirmed
# sources because "subject line" is vendor vocabulary - and needed 4 remedial passes.
#
# Three subjects are deliberately NOT here because a neighbouring corpus already owns
# them and a pass would re-retrieve it: blog on-page structure and article AEO/GEO
# (blog-writer, 83 sources), topic clusters and AI search (seo-advisor), and headlines,
# CTAs, subject lines and social proof (copywriting-advisor, 494 sources). Cross-cite
# those; never re-buy them.
QUERIES = {
    # ---------------------------------------------------------------- evidence
    "q1_firm_generated_content_effects": (
        "Econometric and causal research on firm-generated content and branded content "
        "in social media: measured effects of company-published content on customer "
        "behaviour and sales, long-term versus short-term effects of brand "
        "communication, advertising elasticity meta-analysis, whether owned-media "
        "content produces incremental revenue, and selection bias when firms report "
        "the performance of their own content."
    ),
    "q2_video_engagement_retention": (
        "Empirical research on video engagement and retention: how production style "
        "affects engagement in large-scale video data, viewer drop-off and completion "
        "curves, optimal video length evidence, cognitive theory of multimedia "
        "learning, the modality redundancy and segmenting principles, talking-head "
        "versus screencast presentation, and captions and subtitles affecting "
        "comprehension and retention."
    ),
    "q3_short_form_video_feeds": (
        "Research on short-form video feeds and algorithmic recommendation: how "
        "recommender exposure shapes what gets watched, engagement and completion in "
        "vertical short video, audio-off and sound-off viewing, autoplay and loop "
        "effects, and measurement of creator reach distribution in feed-ranked systems "
        "rather than follower-ranked systems."
    ),
    "q4_podcast_audio_consumption": (
        "Research on podcast and spoken-audio consumption: listening behaviour and "
        "completion rates, episode length and listener retention, host-read advertising "
        "efficacy and parasocial relationship with hosts, discovery and subscription "
        "mechanics, and how a podcast download is counted and measured compared with a "
        "video view."
    ),
    "q5_live_streaming_synchronous": (
        "Research on live and synchronous video: live streaming commerce and its "
        "measured effects on purchase, real-time interactivity and social presence, "
        "viewer attrition over the duration of a live session, synchronous versus "
        "asynchronous delivery in online instruction and completion, and whether live "
        "attendance predicts later action better than recorded viewing."
    ),
    "q6_visual_information_design": (
        "Research on visual information design and comprehension: graphical perception "
        "and the accuracy of different visual encodings, dual coding theory and the "
        "picture superiority effect, data visualization literacy, misleading chart "
        "encodings, whether adding imagery to text improves recall, and accessibility "
        "requirements for images and alternative text."
    ),
    "q7_social_post_engagement": (
        "Research on what drives engagement with social media posts: content features "
        "predicting sharing and virality, informativeness and emotional content in "
        "brand posts related to engagement, message characteristics predicting retweets "
        "and reshares, image versus text versus link post performance measured in field "
        "data, and post length related to engagement."
    ),
    "q8_newsletter_owned_channel": (
        "Research on email newsletters as an owned audience channel: subscriber list "
        "growth and attrition, unsubscribe and disengagement drivers, sending frequency "
        "related to churn, paid newsletter subscription conversion and retention, the "
        "economics of creator-operated newsletters, and how Apple Mail Privacy "
        "Protection changed what an open rate measures."
    ),
    "q9_diffusion_cascades_virality": (
        "Research on the diffusion of online content: the size and shape of information "
        "cascades, what fraction of content spreads beyond one step, structural virality "
        "versus popularity, predictability of cascade size, memetic mutation and "
        "remixing as content spreads, and the role of network position versus content "
        "features in transmission."
    ),
    "q10_ugc_creative_asset": (
        "Research on user-generated and creator-produced content as a marketing asset: "
        "consumer-generated advertising effects, creator content compared with "
        "brand-produced content in the same placement, brand community content, "
        "perceived authenticity and its effects, sponsored content disclosure effects "
        "on persuasion, and regulations governing creator endorsement."
    ),
    "q11_source_credibility_expertise": (
        "Research on source credibility and perceived expertise in communication: "
        "credibility scale research and its dimensions, expertise and trustworthiness "
        "cues affecting persuasion, author identity and byline effects, organisational "
        "versus individual voice, demonstrated experience effects on judged competence, "
        "and how audiences evaluate authority in online information."
    ),
    "q12_message_frequency_scheduling": (
        "Research on message frequency and scheduling: continuity versus pulsing versus "
        "flighting advertising schedules, recency planning and the frequency debate, "
        "brand post frequency related to engagement and unfollowing in field data, "
        "advertising wearout and diminishing returns from repeated exposure, and how "
        "often an organisation can publish before per-item response declines."
    ),
    "q13_seeding_amplification_distribution": (
        "Research on seeding and amplification of marketing content: seeding strategies "
        "for viral marketing and whether targeting hubs or bridges or fringe members "
        "produces larger cascades, earned versus paid exposure and their relative "
        "contribution in media mix modelling, syndication and duplicate distribution "
        "effects, and field experiments comparing organic reach against paid "
        "amplification of the same asset."
    ),
    "q14_attention_decay_refresh": (
        "Research on the decay of attention to published content: novelty and the decay "
        "of collective attention, the temporal profile of views and shares after "
        "publication, how long published material continues attracting traffic and how "
        "that differs between search-driven and feed-driven distribution, whether "
        "updating a document restores its audience, and measured lifespans of news "
        "versus reference material."
    ),
    "q15_content_incrementality_attribution": (
        "Research on measuring the incremental return of marketing content: the "
        "difficulty of measuring advertising returns from observational data, "
        "discrepancies between experimental and observational attribution estimates, "
        "multi-touch attribution validity, the evidence behind claims that buyers "
        "complete most of the purchase journey before contacting a vendor, and the "
        "evidence for the proportion of a market in-market at any time."
    ),
    "q16_ai_generated_content": (
        "Research on AI-generated marketing and editorial content: whether "
        "machine-generated content performs comparably to human-written content in "
        "field tests, detection of synthetic text and its reliability, disclosure and "
        "labelling effects on audience trust, provenance and watermarking standards, "
        "and whether non-article media types such as video transcripts, PDF documents, "
        "podcast show notes and image alternative text are cited differently from HTML "
        "passages by generative answer engines."
    ),
    "q17_folklore_provenance": (
        "Tracing the origin of widely repeated content marketing statistics and whether "
        "each has a traceable primary source: the claim that buyers are 57 or 70 "
        "percent through the purchase journey before contacting sales, the claim that "
        "content marketing costs 62 percent less and generates three times the leads, "
        "the 80/20 and 4-1-1 ratios of educational to promotional material, the claim "
        "that video generates 1200 percent more shares, the claim that 85 percent of "
        "video is watched without sound, the claim that a buyer needs seven touches, "
        "the claim that one video repurposes into thirty pieces, and the 95-5 rule. "
        "For each, identify whether a primary source exists, who published it, whether "
        "the method was disclosed, and whether independent replication exists."
    ),
    "q18_metric_definitions": (
        "How engagement metrics are defined and whether they are comparable across "
        "platforms: what duration counts as a video view on different services, how "
        "impressions and reach are distinguished, how a podcast download is defined by "
        "the measurement guidelines, what an engagement rate divides by, how "
        "platform-reported metrics have been restated or corrected, and the "
        "methodological problems with comparing view counts between platforms."
    ),

    # ---------------------------------------------------------------- craft
    "q19_written_gated_assets_craft": (
        "How to structure long-form written content assets in 2026: definitive guides "
        "and pillar pages, whitepapers, ebooks and gated downloads. Show the section "
        "order that works, how long each format runs, how to open one, how to structure "
        "a gated asset differently from an ungated one, whether gating is worth the drop "
        "in reach, and what a strong example of each looks like."
    ),
    "q20_case_study_craft": (
        "How to write a customer case study that persuades in 2026: the structure that "
        "works, how to open one, how much narrative versus numbers, how to handle "
        "situations where the client will not disclose results, how long it should run, "
        "how to format it for a website versus a sales deck versus a social post, and "
        "annotated breakdowns of case studies that are considered strong."
    ),
    "q21_newsletter_craft": (
        "How to write and structure an email newsletter in 2026: the section order that "
        "works, how to open an issue, single-topic versus roundup formats, how long an "
        "issue should run, sending rhythm, how to grow a list from zero, plain text "
        "versus designed layouts, and annotated breakdowns of newsletters that are "
        "considered excellent."
    ),
    "q22_longform_video_youtube_craft": (
        "How to structure a long-form YouTube video in 2026: opening technique in the "
        "first thirty seconds, retention editing and pattern interrupts, pacing, "
        "chapters, thumbnail and title conventions, how creators use their own "
        "retention graphs to re-cut, description and caption formatting, and annotated "
        "breakdowns of channels that do this well."
    ),
    "q23_short_form_video_craft": (
        "How to make short-form vertical video in 2026 for TikTok, Instagram Reels and "
        "YouTube Shorts: opening technique in the first three seconds, loop and rewatch "
        "construction, on-screen text and caption conventions, sound and trending audio "
        "use, length choices, how the three platforms differ in practice, and annotated "
        "breakdowns of accounts that perform consistently."
    ),
    "q24_podcast_production_craft": (
        "How to produce a podcast in 2026: episode structure, cold opens and intros, "
        "episode length choices, interview technique and preparation, show notes and "
        "chapter formatting, how to launch a new show, publishing rhythm, and how "
        "established shows structure an episode from opening to close."
    ),
    "q25_webinar_live_craft": (
        "How to run a webinar or live session in 2026: session structure and running "
        "order, how to open, keeping attention across the full session, interaction and "
        "polling technique, length choices, registration and reminder sequences, "
        "handling the drop-off partway through, and how to repurpose the recording."
    ),
    "q26_visual_formats_craft": (
        "How to design infographics, social carousels and memes in 2026: how to "
        "sequence a carousel and how many frames it should run, opening frame "
        "technique, text density per frame, how to lay out an infographic so the "
        "hierarchy reads, formatting a document carousel for LinkedIn, meme format "
        "conventions and when a brand should and should not use one, and annotated "
        "breakdowns of each that work."
    ),
    "q27_social_text_craft": (
        "How to write text posts for LinkedIn, X and Threads in 2026: opening line "
        "technique before the truncation point, line breaks and white space, how to "
        "construct a multi-post thread and how to close one, post length choices, "
        "hashtag and link conventions and whether they still matter, differences "
        "between the three platforms in practice, and annotated breakdowns of accounts "
        "that post consistently well."
    ),
    "q28_platform_specs_craft": (
        "Current official specifications for publishing formats, from the platforms "
        "own documentation: aspect ratios and durations for Instagram Reels, TikTok "
        "videos and YouTube Shorts, character limits and truncation points for LinkedIn "
        "and X posts, image dimensions for carousels and link previews, caption and "
        "alternative text limits, and where each platform documents these. Cite the "
        "platform help centre or business documentation page for each and note when it "
        "was last revised."
    ),
    "q29_linkedin_x_threads_creator_structure_craft": (
        "How specific named, full-time LinkedIn and X creators and ghostwriters such as "
        "Justin Welsh, Sahil Bloom, Amanda Natividad, Dan Koe, Katelyn Bourgoin and Jay "
        "Clouse structure a text post as a piece of writing in 2026, drawn from the "
        "creator's own newsletter, YouTube channel, course or a named third-party "
        "teardown of their technique rather than a social media scheduling tool's "
        "generic listicle: how they decide the single idea a post carries, what the "
        "opening line does beyond surviving the truncation point, how they pace and "
        "close a multi-post thread, and annotated teardowns naming a specific post that "
        "worked and a specific one that failed."
    ),
    "q30_carousel_creator_structure_craft": (
        "How specific named LinkedIn and Instagram creators and designers sequence a "
        "carousel as a piece of storytelling in 2026, drawn from the creator's own "
        "breakdown, YouTube video or course rather than a scheduling tool's generic "
        "carousel guide: how they choose the number of frames, what the cover frame "
        "promises versus what the closing frame resolves, how one idea is paced per "
        "frame across a real published carousel, and annotated teardowns naming a "
        "specific carousel that worked and a specific one that failed."
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


# A source found ONLY by the craft passes is craft by provenance, whatever its domain.
#
# This is the load-bearing rule, and it replaced a domain allowlist that did not work.
# The allowlist was a guess at where craft lives and it caught 11 sources out of 154:
# the engines return academic results even for practitioner-register queries, so the
# real craft web arrives as a long tail of one-off blogs nobody can enumerate in
# advance. What IS knowable is which question surfaced a source. If a page only ever
# appeared when we asked "show me landing page teardowns", it is craft, and treating it
# as evidence would be wrong regardless of how respectable its domain looks.
#
# Confirmed still wins: a peer-reviewed paper that happens to surface in a craft pass
# is still evidence.
CRAFT_PASSES = {
    "q19_written_gated_assets_craft", "q20_case_study_craft",
    "q21_newsletter_craft", "q22_longform_video_youtube_craft",
    "q23_short_form_video_craft", "q24_podcast_production_craft",
    "q25_webinar_live_craft", "q26_visual_formats_craft",
    "q27_social_text_craft", "q28_platform_specs_craft",
    "q29_linkedin_x_threads_creator_structure_craft",
    "q30_carousel_creator_structure_craft",
}
assert CRAFT_PASSES <= set(QUERIES), sorted(CRAFT_PASSES - set(QUERIES))

# Evidence-register passes that need `general` (all four engines) rather than `scientific`
# (exa + tavily). Both of these are provenance questions, and a provenance question has two
# halves that live in different places: WHERE a claim circulates is a Serper question, and
# WHETHER a primary source exists underneath it is an Exa question. Running them scientific
# would retrieve the second half only, which is precisely how you end up unable to say who
# started a number. They keep EVIDENCE_SUFFIX - they are not craft.
GENERAL_PASSES = {"q17_folklore_provenance", "q18_metric_definitions"}
assert GENERAL_PASSES <= set(QUERIES) and not (GENERAL_PASSES & CRAFT_PASSES)


def tier_of(u, topics=None):
    """Three tiers, in precedence order.

    confirmed    peer-reviewed research, primary regulatory text, or original empirical
                 usability research. May support a factual claim.
    craft        practitioner teaching, teardowns, swipe files, video. May demonstrate
                 TECHNIQUE and format conventions. May NEVER support a factual claim,
                 and factcheck mode does not read it.
    practitioner everything else: an agency or vendor making a case. Labelled as such
                 whenever quoted.

    No blanket ".gov" or ".edu" rule on purpose. A university publishes research,
    course pages and advertising from one domain, so the suffix carries no evidentiary
    signal. Peer review is carried by the enumerated publishers instead.

    confirmed is checked BEFORE craft so that if a craft domain ever publishes real
    research it is not demoted by the domain match.
    """
    d = domain_of(u)
    if d in CONFIRMED_DOMAINS or any(d.endswith("." + c) for c in CONFIRMED_DOMAINS):
        return "confirmed"
    # First-party platform documentation is PRACTITIONER, never craft, and it has to be
    # checked before the provenance rule below.
    #
    # The spec pass that retrieves these docs is itself a craft-register pass, so
    # provenance was tiering 7 of the first 9 platform docs as craft - which would have
    # made them unusable for exactly the thing they exist for. `[K]` may never support a
    # factual claim and factcheck mode does not read it, but "a Reel is 9:16" is a
    # definitional fact and the platform's own page is its primary source. Craft is the
    # wrong quarantine for it; the right guard is the [P*] marker, which already says
    # "authoritative for what the platform defines, never evidence that it works".
    if is_platform_doc(u):
        return "practitioner"
    if d in CRAFT_DOMAINS or any(d.endswith("." + c) for c in CRAFT_DOMAINS):
        return "craft"
    # provenance: found only by craft-register questions
    if topics and set(topics) <= CRAFT_PASSES:
        return "craft"
    return "practitioner"


def is_junk(url, title):
    d = domain_of(url)
    # A named creator's own post about their own technique skips the UGC gate too - see
    # CREATOR_PRIMARY_SOURCE_URLS above. Checked before the domain gate, same shape as
    # the platform-doc carve-out below. Still has to clear the topic guard afterward.
    if norm_url(url) in {norm_url(u) for u in CREATOR_PRIMARY_SOURCE_URLS}:
        pass
    # First-party platform documentation skips the UGC gate ONLY. It still has to clear
    # the topic guard below, or help.instagram.com/1234 "How to report an account" would
    # ride straight in on the carve-out.
    elif not is_platform_doc(url):
        if d in JUNK_DOMAINS or any(d.endswith("." + j) for j in JUNK_DOMAINS):
            return "social/UGC"
    if any(d.endswith(m) for m in MIRROR_SUFFIXES):
        return "localized mirror"
    # Normalize separators to spaces so short tokens match as whole words. Plain
    # substring matching lets "hou-SEO-frepresentatives" through; \b would not help
    # either, since underscores count as word characters.
    #
    # Threshold is 3, not copywriting's 4. At 4 the truncated stems in TOPIC_TOKENS -
    # blog, writ, post, hook, text, word - could only ever match as whole words, and
    # " blog " does not occur in real prose, so a page titled "Blogging in 2026" was
    # discarded as off-topic. 3 still catches the bug the guard was written for, which
    # was "seo" matching inside "houseofrepresentatives".
    #
    # For platform docs AND creator-primary-source exemptions, the HOST is excluded from
    # the haystack. Every linkedin.com/substack.com URL contains a topic token in its own
    # domain name - leaving the host in would let anything on the exemption list pass the
    # guard for free, the same failure the platform-doc comment below already names.
    host_excluded = is_platform_doc(url) or norm_url(url) in {
        norm_url(u) for u in CREATOR_PRIMARY_SOURCE_URLS}
    subject = f"{title} {urlsplit(url).path}" if host_excluded else f"{title} {url}"
    hay = " " + re.sub(r"[^a-z0-9]+", " ", subject.lower()).strip() + " "
    for tok in TOPIC_TOKENS:
        if len(tok) <= 3:
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

    craft = key in CRAFT_PASSES
    # The suffix decides the register, and --mode is ALSO passed explicitly rather than
    # left on auto. Auto inference is what silently routed seven copywriting passes to
    # entity search and all nine of its craft passes to scientific; there is no reason to
    # re-run that risk when we already know which register each pass belongs to. The
    # suffix/detect_mode agreement is still asserted in _selftest, as a guard for anyone
    # who later drops --mode.
    #
    # --num 15 on evidence passes: 18 evidence passes over ~32 topics is roughly 1.8 topics
    # per pass, and at the default 10 per service that is thinner per-topic than copywriting
    # managed. Craft stays at the default; practical mode runs 4 services plus the
    # site:youtube.com variant, so it already returns more per pass.
    suffix = CRAFT_SUFFIX if craft else EVIDENCE_SUFFIX
    mode = "practical" if craft else ("general" if key in GENERAL_PASSES else "scientific")
    num = [] if craft else ["--num", "15"]

    def _attempt(extra):
        try:
            r = subprocess.run(
                [sys.executable, str(RESEARCH_PY), "--query", query + suffix,
                 "--mode", mode, "--depth", "deep", "--json", *num, *extra],
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
    #    there is no such thing as too much primary research. Craft gets a higher cap
    #    because youtube.com is a single domain holding many distinct teardowns - at
    #    the standard cap of 5 the entire video tier would be five videos.
    per_domain, capped, domain_cut = {}, [], 0
    for e in kept:
        d = domain_of(e["url"])
        tier = tier_of(e["url"], e["topics"])
        if tier != "confirmed":
            if is_platform_doc(e["url"]):
                cap = PLATFORM_DOC_CAP
            elif tier == "craft":
                cap = CRAFT_DOMAIN_CAP
            else:
                cap = PER_DOMAIN_CAP
            if per_domain.get(d, 0) >= cap:
                domain_cut += 1
                continue
            per_domain[d] = per_domain.get(d, 0) + 1
        capped.append(e)
    if domain_cut:
        log(f"  dropped {domain_cut} (per-domain cap)")

    # 4. Confirmed-tier jumps the global cap. Capping it would cut peer-reviewed
    #    research while keeping vendor blogs that more engines happened to surface,
    #    which is backwards for an evidence corpus. Craft gets a reserved allocation
    #    for the same reason in reverse: it is the thing the first corpus was missing,
    #    so it must not be squeezed out by whichever vendor pages ranked well.
    confirmed_e = [e for e in capped if tier_of(e["url"], e["topics"]) == "confirmed"]
    craft_e = [e for e in capped if tier_of(e["url"], e["topics"]) == "craft"]
    # First-party platform docs are practitioner-tier but get their own allocation, taken
    # out before the practitioner slice is cut. They are the only source for what a format
    # IS, and without a reserve they compete for room against agency blog posts and lose.
    rest = [e for e in capped if tier_of(e["url"], e["topics"]) == "practitioner"]
    platform_e = [e for e in rest if is_platform_doc(e["url"])]
    practitioner_e = [e for e in rest if not is_platform_doc(e["url"])]
    # Pinned sources take slots first, ahead of the score-based sort - see
    # PINNED_CRAFT_URLS for why. They still count against CRAFT_RESERVE, and a source
    # only lands here if it also survived tiering, junk and domain-cap above it.
    _pinned_norm = {norm_url(u) for u in PINNED_CRAFT_URLS}
    craft_pinned = [e for e in craft_e if norm_url(e["url"]) in _pinned_norm]
    craft_unpinned = [e for e in craft_e if norm_url(e["url"]) not in _pinned_norm]
    craft_keep = craft_pinned + craft_unpinned[:max(0, CRAFT_RESERVE - len(craft_pinned))]
    platform_keep = platform_e[:PLATFORM_DOC_RESERVE]
    room = max(0, SOURCE_CAP - len(confirmed_e) - len(craft_keep) - len(platform_keep))
    if len(practitioner_e) > room:
        log(f"CAP {len(capped)} eligible -> {len(confirmed_e)} confirmed + "
            f"{len(craft_keep)} craft + {len(platform_keep)} first-party + "
            f"top {room} practitioner")
    ranked = confirmed_e + craft_keep + platform_keep + practitioner_e[:room]

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
            "tier": tier_of(e["url"], e["topics"]),
            # Rendered [P*] in the synthesis. Authoritative for what a platform REQUIRES
            # or DEFINES, quoted with a retrieval date; never evidence that anything WORKS.
            "first_party": is_platform_doc(e["url"]),
            "topics": e["topics"],
            "engines": sorted(e["engines"]),
            "published_date": e["published_date"],
        })
        next_index += 1
    sources.sort(key=lambda s: s["index"])
    if locked:
        log(f"  preserved {len(locked)} existing indices, added {len(fresh)} new")

    # Re-tier the locked entries too. Indices never move, but the tier RULE changed on
    # 2026-08-15 when the craft tier was added, and a source frozen at its old tier
    # would contradict sources.json's own definition. Cheap to recompute, and the only
    # thing that must stay immutable is the index.
    retiered = 0
    for s in sources:
        t = tier_of(s["url"], s.get("topics"))
        if t != s["tier"]:
            s["tier"] = t
            retiered += 1
        s["first_party"] = is_platform_doc(s["url"])
    if retiered:
        log(f"  re-tiered {retiered} existing source(s) under the current rules")

    counts = {t: sum(1 for s in sources if s["tier"] == t)
              for t in ("confirmed", "craft", "practitioner")}
    n_first_party = sum(1 for s in sources if s.get("first_party"))
    out = {
        "generated_at": datetime.now().date().isoformat(),
        "method": ("28 deep passes via the in-repo research skill: 18 evidence passes in "
                   "scientific/general mode and 10 craft passes in practical mode, with a "
                   "separate suffix per register so the craft half is not silently routed "
                   "to the journals. Deduped by normalized URL, junk-filtered, per-domain "
                   "capped, tiered confirmed / craft / practitioner"),
        "note": ("inline [sN] in references/research-synthesis.md resolves on the `index` "
                 "field. tier=craft means technique and worked examples only - never "
                 "usable to support a factual claim, and invisible to factcheck mode. "
                 "first_party=true is platform documentation, rendered [P*]: authoritative "
                 "for what a platform requires or defines, never evidence that something "
                 "works, and always quoted with a retrieval date"),
        "total_found": total_found,
        "source_count": len(sources),
        "confirmed": counts["confirmed"],
        "craft": counts["craft"],
        "practitioner": counts["practitioner"],
        "first_party": n_first_party,
        "sources": sources,
    }
    (RESEARCH_DIR / "sources.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"extract: {total_found} deduped -> {len(sources)} kept "
        f"({counts['confirmed']} confirmed / {counts['craft']} craft / "
        f"{counts['practitioner']} practitioner, of which {n_first_party} first-party)")


def verify():
    """Every [sN] in this skill's references/ and in every spoke's must resolve.

    The spokes deliberately have no corpus of their own and cite back to this one, so
    a verify that only checked the hub would miss exactly the citations most likely to
    rot: the ones written in a different folder from the sources.json they point at.

    blog-writer is a special case - it keeps its own 83-source corpus for AEO/GEO and
    its own [sN] namespace. Its citations are therefore NOT checked here; only the
    spokes that genuinely have no corpus are. Checking it would report every one of its
    own valid citations as broken.
    """
    sj = _load(RESEARCH_DIR / "sources.json") or {}
    valid = {s["index"] for s in sj.get("sources", [])}
    skills_dir = RESEARCH_DIR.parents[1]
    ref_dirs = [RESEARCH_DIR.parent / "references"] + [
        skills_dir / spoke / "references"
        for spoke in SPOKES if spoke != "blog-writer"
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
    """The evidence rules are the whole point of this file, so they get a check.

    Every assert below was a real bug in a previous corpus, or a judgment call this file
    makes that someone could reasonably reverse by accident later.
    """
    assert norm_url("http://WWW.Example.com/a/?utm_source=x#f") == "https://example.com/a"
    assert norm_url("https://example.com") == "https://example.com/"

    # --- tier: peer-reviewed press -------------------------------------------------
    assert tier_of("https://academic.oup.com/joc/article/70/1/1") == "confirmed"
    assert tier_of("https://journals.sagepub.com/doi/10.1177/1461444820912") == "confirmed"
    assert tier_of("https://www.sciencedirect.com/science/article/pii/S074756322") == "confirmed"
    # computational social science: ICWSM lives at ojs.aaai.org, not at "aaai/icwsm"
    assert tier_of("https://ojs.aaai.org/index.php/ICWSM/article/view/14134") == "confirmed"
    assert tier_of("https://dl.acm.org/doi/10.1145/3411764") == "confirmed"

    # --- tier: the deliberate exceptions -------------------------------------------
    # original empirical research, method published with result
    assert tier_of("https://www.nngroup.com/articles/scrolling-and-attention/") == "confirmed"
    # population media-consumption surveys. See the header caveat: these support "X% of
    # adults use TikTok for news", NEVER "video outperforms text".
    assert tier_of("https://www.pewresearch.org/journalism/2026/social-media-news/") == "confirmed"
    assert tier_of("https://reutersinstitute.politics.ox.ac.uk/digital-news-report/2026") == "confirmed"
    assert tier_of("https://www.ofcom.org.uk/research/online-nation") == "confirmed"
    # ...but the parent university is NOT confirmed. Listing ox.ac.uk instead of the full
    # host would have confirmed every page Oxford publishes.
    assert tier_of("https://www.ox.ac.uk/news/open-day") == "practitioner"
    # normative standards text
    assert tier_of("https://www.w3.org/WAI/media/av/captions/") == "confirmed"
    assert tier_of("https://www.ftc.gov/business-guidance/endorsement-guides") == "confirmed"

    # --- tier: the rejections, each named in the header ----------------------------
    # a re-publisher of vendor numbers is not a data source, however it is styled
    assert tier_of("https://www.statista.com/statistics/272014/social-network-users/") == "practitioner"
    assert tier_of("https://www.thinkwithgoogle.com/marketing-strategies/video/") == "practitioner"
    assert tier_of("https://www.nielsen.com/insights/2026/streaming-report/") == "practitioner"
    # closest call in the list: probability sample and published method, but sold to the
    # broadcasters the number benefits. Recorded so nobody promotes it later.
    assert tier_of("https://www.edisonresearch.com/infinite-dial-2026/") == "practitioner"
    # every "State of Content Marketing" report, however large the sample
    assert tier_of("https://contentmarketinginstitute.com/research/b2b-2026") == "practitioner"
    assert tier_of("https://www.semrush.com/blog/content-marketing-statistics/") == "practitioner"
    assert tier_of("https://buffer.com/resources/social-media-benchmarks/") == "practitioner"
    assert tier_of("https://blog.hootsuite.com/instagram-statistics/") == "practitioner"
    # dropped from the inherited copywriting list
    assert tier_of("https://www.warc.com/content/article/x") == "practitioner"
    assert tier_of("https://baymard.com/blog/checkout-flow") == "practitioner"
    # a .edu suffix is not evidence: this is university marketing copy
    assert tier_of("https://www.phoenix.edu/articles/business/content-marketing.html") == "practitioner"

    # --- tier: craft ---------------------------------------------------------------
    assert tier_of("https://www.youtube.com/watch?v=abc123") == "craft"
    assert tier_of("https://www.animalz.co/blog/content-strategy/") == "craft"
    assert tier_of("https://www.superpath.co/blog/content-calendar") == "craft"
    # provenance: found ONLY by craft-register passes, so craft whatever the domain. This
    # is the rule that actually populates the tier; the allowlist above is only a floor.
    assert tier_of("https://some-random-blog.com/reels-hooks",
                   ["q23_short_form_video_craft"]) == "craft"
    assert tier_of("https://some-random-blog.com/reels-hooks",
                   ["q23_short_form_video_craft", "q2_video_engagement_retention"]) == "practitioner"
    # confirmed still wins, so a real paper surfacing in a craft pass stays evidence
    assert tier_of("https://dl.acm.org/doi/10.1145/1", ["q23_short_form_video_craft"]) == "confirmed"
    # ...and a platform doc beats provenance too. The spec pass IS a craft pass, so without
    # this 7 of the first 9 platform docs tiered craft and became unquotable for the
    # definitional facts they exist to supply.
    assert tier_of("https://developers.tiktok.com/doc/content-posting-api",
                   ["q28_platform_specs_craft"]) == "practitioner"
    assert tier_of("https://www.linkedin.com/help/linkedin/answer/a424737",
                   ["q28_platform_specs_craft"]) == "practitioner"

    # --- junk gate: first-party platform docs --------------------------------------
    # DEFECT 3. The apex stays junk; the documentation does not. Copywriting's corpus has
    # zero of these because the apex entry killed every subdomain.
    assert is_junk("https://help.instagram.com/1038071743007909",
                   "Reels video specifications") is None
    assert is_junk("https://business.linkedin.com/marketing-solutions/ads/specs",
                   "LinkedIn ad specifications") is None
    assert is_junk("https://support.tiktok.com/en/using-tiktok/creating-videos",
                   "Video length and format") is None
    # path-based, on the same apex as the feed - a host allowlist cannot reach these
    assert is_junk("https://www.facebook.com/business/help/980593475366490",
                   "Image and video format specs") is None
    assert is_junk("https://www.linkedin.com/help/linkedin/answer/a521928",
                   "Character limits for posts") is None
    # the feed itself is still junk
    assert is_junk("https://www.linkedin.com/pulse/content-strategy-x", "Content strategy") == "social/UGC"
    assert is_junk("https://www.instagram.com/p/Cabc123/", "Reels post") == "social/UGC"
    assert is_junk("https://www.tiktok.com/@user/video/123", "Content tips") == "social/UGC"

    # --- junk gate: named creator primary sources (2026-08-31, Aleem's explicit call) ---
    # exempted: on the allowlist, no www to prove norm_url matching works
    assert is_junk("https://justinwelsh.substack.com/p/how-to-write-compelling-long-form",
                   "How to write compelling long-form") is None
    # exempted even with a www the allowlist entry doesn't have (norm_url strips it both sides)
    assert is_junk(
        "https://www.linkedin.com/posts/justinwelsh_my-strategy-when-i-started-was-pretty-basic-activity-7415011488983203840-7Rmy",
        "My strategy when I started was pretty basic") is None
    # a DIFFERENT linkedin.com post by the same creator, not on the allowlist, is still junk -
    # the exemption is per-URL, never per-person
    assert is_junk("https://www.linkedin.com/posts/justinwelsh_some-other-post-1234567890",
                   "Some other post") == "social/UGC"
    # the carve-out bypasses the UGC gate ONLY, never the topic guard
    assert is_junk("https://help.instagram.com/1234", "How to report an account") == "off-topic"

    # --- junk gate: the topic guard ------------------------------------------------
    # the bug it exists for: trusted publisher, off-subject document
    assert is_junk("https://census.gov/119_legislative_schedule.pdf", "Legislative Schedule")
    assert is_junk("https://example.com/octopus-anatomy", "Octopus anatomy") == "off-topic"
    # DEFECT 2. At the inherited threshold of 4 these were all discarded, because the
    # truncated stems could only match as whole words and " blog " is not real text.
    assert is_junk("https://example.com/x", "Blogging in 2026") is None
    assert is_junk("https://example.com/x", "How we grew the vlog") is None
    assert is_junk("https://example.com/x", "Writing for the web") is None
    assert is_junk("https://example.com/x", "Reels that actually work") is None
    assert is_junk("https://example.com/x", "Meme marketing") is None
    assert is_junk("https://example.com/x", "Posts that get views") is None
    # still junk by Aleem's explicit call: high volume, low signal, untierable
    assert is_junk("https://medium.com/@x/content-strategy", "Content strategy") == "social/UGC"
    assert is_junk("https://reddit.com/r/content_marketing", "Content marketing") == "social/UGC"

    # --- DEFECT 1: the register a pass actually runs under -------------------------
    # This is the assert that matters most. Every copywriting craft pass ran under
    # `scientific` because one shared suffix contained the words "peer-reviewed", so
    # Serper never ran and the corpus ended up with 2 YouTube sources in 494 - then
    # documented the gap as a limitation of the search engines.
    sys.path.insert(0, str(RESEARCH_PY.parent))
    import research as _r  # noqa: PLC0415

    assert _r.detect_mode(CRAFT_SUFFIX) == "practical", \
        "CRAFT_SUFFIX must not contain a _SCI_HINT or _PERSON_HINT token"
    assert _r.detect_mode("x" + EVIDENCE_SUFFIX) == "scientific"
    for key, q in QUERIES.items():
        craft = key in CRAFT_PASSES
        want = "practical" if craft else "scientific"
        got = _r.detect_mode(q + (CRAFT_SUFFIX if craft else EVIDENCE_SUFFIX))
        assert got == want, f"{key}: routes {got}, expected {want}"
        # nothing may route entity. A pass that searches for PEOPLE is a bug, not a result.
        assert got != "entity", key
    assert "practical" in _r._SERVICES, "research.py is missing the practical service set"
    assert "serper" in _r._SERVICES["practical"]["deep"], \
        "practical mode without serper means no site:youtube.com variant and no craft tier"

    print(f"selftest ok ({len(QUERIES)} passes: "
          f"{len(QUERIES) - len(CRAFT_PASSES)} evidence / {len(CRAFT_PASSES)} craft)")


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

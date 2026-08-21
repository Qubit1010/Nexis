#!/usr/bin/env python3
"""Build the social-media-advisor corpus: 14 deep research passes -> a tiered sources.json.

Subcommands, all idempotent:

    python gather.py run       # the 14 deep passes -> passes/<key>.json  (resume-safe)
    python gather.py extract   # passes/*.json -> a deduped, tiered, capped sources.json
    python gather.py verify    # every [sN] in the hub + spoke references/ resolves
    python gather.py selftest  # the evidence + mode-routing rules, as executable asserts
    python gather.py           # run, then extract

Cloned from content-advisor's, which came from copywriting-advisor -> branding-advisor ->
strategic-foundation -> seo-advisor's run_passes.py + build_corpus.py. Gather via
Exa/Serper/Tavily/Jina.

TIMEBOXED BUILD. 14 passes and a 280 cap, not content-advisor's 28 and 560. This was an
explicit scope decision, not an accident, and it is recorded so nobody later reads the
smaller corpus as evidence the subject is thinner than content marketing. It is not.


WHY THIS CORPUS IS EPISTEMICALLY DIFFERENT FROM EVERY SIBLING
--------------------------------------------------------------
Every other advisor in this family can, in principle, answer its central question from
confirmed-tier evidence. This one cannot, and the whole design follows from that.

NOBODY OUTSIDE THE PLATFORM KNOWS HOW THE ALGORITHM WORKS. There is no peer-reviewed
source that establishes how LinkedIn ranks a post, because the ranker is proprietary,
undocumented, and changed without notice. Every claim in circulation traces to one of
three registers, and the corpus must keep them apart rather than flattening them into
"how the algorithm works":

  [P*] what the platform SAYS it does - first-party docs, engineering blogs, newsrooms.
       Authoritative for what a platform REQUIRES or DEFINES. Never evidence that
       anything WORKS. Always quoted with a retrieval date.
  [P]  what a vendor MEASURED ON ITS OWN CUSTOMERS - a labelled, attributed number,
       never stated as measured fact.
  [C]  what research establishes about ALGORITHMIC FEEDS AS A CLASS - exposure
       allocation, engagement signals, growth dynamics, cascades. Real evidence, but
       about the kind of system, not about LinkedIn in particular.

The practical consequence, and the reason PLATFORM_DOC_RESERVE is raised here: first-party
documentation is a PRIMARY source in this corpus, not a supplement. A run that returns zero
linkedin.com / instagram.com / tiktok.com / youtube.com sources has failed, however many
sources it returned in total.

SECOND CONSEQUENCE: THIS CORPUS DECAYS FASTER THAN ANY SIBLING. Brand theory keeps for
years. A feed-ranking change keeps for a quarter. Refresh the craft half far more often
than the evidence half, and never let a platform spec ship without its retrieval date.

THIS SKILL LANDS ON A DOCUMENTED FAULT LINE, DELIBERATELY.
content-advisor/references/format-specs/00-index.md already records that
marketing-advisor and content-engine assert hard platform numbers (link penalty -60-68%,
hashtags -29%, dwell 13x) which content-advisor and copy-conversion classify as unsourced
convention and forbid quoting. This corpus sides with the latter, on the tiering above.
Following branding-advisor's precedent with differentiation-vs-distinctiveness, the skill
NAMES the disagreement rather than silently resolving it - a skill that quietly
contradicts its sibling is worse than one that says where the two camps differ.

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
# No executor spoke exists yet - this skill ships advisor-only, and a client-facing
# social strategy document (19-social-media-strategy.md) is a deliberate later build.
# The skills listed are the ones that would carry an [sN] the moment one is written:
# linkedin-commenter executes the engagement habit this corpus theorises, and
# content-engine / post-creator apply platform rules to NexusPoint's own posting.
#
# marketing-advisor is deliberately NOT walked. It keeps its own [sN] namespace over a
# 234-source corpus, so checking it would report every one of its citations as broken -
# and separately, its _research/sources.json does not exist at all, so its citations do
# not currently resolve against anything. That is a real defect in that skill, flagged
# and left alone here rather than silently absorbed.
SPOKES = (
    "linkedin-commenter", "content-engine", "post-creator", "shorts-creator",
)

# The cap governs how much PRACTITIONER material may accumulate; confirmed, craft and
# first-party platform docs have their own allocations below.
SOURCE_CAP = 280
PER_DOMAIN_CAP = 5
# youtube.com is one domain holding many distinct teardowns, so the standard cap would
# reduce the whole video tier to five videos.
CRAFT_DOMAIN_CAP = 16
# Reserved allocation so the craft tier cannot be squeezed out by whichever vendor pages
# happened to rank. Scaled from content-advisor's 140/560 to hold the same quarter share
# of a 280 cap: 7 of the 14 passes are craft, and they are the half that answers "what do
# I actually do on this platform".
CRAFT_RESERVE = 70
# First-party platform documentation gets its own cap and its own allocation.
#
# RAISED FROM content-advisor's 12/45, and this is the single most consequential constant
# in the file. There, platform docs supplemented an evidence corpus. HERE THEY ARE THE
# PRIMARY SOURCE: when the question is "how does TikTok rank a video in 2026", the best
# available answer is what TikTok published and when, and no peer-reviewed alternative
# exists. Ten platforms times a handful of genuinely load-bearing docs each - ranking
# explainer, creator guide, newsroom change announcement, spec page - does not fit in 45.
PLATFORM_DOC_CAP = 20
PLATFORM_DOC_RESERVE = 75

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
    # ADDED after the first live run, and this one is worth reading before deleting.
    #
    # The q14 query led with the words "social listening", and the engines returned the
    # SOCIAL SECURITY ADMINISTRATION. Ten of that pass's twelve surviving sources were
    # ssa.gov, usa.gov, a Merriam-Webster entry, a Cambridge Dictionary entry and a bar in
    # Birmingham called Social Kitchen. The topic guard passed them all because "social"
    # is necessarily a topic token in this corpus, so the guard cannot be the fix.
    #
    # dictionary.cambridge.org is the sharpest one: it was tiered CONFIRMED, because
    # cambridge.org is an enumerated academic publisher and the dictionary rides in on
    # the same apex. A dictionary definition of the word "social" was therefore sitting
    # in this corpus as peer-reviewed evidence. Junking beats the tiering, so listing it
    # here fixes the tier as well as the inclusion.
    "ssa.gov", "usa.gov", "merriam-webster.com", "dictionary.cambridge.org",
    "britannica.com", "dictionary.com", "thefreedictionary.com",
}

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
    # ADDED after the first live run. LinkedIn publishes its feed-ranking explanations on
    # news.linkedin.com and linkedin.com/blog/engineering, NOT on the two hosts inherited
    # from content-advisor - and those two posts are the single best available source on
    # how the LinkedIn feed ranks. Both were killed as "social/UGC" by the linkedin.com
    # apex entry. For a corpus whose headline question is "how does the LinkedIn algorithm
    # work", losing them is the whole ballgame.
    "news.linkedin.com",
    # help.snapchat.com returned an actual "How We Rank Content" page, which is exactly a
    # [P*] source; only the business hosts were inherited.
    "help.snapchat.com",
    "newsroom.pinterest.com", "policy.pinterest.com",
    "creators.tiktok.com", "effecthouse.tiktok.com",
    "about.x.com", "newsroom.snap.com",
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
    # See the note on news.linkedin.com above. /blog/engineering is where the feed
    # ranking write-ups live; /top-content is LinkedIn defining its own ad metrics, which
    # is first-party by definition (and [P*] already forbids reading it as proof anything
    # works, so admitting ad-sales collateral here is safe).
    ("linkedin.com", "/blog"), ("linkedin.com", "/top-content"),
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
    # the platform as a SYSTEM, and the account on it - the tokens that separate this
    # corpus from content-advisor's. Without these the guard admits a document about
    # what a Reel looks like and rejects one about how the For You page ranks it, which
    # is exactly backwards for this skill.
    "rank", "ranking", "distribut", "exposure", "gatekeep", "curat", "for you",
    "discover", "explore page", "suggest", "timeline", "shadowban", "shadow ban",
    "throttl", "penalt", "suppress", "demot", "moderat", "policy", "guideline",
    "hashtag", "keyword", "tag", "mention", "profile", "bio", "handle", "verifi",
    "badge", "monetiz", "monetis", "creator fund", "partner program", "affiliate",
    "community", "group", "forum", "subreddit", "listening", "sentiment",
    "advocacy", "employee advocacy", "share of voice", "comment", "reply", "dm",
    "direct message", "inbox", "notification", "story", "stories",
    "organic", "paid", "boost", "amplification", "cross-post", "cross post",
    "growth", "grow", "unfollow", "audience size",
    # NOT here, and each one is a trap this file already fell into once:
    #   "account" admits "how to report an account" and every settings page - the exact
    #     platform-doc the topic guard exists to keep out. "growth"/"follow" cover the
    #     real cases.
    #   "gain" and "lose" are 4 chars, so is_junk matches them as SUBSTRINGS: "gain"
    #     matches "again", "lose" matches "close" and "closed". Both admit anything.
    #   "live" matches "deliver" and "delivery". Use "livestream", already above.
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

# 14 deep passes in three registers.
#
# EVIDENCE (q1-q6)  ends with EVIDENCE_SUFFIX and routes `scientific`.
# GENERAL  (q7)     ends with EVIDENCE_SUFFIX and routes `general` - see GENERAL_PASSES.
# CRAFT    (q8-q14) ends with CRAFT_SUFFIX and routes `practical`.
# _selftest asserts that routing. Do not edit a query without re-running it.
#
# VOCABULARY IS THE WHOLE GAME IN THE EVIDENCE HALF, and it bites harder here than in
# any sibling corpus, because this subject's industry vocabulary has almost no academic
# counterpart. Asking "how does the Instagram algorithm work" retrieves Hootsuite and
# Later; asking about "algorithmic curation" and "exposure allocation in recommender
# systems" retrieves the audits and the computational social science. "Organic reach
# decline" retrieves agency blogs; "algorithmic gatekeeping" and "preferential
# attachment" retrieve the research the agency blogs are loosely describing. "Personal
# branding" retrieves LinkedIn coaches; "self-presentation", "impression management"
# and "microcelebrity" retrieve the literature. Copywriting-advisor learned this the
# expensive way and needed four remedial passes.
#
# THE EVIDENCE HALF DELIBERATELY DOES NOT ASK ABOUT ANY NAMED PLATFORM. It asks about
# the class of system. That is not a limitation to apologise for, it is the honest
# shape of the available evidence, and mixing the registers in one query is how you get
# a corpus that looks like it can prove things about LinkedIn when it cannot.
#
# Subjects deliberately NOT here because a neighbouring corpus already owns them and a
# pass would re-retrieve it: what a format looks like and how long it runs
# (content-advisor, 560 sources - it owns the artifact, this owns the platform),
# headlines, hooks-as-copy and CTAs (copywriting-advisor, 494), platform character
# limits and truncation points (copy-conversion's platform-formatting.md), article
# AEO/GEO (blog-writer, 83), and X/Twitter's open-sourced ranking internals, which
# awesome-claude-skills/twitter-algorithm-optimizer already documents from the source
# release. Cross-cite those; never re-buy them.
QUERIES = {
    # ---------------------------------------------------------------- evidence
    "q1_algorithmic_curation_ranking": (
        "Empirical research and independent audits of algorithmic curation and feed "
        "ranking in social platforms: how recommender systems allocate exposure "
        "between accounts, engagement-optimised ranking and its measured effects on "
        "what circulates, algorithmic gatekeeping, sociotechnical audits of platform "
        "recommendation systems, exposure diversity and filter bubble findings, and "
        "the measured difference between network-graph distribution and "
        "interest-based or recommendation-based distribution."
    ),
    "q2_exposure_allocation_reach": (
        "Research on how attention and exposure are distributed across creators and "
        "pages in online platforms: inequality of exposure, preferential attachment "
        "and cumulative advantage in follower growth, the long tail of creator reach, "
        "measured decline of unpaid distribution for organisational pages, platform "
        "incentives shaping organic distribution, and studies measuring what fraction "
        "of an account's audience actually sees a given post."
    ),
    "q3_engagement_signal_mechanics": (
        "Empirical research on social media engagement as a measured construct: what "
        "predicts commenting, sharing and saving as distinct behaviours rather than "
        "one variable, reciprocity and interaction effects between accounts, the "
        "relationship between engagement metrics and downstream business outcomes, "
        "engagement bait and manipulation detection, and validated measurement of "
        "engagement including why engagement-rate definitions differ between studies."
    ),
    "q4_audience_growth_dynamics": (
        "Research on audience and follower growth in online social networks: growth "
        "mechanisms and network effects, what causes accounts to gain and lose "
        "followers over time, the measured relationship between posting frequency and "
        "audience growth, tenure and consistency effects, cross-platform audience "
        "migration, and formation, participation and retention in online communities "
        "and groups."
    ),
    # WORDING CONSTRAINT, not style. This query may not contain "founder", "co-founder",
    # "CEO", "CTO", "owner", "president" or "who is": research.py's _PERSON_HINT matches
    # them and forces the pass into `entity` mode, which runs Exa with category="people"
    # and LinkedIn X-ray dorks. The pass would then search for PEOPLE rather than for
    # research about people, and return a list of profiles. _selftest caught exactly this
    # on the first run. "entrepreneur" and "senior leader" are the safe synonyms.
    "q5_self_presentation_personal_branding": (
        "Research on personal branding and self-presentation in online professional "
        "and social contexts: microcelebrity and self-branding practices, impression "
        "management on professional networks, parasocial interaction and relationship "
        "formation with creators and public figures, entrepreneur and senior-leader "
        "visibility effects on organisational outcomes, perceived authenticity, and "
        "measured differences between individual and organisational accounts."
    ),
    "q6_influencer_ugc_credibility": (
        "Research on influencer marketing and user-generated content effectiveness: "
        "measured effects of influencer endorsement on attitudes and purchase, source "
        "credibility and parasocial trust as mediating mechanisms, micro versus macro "
        "influencer effects, sponsorship and paid-partnership disclosure effects on "
        "persuasion and trust, user-generated content effects, and selection bias in "
        "how influencer campaign results are reported."
    ),
    # -------------------------------------------------- provenance (general mode)
    "q7_social_folklore_provenance": (
        "Provenance checks on widely repeated social media marketing claims: where the "
        "best-time-to-post tables actually come from and whether any controlled test "
        "supports them, whether hashtags still affect reach and what evidence exists, "
        "whether outbound links are penalised in feeds and who first claimed it, "
        "whether shadowbanning is a documented platform behaviour or a folk "
        "explanation, engagement pods and reciprocity rings, follower-count "
        "thresholds, and the origin of commonly cited social media engagement and "
        "reach statistics. Trace each claim to its earliest traceable source and say "
        "plainly when none exists."
    ),
    # ------------------------------------------------------------------- craft
    "q8_linkedin_platform_craft": (
        "How LinkedIn distribution and organic account growth actually work in 2026: "
        "what LinkedIn itself documents about feed ranking, content distribution and "
        "creator features, what changed on the platform during 2025 and 2026, which "
        "post formats currently get distribution, posting cadence and timing in "
        "practice, how commenting and dwell time are said to affect reach, personal "
        "profile versus company page, newsletters and video, profile optimisation, "
        "and annotated breakdowns of accounts that grew. Cite LinkedIn's own help "
        "centre, business and engineering pages and give the date of each."
    ),
    "q9_instagram_platform_craft": (
        "How Instagram distribution and organic account growth actually work in 2026: "
        "what Instagram and Adam Mosseri have publicly stated about ranking across "
        "Feed, Reels, Stories and Explore, what changed during 2025 and 2026, sends "
        "and saves versus likes, Reels versus carousels versus photos for reach, "
        "hashtags and in-app search, posting cadence, profile and bio optimisation, "
        "comment-to-DM mechanics, and annotated breakdowns of accounts that grew. "
        "Cite Instagram's own creator and help documentation with dates."
    ),
    "q10_facebook_platform_craft": (
        "How Facebook organic distribution actually works for businesses in 2026: "
        "what Meta documents about News Feed ranking and Page distribution, what "
        "changed during 2025 and 2026, the state of unpaid Page reach, Facebook "
        "Groups as a distribution and community surface, Reels on Facebook, "
        "cross-posting from Instagram, local and community-business use cases, and "
        "when a business should not bother with a Facebook Page at all. Cite Meta's "
        "own business help, newsroom and transparency documentation with dates."
    ),
    "q11_youtube_platform_craft": (
        "How YouTube distribution and channel growth actually work in 2026: what "
        "YouTube documents about its recommendation system, the difference between "
        "browse, suggested and search traffic, click-through rate and average view "
        "duration as levers, the Shorts feed and how it differs from long-form, "
        "titles thumbnails and packaging, publishing cadence, playlists and channel "
        "structure, monetisation thresholds, and annotated breakdowns of channels "
        "that grew. Cite YouTube's own creator documentation and blog with dates."
    ),
    "q12_tiktok_platform_craft": (
        "How TikTok distribution and account growth actually work in 2026: what "
        "TikTok documents about For You page ranking and content distribution, what "
        "changed during 2025 and 2026 including any regulatory or ownership effects "
        "on the product, watch time and completion as levers, sounds trends and "
        "participation formats, search and TikTok SEO, posting cadence, the Creative "
        "Center as a research tool, and annotated breakdowns of accounts that grew. "
        "Cite TikTok's own newsroom, support and business documentation with dates."
    ),
    "q13_secondary_platforms_craft": (
        "How X, Reddit, Pinterest, Threads and Snapchat actually work for a business "
        "in 2026: what each platform documents about how content is ranked and "
        "surfaced, what changed on each during 2025 and 2026, which kind of business "
        "each one genuinely suits, the norms and moderation rules that get brands "
        "removed or downranked on each, realistic effort-to-return, and explicitly "
        "when a business should not use each one. Cite each platform's own "
        "documentation with dates, and be concrete about which are not worth it."
    ),
    # ---------------------------------------------- supplementary doc passes (q15-q17)
    #
    # ADDED after the first live run, which is the honest reason they exist and why they
    # are phrased so differently from q8-q14. That run returned 13 first-party docs and
    # ALL of them were Meta or YouTube: zero Instagram, zero TikTok, zero Pinterest, zero
    # X. Tracing the raw passes showed this was NOT the junk gate - those hosts produced
    # literally zero hits across all 14 passes - so widening the gate could not fix it.
    # Asking "how does Instagram rank, cite Instagram's documentation" returns agency
    # blogs ABOUT the documentation, because that is what ranks for that phrasing.
    #
    # These three ask for the documents themselves, in the documents' own vocabulary, and
    # name the hosts. In a corpus where first-party docs are the PRIMARY source, a
    # platform with no [P*] entry cannot be advised on honestly.
    "q15_instagram_tiktok_docs": (
        "Official Instagram and TikTok documentation and announcements explaining how "
        "content is ranked and distributed: Instagram help centre and creator pages on "
        "Feed, Reels, Stories and Explore ranking signals, Adam Mosseri's published "
        "statements on how ranking works, TikTok support and newsroom pages on how the "
        "For You feed recommends videos, TikTok's published recommendation-system "
        "explanations, and each platform's own community guidelines on what limits "
        "distribution. site:help.instagram.com site:about.instagram.com "
        "site:creators.instagram.com site:support.tiktok.com site:newsroom.tiktok.com"
    ),
    "q16_linkedin_docs": (
        "Official LinkedIn documentation and engineering publications explaining how the "
        "LinkedIn feed ranks and distributes posts: LinkedIn engineering blog write-ups "
        "on the feed ranking architecture and its relevance models, LinkedIn newsroom "
        "announcements about feed changes, LinkedIn help centre pages on how the feed "
        "decides what members see, and LinkedIn's published guidance for creators. "
        "site:linkedin.com/blog/engineering site:news.linkedin.com "
        "site:engineering.linkedin.com site:linkedin.com/help"
    ),
    "q17_secondary_platform_docs": (
        "Official documentation from X, Reddit, Pinterest, Threads and Snapchat "
        "explaining how each ranks and surfaces content: X help pages on timeline "
        "ranking and its open-sourced recommendation algorithm, Reddit help and "
        "moderator documentation on how posts are ranked and what self-promotion rules "
        "apply, Pinterest business and creator documentation on the home feed and "
        "search, Meta documentation covering Threads ranking, and Snapchat's published "
        "content-ranking explanation. site:help.x.com site:business.reddithelp.com "
        "site:help.pinterest.com site:help.snapchat.com"
    ),
    # REWRITTEN after the first live run returned the Social Security Administration.
    # The original opened with the bare words "social listening", and "social" is the
    # highest-frequency word in this entire corpus, so the engines resolved it to the
    # most-searched "social" entity on the internet. Ten of twelve surviving sources were
    # ssa.gov, usa.gov, dictionaries and a bar called Social Kitchen.
    #
    # This version never uses "social" as a leading noun: it leads with "brand mention
    # monitoring" and "community manager", which are unambiguous marketing terms with no
    # government or lexical homonym.
    "q14_listening_community_craft": (
        "Brand mention monitoring and online community management practice in 2026: "
        "how marketing teams track brand and competitor mentions across platforms, "
        "which monitoring tools exist at free and paid tiers and what each can and "
        "cannot see, turning a mention into a response workflow, how a community "
        "manager triages comments and direct messages at volume, moderation and "
        "escalation practice, responding to public criticism of a brand, employee "
        "advocacy programmes, and how share of voice is calculated and where that "
        "calculation misleads marketers. Prefer practitioner walkthroughs, documented "
        "workflows and named tooling."
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
    "q8_linkedin_platform_craft", "q9_instagram_platform_craft",
    "q10_facebook_platform_craft", "q11_youtube_platform_craft",
    "q12_tiktok_platform_craft", "q13_secondary_platforms_craft",
    "q14_listening_community_craft",
    "q15_instagram_tiktok_docs", "q16_linkedin_docs", "q17_secondary_platform_docs",
}
assert CRAFT_PASSES <= set(QUERIES), sorted(CRAFT_PASSES - set(QUERIES))

# Evidence-register passes that need `general` (all four engines) rather than `scientific`
# (exa + tavily). Both of these are provenance questions, and a provenance question has two
# halves that live in different places: WHERE a claim circulates is a Serper question, and
# WHETHER a primary source exists underneath it is an Exa question. Running them scientific
# would retrieve the second half only, which is precisely how you end up unable to say who
# started a number. They keep EVIDENCE_SUFFIX - they are not craft.
GENERAL_PASSES = {"q7_social_folklore_provenance"}
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
    # Checked BEFORE the confirmed match, because the whole point is that these sit on a
    # confirmed publisher's apex. dictionary.cambridge.org inherits cambridge.org, so a
    # dictionary entry for the word "social" tiered as peer-reviewed evidence in the first
    # live run. extract() drops these at the junk gate before tiering, so this guard is
    # belt-and-braces - but tier_of is called directly elsewhere and should not hand back
    # "confirmed" for a dictionary just because the junk gate happened to run first.
    if d in JUNK_DOMAINS or any(d.endswith("." + j) for j in JUNK_DOMAINS):
        return "practitioner"
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
    # First-party platform documentation skips the UGC gate ONLY. It still has to clear
    # the topic guard below, or help.instagram.com/1234 "How to report an account" would
    # ride straight in on the carve-out.
    if not is_platform_doc(url):
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
    # For platform docs the HOST is excluded from the haystack. Every one of them contains
    # a platform name that is itself a topic token - help.instagram.com always matches
    # "instagram" - so leaving the host in disables the guard for exactly the sources the
    # carve-out just let past, and "How to report an account" would count as on-topic.
    subject = f"{title} {urlsplit(url).path}" if is_platform_doc(url) else f"{title} {url}"
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
    craft_keep = craft_e[:CRAFT_RESERVE]
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
    assert tier_of("https://some-random-blog.com/linkedin-reach",
                   ["q8_linkedin_platform_craft"]) == "craft"
    assert tier_of("https://some-random-blog.com/linkedin-reach",
                   ["q8_linkedin_platform_craft", "q2_exposure_allocation_reach"]) == "practitioner"
    # confirmed still wins, so a real paper surfacing in a craft pass stays evidence
    assert tier_of("https://dl.acm.org/doi/10.1145/1", ["q8_linkedin_platform_craft"]) == "confirmed"
    # ...and a platform doc beats provenance too. EVERY platform doc in this corpus arrives
    # through a craft pass, because the craft passes are the ones that name platforms at
    # all - so without this rule the entire [P*] tier would tier craft and become
    # unquotable for exactly the definitional facts it exists to supply. In content-advisor
    # this cost 7 of the first 9 docs. Here it would cost all of them.
    assert tier_of("https://developers.tiktok.com/doc/content-posting-api",
                   ["q12_tiktok_platform_craft"]) == "practitioner"
    assert tier_of("https://www.linkedin.com/help/linkedin/answer/a424737",
                   ["q8_linkedin_platform_craft"]) == "practitioner"
    assert tier_of("https://blog.youtube/news-and-events/recommendations/",
                   ["q11_youtube_platform_craft"]) == "practitioner"

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
    # REGRESSION, first live run: these four came back from the searches and were all
    # killed as social/UGC by the linkedin.com and snapchat apex entries. The first two
    # are LinkedIn's own engineering write-ups on feed ranking, i.e. the best [P*] source
    # this corpus can have on its single most-asked question.
    assert is_platform_doc("https://www.linkedin.com/blog/engineering/feed/"
                           "engineering-the-next-generation-of-the-linkedin-feed")
    assert is_platform_doc("https://news.linkedin.com/2026/ImprovingTheFeed")
    assert is_platform_doc("https://www.linkedin.com/top-content/marketing/"
                           "digital-advertising-metrics/")
    assert is_platform_doc("https://help.snapchat.com/hc/en-us/articles/8961653169940-"
                           "How-We-Rank-Content")
    assert is_junk("https://news.linkedin.com/2026/ImprovingTheFeed",
                   "Improving the feed") is None
    # ...but a person's post on the same apex is still UGC, not documentation
    assert is_junk("https://www.linkedin.com/posts/apoorv-goyal_i-posted-every-day",
                   "I posted on LinkedIn every day") == "social/UGC"
    # the feed itself is still junk
    assert is_junk("https://www.linkedin.com/pulse/content-strategy-x", "Content strategy") == "social/UGC"
    assert is_junk("https://www.instagram.com/p/Cabc123/", "Reels post") == "social/UGC"
    assert is_junk("https://www.tiktok.com/@user/video/123", "Content tips") == "social/UGC"
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

    # THIS SKILL'S OWN FAILURE MODE. content-advisor's TOPIC_TOKENS describe the artifact
    # - formats, hooks, thumbnails - so a document about how a platform RANKS things read
    # as off-topic while a document about what a Reel looks like sailed through. That is
    # precisely backwards here, and it would have quietly gutted the corpus rather than
    # failing loudly. Each of these is a real query this skill has to be able to answer.
    assert is_junk("https://example.com/x", "How the For You page ranks videos") is None
    assert is_junk("https://example.com/x", "Is shadowbanning real") is None
    assert is_junk("https://example.com/x", "Do hashtags still work") is None
    assert is_junk("https://example.com/x", "Why our organic reach collapsed") is None
    assert is_junk("https://example.com/x", "Growing an account from zero") is None
    assert is_junk("https://example.com/x", "Community management at scale") is None
    assert is_junk("https://example.com/x", "Social listening workflow") is None
    # REGRESSION, first live run: the q14 query "social listening" returned the Social
    # Security Administration, and 10 of 12 surviving sources from that pass were junk.
    # The topic guard cannot catch these - "social" has to be a topic token here - so the
    # domain list is the only place to stop them.
    assert is_junk("https://www.ssa.gov/myaccount/", "my Social Security")
    assert is_junk("https://secure.ssa.gov/RIL/SiView.action", "Social Security")
    assert is_junk("https://www.usa.gov/social-security", "Social Security - USAGov")
    assert is_junk("https://www.merriam-webster.com/dictionary/social", "SOCIAL Definition")
    # the sharpest one: it tiered CONFIRMED off cambridge.org, so a dictionary entry for
    # the word "social" was sitting in the corpus as peer-reviewed evidence
    assert is_junk("https://dictionary.cambridge.org/dictionary/english/social", "SOCIAL")
    assert tier_of("https://dictionary.cambridge.org/dictionary/english/social") != "confirmed"
    # ...and the real publisher is untouched
    assert tier_of("https://www.cambridge.org/core/journals/x/article/y") == "confirmed"
    assert is_junk("https://example.com/x", "Optimising your profile and bio") is None

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

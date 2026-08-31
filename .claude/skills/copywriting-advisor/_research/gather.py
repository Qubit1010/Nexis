#!/usr/bin/env python3
"""Build the copywriting-advisor corpus: 16 deep research passes -> a tiered sources.json.

Subcommands, all idempotent:

    python gather.py run       # the 16 deep passes -> passes/<key>.json  (resume-safe)
    python gather.py extract   # passes/*.json -> a deduped, tiered, capped sources.json
    python gather.py verify    # every [sN] in the hub + spoke references/ resolves
    python gather.py           # run, then extract

Cloned from .claude/skills/branding-advisor/_research/gather.py, which was cloned from
strategic-foundation's, which was collapsed out of seo-advisor's run_passes.py +
build_corpus.py. Same Exa path, same reason: NotebookLM auth for that account has been
dead since 2026-07-14, and research-backed-skills.md explicitly permits the direct-Exa
fallback.

Evidence rules carried over unchanged, each of which was a real bug in an earlier run:
  - no blanket ".gov" or ".edu = confirmed" (a suffix carries no evidentiary signal)
  - a topic-token guard so an off-topic PDF cannot ride in on a trusted domain
  - a per-domain cap so one agency blog cannot dominate the corpus
  - confirmed-tier sources jump the global cap
  - indices are stable across refreshes, so existing [sN] citations never repoint

What is different here is the tier list. Copywriting's empirical literature lives in
advertising and consumer psychology - message framing, processing fluency, social
proof, emotional appeals - rather than the marketing-science and brand-equity journals
branding leaned on. CONFIRMED_DOMAINS is rebuilt around those publishers.

This matters more here than anywhere else in the repo. Copywriting is the most
folklore-dense subject Nexis covers, and almost none of the folklore is falsifiable as
stated: "you have 8 seconds", "nobody reads below the fold", "long copy outsells
short", "the $300M button", "personalized subject lines lift opens 26%". Every one of
those circulates as a finding and none of them began as one. Separating the measured
from the merely repeated IS the skill.

Two tier calls worth stating outright, because they are judgment and not mechanism:

  - nngroup.com and baymard.com are CONFIRMED. Both run original moderated usability
    and eye-tracking studies and publish method alongside result. They are the primary
    source for scanning, scrolling and form behaviour, and a corpus that tiered them
    practitioner would have no confirmed evidence at all for how people actually read
    a page. This is a deliberate exception to "peer-reviewed or primary data", made on
    the grounds that they ARE the primary data.
  - Every email/CRM/landing-page SaaS "benchmark report" is PRACTITIONER, without
    exception, however large the sample. They measure their own customers, publish no
    method, and have a commercial interest in the number. Mailchimp, HubSpot,
    Klaviyo, Campaign Monitor, Unbounce, Litmus: all practitioner. Several of the
    claims this skill exists to refuse originate in exactly these reports.

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

# The spokes that cite this corpus. verify() walks these too, because a citation
# written in a different folder from the sources.json it points at is exactly the one
# most likely to rot unnoticed. blog-writer is here because its client-brand path
# leans on this corpus even though it keeps its own for AEO/GEO.
SPOKES = ("copy-conversion", "blog-writer")

# Raised from 280 on 2026-08-15 when the craft tier was added. The corpus had legitimately
# grown to 417 locked sources across 29 passes, so a 280 cap left room = 280 - confirmed -
# craft = 4, and silently discarded every new source instead of limiting low-quality growth.
# The cap governs how much PRACTITIONER material may accumulate; confirmed and craft have
# their own allocations below.
SOURCE_CAP = 470
PER_DOMAIN_CAP = 5
# youtube.com is one domain holding many distinct teardowns, so the standard cap would
# reduce the whole video tier to five videos.
CRAFT_DOMAIN_CAP = 14
# Reserved allocation so the craft tier cannot be squeezed out by whichever vendor
# pages happened to rank - it is precisely what the first corpus was missing.
CRAFT_RESERVE = 90

# Peer-reviewed research or primary data, versus an agency or SaaS vendor making a case
# for its own service. Copywriting's empirical literature sits in advertising, consumer
# psychology and psycholinguistics, so those publishers lead the list.
#
# Deliberately NOT here: hbr.org, every conversion-optimization agency blog, every
# "we analyzed 10 million emails" vendor report, and the swipe-file sites. Also not
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
    # Advertising and consumer psychology specifically. This is where copywriting's
    # primary literature actually lives: JCR and JCP carry the framing, fluency and
    # persuasion work; the AMA publishes Journal of Marketing and JMR; the Journal of
    # Advertising and JAR carry the ad-copy and emotional-appeal studies; APA carries
    # the underlying cognition.
    "ama.org", "journals.ama.org", "myama.org",
    "psycnet.apa.org", "apa.org",
    "acrwebsite.org",
    "journalofadvertisingresearch.com", "warc.com",
    "palgrave.com", "link.palgrave.com",
    # HCI and information retrieval. How people scan, read and skip on a screen is a
    # CHI/CSCW/SIGIR literature, and the AEO/GEO passes depend on the IR side of it.
    "dl.acm.org", "acm.org", "sigir.org", "aclanthology.org", "ieee.org",
    "ieeexplore.ieee.org",
    # Original empirical usability research. See the header: these ARE the primary
    # source for reading, scanning and form behaviour on real pages, and they publish
    # method with result. Enumerated deliberately, not inferred.
    "nngroup.com", "baymard.com",
    # primary statistical and regulatory data. The FTC one matters: endorsement and
    # testimonial rules are law, not opinion, and copy that ignores them is a
    # liability rather than a style choice.
    "ftc.gov", "bls.gov", "census.gov", "sec.gov",
}

# The craft canon: where practitioners actually teach and demonstrate copywriting.
#
# Added 2026-08-15 after Aleem pointed out the first corpus was 2 craft sources out of
# 314. The cause was a bad transplant: branding's junk list rightly excluded Dribbble
# and Behance because a portfolio page is an image with no claim in it, and that logic
# was carried over to swipe files and YouTube. For copywriting that is exactly backwards
# - a teardown of a page that shipped IS the practitioner evidence, and the per-platform
# format conventions live nowhere else.
#
# These are a SEPARATE tier, never merged into practitioner. A craft source may show how
# to write something; it may never support a factual claim. tier_of() returns "craft" and
# the factcheck mode ignores that tier entirely.
CRAFT_DOMAINS = {
    # named practitioner canon
    "copyhackers.com", "marketingexamples.com", "harrydry.com", "verygoodcopy.com",
    "nickkolenda.com", "cxl.com", "copyblogger.com", "growth.design", "julian.com",
    "goodcopy.co", "goodemailcopy.com", "emaillove.com", "marketingbrew.com",
    # swipe files and teardown galleries: real shipped copy, which is what a per-asset
    # format table has to be built from
    "swiped.co", "swipefile.com", "swipe-file.com", "reallygoodemails.com",
    "landingfolio.com", "saaslandingpage.com", "onepagelove.com", "lapa.ninja",
    "landingrate.io", "pageflows.com",
    # video teardowns and course content. NotebookLM ingests these natively via
    # `source add --type youtube`, so a video is transcribed and queryable rather than
    # a dead link - which is the argument for including them at all.
    "youtube.com", "youtu.be",
}

# Somebody's opinion with no editorial process, or a page with no argument in it.
# Medium, Substack and Reddit stay junked by Aleem's explicit call: highest volume,
# lowest signal, and impossible to tier honestly.
JUNK_DOMAINS = {
    "facebook.com", "linkedin.com", "twitter.com", "x.com", "instagram.com",
    "pinterest.com", "tiktok.com", "quora.com", "medium.com", "reddit.com",
    "slideshare.net", "scribd.com", "issuu.com",
    "substack.com", "coursehero.com", "studocu.com",
    "quizlet.com", "chegg.com", "cliffsnotes.com", "bartleby.com",
    # Freelance marketplaces and job boards, which rank for "copywriter" and carry
    # service listings rather than evidence.
    "upwork.com", "fiverr.com", "indeed.com", "glassdoor.com", "ziprecruiter.com",
}

# Named-creator primary sources living on an otherwise-junked domain. Added 2026-08-31,
# Aleem's explicit call, mirroring content-advisor's identical exemption (added same
# day, same reasoning): q30 exists specifically to find named creators explaining their
# OWN formatting technique, and the clearest instance the pass found is the creator's
# own linkedin.com post. Exact-URL allowlist, not a domain or name-pattern rule - see
# content-advisor/_research/gather.py's CREATOR_PRIMARY_SOURCE_URLS for the full
# rationale against broadening this. Raw, not normalized - norm_url() is defined below,
# so is_junk() normalizes both sides at call time instead.
CREATOR_PRIMARY_SOURCE_URLS = (
    "https://www.linkedin.com/posts/justinwelsh_my-strategy-when-i-started-was-pretty-basic-activity-7415011488983203840-7Rmy",
)

MIRROR_SUFFIXES = (".google.cn", ".google.co.jp", ".google.de", ".google.fr")

# A source has to be plausibly about persuasive writing, the psychology under it, or
# how people read it. Without this guard a trusted publisher admits anything it happens
# to print, which is how an earlier corpus ranked a legislative calendar as a top-tier
# source.
TOPIC_TOKENS = (
    # the craft
    "copy", "copywrit", "headline", "subhead", "hook", "tagline", "slogan",
    "call to action", "cta", "landing page", "sales page", "sales letter",
    "subject line", "email", "newsletter", "advertis", "ad copy", "creative",
    "product description", "microcopy", "button", "form", "checkout", "wording",
    # the mechanism
    "persuas", "persuade", "influenc", "framing", "frame", "argument", "rhetoric",
    "appeal", "emotion", "affect", "arousal", "fear", "humor", "humour",
    "social proof", "testimonial", "review", "endorse", "credibil", "trust",
    "scarcity", "urgency", "guarantee", "reciproc", "commitment", "anchor",
    "nudge", "compliance", "attitude", "intention", "motivat",
    # how it is read
    "readab", "legib", "fluency", "disfluen", "comprehen", "process",
    "attention", "scan", "scroll", "fold", "eye track", "eye-track", "gaze",
    "recall", "memor", "salien", "concrete", "abstract", "specific", "vague",
    "narrative", "story", "storytell", "transportation",
    # the outcome
    "conversion", "convert", "click", "click-through", "clickthrough", "response",
    "open rate", "engagement", "purchase", "choice", "preference", "willingness",
    "funnel", "acquisition", "churn", "revenue",
    # method
    "experiment", "randomi", "field study", "a/b", "split test", "meta-analy",
    "replicat", "effect size", "sample size", "statistical",
    # search-era distribution
    "search", "seo", "aeo", "geo", "answer engine", "generative engine",
    "ai search", "ai overview", "citation", "retriev", "rank", "query",
    "llm", "language model", "chatbot",
    # broad catch-alls. The guard exists to reject a document that rode in on a
    # trusted publisher while being clearly off-subject, not to be a precision filter.
    "consumer", "customer", "audience", "market", "brand", "messag", "communicat",
    "content", "writ", "text", "language", "linguistic", "word", "blog", "article",
    "web", "online", "digital", "user", "product", "business", "commerc",
)

SUFFIX = (" Give specific numbers, named frameworks, effect sizes and concrete steps, "
          "and cite sources. Distinguish peer-reviewed evidence from agency or vendor "
          "opinion. Where a widely repeated statistic has no traceable primary source, "
          "say so explicitly. Where the sources disagree, preserve the disagreement "
          "rather than picking a side.")

# CRAFT_SUFFIX contains no _SCI_HINT token (no "study", "paper", "journal", "trial",
# "peer-reviewed"), unlike SUFFIX above. That is not cosmetic: SUFFIX's "Distinguish
# peer-reviewed evidence..." phrase is exactly what routed every craft pass in this file
# under `scientific` mode historically (q27's own comment documents the resulting
# failure). Added 2026-08-31 alongside q30, the first craft pass to explicitly request
# `--mode practical` rather than rely on auto-detection - see run_pass().
CRAFT_SUFFIX = (
    " Show concrete worked examples, named creators and practitioners, current platform "
    "specifications with dates, and step-by-step technique. Prefer teardowns, annotated "
    "breakdowns and practitioner walkthroughs over summaries. Where a widely repeated "
    "claim has no traceable origin, say so.")

# One deep pass per subject the hub has to be able to answer on. q16 is what the
# factcheck mode leans on hardest, so it targets provenance and replication directly
# rather than technique.
QUERIES = {
    "q1_headline_evidence": (
        "Empirical research on headline and title effectiveness: experimental studies "
        "on headline wording and readership or click-through, curiosity gap and "
        "information gap research, question versus statement headlines, numbers and "
        "listicle formats in headlines, negativity and emotional wording effects on "
        "click behaviour in large-scale field experiments, headline length, and "
        "evidence on whether clarity or curiosity performs better and under what "
        "conditions."
    ),
    "q2_cta_button_copy": (
        "Research on calls to action and button copy: experimental evidence on action "
        "verb choice, first-person versus second-person button wording, button "
        "placement and repetition, friction words and perceived commitment, the "
        "provenance of the widely repeated three hundred million dollar button case "
        "study, evidence on whether button colour affects conversion, and how many "
        "distinct calls to action a page can carry before performance degrades."
    ),
    "q3_landing_page_structure": (
        "Landing page and sales page structure research: evidence on above-the-fold "
        "content and whether users scroll, page length and conversion, hero section "
        "composition, form field count and completion rates, navigation removal on "
        "dedicated landing pages, message match between ad and landing page, and "
        "controlled studies rather than vendor case studies on any of these."
    ),
    "q4_email_copy_subject_lines": (
        "Email marketing copy research: experimental evidence on subject line wording "
        "and open behaviour, personalization effects in email field experiments, "
        "subject line length, emoji and punctuation effects, preview text, send-time "
        "research, sequence and cadence effects, and critically how Apple Mail Privacy "
        "Protection since 2021 changed what an open rate measures and whether "
        "pre-2021 email benchmarks remain comparable."
    ),
    "q5_ad_copy_effectiveness": (
        "Advertising copy effectiveness research: what distinguishes high-performing "
        "from low-performing ad copy in controlled tests, informational versus "
        "transformational appeals, message repetition and wearout, creative quality "
        "effect sizes relative to targeting and budget, search ad copy experiments, "
        "social ad copy length, and meta-analyses of advertising elasticity."
    ),
    "q6_message_framing": (
        "Message framing research: gain versus loss framing meta-analyses and their "
        "moderators, prospect theory applied to marketing messages, attribute framing "
        "versus goal framing, positive and negative framing effect sizes, temporal "
        "framing and construal level theory, regulatory focus and message congruence, "
        "and the replication status of the classic framing findings."
    ),
    "q7_social_proof_testimonials": (
        "Social proof and testimonial research: experimental evidence on consumer "
        "reviews and ratings affecting purchase, the effect of review volume versus "
        "review valence, descriptive norms in persuasive messages, the "
        "identifiable-victim and specificity effects in testimonials, fake review "
        "detection and consumer scepticism, expert versus peer endorsement, and the "
        "Federal Trade Commission rules governing testimonials and endorsements in "
        "advertising."
    ),
    "q8_scarcity_urgency_guarantees": (
        "Scarcity, urgency and risk reversal research: experimental evidence on limited "
        "quantity versus limited time scarcity appeals, deadline effects on response, "
        "consumer scepticism and reactance toward manufactured urgency, money-back "
        "guarantee and warranty effects on purchase and on returns, free trial framing, "
        "and regulatory constraints on countdown timers and false scarcity claims."
    ),
    "q9_readability_fluency_specificity": (
        "Processing fluency and readability research in persuasion: fluency effects on "
        "judgment truth and liking, disfluency and its effect on recall and "
        "deliberation, concreteness and imageability effects on comprehension and "
        "memory, specificity and numeric precision effects on credibility, jargon and "
        "its effect on perceived competence versus comprehension, readability formulas "
        "and their validity, and sentence length research."
    ),
    "q10_copy_length": (
        "Evidence on copy length: experimental and field research on long versus short "
        "copy, the interaction between message length and involvement or purchase "
        "consideration, elaboration likelihood model evidence on argument quantity "
        "versus quality, word count and conversion in controlled tests, and the "
        "provenance of the direct-response claim that long copy outsells short copy."
    ),
    "q11_voice_of_customer_language": (
        "Voice of customer research and linguistic mimicry: methods for mining customer "
        "language from reviews interviews and support tickets, evidence on whether "
        "mirroring customer vocabulary improves persuasion, linguistic style matching "
        "and accommodation research, jobs-to-be-done interview methodology, message "
        "testing methods, and evidence on whether customer-derived language "
        "outperforms internally written language in controlled tests."
    ),
    "q12_benefits_features_construal": (
        "Benefits versus features research: means-end chain theory and laddering "
        "methodology, attribute versus benefit versus value claims and their measured "
        "effects, construal level theory applied to product messaging, desirability "
        "versus feasibility framing across temporal distance, abstract versus concrete "
        "product claims, and evidence on when feature-level detail outperforms benefit "
        "language."
    ),
    "q13_emotional_appeals": (
        "Emotional appeals in advertising and copy: meta-analyses of emotional versus "
        "rational appeal effectiveness, discrete emotion research on fear appeals "
        "including the extended parallel process model, humour effects on recall and "
        "persuasion, awe and anger and their effect on sharing and virality, the "
        "Binet and Field emotional-versus-rational long-term effectiveness argument "
        "and criticism of it, and emotional arousal effects on transmission."
    ),
    "q14_aeo_geo_copy_2026": (
        "Writing content for answer engines and AI search in 2025 and 2026: what makes "
        "a passage likely to be retrieved and cited by large language model search "
        "systems, generative engine optimization research including the Princeton GEO "
        "study and its methodology and limitations, answer-first and self-contained "
        "passage structure, chunking and retrieval-augmented generation implications "
        "for how copy should be written, citation behaviour of ChatGPT Perplexity and "
        "Google AI Overviews, and measured differences between traditional search "
        "ranking factors and AI citation factors."
    ),
    "q15_platform_format_conventions_2026": (
        "Platform copy format constraints and conventions in 2026: documented character "
        "limits and truncation points for Google Ads Meta Ads LinkedIn and email "
        "subject lines, mobile versus desktop truncation, evidence on optimal length "
        "per platform from large-scale analyses, accessibility requirements for link "
        "text and alt text and plain language, and how platform algorithm changes have "
        "altered what copy formats get distribution."
    ),
    # ---- the provenance pass ---------------------------------------------
    # The single most load-bearing pass in this corpus. Every prior skill in this repo
    # found that its most valuable output was refusal, and copywriting has more
    # unsourced folklore in circulation than branding did. Asking about the claims
    # directly - rather than hoping the technique passes happen to debunk them - is
    # what makes factcheck mode answerable rather than a shrug.
    "q16_folklore_provenance_replication": (
        "Provenance and replication of widely repeated marketing statistics: the origin "
        "of the claim that human attention span has fallen to eight seconds and whether "
        "any primary study supports it, the origin of the claim that users do not "
        "scroll below the fold and what eye-tracking data actually shows, the three "
        "hundred million dollar button anecdote and whether it was a controlled "
        "experiment, claims that personalized email subject lines increase open rates "
        "by a specific percentage and their sources, the claim that people read only "
        "twenty percent of a web page, replication and statistical power problems in "
        "commercial A/B testing, and how often reported conversion test wins fail to "
        "replicate."
    ),
    # ---- remedial passes -------------------------------------------------
    # Four holes the first extract exposed, each found by checking the corpus against
    # what the skill files already assert rather than by eyeballing the totals.
    #
    # q4 came back 0 confirmed / 10 practitioner. It is not a retrieval failure so much
    # as a register failure: "email subject line" is vendor vocabulary and returns
    # vendor benchmark reports. The real work is randomized field experiments published
    # in Marketing Science and JMR, and the corpus had zero INFORMS sources. This asks
    # in that register and deliberately avoids the phrase "best practices".
    "q17_email_field_experiments": (
        "Randomized field experiments in email and direct marketing: large-scale field "
        "experiments measuring the causal effect of email personalization on opens "
        "clicks and purchase, Sahni Wheeler and Chintagunta on personalization in email "
        "marketing, retargeting and email frequency field experiments, advertising "
        "measurement and the difficulty of establishing causal advertising effects, "
        "selection bias in observational marketing benchmarks, and how Apple Mail "
        "Privacy Protection affects the validity of open-rate measurement."
    ),
    # q16 was supposed to carry the replication half of factcheck mode and returned
    # attention-span content almost exclusively - the engines locked onto the most
    # famous claim in the query and ignored the rest. The experimentation literature
    # is a separate body filed under online controlled experiments, and without it the
    # skill cannot honestly say why reported conversion wins evaporate.
    "q18_experiment_validity_replication": (
        "Online controlled experiments and their validity: statistical power and sample "
        "size requirements for A/B tests on conversion, the winner's curse and "
        "regression to the mean in reported experiment results, peeking and optional "
        "stopping problems in sequential testing, false discovery rates when running "
        "many simultaneous tests, replication rates of marketing and conversion "
        "experiments, Kohavi and colleagues on trustworthy online controlled "
        "experiments, and effect size distributions actually observed in commercial "
        "experimentation programs."
    ),
    # The corpus had zero nngroup.com and zero baymard.com despite both being
    # whitelisted as confirmed. Nothing in the first sixteen passes asked how people
    # physically read a page, so the fold and scrolling claims - which factcheck mode
    # is expected to rule on - had no evidence behind them at all.
    "q19_reading_scanning_eye_tracking": (
        "How people actually read and scan web pages: eye-tracking studies of web "
        "reading, F-pattern and layer-cake scanning behaviour, Nielsen Norman Group "
        "research on scrolling and attention above and below the fold, what percentage "
        "of page text is actually read, fixation and reading rate measurement, Baymard "
        "Institute usability research on checkout and form field completion, banner "
        "blindness, and how mobile reading behaviour differs from desktop."
    ),
    # method.md and review-rubric.md both already assert that testimonial and
    # endorsement rules are law rather than style. That assertion needs a primary
    # source or it has to come out. ftc.gov was whitelisted and returned nothing,
    # because no pass asked a legal question.
    "q20_endorsement_disclosure_law": (
        "Advertising claim substantiation and endorsement law: the Federal Trade "
        "Commission Endorsement Guides and 16 CFR Part 255, disclosure requirements for "
        "testimonials reviews and influencer endorsements, the FTC rule on fake and "
        "deceptive reviews, substantiation requirements for express and implied "
        "advertising claims, regulation of dark patterns including false urgency and "
        "countdown timers, negative option and subscription cancellation rules, and "
        "enforcement actions involving deceptive marketing claims."
    ),
    # ---- craft passes (q21-q28) ------------------------------------------
    # Deliberately written in PRACTITIONER register, which is the whole point. Every
    # one of q1-q20 says "empirical research", "meta-analysis", "field experiments" -
    # so even the craft web that was not junked never surfaced. These ask the way a
    # copywriter asks, name the practitioners by name, and request examples and
    # teardowns rather than effect sizes.
    #
    # Sources from these land in the CRAFT tier: usable for technique, format and
    # worked examples, never as evidence for a claim.
    "q21_landing_page_teardowns": (
        "Landing page and sales page copy teardowns with real examples: annotated "
        "breakdowns of high-converting landing pages, before and after copy rewrites, "
        "hero section examples, Copyhackers and Joanna Wiebe teardowns, Marketing "
        "Examples by Harry Dry, CXL landing page analysis, SaaS homepage copy examples, "
        "and swipe files of pages that actually shipped."
    ),
    "q22_headline_hook_formulas": (
        "Headline and hook writing formulas with examples: proven headline templates and "
        "swipe files, hook formulas for social and long form, subject line examples that "
        "worked, VeryGoodCopy micro-lessons, how to write a first line that earns the "
        "second, curiosity and specificity techniques, and annotated examples of "
        "headlines rewritten from weak to strong."
    ),
    "q23_email_sequence_craft": (
        "Email copywriting craft with real examples: welcome sequence examples and "
        "teardowns, nurture and onboarding sequence structure, abandoned cart email "
        "copy, Really Good Emails examples, how many emails in a sequence and what each "
        "one does, plain text versus designed email copy, and annotated breakdowns of "
        "sequences from real companies."
    ),
    "q24_ad_copy_craft_by_platform": (
        "Ad copy craft by platform in 2026: writing Google Search ads including "
        "responsive search asset strategy, Meta and Facebook and Instagram ad copy "
        "structure with hook body CTA, LinkedIn ad copy for B2B, primary text versus "
        "headline versus description, ad copy examples and teardowns, matching ad copy "
        "to landing page, and how much copy each placement actually shows before "
        "truncating."
    ),
    "q25_cta_microcopy_craft": (
        "CTA and microcopy craft with examples: button copy examples that outperformed, "
        "writing form labels and error messages and empty states, reassurance copy near "
        "the button, checkout microcopy, UX writing guidelines and patterns, Growth "
        "Design case studies, and annotated examples of microcopy rewrites."
    ),
    "q26_product_description_craft": (
        "Product description and ecommerce copywriting craft: product page copy "
        "structure, writing specifications alongside benefits, DTC brand product copy "
        "examples, category page copy, marketplace listing copy for Amazon and Shopify, "
        "and teardowns of product pages that convert."
    ),
    "q27_platform_format_conventions_craft": (
        "Practical platform copy formatting guides for 2026: current character limits "
        "and truncation points for Google Ads and Meta Ads and LinkedIn and X and email "
        "subject lines, how much text shows on mobile before the more link, ideal length "
        "per platform from practitioner testing, formatting for skimmability with line "
        "breaks and whitespace, and up to date platform specification cheat sheets."
    ),
    # q27 failed exactly the way branding's q13 did: asking for "platform copy
    # formatting conventions" retrieved LinkedIn PROFILES of people who do that work -
    # a medical editor, a Google Ads coach - rather than the specifications. The fix is
    # the same one that worked there: drop the vocabulary that describes a job and use
    # the vocabulary that appears ON the artifact, so the query matches spec sheets.
    "q29_platform_character_specs": (
        "Google Ads responsive search ad headline 30 character limit and description 90 "
        "character limit, Meta Facebook Instagram ad primary text 125 characters "
        "headline 40 characters link description, LinkedIn sponsored content intro text "
        "150 characters headline 70 characters, X post character limit, email subject "
        "line truncation on iPhone Gmail mobile pixels, meta description 155 characters, "
        "title tag 60 characters, ad specs cheat sheet 2026."
    ),
    "q28_copywriting_2026_technique_shifts": (
        "What changed in copywriting technique in 2025 and 2026: writing copy that does "
        "not read as AI generated, how copywriters are using and not using AI in their "
        "workflow, copy for AI search and answer engines versus traditional pages, "
        "shifts in what converts post generative AI, conversational and chat interface "
        "copy, and practitioner commentary on which older copywriting rules stopped "
        "working."
    ),
    # copy-conversion/references/platform-formatting.md cites this corpus for LinkedIn
    # line-break/whitespace structure and Instagram caption structure, but neither claim
    # had a source - added 2026-08-31 specifically to close that gap, anchored on named
    # creators per q27's own retrieval-trap lesson rather than "best practices" phrasing.
    "q30_linkedin_instagram_line_formatting_craft": (
        "How specific named LinkedIn ghostwriters and Instagram caption writers, such as "
        "Justin Welsh, Katelyn Bourgoin, Amanda Natividad and Dan Koe, explain their own "
        "line-break, paragraph-length and white-space technique in a text post in 2026, "
        "drawn from their own newsletter, YouTube video or a named third-party teardown "
        "of their formatting rather than a generic social-media best-practices listicle, "
        "and how they treat the caption and the image as one unit on Instagram "
        "specifically. Where a widely repeated claim that short paragraphs and frequent "
        "line breaks improve readability has no traceable primary source or named "
        "creator explanation behind it, say so explicitly rather than restating it as "
        "settled."
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
    "q21_landing_page_teardowns", "q22_headline_hook_formulas",
    "q23_email_sequence_craft", "q24_ad_copy_craft_by_platform",
    "q25_cta_microcopy_craft", "q26_product_description_craft",
    "q27_platform_format_conventions_craft",
    "q28_copywriting_2026_technique_shifts",
    "q30_linkedin_instagram_line_formatting_craft",
}


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
    if d in CRAFT_DOMAINS or any(d.endswith("." + c) for c in CRAFT_DOMAINS):
        return "craft"
    # provenance: found only by craft-register questions
    if topics and set(topics) <= CRAFT_PASSES:
        return "craft"
    return "practitioner"


def is_junk(url, title):
    d = domain_of(url)
    exempt = norm_url(url) in {norm_url(u) for u in CREATOR_PRIMARY_SOURCE_URLS}
    if not exempt and (d in JUNK_DOMAINS or any(d.endswith("." + j) for j in JUNK_DOMAINS)):
        return "social/UGC"
    if any(d.endswith(m) for m in MIRROR_SUFFIXES):
        return "localized mirror"
    # Normalize separators to spaces so short tokens match as whole words. Plain
    # substring matching lets "hou-SEO-frepresentatives" through; \b would not help
    # either, since underscores count as word characters.
    # For an exempted URL the HOST is excluded from the haystack (matches
    # content-advisor's platform-doc treatment): linkedin.com is itself a topic token,
    # so leaving it in would let anything added to the exemption list pass for free.
    subject = f"{title} {urlsplit(url).path}" if exempt else f"{title} {url}"
    hay = " " + re.sub(r"[^a-z0-9]+", " ", subject.lower()).strip() + " "
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

    # Craft passes get the clean suffix AND an explicit --mode, rather than trusting
    # auto-detection on a query + suffix that (for every pass before q30) contained the
    # word "peer-reviewed". Evidence passes are untouched: SUFFIX's science-register
    # language is what correctly routes them, so it stays implicit for them.
    craft = key in CRAFT_PASSES
    suffix = CRAFT_SUFFIX if craft else SUFFIX
    mode_args = ["--mode", "practical"] if craft else []

    def _attempt(extra):
        try:
            r = subprocess.run(
                [sys.executable, str(RESEARCH_PY), "--query", query + suffix,
                 "--depth", "deep", "--json", *mode_args, *extra],
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
            cap = CRAFT_DOMAIN_CAP if tier == "craft" else PER_DOMAIN_CAP
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
    practitioner_e = [e for e in capped if tier_of(e["url"], e["topics"]) == "practitioner"]
    craft_keep = craft_e[:CRAFT_RESERVE]
    room = max(0, SOURCE_CAP - len(confirmed_e) - len(craft_keep))
    if len(practitioner_e) > room:
        log(f"CAP {len(capped)} eligible -> {len(confirmed_e)} confirmed + "
            f"{len(craft_keep)} craft + top {room} practitioner")
    ranked = confirmed_e + craft_keep + practitioner_e[:room]

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
    if retiered:
        log(f"  re-tiered {retiered} existing source(s) under the current rules")

    counts = {t: sum(1 for s in sources if s["tier"] == t)
              for t in ("confirmed", "craft", "practitioner")}
    out = {
        "generated_at": datetime.now().date().isoformat(),
        "method": ("28 deep passes via the in-repo research skill (Exa+Tavily+Serper+Jina "
                   "fused, content-extracted), deduped by normalized URL, junk-filtered, "
                   "per-domain capped, tiered confirmed / craft / practitioner"),
        "note": ("inline [sN] in references/research-synthesis.md resolves to "
                 "sources[N-1]. tier=craft means technique and worked examples only - "
                 "never usable to support a factual claim, and invisible to factcheck "
                 "mode"),
        "total_found": total_found,
        "source_count": len(sources),
        "confirmed": counts["confirmed"],
        "craft": counts["craft"],
        "practitioner": counts["practitioner"],
        "sources": sources,
    }
    (RESEARCH_DIR / "sources.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"extract: {total_found} deduped -> {len(sources)} kept "
        f"({counts['confirmed']} confirmed / {counts['craft']} craft / "
        f"{counts['practitioner']} practitioner)")


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
    """The evidence rules are the whole point of this file, so they get a check."""
    assert norm_url("http://WWW.Example.com/a/?utm_source=x#f") == "https://example.com/a"
    assert norm_url("https://example.com") == "https://example.com/"
    # advertising and consumer psychology are this corpus's primary literature
    assert tier_of("https://academic.oup.com/jcr/article/34/2/231") == "confirmed"
    assert tier_of("https://psycnet.apa.org/record/2012-1") == "confirmed"
    assert tier_of("https://journals.sagepub.com/doi/10.1177/002224378101800104") == "confirmed"
    # the deliberate exception: original empirical usability research
    assert tier_of("https://www.nngroup.com/articles/scrolling-and-attention/") == "confirmed"
    assert tier_of("https://baymard.com/blog/checkout-flow-average-form-fields") == "confirmed"
    # a vendor measuring its own customers is not evidence, however large the sample
    assert tier_of("https://mailchimp.com/resources/email-marketing-benchmarks/") == "practitioner"
    assert tier_of("https://blog.hubspot.com/marketing/email-open-rates") == "practitioner"
    assert tier_of("https://unbounce.com/conversion-benchmark-report/") == "practitioner"
    # a .edu suffix is not evidence: this is university marketing copy
    assert tier_of("https://www.phoenix.edu/articles/business/copywriting.html") == "practitioner"
    # craft tier: technique and worked examples, never evidence for a claim
    assert tier_of("https://copyhackers.com/2023/01/landing-page-teardown/") == "craft"
    assert tier_of("https://www.youtube.com/watch?v=abc123") == "craft"
    assert tier_of("https://swiped.co/file/example") == "craft"
    assert tier_of("https://marketingexamples.com/copywriting/headlines") == "craft"
    # confirmed wins over craft if a craft domain ever publishes real research
    assert tier_of("https://www.nngroup.com/articles/scrolling-and-attention/") == "confirmed"
    # the bug the topic guard exists for: trusted publisher, off-subject document
    assert is_junk("https://census.gov/119_legislative_schedule.pdf", "Legislative Schedule")
    assert is_junk("https://ftc.gov/business-guidance/endorsement-guides",
                   "Endorsement guides") is None
    # swipe files and video are NO LONGER junk - they are the craft tier. This reversed
    # on 2026-08-15; branding's rule that a gallery carries no claim is true of a logo
    # portfolio and false of a page teardown.
    assert is_junk("https://swiped.co/file/example", "Sales letter") is None
    assert is_junk("https://reallygoodemails.com/emails/x", "Email copy") is None
    assert is_junk("https://www.youtube.com/watch?v=abc", "Copywriting teardown") is None
    # still junk by Aleem's explicit call: high volume, low signal, untierable
    assert is_junk("https://linkedin.com/pulse/copywriting", "Copywriting") == "social/UGC"
    assert is_junk("https://medium.com/@x/copywriting", "Copywriting") == "social/UGC"
    assert is_junk("https://reddit.com/r/copywriting", "Copywriting") == "social/UGC"

    # named-creator primary source exemption (2026-08-31) - exact-URL, not per-domain/person.
    # The domain gate is skipped, but the topic guard still independently applies: this
    # corpus's TOPIC_TOKENS is scoped to copywriting vocabulary (headline, CTA, subject
    # line...), narrower than content-advisor's, and this exact title contains none of
    # it - so it still resolves "off-topic" here even though the exemption fires. That is
    # correct, not a bug: the exemption removes the domain block, not the relevance bar.
    assert is_junk(
        "https://www.linkedin.com/posts/justinwelsh_my-strategy-when-i-started-was-pretty-basic-activity-7415011488983203840-7Rmy",
        "My strategy when I started was pretty basic") == "off-topic"
    assert is_junk("https://www.linkedin.com/posts/justinwelsh_some-other-post-1234567890",
                   "Some other post") == "social/UGC"
    # short tokens must match as whole words, not substrings
    assert is_junk("https://example.com/octopus-anatomy", "Octopus anatomy") == "off-topic"
    assert is_junk("https://example.com/cta-placement", "CTA placement") is None
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

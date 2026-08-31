# Research synthesis — content marketing, 2026

The cited evidence behind every claim this skill family makes. **560 sources**, **285
confirmed / 140 craft / 135 practitioner**, of which **9 are first-party platform
documentation**. Built 2026-08-15 from **28 deep passes** through the in-repo `research`
skill: 18 in the evidence register (`scientific`, plus `general` for the two provenance
passes) and 10 in the craft register (`practical`).

Every `[sN]` resolves against `_research/sources.json` on the **`index` field**. Run
`python _research/gather.py verify` after editing any citation.

---

## How to read the tags

| Tag | Tier | May be used for | May NOT be used for |
|---|---|---|---|
| `[C]` | confirmed | Supporting a factual claim | - |
| `[P]` | practitioner | A labelled, attributed number | Being stated as measured fact |
| `[P*]` | first-party platform documentation | What a platform **requires or defines** - a limit, a ratio, a metric rule - **quoted with a retrieval date** | Evidence that anything **works** |
| `[K]` | craft | **Technique, worked examples, format conventions** | **Supporting any factual claim. Factcheck mode does not read this tier at all** |

**`[P*]` is the tier this corpus added.** A platform documenting its own product is not
neutral - it has an interest in you posting more - but it is the only primary source for what
a format *is*. Treating it as evidence of performance is the single most likely way to misuse
this corpus.

---

## The tier list, and the calls that were judgment rather than mechanism

**Confirmed** is rebuilt around media and communication research, computational social science
and multimedia learning, rather than the advertising psychology `copywriting-advisor` leaned on.
That means SAGE (33 sources), Taylor & Francis (32), ACM (32), ScienceDirect (30), Springer
(27), PMC (25), plus `ojs.aaai.org` enumerated explicitly because ICWSM proceedings live there
and "AAAI/ICWSM" is not a domain.

**Pew, the Reuters Institute and Ofcom are confirmed**, on the same grounds as
`copywriting-advisor`'s NN/g exception and arguably stronger: probability or panel-based
sampling, published methodology and questionnaires, and - unlike NN/g, which sells consulting -
nothing to sell. `reutersinstitute.politics.ox.ac.uk` is enumerated as a **full host**; listing
`ox.ac.uk` would have confirmed an entire university.

> **The caveat that ships with all three:** they measure media consumption **in a population**.
> They support "X% of adults regularly get news on TikTok". They do **not** support "video
> posts outperform text posts". Conflating the two launders descriptive statistics into
> performance claims.

**Rejected deliberately, and named so nobody promotes them later:** `statista.com`, a paywalled
**re-publisher** of vendor numbers wearing the visual grammar of a data source, and the largest
single laundering vector in this field. `thinkwithgoogle.com` (ad sales in a research costume).
`nielsen.com` and `comscore.com` (syndicated measurement sold to the industry being measured).
`edisonresearch.com` - the closest call, since Infinite Dial uses a probability sample and
publishes method, but Edison sells syndicated research to the broadcasters and podcast networks
the numbers benefit. Every "State of Content Marketing" report is practitioner without
exception, however large the sample.

**Dropped from the inherited copywriting list:** `warc.com` (paywalled commercial
intelligence) and `baymard.com` (checkout usability, irrelevant to content formats).

---

## Corpus corrections, made before this corpus was built

Three defects in the shared research pipeline were found on 2026-08-15 and fixed here. All
three had silently damaged `copywriting-advisor`'s corpus, and any older `gather.py` still
carries them.

1. **One suffix for both registers.** The shared `SUFFIX` contained "peer-reviewed", which
   matches `research.py`'s `_SCI_HINT`, and `detect_mode` checks `_SCI_HINT` before
   `_CRAFT_HINT`. Measured on copywriting's own 29 queries: **14 detect `practical` bare, 0
   with the suffix attached.** Every craft pass there ran `scientific`, so Serper never ran and
   the `site:youtube.com` variant never fired. That corpus has **2 YouTube sources in 494** and
   documents the gap as a limitation of the search engines. **This corpus, with the suffix
   split and `--mode` passed explicitly, has 16.**
2. **The topic guard deleted the subject.** Tokens of length `<= 4` matched as whole words, but
   the token list holds truncated stems. `" blog "` does not occur in real prose, so a page
   titled "Blogging in 2026" was discarded as off-topic. Threshold is now 3.
3. **Platform documentation was unreachable.** `JUNK_DOMAINS` holds the platform apexes and
   `is_junk` matches on suffix, so `help.instagram.com` and `business.linkedin.com` died with
   the feed. Copywriting's corpus contains **zero** LinkedIn, Meta, X, Instagram or TikTok
   sources. This one has 9, via a `PLATFORM_DOC_HOSTS` carve-out that bypasses the junk gate
   only and never the topic guard.

A fourth was found during extraction: the **provenance rule was tiering platform docs as
craft**, because the spec pass that retrieves them is itself a craft pass. Seven of the first
nine were affected. `is_platform_doc` now short-circuits provenance, since "a Reel is 9:16" is
a definitional fact and craft may never support one.

---

## Remaining honest weaknesses

1. **The folklore pass could not find debunkings, only the folklore.** Q17 returned 13 sources,
   12 of them practitioner statistics round-ups. So its findings are **"no traceable primary
   source within this corpus"**, which is weaker than "fabricated". Where
   `copywriting-advisor` could say the 8-second attention span *is* fabricated because it held
   a source tracing it, this corpus can only say the trail runs cold. State it that way.
2. **The 95-5 rule is real and this corpus does not contain it.** It comes from the LinkedIn
   B2B Institute and Ehrenberg-Bass. Q17 lumped it with genuinely unsourced claims and found
   nothing either way. **Do not cite Q17 as evidence against it.**
3. **Podcast evidence is vendor-heavy.** Q4 returned mostly hosting-platform blogs and stats
   aggregators. The listening-motivation research `[C]` [s36] is real; the audience-size and
   format-preference numbers are not.
4. **Thought leadership has no literature under that name.** Q11 recovered the source
   credibility tradition instead - McCroskey's 1966 competence and trustworthiness scales, and
   meta-analyses [s85][s92] - which is the real construct underneath. There is no confirmed
   evidence for "thought leadership programmes" as practised.
5. **Per-platform view thresholds are not in the research literature** [s1]. They exist only in
   platform documentation `[P*]`, which is exactly why that tier was added.
6. **Memes have almost no direct evidence.** They are covered obliquely through diffusion
   (Q9) and the meme-shape work [s126]. The craft layer carries them; treat any meme claim as
   `[K]`.

---

# Q1 — Does content marketing actually work?

**Owned social media has a positive but modest effect on sales.** A meta-analysis of brands'
owned social media finds positive effects on both engagement and sales, with the **average
sales effect statistically significant but small relative to the engagement effect** `[C]`
[s6][s18]. This is the honest headline for the whole subject: it works, and it works less
dramatically than it is sold.

**Firm-generated content moves customer behaviour at the individual level.** A customer-level
econometric study links exposure to a retailer's social posts with subsequent purchasing and
cross-buying `[C]` [s72]. Single-firm panel evidence, not a broad meta-estimate.

**Content, sponsorship and influencer effects are separable and have been compared** `[C]`
[s72]. A meta-analysis of influencer effectiveness reports mechanisms and moderators `[C]`
[s73].

**Practical read:** promise direction, not magnitude. There is no defensible ROI multiple, and
the two most-quoted ones are in the kill list.

# Q2 — Video: length, format, retention

**Engagement drops sharply after about six minutes.** In **6.9 million MOOC viewing sessions**,
students watched at most around six minutes regardless of total video length `[C]`. This is the
actual source behind "keep videos short" - an education dataset, not a marketing benchmark, and
it should be attributed that way.

**Production style is not neutral.** Screencast and step-by-step drawing formats outperform
slide decks over the same material; videos including the instructor's face outperform
slides-only and recorded lecture capture; faster pace and evident enthusiasm correlate with
engagement `[C]` [s24][s190]. Showing a face has measured effects on retention and visual
attention `[s190]`.

**Segmenting reduces cognitive load and improves retention** `[C]` [s41], consistent with the
Cognitive Theory of Multimedia Learning `[C]` [s183] and the modality and redundancy principles
`[C]` [s8][s187].

**Practical read:** chunk into sub-six-minute units, show a face, favour demonstration over
slides. Say the evidence is educational, because it is.

# Q3 — Short-form vertical video

**Completion rate is mechanically biased by duration.** Shorter items achieve higher completion
by construction while longer items accumulate more watch time, and looping distorts both `[C]`
[s31]. Feeds also carry **strong position bias** - what gets watched depends on where it
appeared `[C]` [s31].

**Consequence: raw short-form engagement metrics are not comparable across videos of different
lengths**, let alone across accounts. Bias-aware or counterfactual evaluation is required.

**"85% of video is watched without sound" is not substantiated in this corpus.** The
audio-off pass returned nothing supporting it.

# Q4 — Podcasts

**Listening motivations are researched; audience sizes are not.** Motivations and outcomes of
podcast listening are peer-reviewed `[C]` [s36]. Everything about audience size, video-podcast
preference and format share came back vendor-published `[P]`.

**Practical read:** treat podcast market numbers as directional vendor claims and label them.
The host-listener relationship is the one mechanism with support.

# Q5 — Live and synchronous video

**Real-time interaction changes sustained engagement**, compared against a simulated "virtual
live" condition `[C]` [s10]. **Social presence is positively associated with purchase
intention** across several SEM studies `[C]` [s51][s56][s42][s27].

**But the field is methodologically thin.** A review of live streaming commerce notes
heterogeneity across settings and the dominance of survey and PLS-SEM designs, explicitly
calling for more experiments and longitudinal work `[C]` [s17].

**Webinars specifically have no literature.** What exists is live-commerce research plus the
synchronous-instruction literature. Treat webinar advice as `[K]`.

# Q6 — Visual formats: infographics, carousels, memes

**Graphics beat text for long-term retention** `[C]` [s34], and a **meta-analysis finds
graphics improve reading comprehension** `[C]` [s239]. NN/g summarises the picture-superiority
effect for practitioners `[C]` [s29].

**The mechanism is contested.** Dual coding versus depth-of-processing is an open question, not
settled science. Do not explain *why* visuals work as if it were established.

**Encoding choice is measurable.** Cleveland and McGill's graphical perception work established
that different visual encodings carry different accuracy `[C]` [s240], extended by later work
on task and data distribution `[C]` [s235] and synthesised in "The Science of Visual Data
Communication" `[C]` [s238]. Common visual errors are catalogued `[C]` [s237][s64].

**Accessibility is normative, not optional** - figures and tables have documented
accessibility requirements `[C]` [s62].

# Q7 — Social post engagement

**Emotion and arousal predict sharing; information does not.** Two independent field studies
across video ads, 11 emotions and 60+ ad characteristics found **information-focused content had
a significantly negative effect on sharing**, except in risky contexts; high-arousal positive
emotions such as inspiration and amusement, plus surprise, increased sharing; sadness decreased
it unless paired with hope or rescue `[C]`.

**"Engagement" is not one thing.** A systematic review finds it is operationalised
heterogeneously across studies - likes, comments, shares, clickthrough, dwell - which makes
cross-study effect sizes largely incomparable `[C]` [s1]. This is why the vendor benchmark
tables disagree with each other.

**Vividness and interactivity correlate with engagement, but findings are mixed** across
platforms and metrics `[C]`.

# Q8 — Newsletters as an owned channel

**Apple Mail Privacy Protection broke the open rate.** MPP preloads remote images through
Apple's proxy, registering an "open" the recipient never performed, and obscures IP, location
and open time `[P]`. Both the mechanism and its direction are agreed; **no peer-reviewed
quantification of the inflation exists in this corpus**, and the widely repeated "15-20%" is a
practitioner opinion post.

**Practical read:** pre-2021 and post-2021 open rates are not comparable, and neither are two
lists with different Apple Mail shares. Optimise on clicks and downstream action.

# Q9 — Diffusion, cascades and virality

**Structural virality is distinct from popularity.** Goel et al. define it via average pairwise
distance in the diffusion tree, separating deep multi-step spread from shallow broadcast; large
cascades arise either way `[C]` [s13].

**Most reported diffusion differences are size artefacts.** A PNAS study shows that apparent
structural differences between content types or platforms often reflect **differences in cascade
size**, and that after matching on size those differences diminish or reverse `[C]` [s14][s16].

**Practical read:** this is the single most useful finding in the corpus for resisting
"our competitor's content is more viral" claims. Ask what the cascade sizes were first.

# Q10 — User-generated and creator content

**Non-sponsored UGC outperforms sponsored, mediated by perceived authenticity** - but the
strongest statement of this in the corpus is an MSc thesis, so treat the mediation claim as
weak. Peer-reviewed work does find **UGC increases purchase intention among young adults** `[C]`
and that credibility and authenticity are the central variables `[C]` [s22][s39][s83].

**Disclosure matters and is measurable.** Advertising disclosure and source credibility jointly
affect consumer responses to influencer endorsements `[C]` [s84]; self-disclosure and message
sidedness affect sponsored-content outcomes `[C]` [s79].

**Both UGC and firm-created content can drive brand outcomes** - they are not substitutes `[C]`
[s76].

# Q11 — Credibility and expertise (the real construct under "thought leadership")

**Source credibility has a 60-year measurement tradition.** McCroskey's 1966 scales measured
**competence and trustworthiness**; measures have been reviewed across 1951-2018 `[C]` [s93].

**Meta-analytic support exists.** Factors associated with information credibility perceptions
have been meta-analysed `[C]` [s85], as has perceived source credibility and advertising
persuasiveness with its moderators `[C]` [s92]. Source credibility effects depend on whether
prior attitudes exist `[C]` [s40].

**There is no confirmed evidence for "thought leadership" as a programme.** The construct
that has evidence is credibility, and it is built from demonstrated competence and
trustworthiness rather than from publishing volume.

# Q12 — Publishing frequency and scheduling

**There is no universal optimal frequency, and the formal work says so.** Vakratsas and Naik
model scheduling as depending on carryover, diminishing returns and constraints: **pulsing,
flighting or continuity can each be optimal depending on response dynamics** `[C]`. No fixed
exposure number is prescribed.

**Effective frequency has been meta-analysed** `[C]` [s99], and **carryover effects across
marketing communication** likewise `[C]` [s108]. Scheduling content on social media
specifically has theory-and-evidence treatment `[C]` [s102].

**Recency planning versus effective frequency is a genuine, unresolved disagreement.** Report
both.

**Practical read:** answer "how often should we post" with capacity first. The literature
supports "it depends on carryover and response curvature", which is not a number.

# Q13 — Seeding, distribution and amplification

**The literature openly conflicts on who to seed.** A Journal of Marketing review states plainly:
**"Four studies recommend seeding hubs, three recommend fringes, and one recommends bridges"**
`[C]`.

**The best direct empirical comparison favours hubs and bridges.** Two field experiments plus a
live campaign compared four seeding strategies; **high-degree (hubs) and high-betweenness
(bridges) performed best** `[C]` [s11][s15][s110]. Message and network factors both contribute
`[C]` [s112], and seeding interacts with the rest of the marketing mix `[C]` [s113].

**Paid advertising can generate earned impressions** `[C]` [s111] - relevant to any
owned/earned/paid plan, and one of the few places that framework has support.

# Q14 — Decay, evergreen and refresh

**Attention decays as novelty decays.** Wu and Huberman, across roughly a million users, model
attention propagating then fading under an explicit time-decreasing novelty factor `[C]`
[s20][s21][s26][s54]. **Collective memory and attention decay follows a universal form** `[C]`
[s126].

**Decay profiles differ by mechanism.** Yang and Leskovec identify recurrent temporal shapes -
sharp exogenously-triggered bursts that decay fast, slower endogenous rises, and multi-peak
patterns - linking mechanism to decay rate `[C]`.

**Attention windows are shortening over time** `[C]` [s126].

**What the corpus does NOT establish:** that refreshing a document restores its audience. The
novelty model implies it should, and **no study in this corpus tests the tactic.** Say so.

**Practical read:** search-driven evergreen and feed-driven trending have genuinely different
decay curves, which is the defensible basis for a ratio. Do not quote a "content half-life"
number - that is a vendor coinage.

# Q15 — Measuring content: incrementality and attribution

**Observational data cannot establish incremental effect.** A peer-reviewed overview of digital
advertising markets documents pervasive attribution bias `[C]`, and research finds models
relying only on observational data cannot reliably estimate incremental impact `[C]` [s28].

**The size of the error is the point.** A study of nearly **2,000 representative Meta
campaigns** found sophisticated observational models produced **large errors against
experimental ground truth** `[C]` [s28].

**Multi-touch attribution is not a causal tool** `[C]` [s28]. Attribution assigns credit among
observed touchpoints; incrementality asks what happened *because* the marketing ran. They are
different questions.

**Practical read:** this is why `content-strategy` never promises a percentage lift, and why
the measurement section states what it cannot measure. Engagement metrics and financial
performance have been related directly in at least one study `[C]` [s169], but the general case
remains unresolved.

# Q16 — AI-generated content

**Detection works, unreliably and temporarily.** Linguistic features distinguish AI from human
text on benchmark corpora, but performance degrades under editing, domain shift and model
updates `[C]` [s25][s30][s158]. Hybrid approaches are proposed to mitigate this `[C]` [s45].
**Humans are not reliably better than machines at the task** `[C]` [s162].

**Quality perception is measurable and mixed.** Multi-country experimental evidence compares
quality and perceptions of AI versus human output `[C]` [s157]; emotional valence and appeals
differ between AI and human writing `[C]` [s165].

**Disclosure changes reception.** Non-disclosure interacts with audience cognitive
dispositions `[C]` [s160], and disclaimers shape perception `[C]` [s156].

**Provenance needs layers, not a mechanism.** NIST concludes cryptographic provenance,
metadata, watermarking and classifiers must be combined, each having distinct failure modes -
metadata stripping, adversarial edits, paraphrasing, recompression `[C]`. Watermarking carries
regulatory implications under the EU AI Act `[C]` [s60].

**Practical read:** do not promise a client that AI content is undetectable, and do not promise
that detection is reliable either. Both are false.

# Q17 — Folklore: what has no traceable source

Eight claims were traced. **None has a traceable primary source within this corpus.** The pass
returned mostly statistics round-ups, so read this as *the trail runs cold*, not as *proven
fabricated*.

| Claim | Status in this corpus |
|---|---|
| Buyers are 57% (or 70%) through the journey before contacting sales | No primary source, no disclosed method, no replication. **The figure itself shifts between retellings, which is the tell** |
| Content marketing costs 62% less and generates 3x the leads | No primary source. One round-up asserts "3x more leads" while remaining a compiled list |
| The 80/20 and 4-1-1 educational-to-promotional ratios | Presented as rules of thumb, never as empirical claims |
| Video generates 1,200% more shares than text and images combined | No primary source, no methodological detail anywhere |
| 85% of video is watched without sound | Not traceable. The short-form pass separately failed to substantiate audio-off rates |
| A buyer needs seven touches | Framed historically as a rule of thumb |
| One video repurposes into 30 pieces | Workflow framing, never an empirical statistic |
| The 95-5 rule | **Not found either way.** It is genuinely real (LinkedIn B2B Institute / Ehrenberg-Bass) and simply absent here. Do not cite this row against it |

# Q18 — What the metrics actually mean

**There is no single engagement-rate formula.** Practice divides engagements by followers,
reach, impressions or views - and **different denominators yield different results**, so the
formula must always be stated `[C]` [s1].

**Reach and impressions are distinct**: reach is unique accounts exposed, impressions are total
displays.

**"Engagements" has no canonical component list.** Likes, comments, shares and saves are usual;
clicks are sometimes included, varying by platform and source.

**Per-platform view thresholds are absent from the research literature** `[C]` [s1]. They exist
only in platform documentation: YouTube's own view-metric page `[P*]` [s426][s427], its
formatting specifications `[P*]` [s428], Instagram's content-publishing and media requirements
`[P*]` [s429][s430][s432][s433], TikTok's posting API `[P*]` [s431], and LinkedIn's video
specifications `[P*]` [s434].

**Podcast download definitions are not in this corpus at all.** The IAB measurement guidelines
were not retrieved.

**Practical read: cross-platform view comparison is not interpretable.** Give the definitions
from `[P*]` with their retrieval date, and refuse the ratio.

---

# Q19-Q28 — The craft layer

Ten passes in practitioner register covering written and gated assets, case studies,
newsletters, long-form video, short-form video, podcast production, webinars, visual formats,
social text, and platform specifications. **16 YouTube sources** and the practitioner canon
came in here, against copywriting's 2.

These populate `format-specs/` and are tagged `[K]`. **They may inform structure, technique and
per-platform convention. They may never support a factual claim, and factcheck mode does not
read them.** Where a craft source and a confirmed source disagree about what works, the
confirmed source wins and the craft source is reported as convention.

The craft passes generated their own folklore immediately, as copywriting's did. Anything
numeric that appeared only in the craft layer is in `what-not-to-do.md`, not here.

Q28 specifically retrieved the platform documentation now tiered `[P*]`, which is the only
reason this corpus can answer a specifications question at all.

**Q29-Q30, added 2026-08-31.** Q27 and Q26's own craft sources (10 each) turned out to be
generic scheduling-tool blog listicles with zero named practitioners - the exact anti-pattern
this tier exists to avoid, discovered when a generated LinkedIn post came back as dense
paragraphs with no real technique behind the claim. The retrieval trap was the same one
copywriting's q27 already documented: querying "best practices"/"conventions" phrasing surfaces
SaaS marketing blogs, not the creators who actually do the work. Q29 (LinkedIn/X/Threads) and
Q30 (carousels) queried named creators directly instead (Justin Welsh, Dan Koe, Sahil Bloom,
Jay Clouse and others), which is what now backs `social-text.md` and `visual.md`'s structure
claims. A second issue surfaced during this refresh, not query phrasing: Exa returns no
relevance score for this search mode, so `fuse.py`'s score-based tie-break silently sank every
Exa-only result (all of q29/q30's best finds) below Tavily-sourced results scoring 0.5+
regardless of actual quality - a gap in the shared `research` skill's cross-engine scoring, not
specific to this corpus. Twelve sources hand-verified as genuinely on-target are pinned in
`gather.py`'s `PINNED_CRAFT_URLS` rather than left to that tie-break.

---

## Live Query Additions

*Nothing yet. When the corpus is silent, follow `notebook-live-query.md`, then append the
cited finding here with its date and tier so it is reusable.*

# Copywriting — research synthesis

The cited master document. Everything the hub and `copy-conversion` assert traces back here.

**Corpus:** 422 sources, **211 confirmed / 66 craft / 145 practitioner**, built 2026-08-15
from 29 deep research passes. Audit trail in `_research/sources.json`; `[sN]` resolves to
`sources[N-1]`.

**How to read the tags. Three tiers, and the third one is a quarantine.**

| Tag | Tier | May be used for | May NOT be used for |
|---|---|---|---|
| `[C]` | confirmed | Supporting a factual claim | - |
| `[P]` | practitioner | A labelled, attributed number | Being stated as measured fact |
| `[K]` | craft | **Technique, worked examples, format conventions** | **Supporting any factual claim. Factcheck mode does not read this tier at all** |

The craft tier exists because the first version of this corpus contained **2 craft sources out
of 314**. The cause was a bad transplant: `branding-advisor`'s junk list rightly excluded
Dribbble and Behance, because a logo portfolio is an image with no claim in it, and that rule
was carried over to swipe files and YouTube. For copywriting it is backwards - a teardown of a
page that shipped is exactly the practitioner evidence, and per-platform format conventions
live nowhere else. Passes q21-q29 were added in practitioner register to fix it.

Craft tier is assigned **by provenance, not by domain**: a source found only by the craft
passes is craft whatever its domain, because a domain allowlist caught 11 sources out of 154.
Confirmed still wins, so a peer-reviewed paper surfacing in a craft pass stays evidence. The
rule errs safe: a few real papers sit in craft, which only costs us the right to cite them.

**The two judgment calls in the tier list**, both stated in `_research/gather.py`:
`nngroup.com` is confirmed because it runs and publishes original eye-tracking studies; every
email/CRM/landing-page SaaS benchmark report is practitioner regardless of sample size,
because it measures its own customers with an interest in the result.

**Three honest weaknesses in this corpus**, stated up front rather than discovered later:

1. **Email is the thin section.** q4 returned 0 confirmed against 10 practitioner and the
   remedial q17 recovered only 1. The academic email literature exists but did not retrieve;
   almost everything this corpus holds on email is vendor-published. Treat every email
   benchmark accordingly.
2. **Platform format limits have no confirmed source** (q15, 0 confirmed). This is expected -
   character limits are vendor-documented by nature - and it is why `copy-conversion` requires
   verification against platform documentation at time of writing rather than quoting a
   remembered number.
3. **Baymard Institute returned nothing** despite being whitelisted, so checkout and form
   evidence here rests on `[s87]` and the NN/g set rather than Baymard's larger body.

---

## Q1 — Headlines: what actually predicts a click

**Simpler headlines beat complex ones, at scale.** Over 30,000 field experiments with The
Washington Post and Upworthy found readers prefer simpler headlines - more common words,
more readable writing - and a follow-up mechanism experiment showed readers paid more
attention to and processed more deeply the simpler versions `[C]` [s76]. This is the single
best-evidenced headline finding in the corpus and it runs directly against the instinct to
sound sophisticated.

**Negativity increases consumption, in news.** A series of randomized controlled trials
(N = 22,743) on viral news stories found a causal effect of negative words on news
consumption `[C]` [s71][s73], published in Nature Human Behaviour. **The domain caveat is
load-bearing:** this is news headline clickthrough, not B2B purchase behaviour, and nothing
in this corpus extends it to a landing page for a considered purchase. Do not sell a client
negativity on the strength of a news-media finding.

**Positive-emotion words do not measurably hurt.** Across thousands of online field
experiments, the hypothesis that positive-emotion words are negatively associated with
headline success found no support (β = -0.04, p = 0.07) `[C]` [s6][s69].

**Concreteness is curvilinear, not monotonic.** A meta-analysis of 8,977 headline experiments
found the effect of concreteness depends on the baseline: when headlines are too vague, more
concreteness raises clickthrough; when they are already too concrete, more concreteness
lowers it `[C]` [s74]. There is an optimum, not a direction.

**Curiosity gaps can backfire.** Lab and field experiments comparing curiosity-gap headlines
against summary headlines do not support the publisher belief that vagueness reliably wins
`[C]` [s5][s70].

**Practical read:** clarity first, specificity tuned rather than maximised, curiosity as a
tested option rather than a default.

---

## Q2 — CTAs and button copy

**Repeating the headline verbatim on the button raised clickthrough** in a field study of 956
platform visitors, explained through processing fluency `[C]` [s2]. This is the most directly
actionable CTA finding in the corpus and almost nobody does it.

**Verbs and concrete language characterise mobilising text.** Across three studies (Study 1
N = 728), texts written to mobilise others contained more verbs and more concrete words than
texts written to express a view `[C]` [s83].

**Users prefer CTAs that are explainable and intuitive** - high transparency about what
happens next `[C]` [s80]. Wording changes at the CTA can shift outcomes substantially `[C]`
[s79], and prosocial CTA framing was tested in two field experiments in a referral context
`[C]` [s78].

**A null result worth carrying:** an experiment on charity donation-button *design* found no
significant effects on rated transactional trust `[C]` [s81]. Not every button variable moves
anything.

**"Submit" is contested on grounds of user vocabulary, not data** `[P]` [s247] - the linked
discussion is practitioners disputing whether any research supports it. Treat it as a
reasonable heuristic, not a finding.

### The $300M button

The corpus contains the original account from the consultant's own site `[P]` [s208], plus
retellings `[P]` [s198][s199][s213]. What the primary account describes is **usability
testing** that identified registration friction; a 45% conversion increase and the ~$300M
annualised figure appear in a retelling `[P]` [s198].

**The honest answer:** it is a real consulting engagement, not a fabrication - but it is a
single uncontrolled case with no published methodology, no baseline data and no independent
replication, and the dollar figure is an annualised estimate. It is an illustration of
removing friction, never evidence of an effect size. **There is no confirmed-tier source for
it in this corpus.**

---

## Q3 — Landing pages and page structure

**More content correlates with fewer conversions.** An empirical study of commercial landing
pages found a negative correlation between content volume and conversion `[C]` [s1][s86]. An
analysis of 25,027 landing pages examined which elements are present and how they relate to
conversion `[C]` [s85].

**But the relationship is an inverted U, not a line.** Manipulating the number of attributes
across three website versions produced evidence of an inverted-U relationship between amount
of information and information processing `[C]` [s88], and a study varying information volume
across three landing pages per product found an amount that maximises interest `[C]` [s89].
Too little information is a failure mode as real as too much.

**Forms:** a controlled lab study evaluated 20 published web-form optimisation guidelines
`[C]` [s87]. Navigation depth had the greatest influence on usability and efficiency in an
eHealth design study `[C]` [s91].

---

## Q4 / Q17 — Email

**This is the weakest section in the corpus and the skill says so.** Zero confirmed sources in
q4 [s142]-[s151], one in the remedial q17. Everything below is `[P]` unless marked.

The claim that personalised subject lines lift open rates by a specific percentage traces to
vendor sources here `[P]` [s142][s144][s148]. Two academic-adjacent sources report real
research on subject-line personalisation - a Chicago Booth Review write-up `[P]` [s145] and a
Stanford GSB working paper on personalisation in email marketing `[P]` [s147] - but the
published journal versions did not retrieve, so **no specific personalisation lift figure in
this corpus is confirmed-tier.**

**Never quote an email benchmark to a client as measured fact.** Vendor benchmarks measure
that vendor's customers, exclude non-users entirely, and are published by a party selling
email software.

### Open rate after Apple Mail Privacy Protection

The corpus did not retrieve a confirmed technical source on MPP. **Flagged as not in sources.**
State the mechanism from the client's own data instead: since 2021 Apple Mail pre-fetches
images for users who enable protection, which registers as an open regardless of whether the
message was read. Any open-rate comparison spanning 2021 is comparing two different
measurements. Do not present a pre-2021 email benchmark as comparable to a current number.

---

## Q5 — Advertising copy

**Saying less can outperform saying more in paid search.** A field experiment run with a
mid-sized B2C furniture retailer via Google across four ad copies produced 280,877
observations `[C]` [s28].

Advertising appeal types have been scaled on a common metric by comparative meta-analysis,
giving relative impact measures for seven appeal types `[C]` [s53], and a systematic review
covers appeal effectiveness more broadly `[C]` [s56].

---

## Q6 — Message framing: the industry's most oversold lever

**This is the most important finding in the corpus for anyone selling copywriting.**

A review of **1,149 studies covering 30 message variations** - narrative vs non-narrative,
gain- vs loss-framed, one- vs two-sided and so on - found that although differences between
message forms are statistically significant, **they do not make much practical difference to
persuasiveness** `[C]` [s107].

The framing literature specifically:

- **Risky-choice framing:** strong and consistent evidence. **Attribute framing:** little but
  mostly positive evidence. **Goal / message framing:** a lack of consistent evidence, despite
  a considerable body of work `[C]` [s11].
- Gain-framed messages **do not** motivate sun protection: meta-analysis k = 33, N = 4,168,
  no significant difference in persuasiveness `[C]` [s111].
- Health message framing meta-analyses find limited support `[C]` [s103][s110][s112]; a
  further meta-analysis (k = 25, N = 5,772) examined the affective dimension `[C]` [s105].
- Effects are moderated by dispositional factors `[C]` [s104] and by construal level and
  mind-set `[C]` [s106][s109].

**What this means in practice:** "reframe it as loss instead of gain" is not a reliable lever.
Choosing between message forms matters far less than whether the underlying offer, proof and
clarity are right. Copy advice that promises large gains from a framing switch is
overselling.

---

## Q7 — Social proof and reviews

**Reviews have measured commercial effect.** A meta-analysis of how online product reviews
affect retail sales reports valence Es = .78 and volume Es = .41, with sales elasticities
significantly greater on third-party websites, greater when critics' opinions are included,
and greater for high-involvement products `[C]` [s114].

Valence and variance interact `[C]` [s117]; the effect of valence intensity is asymmetric
`[C]` [s119]; peer and expert reviews affect evaluations differently and are mediated by
consumer confidence `[C]` [s113]. Consumers are influenced primarily by **information quality**
in reviews, with source credibility having limited effect on diagnosticity `[C]` [s118].

**Suspicion is costly.** Reviews suspected of being fake cause consumers to discount the
reviewer's opinion, and lower opinions of the reviewer directly harm brand and website
attitudes `[C]` [s115]. Consumers use identifiable cues to form that suspicion.

**Practical read:** the third-party-site finding matters more than most agencies act on -
proof hosted where the seller controls it is worth less than proof hosted where they do not.

---

## Q8 — Scarcity, urgency and guarantees

**Scarcity works on average.** A meta-analysis of product scarcity effects finds cues
signalling unavailability generally enhance value and desirability and increase purchase
intentions `[C]` [s13][s123]. Time-limited promotions accelerate purchase `[C]` [s130], and
limited-time messages affect impulse purchase `[C]` [s126].

**And it backfires under identifiable conditions**, which is the part usually omitted:

- Supply-driven limited quantities **can backfire**, reducing perceived retailer sincerity and
  purchase intention; timely availability guarantees and external attribution framing mitigate
  it `[C]` [s121].
- The positive effect of limited-time offers is **attenuated or reversed into a negative
  effect** when consumer flexibility is restricted, driven by psychological reactance `[C]`
  [s125].
- A randomized field experiment compared pressure-based nudges (quantity scarcity, time
  scarcity, social persuasion) against self-assurance nudges on **both purchases and returns**
  `[C]` [s127] - pressure tactics that raise purchases can also raise returns.
- Shortening return deadlines can counterintuitively **increase** return rates `[C]` [s128].

Countdown time units themselves affect participation intentions `[C]` [s124].

**Practical read:** scarcity is real, cheap to fake, and the failure mode is not that it stops
working but that it damages trust and inflates returns. See Q20 for where fake urgency stops
being a tactic and becomes a legal exposure.

---

## Q9 — Fluency, readability and specificity

**Complex vocabulary makes writers look less intelligent, not more.** Experiments manipulating
text complexity found a negative relationship between needless complexity and judged
intelligence `[C]` [s136] - Oppenheimer's "erudite vernacular" paper. This is the strongest
available answer to a client who wants their copy to sound more sophisticated.

**Fluency drives positive judgment, including judgments of truth.** A review of 40 articles
found various instantiations of fluency uniformly produce positive judgments such as liking
and confidence, and predict willingness to undertake a task `[C]` [s131]. The fluency-truth
link traces to Begg et al. (1992) `[C]` [s8], with repetition and perceptual fluency as the
two main routes `[C]` [s137], and the effect can reverse when people learn to reinterpret the
cue `[C]` [s139].

**Concreteness raises interest and comprehension** `[C]` [s134]. Plain-language redrafting of
legal contracts measurably improved comprehension among non-experts `[C]` [s140]. Linguistic
devices interact with processing mode `[C]` [s132]. Readability formulas based on surface
features are criticised as too shallow, with cognitively-based indices proposed instead `[C]`
[s133].

**A caution against overreach:** phrasing effects can be strong in the lab. The "more-credible"
effect - "A is more than B" endorsed more than the identical "B is less than A" - was probed
across 9 experiments, total N = 5,643 `[C]` [s135].

---

## Q10 — Copy length

**No confirmed source in this corpus supports "long copy outsells short copy" as a general
rule.** The direct-response claim has no traceable primary study here.

What the evidence does show:

- A **well-controlled experiment** on direct-mail sales letters found **no significant
  differences in response rates as a function of readability level**, across both professional
  and layperson segments `[C]` [s24]. A null result on a variable the industry treats as
  decisive.
- Landing page content volume correlates **negatively** with conversion `[C]` [s1].
- Paid search: four ad copies, 280,877 observations, "achieving more by saying less" `[C]`
  [s28].
- Crowdfunding: word count against funding success across 70,000+ Kickstarter projects `[C]`
  [s29].
- Longer reviews are **less** helpful when the rate of argumentation change is high, holding
  for both low- and high-involvement products `[C]` [s27].
- Across six studies, the number of words used to express a constant number of thoughts
  influenced subsequent evaluations `[C]` [s30].
- Conclusion explicitness in advertising is moderated by need for cognition `[C]` [s25];
  message-cue effects are moderated by processing capacity `[C]` [s23].

**Practical read:** length should follow how much the reader needs to decide, and the burden
of proof sits with whoever wants it longer. "Long copy sells" is folklore; so is "nobody reads
anything".

---

## Q11 — Customer language and linguistic style matching

**Style matching has measured effects.** Language style matching between a review and its
intended readers directly influences perceived review quality `[C]` [s35], with a main effect
on review helpfulness of F(1, 249) = 44.88, p < 0.001 `[C]` [s37]. Affective content and style
matches influence retail site outcomes `[C]` [s31]; five studies including textual analysis of
1,000+ reviews show how language shapes word-of-mouth impact `[C]` [s40]. LSM measurement
itself has been validated against transcribed encounters using LIWC `[C]` [s32].

**The counterintuitive finding that qualifies all of it:** the **Language Backfire Effect** -
frontline employees switching language to serve customers *decreased* customer satisfaction,
**even when switching into the customer's own language**, explained by perceived identity
threat, and also reducing word-of-mouth and repurchase intentions `[C]` [s36].

**Practical read:** mine customer vocabulary, but mirroring is not automatically safe.
Adopting a customer's language can read as accommodation the customer did not ask for.

**Method:** Voice-of-Customer methodology traces to Griffin and Hauser in Marketing Science
`[K]` [s229]. Practitioner sources converge on review mining, support tickets, NPS verbatims
and interviews as the sources `[P]` [s188][s190][s207], and warn against relying on surveys
alone `[P]` [s217]. NLP is effective for capturing customer voice at scale `[C]` [s33].

---

## Q12 — Benefits versus features

**"Benefits, not features" is a moderated claim, not a law.**

Grounded in construal-level theory, four studies show when marketers should emphasise
attributes versus benefits, depending on whether the purchase is planned for the near or
distant future `[C]` [s41]. Desirability concerns (high-level construal) outweigh feasibility
concerns (low-level) at greater psychological distance `[C]` [s10]. Attribute-based versus
alternative-based information shifts choice between desirability- and feasibility-driven
criteria `[C]` [s45]. Temporal framing effects depend on construal level and need for
cognition `[C]` [s42].

Feature and benefit **sentences** have distinct effects on consumer memory `[C]` [s46].
Whether to claim a single benefit or several is moderated by intergoal association `[C]`
[s43], and abstract-versus-concrete product information effects are conditional `[C]` [s44].

Means-end chain theory (Gutman 1982) and the laddering interview method are the standard
technique for getting from attribute to benefit to value `[P]` [s185][s233][s234].

**Practical read:** near-term, concrete, feasibility-focused purchases can be better served by
attributes - which is why stripping specifications out of a product page in favour of benefit
language sometimes reduces conversion.

---

## Q13 — Emotional appeals

**Fear appeals are genuinely contested and this synthesis preserves the disagreement.**

- A comprehensive meta-analysis finds fear appeals effective for influencing attitudes,
  intentions and behaviours `[C]` [s4][s51].
- A review of sixty years of fear-appeal research concludes that **experimental evidence
  argues against** the use of threatening health information `[C]` [s54], and a critical
  re-analysis with a revised meta-analytic test reports that consensus remains elusive `[C]`
  [s52].

Both positions are held by serious researchers. Anyone who tells a client "fear works" or
"fear backfires" without the qualifier is picking a side the literature has not settled. The
Extended Parallel Process Model (Witte 1992) is the standard framework, distinguishing threat
from efficacy `[C]` [s55][s7].

**Humour reduces the defensive responses high fear provokes**, restoring persuasive effect
across two studies `[C]` [s57].

Affective versus cognitive appeal effectiveness varies with individualism-collectivism `[C]`
[s59]. Valence-based approaches sacrifice explanatory power relative to discrete emotions
`[C]` [s60], and anger elicitation specifically has been meta-analysed `[C]` [s58].

**Not in sources:** the Binet and Field emotional-versus-rational long-term effectiveness
argument did not retrieve. Do not cite its figures from memory.

---

## Q14 — Writing for AI answer engines

**The primary source is the Princeton GEO paper** `[C]` [s62][s195], which formalises
generative engines and tests content modifications. **Use it for direction, never for the
per-method percentages** - the widely circulated 30-40% figure appears here only in
practitioner restatement `[P]` [s171].

Newer confirmed work has moved past it:

- Structural features - not just semantic content - systematically affect GEO outcomes `[C]`
  [s61].
- Exposure has shifted from rank-based to **citation-based**: sources that are not cited
  receive effectively no exposure regardless of retrieval rank `[C]` [s65].
- Citation *selection* and citation *absorption* are different measurements, and citation
  count is a breadth measure that should not be read as influence `[C]` [s64].
- Whether GEO is distinct from SEO or SEO repackaged is an open empirical question, addressed
  by measuring where AI-cited pages sit in Google's rank distribution `[C]` [s63].
- **C-SEO Bench asks directly whether conversational SEO methods work**, and finds methods do
  not transfer across application domains `[P]` [s253]. Treat cross-domain GEO advice
  sceptically. (Tiering note: this is a NeurIPS paper and is peer-reviewed in substance;
  it reads practitioner only because `papers.neurips.cc` is not in the confirmed domain list.
  Weigh it as research.)
- AI-generated content polluting the web degrades retrieval itself - "retrieval collapse"
  `[C]` [s66].

**Practitioner claims to handle carefully:** the 134-167 word self-contained passage unit and
associated correlations `[P]` [s165], AI citation factor rankings `[P]` [s164], and the
16-pillar audit reporting an odds ratio of 4.2 for page quality `[P]` [s175].

**Boundary:** `seo-onpage/references/checks.md` owns the on-page thresholds and `blog-writer`
owns article structure. This corpus does not restate their numbers.

---

## Q15 — Platform format constraints

**Zero confirmed sources.** All platform limits here are third-party blogs `[P]`
[s153][s155][s157][s158][s160][s161], not platform documentation.

**Therefore:** never quote a character limit from this corpus or from memory. Verify against
the platform's own documentation at time of writing and record the date. Truncation point -
what a reader sees before the "more" link on their device - matters more than the field limit
and is the thing that actually changes.

---

## Q16 — The eight-second attention span

**The claim is fabricated.** No primary study supports it `[P]` [s154], and the BBC traced the
"down from 12 seconds in 2000 to 8 seconds now, less than a goldfish" formulation and found
no supporting source `[P]` [s159]. It is widely believed: 50% of the UK public accept it
`[P]` [s152].

**What is real, and what it actually measures:** attention spans **on screens** have shrunk in
measurable ways over the past two decades, per Gloria Mark's research `[C]` [s3]. That work
measures how long someone stays on one screen before switching - a different construct from a
biological attention span, and not eight seconds.

**How to answer a client:** the goldfish statistic is not real; the underlying concern is.
People switch attention on screens faster than they used to, which is an argument for getting
to the point, not evidence of an eight-second cliff.

---

## Q18 — Why reported conversion wins evaporate

**Only about 30% of tested ideas improve metrics** in mature experimentation programs `[P]`
[s307], reported from Kohavi's work. The confirmed literature behind it:

- Trustworthy online controlled experiments `[C]` [s269][s272][s273], including at large scale
  `[C]` [s273].
- Twelve common metric interpretation pitfalls `[C]` [s270] and challenges in evaluating
  results `[C]` [s267].
- Sample-size estimation is under-studied relative to its importance for power and type-I
  error control `[C]` [s268].
- Optional stopping is a known failure mode; sequential testing methods exist precisely
  because stopping when a result looks good invalidates it `[C]` [s271].
- Practical guidance puts the number of users needed **at least in the thousands** `[P]`
  [s302], with minimum detectable effect as the governing quantity `[P]` [s305].

**Practical read for an agency:** most SMB clients cannot run a conclusive copy test. Stopping
a test when it looks like a win selects for noise, which is the mechanism behind wins that do
not persist. Recommend copy changes on the argument for them and be honest that attribution
will be directional.

---

## Q20 — Where copy stops being style and becomes law

US law, primary sources.

- **16 CFR Part 255**, the FTC Guides Concerning the Use of Endorsements and Testimonials in
  Advertising, are administrative interpretations of Section 5 of the FTC Act (15 U.S.C. 45)
  `[C]` [s263][s265][s260].
- **Substantiation:** an advertiser must possess and rely upon adequate substantiation -
  including competent and reliable scientific evidence where appropriate - for claims made
  *through endorsements*, to the same standard as claims made directly `[P]` [s301], with the
  FTC's Advertising Substantiation policy statement as the primary text `[C]` [s264].
- **Material connections** between advertiser and endorser must be fully disclosed `[C]`
  [s283].
- **The Rule on the Use of Consumer Reviews and Testimonials** prohibits identified unfair or
  deceptive review practices, and the FTC enforces against fake and misleading reviews `[P]`
  [s311][s313][s314].
- **Implied claims count.** The FTC assesses deception from the advertisement as a whole, not
  only its literal statements `[C]` [s288][s285].

Disclosure changes consumer response: disclosure of material connections affects credibility
`[C]` [s284], disclosure message type affects trust and attitudes `[C]` [s289], and disclosure
regulation has measurable market effects `[C]` [s287]. Endorser liability is real `[C]`
[s290][s116]. Fake reviews are regulated across US, UK and EU regimes `[C]` [s286].

**Not in sources:** no confirmed source on countdown-timer or dark-pattern rules specifically
retrieved. The general deception principle in [s288] applies - a timer that resets is a
representation the advertiser cannot substantiate - but do not cite a specific rule we have
not read.

**This is not legal advice and the skill must say so.** It is a flag to raise with the client
and their counsel, not a compliance opinion.

---

## Q21-Q29 — The craft layer `[K]`

**Read the tier tag before using anything here.** Nothing in this section may support a
factual claim. It is technique, worked examples and format conventions.

### What the craft passes actually contain

- **Headline and hook swipe files** — 47 opening lines [s401], 35 headline formulas [s403],
  21 headline examples [s410], VeryGoodCopy's 207 micro-lessons [s411], and a Copyhackers
  headline/button case [s406]. Practitioner consensus is that the hook carries
  disproportionate weight, with no effect sizes attached.
- **Microcopy** — action-oriented button labels, error messages, empty states, with example
  galleries [s387][s390][s393][s398][s404][s407].
- **Ad copy by platform** — responsive search ads [s385], Meta primary text vs headline vs
  description [s392][s391][s405], LinkedIn B2B [s395], Google B2B [s396][s399].
- **Product and ecommerce** — product page and listing copy [s380][s381][s383][s394][s397]
  [s402][s408].
- **Landing pages** — step-by-step and teardown material [s382][s388][s389][s400][s412].

### Platform character limits — use the primary source

Pass q27 **failed** and is a documented example of the retrieval trap: asking for "platform
copy formatting conventions" returned LinkedIn profiles of *people* who do that work, exactly
as `branding-advisor`'s q13 returned profiles of personal-branding consultants. The remedial
q29 fixed it by querying the vocabulary that appears **on** a spec sheet rather than the
vocabulary describing the job.

The useful outcome: **Google's own responsive-search-ad documentation** [s418], plus
character-limit references [s419][s420].

**The standing rule does not change.** Quote a limit only from the platform's own current
documentation, and record the date you checked. `[K]` and `[P]` cheat sheets go stale
silently, and truncation point on the reader's device matters more than the field maximum.

### New folklore the craft passes surfaced

The craft tier immediately produced fresh unsourced claims, which is a good argument for
keeping it quarantined:

| Claim | Status |
|---|---|
| "You have about 2 seconds before someone scrolls past" | `[K]` [s401]-adjacent. **No primary citation.** Same shape as the 8-second myth |
| "78% of marketing agencies now use generative AI" | Repeated across sources, attributed to Statista, **primary table never linked** `[K]`. Treat as unverified secondary |
| "Microcopy is the 3-5 most-read words on your interface" | `[K]`. Vendor assertion, no measurement |

None of these may be used with a client as fact. They belong in the same bucket as the
claims in `what-not-to-do.md`.

---

## The refusal list

Claims to reject, with what to say instead. `what-not-to-do.md` carries the short version.

| Claim | Status | Say instead |
|---|---|---|
| "You have 8 seconds" | Fabricated `[P]` [s154][s159] | Screen attention has measurably shortened `[C]` [s3]; get to the point |
| "Nobody reads below the fold" | False as stated. Above the fold takes 57% of viewing time, the second screenful 17%, the rest 26% `[C]` [s259] | People scroll; attention is front-loaded |
| "The $300M button proves X" | Uncontrolled single case, consultant-reported `[P]` [s208][s198] | Useful illustration of friction, not an effect size |
| "Personalised subject lines lift opens 26%" | No confirmed source `[P]` [s142][s144] | The email evidence here is vendor-published; measure your own |
| "Long copy outsells short copy" | No confirmed support; a controlled direct-mail test found no readability effect `[C]` [s24], and content volume correlates negatively with landing page conversion `[C]` [s1] | Length follows what the reader needs to decide |
| "Red buttons convert better" | Not supported. A donation-button design experiment found no significant effect on trust `[C]` [s81] | Contrast and clarity of what happens next |
| "Switch to loss framing for a big lift" | Goal/message framing lacks consistent evidence `[C]` [s11]; across 1,149 studies message form makes little practical difference `[C]` [s107] | Fix the offer, proof and clarity first |
| "Always benefits, never features" | Moderated by construal level and purchase timing `[C]` [s41][s45] | Depends on how near and concrete the decision is |
| "Mirror your customer's language" | Supported `[C]` [s35][s37] but can backfire via identity threat `[C]` [s36] | Mine their vocabulary; do not perform it |
| "Fear appeals work" / "fear backfires" | Genuinely contested `[C]` [s4][s51] vs `[C]` [s54][s52] | State the disagreement and the EPPM conditions `[C]` [s55] |
| "This change will lift conversion X%" | Unknowable in advance; ~30% of tested ideas improve metrics at all `[P]` [s307] | Argue the change; do not promise a number |
| Any specific platform character limit | No confirmed source `[P]` [s153]-[s161] | Verify against platform docs and date it |

---

## Live query fallback

When a question is not answered here, do not guess. Follow `notebook-live-query.md`: run a
fresh research pass, cite what comes back, and append it to this document under a **Live Query
Additions** heading so the next person inherits it.

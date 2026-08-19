# Platform copy format constraints and conventions in 2026: documented character limits and truncation points for Google Ads Meta Ads LinkedIn and email subject lines, mobile versus desktop truncation, evidence on optimal length per platform from large-scale analyses, accessibility requirements for link text and alt text and plain language, and how platform algorithm changes have altered what copy formats get distribution. Give specific numbers, named frameworks, effect sizes and concrete steps, and cite sources. Distinguish peer-reviewed evidence from agency or vendor opinion. Where a widely repeated statistic has no traceable primary source, say so explicitly. Where the sources disagree, preserve the disagreement rather than picking a side.

*mode: scientific | depth: deep | 2026-08-15*

---

## Answer

Google Ads enforces strict character limits: 30 for headlines, 90 for descriptions. Meta ads recommend 125 for primary text, 40 for headlines. LinkedIn and email subject lines have no strict limits but should be concise for optimal engagement.

## Summary
- The provided sources document hard character limits for Google Ads (e.g., 30-character responsive search ad headlines; 90-character descriptions) and placement-specific recommendations for Meta Ads (e.g., 125-character primary text recommendation; 40-character headline limit with a 27-character headline recommendation for Facebook Feed). They also provide LinkedIn truncation points (~140 characters on mobile; ~210 on desktop) and engagement-optimal post lengths (1,301–2,500 characters), and email subject line guidance (30–50 characters) [1][2][4][7][8].
- Only LinkedIn [7] reports effect-size-like outcomes (median engagement rates by length band). Other sources offer limits and recommendations but not causal, peer-reviewed evidence.
- The sources do not cover accessibility requirements (link text, alt text, plain language) or definitive evidence on how algorithm changes alter distribution beyond product-level length changes (e.g., TikTok captions expansion; X length tied to paid plans) [6]. Where such topics are requested, there is insufficient evidence in the provided materials.
- Practical steps supported by these sources include writing LinkedIn hooks to fit within ~140 characters for mobile, keeping Facebook Feed headlines at or under 27 characters, and targeting 30–50 characters for email subject lines [2][7][8].

## Key Findings
- Google Ads hard limits and enforcement [1][4]
  - Responsive Search Ads (RSA): headline 30 characters; description 90 characters; display path segments 15 characters each [4].
  - Sitelinks: link text 25 characters; each optional description line 35 characters [4].
  - Spaces and punctuation count toward limits [4].
  - Enforcement occurs at save time (ads cannot be saved if limits are exceeded) [1].
  - Concrete step: Draft RSA headlines ≤30 and descriptions ≤90; keep display paths ≤15 per segment; plan sitelinks with ≤25-character titles and ≤35-character descriptions [4].

- Meta Ads limits and placement-specific recommendations [2]
  - Primary text: 125 characters recommended [2].
  - Headline: 40-character limit; however, Facebook Feed recommends 27-character headlines (indicating earlier truncation in that placement) [2].
  - Description: 25 characters [2].
  - Concrete step: For Facebook Feed, keep headlines ≤27 characters to avoid truncation; keep primary text near 125 characters and descriptions ≤25 for broad placement compatibility [2].
  - Note on disagreement/complementarity: The 40-character headline limit vs 27-character Facebook Feed recommendation reflects a difference between hard limits and placement-specific truncation guidance rather than a contradictory limit [2].

- LinkedIn truncation points and engagement-optimal lengths [7]
  - Mobile truncation at approximately 140 characters; desktop truncation around ~210 characters [7].
  - “First 140 characters do most of the work” (practical implication for the hook) [7].
  - Posts 1,301–2,500 characters achieve the highest median engagement rate (2.61–2.67%), compared with 2.10% for posts under 400 characters [7].
  - Concrete steps: Put the hook and key value proposition within ~140 characters so it survives mobile truncation; consider post bodies in the 1,301–2,500 character range if optimizing for median engagement, per [7].

- Email subject line length guidance and truncation risk on mobile [8]
  - Recommended “ideal” subject line length: 30–50 characters (roughly 7–9 words) to remain visible on mobile and preserve clarity [8].
  - Engagement claim is directional: when the key part of the message is visible, opens increase; when hidden behind an ellipsis, interest drops. No numeric effect size is specified in the source [8].
  - Concrete steps: Aim for 30–50 characters and frontload the most important words to avoid mobile ellipsis truncation [8].
  - Evidence caveat: The source emphasizes there is no universal magic number; testing is advised [8].

- Cross-platform length changes relevant to distribution constraints (product-level) [6]
  - TikTok increased caption length from 2,200 to 4,000 characters, expanding possible copy length [6].
  - X (formerly Twitter) tied longer post length to a paid feature, changing who can publish long-form copy [6].
  - Concrete implication: Platform product changes alter available character budgets over time; teams should re-check limits before campaigns [6].
  - Algorithm-change caveat: These are product/feature changes; no causal evidence in the provided sources links length changes to algorithmic distribution preferences.

- Google Ads truncation examples exist but no pixel-width specifics are provided here [5]
  - The guide provides truncation examples and a live counter; however, no numeric truncation pixels or device-specific cutoffs beyond the hard limits are given in the provided excerpt [5].
  - Practical step: Use a counter/validator to preview potential truncation and stay within published limits [5].

## Evidence Quality
- Study types in the provided materials:
  - Tool/spec sheets and vendor/agency blog posts summarizing platform limits or offering recommendations [1][2][4][5][6][8].
  - A data-backed blog analysis for LinkedIn with reported median engagement rates by length band [7].
- Peer-reviewed evidence:
  - None of the provided sources are peer-reviewed academic studies. All evidence here should be considered practitioner/vendor guidance or platform-spec documentation proxies.
- Effect sizes:
  - Only [7] provides explicit comparative engagement rates (2.61–2.67% vs 2.10%) for LinkedIn post-length bands. Other sources provide recommendations without quantified effect sizes [2][8].
- Areas with insufficient or no coverage in the provided sources:
  - Accessibility requirements (e.g., link text best practices, alt text standards, plain language guidelines) are not documented in these sources. No named accessibility frameworks are cited in the provided materials.
  - Causal claims about how algorithm changes alter distribution by copy format are not evidenced here; only product-level changes to character allotments are mentioned [6].

- Widely repeated statistics without traceable primary sources in this set:
  - “Ideal” email subject line lengths are given as 30–50 characters [8], but the source provides no primary, peer-reviewed dataset or quantified effect size; it also notes there is no universal number [8].
  - Meta “125-character primary text” appears as a recommendation rather than a hard limit and is placement-dependent in practice [2]. No primary platform paper or peer-reviewed evidence is provided in these materials.

## Open Questions
- Accessibility
  - What are the authoritative accessibility requirements for ad and social copy (e.g., link text clarity, alt text expectations, plain language standards) and their measured impact on engagement or reach? Not covered by the provided sources.
- Truncation specifics beyond counts
  - What are the pixel-based truncation thresholds for Google Ads headlines/descriptions across devices and languages, and for email subject lines across major clients? The provided sources do not supply pixel-width or client-by-client truncation data.
- Algorithm and distribution
  - Do platform algorithms explicitly favor certain copy lengths or formats beyond mechanical truncation and product constraints? The provided sources do not establish causal links between algorithm changes and distribution outcomes.
- Meta placement-by-placement detail
  - Beyond the 27-character Facebook Feed headline recommendation, what are the precise truncation points across other Meta placements? The provided materials do not provide a full placement matrix.
- Generalizability and sample sizes
  - For LinkedIn engagement-by-length findings, what is the sample size, time frame, and methodology? Only summary outcomes are provided in [7]; without methods, generalizability remains uncertain.
- Email subject lines
  - What are quantified effect sizes for different subject line lengths across industries and inbox providers? The provided materials offer directional guidance but no cross-provider effect-size estimates.

## Sources
[1] Google Ads Character Limits (2026) — Full Spec Sheet — https://adplus.com/tools/ad-specs-validator/google-ads-character-limits  
[2] Meta Ad Copy Specs: Every Character Limit for 2026 — https://adsuploader.com/blog/meta-ad-copy-specs  
[3] Google Ads character limits 2026 | ClickPatrol™ — https://clickpatrol.com/google-ads-character-limits-2026-guide-headlines  
[4] Google Ads character limits 2026: table + free checker — https://kunidadesigns.com/blog/google-ads-character-limits-guide  
[5] Google Ads Character Limits 2026: The Complete Cheat Sheet | AdsPreview.us — https://adspreview.us/guides/google-ads-character-limits  
[6] Social Media Character Limits 2026: All Platforms, One Table | TypeCount — https://typecount.com/blog/social-media-character-limits  
[7] LinkedIn Character Limits 2026: All Limits + Best Post Length Data — https://authoredup.com/blog/linkedin-character-limit  
[8] The Best Email Subject Line Length in 2026 (Backed by Data) — https://www.mailpro.com/blog/email-subject-line-lenght

## Ranked Sources

1. [Google Ads Character Limits (2026) — Full Spec Sheet](https://adplus.com/tools/ad-specs-validator/google-ads-character-limits) — `tavily`
   > YouTube (Video action / In-feed):

 Headline: `15 characters` for in-feed video, `100 characters` for the long-form
 Description lines: `2 lines × 35 characters` for in-feed, `70 characters` total for
2. [Meta Ad Copy Specs: Every Character Limit for 2026](https://adsuploader.com/blog/meta-ad-copy-specs) — `tavily`
   > Ads UploaderBlog

Sign in

Ad Specifications

# Meta Ad Copy Specs: Every Character Limit for 2026

By Chris Pollard

April 5, 2026• 16 min read

Meta ad copy specs define character limits for three t
3. [Google Ads character limits 2026 | ClickPatrol™](https://clickpatrol.com/google-ads-character-limits-2026-guide-headlines) — `tavily`
   > Sign in
 Book a Demo
 Start My Free 7-Day Trial

# Google Ads character limits (2026 Guide): Headlines, descriptions & all ad formats

Abisola |

Browser-like panel with alert dots and a navy cursor p
4. [Google Ads character limits: the complete 2026 guide](https://kunidadesigns.com/blog/google-ads-character-limits-guide) — `tavily`
   > Kunida Designs

Get a Free Landing Page Plan

Blog

# Google Ads character limits: the complete 2026 guide

By Kunida Designs · Published April 2, 2026 · Updated April 2, 2026 ·  Back to blog

 Paid M
5. [Google Ads Character Limits 2026: The Complete Cheat Sheet | AdsPreview.us](https://adspreview.us/guides/google-ads-character-limits) — `tavily`
   > Remove articles: a, an, the. “Get the best rates” is 18 characters. “Get best rates” is 14. Ad copy reads fine without articles.

Use ampersands instead of “and”. “Fast & friendly” is 15 characters. “
6. [Social Media Character Limits 2026: All Platforms, One Table | TypeCount](https://typecount.com/blog/social-media-character-limits) — `tavily`
   > So this page does one job: every limit in one table. The bigger platforms get full guides — every field, the truncation points nobody documents, a live counter built in — while the smaller ones are co
7. [LinkedIn Character Limits 2026: All Limits + Best Post Length Data](https://authoredup.com/blog/linkedin-character-limit) — `tavily`
   > Optimal post length: 1,301–2,500 characters. Posts in this range generate the highest median engagement rate (2.61–2.67%), well above the 2.10% seen for posts under 400 characters.
 First 140 characte
8. [The Best Email Subject Line Length in 2026 (Backed by Data)](https://www.mailpro.com/blog/email-subject-line-lenght) — `tavily`
   > Engagement. When the key part of your message is visible, opens go up; when it’s hidden behind an ellipsis, interest drops.

## The Ideal Length in 2026

If you want one simple target that works acros
9. [LinkedIn Ad Specs – Your Guide for 2026 | Veuno on LinkedIn Ads](https://www.veuno.com/linkedin-ad-specs-your-guide-for-2026) — `tavily`
   > Single Image Ads appear on both desktop and mobile; however, vertical images are only on mobile. Did you know that LinkedIn traffic is 80% mobile? Something to consider!

##### LinkedIn Single Image A
10. [TOP 10 EMAIL SUBJECT LINE STATISTICS 2026 THAT EXPOSE SHOCKING OPEN RATE SECRETS](https://www.amraandelma.com/best-email-subject-line-statistics) — `tavily`
   > In 2026, a comprehensive analysis of over 5.2 billion marketing emails conducted by Litmus and HubSpot revealed that subject lines between 61 and 70 characters now achieve an even higher average open 
11. [Do You Want $150 for FREE? Measuring the effect of language on marketing email open rates](https://doi.org/10.1016/j.amper.2026.100271) — `exa`
   > Marketers have made analyses of which words are conducive to successful marketing emails. We propose taking a deeper look into the language to discover which kinds of words and linguistic features cau
12. [Enhancing reach and effectiveness of recruitment through email: a study within a trial (SWAT) | Trials | Springer Nature Link](https://link.springer.com/article/10.1186/s13063-026-09902-1) — `exa`
   > Best practices for efficient and effective email recruitment are unclear. This study within a trial (SWAT) aimed to evaluate the effect of an email’s subject line and a prenotification email, as well 
13. [Linguistic effects on news headline success: Evidence from thousands of online field experiments (Registered Report) | PLOS One](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0281682) — `exa`
   > In this Registered Report, a follow-up to a previously-published Protocol [28] , we conduct an analysis of experimental field data that provides very strict controls as well as a number of other benef
14. [The impact of linguistic features on CTR in Instagram ads: A study of supplement and cosmetic products](https://journals.plos.org/plosone/article/file?id=10.1371%2Fjournal.pone.0338313&type=printable) — `exa`
   > This study analyzes linguistic features impacting click-through rate (CTR) in Jap anese Instagram ads (21,692 ads; July 2021-June 2023, Meta’s Marketing API). CTR was computed as link clicks/impressio
15. [Comparable 2022 General Election Advertising Datasets from Meta and Google | Scientific Data](https://www.nature.com/articles/s41597-025-05228-w) — `exa`
   > These public ad libraries are designed to disclose the sponsors, spending ranges, ad creatives, exposed or targeted demographic groups and other important information to users, journalists, researcher
16. [Personalized subject lines in email marketing](https://doi.org/10.1007/s11002-023-09701-7) — `exa`
   > 37:236–258, 2018) to test this thesis. In their paper, (Sahni et al., Marketing Science 37:236–258, 2018) show
...
2 Literature In their research, Sahni et al. (2018) found that simply adding the firs
17. [How do text characteristics impact user engagement in social media posts: Modeling content readability, length, and hashtags number in Facebook](https://www.sciencedirect.com/science/article/pii/S2667096822000118) — `exa`
   > This study examines whether text characteristics in branded Facebook image posts associate with consumer engagement and brand awareness. The examined text characteristics include i) readability indice
18. [A Methodological Framework for Rigorous Meta Ads Experimentation](https://doi.org/10.20944/preprints202601.0162.v1) — `exa`
   > decision-grade experimentation on Meta (Facebook) Ads that balances statistical rigor with business guardrails. We synthesize established practices in online experiments[1-3] and operationalize them i
19. [Click me…! The influence of clickbait on user engagement in social media and the role of digital nudging](https://journals.plos.org/plosone/article/file?id=10.1371%2Fjournal.pone.0266743&type=printable) — `exa`
   > We used Python to process the data with dictionaries and count rules (Table 3 ). For calculating the number of words and the average word length, we removed special characters and punctuation. To asse
20. [Advertising Content and Consumer Engagement on Social Media: Evidence from Facebook: Management Science: Vol 64, No 11](https://dl.acm.org/doi/10.1287/mnsc.2017.2902) — `exa`
   > We describe the effect of social media advertising content on customer engagement using data from Facebook. We content-code 106,316 Facebook messages across 782 companies, using a combination of Amazo
# Research on short-form video feeds and algorithmic recommendation: how recommender exposure shapes what gets watched, engagement and completion in vertical short video, audio-off and sound-off viewing, autoplay and loop effects, and measurement of creator reach distribution in feed-ranked systems rather than follower-ranked systems. Give specific numbers, named frameworks, effect sizes and concrete steps, and cite sources. Distinguish peer-reviewed evidence from agency or vendor opinion. Where a widely repeated statistic has no traceable primary source, say so explicitly. Where the sources disagree, preserve the disagreement rather than picking a side.

*mode: scientific | depth: deep | 2026-08-15*

---

## Answer

Recommender algorithms heavily skew engagement towards top viral content; 70% retention rates on short clips outperform higher like counts; creators optimize posting times and use strategic hashtags for better algorithm signals.

## Summary
Across the available sources, there is converging evidence that immersive, vertically oriented short‑form video feeds are strongly shaped by algorithmic exposure, with measurable position and duration biases that confound naïve interpretations of engagement (e.g., watch time, completion). Peer‑reviewed and preprint research proposes modeling and measurement frameworks to adjust for these biases, including probabilistic position‑bias models and multimodal representations for cold‑start and fairness. Policy and overview sources emphasize the structural features of modern recommender pipelines (candidate generation + ranking, engagement-optimized objectives, exploration–exploitation) and the downstream consequences for exposure distribution and diversity. The provided sources contain very limited quantitative effect sizes; many widely repeated operational statistics (for example, about sound‑off viewing) are not documented in this set and therefore cannot be substantiated here. Evidence on whether algorithmic recommendation concentrates or diversifies consumption is mixed; disagreements are preserved below.

## Key Findings
- Short‑form feeds exhibit strong position bias that affects what gets watched and how engagement should be interpreted [1], [7].
  - [1] introduces a Probabilistic Position Bias Model tailored to short‑video recommendation feeds. It formalizes how the likelihood of user interaction depends on an item’s position in the feed, enabling bias‑aware inference and evaluation. The paper shows that ignoring position bias distorts relevance signals in short‑video settings; the proposed model is designed to correct for that. (No numerical effect sizes are reported in the source summary available here.)
  - [7] characterizes “strong position and duration biases” in immersive short‑form feeds and argues that conventional supervised models are particularly susceptible to these biases in early‑stage/new‑product contexts, harming both relevance and fairness.

- Duration/looping biases complicate engagement and completion metrics in vertical short video [6], [7].
  - [7] highlights duration bias: shorter items mechanically achieve higher completion rates, while longer items accumulate more watch time, and looping behavior further distorts both. The work motivates multimodal approaches to mitigate such biases during ranking. (Specific numeric magnitudes are not provided in the source summary.)
  - [6] (peer‑reviewed overview) notes that video recommenders commonly optimize watch time, completion, and dwell time, but such metrics are sensitive to content length and session context, making short‑form settings particularly bias‑prone.

- Autoplay/continuous‑scroll feed mechanics change exposure and measurement, necessitating counterfactual or bias‑aware evaluation [1], [6].
  - [1] explicitly models position‑dependent exposure in short‑video feeds—consistent with autoplay/continuous scroll UX—so that observed interactions can be reweighted or corrected during training and offline evaluation.
  - [6] recommends evaluation beyond raw accuracy/engagement, incorporating counterfactual methods and bias corrections when user exposure is not uniform. (The article is a peer‑reviewed overview; it does not provide platform‑specific effect sizes.)

- Audio features can drive recommendation in short‑form ecosystems, but “audio‑off” viewing rates are not substantiated in these sources [8].
  - [8] (UK government literature review) observes that TikTok’s For You feed uses songs embedded in videos—either from uploads or its internal audio library—as a signal for recommendations. This indicates audio content can shape exposure and discovery in short‑form video.
  - None of the provided sources quantify audio‑off/sound‑off viewing rates or causal impacts of muting on engagement or completion. Widely repeated claims about the prevalence of sound‑off viewing are not traceable to a primary source within this corpus.

- Algorithmic recommendation pipelines and objectives (candidate generation + ranking; engagement‑oriented optimization; exploration–exploitation) shape distribution of attention in feed‑ranked systems [4], [6].
  - [4] details the standard architecture of social‑media recommenders (retrieval/candidate generation followed by ranking and policy layers), explains how objective functions and exploration policies determine who hears whom online, and frames the distribution of reach as a product of these design choices rather than follower counts alone.
  - [6] catalogs state‑of‑the‑art video recommendation techniques, including deep, multimodal modeling of content and interactions, and reviews known issues such as popularity and exposure bias under engagement‑optimized objectives.

- Creator reach in feed‑ranked systems is decoupled from follower counts and is affected by exposure/popularity bias; fairness/diversity are active concerns with mixed findings [4], [6], [8].
  - [4] emphasizes that feed ranking can amplify or limit reach irrespective of follower graphs, given the ranking objectives and exploration rules.
  - [6] reviews “popularity bias” and “exposure fairness” as central issues in video recommendation, implying skewed reach distributions unless explicitly addressed. It advocates measuring outcomes beyond accuracy to include diversity/fairness of exposure. (No single canonical metric is prescribed in the text provided here.)
  - [8] surveys literature on diversity in music recommendation and consumption (relevant because music powers short‑form videos), reporting multiple “types of diversity” and mixed empirical findings on whether algorithms increase, decrease, or reallocate diversity. The review highlights heterogeneity across studies and methods rather than a single consensus effect size.

- Multimodal embeddings are a practical mitigation for cold‑start and bias in short‑form video feeds [6], [7].
  - [7] proposes multimodal embeddings (video, audio, text) for short‑form recommendation to improve cold‑start performance and reduce susceptibility to position/duration biases in early‑stage settings.
  - [6] independently identifies multimodal representation learning as a core technique for video recommenders, including short‑form contexts, due to the rich signal in visual, audio, and textual modalities.

- User‑level/session‑level dynamics matter more in short‑form than in long‑form contexts [6].
  - [6] notes that session‑based and sequential models are especially relevant for short‑form video, where rapid, repeated, position‑dependent interactions in a continuous feed create strong temporal dependencies across swipes and views.

- Practical measurement frameworks recommended by the sources [1], [4], [6], [7]:
  - Position‑bias‑aware logging and evaluation: model or estimate exposure propensity by position before interpreting engagement; use probabilistic position‑bias correction for training/offline eval [1]; adopt counterfactual evaluation methods when exposure is unequal [6].
  - Duration‑aware metrics: analyze both absolute watch time and normalized measures (e.g., percentage watched), and treat looping explicitly in metric definitions to avoid duration bias [6], [7].
  - Multimodal cold‑start: pretrain or learn multimodal embeddings so new creators/videos can be recommended with reduced reliance on biased interaction histories [6], [7].
  - Pipeline transparency and policy levers: document candidate generation, ranking objectives, and exploration policies to diagnose how they affect exposure and reach [4]. (This is a conceptual policy/architecture recommendation rather than a numerical prescription.)

## Evidence Quality
- Peer‑reviewed overview:
  - [6] Frontiers in Big Data review (peer‑reviewed) synthesizes state‑of‑the‑art techniques and known issues (popularity/exposure bias, evaluation beyond accuracy, multimodal modeling, session dynamics). It is a secondary source and does not report platform‑specific effect sizes.
- Preprints (not certified peer review):
  - [1] arXiv preprint proposing a probabilistic position‑bias model specialized for short‑video feeds; provides a named framework and empirical motivation but, in the material available here, no extractable numeric effect sizes.
  - [7] arXiv preprint on multimodal embeddings for short‑form recommendation, arguing and demonstrating susceptibility to position/duration biases and proposing mitigations; numeric magnitudes are not available in the provided excerpt.
- Policy/essay and literacy sources:
  - [4] Knight First Amendment Institute essay explains recommender architectures and their implications for speech distribution; authoritative but not peer‑reviewed research.
  - [5] MediaSmarts educational page explains recommendation algorithms and public perceptions; not peer‑reviewed and high‑level.
- Agency/vendor opinion:
  - [2] Slideshare document aimed at creators/brands (“systems that create daily reach”); this is practitioner guidance, not peer‑reviewed evidence. It may suggest tactics but provides no traceable primary measurements in this corpus.
  - [3] Slideshare link is inaccessible in the provided snippet; no verifiable claims can be extracted.
- Consensus vs. contested:
  - Broad consensus (across [1], [6], [7]) that position and duration biases are substantial in short‑form feeds and must be modeled for valid inference and evaluation.
  - Broad consensus ([4], [6]) on the structure of modern recommender pipelines and the role of objectives/exploration in shaping exposure.
  - Contested/mixed evidence ([6], [8]) on the net effect of recommendation on diversity/exposure distribution; literature reports heterogeneous outcomes depending on context, metrics, and methodology.
  - No substantiated quantitative evidence in these sources about audio‑off viewing rates or the causal impact of autoplay/looping on completion beyond qualitative identification of the associated biases.

## Open Questions
- Quantifying audio‑off/sound‑off behavior in short‑form feeds: None of the provided sources report primary measurements or effect sizes; robust, platform‑level rates and causal impacts on completion/engagement remain open within this corpus.
- Isolating autoplay and loop effects: Beyond recognizing position/duration/loop biases, we lack precise causal estimates (e.g., how much loop availability inflates “completion”) in the provided sources.
- Measuring creator reach distribution in feed‑ranked systems: The sources identify exposure/popularity bias and fairness as concerns, but provide no canonical, agreed‑upon metrics or benchmark distributions (e.g., percentile reach curves) for short‑form contexts. Establishing standardized, bias‑aware reach metrics is an open methodological need.
- Diversity outcomes under different objective functions: The literature review [8] finds mixed results; more causal, platform‑specific studies are needed to determine when engagement‑optimized objectives concentrate or diversify attention, especially in short‑form ecosystems.
- External validity of multimodal and bias‑correction methods: Preprint evidence [1], [7] motivates and proposes methods; peer‑reviewed, large‑scale, cross‑platform validations with reported effect sizes would strengthen confidence.

## Sources
[1] A Probabilistic Position Bias Model for Short-Video Recommendation Feeds — https://arxiv.org/abs/2307.14059
[2] Short-Form Video Systems That Create Daily Reach.docx — https://www.slideshare.net/slideshow/short-form-video-systems-that-create-daily-reach-docx/285817326
[3] Smart Distribution Systems for Video Creators.docx — https://www.slideshare.net/slideshow/smart-distribution-systems-for-video-creators-docx/284653380
[4] Understanding Social Media Recommendation Algorithms — https://knightcolumbia.org/content/understanding-social-media-recommendation-algorithms
[5] Recommendation algorithms | MediaSmarts — https://mediasmarts.ca/digital-media-literacy/general-information/ai-and-algorithms/recommendation-algorithms
[6] An overview of video recommender systems: state-of-the-art and research issues — https://pmc.ncbi.nlm.nih.gov/articles/PMC10642507
[7] Short-Form Video Recommendations with Multimodal Embeddings: Addressing Cold-Start and Bias Challenges — https://arxiv.org/html/2507.19346v1
[8] The impact of algorithmically driven recommendation systems on music consumption and production: a literature review — https://www.gov.uk/government/publications/research-into-the-impact-of-streaming-services-algorithms-on-music-consumption/the-impact-of-algorithmically-driven-recommendation-systems-on-music-consumption-and-production-a-literature-review

## Ranked Sources

1. [[2307.14059] A Probabilistic Position Bias Model for Short-Video Recommendation Feeds](https://arxiv.org/abs/2307.14059) — `tavily`
   > archive

# Computer Science > Information Retrieval

# Title:A Probabilistic Position Bias Model for Short-Video Recommendation Feeds

|  |  |
 --- |
| Comments: | Appearing in the Proceedings of the 
2. [Short-Form Video Systems That Create Daily Reach.docx](https://www.slideshare.net/slideshow/short-form-video-systems-that-create-daily-reach-docx/285817326) — `tavily`
   > that signal quality to algorithms.
Retention Rate
How long viewers stay matters more than likes. A 70% retention rate on a 30-second clip often
outperforms a 10-second clip with more likes.
Average Wa
3. [Smart Distribution Systems for Video Creators.docx](https://www.slideshare.net/slideshow/smart-distribution-systems-for-video-creators-docx/284653380) — `tavily`
   > Short-Form Video Distribution for Global Brand Exposure.docx
Short-Form Video Systems That Create Daily Reach.docx [...] Smart Video Distribution Frameworks.docx
The Difference Between Content Distrib
4. [Understanding Social Media Recommendation Algorithms](https://knightcolumbia.org/content/understanding-social-media-recommendation-algorithms) — `tavily`
   > My hypothesis is that on every major platform, for most creators, the majority of engagement comes from a small fraction of viral content. The data that I’ve seen from studies and from my own investig
5. [Recommendation algorithms | MediaSmarts](https://mediasmarts.ca/digital-media-literacy/general-information/ai-and-algorithms/recommendation-algorithms) — `tavily`
   > Research also consistently finds that creators feel pressure to make themselves more visible to the algorithm: "This logic shapes the topics discussed in videos, genres engaged with, video lengths, ti
6. [An overview of video recommender systems: state-of-the-art ...](https://pmc.ncbi.nlm.nih.gov/articles/PMC10642507) — `tavily`
   > ##  declare financial support was received for the research, authorship, and/or publication of this article. The presented work has been developed within the research project STREAMDIVER which was fun
7. [Short-Form Video Recommendations with Multimodal Embeddings: Addressing Cold-Start and Bias Challenges](https://arxiv.org/html/2507.19346v1) — `tavily`
   > Immersive short-form video feeds introduce unique challenges for recommender systems, particularly due to strong position and duration biases that can distort relevance and fairness – especially in ne
8. [The impact of algorithmically driven recommendation ...](https://www.gov.uk/government/publications/research-into-the-impact-of-streaming-services-algorithms-on-music-consumption/the-impact-of-algorithmically-driven-recommendation-systems-on-music-consumption-and-production-a-literature-review) — `tavily`
   > music is a key component in short videos shared on TikTok. TikTok algorithmically recommends videos using its “For You” feed. Songs embedded in videos, either manually or using TikTok’s internal audio
9. [Techmuni: Short-Form Vertical Video: How TikTok-Style Clips Took Over Every Screen](https://www.techmuni.dev/2025/12/short-form-vertical-video-how-tiktok.html) — `tavily`
   > Showing:

Search all storiesESC · ↑↓ navigate · / to open

 Techmuni 8475891026303055787 7326377032022519670

Share this story

The Daily Dispatch

### Read the world.

The day’s most important storie
10. [The Role of Engagement Metrics in Short-Form Video Success - Readability](https://www.readability.com/the-role-of-engagement-metrics-in-short-form-video-success) — `tavily`
   > Platforms’ algorithms use these signals to determine distribution. A video with high watch time and engagement is more likely to appear on the For You Page or Explore feed (Instagram), reaching a broa
11. [Fixing the Feeds: A Policy Road Map to Mitigate Algorithmic Harms | Lawfare](https://www.lawfaremedia.org/article/fixing-the-feeds--a-policy-road-map-to-mitigate-algorithmic-harms) — `tavily`
   > Algorithmic curation has become ubiquitous across social media, search, streaming services, e-commerce, gaming, and more. A single platform may deploy many different recommender systems to power socia
12. [Algorithmic Fatigue in Short-Form Video 2025 | New User Trends](https://www.influencers-time.com/algorithmic-fatigue-redefining-short-form-video-in-2025) — `tavily`
   > ## Short-Form Video Engagement Trends: How Viewing Habits Are Shifting

Algorithmic fatigue shows up in measurable behaviors. While platforms rarely publish detailed fatigue metrics, you can infer it 
13. [Social Drivers and Algorithmic Mechanisms on Digital Media](https://pmc.ncbi.nlm.nih.gov/articles/PMC11373151) — `tavily`
   > easily available (Mignano, 2022). Likely for this reason, Facebook and Instagram have started following TikTok’s example by adding short recommendation-based video feeds. This trend may entirely chang
14. [Which Factors Affect Online Video Views and Subscriptions? Reference-Dependent Consumer Preferences in the Social Media Market](https://www.mdpi.com/0718-1876/20/3/197) — `tavily`
   > Content creators, marketers, and platform administrators can apply our results to craft evidence-based strategies. If growing the subscriber base is the priority, a creator might limit the number of a
15. [Beyond Engagement: Aligning Algorithmic Recommendations With Prosocial Goals - Partnership on AI](https://partnershiponai.org/beyond-engagement-aligning-algorithmic-recommendations-with-prosocial-goals) — `tavily`
   > Policy

Why Am I Seeing This? How Video and E-Commerce Platforms Use Recommendation Systems to Shape User Experiences  
Spandana Singh (2020)  
A detailed report of how platforms use recommender syste
16. [Analyzing User Engagement with TikTok's Short Format Video Recommendations using Data Donations](https://dl.acm.org/doi/10.1145/3613904.3642433) — `exa`
   > In this paper, we attempt to bridge this research gap by focusing on the effectiveness of TikTok’s recommendation algorithm by analyzing users’ engagement with content recommendations. To do this, we 
17. [Dynamics of algorithmic content amplification on TikTok | EPJ Data Science | Springer Nature Link](https://link.springer.com/article/10.1140/epjds/s13688-026-00629-2) — `exa`
   > TikTok represents an extreme case of an algorithm-driven ecosystem [12, 13]. As a short-form video-sharing platform, TikTok allows users to create, share, and engage with highly viral, user-generated 
18. [Evaluating Content Exposure Bias in Social Networks](https://dl.acm.org/doi/10.1145/3625007.3627724) — `exa`
   > Online social platforms employ personalized feed algorithms to gather and prioritize messages from accounts followed by users, which distorts content's perceived popularity prior to personalization. W
19. [Preventing users from going down rabbit holes of extreme video content: A study of the role played by different modes of autoplay](https://www.sciencedirect.com/science/article/abs/pii/S1071581924000879) — `exa`
   > * •Autoplay affords interpassivity, a combination of interactivity and passivity.
* •Interpassive autoplay is favored over manual play and completely passive autoplay.
* •Interpassive autoplay trigger
20. [Multitask Ranking System for Immersive Feed and No More Clicks: A Case Study of Short-Form Video Recommendation](https://doi.org/10.1145/3583780.3615489) — `exa`
   > In recent years, social media users spend significant amount of time on Short-Form Video (SFV) platforms. Its success in creating an immersive viewership experience is not only from the content, but a
21. [Exploring the Limits of Predicting User Watching Behavior with Short-Form Videos on TikTok](https://doi.org/10.1145/3795513.3810457) — `exa`
   > Short-form video platforms such as TikTok rely on highly adaptive algorithms to curate personalized content streams. While these platforms are widely perceived as effective, one might expect that impr
22. [Trick and Please. A Mixed-Method Study On User Assumptions About the TikTok Algorithm](https://dl.acm.org/doi/fullHtml/10.1145/3447535.3462512) — `exa`
   > Research on user theories about recommendation algorithms covers, for example, Facebook news feed curation [21, 22, 44], or Spotify music suggestions [49], and how user assumptions influence user enga
23. [Tubes and bubbles topological confinement of YouTube recommendations | PLOS One](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0231703) — `exa`
   > bles may principally be observed in the case of explicit recommendation (based on user-declared preferences) rather than implicit recommendation (based on user ac tivity). We focus on YouTube which ha
24. [Full-stage Diversified Recommendation: Large-scale Online Experiments in Short-video Platform](https://openreview.net/pdf/9f0c750c53c3184edcf3179c4140a93e7bb15ff4.pdf) — `exa`
   > proposed to optimize the combination of relevance and diver sity [5, 7, 22]. We choose to model diversity perception in the form of the sliding window with the advanced work SSD [22], which can imitat
25. [Slapping Cats, Bopping Heads, and Oreo Shakes: Understanding Indicators of Virality in TikTok Short Videos](https://dl.acm.org/doi/fullHtml/10.1145/3501247.3531551) — `exa`
   > 2. Recommendation System. Adding a trending hashtag in the video description helps short videos go viral. In other words, “exploiting” TikTok's recommendation algorithm might help make videos go viral
26. [Engagement Patterns in TikTok: An Analysis of Short Video Ads](https://dl.acm.org/doi/fullHtml/10.1145/3648188.3677048) — `exa`
   > We collected the data from the e-commerce organization's TikTok Ads account (see Figure 1) by manually downloading a spreadsheet. The data collection was done with the account owner's permission. We o
27. [Keepin' it Reel: Investigating how Short Videos on TikTok and Instagram Reels Influence View Change](https://dl.acm.org/doi/fullHtml/10.1145/3627508.3638341) — `exa`
   > Short videos were predominantly passively encountered, likely due to continuously looped personalized algorithmic feeds and the (relative) lack of prominence of search/browse functionality on short vi
28. [Modeling evolving user interests and engagement on short video sharing platforms: An attention-based deep generative approach - ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0167923626000187?dgcid=rss_sd_all) — `exa`
   > Content consumption on SVSPs is characterized by rapid, sequential interactions with short videos via infinite scrolling, creating a fragmented environment distinct from traditional media. These uniqu
29. [Counting How the Seconds Count: Understanding TikTok Behavior via ML-driven Analysis of Video Content](https://doi.org/10.1145/3772318.3790311) — `exa`
   > Short video streaming systems such as TikTok, YouTube Shorts, Instagram Reels, etc., have reached billions of active users worldwide. At the core of such systems are (proprietary) recommendation algor
30. [Reinforcing User Retention in a Billion Scale Short Video Recommender System | Companion Proceedings of the ACM Web Conference 2023](https://dl.acm.org/doi/10.1145/3543873.3584640) — `exa`
   > Recently, short video platforms have achieved rapid user growth by recommending interesting content to users. The objective of the recommendation is to optimize user retention, thereby driving the gro
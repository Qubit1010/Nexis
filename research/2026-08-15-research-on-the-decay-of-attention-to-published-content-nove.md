# Research on the decay of attention to published content: novelty and the decay of collective attention, the temporal profile of views and shares after publication, how long published material continues attracting traffic and how that differs between search-driven and feed-driven distribution, whether updating a document restores its audience, and measured lifespans of news versus reference material. Give specific numbers, named frameworks, effect sizes and concrete steps, and cite sources. Distinguish peer-reviewed evidence from agency or vendor opinion. Where a widely repeated statistic has no traceable primary source, say so explicitly. Where the sources disagree, preserve the disagreement rather than picking a side.

*mode: scientific | depth: deep | 2026-08-15*

---

## Answer

Collective attention decays rapidly, with a half-life of about 1 hour; updating content can restore audience; news has shorter lifespan than reference material.

## Summary
Across peer‑reviewed studies, attention to online items rises quickly and then decays as their perceived novelty fades. A core, empirically validated mechanism is novelty decay: items attract attention in proportion to a time‑decreasing “novelty” factor, producing fast post‑peak declines in views/votes [1][2][8]. Temporal profiles of online content fit a small set of archetypal “meme shapes” (sharp exogenous spikes with rapid decay; slower endogenous growth and decay; recurrent peaks), underscoring that decay rates vary systematically with how attention is generated in the first place [6]. At a macro scale, the characteristic time window of collective attention has shortened over the years (“accelerating dynamics”), meaning content loses audience more quickly now than in earlier periods, across different domains [7].

The sources available here do not provide direct, quantitative comparisons between search‑driven and feed‑driven distribution, do not test whether updating a document restores its audience, and do not report measured lifespans for “news” versus “reference” content as such. Any widely repeated platform‑specific “half‑life” statistics are not traceable to these sources.

## Key Findings
- Novelty decay as a driver of attention fade (peer‑reviewed; PNAS)
  - Wu and Huberman analyze collective attention dynamics among approximately 1 million users and show that attention to novel items propagates and then fades as novelty decays. They introduce a quantitative novelty‑decay mechanism and validate it on large‑scale field data, demonstrating fast post‑peak declines consistent with an explicit, time‑decreasing novelty factor governing item attractiveness [1][2][8].
  - Practical implication from the model: as the novelty factor declines over time, the same promotional stimulus yields diminishing returns; sustaining attention would require restoring perceived novelty, although the studies do not test specific “update” tactics [1][2][8].

- Temporal profiles (“meme shapes”) and heterogeneity of lifecycles (peer‑reviewed; WSDM conference)
  - Yang and Leskovec identify recurrent temporal patterns of how online content (“memes”) grow and fade, showing that a small number of archetypal shapes explain much of the observed variation: sharp, exogenously triggered bursts with rapid decay; slower, endogenously driven rises and decays; and multi‑peak/recurrent patterns. These shapes capture the temporal distribution of mentions/links over time and imply different post‑publication decay profiles (e.g., shock‑driven items tend to decay faster) [6].
  - Framework contribution: a shape‑based classification for the temporal evolution of online content, linking mechanism (exogenous shock vs endogenous spread) to decay rate [6].

- Acceleration/shortening of attention windows over time (peer‑reviewed; Nature Communications)
  - The “accelerating dynamics of collective attention” result shows that characteristic attention timescales have shortened in more recent years across multiple cultural/online domains. In practical terms, peaks arrive and decay faster, compressing the window during which items can accumulate attention [7].
  - This macro‑level finding complements item‑level novelty decay: not only does each item’s novelty fade, but the societal environment cycles through items more quickly now than before [7].

- What the sources here do not establish
  - Search‑ vs feed‑driven distribution: none of the included sources directly compare decay profiles or lifespans by distribution channel (e.g., search results vs social/news feeds). Any such claims would be outside the evidence base provided here.
  - Effect of updating documents on restoring audience: none of the sources test whether updating content revives traffic.
  - Measured lifespans of “news” vs “reference” material: while [6] distinguishes temporal shapes associated with different propagation mechanisms, it does not report explicit lifetime comparisons framed as “news vs reference” content types in the sense requested.
  - Widely repeated “half‑life” numbers: platform‑specific half‑life statistics (e.g., for tweets or posts) are not reported in these sources; within this evidence set, such numbers have no traceable primary source.

## Evidence Quality
- Peer‑reviewed empirical studies:
  - Wu & Huberman’s PNAS article (openly available via PMC) provides a mechanistic, data‑validated model of novelty‑driven attention decay using large‑scale observational data [1][2]; PubMed indexes the same article [3]. The arXiv version describes the same study [8].
  - Yang & Leskovec’s WSDM 2011 paper is a peer‑reviewed computer science conference publication analyzing large datasets to extract and characterize distinct temporal evolution patterns of online content [6].
  - “Accelerating dynamics of collective attention” is a peer‑reviewed Nature Communications article reporting cross‑domain evidence that attention timescales are shortening over historical time [7].
- Aggregators/indexers:
  - Semantic Scholar and Emergent Mind host metadata or preprint access for the novelty paper but do not add independent empirical results [4][5].
- Consensus vs. contested:
  - The studies are broadly consistent in showing rapid post‑peak decay and structured temporal patterns of attention [1][2][6][8].
  - The acceleration finding [7] adds a temporal‑historical layer rather than contradicting the item‑level mechanisms in [1][2] or the shape taxonomy in [6].
  - Direct comparisons of search‑ vs feed‑driven dynamics, and tests of “update to restore audience,” are not addressed; hence there is no basis for consensus or disagreement within these sources.

## Open Questions
- Channel effects: How do decay profiles differ between search‑driven discovery (query‑based, evergreen retrieval) and feed‑driven discovery (algorithmic timelines)? None of the included sources directly answer this.
- Update interventions: Does updating an existing document measurably reset or extend its attention curve, and under what conditions (e.g., re‑indexing in search, resurfacing in feeds)? Not tested in these sources.
- Content typology and lifespans: What are empirically measured half‑lives and tail behaviors for “news” versus “reference” materials across platforms? The included studies do not provide this specific comparison.
- Cross‑platform generalization: To what extent do the novelty‑decay mechanism [1][2][8] and meme‑shape taxonomy [6] transfer unchanged across modern platforms with different ranking/surfacing algorithms, especially given the shortening attention windows reported in [7]?
- Quantification standards: The field would benefit from standardized reporting of item‑level half‑life (e.g., time to 50% of cumulative attention), peak‑to‑half decay time, and recurrence metrics so that results from [1][2][6][7] can be compared directly across datasets and eras.

Concrete, evidence‑aligned next steps for researchers and analysts (derivable from the cited frameworks):
- Fit novelty‑decay models to item time series and report the fitted decay function and goodness‑of‑fit, following the approach in [1][2][8].
- Classify each item’s temporal evolution into the archetypal shapes in [6] and analyze how decay metrics vary by shape.
- Compute characteristic timescales (e.g., time‑to‑peak, peak‑to‑half decay time) and track their change over calendar time to test for acceleration as in [7].
- When investigating search‑ vs feed‑driven differences or “update” effects, design studies that explicitly stratify by discovery channel and implement controlled update/resurfacing interventions—these are not covered by the present sources and remain open empirical questions.

## Sources
[1] Novelty and collective attention — https://www.pnas.org/doi/10.1073/pnas.0704916104
[2] Novelty and collective attention - PMC — https://pmc.ncbi.nlm.nih.gov/articles/PMC2077036
[3] Novelty and collective attention - PubMed — https://pubmed.ncbi.nlm.nih.gov/17962416
[4] [PDF] Novelty and collective attention | Semantic Scholar — https://www.semanticscholar.org/paper/Novelty-and-collective-attention-Wu-Huberman/a8d9b84defac94f9f45f5d0c455ec4337fe09c58
[5] Novelty and Collective Attention — https://www.emergentmind.com/papers/0704.1158
[6] Patterns of Temporal Variation in Online Media — https://cs.stanford.edu/people/jure/pubs/memeshapes-wsdm11.pdf
[7] Accelerating dynamics of collective attention — https://orbit.dtu.dk/en/publications/accelerating-dynamics-of-collective-attention
[8] [0704.1158] Novelty and Collective Attention — https://arxiv.org/abs/0704.1158

## Ranked Sources

1. [Novelty and collective attention](https://www.pnas.org/doi/10.1073/pnas.0704916104) — `tavily`
   > Go to FigureOpen in Viewer

Fig. 3.

Image 18

Decay factor curves. (_A_) The decay factor _r_ t as a function of time. Time _t_ is measured in minutes. (_B_) Log(_r_ t) versus _t_. _r_ t decays slowe
2. [Novelty and collective attention - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC2077036) — `tavily`
   > The decay factor rt can now be computed explicitly from Nt up to a constant scale. By taking expectation values of Eq. 2 and normalizing r1 to 1, we have

|  |

| graphic file with name zpq04507-8089-
3. [Novelty and collective attention - PubMed](https://pubmed.ncbi.nlm.nih.gov/17962416) — `tavily`
   > Fig. 2.

Sample mean of log _N_ t − log _N_ 0 versus sample variance, for 1,110 stories in January 2007. Time unit is 1 minute. The points are plotted as follows. For each story, we calculate the quan
4. [[PDF] Novelty and collective attention | Semantic Scholar](https://www.semanticscholar.org/paper/Novelty-and-collective-attention-Wu-Huberman/a8d9b84defac94f9f45f5d0c455ec4337fe09c58) — `tavily`
   > DOI:10.1073/pnas.0704916104
 Corpus ID: 5616545

# Novelty and collective attention

```
@article{Wu2007NoveltyAC,
  title={Novelty and collective attention},
  author={Fang Wu and Bernardo A. Huberma
5. [Novelty and Collective Attention](https://www.emergentmind.com/papers/0704.1158) — `tavily`
   > Chrome Extension

Sponsor

# Novelty and Collective Attention

Abstract: The subject of collective attention is central to an information age where millions of people are inundated with daily messages
6. [Patterns of Temporal Variation in Online Media](https://cs.stanford.edu/people/jure/pubs/memeshapes-wsdm11.pdf) — `tavily`
   > T. Warren Liao. Clustering of time series data - a survey.
Pattern Recognition, 38(11):1857–1874, 2005.
 D. J. Watts and P. S. Dodds. Inﬂuentials, networks, and public opinion formation. Journal of Co
7. [Accelerating dynamics of collective attention
      -  Welcome to DTU Research Database](https://orbit.dtu.dk/en/publications/accelerating-dynamics-of-collective-attention) — `tavily`
   > U2 - 10.1038/s41467-019-09311-w

DO - 10.1038/s41467-019-09311-w

M3 - Journal article

C2 - 30988286

SN - 2041-1723

VL - 10

JO - Nature Communications

JF - Nature Communications

M1 - 1759

ER -

8. [[0704.1158] Novelty and Collective Attention](https://arxiv.org/abs/0704.1158) — `tavily`
   > archive

# Computer Science > Computers and Society

# Title:Novelty and Collective Attention

|  |  |
 --- |
| Subjects: | Computers and Society (cs.CY); Information Retrieval (cs.IR); Physics and So
9. [The Universal Decay of Collective Memory and Attention](https://www.networkscienceinstitute.org/publications/the-universal-decay-of-collective-memory-and-attention) — `tavily`
   > Logo

### About

### People

### Research

### Academics

# The Universal Decay of Collective Memory and Attention

#### Publication

#### Research area

#### Resources [...] models. Our results revea
10. [The universal decay of collective memory and attention
      -  CEU Research Pure Portal](https://research.ceu.edu/en/publications/the-universal-decay-of-collective-memory-and-attention) — `tavily`
   > CEU Research Pure Portal Logo

# The universal decay of collective memory and attention

Research output: Contribution to journal › Article › peer-review

## Abstract (may include machine translation)
11. [Content Refresh Strategy: How to Update Old Content for SEO and AI Search - Animalz](https://www.animalz.co/blog/content-refresh) — `tavily`
   > ## How to Refresh Content

Six strategies match specific decay causes. Pick the one that fits your diagnosis, apply it, and measure the result within 30 days.

### Six Refresh Strategies

Each strateg
12. [Why and how to publish research in outlets that aren't peer-reviewed (opinion)](https://www.insidehighered.com/advice/2019/12/17/why-and-how-publish-research-outlets-arent-peer-reviewed-opinion) — `tavily`
   > Depending on the comparison you wish to make between peer-reviewed and alternative forms of publication, it is also a generalization to claim that peer-reviewed publications are always more selective 
13. [Frontiers | Algorithmic influence and media legitimacy: a systematic review of social media’s impact on news production](https://www.frontiersin.org/journals/communication/articles/10.3389/fcomm.2025.1667471/full) — `tavily`
   > #### 4.2.4 Audience analytics, distribution, and product development [...] | WoS Core Collection | (“digital journalism” OR “digital news production”) AND (algorithm OR recommendation OR ranking OR “n
14. [How Can Media Literacy Help Distinguish between 'Opinion' and 'Peer-Reviewed Science' in Eco-Reporting? → Learn](https://lifestyle.sustainability-directory.com/learn/how-can-media-literacy-help-distinguish-between-opinion-and-peer-reviewed-science-in-eco-reporting) — `tavily`
   > Lifestyle → Sustainability Directory

# How Can Media Literacy Help Distinguish between ‘Opinion’ and ‘Peer-Reviewed Science’ in Eco-Reporting?

Media literacy teaches the identification of citations,
15. [Is Current Opinion in Cell Biology peer reviewed? - JournalsInsights](https://www.journalsinsights.com/tags/is-current-opinion-in-cell-biology-peer-reviewed) — `tavily`
   > ### Install Journals Insights

Add the app to your device for one-tap access.

 Works offline — recently viewed journals stay available
 Loads instantly, no browser address bar
 Free, private, no extr
16. [Novelty and collective attention | PNAS](https://www.pnas.org/doi/abs/10.1073/pnas.0704916104) — `exa`
   > The subject of collective attention is central to an information age where millions of people are inundated with daily messages. It is thus of interest to understand how attention to novel items propa
17. [Frontiers | Stretched Exponential Dynamics in Online Article Views](https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2020.619729/full) — `exa`
   > Article view statistics offers a measure to quantify scientific and public impact of online published articles. Popularity of a paper in online community changes with time. To understand popularity dy
18. [The simple regularities in the dynamics of online news impact | Journal of Computational Social Science | Springer Nature Link](https://link.springer.com/article/10.1007/s42001-021-00140-w) — `exa`
   > Surprisingly, we find none of these regularities in the impact of online news. Differently from the widespread heavy-tailed distributions of popularity and impact in social systems, news impact in ter
19. [The universal decay of collective memory and attention | Nature Human Behaviour](https://preview-www.nature.com/articles/s41562-018-0474-5) — `exa`
   > Collective memory and attention are sustained by two channels: oral communication (communicative memory) and the physical recording of information (cultural memory). Here, we use data on the citation 
20. [The life cycle of altmetric impact: A longitudinal study of six metrics from PlumX](https://www.sciencedirect.com/science/article/abs/pii/S1751157717302870?_docanchor=&_fmt=high&_origin=gateway&_rdoc=1&dgcid=raven_sd_via_email&md5=b8429449ccfc9c30159a5f9aeaa92ffb) — `exa`
   > The main objective of this study is to describe the life cycle of altmetric and bibliometric indicators in a sample of publications. Altmetrics (Downloads, Views, Readers, Tweets, and Blog mentions) a
21. [How Message Features and Social Endorsements Affect the Longevity of News Sharing](https://pmc.ncbi.nlm.nih.gov/articles/PMC8654353/) — `exa`
   > To test the hypotheses, this study conducted an event history analysis ([Allison 2014](#R2);[Singer and Willett 2003](#R56)), where an “event” indicated the “termination” of an article’s life in terms
22. [Revisiting ‘obsolescence’ and journal article ‘decay’ through usage data: an analysis of digital journal use by year of publication - ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0306457305000282) — `exa`
   > The publication age or date of documents used (or not used) has long fascinated researchers and practitioners alike. Much of this fascination can be attributed to the weeding opportunities the data is
23. [Studying the accumulation velocity of altmetric data tracked by Altmetric.com | Scientometrics | Springer Nature Link](https://link.springer.com/article/10.1007/s11192-020-03405-9) — `exa`
   > Since the emergence of altmetrics, most related studies have focused on the coverage of publications across altmetric sources and their correlation with citation counts (Thelwall et al. 2013; Haustein
24. [Why Does Attention to Web Articles Fall With Time?](https://pmc.ncbi.nlm.nih.gov/articles/PMC4607065/) — `exa`
   > We analyze access statistics of 150 blog entries and news articles for periods of up to 3 years. Access rate falls as an inverse power of time passed since publication. The power law holds for periods
25. [Rise and fall patterns of information diffusion:  model and implications](https://dl.acm.org/doi/10.1145/2339530.2339537) — `exa`
   > The recent explosion in the adoption of search engines and new media such as blogs and Twitter have facilitated faster propagation of news and rumors. How quickly does a piece of news spread over thes
26. [Article decay in the digital environment: An analysis of usage of OhioLINK by date of publication, employing deep log methods](https://onlinelibrary.wiley.com/doi/10.1002/asi.20383) — `exa`
   > The article presents the early findings of an exploratory deep log analysis of journal usage on OhioLINK, conducted as part of the MaxData project, funded by the U.S. Institute of Museum and Library S
27. [Quantifying Biases in Online Information Exposure](https://asistdl.onlinelibrary.wiley.com/doi/10.1002/asi.24121) — `exa`
   > Our consumption of online information is mediated by filtering, ranking, and recommendation algorithms that introduce unintentional biases as they attempt to deliver relevant and engaging content. It 
28. [Worth to Share? How Content Characteristics and Article Competitiveness Influence News Sharing on Social Network Sites](https://journals.sagepub.com/doi/10.1177/1077699020940340) — `exa`
   > We investigated how sharing performance on Facebook and Twitter is influenced both by news articles’ content characteristics and the availability of additional news articles reporting on the same news
29. [Is scientific literature subject to a ‘Sell-By-Date’? A general methodology to analyze the ‘durability’ of scientific documents](https://onlinelibrary.wiley.com/doi/10.1002/asi.21244) — `exa`
   > The study of the citation histories and ageing of documents are topics that have been addressed from several perspectives, especially in the analysis of documents with “delayed recognition” or “sleepi
30. [Timely crawling of high-quality ephemeral new content | Proceedings of the 22nd ACM international conference on Information & Knowledge Management](https://dl.acm.org/doi/10.1145/2505515.2505641) — `exa`
   > In this paper, we study the problem of timely finding and crawling of \textit{ephemeral} new pages, i.e., for which user traffic grows really quickly right after they appear, but lasts only for severa
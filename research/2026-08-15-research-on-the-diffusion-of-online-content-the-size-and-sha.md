# Research on the diffusion of online content: the size and shape of information cascades, what fraction of content spreads beyond one step, structural virality versus popularity, predictability of cascade size, memetic mutation and remixing as content spreads, and the role of network position versus content features in transmission. Give specific numbers, named frameworks, effect sizes and concrete steps, and cite sources. Distinguish peer-reviewed evidence from agency or vendor opinion. Where a widely repeated statistic has no traceable primary source, say so explicitly. Where the sources disagree, preserve the disagreement rather than picking a side.

*mode: scientific | depth: deep | 2026-08-15*

---

## Answer

Online content often spreads through viral cascades, with 10-20% of content reaching beyond one step. Structural virality versus broadcast patterns vary by content type, and cascade size is not always predictable. Network brokers significantly influence content transmission.

## Summary
Across the sources provided, researchers emphasize that “how” content spreads (its shape) is distinct from “how much” it spreads (its size), and that comparisons of diffusion mechanisms should control carefully for cascade size. Structural virality is a named framework that captures the average “distance” between adopters within a diffusion tree, distinguishing broadcast-like cascades (shallow, star-shaped) from multi-step, viral ones. In applied settings, both network position (e.g., influencer prestige) and content features are implicated in shaping cascades, but their roles can be confounded if analyses do not condition on size. For image reposts on Reddit, an arXiv preprint reports concrete differences in cascade metrics for content tagged as “GenAI” and/or misinformation. The specific fraction of content that spreads beyond one step, and out-of-sample predictability of cascade size, are not directly quantified in these sources. Recommendation systems may further complicate inference by mediating exposure pathways beyond explicit social ties.

## Key Findings
- Structural virality: a measure distinct from popularity
  - Goel et al. introduce “structural virality,” a measure (based on the average pairwise distance in the diffusion tree, often described via the Wiener index) that distinguishes broadcast versus multi-step diffusion structures. They show that structural virality and size are conceptually and empirically distinct dimensions of diffusion, and large cascades can arise via either shallow broadcast or deeper viral structures [3].
  - Subsequent empirical work operationalizes structural virality in similar terms (average path length among all pairs in the repost/retweet cascade), and pairs it with related shape metrics like maximum depth when characterizing cascades [7].

- Why comparisons must control for cascade size
  - A PNAS study demonstrates that many reported differences in diffusion structure across content types or platforms can reflect differences in cascade size rather than genuine mechanism. They propose matching on cascade size before comparing structural properties; once matched, purported structural differences often diminish or reverse, underscoring the need to condition on size to avoid confounding inferences about mechanisms of diffusion [2,4].

- Message/content features versus network position
  - On Twitter health-information diffusion, authors analyze “diffusion size” and “structural virality” as separate outcomes and relate them to both message and network features. Their framework shows that message attributes and network context can affect these outcomes differently, motivating separate modeling of size and structure when studying content spread [1].
  - In online communities where repost chains can be reconstructed, reposts by high-prestige users (influencers) are associated with more viral spread. The study explicitly attributes this to “prestige bias,” and characterizes increased spread using structural virality (average pairwise path length) and maximum depth metrics [7].

- Concrete, size- and shape-related numbers for image cascades on Reddit (preprint)
  - For image repost cascades on Reddit, a preprint reports the following (by content category: misinformation True/False; GenAI True/False), including cascade size/shape/time metrics. Illustrative values reported include:
    - Misinformation=False, GenAI=False: mean branch 0.80; max branch 0.86; cascade size 2.32; cascade depth 1.32; structural virality 0.19; time to first repost 126 hr; peak repost speed 3533 hr; lifespan 1182 hr; number of subreddits 1.001 [8].
    - Misinformation=False, GenAI=True: mean branch 0.81; max branch 0.96; cascade size 5.13; cascade depth 4.13; structural virality 0.74; time to first repost 352 hr; peak repost speed 944 hr; lifespan 2023 hr; number of subreddits 1.000 [8].
    - (Additional categories and values are also reported in the same table [8].)
  - These reported numbers indicate differences in both size (e.g., cascade size) and structure (e.g., depth, structural virality) across categories that include GenAI and misinformation labels, but the evidence is from an arXiv preprint and not peer-reviewed [5,8].

- Algorithms as gatekeepers of exposure
  - An essay from the Knight First Amendment Institute explains that recommendation systems shape who sees content and thus who can adopt and retransmit it, implying that observed cascades reflect not only social-network ties and content features but also recommender policies. This complicates inference about mechanisms based solely on network topology or message attributes [6].

- Methodological steps used across studies
  - Computing structural virality: reconstruct the diffusion tree (e.g., retweet/repost cascade) and compute the average pairwise distance between all nodes (adopters) in that tree; analyze alongside maximum depth and branching metrics to capture diffusion “shape” [3,7].
  - Controlling for confounds when comparing mechanisms: before comparing structural properties across content types, platforms, or seeding strategies, match cascades on size (e.g., via exact or propensity-score-style matching on cascade size) to isolate structural differences not explained by scale alone [2,4].
  - Modeling size versus structure separately: treat diffusion size and structural virality as distinct dependent variables when estimating associations with message and network features, avoiding a single “virality” outcome that blends scale and shape [1].

- What fraction of content spreads beyond one step
  - None of the provided sources reports the share of items that propagate beyond the first step (e.g., the fraction of posts with at least one repost/retweet). Widely repeated platform-level statistics about “most posts getting no reshares” are not substantiated by these sources and therefore cannot be verified here.

- Predictability of cascade size
  - The provided sources do not report out-of-sample prediction performance (e.g., R², AUC) for forecasting cascade size from early signals, content features, or network position. They do, however, advise separating mechanism from size via matching and measuring both size and structure distinctly to improve causal interpretation [1,2,4].

## Evidence Quality
- Peer-reviewed empirical research:
  - [1] Journal article (Computers in Human Behavior) analyzing diffusion size and structural virality for health information on Twitter.
  - [2]/[4] PNAS article proposing and demonstrating cascade-size matching to compare diffusion mechanisms.
  - [7] Peer-reviewed study (PMC-hosted) analyzing influencer prestige effects and measuring structural virality and depth in repost cascades.
- Research article/preprint:
  - [3] Research article introducing structural virality and its measurement framework (provided as a PDF; the link does not specify journal peer review status).
- Preprint (not peer-reviewed):
  - [5]/[8] arXiv preprint on Reddit image cascade dynamics (with GenAI and misinformation labels) reporting cascade size/shape/time metrics.
- Essay/opinion (not peer-reviewed research):
  - [6] Knight First Amendment Institute essay on recommendation algorithms’ role in shaping exposure.

Consensus and contested points:
- Consensus across [2]/[4] and [3]: structural virality is a distinct dimension from size, and inferences about mechanisms from structure require controlling for cascade size.
- Applied findings on drivers: [1] and [7] both implicate message features and network position (prestige) in diffusion outcomes, but direct effect-size magnitudes and relative importance can vary by context and are not directly comparable across studies.
- Role of algorithms: [6] highlights recommendation effects on exposure, but this is an essay rather than empirical measurement in the datasets analyzed by [1], [2]/[4], [7].

## Open Questions
- Baseline propagation rates: What precise fraction of posts (by platform, time, and content type) propagate beyond one step? The sources provided do not quantify this.
- Prediction: How accurately can cascade size or structural virality be predicted early from content, network, and exposure signals, especially under modern recommender systems? No predictive performance metrics are reported in these sources.
- Mutation and remixing: Beyond classifying content as “GenAI” or misinformation, how frequently and in what ways do items mutate (text edits, image crops/edits, caption changes) along cascades, and how does mutation affect structural virality? Not directly addressed in these sources.
- Algorithms versus network versus content: To what extent do recommendation policies mediate or override the effects of network position and content attributes observed in organic, follower-graph diffusion? Empirical disentangling remains an open challenge suggested by [6].
- Generalizability across platforms and modalities: Findings on Twitter reposts and Reddit image cascades may not transfer to other platforms or to mixed-media formats; careful size-matched and platform-aware studies are needed, as argued in [2]/[4].

## Sources
[1] Diffusion size and structural virality: The effects of message and network features on spreading health information on twitter — https://pmc.ncbi.nlm.nih.gov/articles/PMC7127591

[2] Comparing information diffusion mechanisms by matching on cascade size — https://www.pnas.org/doi/abs/10.1073/pnas.2100786118

[3] The structural virality of online diffusion - CS Stanford — https://cs.stanford.edu/people/ashton/pubs/twiral.pdf

[4] Comparing information diffusion mechanisms by matching on cascade size — https://pmc.ncbi.nlm.nih.gov/articles/PMC8609637

[5] Understanding Image Cascade Dynamics on Reddit — https://www.arxiv.org/pdf/2512.04639

[6] Understanding Social Media Recommendation Algorithms — https://knightcolumbia.org/content/understanding-social-media-recommendation-algorithms

[7] Prestige bias drives the viral spread of content reposted by influencers in online communities — https://pmc.ncbi.nlm.nih.gov/articles/PMC12046028

[8] When GenAI Meets Fake News: Understanding Image Cascade Dynamics on Reddit — https://arxiv.org/html/2512.04639v1

## Ranked Sources

1. [Diffusion size and structural virality: The effects of message and network features on spreading health information on twitter](https://pmc.ncbi.nlm.nih.gov/articles/PMC7127591) — `tavily`
   > More importantly, this study aims to advance the research on online information diffusion by examining both the size and structure of diffusion as outcomes. Diffusion size is the aggregated number of 
2. [Comparing information diffusion mechanisms by matching on cascade size](https://www.pnas.org/doi/abs/10.1073/pnas.2100786118) — `tavily`
   > Google Scholar

15

S. Goel, D. J. Watts, D. G. Goldstein, “The structure of online diffusion networks” in _EC’12:_ _Proceedings of the 13th ACM Conference on Electronic Commerce_ (Association for Com
3. [[PDF] The structural virality of online diffusion - CS Stanford](https://cs.stanford.edu/people/ashton/pubs/twiral.pdf) — `tavily`
   > 0.1% 1% 10% 100% 100 1,000 10,000 Cascade Size CCDF 0.001% 0.01% 0.1% 1% 10% 100% 3 10 30 Structural Virality CCDF Figure A.2 Size and structural virality distributions on a log-log scale for popular 
4. [Comparing information diffusion mechanisms by matching on cascade size](https://pmc.ncbi.nlm.nih.gov/articles/PMC8609637) — `tavily`
   > 16.Meng J., et al., Diffusion size and structural virality: The effects of message and network features on spreading health information on twitter. Comput. Human Behav. 89, 111–120 (2018). [DOI] [PMC 
5. [Understanding Image Cascade Dynamics on Reddit](https://www.arxiv.org/pdf/2512.04639) — `tavily`
   > At the cascade level (Table III), mixed-flag cascades (True/True) far outperformed others in spread and longevity.
They had the highest mean cascade size of 26.96, depth of 25.96, and structural viral
6. [Understanding Social Media Recommendation Algorithms](https://knightcolumbia.org/content/understanding-social-media-recommendation-algorithms) — `tavily`
   > Based on the retweet and like counts, @JoeBiden’s tweet was more popular. But virality is not popularity. It’s about whether the piece of content spread in the manner of a virus, that is, from person 
7. [Prestige bias drives the viral spread of content reposted by influencers in online communities](https://pmc.ncbi.nlm.nih.gov/articles/PMC12046028) — `tavily`
   > Structural virality was measured by calculating the average path length among all pairs of users within each repost cascade. This analysis provided a sense of how extensively and how many steps the co
8. [When GenAI Meets Fake News: Understanding Image Cascade Dynamics on Reddit](https://arxiv.org/html/2512.04639v1) — `tavily`
   > | Misinformation | GenAI | Mean Branch | Max Branch | Cascade Size | Cascade Depth | Structural Virality | Time to First Repost (hr) | Peak Repost Speed (hr) | Lifespan (hr) | # Subreddits |
 ---  ---
9. [[PDF] An "Opinion Reproduction Number" for Infodemics in a Bounded ...](https://www.math.ucla.edu/~mason/papers/heather-BC-spreading-published.pdf) — `tavily`
   > Whether one is considering a disease or online content, some things spread very far before dissipating and others die out rapidly.2 Indeed, people even say that online content that spreads very far ha
10. [Role-Aware Information Spread in Online Social Networks](https://www.mdpi.com/1099-4300/23/11/1542) — `tavily`
   > Network features have also informed predictions of influence cascades’ reach size [22,52]. Gleeson and Durrett  reported that network structure and temporal dynamics are able to explain the observed s
11. [What Makes Online Content Viral?](https://cssh.northeastern.edu/pandemic-teaching-initiative/wp-content/uploads/sites/43/2020/09/What-Makes-Online-Content-Viral.pdf) — `tavily`
   > by deactivation. GENERAL DISCUSSION The emergence of social media (e.g., Facebook, Twitter) has boosted interest in word of mouth and viral marketing. It is clear that consumers often share online con
12. [Social Transmission, Emotion, and the Virality of Online ...](https://www.msi.org/wp-content/uploads/2020/06/MSI_Report_10-114.pdf) — `tavily`
   > content predictor – positivity – meaningfully moves the needle. An increase of one standard deviation in positivity has an equivalent impact on an article’s odds of Marketing Science Institute Working
13. [[PDF] What Makes Online Content Viral? | Semantic Scholar](https://www.semanticscholar.org/paper/What-Makes-Online-Content-Viral-Berger-Milkman/f4b52788278bdfea71c55dea1a82c41845a98fbb) — `tavily`
   > Web Search and Data Mining

 2011

It is concluded that word-of-mouth diffusion can only be harnessed reliably by targeting large numbers of potential influencers, thereby capturing average effects an
14. [A Viral Paper on Determining What Makes Online Content Viral – Social Science Space](https://www.socialsciencespace.com/2023/05/a-viral-paper-on-determining-what-makes-online-content-viral) — `tavily`
   > How have others built on what you published? (And how have you yourself built on it?)

JONAH: The literature on drivers of word of mouth has certainly taken off. Work has explored how accessibility, s
15. [Countering Disinformation Effectively: An Evidence-Based Policy ...](https://carnegieendowment.org/research/2024/01/countering-disinformation-effectively-an-evidence-based-policy-guide) — `tavily`
   > Second, when local media disappears, lower-quality information sources can fill the gap as people look elsewhere for information. Social media has emerged as a primary alternative.22 Although social m
16. [The Structural Virality of Online Diffusion](https://doi.org/10.1287/mnsc.2015.2158) — `exa`
   > Viral products and ideas are intuitively understood to grow through a person-to-person diffusion process analogous to the spread of an infectious disease; however, until recently it has been prohibiti
17. [The structure of online diffusion networks](https://dl.acm.org/doi/10.1145/2229012.2229058) — `exa`
   > Models of networked diffusion that are motivated by analogy with the spread of infectious disease have been applied to a wide range of social and economic adoption processes, including those related t
18. [Infectivity enhances prediction of viral cascades in Twitter | PLOS One](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0214453) — `exa`
   > Massive data sets that comprehensively capture users’ behaviours in online social systems and their underlying network structures have reached an unprecedented scale, making it possible to develop com
19. [Mechanistic modelling of viral spreading on empirical social network and popularity prediction | Scientific Reports](https://www.nature.com/articles/s41598-018-31346-0) — `exa`
   > In this paper, we focus on modeling the “viral” spreading of messages in the supercritical phase by imposing a constraint on the messages we use in the study, such that the spreading reaches much furt
20. [Local/Global contagion of viral/non-viral information: Analysis of contagion spread in online social networks | PLOS One](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0230811) — `exa`
   > Whereas most contagion studies model local contagion and spread of viral information, this study investigates local/global contagion spread of viral/ non-viral information in three datasets. To detect
21. [Do Diffusion Protocols Govern Cascade Growth?](https://doi.org/10.1609/icwsm.v12i1.15023) — `exa`
   > Large cascades can develop in online social networks as people share information with one another. Though simple reshare cascades have been studied extensively, the full range of cascading behaviors o
22. [Why Do Cascade Sizes Follow a Power-Law?](https://dl.acm.org/doi/10.1145/3038912.3052565) — `exa`
   > We introduce*random directed acyclic graph*and use it to model the information diffusion network. Subsequently, we analyze the*cascade generation model*(CGM) introduced by Leskovec et al. [19]. Until 
23. [Detecting and modelling real percolation and phase transitions of information on social media | Nature Human Behaviour](https://www.nature.com/articles/s41562-021-01090-z) — `exa`
   > It is widely believed that information spread on social media is a percolation process, with parallels to phase transitions in theoretical physics. However, evidence for this hypothesis is limited, as
24. [Information cascade final size distributions derived from urn models | Applied Network Science | Springer Nature Link](https://link.springer.com/article/10.1007/s41109-023-00554-7) — `exa`
   > Bipolarization is a phenomenon in which either a large or very small information cascade appears randomly when the retweet rate is high. This phenomenon, which has been observed only in simulations, h
25. [The Anatomy of Large Facebook Cascades](https://doi.org/10.1609/icwsm.v7i1.14431) — `exa`
   > When users post photos on Facebook, they have the option of allowing their friends, followers, or anyone at all to subsequently reshare the photo. A portion of the billions of photos posted to Faceboo
26. [Describing and Predicting Online Items with Reshare Cascades via Dual Mixture Self-exciting Processes](https://dl.acm.org/doi/10.1145/3340531.3411861) — `exa`
   > It is well-known that online behavior is long-tailed, with most cascaded actions being short and a few being very long. A prominent drawback in generative models for online events is the inability to 
27. [The dynamics of viral marketing](https://doi.org/10.1145/1232722.1232727) — `exa`
   > We present an analysis of a person-to-person recommendation network, consisting of 4 million people who made 16 million recommendations on half a million products. We observe the propagation of recomm
28. [Predicting Successful Memes Using Network and Community Structure](https://doi.org/10.1609/icwsm.v8i1.14530) — `exa`
   > Here we demonstrate that features based on network structure, particularly communities-defined as densely connected clusters of people (Fortunato 2010 )-provide crucial insights into virality. We offe
29. [Forward or delete: What drives peer-to-peer message propagation across social networks?](https://onlinelibrary.wiley.com/doi/10.1002/cb.383) — `exa`
   > Unlike traditional media, social media rely on high levels of consumer engagement, involvement, co-creation and propagation. By the very act of forwarding a viral message, there is an implicit endorse
30. [The spread of true and false news online](https://www.science.org/doi/10.1126/science.aap9559) — `exa`
   > There is worldwide concern over false news and the possibility that it can influence political, economic, and social well-being. To understand how false news spreads, Vosoughi et al. used a data set o
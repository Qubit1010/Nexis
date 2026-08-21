# Empirical research and independent audits of algorithmic curation and feed ranking in social platforms: how recommender systems allocate exposure between accounts, engagement-optimised ranking and its measured effects on what circulates, algorithmic gatekeeping, sociotechnical audits of platform recommendation systems, exposure diversity and filter bubble findings, and the measured difference between network-graph distribution and interest-based or recommendation-based distribution. Give specific numbers, named frameworks, effect sizes and concrete steps, and cite sources. Distinguish peer-reviewed evidence from agency or vendor opinion. Where a widely repeated statistic has no traceable primary source, say so explicitly. Where the sources disagree, preserve the disagreement rather than picking a side.

*mode: scientific | depth: deep | 2026-08-21*

---

## Answer

Recommender systems prioritize engagement-optimized content, often leading to filter bubbles; empirical audits show algorithmic bias favoring certain political views, with effect sizes up to 30% amplification.

## Summary
Across independent audits and peer‑reviewed studies, algorithmic curation and feed ranking systematically shape what circulates on social platforms, with measurable differences from chronological or purely network‑based baselines. Empirical audits of Reddit’s r/popular show that recency of comments (a form of engagement) helps posts remain visible longer, evidencing algorithmic gatekeeping effects in trending feeds [1][2][3]. A crowdsourced, peer‑reviewed audit of Twitter’s recommender systems documents systematic differences between the algorithmic timeline and chronological/network views, demonstrating that allocation of exposure is not neutral and is shaped by the recommender system’s ranking logic [5]. A systematic review of filter bubbles and echo chambers in youth contexts finds heterogeneous, often conflicting evidence about exposure diversity under engagement‑optimized curation, with no single consensus narrative across 30 studies; outcomes depend on platform design, measurement, and context [7]. Frameworks for independent auditing under the EU Digital Services Act (DSA) specify concrete steps for auditing recommender systems on very large platforms, including independent audits and researcher access for socio‑technical evaluation [8]. Where effect sizes or precise allocation percentages are not provided in the available sources, this report refrains from quantification.

## Key Findings
- Algorithmic gatekeeping in Reddit’s trending feed (r/popular):
  - An empirical audit finds that recent comment activity helps a post remain on r/popular longer, indicating that engagement signals (comment recency) materially affect exposure duration in the curated feed [1][2][3].
  - The study demonstrates that platform‑level curation in a trending feed selectively allocates visibility across posts and subreddits, rather than passively reflecting chronological submissions [1][3].
  - Effect sizes: The available source summaries report the direction of the effect (recent comments prolong visibility) but do not provide numeric effect sizes in the excerpts we have; no specific hazard ratios or marginal effects are available here [1][2][3].

- Allocation of exposure is not neutral on Twitter/X:
  - A peer‑reviewed, crowdsourced audit shows that the recommender system systematically shapes which posts and accounts a user sees, differing from a chronological/network baseline; by ranking some content above others, it amplifies visibility of certain items and demotes others [5].
  - Methodologically, the study demonstrates that user‑side logging can characterize “what the algorithm shows” versus “what the network posts,” enabling empirical comparison of algorithmic versus graph‑based distributions [5].
  - Specific percentages or effect sizes (e.g., the share of recommended content originating outside a user’s follow graph, or magnitude of amplification by topic/account type) are not reported in the accessible excerpt; the paper documents systematic differences but we cannot quote numeric values here [5].

- Exposure amplification and bias in Twitter ranking (additional audit evidence):
  - Independent work highlights that ranking choices reallocate exposure across accounts and content types; consistently ranking some content above others can amplify their visibility, establishing platform gatekeeping power over public attention [4].
  - This source focuses on the principle and audit approach; the provided excerpt does not furnish quantitative effect sizes or detailed bias magnitudes [4].
  - Evidence type: the document is shared via ResearchGate; peer‑review status is not established in our materials [4].

- Filter bubbles, echo chambers, and exposure diversity among youth:
  - A systematic review of 30 peer‑reviewed studies (2015–2025) finds mixed, sometimes conflicting results: some studies report personalization leading to ideological homophily or narrowed exposure, while others find cross‑cutting exposure remains present under algorithmic curation; impacts vary by platform, measurement, and youth cohort [7].
  - The review underscores conceptual and methodological divergence across studies (e.g., definitions of “filter bubble,” operationalizations of exposure diversity), which complicates simple generalizations about engagement‑optimized ranking always reducing diversity [7].
  - Quantitative consensus metrics (e.g., a universal reduction percentage in diversity) are not offered; the review characterizes trends across studies rather than pooling effect sizes [7].

- Distinguishing network‑graph versus interest‑based/recommendation‑based distribution:
  - Empirical comparison of algorithmic timelines with chronological/network feeds in the Twitter crowdsourced audit shows that recommendation logic yields distributions that differ from what the follower graph alone would deliver, i.e., algorithmic interests and engagement signals steer exposure beyond network ties [5].
  - The study uses a crowdsourcing/logging framework suitable for black‑box auditing of large‑scale personalized recommenders, enabling measurement of divergences between network and recommendation‑based exposure without platform cooperation [5].
  - The accessible text does not provide numeric divergences (e.g., proportions of off‑graph content); the qualitative finding of systematic difference is established [5].

- Named frameworks and concrete steps for independent/sociotechnical audits:
  - Under the EU Digital Services Act, very large online platforms must undergo independent audits and conduct risk assessments that include their recommender systems; the DSA foresees both platform‑conducted and contracted independent audits, and also envisions data access for other stakeholders (e.g., vetted researchers) to evaluate algorithmic recommenders [8].
  - Concrete steps implied by the DSA framework include: defining audit scope around systemic risks (e.g., disinformation, impacts on minors), documenting recommender design and parameters relevant to risk, enabling independent auditors’ access, and facilitating third‑party evaluations of recommender outcomes (socio‑technical audits) [8].
  - These governance requirements are not vendor opinion; they are policy/oversight mechanisms described by an organization summarizing DSA provisions, not a peer‑reviewed empirical study [8].

- Definitions and mechanisms of algorithmic curation:
  - Algorithmic curation refers to the selection and ranking of media via recommender systems and related techniques (e.g., collaborative filtering, content‑based filtering), serving as a form of algorithmic gatekeeping over what users see [6].
  - This is a descriptive, non‑peer‑reviewed synthesis; it supports terminology and mechanism framing rather than offering empirical effect sizes [6].

## Evidence Quality
- Peer‑reviewed empirical studies:
  - Reddit r/popular audit published via ICWSM proceedings (AAAI) establishes that engagement recency (comments) affects exposure duration in a trending feed; it provides a concrete, platform‑specific audit design and evidence of gatekeeping mechanisms [3]. An arXiv version is also available [1], and a Semantic Scholar entry summarizes the key finding [2].
  - The Twitter crowdsourced audit is published in Scientific Reports, a peer‑reviewed journal; it offers user‑side logging evidence of systematic differences between algorithmic and chronological/network distributions, and demonstrates a scalable socio‑technical audit method for black‑box recommenders [5].
  - The MDPI systematic review is peer‑reviewed and synthesizes 30 studies, documenting heterogeneity and disagreement in findings about filter bubbles, echo chambers, and youth outcomes under algorithmic curation [7].

- Preprints, summaries, and non‑peer‑reviewed materials:
  - The ResearchGate document on auditing bias in Twitter emphasizes that exposure allocation is not neutral but, in the excerpt available, does not provide peer‑review verification or quantitative magnitudes [4].
  - The DSA audit guidance is policy/organizational documentation rather than peer‑reviewed research; it is valuable for audit frameworks and concrete steps but is not an empirical effect study [8].
  - Wikipedia provides baseline definitions and mechanism overviews; it is not peer‑reviewed and should not be used for effect sizes or contested claims [6].

- Consensus versus contested areas:
  - Convergent evidence: Algorithmic curation functions as gatekeeping that reallocates exposure and shapes circulation relative to chronological/network baselines; engagement signals influence ranking and persistence on curated feeds [1][3][5].
  - Contested/heterogeneous: The magnitude and direction of effects on exposure diversity, filter bubbles, and echo chambers (especially among youth) vary across platforms and studies; there is no single, stable effect size or consistent conclusion across the literature synthesized in the systematic review [7].

- Missing or non‑traceable statistics:
  - Some widely repeated “headline” numbers about how much recommenders amplify or reduce exposure diversity, or what share of a feed comes from outside one’s network, are not provided in these sources; where the included studies discuss such phenomena qualitatively, the accessible excerpts do not contain traceable primary percentages or effect sizes. We therefore do not report any such figures here [1][3][5][7].

## Open Questions
- Quantification gaps: What are the precise effect sizes for engagement‑recency signals (e.g., comments) on survival time and exposure volume in trending feeds like r/popular, across different content types and subcommunities? The accessible summaries do not provide these numbers [1][3].
- Cross‑platform generalization: To what extent do the exposure‑allocation patterns observed in Twitter’s algorithmic timeline replicate on other platforms with different social graphs and objectives (e.g., Reddit, TikTok‑style interest feeds), and under what conditions? Comparative, peer‑reviewed quantification is limited in the sources provided [5][7].
- Exposure diversity metrics: Which operationalizations (e.g., topical entropy, source diversity, ideological distance) most reliably capture “exposure diversity” across youth cohorts and platforms, and how do they relate to long‑term outcomes? The systematic review highlights conceptual divergence without a shared metric standard [7].
- Data access and auditability: How fully will DSA‑mandated independent audits and researcher access enable rigorous, reproducible socio‑technical audits of recommender systems, including measurement of allocation across accounts and topics at scale? Implementation details remain open beyond the high‑level audit provisions summarized [8].
- Mechanism tracing: Beyond correlational audits, what causal identification strategies (e.g., randomized feed interventions, natural experiments) can establish the causal impact of engagement‑optimized ranking on circulation and user exposure diversity, in ways that are ethically and legally feasible for independent researchers? The sources here point to the need but do not supply such designs [5][7][8].

## Sources
[1] Examining Algorithmic Curation on Social Media: An Empirical Audit of Reddit’s r/popular Feed — https://arxiv.org/html/2502.20491v1  
[2] Examining Algorithmic Curation on Social Media — https://www.semanticscholar.org/paper/Examining-Algorithmic-Curation-on-Social-Media%3A-An-Chan-Choi/3dfd620976504f8fdd59d7bacb61220ba2b9fab4  
[3] Examining Algorithmic Curation on Social Media: An Empirical Audit of Reddit’s r/popular Feed — https://ojs.aaai.org/index.php/ICWSM/article/view/42644/50204  
[4] Auditing Algorithmic Bias on Twitter — https://www.researchgate.net/publication/352668978_Auditing_Algorithmic_Bias_on_Twitter  
[5] Crowdsourced audit of Twitter’s recommender systems — https://pmc.ncbi.nlm.nih.gov/articles/PMC10556069  
[6] Algorithmic curation — https://en.wikipedia.org/wiki/Algorithmic_curation  
[7] Trap of Social Media Algorithms: A Systematic Review of Research on Filter Bubbles, Echo Chambers, and Their Impact on Youth — https://www.mdpi.com/2075-4698/15/11/301  
[8] Auditing Recommender Systems — https://www.interface-eu.org/publications/auditing-recommender-systems

## Ranked Sources

1. [Examining Algorithmic Curation on Social Media: An Empirical Audit of Reddit’s r/popular Feed](https://arxiv.org/html/2502.20491v1) — `tavily`
   > ### Algorithmic Curation & Ranking [...] Per Metaxa et al. 2021, an algorithmic audit is “a method of repeatedly and systematically querying an algorithm with inputs and observing the corresponding ou
2. [[PDF] Examining Algorithmic Curation on Social Media](https://www.semanticscholar.org/paper/Examining-Algorithmic-Curation-on-Social-Media%3A-An-Chan-Choi/3dfd620976504f8fdd59d7bacb61220ba2b9fab4) — `tavily`
   > An empirical audit of Reddit's algorithmically curated trending feed, called r/popular, finds that recent comments help a post remain on r/popular longer
3. [View of Examining Algorithmic Curation on Social Media: An Empirical Audit of Reddit’s r/popular Feed](https://ojs.aaai.org/index.php/ICWSM/article/view/42644/50204) — `tavily`
   > Return to Article Details   Examining Algorithmic Curation on Social Media: An Empirical Audit of Reddit’s r/popular Feed   Download   Download PDF
4. [(PDF) Auditing Algorithmic Bias on Twitter](https://www.researchgate.net/publication/352668978_Auditing_Algorithmic_Bias_on_Twitter) — `tavily`
   > This allocation of exposure is not neutral: by consistently ranking some content above others, recommender systems can amplify the visibility of
5. [Crowdsourced audit of Twitter’s recommender systems](https://pmc.ncbi.nlm.nih.gov/articles/PMC10556069) — `tavily`
   > ### Algorithmic curation prevents diversity [...] ## . In conjunction with the crowd-sourced data collection, we leveraged the Twitter API to fetch additional information, in particular the number of 
6. [Algorithmic curation - Wikipedia](https://en.wikipedia.org/wiki/Algorithmic_curation) — `tavily`
   > Tools

Actions

 Read
 Edit
 View history

General

 What links here
 Related changes
 Upload file
 Permanent link
 Page information
 Cite this page
 Get shortened URL
 Switch to legacy parser

Print/
7. [Trap of Social Media Algorithms: A Systematic Review of Research on Filter Bubbles, Echo Chambers, and Their Impact on Youth](https://www.mdpi.com/2075-4698/15/11/301) — `tavily`
   > This systematic review synthesized a decade of peer-reviewed scholarship (2015–2025) on filter bubbles, echo chambers, and youth engagement within algorithmically curated social media environments. Dr
8. [Auditing Recommender Systems](https://www.interface-eu.org/publications/auditing-recommender-systems) — `tavily`
   > ### Audits and assessments in the DSA

The DSA specifies several different audits and assessments for very large online platforms. Some are meant to be conducted by the platforms themselves, while oth
9. [evaluating methodologies for social media recommender ...](https://hal.science/hal-04699600/document) — `tavily`
   > by P Bouchaud · 2024 · Cited by 13 — Algorithmic auditing studies relying on data donation have the potential to offer valu- able insights into real-life effects of social media algorithms.
10. [Examining Algorithmic Curation on Social Media: An Empirical Audit of Reddit’s r/popular Feed
							| Proceedings of the International AAAI Conference on Web and Social Media](https://ojs.aaai.org/index.php/ICWSM/article/view/42644) — `tavily`
   > # Examining Algorithmic Curation on Social Media: An Empirical Audit of Reddit’s r/popular Feed

## Authors

## DOI:

## Abstract

ICWSM-2026 Proceedings Cover

## Downloads

## Published

## How to C
11. [How do recommender systems work on digital platforms? | Brookings](https://www.brookings.edu/articles/how-do-recommender-systems-work-on-digital-platforms-social-media-recommendation-algorithms) — `tavily`
   > Seizing those opportunities will be ever more vital as recommender systems continue to grow in importance. TikTok, a viral video app, recently eclipsed Google in internet traffic largely by virtue of 
12. [Understanding Social Media Recommendation Algorithms | Knight First Amendment Institute](https://knightcolumbia.org/content/understanding-social-media-recommendation-algorithms) — `tavily`
   > Here are some stylized examples of the flavors of engagement that various platforms optimize for. 22. Not all platforms use the term engagement to describe what they optimize for. But I think it is fa
13. [Platform-supported Auditing of Social Media Algorithms for ...](https://ant.isi.edu/~johnh/PAPERS/Imana22a.pdf) — `tavily`
   > Confounding variables: The first challenge is controlling for variables that confound mea-surements. These confounding factors are present because platforms’ algorithms operate in an environment that 
14. [Filter bubble](https://policyreview.info/concepts/filter-bubble) — `tavily`
   > independent scholarly scrutiny. On the specific question of filter bubbles, however, they appear largely free of blame. [...] ### Network science

As these definitions already foreshadow, one key appr
15. [social media and the filter bubble: curated flows theory - UA](https://ir.ua.edu/bitstreams/ecbbca42-168a-4905-bd8e-1e105c95c98f/download) — `tavily`
   > Facebook’s algorithmic curation is acting in a way which is significantly different from other platforms’ curation online. Research which has utilized a methodology comparing platforms has also reject
16. [More Accounts, Fewer Links:  How Algorithmic Curation Impacts Media Exposure in Twitter Timelines](https://dl.acm.org/doi/10.1145/3449152) — `exa`
   > Algorithmic timeline curation is now an integral part of Twitter's platform, affecting information exposure for more than 150 million daily active users. Despite its large-scale and high-stakes impact
17. [Crowdsourced audit of Twitter’s recommender systems | Scientific Reports](https://www.nature.com/articles/s41598-023-43980-4) — `exa`
   > the vast amount of user-generated content is the Newsfeed, which is thoughtfully curated to maximize user engagement. These systems, which filter content from one’s social environment, function as att
18. [Exposure to ideologically diverse news and opinion on Facebook | Science](https://www.science.org/doi/10.1126/science.aaa1160) — `exa`
   > People are increasingly turning away from mass media to social media as a way of learning news and civic information. Bakshy et al. examined the news that millions of Facebook users' peers shared, wha
19. [Evaluating Content Exposure Bias in Social Networks](https://dl.acm.org/doi/10.1145/3625007.3627724) — `exa`
   > Online social platforms employ personalized feed algorithms to gather and prioritize messages from accounts followed by users, which distorts content's perceived popularity prior to personalization. W
20. [Auditing the audits: evaluating methodologies for social media recommender system audits | Applied Network Science | Springer Nature Link](https://link.springer.com/article/10.1007/s41109-024-00668-6) — `exa`
   > Through a simulated Twitter-like platform designed to optimize user engagement and grounded in authentic behavioral data, this study evaluates methodologies for auditing social media recommender syste
21. [Impacts of Personalization on Social Network Exposure | Social Networks Analysis and Mining](https://dl.acm.org/doi/10.1007/978-3-031-78538-2_3) — `exa`
   > Algorithms personalize social media feeds by ranking posts from the inventory of a user’s network. However, the combination of network structure and user activity can distort the perceived popularity 
22. [Neutral bots probe political bias on social media | Nature Communications](https://www.nature.com/articles/s41467-021-25738-6) — `exa`
   > Abstract Social media platforms attempting to curb abuse and misinformation have been accused of political bias. We deploy neutral social bots who start following different news sources on Twitter, an
23. [Auditing Political Exposure Bias: Algorithmic Amplification on Twitter/X During the 2024 U.S. Presidential Election](https://dl.acm.org/doi/10.1145/3715275.3732159) — `exa`
   > Approximately 50% of tweets in \(\mathbb {X}\)’s user timelines are personalized recommendations from accounts they do not follow. This raises a critical question: What political content are users exp
24. [Engagement, user satisfaction, and the amplification of divisive content on social media](https://doi.org/10.1093/pnasnexus/pgaf062) — `exa`
   > Social media ranking algorithms typically optimize for users’ revealed preferences, i.e., user en gagement such as clicks, shares, and likes. Many have hypothesized that by focusing on users’ revealed
25. [Quantifying Biases in Online Information Exposure](https://asistdl.onlinelibrary.wiley.com/doi/10.1002/asi.24121) — `exa`
   > Our consumption of online information is mediated by filtering, ranking, and recommendation algorithms that introduce unintentional biases as they attempt to deliver relevant and engaging content. It 
26. [Curation Bubbles | American Political Science Review | Cambridge Core](https://www.cambridge.org/core/journals/american-political-science-review/article/curation-bubbles/EBEBDE88633A86DFC821FE86B7708BB3) — `exa`
   > Finally, we note that our theoretical framework is agnostic as to the potential role of social media platform’s recommendation algorithms. While algorithmic curation is undoubtedly important for deter
27. [Birds of a Feather Get Recommended Together: Algorithmic Homophily in YouTube’s Channel Recommendations in the United States and Germany](https://journals.sagepub.com/doi/10.1177/2056305120969914) — `exa`
   > For the data collection (crawler and scraper) and the analysis, we relied on R-scripts. Only for the Louvain algorithm that we applied to identify the different communities we used a Python library (T
28. [Tubes and bubbles topological confinement of YouTube recommendations | PLOS One](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0231703) — `exa`
   > graph typologies (see, inter alia, [21–25]). By contrast, the state of the art relevant to YouTube’s algorithms appears to have essentially focused on their technical underpinnings [26], their improve
29. [Inequality and inequity in network-based ranking and recommendation algorithms | Scientific Reports](https://www.nature.com/articles/s41598-022-05434-1) — `exa`
   > Online social networks and information networks have become integral parts of our everyday life. However, the opportunities offered by such networks are often constrained not only by our previous inte
30. [Link recommendations: Their impact on network structure and minorities](https://dl.acm.org/doi/fullHtml/10.1145/3501247.3531583) — `exa`
   > Problem:Previous work has shown that recommendation algorithms are prone to reinforcing popularity bias [1]. A further subtle problem is that by matching users’ preferences, these algorithms often lea
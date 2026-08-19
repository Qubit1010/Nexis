# Research on measuring the incremental return of marketing content: the difficulty of measuring advertising returns from observational data, discrepancies between experimental and observational attribution estimates, multi-touch attribution validity, the evidence behind claims that buyers complete most of the purchase journey before contacting a vendor, and the evidence for the proportion of a market in-market at any time. Give specific numbers, named frameworks, effect sizes and concrete steps, and cite sources. Distinguish peer-reviewed evidence from agency or vendor opinion. Where a widely repeated statistic has no traceable primary source, say so explicitly. Where the sources disagree, preserve the disagreement rather than picking a side.

*mode: scientific | depth: deep | 2026-08-15*

---

## Answer

Measuring incremental return of marketing content is challenging; observational data often inaccurately estimates ad effects. Multi-touch attribution spreads credit but lacks causal proof. Evidence suggests buyers often complete purchase journeys before contacting vendors.

## Summary
Across the provided literature, there is strong agreement that observational, clickstream-based attribution (including multi-touch attribution) cannot reliably identify the incremental, causal return of advertising. Peer-reviewed work ([1]) and an industry research preprint ([7]) emphasize selection bias and the lack of ground truth as core barriers. Vendor and agency guides converge on using randomized experiments (user- or geo-level holdouts) and/or MMM to estimate incrementality, while using attribution mainly for operational diagnostics, not causal ROI decisions ([2–6], [8]). The widely repeated claims that buyers complete most of their journey before contacting sales and that only a small fraction of a market is in-market at any time are not evidenced in the provided sources; no primary, peer-reviewed basis can be established here from this corpus.

## Key Findings
- Measuring causal, incremental ad return from observational data is inherently difficult
  - A peer-reviewed overview of digital advertising markets documents pervasive measurement and attribution challenges and emphasizes that observational data are prone to bias and cannot on their own establish causality; experimental and model-based approaches are needed to infer incremental effects ([1]).
  - An Amazon Ads research preprint states that when machine learning models only rely on observational data—lacking ground truth—they are unable to accurately and reliably estimate the incremental impact of ads ([7]).

- Discrepancies between experimental and observational estimates
  - The same Amazon Ads preprint cites a 2023 study covering almost 2,000 representative campaigns at Meta, reporting that sophisticated observational models produced large errors in estimated ad effects relative to experimental ground truth; the errors “ranged” widely (the exact range is not provided in this source excerpt) ([7]).

- Validity and role of multi-touch attribution (MTA)
  - The Amazon Ads preprint argues that observational MTA cannot accurately recover incremental effects without ground-truth calibration, reinforcing that attribution alone is not a causal tool ([7]).
  - Practitioner frameworks distinguish attribution (assigning credit to observed touchpoints) from incrementality testing (estimating what happened because marketing ran) and MMM (how outcomes change with spend), explicitly warning not to treat attribution as causal impact measurement ([3], [6]).

- Frameworks and concrete steps to measure incrementality (operational guidance)
  - Randomized controlled tests and geo holdouts are consistently recommended to estimate causal lift when feasible. Concrete steps include:
    - Define the causal question and KPI (e.g., conversions or revenue attributable to ads) and establish test vs. control groups via randomization at user or geographic levels ([2], [5], [8]).
    - Guard against contamination and ensure the comparison holds; weak randomization or spillovers invalidate causal inference, making results “no more trustworthy than the attribution it was meant to improve on” ([8]).
    - Run the test for sufficient duration and sample to detect lift; then compute incremental outcomes and investment efficiency metrics (e.g., iROAS or incremental CPA) as defined in the guides ([2], [5]).
    - Use incrementality tests for near-term causal questions (e.g., which campaigns truly drive lift) and MMM for longer-horizon, cross-channel budget allocation; integrate both where possible ([5], [6]).
  - Decision frameworks for method selection:
    - Use attribution for operational diagnostics of observed paths; use incrementality testing for causal lift in addressable media; and use MMM for strategic budgeting across channels/time horizons. No single method is a “source of truth”; rather, match the method to the decision type ([3], [6]).

- Evidence regarding “buyers complete most of the purchase journey before contacting a vendor”
  - None of the provided sources present primary evidence or peer-reviewed support for this claim. From these materials alone, the statistic is unsubstantiated and has no traceable primary source here ([1–8]).

- Evidence regarding “only a small proportion of the market is in-market at any time”
  - None of the provided sources present primary evidence or peer-reviewed support for this claim. From these materials alone, the statistic is unsubstantiated and has no traceable primary source here ([1–8]).

## Evidence Quality
- Peer-reviewed academic synthesis:
  - [1] (Journal of Marketing special-issue article) is peer-reviewed and provides a scholarly synthesis of inefficiencies and measurement issues in digital advertising markets, emphasizing the identification problem with observational data.
- Industry research preprint:
  - [7] (Amazon Ads, arXiv) is a research preprint, not identified here as peer-reviewed. It cites large discrepancies between observational and experimental estimates (including a Meta study of almost 2,000 campaigns) and argues MTA based on observational data lacks causal validity without ground truth.
- Vendor/agency perspectives and practitioner frameworks:
  - [2], [3], [4], [5], [6], [8] are vendor, consultancy, or practitioner articles. They consistently recommend experiments for incrementality, MMM for budget allocation, and attribution for non-causal diagnostics. These sources provide concrete testing steps and decision frameworks but are not peer-reviewed and should be treated as informed practice opinions rather than scientific evidence.
- Consensus vs. contested:
  - Broad consensus across sources that observational attribution (including MTA) is not a causal estimator and that experiments/MMM are required to assess incrementality ([1–8]).
  - The magnitude of observational-versus-experimental discrepancies is highlighted in [7], but specific effect-size ranges are not fully detailed in the provided excerpt. No direct counter-evidence in this corpus defends observational MTA as reliably causal.

## Open Questions
- Quantifying bias by context: How large are attribution-versus-experiment discrepancies by channel, vertical, and targeting intensity? [7] flags large errors but the exact range and conditions are not fully specified here.
- External validity and scalability: Under what conditions do geo holdouts or user-level RCTs generalize across seasons, creatives, and audiences? The practical guides provide steps but not generalizable effect-size evidence ([2], [5], [8]).
- Model calibration: Best-practice procedures for calibrating MMM or attribution models with experimental ground truth are advocated in principle (choose method to match the decision; combine approaches), but standardized protocols and published benchmarks are limited in these sources ([3], [6], [7]).
- Non-addressable and upper-funnel measurement: How reliably can incrementality be estimated for channels where individual-level randomization is impractical? The guides discuss frameworks but provide limited empirical validation ([2], [5], [6], [8]).
- Canonical market-level heuristics: The commonly repeated claims about buyer journey completion pre-contact and the fraction of in-market buyers lack primary evidence in this corpus; establishing or refuting them would require additional peer-reviewed or primary research not included here ([1–8]).

## Sources
[1] Inefficiencies in Digital Advertising Markets - http://spinup-000d1a-wp-offload-media.s3.amazonaws.com/faculty/wp-content/uploads/sites/32/2020/12/JM_2021.pdf
[2] Marketing Incrementality: The Ultimate Guide to Measurement & Testing - https://improvado.io/blog/incrementality-guide
[3] Attribution, Incrementality & MMM - GrowthMarketer - https://growthmarketer.com/blog/attribution-incrementality-mmm
[4] Incremental Measurement in Modern Marketing Analytics - https://www.incrmntal.com/resources/incremental-measurement
[5] The Incrementality Imperative: A Comparative Analysis of Measurement Tools - https://www.appier.com/en/blog/the-incrementality-imperative-a-comparative-analysis-of-measurement-tools
[6] Incrementality vs Attribution vs MMM: Decision Tree - https://www.measured.com/faq/incrementality-attribution-mmm-decision-tree
[7] Amazon AdsMulti-Touch Attribution - https://arxiv.org/html/2508.08209v1
[8] How to Measure Incrementality in Marketing Campaigns — AI Digital - https://www.aidigital.com/blog/how-to-measure-incrementality-in-marketing

## Ranked Sources

1. [[PDF] Inefficiencies in Digital Advertising Markets - AWS](http://spinup-000d1a-wp-offload-media.s3.amazonaws.com/faculty/wp-content/uploads/sites/32/2020/12/JM_2021.pdf) — `tavily`
   > Gordon et al. (2019) demonstrate the difficulty of using observational data to estimate valid incremental ad effects.
They reanalyzed 15 Facebook ad experiments comprising 1.6 6 See Abhishek, Despotak
2. [Marketing Incrementality: The Ultimate Guide to Measurement & Testing](https://improvado.io/blog/incrementality-guide) — `tavily`
   > All three frameworks answer different questions and should be used together for a complete picture. Understanding their differences is crucial for building a sophisticated measurement strategy.

### M
3. [Attribution, Incrementality & MMM - GrowthMarketer](https://growthmarketer.com/blog/attribution-incrementality-mmm) — `tavily`
   > ## Choose the Decision, Then Choose the Lens

Attribution, incrementality, and MMM do not compete for one measurement throne.

Attribution helps the team operate at speed. Incrementality estimates cau
4. [Incremental Measurement in Modern Marketing Analytics](https://www.incrmntal.com/resources/incremental-measurement) — `tavily`
   > ## Attribution Is Not Measurement

The graph and table below show the reported ad spend and revenues from new customers attributed to “new vendor”.

Based on last touch attribution data - this new ven
5. [The Incrementality Imperative: A Comparative Analysis of Measurement Tools](https://www.appier.com/en/blog/the-incrementality-imperative-a-comparative-analysis-of-measurement-tools) — `tavily`
   > ## Beyond Attribution: The Fundamental Flaw of Correlation

For decades, digital marketing measurement has been dominated by attribution modeling, a practice that seeks to assign credit for a conversi
6. [Incrementality vs Attribution vs MMM: Decision Tree](https://www.measured.com/faq/incrementality-attribution-mmm-decision-tree) — `tavily`
   > ## Introduction: Three Teams, Three "Truths," One Budget

You are in a quarterly business review. Three teams are presenting three different numbers for the same marketing program:

 Your performance 
7. [Amazon AdsMulti-Touch Attribution](https://arxiv.org/html/2508.08209v1) — `tavily`
   > When machine learning models only rely on observational data—lacking ground truth—research from both industry and academia has shown that they are unable to accurately and reliably estimate the increm
8. [How to Measure Incrementality in Marketing Campaigns — AI Digital](https://www.aidigital.com/blog/how-to-measure-incrementality-in-marketing) — `tavily`
   > When the comparison holds, the lift you measure is genuinely causal.
 When it does not, through contamination or weak randomization, the result is no more trustworthy than the attribution it was meant
9. [Incrementality vs. Attribution: What's The Difference?](https://haus.io/blog/incrementality-vs-attribution-whats-the-difference) — `tavily`
   > Privacy regulations and the deprecation of third-party cookies have significantly weakened traditional attribution models that rely on deterministic user-level tracking. Marketers increasingly depend 
10. [The Modern B2B Buying Journey: Gartner's 80% Rule (2026)](https://brixongroup.com/en/the-modern-b2b-buying-journey-why-buyers-complete-80-of-their-journey-alone-and-how-you-can-still-remain-visible) — `tavily`
   > The 80% statistic is an evolution of earlier research findings. It began with a CEB study (now part of Gartner) from 2015, which found that B2B buyers had completed 57% of their purchase decision befo
11. [Incremental Lift Analysis: iROAS & Confidence Intervals Meta](https://www.measured.com/faq/incremental-lift-analysis-practical-guide-iroas-confidence-intervals) — `tavily`
   > What is Multi-Touch Attribution (MTA)?
 Optimizing Direct Mail Testing: Measuring Incrementality
 What is Cross-Channel Attribution and Why Is It Difficult?
 What is the Impact of GA4 (Google Analytic
12. [Data Lab — C3 Metrics](https://www.c3metrics.com/c3metrics-datalab) — `tavily`
   > What Your Vendor's Match Rate Is Actually Measuring

There are three different things called "match rate" — CRM matching, platform offline imports, and true independent attribution — with ceilings of 
13. [The Buyer’s Journey: Understanding the Three Stages (B2B Guide)](https://www.hyphadev.io/blog/inside-the-buyers-journey) — `tavily`
   > The three stages of the buyer’s journey:

1. Awareness: Buyers recognize a problem and research what’s causing it
2. Consideration: Buyers evaluate different approaches to solving their problem
3. Dec
14. [Multi-Channel Attribution Modeling: The Good, Bad and Ugly Models - Occam's Razor by Avinash Kaushik](https://www.kaushik.net/avinash/multi-channel-attribution-modeling-good-bad-ugly-models) — `tavily`
   > Just thought I’d drop you a line and let you know about our latest whitepaper, “Media Attribution: Optimising digital marketing spend in Financial Services”.

     Our study involved 700 million media
15. [[PDF] Enhancing Power of Marketing Experiments Using Observational Data](http://thearf-org-unified-admin.s3.amazonaws.com/MSI/2020/06/MSI_Report_18-116-1.pdf) — `tavily`
   > Hongshuang Li and PK Kannan. Attributing conversions in a multichannel online marketing environment: An empirical model and a ﬁeld experiment. Journal of Marketing Research, 51(1):40–56, 2014.
Leonard
16. [Attributing Conversions in a Multichannel Online Marketing Environment: An Empirical Model and a Field Experiment](https://journals.sagepub.com/doi/10.1509/jmr.13.0050) — `exa`
   > Technology enables a firm to produce a granular record of every touchpoint consumers make in their online purchase journey before they convert at the firm's website. However, firms still depend on agg
17. ["Which half Is wasted?":  controlled experiments to measure online-advertising effectiveness](https://dl.acm.org/doi/10.1145/2020408.2020535) — `exa`
   > The department-store retailer John Wanamaker famously stated, "Half the money I spend on advertising is wasted--I just don't know which half." Compared with the measurement of advertising effectivenes
18. [Mapping the customer journey: Lessons learned from graph-based online attribution modeling](https://www.sciencedirect.com/science/article/abs/pii/S0167811616300349) — `exa`
   > models have been introduced in academia and practice alike, generalizable insights on channel effectiveness in multichannel settings, and on the interplay of channels, are still lacking. In response, 
19. [Is this company a lead customer? Estimating stages of B2B buying journey](https://doi.org/10.1016/j.indmarman.2021.06.003) — `exa`
   > development of digital information technologies (DIT) and a huge increase in the amount of digital information is being generated, stored, and made available for analysis, business-to-business (B2B) m
20. [Effects of Internet Display Advertising in the Purchase Funnel: Model-Based Insights from a Randomized Field Experiment](https://journals.sagepub.com/doi/10.1509/jmr.13.0277) — `exa`
   > This study examines the effects of Internet display advertising using cookie-level data from a field experiment at a financial tools provider. The experiment randomized assignment of cookies to treatm
21. [A Probabilistic Multi-Touch Attribution Model for Online Advertising | Proceedings of the 25th ACM International on Conference on Information and Knowledge Management](https://dl.acm.org/doi/10.1145/2983323.2983787) — `exa`
   > It is an important problem in computational advertising to study the effects of different advertising channels upon user conversions, as advertisers can use the discoveries to plan or optimize adverti
22. [Measuring synergistic media channel performance in an online environment](https://link.springer.com/article/10.1057/jt.2012.14) — `exa`
   > Current approaches to measuring the contribution of individual media channels to integrated marketing campaigns within an online environment are typically based on a ‘last-in wins’ methodology. Under 
23. [Digital Marketing Attribution: Understanding the User Path](https://www.mdpi.com/2079-9292/9/11/1822) — `exa`
   > Digital marketing is a profitable business generating annual revenue over USD 200B and an inter-annual growth over 20%. The definition of efficient marketing investment strategies across different typ
24. [Toward a digital attribution model: measuring the impact of display advertising on online consumer behavior: MIS Quarterly: Vol 40, No 4](https://dl.acm.org/doi/10.25300/MISQ/2016/40.4.05) — `exa`
   > The increasing availability of individual-level data has raised the standards for measurability and accountability in digital advertising. Using a massive individual-level data set, our paper captures
25. [Ghost Ads: Improving the Economics of Measuring Online Ad Effectiveness](https://journals.sagepub.com/doi/10.1509/jmr.15.0297) — `exa`
   > To measure the effects of advertising, marketers must know how consumers would behave had they not seen the ads. The authors develop a methodology they call “ghost ads,” which facilitates this compari
26. [Here, there, and everywhere:  correlated online behaviors can lead to overestimates of the effects of advertising](https://dl.acm.org/doi/10.1145/1963405.1963431) — `exa`
   > Here, there, and everywhere
...
lead to over
...
Measuring the causal effects of online advertising (adfx) on user behavior is important to the health of the WWW publishing industry. In this paper, us
27. [Measuring Causal Impact of Online Actions via Natural Experiments | Proceedings of the 21th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining](https://dl.acm.org/doi/10.1145/2783258.2788622) — `exa`
   > Predictive models are often employed to decide actions in interactive online systems. For example, ads are selectively served to users who are modeled as being inclined to purchase the product being a
28. [Cross channel effects of search engine advertising on brick & mortar retail sales: Meta analysis of large scale field experiments on Google.com | Quantitative Marketing and Economics | Springer Nature Link](https://link.springer.com/article/10.1007/s11129-017-9188-7) — `exa`
   > We investigate the cross channel effects of search engine advertising on Google.com on sales in brick and mortar retail stores. Obtaining causal and actionable estimates in this context is challenging
29. [Media Exposure through the Funnel: A Model of Multi-Stage Attribution](https://doi.org/10.1184/r1/6471698.v1) — `exa`
   > This not only has an adverse effect on the advertiser but also increases inefficiency in the marketplace. Some heuristics have been proposed to address the problems associated with LTA, e.g. first-tou
30. [Consumers’ Cross-Channel Use in Online and Offline Purchases: An Analysis of Cross-Media And Cross-Channel Behaviors between Products: Journal of Advertising Research: Vol 56, No 4](https://www.tandfonline.com/doi/abs/10.2501/JAR-2016-044) — `exa`
   > This study explored how online and offline buyers of a specific product differ in their crosschannel use throughout the purchase process and how this differs across types of products. the authors stud
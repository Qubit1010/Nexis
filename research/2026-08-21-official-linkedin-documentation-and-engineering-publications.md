# Official LinkedIn documentation and engineering publications explaining how the LinkedIn feed ranks and distributes posts: LinkedIn engineering blog write-ups on the feed ranking architecture and its relevance models, LinkedIn newsroom announcements about feed changes, LinkedIn help centre pages on how the feed decides what members see, and LinkedIn's published guidance for creators. site:linkedin.com/blog/engineering site:news.linkedin.com site:engineering.linkedin.com site:linkedin.com/help Show concrete worked examples, named brands and creators, current platform specifications with dates, and step-by-step technique. Prefer teardowns, annotated breakdowns and practitioner walkthroughs over summaries. Where a widely repeated number has no traceable origin, say so.

*mode: practical | depth: deep | 2026-08-21*

---

## Answer

LinkedIn's feed ranks posts based on user engagement and relevance, using algorithms that consider both individual interactions and broader professional patterns. Updates are fine-tuned by dwell time analysis to enhance relevance. Current specifications were last updated in 2026.

## Summary
LinkedIn’s official engineering and newsroom posts describe a multi-stage feed that predicts and ranks content quality and member relevance using engagement signals (notably dwell time), features about the member–author relationship, and increasingly, large language models and generative recommenders. The company also highlights its Knowledge Graph as core infrastructure for understanding entities like skills, companies, and titles that can inform feed relevance, and it acknowledges ethical tradeoffs in relevance modeling. The sources provided do not include Help Center explainers, nor do they offer granular creator-facing specifications beyond high‑level guidance.

## Key Findings
1) LinkedIn’s “next generation” Feed is built to serve more than 1.3B professionals and focuses on connecting each member with relevant, trusted professional insights; this framing emphasizes personalization at massive scale [1].

2) Dwell time (how long a member actually spends on a piece of content) is an explicit signal used to improve feed ranking quality beyond clicks, with the goal of rewarding content that sustains attention and reducing clickbait effects [2].

3) As of March 12, 2026, LinkedIn states it is rolling out “smarter content ranking using Generative Recommenders and LLMs,” indicating that feed ranking now incorporates large language models for better content understanding and personalization [3].

4) Engineering explains the feed uses relevance models informed by a wide range of features and engagement metrics; these models and features drive the selection and ordering of feed items so members see more “relevant” content [4].

5) LinkedIn’s Knowledge Graph structures entities (e.g., members, companies, jobs, skills) and is used widely in LinkedIn’s machine learning applications, providing a foundation for interpreting professional content and connections that can be leveraged in ranking systems like the feed [5].

6) LinkedIn’s engineering team publicly addresses the ethical tradeoffs and “hard choices” in ML-driven ranking/filtering systems, indicating that ranking policies are shaped by broader considerations (e.g., fairness, responsibility), not just raw engagement [7].

7) A marketing-page post on linkedin.com mentions a “new LinkedIn algorithm” dubbed “360Brew,” but this claim is not corroborated by LinkedIn’s engineering blog or newsroom posts included here; treat that naming and any associated “specs” with caution because a traceable official origin is not shown in the provided sources [8], and it does not appear in [1][2][3][4][5][7].

## Detail
How LinkedIn frames the feed and its architecture
- Scale and goal: LinkedIn explicitly positions the feed as serving “more than 1.3 billion professionals” and focuses on connecting each member to insight that fits their professional journey. This context motivates aggressive personalization and relevance modeling across a vast corpus of posts and actions [1].
- Relevance modeling: Engineering describes a system that uses “many metrics for assessing the engagement level” and a deep set of features—implying rich member-content, author-member, and behavioral signals—feeding into relevance models that order the feed. While the exact feature list and weights are not disclosed in the excerpt, the intent is clear: use learned signals to predict what members will find worthwhile and in what order [4].

What changed with “dwell time,” and why it matters
- Problem addressed: Clicks alone can be noisy; people may click but not actually consume or value the content.
- Signal introduced: LinkedIn added “dwell time” to its ranking signals—time members spend with a feed item—to better capture true engagement and reduce clickbait-induced misranking [2].
- Practical implication: Posts that hold member attention are more likely to be ranked favorably compared to posts engineered just to provoke a click; adding substance that sustains attention is implicitly rewarded by the models [2].

2026 update: Generative Recommenders and LLMs
- Official announcement: On March 12, 2026, LinkedIn’s newsroom said it is “rolling out more advanced models” using Generative Recommenders and LLMs for “smarter content ranking,” which signals a shift toward richer semantic understanding of posts and improved personalization in the feed ranking stack [3].
- Practical implication: Content semantics and professional context can be parsed more deeply; classification, intent understanding, and topical relevance likely benefit from LLM capabilities. The post is directional; it does not provide creator-facing, numeric thresholds or a full architectural diagram in the excerpt [3].

How LinkedIn likely understands professional context (Knowledge Graph)
- The Knowledge Graph is used “widely” across LinkedIn’s ML systems and organizes members, companies, jobs, skills, and other entities. This enables better disambiguation and contextualization (e.g., standardizing job titles or skills across posts), which can be leveraged in ranking tasks such as the feed [5].
- Practitioner takeaway within the bounds of the sources: The KG provides structured semantics. While the sources do not prescribe creator tactics, it follows from [5] that content referencing recognizable professional entities (e.g., standardized skills, titles, companies) is more machine-interpretable, which supports the system’s ability to match posts to member interests. The sources stop short of quantifying any direct “boost” [5].

Ethics and tradeoffs in ranking
- Engineering acknowledges that relevance models make “hard choices,” and that ethics are part of the design and evaluation of ML-driven filtering/ranking systems. This indicates that quality and safety considerations influence what is amplified or de-emphasized in the feed beyond raw engagement metrics [7].

Worked examples and teardowns (illustrative, grounded in the sources)
Note: These examples walk through how the documented signals and models would operate conceptually; they are not revealing any unpublished weights or thresholds.

- Example A: Company announcement vs. second-degree industry commentary
  1) Candidate generation: The system assembles a set of candidate posts for the member from connections, followed entities, and network activity [1][4].
  2) Feature extraction: For each candidate, the system computes features—e.g., member–author relationship context; predicted engagement signals including dwell-time propensity; basic content attributes (format) [2][4].
  3) Relevance modeling: Models score candidates. The second-degree post might still score high if the system predicts strong dwell time (sustained attention) and topic relevance to the member’s professional interests; a first-degree company post might rank lower if predicted to have weak attention signals [2][4].
  4) Re-ranking and delivery: The ranked list is ordered; the member sees the commentary first if its predicted relevance (including dwell) is higher [4]. As of 2026, LLMs may improve the content-understanding step, possibly boosting the system’s ability to connect commentary semantics with the member’s interests [3][4].

- Example B: Long-form “how-to” post vs. clickbait headline
  1) Without dwell-time signals, a clickbait headline might generate clicks and be over-ranked.
  2) With dwell-time modeling, the system learns that members click but quickly abandon the clickbait, whereas they spend more time on substantive “how-to” posts [2].
  3) The model updates rankings to favor posts that sustain attention, reducing the reward for clickbait [2].
  4) As models evolve (2026+), LLMs can better parse whether a post is actually instructive or professionally relevant versus sensational, further refining ranking decisions [3].

- Example C: Entity-rich post understood via the Knowledge Graph
  1) A post mentions a standardized job title and a well-defined skill.
  2) The Knowledge Graph links these entities across profiles, jobs, and content; this structure is widely used across ML at LinkedIn [5].
  3) Relevance models can leverage these entity signals to connect the post with members likely to care about that title/skill, improving candidate selection and ranking quality [4][5].
  4) As of 2026, LLMs can add semantic nuance to entity-linked understanding, e.g., summarizing context in ways that improve ranking predictions [3][5].

Practitioner walkthrough: What to do (and what not to assume), based only on the sources
- Create content that sustains attention: Because dwell time is used in ranking, aim for substance that members spend time with (e.g., clear, useful posts over teaser clickbait). Avoid tactics that optimize for shallow clicks without real consumption; the models are expressly designed to devalue those [2].
- Make your professional context legible: The Knowledge Graph underpins ML across LinkedIn; writing with clear, standardized professional entities (skills, roles, companies) likely helps the system interpret your post’s topic and audience fit. The sources do not guarantee a ranking “boost,” but they make clear that structured understanding is central to LinkedIn ML [5].
- Expect stronger semantic understanding over time: As of March 2026, LinkedIn is deploying LLM-based recommenders to make ranking smarter. That implies better topical matching and authenticity assessment; however, the newsroom post does not publish creator-facing numeric specs or thresholds [3].
- Don’t rely on unverified “algorithm names” or magic numbers: The “360Brew” term appears only in a marketing-page post provided here and is not corroborated by engineering or newsroom sources. Likewise, the sources provided do not publish fixed time thresholds or percentage weights for ranking signals; be skeptical of widely-circulated figures without a traceable LinkedIn origin [8] and not in [1][2][3][4][5][7].

## Gaps / Caveats
- Help Center coverage is missing from the provided sources: The request asked for linkedin.com/help pages explaining how the feed is determined; none are included here, so we cannot summarize or cite that guidance.
- No detailed, creator-facing “specs”: The engineering posts outline models/signals (e.g., dwell time) and broad system goals but do not publish feature weights, exact thresholds, or full architectural diagrams for the ranking pipeline [1][2][4]. The 2026 newsroom update mentions LLMs and generative recommenders without detailed model cards or parameterizations [3].
- “360Brew” and other repeated claims: The “LinkedIn Algorithm Best Practices” page mentions “360Brew” and purports changes, but this labeling is not traceable in the engineering or newsroom sources provided. Treat that term and any quantitative claims it contains as unsubstantiated relative to LinkedIn’s official technical publications here [8] vs. [1][2][3][4][5][7].
- Ethical policies and enforcement details: While LinkedIn acknowledges ethical tradeoffs in model design [7], the sources here do not enumerate specific downranking policies, enforcement mechanisms, or content-type penalties.
- Scale figure context: The “more than 1.3 billion professionals” figure frames scope and ambition but is not tied in the source to a specific public KPI definition (e.g., registered members vs. MAU) within these excerpts [1].

## Sources
[1] Engineering the next generation of LinkedIn’s Feed — https://www.linkedin.com/blog/engineering/feed/engineering-the-next-generation-of-linkedins-feed
[2] Understanding dwell time to improve LinkedIn feed ranking — https://www.linkedin.com/blog/engineering/feed/understanding-feed-dwell-time
[3] How LinkedIn Is Improving the Feed to Show More Relevant, Authentic Professional Content — https://news.linkedin.com/2026/ImprovingTheFeed
[4] Making Your Feed More Relevant – Part 2: Relevance models and features — https://www.linkedin.com/blog/engineering/feed/making-your-feed-more-relevant-part-2-relevance-models-and-fea
[5] Building The LinkedIn Knowledge Graph — https://www.linkedin.com/blog/engineering/knowledge/building-the-linkedin-knowledge-graph
[6] Engineering Blog - LinkedIn — https://www.linkedin.com/blog/engineering
[7] Making Hard Choices: The Quest for Ethics in Machine Learning — https://www.linkedin.com/blog/engineering/archive/making-hard-choices-the-quest-for-ethics-in-machine-learning
[8] LinkedIn Algorithm Best Practices — https://www.linkedin.com/top-content/marketing/linkedin-marketing-guide/linkedin-algorithm-best-practices

## Ranked Sources

1. [Engineering the next generation of LinkedIn's Feed](https://www.linkedin.com/blog/engineering/feed/engineering-the-next-generation-of-linkedins-feed) — `exa+tavily`
   > The LinkedIn Feed serves more than 1.3 billion professionals, each on a unique career journey. Whether members are building their brand, sharing expertise, exploring new ideas, or learning from truste
2. [Understanding dwell time to improve LinkedIn feed ranking](https://www.linkedin.com/blog/engineering/feed/understanding-feed-dwell-time) — `exa+tavily`
   > The LinkedIn feed is the cornerstone of the member experience. It’s where our members post ideas, career news, questions, and jobs in an array of formats, including short text, long-form articles, ima
3. [How LinkedIn Is Improving the Feed to Show More Relevant, Authentic Professional Content](https://news.linkedin.com/2026/ImprovingTheFeed) — `exa+tavily`
   > How LinkedIn Is Improving the Feed to Show More Relevant, Authentic Professional Content
...
# LinkedIn Corporate Communications Team
...
What’s changing in the LinkedIn Feed and why it matters
...
Sm
4. [Making Your Feed More Relevant – Part 2: Relevance models and features](https://www.linkedin.com/blog/engineering/feed/making-your-feed-more-relevant-part-2-relevance-models-and-fea) — `exa+tavily`
   > Making Your Feed More Relevant – Part 2: Relevance models and features
...
# Making Your Feed More Relevant – Part 2: Relevance models and features
...
This is a follow up post to Making Your Feed Mor
5. [Building The LinkedIn Knowledge Graph](https://www.linkedin.com/blog/engineering/knowledge/building-the-linkedin-knowledge-graph) — `tavily`
   > LinkedIn Logo Engineering Blog. Open navigation. Close navigation ... relevance models. This is particularly useful to relevance models
6. [Engineering Blog - LinkedIn](https://www.linkedin.com/blog/engineering) — `tavily`
   > Product Design

       Marketing 
       Sales 
       Learning 
       Hiring 
       Profile 
       Messaging/Notifications 
       Feed 
       Profile 
       Groups 
       Accessibility 
      
7. [Making Hard Choices: The Quest for Ethics in Machine ...](https://www.linkedin.com/blog/engineering/archive/making-hard-choices-the-quest-for-ethics-in-machine-learning) — `tavily`
   > LinkedIn Logo Engineering Blog. Open navigation. Close ... But with the ubiquity of software-led decision-making, filtering, and other relevance models
8. [LinkedIn Algorithm Best Practices](https://www.linkedin.com/top-content/marketing/linkedin-marketing-guide/linkedin-algorithm-best-practices) — `tavily`
   > If LinkedIn feels harder than it used to and your reach dropped,
it's not YOU. It's the new LinkedIn algorithm.
Here's what changed 👇
Over the last year, LinkedIn quietly rebuilt how the platform deci
9. [Feed](https://www.linkedin.com/blog/engineering/feed) — `tavily`
   > LinkedIn Logo
LinkedIn Logo

# Feed blog posts

Feed

Hristo Danchev

Mar 12, 2026

Feed

Sakshi Jain

Nov 20, 2025

Infrastructure

Nisheedh Raveendran

Nov 17, 2025

Nisheedh Raveendran

Sep 13, 202
10. [The top 2019 LinkedIn Engineering blogs](https://www.linkedin.com/blog/engineering/archive/the-top-2019-linkedin-engineering-blogs) — `tavily`
   > As the year draws to a close, we're taking a look back at ten of our most popular 2019 articles on the LinkedIn Engineering Blog.
11. [Community-focused Feed optimization - LinkedIn](https://www.linkedin.com/blog/engineering/feed/community-focused-feed-optimization) — `exa`
   > LinkedIn’s feed stands at the center of building global professional knowledge-sharing communities for our members. Members talk about their career stories, job openings, and ideas in a variety of for
12. [A Look Behind the AI that Powers LinkedIn’s Feed: Sifting through Billions of Conversations to Create Personalized News Feeds for Hundreds of Millions of Members](https://www.linkedin.com/blog/engineering/feed/a-look-behind-the-ai-that-powers-linkedins-feed-sifting-through) — `exa`
   > At LinkedIn, our mission is to connect the world’s professionals to make them more productive and successful. The LinkedIn Feed stands at the center of this global professional community: a place for 
13. [Making Your Feed More Relevant – Part I](https://www.linkedin.com/blog/engineering/archive/making-your-feed-more-relevant-part-i) — `exa`
   > The LinkedIn feed is the sorted list of updates displayed to our members when they log in to Linkedin.com or use the mobile app. Feed relevance is the task of evaluating the appropriateness of updates
14. [Spreading the Love in the LinkedIn Feed with Creator-Side Optimization](https://www.linkedin.com/blog/engineering/member-customer-experience/linkedin-feed-with-creator-side-optimization) — `exa`
   > Members can participate in conversations in the feed in two distinct roles: as creators who share posts, and as feed viewers who read those posts and respond to them. When a feed viewer visits the Lin
15. [FollowFeed: LinkedIn's Feed Made Faster and Smarter](https://www.linkedin.com/blog/engineering/feed/followfeed-linkedin-s-feed-made-faster-and-smarter) — `exa`
   > The feed is the default landing experience for LinkedIn’s members. It helps them discover the most relevant content, read original views from people that matter to them, and take part in unique conver
16. [Putting members first: testing and measuring how content appears in your Feed](https://www.linkedin.com/blog/engineering/feed/putting-members-first-testing-and-measuring-how-content-appears-in-your-feed) — `exa`
   > Putting members first: testing and measuring how content appears in your Feed
...
# Putting members first: testing and measuring how content appears in your Feed
...
We’ve shared how the feed works be
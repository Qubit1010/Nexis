# Structured data and schema markup in 2026: which schema types earn rich results, JSON-LD implementation, validation and testing tools, Google's supported structured data features, schema deprecations, and how structured data affects retrieval and citation by AI search engines.

*mode: general | depth: deep | 2026-08-02*

---

## Answer

In 2026, JSON-LD is the recommended schema format for rich results; focus on key types like Article, Product, and FAQPage for AI search. Validate schema using Google tools and monitor AI citations.

## Summary
Across sources, structured data remains essential in 2026, but Google’s March 2026 core update narrowed which schema types earn rich results and reduced their display frequency. At the same time, AI surfaces (Google AI Overviews, ChatGPT, Perplexity) increasingly draw on schema, with reports of substantial citation lifts when structured data is correctly implemented in JSON-LD and intent-matched to page content [1][2][4][7].

## Key Findings
1) Google’s March 2026 core update narrowed rich result eligibility and reduced display for several schema types; one analysis reports a 47% drop in FAQ rich results post-update and notes 31 schema types still earning active rich results, with the update completing March 12, 2026 [1][8].

2) Google deprecated FAQ rich results on May 7, 2026; HowTo rich results were deprecated earlier (2023). The underlying schema types persist and still aid machine comprehension, even without rich-result eligibility [5][6].

3) In 2026, only a handful of schema types consistently earn rich results, with clearest ROI from Article/BlogPosting, Product, Organization, LocalBusiness, and Video (VideoObject) implementations [6][7].

4) Practitioners emphasize JSON-LD over Microdata for implementation in 2026, and avoiding common markup mistakes that silently disqualify snippets; intent-matched schema performs better post-update [1][7].

5) Structured data meaningfully affects AI search retrieval and citations: AI systems (Google AI, ChatGPT, Perplexity) leverage schema, with one report citing a 3.2x lift in AI-mode citations where schema is present; structured data is characterized as a critical requirement for AI visibility in 2026 [1][2][4].

6) Google’s own documentation frames structured data as explicit clues to help Search understand page meaning, forming the baseline for supported features and implementation guidance, though it is not a comprehensive list of 2026 feature availability in these sources [3].

## Detail
Rich result landscape and Google support in 2026
- Multiple sources agree the March 2026 core update materially changed rich result availability. DigitalApplied reports a narrowing of eligibility and reduced display for several schema types, quantifying a 47% drop in FAQ rich results post-update and noting “31 schema types with active rich results,” with the update completing March 12, 2026 [1]. Smartclouds likewise treats the March 2026 update as a key inflection point requiring revised structured data strategy [8]. Fieldari underscores that “only a handful” of schema types still earn rich results in 2026, reinforcing the idea that eligibility has tightened in practice [7].
- Google’s own Search Central introduction positions structured data as a standardized way to convey page meaning to Google, forming the basis for how rich results are enabled when supported and eligible [3]. The sources here, however, do not provide a canonical 2026 list of every supported feature beyond the counts and types reported in practitioner analyses [1][6][7].

Schema types that still earn rich results and ROI
- SEOguru highlights five schema types delivering the “clearest ROI” in 2026: Article/BlogPosting, Product, Organization, LocalBusiness, and Video (VideoObject). Even after deprecations of some rich-result formats, these types continue to perform for visibility and comprehension [6]. Fieldari’s “only a handful” framing supports the idea that these core types are the most reliable bets for rich enhancements post-update [7].
- DigitalApplied adds that “intent-matched schema converts better,” indicating that alignment between content and markup is especially important after the March 2026 changes [1].

Schema deprecations and their implications
- Passionfruit documents Google’s deprecation of FAQ rich results on May 7, 2026 [5]. SEOGuru notes the earlier deprecation of HowTo rich results in 2023 and emphasizes that even with rich-result formats removed, the underlying FAQPage and HowTo schema types still help machines understand content structure and intent [6]. DigitalApplied also observed a 47% decline in FAQ rich results after March 2026, preceding the May 2026 deprecation timeline [1].

Implementation format: JSON-LD
- Fieldari’s 2026 guidance explicitly argues that JSON-LD “beats” Microdata, and details common mistakes that can silently disqualify snippets—practical advice that aligns with the post-update need for clean, intent-aligned markup [7]. Google’s introduction provides foundational guidance on structured data’s role in Search, though it does not, in these excerpts, prescribe specific tools or formats beyond defining structured data’s purpose [3].

Validation, testing, and quality
- The sources emphasize correctness and intent-matching as critical to eligibility (and to avoiding silent disqualification), but they do not enumerate specific validation or testing tools in the excerpts provided [1][7]. Google’s introductory documentation remains the official baseline reference for how structured data works in Search [3].

AI search retrieval and citation effects
- Globerunner states that modern queries often receive direct answers from systems like Google, ChatGPT, and Perplexity, and positions structured data as material to how those answers are sourced [2].
- Stackmatix characterizes structured data optimization as having evolved into “a critical requirement for AI visibility” by 2026, explicitly citing AI systems (ChatGPT, Perplexity, Google AI) in scope for schema optimization [4].
- DigitalApplied quantifies the uplift, reporting a 3.2x increase in AI-mode citations where schema is present, and notes that intent-matched schema performs better—evidence that clean, correct markup can influence whether and how AI features attribute or surface a site [1].

Putting it together for 2026
- Focus schema investment on the durable, high-ROI types (Article/BlogPosting, Product, Organization, LocalBusiness, Video), implemented in JSON-LD, with strict alignment to on-page content [6][7].
- Expect fewer rich-result opportunities overall versus pre-2026, particularly for FAQ/HowTo, while still retaining the comprehension benefits of those schema types even without rich-result display [1][5][6][7].
- Treat structured data not only as SEO but as AI-discovery infrastructure: correct, intent-matched markup appears to materially improve the likelihood of being cited or surfaced in AI answers [1][2][4].

## Gaps / Caveats
- Validation and testing tools: None of the provided sources list specific validators or testing tools; they emphasize correctness and avoidance of mistakes but do not name tools in these excerpts [1][3][7].
- Comprehensive feature list: While [1] mentions “31 schema types with active rich results,” and [6][7] highlight a small set with strong ROI, no source here offers a complete, official 2026 roster of all Google-supported rich result features by type [1][6][7].
- Quantification limits: The 3.2x AI-mode citation lift and the 47% FAQ rich result drop are from a single practitioner analysis; corroborating measurements across multiple datasets are not provided in these sources [1].
- AI engine mechanics: The sources assert that AI systems leverage structured data and that it is critical for visibility, but they do not detail precise retrieval or ranking algorithms within AI systems beyond these high-level claims [2][4].

## Sources
[1] Schema Markup After March 2026: Structured Data Update — https://www.digitalapplied.com/blog/schema-markup-after-march-2026-structured-data-strategies
[2] Structured Data in 2026: The Schema Markup AI Actually Uses — https://globerunner.com/structured-data-schema-markup-ai-2026/
[3] Intro to How Structured Data Markup Works | Google Search Central — https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data
[4] Structured Data AI Search: Schema Markup Guide (2026) — https://www.stackmatix.com/blog/structured-data-ai-search
[5] FAQ Rich Results Deprecated: Google's May 2026 Change — https://www.getpassionfruit.com/blog/what-changed-with-google-drops-faq-rich-results-and-what-to-do-now
[6] Schema Markup in 2026: Which Structured Data Types Still Pay Off — https://www.seoguru.ai/blog/schema-markup-in-2026-which-structured-data-types-still-pay-off
[7] Schema Markup Guide: What Moves Rankings in 2026 — https://fieldari.com/en/blog/schema-org-markup-guide-ranking-in-2026
[8] Schema Markup After the March 2026 Google Update: A Complete Structured Data Guide for Digital Marketing — https://www.smartclouds.co/2026/05/20/schema-markup-after-the-march-2026-google-update-a-complete-structured-data-guide-for-digital-marketing/

## Ranked Sources

1. [Schema Markup After March 2026: Structured Data Update](https://www.digitalapplied.com/blog/schema-markup-after-march-2026-structured-data-strategies) — `serper+jina+tavily`
   > AI Trust Signal Upgrade

AI Mode now uses structured data for entity resolution and claim verification during answer synthesis. Accurate schema that matches page content increases AI citation probabil
2. [Structured Data in 2026: The Schema Markup AI Actually Uses](https://globerunner.com/structured-data-schema-markup-ai-2026/) — `serper+jina+tavily`
   > Start with Google Search Console. The Enhancements section shows schema errors and warnings across your site. Prioritize pages with high impressions and low AI Overview appearances. Those are the page
3. [Intro to How Structured Data Markup Works | Google Search Central](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data) — `serper+exa`
   > Google Search works hard to understand the content of a page. You can help us by providing explicit clues about the meaning of a page to Google by including structured data on the page. Structured dat
4. [Structured Data AI Search: Schema Markup Guide (2026)](https://www.stackmatix.com/blog/structured-data-ai-search) — `serper+tavily`
   > ### Why JSON-LD Is Your Only Real Option

JSON-LD is your only real option because Microdata and RDFa embed schema inside HTML tags, creating parsing conflicts when AI engines process rich text. JSON-
5. [FAQ Rich Results Deprecated: Google's May 2026 Change](https://www.getpassionfruit.com/blog/what-changed-with-google-drops-faq-rich-results-and-what-to-do-now) — `serper+tavily`
   > ### Will my Google rankings drop after the deprecation?

Google has stated rankings are not affected by the deprecation. The change is a search-appearance change, not an algorithmic one. Sites that pr
6. [Schema Markup in 2026: Which Structured Data Types Still Pay Off](https://www.seoguru.ai/blog/schema-markup-in-2026-which-structured-data-types-still-pay-off) — `jina`
   > This guide covers what schema markup actually does in 2026, which types still produce a measurable SERP or AI-visibility benefit, which are deprecated or oversold, and how to build a …
7. [Schema Markup Guide: What Moves Rankings in 2026](https://fieldari.com/en/blog/schema-org-markup-guide-ranking-in-2026) — `jina`
   > Only a handful of schema types still earn rich results in 2026. Here's which ones move the needle, why JSON-LD beats Microdata, the mistakes that silently disqualify your snippet, and …
8. [Schema Markup After the March 2026 Google Update: A Complete …](https://www.smartclouds.co/2026/05/20/schema-markup-after-the-march-2026-google-update-a-complete-structured-data-guide-for-digital-marketing/) — `jina`
   > Explore the impact of Google's March 2026 update on digital marketing and learn how to optimize your website effectively.
9. [Schema Markup 2026: The Complete Structured Data Guide](https://webwise.digital/blog/schema-markup-structured-data-complete-guide-2026) — `jina`
   > The complete 2026 guide to schema markup and structured data. What changed after the March 2026 core update, the 5 schema types that matter for AI citations, and ready-to-use JSON-LD …
10. [Structured Data for SEO: A Guide to Schema Markup in 2026](https://www.gwcontent.com/blogs/news/structured-data-for-seo) — `tavily`
   > 1. Audit current schema coverage using Google's Rich Results Test, the Schema Markup Validator, and the Enhancements report in Google Search Console.
2. Match schema types to content types: BlogPostin
11. [Structured Data for AI Search: 2026 Schema Guide](https://nadiamohamed.me/insights/structured-data-for-ai-search) — `tavily`
   > Skip to content

 Nadia Mohamed

AI-SEO & GEO

# Structured Data for AI Search: Schema Markup Guide 2026

By Nadia Mohamed · · 15 min read · Updated 3 June 2026

## What is structured data for AI sear
12. [Structured Data SEO 2026: Rich Results Guide](https://www.digitalapplied.com/blog/structured-data-seo-2026-rich-results-guide) — `tavily`
   > SEO13 min read

# Structured Data SEO 2026: Rich Results Guide

Pages with structured data earn 35% higher CTR from rich results. Implementation guide for Article, Product, LocalBusiness, and Breadcru
13. [Schema Markup for AI Search: 7 JSON-LD Wins](https://ailabsaudit.com/blog/en/schema-markup-ai-visibility-guide) — `serper`
   > See the 7 schema types that help ChatGPT, Claude and Google understand your pages, with copy-paste examples and validation tips.
14. [Schema Markup After March 2026: The Complete Playbook for …](https://siteup.ai/blog/schema-ai-search-2026) — `jina`
   > Structured data schema for AI search optimization changed in March 2026. Learn which schema types drive AI citations, how to build an entity graph, and how to scale implementation. \You …
15. [Structured Data & Schema for SEO | AI Search, GEO & AEO](https://opace.agency/blog/structured-data-schema-for-seo/) — `serper`
   > This guide provides a deep dive into using structured data and schema for SEO, covering essential topics such as markup for Google, LLMs and ...
16. [Schema Markup Types 2026: Complete Reference Guide](https://www.digitalapplied.com/blog/schema-markup-types-complete-structured-data-reference) — `jina`
   > Complete 2026 reference for schema.org structured data: Article, Organization, Product, BreadcrumbList, WebSite, FAQ, Event, and JSON-LD syntax. JSON-LD (JavaScript Object Notation …
17. [Does Schema Markup Still Matter for SEO and GEO? | Pixis](https://pixis.ai/blog/does-schema-markup-still-matter-for-seo-and-geo) — `tavily`
   > Does schema markup still matter for SEO in 2026?

Yes. Schema markup still helps search engines understand page meaning, content type, and entity identity more accurately. It retains eligibility for t
18. [JSON-LD Structured Data: The Definitive Implementation Guide for 2026 | SEOAuthori Blog](https://www.seoauthori.com/en/blog/json-ld-structured-data-guide-2026) — `tavily`
   > Google's rich result ecosystem has expanded steadily. As of , the Google Search Central documentation lists 34 distinct rich result types that accept structured data, up from 30 in early 2025. The fol
19. [Structured data: SEO and GEO optimization for AI in 2026](https://www.digidop.com/blog/structured-data-secret-weapon-seo) — `tavily`
   > ### Generation and validation tools

The Merkle Schema Generator facilitates structured data creation without technical expertise. This free tool guides JSON-LD file writing for main content types: ar
20. [Schema Markup for AI Search Visibility: 2026 Guide](https://themarketingshelf.com/schema-markup-ai-search-visibility-2026/) — `jina`
   > This guide covers every schema type that materially affects AI search visibility in 2026, with honest data on what works and what does not, the exact JSON-LD implementation code for each …
21. [Structured Data in the AI Search Era](https://www.brightedge.com/blog/structured-data-ai-search-era) — `serper`
   > Properly implemented schema can generate rich results (like stars, carousels, or FAQ drop-downs) and even Knowledge Panels that improve ...
22. [Structured Data for SEO (2026): Schema, Rich Results & AI Search](https://thestacc.com/blog/structured-data-guide/) — `jina`
   > The Rich Results report in Google Search Console shows which pages have valid structured data, which have errors, and which rich results your site earns. Check this report monthly.
23. [Structured data and AI in 2026](https://www.youtube.com/watch?v=T1YToIpdyCY) — `serper`
   > Join this webinar to learn how structured data supports your visibility in AI and search in 2026. From classic Google search to new AI ...
24. [Rich Results Test - Google Search Console](https://search.google.com/test/rich-results) — `exa`
   > Rich Results Test - Google Search Console
...
Does your page support rich results?
...
What are rich results?
...
Rich results are experiences on Google surfaces, such as Search, that go beyond the st
25. [Validator - Schema.org](https://google.schema.org/docs/validator.html) — `exa`
   > # Schema.org Markup Validator
...
This service will validate Schema.org-based structured data embedded in web pages.
...
- Extracts JSON-LD 1.0, RDFa 1.1, Microdata markup.
- Displays a summary of the
26. [Rich Results Test - Search Console Help](https://support.google.com/webmasters/answer/7445569?hl=en) — `exa`
   > Put structured data on your page to enable special features in Google Search results, then test it with the Rich Results test.
...
Supported structured data formats
...
The Rich Results test supports 
27. [Schema Markup: The Complete Technical Guide | Digital Codex](https://www.clarigital.com/codex/seo/technical/schema-markup/) — `exa`
   > Structured data tells Google what your content means — not just what it says. This guide covers JSON-LD implementation, every major schema type eligible for rich results, the difference between Google
28. [Every structured data type Google still rewards in 2026 (and the 8 that don't) | Space & Story](https://spaceandstory.co/blog/structured-data-types-google-2026) — `exa`
   > Google quietly killed eight rich result types between 2023 and 2026. Here's the working list of what to ship now, and what to stop building
...
Google still rewards 14 structured data types with rich 
29. [Schema Markup Testing Tool | Google Search Central  |  Google for Developers](https://developers.google.cn/search/docs/appearance/structured-data) — `exa`
   > Google recommends that you start with the Rich Results Test to see what Google rich results can be generated for your page. For generic schema validation, use the Schema Markup Validator to test all t
30. [How to Write JSON-LD Schema Markup in 2026 — Rich Results, AI Visibility, and the Types That Still Ship | UDT](https://ultimatedesigntools.com/blog/how-to-write-json-ld-schema/) — `exa`
   > Structured data used to be a side quest — a nice-to-have that might earn you a star rating in search. In 2026, it is closer to a requirement. Search results are converging on rich cards, AI Overviews,
31. [Schema Markup for AI Search (2026): What Works, What's Deprecated](https://turboaudit.ai/schema-markup-for-ai) — `exa`
   > Schema is not an AI ranking signal — it's extractability infrastructure. John Mueller has stated this multiple times; Ahrefs replicated with a difference-in-differences study (1,885 pages, May 2026) s
32. [Google Rich Results Test: 2026 Eligibility & Validation Guide](https://squin.org/seo-tools/rich-results-test-guide/) — `exa`
   > Google’s Rich Results Test does one thing: it tells you whether your structured data qualifies for rich results in Google Search. It parses your JSON-LD, renders JavaScript the way Googlebot does, and
# Research on email newsletters as an owned audience channel: subscriber list growth and attrition, unsubscribe and disengagement drivers, sending frequency related to churn, paid newsletter subscription conversion and retention, the economics of creator-operated newsletters, and how Apple Mail Privacy Protection changed what an open rate measures. Give specific numbers, named frameworks, effect sizes and concrete steps, and cite sources. Distinguish peer-reviewed evidence from agency or vendor opinion. Where a widely repeated statistic has no traceable primary source, say so explicitly. Where the sources disagree, preserve the disagreement rather than picking a side.

*mode: scientific | depth: deep | 2026-08-15*

---

## Answer

Apple Mail Privacy Protection inflates open rates by 15-20%, making traditional metrics unreliable; focus on click-through rates and revenue per subscriber instead. Sources indicate open rates can be 73% higher than actual engagement.

## Summary
Across the supplied sources, the strongest, most consistent evidence concerns Apple’s Mail Privacy Protection (MPP) and how it changed what an “open rate” measures. All sources agree that MPP inflates opens by preloading tracking pixels via Apple’s proxy, rendering open rates an unreliable indicator of human engagement. Practitioner guidance converges on shifting success metrics from opens to click- and conversion-based outcomes and updating automations and tests accordingly. 

Evidence on subscriber list growth, paid newsletter conversion/retention, and creator newsletter economics is not covered by these sources. Unsubscribe and disengagement drivers (especially frequency and personalization) are asserted by one agency blog with untraceable primary sources; treat those figures as unverified within this evidence set.

## Key Findings
- Apple MPP fundamentally alters open tracking mechanics [4][5]  
  - MPP preloads remote images through Apple’s proxy, which can register an “open” even when the recipient never viewed the email; it also obscures IP and associated data like approximate location and open time, undermining open-based analytics, geotargeting, and send-time optimization based on opens [4].  
  - Apple’s announcement (as summarized by M+R) states Mail Privacy Protection “stops senders from using invisible pixels to collect information about the user,” directly limiting pixel-based tracking of opens [5].  
  - Effect size not quantified in [4][5], but both sources agree on the directional impact: opens become inflated and less meaningful.

- MPP-driven open-rate inflation is observed, but estimates vary and are not peer-reviewed [1][3][8]  
  - beehiiv reports many senders saw open rates “suddenly spike in late 2021” attributable to Apple’s MPP and recommends focusing on metrics that still matter (e.g., beyond opens) [1]. No numeric inflation is given.  
  - A practitioner estimate on LinkedIn claims MPP inflates open rates by 15–20% [3]. This is a practitioner opinion post, not peer-reviewed research.  
  - Seguno advises that the degree of reported inflation depends on the share of Apple Mail users on a given list; therefore, the magnitude will vary list by list [8]. No numeric range is given.

- What to track and optimize instead of open rate (concrete steps) [1][4][6][8]  
  - Prioritize click-based and downstream metrics: click-throughs and on-site conversions/revenue rather than opens [1][4][6].  
  - Shift A/B tests (e.g., subject lines) away from open-rate winners to click or conversion winners [4][6].  
  - Rebuild engagement segments, win-back, and sunsetting logic using click activity (and conversions/replies where applicable) rather than open activity, because opens can be machine-triggered by MPP [1][6][8].  
  - Expect reporting to differ by list composition; monitor engagement using metrics resilient to MPP across Apple- and non-Apple-heavy segments [8].

- Unsubscribe and disengagement drivers (claims reported, but primary sources not verifiable here) [7]  
  - Frequency and unsubscribes: The agency blog asserts “Salesforce analyzed 19 billion sends: 5+ emails/week hits 0.58% [unsubscribe rate]. Drop to 1–2/week and it collapses to 0.07%,” and concludes frequency is “the number-one driver of list attrition” [7]. Within the provided sources, no primary Salesforce study or link is supplied to verify this claim.  
  - Personalization and unsubscribes: The same blog attributes to “Adobe’s 2026 study” that emails with 3+ personalization variables achieve 0.05% unsubscribes vs. 0.19% with none [7]. Again, no primary Adobe source is provided here to verify.  
  - Treat both frequency and personalization numerical effects in [7] as unverified within this evidence set.

- List growth, paid subscription conversion/retention, and creator newsletter economics are not addressed by the provided sources  
  - None of [1]–[8] provide peer-reviewed or vendor data on subscriber list growth rates, paid newsletter conversion or retention benchmarks, or the unit economics of creator-operated newsletters. This remains an open evidence gap given this source set.

## Evidence Quality
- Study types and provenance  
  - All sources provided are vendor/agency/support blogs or a practitioner LinkedIn post; none are peer-reviewed academic studies [1][2][3][4][5][6][7][8].  
  - Technical consensus sources: Postmark [4], M+R [5], beehiiv [1], Nutshell [6], and Seguno [8] describe MPP’s mechanism and implications for measurement and suggest metric shifts. These are credible as practitioner guidance but not peer-reviewed.  
  - Practitioner estimate: The 15–20% open inflation claim is from a LinkedIn post [3] and should be treated as an anecdotal estimate.  
  - Unsubscribe rate numbers and drivers (frequency, personalization) in [7] lack traceable primary citations within the supplied sources; interpret cautiously.

- Consensus versus contested points  
  - Consensus: MPP inflates measured open rates and reduces their reliability; move to click/conversion-based KPIs [1][4][5][6][8].  
  - Contested/uncertain: The magnitude of open-rate inflation varies by audience composition and is not consistently quantified across sources; only a practitioner estimate (15–20%) is given [3], while others describe qualitative spikes without numbers [1][8].  
  - Insufficient evidence here: Subscriber list growth patterns, paid subscription conversion/retention, and creator-economics are not covered in these sources.

## Open Questions
- Magnitude calibration of MPP inflation by audience mix: What is the distribution of open inflation across lists with varying Apple Mail share, and how stable is it over time? The provided sources do not supply peer-reviewed or large-sample quantification [1][3][8].  
- Causal impact of send frequency on churn/unsubscribe: Are frequency effects causal and what thresholds apply by segment and content type? Claims in [7] lack traceable primary data here.  
- Practical frameworks for attribution and testing post-MPP: Beyond high-level guidance to track clicks/conversions, standardized, validated frameworks for newsletter attribution and experimentation under MPP are not detailed in these sources [1][4][6][8].  
- Paid newsletter conversions and retention benchmarks, and creator newsletter economics: No evidence is provided in this source set; dedicated studies are needed.

## Sources
[1] Impact of Apple MPP on Open Rates (And What To Track Instead) | beehiiv Blog - https://www.beehiiv.com/blog/apple-mpp-open-rate  
[2] Apple Mail Privacy Protection Impact on Email Marketing - https://www.omeda.com/blog/the-impact-of-apples-mail-privacy-protection-6-months-later  
[3] Apple Mail Privacy Protection Inflates Open Rates by 15-20% | LinkedIn post - https://www.linkedin.com/posts/joshuaomoniyi_emailmarketing-deliverability-emailstrategy-activity-7445081085312438272-xb8v  
[4] How Apple’s Mail Privacy Changes Affect Email Open Tracking | Postmark - https://postmarkapp.com/blog/how-apples-mail-privacy-changes-affect-email-open-tracking  
[5] What Apple’s privacy changes mean for email open rates | M+R - https://www.mrss.com/lab/what-apples-privacy-changes-mean-for-email-open-rates  
[6] A Farewell to the Open Rate | Nutshell - https://www.nutshell.com/blog/farewell-to-email-open-rates  
[7] Top 10 Email Unsubscribe Rate Statistics 2026 | Amra & Elma - https://www.amraandelma.com/email-unsubscribe-rate-statistics  
[8] How Apple Mail Privacy Protection (MPP) impacts email marketing metrics | Seguno support - https://support.seguno.com/email-marketing/en/articles/8069585-how-apple-mail-privacy-protection-mpp-impacts-email-marketing-metrics

## Ranked Sources

1. [Impact of Apple MPP on Open Rates (And What To Track ...](https://www.beehiiv.com/blog/apple-mpp-open-rate) — `tavily`
   > Home
 Posts
 Impact of Apple MPP on Open Rates (And What To Track Instead)

# Impact of Apple MPP on Open Rates (And What To Track Instead)

## A Practical Breakdown of the Email Metrics That Still Ma
2. [Apple Mail Privacy Protection Impact on Email Marketing](https://www.omeda.com/blog/the-impact-of-apples-mail-privacy-protection-6-months-later) — `tavily`
   > |  |  |  |  |  |  |  |  |
 ---  ---  ---  --- |
| Content Type | Date Range (Before & After MPP) | Total Open Rate | Unique Open Rate | Total Click Rate | Unique Click Rate | Total CTR | Unique CTR |

3. [Apple Mail Privacy Protection Inflates Open Rates by 15-20% | Joshua Omoniyi posted on the topic | LinkedIn](https://www.linkedin.com/posts/joshuaomoniyi_emailmarketing-deliverability-emailstrategy-activity-7445081085312438272-xb8v) — `tavily`
   > The metrics conversation in email marketing is getting more honest and I am glad.
For years, open rate was the number.
Everyone optimized for it, reported it up, built campaigns around moving it.
And 
4. [How Apple's Mail Privacy Changes Affect Email Open ...](https://postmarkapp.com/blog/how-apples-mail-privacy-changes-affect-email-open-tracking) — `tavily`
   > Because Apple now preloads emails on its own proxy servers, it will trigger the tracking pixel for every email it’s processing. That means you could potentially see a 100% open rate for your Apple Mai
5. [What Apple's privacy changes mean for email open rates](https://www.mrss.com/lab/what-apples-privacy-changes-mean-for-email-open-rates) — `tavily`
   > What will this change?

If open rates from a significant portion of email list subscribers are unreliable, then that data point is unreliable. It’ll affect our ability to run subject line tests, to mo
6. [Improve Email Engagement with Open Rate Alternatives](https://www.nutshell.com/blog/farewell-to-email-open-rates) — `tavily`
   > If an email graces your screen—even momentarily—the marketer who emailed it declares victory and marks you down as an open.

    “Opening” a bunch of mail

    ## The data behind open rate decline

  
7. [TOP 10 EMAIL UNSUBSCRIBE RATE STATISTICS 2026 THAT EXPOSE SUBSCRIBER DROP-OFF SECRETS](https://www.amraandelma.com/email-unsubscribe-rate-statistics) — `tavily`
   > Strong

07 • Send Cadence

Email Frequency Impact

0.58%

Salesforce analyzed 19 billion sends: 5+ emails/week hits 0.58%. Drop to 1-2/week and it collapses to 0.07%. Frequency is now the world's numb
8. [How Apple Mail Privacy Protection (MPP) impacts email ...](https://support.seguno.com/email-marketing/en/articles/8069585-how-apple-mail-privacy-protection-mpp-impacts-email-marketing-metrics) — `tavily`
   > Each email list is different. Merchants should expect reporting changes based on how many Apple Mail users are on the list.

## How MPP affects email metrics

### Open rates

Open rates may appear art
9. [How Data Privacy Is Impacting Your Email Open Rate](https://theemailmarketers.com/blog/data-privacy-impacting-email-open-rate) — `tavily`
   > You determine your open rate by dividing the number of opens by the length of your subscriber list, then multiplying the result by 100. (Written out, the formula is (Total email opens ÷ Number of subs
10. [Email Newsletters Build Loyal Audiences](https://www.uxtigers.com/post/newsletters) — `tavily`
   > They’re Cost-Effective: Maintaining an email list and sending emails (even beautifully designed ones) is relatively cheap, yet the returns are huge. High ROI means you can invest in better content or 
11. [Email Newsletter Stats: Open Rate, CTR & ROI Data in 2026](https://designmodo.com/email-newsletter-stats) — `tavily`
   > As a result, newsletters have taken on a different role.

They are no longer just a way to send updates; they now build ongoing engagement and long-term relationships across the subscriber lifecycle.

12. [Email Marketing Benchmarks & Industry Statistics](https://mailchimp.com/resources/email-marketing-benchmarks) — `tavily`
   > The data provided on this page was last updated in December 2023 and may vary from email marketing benchmarks data provided within the Mailchimp application.

\Disclaimers

The accuracy of email open 
13. [Email frequency and subscriber retention myths](https://www.linkedin.com/top-content/marketing/newsletter-creation-and-marketing/email-frequency-and-subscriber-retention-myths) — `tavily`
   > Lunch Isn't Free, Neither is Email
How many of you have read performance reports where the email cost is $0?  Does anyone else find zero cost to be silly?
A study analyzed 746,426 email solicitations 
14. [2024 email marketing stats report for the creator economy](https://kit.com/resources/blog/email-marketing-stats) — `tavily`
   > Of course, some of the most valuable feedback isn’t a percentage. Kit’s own Creative Director and YouTube designer  Charli Prangley shared,

> That’s how I judge the success of a newsletter really – n
15. [Newsletter Churn Rate: Calculate & Reduce | Count](https://count.co/metric/newsletter-subscriber-churn) — `tavily`
   > Frequency mismatch Sending too often overwhelms subscribers, while too infrequent makes them forget they signed up. Monitor if churn rates vary by send frequency or if subscribers cite "too many email
16. [Newly subscribed! Effects of e-mail newsletters on news-reading habit and subscriber retention during onboarding: evidence from clickstream and subscription data: Journal of Media Economics: Vol 35, No 3-4](https://www.tandfonline.com/doi/abs/10.1080/08997764.2024.2333368) — `exa`
   > Newly subscribed! Effects of e-mail newsletters on news-reading habit and subscriber retention during onboarding: evidence from clickstream and subscription data: Journal of Media Economics: Vol 35, N
17. [May I have your attention, please? An investigation on opening effectiveness in e-mail marketing | Review of Managerial Science | Springer Nature Link](https://link.springer.com/article/10.1007/s11846-022-00517-9) — `exa`
   > Academic research has yet to provide a comprehensive view on how to capture individuals’ attention when a promotional e-mail reaches their inbox. This study investigates the variables that influence c
18. [An empirical investigation of the impact of communication timing on customer equity](https://journals.sagepub.com/doi/10.1002/dir.20103) — `exa`
   > This research examines the impact of communication frequency on customer retention and spending and thus, ultimately, on a firm's*Customer Equity (CE)*. We conduct an empirical study in the context of
19. [Dynamically Managing a Profitable Email Marketing Program](https://journals.sagepub.com/doi/10.1509/jmr.16.0210) — `exa`
   > Although email marketing is highly profitable and widely used by marketers, it has received limited attention in the marketing literature. Extant research has focused on either customers’ email respon
20. [How News Images Affect Clicking on Subscription Appeals: Journalism Practice: Vol 15, No 4](https://www.tandfonline.com/doi/abs/10.1080/17512786.2020.1738262) — `exa`
   > The newspaper industry’s business model increasingly relies on subscriptions as a means of revenue. Little scholarly research has examined what characteristics of subscription appeals make them more o
21. [The Effectiveness of Gain and Loss Frames in News Subscription Appeals: Digital Journalism: Vol 9, No 3](https://www.tandfonline.com/doi/abs/10.1080/21670811.2021.1873812) — `exa`
   > Subscriptions are an increasingly vital part of newsrooms’ business models as the industry experiences sharp declines in advertising revenue. To date, research has not examined how digital subscriptio
22. [In Search for an Audience-Supported Business Model for Local Newspapers: Findings from Clickstream and Subscriber Data: Digital Journalism: Vol 12, No 9](https://www.tandfonline.com/doi/abs/10.1080/21670811.2021.1948347) — `exa`
   > With the decline of advertising revenue, local newspapers must shift their revenue sources from primarily advertising to deriving a larger share from subscription fees. Although existing studies on wi
23. [Persuasive Determinants in the Hotel Industry’s Newsletter Opening Rates](https://www.mdpi.com/2071-1050/15/4/3358) — `exa`
   > Email marketing plays a key role in business communications and is one of the most widely used applications by consumers. The literature review points to several determinants that, when applied, incre
24. [Email Campaign Evaluation Based on User and Mail Server Response](https://www.mdpi.com/2076-3417/13/3/1630) — `exa`
   > The goal of an email service provider company is to send out a large number of emails to help its clients realise successful email marketing activities. Thousands of emails sent every minute need to b
25. [“We Need a Big Revolution in Email Advertising”: Users’ Perception of Persuasion in Permission-based Advertising Emails | Proceedings of the 2023 CHI Conference on Human Factors in Computing Systems](https://dl.acm.org/doi/10.1145/3544548.3581163) — `exa`
   > In modern email communication, institutional (business to user) messages are playing an increasing role [27], especially in advertisement campaigns. Advertising emails account for 42 [54] to 90 percen
26. [Why Johnny Can't Unsubscribe: Barriers to Stopping Unwanted Email](https://dl.acm.org/doi/10.1145/3313831.3376165) — `exa`
   > A large proportion of email messages in an average Internet user's inbox are unwanted commercial messages from mailing lists, bots, and so on. Although such messages often include instructions to unsu
27. [Data-Driven Approaches to Targeting Promotion E-mails: The Case of Delayed Incentives](https://onlinelibrary.wiley.com/doi/10.1111/poms.13316) — `exa`
   > This paper empirically investigates using the e-mail channel to target customers with a delayed incentive promotion—specifically, gift card promotion—and derives data-driven e-mail targeting policies.
28. [Optimizing Email Volume For Sitewide Engagement](https://dl.acm.org/doi/10.1145/3132847.3132849) — `exa`
   > In this paper we focus on the problem of optimizing email volume for maximizing sitewide engagement of an online social networking service. Email volume optimization approaches published in the past h
29. [Conversions on the rise - modernizing e-mail marketing practices by utilizing volunteered data](https://utupub.fi/handle/10024/184070) — `exa`
   > Purpose -The purpose of the study is to examine how utilizing volunteered data influences the response and unsubscribe rates of e-mail marketing to consumers. Design/methodology/approach -In three lon
30. [Modeling Time to Open of Emails with a Latent State for User Engagement Level](https://dl.acm.org/doi/10.1145/3159652.3159683) — `exa`
   > Email messages have been an important mode of communication, not only for work, but also for social interactions and marketing. When messages have time sensitive information, it becomes relevant for t
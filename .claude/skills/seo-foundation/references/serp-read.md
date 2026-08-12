# Reading the SERP - difficulty and click availability

Keyword difficulty is a vendor invention. There is no such metric at Google. Each tool
computes a 0-100 score mostly from the link profiles of incumbent pages, which means it
measures **incumbent link strength** and ignores content quality, intent match, freshness,
and whether the ranking pages answer the question at all `[practitioner]` [s290].

It is also relative to you. KD 40 is comfortable for an established domain and impossible
for a three-month-old site, and no tool knows which one your client is.

So the tool answers "how hard is this in general". The question you need answered is "how
hard is this **for this client**", and only the SERP can answer it. Reading it takes about
ninety seconds and is free.

---

## The manual difficulty read - six questions

`serp_features.py` answers four mechanically. Two are yours, and they are the two that
decide whether to commit.

### 1. Who is ranking? → `top_domains`, `sitelinked_results`
All large recognisable brands means hard. A mix of brands and independent sites means
winnable. Small niche sites means genuinely open.

Sitelinks are the observable proxy: when Google volunteers sitelinks it is treating that
result as a known destination. **4 or more sitelinked results on a page = brand-dominated.**

### 2. Is anything weak on page one? → `ugc_on_page1`, `ugc_positions`
Look for off-intent results, thin pages, three-year-old content, or a forum thread.

> **UGC ranking on page one is the strongest opportunity signal there is.** A Reddit thread
> in the top five means Google could not find a good page, and a good page would win.

This carries the most weight in the winnability score, deliberately.

### 3. Do the ranking pages actually answer the query? → **you**
Sometimes everything ranking is mediocre and Google is picking the least bad option. That
is an opening, and no script can see it. Open the top three and read them.

### 4. How much domain diversity? → `domain_diversity`
Ten different domains is an open SERP (`1.0`). Three domains taking eight slots (`0.4`)
means Google has decided who the authorities are and is not looking for more.

### 5. How fresh is the top content? → `freshness`, `median_age_days`
Everything from this quarter means a freshness system is active and the page will need
maintaining. Everything from 2022 means nobody is maintaining anything, which is an opening.

**Caveat that matters:** most results carry no date. A typical read is "4/10 dated". Treat
freshness as weak evidence, never as the deciding factor.

### 6. Could you be *clearly* better? → **you**
Not marginally. Clearly. If you cannot articulate what this client's page would do that
page one does not, there is no reason to rank yet. This is the single best filter in the
method and it is entirely judgment.

---

## How the winnability score is built

Starts at 3.0, clamped to 1-5. Every adjustment traces to a question above.

| Signal | Adjustment | Why |
|---|---|---|
| UGC in top 5 | **+1.5** | strongest opportunity signal there is |
| UGC on page one, below 5 | +0.75 | same signal, weaker position |
| Domain diversity ≥ 0.9 | +0.75 | open SERP, no settled authorities |
| Domain diversity ≤ 0.6 | −1.0 | consolidated, Google has decided |
| 4+ sitelinked results | −1.0 | brand-dominated page |
| ≤1 sitelinked result | +0.5 | not a brand SERP |
| 4+ major-platform slots | −0.5 | slots you cannot displace with a page |
| Median age > 730 days | +0.5 | nobody is maintaining page one |

**This is a starting position, not a verdict.** It answers four of six questions. Override
it from questions 3 and 6 and say why in the report - an overridden score with a stated
reason is more useful than the number alone.

---

## Click availability - and why it comes back unknown

`course/05`'s test asks how much traffic a query actually has left in it, since roughly
**60% of searches now end without a click** `[practitioner]` [s288] and AI Overviews appear
in about **47% of results** [s291], cutting CTR by **up to 58%** where present [s145].

The five steps:

1. How far down is the first organic result?
2. **Is an AI Overview present?**
3. Does the AI Overview or featured snippet fully answer the query?
4. How many features sit above organic? (**3+ means organic is a minority of the page**)
5. What would a click even be for?

**Serper does not return AI Overview presence.** Verified 2026-08-06 across five query
shapes - it never appears. `answerBox` is effectively never returned either, absent even on
"what is a crm". So steps 1-3 are not observable from this data source, and any
"click availability: healthy" computed from what is left would be a guess dressed as a
measurement, silently distorting every priority score downstream.

So `click_availability` returns **`unknown`** with its observable components listed
(`paa_blocks`, `related_blocks`, `answer_box_present`), and the honest procedure is:

**For the top 20 by priority only, check manually.** Open each in incognito, look for an AI
Overview, and record healthy / reduced / effectively zero in the Sheet. Twenty checks is
about fifteen minutes and it only needs doing for keywords you might actually build for.

The rule of thumb while checking: **fact-answers get absorbed, decision-answers still send
traffic.** "What is a CRM" is answered above the fold. "Best CRM for a 12-person agency"
still needs a click, because the searcher wants to evaluate rather than to know.

---

## The impressions-vs-clicks diagnostic

For clients with Search Console access, this separates three different problems that all
present as "traffic is down":

| Pattern | Problem |
|---|---|
| Impressions down, clicks down | ranking problem - you lost position |
| Impressions flat, clicks down | CTR problem - a SERP feature is eating the click, or your title is |
| Impressions up sharply, CTR collapsed | you are ranking for broad junk that was never relevant |

Citations `[sN]` resolve via `seo-advisor/_research/sources.json`.

# Foundations - Section 6: Keyword Research Part 1, Finding

*Tools can only show you demand that has already been measured. Start where the language actually comes from.*

**Bottom line:** Keyword research has two halves that must not be mixed: finding candidates
and judging them. This section is finding only, and the discipline is to collect without
filtering. Open a tool first and you inherit its blind spots, including the roughly 15% of
daily searches that are entirely new and carry no historical data anywhere.

---

## Why the tool goes last

A keyword tool reports demand it has already observed. That makes it excellent at
confirming and terrible at discovering. Three consequences:

- **About 15% of daily searches are entirely new**, with zero historical data in any
  platform. No tool can show them to you. `[practitioner]`
- **Tools disagree with each other wildly.** Volume estimates for the same keyword can
  differ by as much as **30x** between platforms. Section 7 deals with what to do about
  that. `[practitioner]`
- **Tools bias you toward what everyone else already targets**, because everyone is querying
  the same databases.

The queries worth having are often the ones a customer said out loud on a call last week and
no tool has ever recorded. So you start with language, and you finish with tools.

## The one rule for this section

**Collect. Do not judge.**

No filtering by volume, difficulty, or whether you think you could rank. The instant you
start judging, you stop collecting, and you unconsciously discard anything that does not
match what you already believe. Judgement is Section 7 and it happens once, at the end, in
one pass.

Target: **200 or more raw candidates**. That number is deliberately larger than feels
sensible. Volume in the collection phase is what makes the clustering in Section 8 work.

## Layer 1: your own data

This is the layer with the least competition, because almost nobody does it.

- **Sales call transcripts and discovery notes.** Look for **trigger moments**: the specific
  phrasing people use when describing the problem that made them start looking. That phrasing
  is search behavior. `[practitioner]`
- **Support tickets and email threads.** Every repeated question is an informational query.
- **CRM notes and lost-deal reasons.** Objections are commercial-investigation queries in
  disguise. "Too expensive compared to X" is somebody searching "X alternatives".
- **Your site's internal search.** People telling you exactly what they expected to find and
  did not.
- **Search Console, existing queries.** The most underused source in SEO. You already rank
  for queries you never targeted. Sort by impressions with low clicks and read what is
  there. Many of your best opportunities are already in this report.

If you have a `meeting-insights` archive or client call transcripts, mine them. Real language
from real buyers outperforms any tool's suggestions.

## Layer 2: the SERP itself, free

You already collected some of this in Section 5.

- **People Also Ask.** Expand every box. Expanding one PAA question generates more, so you
  can pull dozens from a single SERP. These are literally Google telling you what searchers
  ask next.
- **Autocomplete.** Type your seed and step through the alphabet: "seo a", "seo b", and so
  on. Tedious, effective, free.
- **Related searches** at the bottom of the SERP.
- **"Searches related to" and refinement chips** near the top on many queries.

## Layer 3: communities

Where people write in their own words instead of a search box.

- **Reddit.** Especially valuable now: it is a heavy citation source for AI engines,
  accounting for roughly half of Perplexity's top citations. Language that appears there is
  language the models have absorbed.
- **Quora**, for question phrasing.
- **YouTube comments** on videos covering your topic. Unfiltered confusion, which is
  informational intent in raw form.
- **Niche forums, Slack and Discord communities, Facebook groups** in your market.

A fast technique: paste a long thread into an AI model and ask it to extract every distinct
question or problem stated, verbatim. You are using the model as a language extractor, not as
a keyword tool, which is the appropriate use of it here.

## Layer 4: competitors

Not to copy targets, but to find gaps.

- Which topics do three or more competitors cover that you do not?
- What do their navigation and service pages call things? Vocabulary differences matter.
- What do their most-linked pages cover?

Section 7 turns this into a formal gap analysis. Here you are just harvesting.

## Layer 5: the tools

Now open them, with everything above already in the sheet.

- **Google Keyword Planner.** The only source with volume data straight from Google, though
  bucketed and ads-oriented.
- **Ahrefs or Semrush** for scaled expansion and competitor keyword exports.
- Free tiers, Search Console, and Keyword Planner genuinely cover a small site. Section 42
  covers whether paid tools are worth it for you.

Use them to **expand** what you already have, not to originate the list.

## Layer 6: AI-era discovery

Two techniques that did not exist a few years ago and matter now.

**Fan-out mapping.** AI engines expand one prompt into **5 to 11 sub-queries**, sometimes 10
to 20, before retrieving anything. You can rank first for the literal query and appear in no
AI answer because you matched none of the sub-queries the engine actually ran. So collect the
sub-queries too. `[practitioner]`

**Inverse prompting.** Ask the engine directly: *"What sub-queries would you search to answer
this prompt?"* It will tell you. Those sub-queries go in your sheet as first-class
candidates. `[practitioner]`

Also worth capturing: AI search queries average **70 to 80 words** against 3 to 4 for
traditional search. Long conversational phrasings belong in your list even though every
volume tool will report zero for them. `[practitioner]`

## Capture format

One sheet, one row per candidate. Columns for now:

| Column | Fill now |
|---|---|
| Query | verbatim, as a human would phrase it |
| Source | first-party, PAA, autocomplete, community, competitor, tool, fan-out |
| Notes | any context worth keeping |

Leave intent, volume, difficulty and priority empty. Those are Section 7 and Section 8.

**Do not deduplicate yet either.** Near-duplicates are evidence about how the same idea gets
phrased, and Section 8 clusters them deliberately.

> **Why this matters:** the quality ceiling of everything downstream is set here. You cannot
> cluster your way to a good keyword map from a thin list, and you cannot rank for a query
> you never wrote down. Most people generate 40 candidates from one tool and wonder why their
> content plan feels generic. It is generic because everyone querying that tool got the same
> 40.

## Do this now

1. **Create the sheet** with the three columns above.
2. **Write 10 to 20 seed terms** from memory: what you do, what problems you solve, what
   people call it.
3. **Mine first-party sources for 30 minutes.** Sales notes, support threads, site search,
   and Search Console existing queries. Capture verbatim phrasing.
4. **Work the SERP layer on your top 5 seeds.** Expand every PAA, step autocomplete through
   the alphabet, grab related searches.
5. **Spend 20 minutes in communities.** Reddit and one niche forum. Extract questions
   verbatim.
6. **List 3 competitors and skim their service pages and top blog posts** for topics and
   vocabulary you are missing.
7. **Now open a keyword tool** and expand your seeds. Export and paste in.
8. **Run inverse prompting** on your three most important topics. Ask an AI engine what
   sub-queries it would run, and capture them.
9. **Count your rows.** Under 200, go back to communities and PAA, which are effectively
   bottomless.

## Capstone step

You have 200+ raw candidate queries for the capstone site, tagged by source, unfiltered and
unjudged. This is the raw material for Section 7, where you learn how much to trust the
numbers, and Section 8, where it becomes a keyword map with one page per intent.

## Key takeaways

- Tools report demand they have already measured, so they confirm well and discover badly.
  Roughly 15% of daily searches are new and invisible to every platform.
- Collect without judging. Filtering while collecting silently biases the list toward what
  you already believed.
- First-party language, sales calls, support tickets, site search, and existing Search
  Console queries, is the least competitive source and the one almost nobody mines.
- Capture AI fan-out sub-queries and long conversational phrasings even though volume tools
  report zero for them. Those are real retrieval targets now.

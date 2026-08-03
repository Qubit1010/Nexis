# Foundations - Section 2: How Search Engines Work

*Three separate systems that fail in three different ways, and why knowing which one broke is most of the job.*

**Bottom line:** Crawling, indexing and ranking are not three stages of one process. They
are three independent systems, each with its own failure mode. A page can be crawled and
never indexed, or indexed and never ranked, and those two problems share no fixes. Almost
every SEO diagnosis starts by working out which of the three actually broke.

---

## The pipeline, and the gates between the stages

**Crawling** is discovery. A bot finds a URL, requests it, and receives whatever the server
returns. Googlebot finds URLs by following links, reading XML sitemaps, and taking manual
submissions in Search Console.

**Indexing** is storage and understanding. Google processes the fetched page, works out what
it is about, decides whether it is a duplicate of something it already has, and if it passes
a quality bar, stores it. Google's index holds over **100 million gigabytes**.

**Ranking** is retrieval and ordering. When someone searches, Google pulls matching pages
from the index and orders them using many separate systems.

The word to hold onto is **gate**. There is a gate between each stage, and each gate rejects
things for its own reasons:

- Crawled does not mean indexed. Google routinely fetches a page, looks at it, and declines
  to store it.
- Indexed does not mean ranked. Being in the index just makes you eligible.
- Ranked does not mean visible. That is the whole AI-answer problem from Section 1.

## Crawling: the technical limits that quietly bite

Most people picture crawling as a bot that reads your page like a person. It is closer to a
program on a budget.

- **Googlebot fetches up to 2MB per URL.** PDFs get 64MB. Anything past that byte limit,
  including content and even HTML in the head, is simply not seen. A bloated page can have
  its real content sitting past the cutoff. `[practitioner]`
- **Crawling happens in two waves.** Wave one fetches the raw HTML. Wave two queues the page
  for the rendering service, which executes JavaScript. In 2026 the gap between them runs
  **24 to 72 hours**. `[practitioner]`
- **AI crawlers are different bots and often skip JavaScript entirely.** GPTBot,
  OAI-SearchBot, ClaudeBot and PerplexityBot crawl independently of Googlebot, and several
  of them do not execute JS at all. `[practitioner]`

That last point is the most under-appreciated fact in this whole course. If your content is
rendered client-side, Google will eventually see it after wave two, and several AI engines
may never see it. You can be perfectly visible in Google and structurally invisible to
ChatGPT for a purely technical reason that has nothing to do with your content.

**Crawl budget**, the thing beginners worry about most, is the thing that matters least for
them. It only becomes a real constraint above roughly **10,000 to 50,000 pages**. If your
site is 40 pages, crawl budget is not your problem and time spent on it is wasted.

## Indexing: the two rejections that look identical and are not

Search Console reports two exclusion states that beginners constantly confuse. They are
completely different problems.

**"Discovered - currently not indexed"** means Google knows the URL exists but has not
gotten around to fetching it. That is a **crawling** signal: budget, architecture, or
internal linking. The page is buried or the site is too big for the attention it gets.

**"Crawled - currently not indexed"** means Google fetched the page, read it, and chose not
to store it. That is a **quality** signal. Nothing technical is broken. Google looked at
your page and decided it was not worth an index slot.

The fixes could not be more different. The first is solved with internal links and a
flatter architecture. The second is solved by making the page better or deleting it. Getting
this backwards is the single most common wasted week in SEO.

Indexing also does **canonicalization**: when Google finds several URLs with near-identical
content, it picks one to represent the group. You express a preference with a canonical tag,
but it is a hint and Google can and does overrule it. Search Console tells you the
"Google-selected canonical", which is the answer that matters.

## Ranking: not an algorithm, a committee

There is no "the algorithm". Google runs **15 or more documented ranking systems** at once.
The ones worth knowing by name:

| System | What it does |
|---|---|
| **RankBrain** | Interprets queries it has never seen before |
| **BERT** | Understands word context and how phrasing changes meaning |
| **MUM** | Works across languages and formats, including images and video |
| **PageRank** | The original link-authority system, still running |
| **Passage Ranking** | Ranks a specific section inside a long page, not just the page |
| **Helpful Content system** | Folded into core ranking in 2024. Demotes content built for search engines rather than people |
| **Freshness systems** | Surfaces newer content for time-sensitive queries |
| **Reviews system** | Judges the depth and expertise of review content |

Two of these change how you should write. **Passage Ranking** means a single strong section
inside a long page can rank on its own, so burying a good answer deep in a page is less
fatal than it used to be. **The Helpful Content system** means writing that is transparently
aimed at ranking rather than at a reader is now a demotion signal rather than a neutral one.

## What Google confirms, and the long list it does not

Google publicly confirms only **seven** ranking factors: backlinks, content quality and
E-E-A-T, HTTPS, page speed and Core Web Vitals, mobile-friendliness, freshness, and page
experience.

Everything else you will read is inference. Some of it is good inference. Much of it is a
tool vendor's correlation study, and a few things are actively contradicted by Google's own
statements. These are **not** ranking factors, despite being repeated constantly:

- Bounce rate, as measured in Google Analytics
- Domain age
- Social signals such as likes and shares
- XML sitemaps as a ranking input, as opposed to a discovery aid
- Meta keywords
- Word count

That last one deserves a sentence, because it drives a lot of bad writing. Long pages
correlate with better rankings. They correlate because thorough answers tend to be longer,
not because length itself is rewarded. Writing to a word count produces padding, and padding
is exactly what the Helpful Content system is designed to catch.

## The other engines

Google is not the only index. **Bing** powers ChatGPT's search, which makes it far more
strategically important than its market share suggests. **IndexNow** is a push protocol
supported by Bing, Yandex and Naver: instead of waiting to be crawled, you notify them that
a URL changed. Google does not support it.

> **Why this matters:** every diagnosis you will ever run starts with "which stage failed".
> Not crawled, crawled but not indexed, indexed but not ranked, and ranked but not clicked
> are four different problems with four different fixes. People who skip this section spend
> years applying ranking fixes to indexing problems and wondering why nothing works.

## Do this now

1. **Open Google Search Console for your capstone site.** If it is not verified, verify it
   now. Everything from here depends on it.
2. **Run URL Inspection on your homepage.** Read the four things it tells you: whether the
   URL is on Google, the Google-selected canonical, the crawl date, and the page's indexing
   status.
3. **Click "Test live URL", then "View tested page", then the screenshot and HTML tabs.**
   This is Googlebot's view. Compare it against what you see in your browser. If content is
   missing from the rendered HTML, you have found a rendering problem, which is Section 26.
4. **Open the Pages report and find the exclusion reasons.** Note how many URLs sit in
   "Discovered - currently not indexed" versus "Crawled - currently not indexed". Write both
   numbers down.
5. **Pick one page from "Crawled - currently not indexed" and read it as a stranger.** Be
   honest about why Google declined to store it. This is usually uncomfortable and usually
   correct.
6. **Check `yoursite.com/robots.txt` in a browser.** Confirm it loads and returns content.
   You do not need to understand it yet, that is Section 21. Just confirm it exists and is
   not blocking everything.

## Capstone step

You now have Search Console verified, a confirmed index status for the homepage, both
exclusion counts written down, and one honest assessment of a page Google refused to index.
If your site turned out to have indexing problems, note them. Tier 3 is where you fix them,
and you will want the before numbers.

## Key takeaways

- Crawling, indexing and ranking are three separate systems with three separate failure
  modes. Diagnosis means identifying which one broke before touching anything.
- "Discovered - not indexed" is a crawling and architecture problem. "Crawled - not indexed"
  is a content quality problem. They look similar in Search Console and share no fixes.
- There is no single algorithm. At least fifteen documented ranking systems run at once, and
  two of them, Passage Ranking and the Helpful Content system, should change how you write.
- Google confirms only seven ranking factors. Bounce rate, domain age, social signals and
  word count are not among them, regardless of how often you read otherwise.

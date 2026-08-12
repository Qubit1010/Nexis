# MENTIONS mode: brand mentions, digital PR, and the honest link position

## Start with the reframe, because it decides the whole engagement

| Signal | Correlation with AI Overview citation |
|---|---|
| **Branded web mentions** | **r = 0.664** |
| **Backlinks** | **r = 0.218** |

`[practitioner, correlational]` - roughly 3x, and **never state it as causal.** Brands that get
mentioned a lot are also brands that are good.

This matters because of what this skill cannot do. There is **no free backlink index**, so
referring domains, DR/DA, link gap, anchor distribution and toxicity all return `unknown`. That
looks like a gap until you notice the thing it cannot measure correlates at 0.218 and the thing it
*can* measure correlates at 0.664.

**Say it plainly in the report:** this is mention work, not link work, and that is the right order
of operations regardless of tooling.

---

## Unlinked mention reclamation

**The highest-converting tactic in the entire authority tier.**

| Tactic | Conversion |
|---|---|
| **Unlinked mention reclamation** | **30-50%+** |
| Broken link building | 5-15% |
| Digital PR + original research | rated most effective by 34-48.6% of practitioners |
| Journalist outreach (Connectively, Qwoted, Featured.com) | 1-2 quality links/month at 2-3 responses/day |

### How this skill finds them

`authority.py --areas mentions` searches the brand, drops the client's own host, fetches each
result and resolves three states:

| State | Meaning |
|---|---|
| `linked` | already links back, nothing to do |
| `unlinked` | mentions the brand, no link - **the queue** |
| `unlinked, url-mentioned` | prints the domain as plain text without linking it - the easiest ask of all |

**Two Serper quirks, both verified 2026-08-09 and both worked around in code:** a quoted phrase
containing an apostrophe is rejected with "Query pattern not allowed for free accounts" (the
message blames the plan, but it is the combination - unquoted works, and quoted-without-apostrophe
works), and `-site:` is not worth spending a pattern allowance on when Python can filter the host.

### The ask

**Three sentences, naming the exact sentence that mentions them. Never a template.**

> Hi <name> - you mentioned <brand> in <article title>, in the line about <the specific thing>.
> We'd be glad if that could link to <url> so readers can find the details.
> Either way, thanks for the mention.

That is the whole email. The conversion rate comes from it being obviously hand-written about a
specific sentence.

**Track it.** Emails sent, replies, links earned. Link building without a tracked conversion rate
is a hobby.

---

## Platform presence: the 4+ threshold

Brands present on **four or more third-party platforms** are reported **2.8x more likely to be
cited by ChatGPT** `[practitioner, single vendor]`.

**The own site is the anchor, not one of the four.**

Shortlist (course/34):

| Platform class | Examples |
|---|---|
| Professional | LinkedIn company page **and** the founder's profile |
| Business data | Crunchbase |
| Review / vetted directory | G2, Capterra, Clutch, Trustpilot, Tripadvisor |
| Encyclopedic | Wikipedia or Wikidata |
| Media | YouTube, podcast appearances, conference speaker pages |
| Community | Reddit, Quora |

### The directory test is editorial standards

**Clutch vets its listings. A submit-your-URL directory does not.** Bulk directory submission is
zero value plus NAP-inconsistency risk. One vetted listing beats fifty scraped ones.

### Consistency is the cheap half

Across every profile, check: one canonical **one-sentence** description, identical category words,
identical founder-name spelling and format, identical URL format. Mechanical to gather, judgment to
rule on, and it fragments the entity when wrong.

---

## Digital PR

- **The average earned digital PR link costs about $750.** Price the activity accordingly.
- **Original research is the most reliable earned-link asset.** A survey of **100 customers is
  enough to be citable.**
- **Journalist requests:** respond **within the first hour**, in **two or three quotable
  sentences**, with one line of credential. Volume is the game: 2-3 responses/day yields 1-2 links
  a month.

---

## What to refuse

| Tactic | Why |
|---|---|
| PBNs | caught within weeks; domain-level suppression |
| Link exchanges at scale | reported 15-40% ranking drops |
| Mass guest posting | **98% of guest-post marketplace sites are low quality** (DR under 40, under 10k monthly traffic) |
| Bulk directory submission | zero value, NAP risk |

**But do not over-correct.** Reciprocal linking at small scale is not a penalty. Three mutual links
with genuine partners is normal and course/33 says so explicitly.

---

## The qualification thresholds this skill cannot apply

Carry them anyway - they are the client conversation, and they are why the prospect list is a
prospect list:

| Criterion | Threshold |
|---|---|
| Topical relevance | checked **first** |
| Real organic traffic | **1,000+ monthly visits** - a zero-traffic site passes ~zero value regardless of DR |
| Domain Rating | **DR 30+** baseline, **50+** high-impact (91% of SEOs set a floor) |
| Toxicity | drop above **Semrush Toxic Score 45** |

**A DR 35 niche-relevant link beats a DR 70 unrelated one.** Count **referring domains, not total
backlinks.** And flag anchor risk above roughly **20% exact-match**.

`push_sheet.py` invariant 4 blocks any link-prospect row carrying one of these numbers without a
named source, because there is no free source and an unattributed figure here was invented.

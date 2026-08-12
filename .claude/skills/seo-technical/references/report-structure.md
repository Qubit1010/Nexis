# The report

Written to `client-projects/<slug>/11-seo-technical.md`, sitting beside
`09-seo-foundation.md` and `10-seo-onpage.md`.

Same shape as seo-onpage's, for the same reason: a client holding both should recognise the
second one. **One-line diagnosis, three prioritized fixes, what is fine, the structural
question.** Not sixty findings.

The scripts produce roughly ninety check rows across the five of them. Ninety rows is a data
export. Turning it into three fixes is the judgment the skill exists to supply, and it is
deliberately not automated - `push_sheet.py --from-results` leaves the Findings tab empty on
purpose.

---

## Template

```markdown
# Technical SEO - <Client>

<date> - crawled <N> pages of <origin>

## Diagnosis

<One sentence. The single thing most responsible for the gap between what this site
publishes and what search and AI engines can use.>

## The three fixes

### 1. <Fix> - Tier <N>, <this week | this month | structural>

**What:** <the concrete change>
**Evidence:** <the measurement, with the number and the URL>
**Why it is first:** <the tier argument - what it unblocks>
**Expected effect:** <honest, and separated into ranking vs conversion where relevant>
**Effort:** <hours/days, and who does it>

### 2. ...
### 3. ...

## What is fine

<Named explicitly. This is what makes the failures credible, and it stops a client paying
to fix something that already works. Include anything already over the Core Web Vitals
floor, with "stop here" attached.>

## The structural question

<One, if there is one. The thing that is not a fix but a decision - a rendering strategy, a
migration, whether hreflang should exist at all, whether the architecture matches the
business. If there isn't one, say so.>

## Not measured

<Every `unknown`, with the manual route. Search Console is always here.>
```

---

## Rules

**Lead with the tier, not the count.** "Twelve schema errors" is a worse headline than "the
sitemap submits fourteen URLs that Google cannot index", even though twelve is bigger. The
tier decides the order; the count never does.

**Every finding names its measurement.** Not "images are unoptimized" but "the LCP element on
the blog template is a 412KB JPEG loaded with `loading="lazy"`, which delays the exact thing
being measured". A finding a client cannot verify is a finding they cannot act on.

**Separate the ranking argument from the conversion argument.** Core Web Vitals below the
floor is a ranking finding. Core Web Vitals already over the floor is a conversion
conversation or nothing at all. Never let the Rakuten numbers do ranking work.

**Say "not connected" in the client's own words.** "We can see what your site serves; only
Search Console can tell us what Google stored. You have that access and we do not - here are
the four numbers to pull." That is a credible sentence. An invented indexation percentage is
not.

**When a whole area passes, say so in one line and move on.** "hreflang: not applicable, and
recorded as such so nobody implements it later for no reason" is a complete section.

**Flag the crawl's own limits.** If the crawl hit its cap, every count is a floor. If pages
were skipped by robots, nothing is known about them. Put this in the header, not a footnote.

---

## Priority vocabulary

Matches `push_sheet.py`'s validation, which blocks anything else and blocks more than five
`this week`.

| Priority | Means |
|---|---|
| `this week` | blocking indexation or actively losing traffic |
| `this month` | real, not urgent |
| `structural` | needs a decision or a development cycle, not a ticket |
| `backlog` | worth doing, will not change anything on its own |

---

## The BUILD handoff

When the engagement includes implementation, the report's three fixes should map onto the
files `emit.py` produced. Say which file does which fix, and name the deploy order:
robots.txt and sitemap first, redirects next, schema last. A report that recommends changes
while a directory of the exact changed files sits unmentioned is two deliverables pretending
to be one.

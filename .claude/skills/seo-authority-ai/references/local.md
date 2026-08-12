# LOCAL mode

Runs only when a business has a physical location or a defined service area. When it does not,
`local.applicable` is still recorded as a `pass` rather than omitted, so nobody implements local
work six months later without asking whether it applies.

**When local applies it is promoted to tier 2**, above extractability and mentions. course/35 is
explicit that it outranks most general work for a business that depends on it, and **46% of all
Google searches carry local intent.**

---

## The weighting, and why most local packages are sold backwards

`[practitioner, modeled estimates, not disclosed weights]`

| Signal group | Weight |
|---|---|
| **Google Business Profile** (categories, completeness, freshness) | **32%** |
| **Reviews** (volume, velocity, sentiment) | **20%** |
| On-page (NAP, local keywords, authority) | 15% |
| Behavioural (CTR, click-to-call, direction requests) | 9% |
| Links (local backlinks, brand authority) | 8% |
| **Citations** (directory consistency) | **6%** |

GBP plus reviews is **roughly half**. Citations are **6%** - and citation-building packages are
the most commonly sold local product. Lead with the profile and the reviews.

---

## Check the primary category first, every time

**The strongest individual signal in local search, and it is one dropdown.** Thirty seconds of
work.

Pick the most specific accurate option. "Personal Injury Attorney" beats "Lawyer". "Fairground"
beats "Tourist Attraction" if the business is a fairground.

`local.gbp_primary_category` returns `review` rather than pass or fail: the category is observable
from the map pack, but "most specific *accurate*" is a judgment only someone who knows the
business can make.

---

## Reviews

| Metric | Threshold | Why |
|---|---|---|
| Volume | **50+ in 12 months** | reported **3x** more likely to appear in AI recommendations |
| Rating | **4.5+** | roughly **doubles** citation frequency |
| Velocity | **2-4 per week** | **5-15/month sustained six months** is reported to move a business **5-10 map pack positions** |
| Response time | **24-48 hours** | applies to negatives especially |

Both AI-surface numbers are `[practitioner, single vendor]`. Treat the direction as reliable and
the magnitude as indicative, and say so.

**Velocity beats total.** A business with 500 old reviews and none this quarter reads as stale; one
with 80 and a steady four a week reads as alive. This skill returns `unknown` for velocity without
dated review data.

---

## NAP consistency

**Byte-identical everywhere.** Not "close enough".

`normalize_nap()` exists to *detect* variants, not to bless them: it maps `St.` to `Street`, `Ste`
to `Suite`, strips punctuation, and then compares. Two listings that normalise to the same string
but were written differently are still a finding.

Real suppressors: "St." against "Street"; a suite number present in one listing and absent in
another; two different phone numbers; a tracking number in one place and the real one elsewhere.

**Fix order** - this is the tier order, and going out of order wastes the effort:

1. **Google Business Profile**, Bing Places, Apple Maps, Yelp, Facebook
2. **Aggregators**: Data Axle, Localeze
3. Industry directories

Tooling: BrightLocal, Whitespark, Yext. None is free, and this skill returns `unknown` for the
directories it cannot see rather than guessing.

---

## Profile completeness

| Element | Target |
|---|---|
| Google Posts | **1-3 weekly** - they now surface in AI Overview citations |
| Q&A seeded | **8-12 entries** covering pricing, service areas, parking, process |
| Photos | **10-25 minimum**, refreshed periodically |
| Every field | completed |

**Never quote the "100+ photos get 520% more calls" figure.** It traces to vendor research citing
Google, not to a Google publication. course/35 flags it explicitly, and there are plenty of
defensible local numbers to use instead.

---

## Schema

**LocalBusiness**, plus **Service** and **FAQPage**. Validated by `seo-technical/schema.py`, not
here.

**FAQ rich results sunset in May 2026. The markup still feeds answer engines.** Pages carrying FAQ
schema are reported **4x** more likely to be cited in AI Overviews. So: keep the markup, stop
expecting the Google rich result, and do not let anyone remove it as "deprecated".

---

## Three surfaces, assessed separately

| Surface | How it is read | What wins it |
|---|---|---|
| **Map pack** | Serper places result | GBP completeness, category, reviews, proximity |
| **Local organic** | Serper organic | the work in `09-seo-foundation.md` and `10-seo-onpage.md` |
| **AI recommendation** | `aivis.py` only | entity clarity, reviews, mentions |

These are different systems and a business can win one while losing another.
`local.three_surfaces` returns `review` with whichever two were observable, and `unknown` for the
third unless `aivis.py` ran.

---

## Location pages

`local.pages_unique` fails on high body overlap between location pages. Templated pages with the
city name swapped are doorway behaviour, and the fact that they sometimes still rank is not an
argument for building them.

**Mobile load under 2 seconds** is the floor - cross-referenced from `seo-technical/vitals.py`,
not measured here.

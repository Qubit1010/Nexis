# Platform Format Checklist

Operational checklist for writing a finished piece. **This file is not a source of truth for
platform mechanics.** It carries craft (structure, sequence, what a good opening does) and defers
every claim about how a platform behaves to the two cited corpora:

| For | Go to | Corpus |
|---|---|---|
| How a platform ranks, distributes, what changed, cadence, growth | `social-media-advisor/references/platform-specs/<platform>.md` | 329 sources, 60 first-party platform docs |
| What a format should be, how long, how it opens, what a view is | `content-advisor/references/format-specs/` | 560 sources, 285 confirmed |

`platform-specs/00-index.md` already names `content-engine` as an executor for LinkedIn and
Instagram. That is the intended relationship: they hold the mechanics, this holds the craft.

---

## Rewritten 2026-08-28. Read this before trusting an older copy.

This file previously carried numbers inherited from `marketing-advisor`, which was deleted for
being untrustworthy. `social-media-advisor/references/what-not-to-do.md:215` names three of them
specifically as having no traceable primary source. **They have been removed, not softened:**

| Removed claim | Why |
|---|---|
| "No link in the body (cuts reach 50-70%)" | No platform documents a link penalty. No citable source exists |
| "3-5 hashtags cuts reach ~29%" | No reach penalty per hashtag and no optimal count exist |
| "a 61s+ read earns ~13x the engagement of a 3s skim" | Unsourced convention |
| "60-85% watch on mute; captions add ~25% retention" | `content-advisor` refuses the 85%-on-mute claim outright |
| "Newsletters bypass the feed, 40-60% open rates" | Open rates have been uninterpretable since Apple MPP in 2021 |
| "Golden Hour: first 60 min on 2-5% of your network" | Same class as best-time-to-post, which the corpus refuses |
| "55% of views from non-followers", "sends worth 3-5x a like", "saves ~3x" | No confirmed weighting of saves or sends against likes exists anywhere in the corpus |
| "doc carousel = #1 format (6.6-7% engagement)" | Practitioner-tier. Direction holds, the number is not assertable |
| "1,300-3,000 chars perform ~38% better", "contrarian hooks lift reach ~49%", "8x company page reach", "AI referrals convert 3.49%", "comparison pages convert 3.2x" | Unsourced |

**The standing rule, taken from the corpus: give the direction, attribute the number, never
assert it.** If a client asks why, say a figure is practitioner convention rather than quoting it
as fact.

---

## Universal craft — applies to every platform

These carry no numeric claim and were never the problem.

- **The opening does one job: earn the next line.** It is not a summary and not a throat-clear.
- **One idea per unit.** Per slide, per beat, per paragraph.
- **The cover or first line must stand alone.** It is seen without the rest and decides whether
  the rest is seen at all.
- **Write to the audience's own words.** For a client, those are in `08-audience-persona.md`,
  verbatim. Do not paraphrase them into marketing language.
- **Close with one action, not three.**
- **Structural translation, never copy-paste**, when moving a piece between platforms. Same
  insight, rebuilt for the destination.
- **Specificity beats intensity.** A real number, name or date outperforms an adjective.

---

## Per platform

For each: the craft is here, the mechanics are one file away. Both files below are worth reading
in full before a first build for a new client.

### LinkedIn → `platform-specs/linkedin.md`

- **Text post.** Hook lands before the "see more" cut, so front-load it. Short paragraphs (1-3
  sentences) with white space between them; dense blocks get skimmed rather than read. This is
  craft consensus among named LinkedIn ghostwriters, not a proven finding - see
  `copy-conversion/references/platform-formatting.md`'s LinkedIn Structure row for the citations
  and the honesty flag (no controlled study of it exists in either corpus). One clear action at
  the end.
- **Document carousel.** Cover stands alone. One insight per slide. Final slide carries the
  action. Accompanying post text sets up why the document is worth opening.
- Direction the corpus supports: **carousels accumulate dwell because they require swipes**, and
  LinkedIn has published about dwell `[P*]`. The engagement multiples in circulation are
  practitioner-tier, so use the direction and attribute any number.
- **Cadence: no first-party statement exists.** Aleem's committed cadence is **2x/week**, set in
  `context/current-priorities.md` after 3x/week failed twice. For a client, take cadence from
  their `18-content-strategy.md`, not from convention.
- **Commenting adds reach without adding posts.** The documented rationale for
  `linkedin-commenter`.

### Instagram → `platform-specs/instagram.md`

- **Reel.** Motion in the first frame. Spoken and on-screen hook together. Short beats, one idea
  each. Captions on, because silent viewing is real even though the specific percentage is not
  citable.
- **Carousel.** Cover is a thumbnail first and a slide second. Max one idea per slide.
- **Caption.** Hook in the first line before truncation. Expand, then one action.
- Direction the corpus supports: **Reels reach non-followers, feed posts and carousels serve the
  existing audience**, because the recommendation surfaces are separate `[P*]`. There is **no
  confirmed weighting of saves or sends against likes** anywhere in the corpus.
- **Cadence: no first-party frequency statement. All numbers are convention.**
- **Stories:** see `agency/personal-brand-stories.md`, which is honest that no dedicated Stories
  benchmark research exists and names its one real data point's source.

### TikTok / YouTube / Facebook / X, Reddit, Pinterest, Threads

Go straight to `platform-specs/tiktok.md`, `youtube.md`, `facebook.md`, `secondary.md`.

Two things worth knowing before writing for these:

- **YouTube redefined a "view" to first-frame on 24 Aug 2026.** Every YouTube view benchmark
  predating that is measuring a different thing; the old metric is now "engaged view".
- **`secondary.md` is explicitly light and uneven** (Reddit has no first-party sources at all,
  Threads has one, Bluesky none). Do not present confident advice for those platforms.

### Blog and long-form

Structure, length and SEO belong to `blog-writer`, validated by `seo-onpage`. Do not duplicate
their thresholds here. Two live corrections those skills already carry: meta description is
**105-155 characters**, and the 40-60 word answer **nests inside** a 134-167 word extractable
section rather than being the same number.

### Email and newsletter → `format-specs/newsletter.md`

Craft only. **Do not set an open-rate target.** Apple MPP broke open rates in 2021 and pre-2021
and post-2021 numbers are not comparable, so an open-rate goal is not a measurable objective.

---

## When a client asks for a number this file does not have

Say the corpus has no confirmed figure, give the direction, and name what is actually measurable
for them. That is the honest answer and it is also the more useful one: a made-up benchmark
cannot be hit or missed, so it cannot inform a decision.

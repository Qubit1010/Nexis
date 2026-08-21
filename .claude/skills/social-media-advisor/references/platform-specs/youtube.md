# YouTube

**Corpus depth: deep, 7 first-party documents.** All `[P*]` retrieved **2026-08-21**.

---

## 1. What it is for

Search-and-discovery driven demand, durable content with a long tail, and depth that no feed
platform supports. The only major surface here where a video keeps earning views for years.

Not for: fast turnaround, small production budgets, or anyone needing results this quarter.

## 2. How it ranks — `[P*]`

YouTube states two objectives for the recommendation system:

> "1. Help each viewer find videos they want to watch. 2. Maximize long-term viewer
> satisfaction." `[P*]` [s197]

The framing that matters is **"long-term viewer satisfaction"**, not per-video engagement. It is
a personalised relevance system: "aims to identify the most relevant content for each user at
any given moment" `[P*]` [s197].

YouTube documents how a creator should read their own performance against the recommendation
system `[P*]` [s196][s200], reach and engagement metrics `[P*]` [s199], a performance
troubleshooting FAQ `[P*]` [s201], and a general how-it-works page `[P*]` [s202].

**Practical consequence:** YouTube publishes more actionable first-party diagnostic guidance
than any other platform in this corpus. When a client asks why a video underperformed, there is
a real first-party answer path `[P*]` [s196][s201]. Use it before reaching for practitioner
theories about thumbnails.

## 3. What changed — dated, and imminent

**24 August 2026: YouTube redefines what a view is.** `[P*]` [s198]

> "Starting August 24, 2026, views across YouTube are counted from the first frame going forward
> — Shorts, Long Form, Podcasts, Live; all the formats. This is the new, standardized,
> consistent definition of a view. And the previous definition of a view will now be called an
> 'engaged view.'"

**This is the most consequential dated fact in the entire corpus and it lands three days after
this file was written.** Flag it every time YouTube measurement comes up:

- **Every YouTube view benchmark predating this date measures a different event.** Historical
  comparisons are broken, and year-on-year view counts will appear to jump for reasons that have
  nothing to do with performance.
- A "view" is now first-frame, matching how feed platforms count. The stricter old metric
  survives as **"engaged view"**, which is the one that still means someone actually watched.
- Anyone reporting a YouTube uplift across this boundary without adjusting is reporting an
  artifact. Say so before they present it to a client.

This is also the cleanest live illustration of the corpus rule that **cross-platform view
comparisons are not interpretable**: YouTube just changed its own counting rule, so even
YouTube-to-YouTube comparisons need a date check.

## 4. Formats that win

Long-form and Shorts are different distribution systems on one platform. Both are now counted
under the unified view definition `[P*]` [s198], which does **not** make them comparable, since
watch duration differs by construction.

Packaging (title and thumbnail) as the primary lever is practitioner-tier here. The
`content-advisor` corpus holds the format-craft evidence; this skill does not restate it.

## 5. Cadence

No first-party frequency statement. Convention only.

## 6. Growth mechanics

- **Read the first-party diagnostics first** `[P*]` [s196][s199][s201]. This platform tells you
  more about your own performance than any other here.
- Optimise for **long-term satisfaction**, the stated objective `[P*]` [s197], not for a
  per-video engagement spike.
- Search and suggested traffic behave differently from feed traffic. Diagnose which one moved
  before changing anything.

## 7. Fails when

- The client needs results inside a quarter.
- Production capacity is not there. This is the most expensive platform per unit output.
- Someone is comparing YouTube views to Instagram or TikTok views. Refuse the comparison.

## 8. Who executes

`content-production` (long-form scripts, Shorts scripts), `reel-creator` /
`hyperframes-reel` (rendered vertical video), `shorts-creator` (frames),
`social-media-skills:youtube-thumbnail` (thumbnail prompts). Format craft, including length
and retention structure, belongs to `content-advisor`.

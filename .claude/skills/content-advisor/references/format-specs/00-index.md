# Format specs — index

All 19 formats from section 7 of the Digital Marketing 2026 concept map, each in exactly one
spec file. **Load the one file you need, never the set.**

Every format inside a spec file follows the same sub-template, so an answer about a whitepaper
and an answer about a Reel come back in the same shape:

> **What it is for** — **Structure** — **The hook** — **Length and pacing** —
> **2026 optimization** — **Distribution** — **Fails when** — **Who executes it**

---

## The 19

| # | Format | Spec file | Who executes it |
|---|---|---|---|
| 1 | Blog posts | `written.md` | `blog-writer` |
| 2 | Articles | `written.md` | `blog-writer` |
| 3 | Guides | `written.md` | `blog-writer` on-site, `content-production` gated |
| 4 | Case studies | `written.md` | `content-production`; `case-study-generator` for NexusPoint's own projects |
| 5 | Whitepapers | `written.md` | `content-production` |
| 6 | Ebooks | `written.md` | `content-production` |
| 7 | Newsletters | `newsletter.md` | `content-production` |
| 8 | Videos (long-form) | `video.md` | `content-production` scripts it; no in-house renderer |
| 9 | Shorts | `video.md` | `shorts-creator` frames, `reel-creator` rendered |
| 10 | Reels | `video.md` | `reel-creator`, `hyperframes-reel` |
| 11 | TikToks | `video.md` | `content-production` scripts it |
| 12 | Podcasts | `audio-live.md` | `content-production` structure and show notes; `podcast-repurposer` for derivatives |
| 13 | Webinars | `audio-live.md` | `content-production` |
| 14 | Infographics | `visual.md` | `linkedin-infographics` |
| 15 | Memes | `visual.md` | `content-production` |
| 16 | Threads | `social-text.md` | `content-production` |
| 17 | LinkedIn posts | `social-text.md` | `content-production`; `post-creator` for Aleem's own |
| 18 | X posts | `social-text.md` | `content-production` |
| 19 | Carousels | `visual.md` | `carousel` for Instagram, `content-production` for LinkedIn document carousels |

**The grouping is by shared mechanics, not by convenience.** A whitepaper and a blog post share
a reading model; a Reel and a TikTok share a viewing model; a meme and an infographic share a
single-glance visual model. Where a format straddles two, it lives with the one whose mechanics
decide whether it works.

---

## What these files are, and are not

**They are** the operational spec: what the format has to do, how it is shaped, and what the
2026 evidence says about each of those, with every claim tiered.

**They are not** the evidence itself. That is `../research-synthesis.md`, organised by question.
When you need to know *why* a spec says what it says, or need to cite it, go there.

**They are not** the fill-in skeleton either. That is
`content-production/references/asset-templates.md`, which carries section headings and nothing
else so there is one source of truth for rationale.

---

## Reading the tiers

| Tag | Means | Follow it |
|---|---|---|
| `[C]` | Confirmed — peer-reviewed, primary data, or normative standards text | As evidence |
| `[P]` | Practitioner — an agency or vendor with a commercial interest, no published method | As a labelled, attributed number. Never as fact |
| `[P*]` | First-party platform documentation | Authoritative for what the platform **requires or defines**. Never evidence that something **works**. Always quoted with its retrieval date |
| `[K]` | Craft — practitioner teaching, teardowns, video | For technique and convention only. **Never** to support a factual claim |

Most of what any format spec says about "best practice" is `[P]` or `[K]`. That is the honest
shape of this subject, and the specs preserve it rather than flattening everything into
confident advice. When a client asks why we recommend something, the tier is the answer.

---

## Two standing rules

**Verify every platform number on the day you use it, and record the date.** Aspect ratios,
character limits and truncation points change quarterly. `[P*]` sources are the right place to
check, and the spec files carry dates for exactly this reason. **Truncation is not the limit**:
the limit is what the field accepts, truncation is what the reader sees before "more", and only
the second one decides whether your first line works.

**Do not treat a convention as a finding.** Hashtag counts, link suppression, emoji use and
posting times are conventions. Several are repeated everywhere and tested nowhere. The specs
mark them as such.

---

## A known conflict in the repo — resolved 2026-08-31, history kept for context

Two existing files once gave different answers about LinkedIn body links, hashtag counts and
whether shorter is better:

- `content-engine/references/platform-formats.md` gave hard numbers, traced to the deleted
  `marketing-advisor`'s 234-source NotebookLM synthesis, which was practitioner-heavy.
- `copy-conversion/references/platform-formatting.md` called the same claims unverified against
  a tiered corpus.

`marketing-advisor` was deleted 2026-08-27 for an integrity failure, and `platform-formats.md`
was rewritten 2026-08-28 to drop the numeric claims it can no longer trace. One qualitative
claim survived that rewrite uncited ("short paragraphs with white space... dense blocks get
skimmed"); as of 2026-08-31 it cross-cites `copy-conversion/platform-formatting.md`'s now-sourced
LinkedIn structure row instead of standing alone. **These specs still side with
`copy-conversion`'s epistemics** as the standing rule for this family: cite one file or the
other, never both, and never present a craft-tier convention as measured fact.

Separately: **how a post is formatted for a platform is `copy-conversion`'s territory**
(`platform-formatting.md`, its `format` mode). These specs cover what the *format* is as a
content asset. Where they touch, cross-cite rather than restate.

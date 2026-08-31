# Visual — infographics, carousels, memes

Three formats sharing one mechanic: **the image carries the argument, and it is judged in a
glance before it is read.** Text-first thinking is why most branded visual content fails.

Tiers per `00-index.md`.

---

## The evidence that applies to all three

**Graphics beat text for long-term retention** `[C]` [s34], and a meta-analysis finds graphics
improve reading comprehension `[C]` [s239]. NN/g summarises the picture-superiority effect for
practitioners `[C]` [s29].

**The mechanism is contested.** Dual coding versus depth-of-processing is unresolved. Use the
effect; do not explain the cause as settled.

**Encoding choice is measurable.** Cleveland and McGill established that different visual
encodings are read with different accuracy `[C]` [s240], extended by later work on task and data
distribution `[C]` [s235] and synthesised in "The Science of Visual Data Communication" `[C]`
[s238]. Common visual errors are catalogued `[C]` [s237][s64].

**Practical consequence:** for a quantitative comparison, position along a common scale is read
more accurately than angle or area. A pie chart of seven slices is a decision to be read
inaccurately.

**Accessibility is normative, not optional.** Figures and tables have documented accessibility
requirements `[C]` [s62]. Alt text is part of the deliverable, not an afterthought.

---

## Infographics

**What it is for.** One argument, whole, in a single glance-then-read image. It is a document
that happens to be an image, not decoration for a post.

**Structure.** A hierarchy that reads without instruction: the claim, the supporting structure,
the evidence, the attribution. If the reader has to work out where to start, it has failed.
`[K]` [s301][s373][s383]

**The hook.** The headline claim, legible at feed size before anything is zoomed.

**Length and pacing.** Density is the trade. Enough to be worth saving, sparse enough to be read
on a phone. Text that requires zooming is text that is not read.

**2026 optimization.** Design for the saved state, not the scroll state - infographics earn
their keep by being kept. Attribution and source lines matter here more than in any other visual
format, because the format signals authority.

**Distribution.** Feed plus the piece it summarises. An infographic with no parent asset is a
claim with nowhere to check it.

**Fails when** it is a bulleted list with a border, when the encoding misleads `[C]` [s237], or
when there is no alt text.

**Who executes it.** `linkedin-infographics` (single-image, template-driven Gemini prompts).

---

## Carousels

**What it is for.** A sequence, where each frame earns the swipe. The only visual format with a
narrative dimension.

**Structure.** Cover carries a single, specific promise (a named outcome or metric, never a
generic title like "Tips for LinkedIn") - it competes against every other post in the feed, so
treat it like a billboard: one message, zero ambiguity about what the viewer gets. `[K]`
[s302][s384]. One idea per frame, transitioned with a "breadcrumb" line that teases the next
frame rather than a bare "next" (Jay Clouse, Jens Joseph Mannanal's problem-solution-result
arc). `[K]` [s384][s301]. **No frame that exists only to set up the next one** - that is the most
common carousel failure and the reason people drop at frame 2. A recap frame for the saver, then
one CTA - "save this" outperforms a bare follow ask because saves carry more distribution weight
than likes. `[K]` [s302][s380][s384]

**The hook.** The cover, legible at feed size. It is competing at thumbnail scale, not at full
size.

**Length and pacing.** 6 to 10 frames is the reported sweet spot across sources - fewer feels
incomplete, more than roughly 12 risks a steep completion-rate drop. `[K]` [s383][s385]. Enough
frames for the idea, no more; if it needs more than that, the idea probably wants a different
format.

**2026 optimization.** Two distinct sub-formats that are not interchangeable:

| | Instagram carousel | LinkedIn document carousel |
|---|---|---|
| Ratio | 4:5 feed images | Document/PDF |
| Read as | Swipe sequence | Paged document |
| Owner | `carousel` | `content-production` |

**Distribution.** Native per platform. Do not repost one file to both.

**Fails when** frames are text-dense, when the cover is a title rather than a claim, or when the
last frame is the only one with substance.

**Who executes it.** `carousel` for Instagram. `content-production` for LinkedIn document
carousels - **the format every spec in this repo calls the strongest organic one, and the one no
image skill builds.**

---

## Memes

**The evidence is close to absent.** No confirmed source in this corpus studies branded memes.
They are covered only obliquely through diffusion research (Q9) and the meme-shape work on
temporal decay `[C]` [s126]. **Everything below is `[K]`.**

**What it is for.** Signalling in-group membership. The mechanism is recognition, not
information.

**Structure.** A named, recognisable template. The in-group tension it lands on. That is the
whole format. `[K]` [s309][s385][s394]

**The hook.** Instant recognition. A meme explained has failed.

**2026 optimization.** Template currency decays fast, and faster than any other format here -
consistent with sharp exogenous bursts decaying quickly `[C]`. A template that was current last
quarter reads as try-hard now.

**Fails when** the brand has no licence to use the format. **"This brand should not post a
meme" is a legitimate and often correct output.** A compliance-software company posting a meme
is not relatable, it is uncanny.

**Distribution.** Feed only, and only where the audience shares the reference.

**Who executes it.** `content-production`.

---

## What generalises across all three

1. **Legible at feed size or it does not exist.** All three are judged at thumbnail scale first.
2. **The image carries the claim.** If the caption is doing the work, the visual is decoration.
3. **Encoding accuracy is measurable** `[C]` [s240] - pick the encoding for the judgment the
   reader has to make.
4. **Alt text and contrast are part of the deliverable** `[C]` [s62].
5. **These are the formats most likely to be judged on saves rather than likes**, which is a
   different denominator - and there is no single engagement-rate formula `[C]` [s1], so state
   which one is being used.

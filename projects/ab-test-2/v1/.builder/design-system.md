---
project: ReplyLab
phase: 2 (design direction)
checkpoint: skipped (--auto)
---

# Design System — ReplyLab

## The aesthetic: "Correspondence desk"

Derived from the product, not picked from a shelf. This is a private instrument a founder opens to
read someone's message, decide what to say back, and check whether their prompt is working. Two
registers have to coexist:

- **Correspondence** — reading and writing prose. Needs a serif, generous measure, quiet chrome.
  A message from a prospective client should look like a letter, not a row in a CRM.
- **Instrument** — the scoreboard. Needs tabular figures, hairline rules, and one signal colour
  used sparingly enough that it still means something.

So: a warm paper ground, ink-dark text, a single restrained accent, and a deliberate three-way
type split. The failure mode being avoided is the SaaS dashboard default — a card grid of equal
tiles on cool grey with a blue gradient header. This is closer to a proof desk than a dashboard.

## Palette

Warm neutrals rather than cool grey, so long reading sessions do not feel clinical.

| Role | Light | Note |
|---|---|---|
| `--paper` | `#faf8f4` | app ground, warm off-white |
| `--surface` | `#ffffff` | raised panels |
| `--surface-sunk` | `#f2efe8` | the received-enquiry block, inputs |
| `--ink` | `#1a1917` | body text, 15.9:1 on paper |
| `--ink-2` | `#57534a` | secondary, 7.4:1 on paper |
| `--ink-3` | `#8a8378` | metadata, 4.6:1 on paper |
| `--rule` | `#e3ded3` | hairlines |
| `--accent` | `#7a3e12` | burnt sienna. Primary actions, active version. 8.1:1 on paper |
| `--accent-soft` | `#f0e4d8` | accent wash |
| `--good` | `#2f6b3f` | 5.9:1 |
| `--bad` | `#9b2c2c` | 6.4:1 |
| `--uncertain` | `#8a8378` | the "not enough data" state, deliberately the same grey as metadata |

Dark scheme overrides the same token names under `prefers-color-scheme: dark`: ground `#16150f`,
surface `#1f1e18`, ink `#f0ece3`, accent lifts to `#d99553` to hold contrast on dark.

Colour rule: the accent is for *action and identity*, good/bad only ever appear on ratings and
their aggregates. Nothing decorative gets colour.

## Type

Three registers, all from system stacks so the tool works offline and starts instantly. Not Inter
everywhere; the split is the point.

| Register | Stack | Used for |
|---|---|---|
| Prose | `Iowan Old Style, Palatino Linotype, Palatino, Georgia, serif` | Enquiry body, draft body, the editing textarea |
| UI | `-apple-system, Segoe UI, Roboto, system-ui, sans-serif` | Labels, buttons, nav, headings |
| Figures | `ui-monospace, SFMono-Regular, Cascadia Mono, Consolas, monospace` with `font-variant-numeric: tabular-nums` | Every number in the scoreboard and metadata strip |

Scale (1.25 ratio, not one flat heading size): `--t-xs 12px`, `--t-sm 13px`, `--t-base 16px`,
`--t-md 18px`, `--t-lg 22px`, `--t-xl 28px`. Prose runs at 17px/1.65 with a `66ch` max measure.
Body text never below 16px.

## Spacing, radius, depth

Space scale `4 / 8 / 12 / 16 / 24 / 32 / 48 / 64` — used with real hierarchy, not uniform padding.
Radius `--r-sm 4px`, `--r-md 8px`, `--r-lg 14px`; the draft sheet gets the large radius so it reads
as a single object.

Depth is a system of exactly three levels: a hairline (`1px solid var(--rule)`) for structure, one
soft shadow (`0 1px 2px rgba(26,25,23,.05), 0 8px 24px -12px rgba(26,25,23,.18)`) for the draft
sheet only, and an accent left-border for the active prompt version. Nothing else is elevated.

## Motion

Functional and fast. `--ease: cubic-bezier(.2,.7,.3,1)`, durations 120ms for hovers, 180ms for
state changes, 240ms for a draft arriving. The one expressive moment: a new draft fades and rises
8px as it lands, so the eye knows where the new text is. All of it sits inside a
`@media (prefers-reduced-motion: reduce)` block that collapses durations to 0.01ms.

## Components

- **Buttons** — three weights: solid accent (primary, one per view), hairline-outlined (secondary),
  and bare text (tertiary). All at least 44px tall. Focus is a 2px accent ring at 2px offset,
  never `outline: none`.
- **Rating control** — a paired segmented control, not two loose buttons. Selected state fills with
  good/bad at low opacity and gets a solid left rule; the unselected side stays neutral. Re-clicking
  the selected side clears the rating.
- **Received enquiry** — sunk surface, accent left rule, prose serif, with subject as a small caps
  UI label above. Reads as a quotation.
- **Metadata strip** — one line under the draft, monospace, `--ink-3`: version, provider, model,
  tokens, latency, cost. Dot separators, no icons.
- **Empty states** — designed, never blank. The scoreboard's empty state explains what it will show
  once drafts are rated and names the minimum sample; the enquiry rail's explains what to paste.
- **Stub banner** — when no API key is present, a persistent strip in the header states it plainly.
  This is a correctness feature, not decoration: a stub draft must never be mistaken for a real one.

## Signature moments

1. **The letter sheet.** The enquiry and the draft sit on one continuous paper sheet in the same
   serif, separated by a hairline and a small "your reply" marker, so drafting reads as replying
   rather than filling a form. The textarea inherits the exact prose type, so switching to edit
   mode does not change how the text looks — only that the cursor is now in it.

2. **The version ledger with confidence whiskers.** The scoreboard is a horizontal ledger, one row
   per prompt version, oldest at the bottom, drawn against a shared 0-100% axis. Each row shows the
   good-rate as a filled bar **and its 95% Wilson interval as a whisker**. A version rated once has
   a whisker spanning nearly the whole axis, so "1 of 1, 100%" is visibly worthless at a glance
   instead of looking like a win. That single visual is the product's opinion: it refuses to let a
   small sample look like progress.

## Accessibility checklist

- All text pairs above meet 4.5:1 (large text 3:1); the values are recorded in the palette table.
- Visible focus ring on every interactive element, tab order follows the visual order.
- Touch targets 44px minimum.
- Every input has a real `<label>`; icon-only controls carry `aria-label`.
- The scoreboard is a `<table>` with proper headers, so the bars are decoration over readable data,
  not the only representation. Rating state is announced with `aria-pressed`.
- `prefers-reduced-motion` respected.
- Responsive: single column under 900px, the rail becomes a horizontal scroller, no horizontal
  page scroll at 360px.

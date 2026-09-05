---
project: LeadQ
aesthetic: "Ledger — warm Swiss instrument panel"
platform: web
created: 2026-08-31T18:34:00Z
checkpoint: SKIPPED (--auto)
---

# Design System — LeadQ

## 1. Direction (the why)

Two audiences with opposite needs share this product. The prospect meets a **public form**
and should feel they are answering a considered questionnaire from someone precise, not
filling in a lead-capture modal. The operator meets a **triage surface** he opens every day
to make one repeated judgement: who is worth an hour. That is a ledger task, not an
analytics task. He is not exploring trends; he is reading a ranked list and marking it up.

So the direction is **Swiss grid discipline on a warm paper ground**: ink-black type,
hairline rules instead of card shadows, a strict tabular rhythm, and exactly one heat scale
reserved for score and nothing else. Records sit on ruled lines like entries in a book, not
in a deck of floating cards.

**What was deliberately rejected:** the `ui-ux-pro-max` catalog's own "Analytics Dashboard"
palette is `#3B82F6` blue with an `#F97316` orange accent on `#F8FAFC` cold white. That is
the exact generic default `design-standards.md` calls slop, and it is wrong here anyway:
cool slate-white plus a decorative accent reads as a metrics product, and this is a
judgement product. The base style is catalog style #1 (Minimalism & Swiss, rated best for
professional tools and WCAG AAA), pushed off the neutral by warming the ground and cutting
the accent count to one.

- **Aesthetic:** Ledger — warm Swiss instrument panel
- **Register / mood:** precise, unhurried, confident. Quiet until something is hot.
- **Reference points:** a printed accounts ledger, Swiss timetable typography, an instrument
  face where the only colour is the reading.

## 2. Color System

Two colour systems that never mix. **Heat** answers "how good is this lead", **State**
answers "what have I done about it". Keeping them separate is why a glance at the table
parses instantly.

### Ground and ink

| Role | Token | Value | Notes |
|------|-------|-------|-------|
| Page ground | `--paper` | `#F6F3EC` | Warm bone. The single biggest move away from the default cold `#F8FAFC`. |
| Raised surface | `--surface` | `#FDFCF9` | Table body, form panel. Barely lighter than paper. |
| Sunken | `--sunken` | `#EDE8DD` | Table head, inert wells. |
| Primary text | `--ink` | `#14120F` | Warm near-black. 17.1:1 on paper. |
| Secondary text | `--ink-2` | `#4A453D` | 8.6:1. Labels, meta. |
| Muted text | `--ink-3` | `#6E6759` | 4.97:1. Hints, timestamps. Deliberately not lighter. |
| Hairline | `--rule` | `#DCD6C9` | The workhorse. Replaces almost every shadow. |
| Strong rule | `--rule-strong` | `#C3BBAA` | Section boundaries, focus outlines' shadow. |

### Heat scale (score only)

| Band | Display token | Value | Text-safe token | Value |
|------|---------------|-------|-----------------|-------|
| Hot | `--ember` | `#D34E24` | `--ember-ink` | `#A83A17` |
| Warm | `--copper` | `#B87333` | `--copper-ink` | `#8A5522` |
| Cold | `--slate` | `#3A5A6B` | `--slate` | `#3A5A6B` (6.5:1, already safe) |

The split is not decoration. `--ember` at 3.8:1 on paper is legal for meters, bars, rules
and numerals >= 24px, but not for small text; `--ember-ink` at 5.7:1 is the version used for
body-size text and as a button background under white (6.4:1). Same for copper. Any UI that
needs a hot colour at small size uses the `-ink` variant, always.

### State scale (status only)

| Status | Token | Value | Contrast on paper | Treatment |
|--------|-------|-------|-------------------|-----------|
| New | `--ink` | `#14120F` | 17.1:1 | Filled ink pill, paper text. Loudest, because it is the one that needs action. |
| Contacted | `--state-contacted` | `#2F5D8C` | 6.1:1 | Outlined. |
| Qualified | `--state-qualified` | `#2C6E49` | 5.4:1 | Outlined with a filled tint. |
| Dead | `--state-dead` | `#6E6759` | 5.0:1 | Drained grey, row dims to 55%. Not red: dead is a resolution, not an error. |

### Semantic

`--success #2C6E49` · `--danger #A33223` · `--info #2F5D8C`. Error text uses `--danger`
at body size (5.4:1), error borders use it at 2px.

- **Dark mode:** no. Deliberate: one operator, one machine, and a paper ground is the whole
  point of the register. A dark variant would need a second heat scale to stay legible and
  buys nothing here. Recorded as a non-goal, not an oversight.
- **Contrast:** every pair above is stated with its measured ratio. Nothing ships under
  4.5:1 for body text or 3:1 for large text and UI boundaries.

## 3. Typography

| Role | Font | Weight | Size / scale |
|------|------|--------|--------------|
| Display (score, page title) | `--font-sans` | 700 | 40px / 1.05, tracking -0.03em |
| H1 / H2 | `--font-sans` | 650-700 | 28px / 22px, tracking -0.02em |
| Body | `--font-sans` | 400 | 16px / 1.6 |
| Small / meta | `--font-sans` | 500 | 13px / 1.45 |
| Eyebrow / column head | `--font-mono` | 600 | 12px, tracking +0.12em, uppercase |
| All numerals and IDs | `--font-mono` | 500-700 | tabular-nums, slashed zero where available |

```
--font-sans: "Segoe UI Variable Display", "Segoe UI", system-ui, -apple-system,
             "Helvetica Neue", Arial, sans-serif;
--font-mono: "Cascadia Code", "Cascadia Mono", ui-monospace, "SF Mono", Consolas,
             "Roboto Mono", monospace;
```

- **Pairing rationale:** no webfont is loaded. `next/font/google` fetches at build time,
  which makes `next build` fail offline and slows every cold build, and this project has to
  run locally on demand. The register is therefore carried by *scale, weight contrast,
  negative tracking and tabular numerals* rather than by a distinctive face. The mono is
  doing the personality work: every number in the product is monospaced and column-aligned,
  which is what makes it read as an instrument. This is the one place the design is more
  constrained than it would be with a licensed face, and it is logged as such.
- **Type scale:** 12 / 13 / 15 / 16 / 18 / 22 / 28 / 40 / 56. Real jumps, not one size
  repeated. Body never below 16px.
- **Measure:** prose capped at 68ch.

## 4. Tokens

- **Spacing:** 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96 (`--s-1` .. `--s-9`).
- **Radius:** `--r-sm 2px` (inputs, pills-that-are-not-pills), `--r-md 4px` (panels),
  `--r-pill 999px` (status pills only). Near-square by intent: sharp corners read as
  instrument, rounded reads as consumer app.
- **Shadow:** used almost nowhere. `--shadow-pop: 0 1px 2px rgba(20,18,15,.06),
  0 8px 24px -8px rgba(20,18,15,.18)` for the one floating surface (the expanded receipt).
  Everything else separates with `--rule`.
- **Border:** 1px `--rule` default; 2px `--ink` on focus; 2px `--danger` on error.
- **Z-index:** 10 sticky table head · 20 dropdown · 30 dialog · 50 toast.
- **Breakpoints:** 640 (sm) · 900 (md) · 1200 (lg).

## 5. Motion

| Use | Duration | Easing |
|-----|----------|--------|
| Hover / focus / colour | 120ms | `ease-out` |
| Row expand, panel reveal | 180ms | `cubic-bezier(.2,.8,.2,1)` |
| Score meter fill on mount | 600ms | `cubic-bezier(.2,.8,.2,1)` |

Motion is confirmation, never entertainment. The only animation with any length is the score
meter drawing itself in, which reinforces that the number was computed rather than typed.
`@media (prefers-reduced-motion: reduce)` collapses every duration to 0.01ms globally.

## 6. Component Treatments

- **Table = ledger.** No card, no zebra striping. Rows separate with a single hairline and a
  full-width hover wash (`--sunken`). Sticky mono column heads, uppercase, tracked out.
  Sortable heads get a mono caret and `aria-sort`.
- **Score cell.** A 3px vertical heat rule, then the score at 40px mono 700, then a 4px
  horizontal meter bar showing score/100 in the band colour. Three encodings of the same
  value (position, number, length) so it survives both a glance and a colour-blind reader.
- **Status pill.** 999px radius, 13px, 44px minimum hit area via padding. New is filled;
  the rest are outlined. This is the only rounded thing in the product.
- **Buttons.** Primary: `--ember-ink` fill, paper text, 2px radius. Secondary: ink hairline
  on transparent. Ghost: ink text only. All >= 44px tall. Focus is a 2px ink outline with a
  2px paper offset, visible on every ground.
- **Inputs.** Paper-white field, 1px `--rule`, 2px `--ink` on focus, 2px `--danger` +
  message on error. Every input has a real `<label for>`; hints sit above the field, errors
  below it and are `aria-describedby`-linked and `role="alert"`.
- **Empty state.** Designed, never blank: a ruled ledger frame, a one-line explanation, and
  the copyable public form URL. On the dashboard it is the onboarding.
- **Loading.** Skeleton rows that match the ledger rhythm exactly, so nothing shifts on
  arrival. Buttons disable and swap to a mono working label during async work.

## 7. Signature Moments

1. **The scoring receipt.** Expanding a lead row unrolls its score as a till receipt: each
   rule that fired on its own line, label left, signed points right in mono, then a ruled
   total. This is the product's whole thesis made visible — the operator can see exactly
   why a lead is an 82, and therefore trusts the number and knows which rule to edit. No
   template has this, because no template knows what the number means.

2. **The numbered intake column.** The public form is one editorial column with each
   question numbered `01` `02` `03` in ember mono, generous vertical rhythm between bands,
   no card and no hero gradient. It reads like a well-set questionnaire from someone who
   takes the work seriously, which is precisely the first impression the business is trying
   to make.

## 8. Accessibility Commitments

- Every colour pair above is stated with a measured ratio; small text never uses a display
  token.
- Visible 2px focus ring on every interactive element; tab order follows visual order.
- 44x44px minimum for every control including status pills and sort headers.
- Labels bound to inputs; `aria-label` on icon-only controls; `aria-sort` on sortable heads;
  `aria-expanded` on the receipt toggle; `role="alert"` on validation messages.
- Body text 16px minimum; the table scrolls horizontally inside its own container rather
  than pushing the page.
- `prefers-reduced-motion` honoured globally.
- Status is never encoded by colour alone: every pill carries its word, every band carries
  its number.
